import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Users, ArrowRight, Ghost, Sparkles } from 'lucide-react';
import { Card, Button, Loading, EmptyState, Badge } from '@/components/ui';
import { EventCard } from '@/components/event';
import { useAuthStore } from '@/lib/store';
import { api } from '@/lib/api';
import type { EventListItem, TeamMembershipStatus } from '@/lib/types';

export function DashboardPage() {
    const { user } = useAuthStore();
    const [events, setEvents] = useState<EventListItem[]>([]);
    const [teamStatus, setTeamStatus] = useState<TeamMembershipStatus | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [eventsData, teamData] = await Promise.all([
                api.listEvents(),
                api.getMyTeamStatus(),
            ]);

            setEvents(eventsData);
            setTeamStatus(teamData);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <Loading message="Awakening bulldogs..." />;
    }

    const activeEvents = events.filter((e) => e.is_active);
    const upcomingEvents = events.filter((e) => e.is_registration_open && !e.is_active);

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Welcome */}
            <div className="relative overflow-hidden rounded-2xl bg-linear-to-br from-phantom-900/50 to-void-100 border border-phantom-800/50 p-8">
                <div className="relative z-10">
                    <h1 className="text-3xl font-display font-bold text-white">
                        Welcome back, <span className="text-phantom-400">{user?.nickname}</span>
                    </h1>
                    <p className="mt-2 text-mist-400">Ready to solve some mysteries?</p>
                </div>
                <Ghost className="absolute right-8 top-1/2 -translate-y-1/2 w-24 h-24 text-phantom-800/30" />
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="p-5">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-phantom-900/50 flex items-center justify-center">
                            <Users className="w-6 h-6 text-phantom-400" />
                        </div>
                        <div>
                            <p className="text-sm text-mist-500">Team</p>
                            <p className="text-lg font-semibold text-white">
                                {teamStatus?.has_team ? teamStatus.team?.name : 'No team'}
                            </p>
                        </div>
                    </div>
                </Card>

                <Card className="p-5">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-specter-900/50 flex items-center justify-center">
                            <Sparkles className="w-6 h-6 text-specter-400" />
                        </div>
                        <div>
                            <p className="text-sm text-mist-500">Active Hunts</p>
                            <p className="text-lg font-semibold text-white">{activeEvents.length}</p>
                        </div>
                    </div>
                </Card>

                <Card className="p-5">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-blood-900/50 flex items-center justify-center">
                            <Calendar className="w-6 h-6 text-blood-400" />
                        </div>
                        <div>
                            <p className="text-sm text-mist-500">Upcoming</p>
                            <p className="text-lg font-semibold text-white">{upcomingEvents.length}</p>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Team Status */}
            {!teamStatus?.has_team && (
                <Card className="p-6 border-phantom-700/50">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-lg font-semibold text-white">Join or Create a Team</h2>
                            <p className="mt-1 text-mist-400">
                                You need a team to participate in scavenger hunts.
                            </p>
                        </div>
                        <Link to="/team">
                            <Button variant="primary">
                                Get Started
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                        </Link>
                    </div>
                </Card>
            )}

            {/* Pending Join Requests */}
            {teamStatus?.pending_requests && teamStatus.pending_requests.length > 0 && (
                <Card className="p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">Pending Requests</h2>
                    <div className="space-y-2">
                        {teamStatus.pending_requests.map((req) => (
                            <div
                                key={req.id}
                                className="flex items-center justify-between p-3 bg-void-200 rounded-lg"
                            >
                <span className="text-mist-200">
                  Request to join <strong>{req.team_name}</strong>
                </span>
                                <Badge variant="phantom">
                                    {req.votes_received}/{req.votes_needed} votes
                                </Badge>
                            </div>
                        ))}
                    </div>
                    <Link to="/team" className="block mt-4">
                        <Button variant="secondary" className="w-full">
                            View Details
                        </Button>
                    </Link>
                </Card>
            )}

            {/* Active Events */}
            {activeEvents.length > 0 && (
                <section>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-display font-semibold text-white">
                            <Sparkles className="w-5 h-5 inline mr-2 text-specter-400" />
                            Live Hunts
                        </h2>
                        <Link to="/events" className="text-phantom-400 hover:text-phantom-300 text-sm">
                            View all →
                        </Link>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {activeEvents.slice(0, 2).map((event) => (
                            <Link key={event.id} to={`/events/${event.id}`}>
                                <EventCard event={event} />
                            </Link>
                        ))}
                    </div>
                </section>
            )}

            {/* Upcoming Events */}
            {upcomingEvents.length > 0 && (
                <section>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-display font-semibold text-white">
                            <Calendar className="w-5 h-5 inline mr-2 text-phantom-400" />
                            Upcoming Hunts
                        </h2>
                        <Link to="/events" className="text-phantom-400 hover:text-phantom-300 text-sm">
                            View all →
                        </Link>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {upcomingEvents.slice(0, 2).map((event) => (
                            <Link key={event.id} to={`/events/${event.id}`}>
                                <EventCard event={event} />
                            </Link>
                        ))}
                    </div>
                </section>
            )}

            {/* Empty state */}
            {events.length === 0 && (
                <EmptyState
                    title="No hunts available"
                    description="Check back later for new scavenger hunts and riddle challenges."
                />
            )}
        </div>
    );
}
