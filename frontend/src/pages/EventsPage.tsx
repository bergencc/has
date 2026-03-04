import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar } from 'lucide-react';
import { Loading, EmptyState } from '@/components/ui';
import { EventCard } from '@/components/event';
import { api } from '@/lib/api';
import type { EventListItem } from '@/lib/types';

export function EventsPage() {
    const [events, setEvents] = useState<EventListItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<'all' | 'active' | 'upcoming' | 'past'>('all');
    const [includePast, setIncludePast] = useState(false);

    const loadEvents = useCallback(async () => {
        try {
            const data = await api.listEvents(undefined, includePast);

            setEvents(data);
        } catch (error) {
            console.error('Failed to load events:', error);
        } finally {
            setLoading(false);
        }
    }, [includePast]);

    useEffect(() => {
        loadEvents();
    }, [loadEvents]);

    const filteredEvents = events.filter((event) => {
        switch (filter) {
            case 'active':
                return event.is_active;
            case 'upcoming':
                return event.is_registration_open && !event.is_active;
            case 'past':
                return event.status === 'completed';
            default:
                return true;
        }
    });

    if (loading) {
        return <Loading message="Discovering hunts..." />;
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <h1 className="page-title">
                    <Calendar className="w-8 h-8 inline mr-3 text-phantom-500" />
                    Events
                </h1>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-1 p-1 bg-void-100 rounded-lg">
                    {(['all', 'active', 'upcoming', 'past'] as const).map((f) => (
                        <button
                            key={f}
                            onClick={() => {
                                setFilter(f);
                                if (f === 'past') setIncludePast(true);
                            }}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                                filter === f
                                    ? 'bg-phantom-600 text-white'
                                    : 'text-mist-400 hover:text-white'
                            }`}
                        >
                            {f.charAt(0).toUpperCase() + f.slice(1)}
                        </button>
                    ))}
                </div>

                {filter !== 'past' && (
                    <label className="flex items-center gap-2 text-sm text-mist-400 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={includePast}
                            onChange={(e) => setIncludePast(e.target.checked)}
                            className="rounded border-phantom-700 bg-void-200 text-phantom-500 focus:ring-phantom-500"
                        />
                        Include past events
                    </label>
                )}
            </div>

            {/* Events Grid */}
            {filteredEvents.length === 0 ? (
                <EmptyState
                    icon={<Calendar className="w-8 h-8 text-phantom-500" />}
                    title="No events found"
                    description={
                        filter === 'all'
                            ? 'Check back later for new scavenger hunts'
                            : `No ${filter} events at the moment`
                    }
                />
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredEvents.map((event) => (
                        <Link key={event.id} to={`/events/${event.id}`}>
                            <EventCard event={event} onClick={() => {}} />
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}
