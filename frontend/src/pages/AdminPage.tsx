import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Shield, Plus, Edit, Eye, Users } from 'lucide-react';
import {
    Card,
    Button,
    Loading,
    Badge,
    EmptyState,
    Modal,
    Input,
    Alert,
} from '@/components/ui';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { EventListItem } from '@/lib/types';

export function AdminPage() {
    const [events, setEvents] = useState<EventListItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);

    useEffect(() => {
        loadEvents();
    }, []);

    const loadEvents = async () => {
        try {
            const data = await api.listEvents(undefined, true);

            setEvents(data);
        } catch (error) {
            console.error('Failed to load events:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <Loading message="Loading admin panel..." />;
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <h1 className="page-title">
                    <Shield className="w-8 h-8 inline mr-3 text-phantom-500" />
                    Admin Dashboard
                </h1>
                <Button variant="primary" onClick={() => setShowCreateModal(true)}>
                    <Plus className="w-4 h-4" />
                    Create Event
                </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="p-5">
                    <div className="text-3xl font-bold text-white">{events.length}</div>
                    <div className="text-sm text-mist-500">Total Events</div>
                </Card>
                <Card className="p-5">
                    <div className="text-3xl font-bold text-specter-400">
                        {events.filter((e) => e.is_active).length}
                    </div>
                    <div className="text-sm text-mist-500">Active</div>
                </Card>
                <Card className="p-5">
                    <div className="text-3xl font-bold text-phantom-400">
                        {events.filter((e) => e.is_registration_open).length}
                    </div>
                    <div className="text-sm text-mist-500">Registration Open</div>
                </Card>
                <Card className="p-5">
                    <div className="text-3xl font-bold text-mist-400">
                        {events.filter((e) => e.status === 'completed').length}
                    </div>
                    <div className="text-sm text-mist-500">Completed</div>
                </Card>
            </div>

            {/* Events List */}
            <section>
                <h2 className="section-title mb-4">All Events</h2>
                {events.length === 0 ? (
                    <EmptyState
                        title="No events yet"
                        description="Create your first scavenger hunt event"
                        action={
                            <Button variant="primary" onClick={() => setShowCreateModal(true)}>
                                <Plus className="w-4 h-4" />
                                Create Event
                            </Button>
                        }
                    />
                ) : (
                    <div className="space-y-3">
                        {events.map((event) => (
                            <Card key={event.id} className="p-4">
                                <div className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3">
                                            <h3 className="font-semibold text-white">{event.title}</h3>
                                            <Badge
                                                variant={
                                                    event.is_active
                                                        ? 'specter'
                                                        : event.is_registration_open
                                                            ? 'phantom'
                                                            : event.status === 'completed'
                                                                ? 'mist'
                                                                : 'blood'
                                                }
                                            >
                                                {event.is_active
                                                    ? 'Live'
                                                    : event.is_registration_open
                                                        ? 'Registration'
                                                        : event.status}
                                            </Badge>
                                        </div>
                                        <div className="flex items-center gap-4 mt-1 text-sm text-mist-500">
                                            <span className="font-mono">{event.code}</span>
                                            <span>
                        {formatDate(event.starts_at)} - {formatDate(event.ends_at)}
                      </span>
                                            <span className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                                                {event.registered_teams_count} teams
                      </span>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Link to={`/admin/events/${event.id}`}>
                                            <Button variant="secondary" size="sm">
                                                <Edit className="w-4 h-4" />
                                                Manage
                                            </Button>
                                        </Link>
                                        <Link to={`/events/${event.id}`}>
                                            <Button variant="ghost" size="sm">
                                                <Eye className="w-4 h-4" />
                                            </Button>
                                        </Link>
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>
                )}
            </section>

            {/* Create Event Modal */}
            <CreateEventModal
                isOpen={showCreateModal}
                onClose={() => setShowCreateModal(false)}
                onSuccess={loadEvents}
            />
        </div>
    );
}

interface CreateEventModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

function CreateEventModal({ isOpen, onClose, onSuccess }: CreateEventModalProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const [formData, setFormData] = useState({
        title: '',
        code: '',
        description: '',
        starts_at: '',
        ends_at: '',
        min_team_size: 1,
        max_team_size: 4,
        ranking_point: 0,
        treat_point: 0,
        decoding_point: 0,
        perception_point: 0,
        logic_point: 0,
        resilience_point: 0,
        arcane_point: 0,
        insight_point: 0,
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        setLoading(true);
        setError('');

        try {
            await api.createEvent({
                ...formData,
                starts_at: new Date(formData.starts_at).toISOString(),
                ends_at: new Date(formData.ends_at).toISOString(),
            });

            onSuccess();
            onClose();
            setFormData({
                title: '',
                code: '',
                description: '',
                starts_at: '',
                ends_at: '',
                min_team_size: 1,
                max_team_size: 4,
                ranking_point: 0,
                treat_point: 0,
                decoding_point: 0,
                perception_point: 0,
                logic_point: 0,
                resilience_point: 0,
                arcane_point: 0,
                insight_point: 0,
            });
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };

            setError(error.response?.data?.detail || 'Failed to create event');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Create Event" size="lg">
            <form onSubmit={handleSubmit} className="space-y-4">
                {error && <Alert type="error">{error}</Alert>}

                <Input
                    label="Event Title"
                    placeholder="Halloween Scavenger Hunt 2024"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    required
                />

                <Input
                    label="Event Code"
                    placeholder="HALLOWEEN-2024"
                    value={formData.code}
                    onChange={(e) =>
                        setFormData({ ...formData, code: e.target.value.toUpperCase() })
                    }
                    required
                />

                <div>
                    <label className="block text-sm font-medium text-mist-300 mb-2">
                        Description
                    </label>
                    <textarea
                        className="w-full px-4 py-3 bg-void-200 border border-phantom-900/30 rounded-lg text-mist-100 placeholder:text-mist-600 focus:outline-none focus:border-phantom-600 focus:ring-1 focus:ring-phantom-600 transition-colors resize-none"
                        rows={3}
                        placeholder="Describe your event..."
                        value={formData.description}
                        onChange={(e) =>
                            setFormData({ ...formData, description: e.target.value })
                        }
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <Input
                        label="Start Date & Time"
                        type="datetime-local"
                        value={formData.starts_at}
                        onChange={(e) =>
                            setFormData({ ...formData, starts_at: e.target.value })
                        }
                        required
                    />
                    <Input
                        label="End Date & Time"
                        type="datetime-local"
                        value={formData.ends_at}
                        onChange={(e) =>
                            setFormData({ ...formData, ends_at: e.target.value })
                        }
                        required
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <Input
                        label="Min Team Size"
                        type="number"
                        min={1}
                        max={10}
                        value={formData.min_team_size}
                        onChange={(e) =>
                            setFormData({ ...formData, min_team_size: parseInt(e.target.value) })
                        }
                        required
                    />
                    <Input
                        label="Max Team Size"
                        type="number"
                        min={1}
                        max={10}
                        value={formData.max_team_size}
                        onChange={(e) =>
                            setFormData({ ...formData, max_team_size: parseInt(e.target.value) })
                        }
                        required
                    />
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Input
                        label="Event Ranking"
                        type="number"
                        min={0}
                        value={formData.ranking_point}
                        onChange={(e) =>
                            setFormData({ ...formData, ranking_point: parseInt(e.target.value) || 0 })
                        }
                    />
                    <Input
                        label="Event Treat"
                        type="number"
                        min={0}
                        value={formData.treat_point}
                        onChange={(e) =>
                            setFormData({ ...formData, treat_point: parseInt(e.target.value) || 0 })
                        }
                    />
                    <Input
                        label="Decoding"
                        type="number"
                        min={0}
                        max={100}
                        value={formData.decoding_point}
                        onChange={(e) =>
                            setFormData({ ...formData, decoding_point: parseInt(e.target.value) || 0 })
                        }
                    />
                    <Input
                        label="Perception"
                        type="number"
                        min={0}
                        max={100}
                        value={formData.perception_point}
                        onChange={(e) =>
                            setFormData({ ...formData, perception_point: parseInt(e.target.value) || 0 })
                        }
                    />
                    <Input
                        label="Logic"
                        type="number"
                        min={0}
                        max={100}
                        value={formData.logic_point}
                        onChange={(e) =>
                            setFormData({ ...formData, logic_point: parseInt(e.target.value) || 0 })
                        }
                    />
                    <Input
                        label="Resilience"
                        type="number"
                        min={0}
                        max={100}
                        value={formData.resilience_point}
                        onChange={(e) =>
                            setFormData({ ...formData, resilience_point: parseInt(e.target.value) || 0 })
                        }
                    />
                    <Input
                        label="Arcane"
                        type="number"
                        min={0}
                        max={100}
                        value={formData.arcane_point}
                        onChange={(e) =>
                            setFormData({ ...formData, arcane_point: parseInt(e.target.value) || 0 })
                        }
                    />
                    <Input
                        label="Insight"
                        type="number"
                        min={0}
                        max={100}
                        value={formData.insight_point}
                        onChange={(e) =>
                            setFormData({ ...formData, insight_point: parseInt(e.target.value) || 0 })
                        }
                    />
                </div>

                <div className="flex justify-end gap-3 pt-4">
                    <Button type="button" variant="secondary" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button type="submit" variant="primary" loading={loading}>
                        Create Event
                    </Button>
                </div>
            </form>
        </Modal>
    );
}
