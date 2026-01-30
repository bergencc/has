import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
    ArrowLeft,
    Plus,
    Edit,
    Trash2,
    Save,
    X,
    HelpCircle,
    QrCode,
    GripVertical,
} from 'lucide-react';
import {
    Card,
    Button,
    Input,
    Loading,
    Badge,
    Alert,
    Modal,
    EmptyState,
} from '@/components/ui';
import { api } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';
import type { Event } from '@/lib/types';

interface ChallengeAdmin {
    id: number;
    event_id: number;
    type: 'riddle' | 'scavenger_code';
    title: string;
    prompt: string;
    points: number;
    hint_cost: number;
    max_attempts: number | null;
    point_decay_per_attempt: number;
    hints: string[] | null;
    unlock_rule: Record<string, unknown> | null;
    accepted_answers: string[];
    sort_order: number;
    is_active: boolean;
    created_at: string;
}

export function AdminEventPage() {
    const { eventId } = useParams<{ eventId: string }>();
    const [event, setEvent] = useState<Event | null>(null);
    const [challenges, setChallenges] = useState<ChallengeAdmin[]>([]);
    const [loading, setLoading] = useState(true);
    const [showChallengeModal, setShowChallengeModal] = useState(false);
    const [editingChallenge, setEditingChallenge] = useState<ChallengeAdmin | null>(null);
    const [error, setError] = useState('');

    useEffect(() => {
        if (eventId) {
            loadData();
        }
    }, [eventId]);

    const loadData = async () => {
        try {
            const [eventData, challengesData] = await Promise.all([
                api.getEvent(parseInt(eventId!)),
                api.getAdminChallenges(parseInt(eventId!)),
            ]);

            setEvent(eventData);
            setChallenges(challengesData as ChallengeAdmin[]);
        } catch (error) {
            console.error('Failed to load data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteChallenge = async (challengeId: number) => {
        if (!confirm('Are you sure you want to delete this challenge?')) return;

        try {
            await api.deleteChallenge(challengeId);
            await loadData();
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };

            setError(error.response?.data?.detail || 'Failed to delete challenge');
        }
    };

    const handleEditChallenge = (challenge: ChallengeAdmin) => {
        setEditingChallenge(challenge);
        setShowChallengeModal(true);
    };

    const handleCreateChallenge = () => {
        setEditingChallenge(null);
        setShowChallengeModal(true);
    };

    if (loading) {
        return <Loading message="Loading event..." />;
    }

    if (!event) {
        return (
            <EmptyState
                title="Event not found"
                action={
                    <Link to="/admin">
                        <Button variant="secondary">
                            <ArrowLeft className="w-4 h-4" />
                            Back to Admin
                        </Button>
                    </Link>
                }
            />
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div>
                <Link
                    to="/admin"
                    className="inline-flex items-center gap-1 text-mist-400 hover:text-white mb-4 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back to Admin
                </Link>
                <div className="flex items-start justify-between">
                    <div>
                        <h1 className="page-title">{event.title}</h1>
                        <p className="text-phantom-400 font-mono">{event.code}</p>
                    </div>
                    <Badge
                        variant={
                            event.is_active
                                ? 'specter'
                                : event.status === 'completed'
                                    ? 'mist'
                                    : 'phantom'
                        }
                    >
                        {event.is_active ? 'Live' : event.status}
                    </Badge>
                </div>
            </div>

            {error && <Alert type="error">{error}</Alert>}

            {/* Event Details */}
            <Card className="p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Event Details</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                        <p className="text-mist-500">Start</p>
                        <p className="text-mist-200">{formatDateTime(event.starts_at)}</p>
                    </div>
                    <div>
                        <p className="text-mist-500">End</p>
                        <p className="text-mist-200">{formatDateTime(event.ends_at)}</p>
                    </div>
                    <div>
                        <p className="text-mist-500">Teams</p>
                        <p className="text-mist-200">{event.registered_teams_count} registered</p>
                    </div>
                    <div>
                        <p className="text-mist-500">Challenges</p>
                        <p className="text-mist-200">{challenges.length} total</p>
                    </div>
                </div>
            </Card>

            {/* Challenges */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="section-title">Challenges</h2>
                    <Button variant="primary" onClick={handleCreateChallenge}>
                        <Plus className="w-4 h-4" />
                        Add Challenge
                    </Button>
                </div>

                {challenges.length === 0 ? (
                    <EmptyState
                        title="No challenges yet"
                        description="Add riddles and scavenger codes for teams to solve"
                        action={
                            <Button variant="primary" onClick={handleCreateChallenge}>
                                <Plus className="w-4 h-4" />
                                Create First Challenge
                            </Button>
                        }
                    />
                ) : (
                    <div className="space-y-3">
                        {challenges
                            .sort((a, b) => a.sort_order - b.sort_order)
                            .map((challenge, index) => (
                                <Card key={challenge.id} className="p-4">
                                    <div className="flex items-start gap-4">
                                        <div className="text-mist-600 cursor-move">
                                            <GripVertical className="w-5 h-5" />
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3">
                        <span className="text-mist-500 font-mono text-sm">
                          #{index + 1}
                        </span>
                                                <h3 className="font-semibold text-white">{challenge.title}</h3>
                                                <Badge variant={challenge.type === 'riddle' ? 'phantom' : 'specter'}>
                                                    {challenge.type === 'riddle' ? (
                                                        <>
                                                            <HelpCircle className="w-3 h-3 mr-1" />
                                                            Riddle
                                                        </>
                                                    ) : (
                                                        <>
                                                            <QrCode className="w-3 h-3 mr-1" />
                                                            Scavenger
                                                        </>
                                                    )}
                                                </Badge>
                                                {!challenge.is_active && (
                                                    <Badge variant="blood">Inactive</Badge>
                                                )}
                                            </div>
                                            <p className="text-sm text-mist-400 mt-1 line-clamp-2">
                                                {challenge.prompt}
                                            </p>
                                            <div className="flex items-center gap-4 mt-2 text-xs text-mist-500">
                                                <span>{challenge.points} points</span>
                                                <span>{challenge.accepted_answers.length} accepted answers</span>
                                                {challenge.hints && (
                                                    <span>{challenge.hints.length} hints</span>
                                                )}
                                                {challenge.max_attempts && (
                                                    <span>Max {challenge.max_attempts} attempts</span>
                                                )}
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => handleEditChallenge(challenge)}
                                            >
                                                <Edit className="w-4 h-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => handleDeleteChallenge(challenge.id)}
                                                className="text-blood-400 hover:text-blood-300"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </Card>
                            ))}
                    </div>
                )}
            </div>

            {/* Challenge Modal */}
            <ChallengeModal
                isOpen={showChallengeModal}
                onClose={() => {
                    setShowChallengeModal(false);
                    setEditingChallenge(null);
                }}
                onSuccess={loadData}
                eventId={parseInt(eventId!)}
                challenge={editingChallenge}
            />
        </div>
    );
}

interface ChallengeModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
    eventId: number;
    challenge: ChallengeAdmin | null;
}

function ChallengeModal(
    {
        isOpen,
        onClose,
        onSuccess,
        eventId,
        challenge,
    }: ChallengeModalProps
) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [formData, setFormData] = useState({
        type: 'riddle' as 'riddle' | 'scavenger_code',
        title: '',
        prompt: '',
        points: 100,
        hint_cost: 10,
        max_attempts: '' as string | number,
        point_decay_per_attempt: 0,
        hints: [''],
        accepted_answers: [''],
        sort_order: 0,
        is_active: true,
    });

    useEffect(() => {
        if (challenge) {
            setFormData({
                type: challenge.type,
                title: challenge.title,
                prompt: challenge.prompt,
                points: challenge.points,
                hint_cost: challenge.hint_cost,
                max_attempts: challenge.max_attempts || '',
                point_decay_per_attempt: challenge.point_decay_per_attempt,
                hints: challenge.hints || [''],
                accepted_answers: challenge.accepted_answers,
                sort_order: challenge.sort_order,
                is_active: challenge.is_active,
            });
        } else {
            setFormData({
                type: 'riddle',
                title: '',
                prompt: '',
                points: 100,
                hint_cost: 10,
                max_attempts: '',
                point_decay_per_attempt: 0,
                hints: [''],
                accepted_answers: [''],
                sort_order: 0,
                is_active: true,
            });
        }
    }, [challenge]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const data = {
            ...formData,
            event_id: eventId,
            max_attempts: formData.max_attempts || null,
            hints: formData.hints.filter((h) => h.trim()),
            accepted_answers: formData.accepted_answers.filter((a) => a.trim()),
        };

        try {
            if (challenge) {
                await api.updateChallenge(challenge.id, data);
            } else {
                await api.createChallenge(data);
            }

            onSuccess();
            onClose();
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };

            setError(error.response?.data?.detail || 'Failed to save challenge');
        } finally {
            setLoading(false);
        }
    };

    const addHint = () => {
        setFormData({ ...formData, hints: [...formData.hints, ''] });
    };

    const removeHint = (index: number) => {
        const hints = formData.hints.filter((_, i) => i !== index);
        setFormData({ ...formData, hints: hints.length ? hints : [''] });
    };

    const addAnswer = () => {
        setFormData({ ...formData, accepted_answers: [...formData.accepted_answers, ''] });
    };

    const removeAnswer = (index: number) => {
        const answers = formData.accepted_answers.filter((_, i) => i !== index);
        setFormData({ ...formData, accepted_answers: answers.length ? answers : [''] });
    };

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title={challenge ? 'Edit Challenge' : 'Create Challenge'}
            size="lg"
        >
            <form onSubmit={handleSubmit} className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
                {error && <Alert type="error">{error}</Alert>}

                {/* Type */}
                <div>
                    <label className="label">Type</label>
                    <div className="flex gap-2">
                        <button
                            type="button"
                            onClick={() => setFormData({ ...formData, type: 'riddle' })}
                            className={`flex-1 p-3 rounded-lg border transition-colors ${
                                formData.type === 'riddle'
                                    ? 'border-phantom-500 bg-phantom-900/30 text-white'
                                    : 'border-phantom-900/30 text-mist-400 hover:border-phantom-700'
                            }`}
                        >
                            <HelpCircle className="w-5 h-5 mx-auto mb-1" />
                            Riddle
                        </button>
                        <button
                            type="button"
                            onClick={() => setFormData({ ...formData, type: 'scavenger_code' })}
                            className={`flex-1 p-3 rounded-lg border transition-colors ${
                                formData.type === 'scavenger_code'
                                    ? 'border-specter-500 bg-specter-900/30 text-white'
                                    : 'border-phantom-900/30 text-mist-400 hover:border-phantom-700'
                            }`}
                        >
                            <QrCode className="w-5 h-5 mx-auto mb-1" />
                            Scavenger Code
                        </button>
                    </div>
                </div>

                {/* Title */}
                <Input
                    label="Title"
                    placeholder="The Mysterious Clock Tower"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    required
                />

                {/* Prompt */}
                <div>
                    <label className="label">Prompt / Description</label>
                    <textarea
                        className="input resize-none"
                        rows={4}
                        placeholder="Enter the riddle or description..."
                        value={formData.prompt}
                        onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
                        required
                    />
                </div>

                {/* Points */}
                <div className="grid grid-cols-3 gap-4">
                    <Input
                        label="Points"
                        type="number"
                        min={1}
                        value={formData.points}
                        onChange={(e) =>
                            setFormData({ ...formData, points: parseInt(e.target.value) || 0 })
                        }
                        required
                    />
                    <Input
                        label="Hint Cost"
                        type="number"
                        min={0}
                        value={formData.hint_cost}
                        onChange={(e) =>
                            setFormData({ ...formData, hint_cost: parseInt(e.target.value) || 0 })
                        }
                    />
                    <Input
                        label="Max Attempts"
                        type="number"
                        min={1}
                        placeholder="Unlimited"
                        value={formData.max_attempts}
                        onChange={(e) =>
                            setFormData({
                                ...formData,
                                max_attempts: e.target.value ? parseInt(e.target.value) : '',
                            })
                        }
                    />
                </div>

                {/* Accepted Answers */}
                <div>
                    <label className="label">Accepted Answers</label>
                    <p className="text-xs text-mist-500 mb-2">
                        Add all valid answer variations. They will be normalized automatically.
                    </p>
                    {formData.accepted_answers.map((answer, index) => (
                        <div key={index} className="flex gap-2 mb-2">
                            <Input
                                placeholder="Enter an accepted answer"
                                value={answer}
                                onChange={(e) => {
                                    const answers = [...formData.accepted_answers];

                                    answers[index] = e.target.value;

                                    setFormData({ ...formData, accepted_answers: answers });
                                }}
                                required={index === 0}
                            />
                            {formData.accepted_answers.length > 1 && (
                                <Button
                                    type="button"
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => removeAnswer(index)}
                                >
                                    <X className="w-4 h-4" />
                                </Button>
                            )}
                        </div>
                    ))}
                    <Button type="button" variant="secondary" size="sm" onClick={addAnswer}>
                        <Plus className="w-4 h-4" />
                        Add Answer Variant
                    </Button>
                </div>

                {/* Hints */}
                <div>
                    <label className="label">Hints (optional)</label>
                    {formData.hints.map((hint, index) => (
                        <div key={index} className="flex gap-2 mb-2">
                            <Input
                                placeholder={`Hint ${index + 1}`}
                                value={hint}
                                onChange={(e) => {
                                    const hints = [...formData.hints];
                                    hints[index] = e.target.value;

                                    setFormData({ ...formData, hints });
                                }}
                            />
                            <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => removeHint(index)}
                            >
                                <X className="w-4 h-4" />
                            </Button>
                        </div>
                    ))}
                    <Button type="button" variant="secondary" size="sm" onClick={addHint}>
                        <Plus className="w-4 h-4" />
                        Add Hint
                    </Button>
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-3 pt-4 border-t border-phantom-900/20">
                    <Button type="button" variant="secondary" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button type="submit" variant="primary" loading={loading}>
                        <Save className="w-4 h-4" />
                        {challenge ? 'Save Changes' : 'Create Challenge'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
}
