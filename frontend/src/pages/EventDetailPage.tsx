import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
    Calendar,
    Clock,
    Users,
    ArrowLeft,
    Play,
    Trophy,
    RefreshCw,
} from 'lucide-react';
import {
    Card,
    Button,
    Loading,
    Badge,
    Alert,
    EmptyState,
} from '@/components/ui';
import { ChallengeCard, Leaderboard } from '@/components/event';
import { useAuthStore } from '@/lib/store';
import { api } from '@/lib/api';
import { formatDate, formatDateTime, formatTimeRemaining } from '@/lib/utils';
import type { Event, ChallengeStatus, EventLeaderboard, TeamMembershipStatus } from '@/lib/types';

export function EventDetailPage() {
    const { eventId } = useParams<{ eventId: string }>();
    const { user } = useAuthStore();
    const [event, setEvent] = useState<Event | null>(null);
    const [challenges, setChallenges] = useState<ChallengeStatus[]>([]);
    const [leaderboard, setLeaderboard] = useState<EventLeaderboard | null>(null);
    const [teamStatus, setTeamStatus] = useState<TeamMembershipStatus | null>(null);
    const [isRegistered, setIsRegistered] = useState(false);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState<'challenges' | 'leaderboard'>('challenges');

    const loadData = useCallback(async () => {
        if (!eventId) return;

        try {
            const [eventData, teamData, leaderboardData] = await Promise.all([
                api.getEvent(parseInt(eventId)),
                api.getMyTeamStatus(),
                api.getEventLeaderboard(parseInt(eventId)),
            ]);

            setEvent(eventData);
            setTeamStatus(teamData);
            setLeaderboard(leaderboardData);

            // Check if registered
            if (teamData.team) {
                const registrations = await api.getEventRegistrations(parseInt(eventId));
                const registered = registrations.some((r) => r.team.id === teamData.team!.id);

                setIsRegistered(registered);

                // Load challenges if registered and event is active
                if (registered && eventData.is_active) {
                    const challengesData = await api.getEventChallenges(parseInt(eventId));

                    setChallenges(challengesData);
                }
            }
        } catch (error) {
            console.error('Failed to load event data:', error);
        } finally {
            setLoading(false);
        }
    }, [eventId]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    // Auto-refresh leaderboard and challenges every 20 seconds during active event
    useEffect(() => {
        if (!event?.is_active || !isRegistered) return;

        const interval = setInterval(async () => {
            if (eventId) {
                const [challengesData, leaderboardData] = await Promise.all([
                    api.getEventChallenges(parseInt(eventId)),
                    api.getEventLeaderboard(parseInt(eventId)),
                ]);

                setChallenges(challengesData);
                setLeaderboard(leaderboardData);
            }
        }, 20000);

        return () => clearInterval(interval);
    }, [event?.is_active, isRegistered, eventId]);

    const handleRegister = async () => {
        if (!event) return;

        setActionLoading(true);
        setError('');

        try {
            await api.registerForEvent(event.id);
            await loadData();
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };

            setError(error.response?.data?.detail || 'Failed to register');
        } finally {
            setActionLoading(false);
        }
    };

    if (loading) {
        return <Loading message="Entering the hunt..." />;
    }

    if (!event) {
        return (
            <EmptyState
                title="Event not found"
                description="This hunt doesn't exist or has been removed."
                action={
                    <Link to="/events">
                        <Button variant="secondary">
                            <ArrowLeft className="w-4 h-4" />
                            Back to Events
                        </Button>
                    </Link>
                }
            />
        );
    }

    const totalPoints = challenges.reduce((sum, c) => sum + (c.points_awarded || 0), 0);
    const solvedCount = challenges.filter((c) => c.is_solved).length;

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <Link
                        to="/events"
                        className="inline-flex items-center gap-1 text-mist-400 hover:text-white mb-4 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back to Events
                    </Link>
                    <h1 className="page-title">{event.title}</h1>
                    <p className="text-phantom-400 font-mono mt-1">{event.code}</p>
                </div>

                <div className="flex items-center gap-2">
                    {event.is_active && (
                        <Badge variant="specter" className="animate-pulse">
                            <Play className="w-3 h-3 mr-1" />
                            Live
                        </Badge>
                    )}
                    {event.is_registration_open && !event.is_active && (
                        <Badge variant="phantom">Registration Open</Badge>
                    )}
                    {event.status === 'completed' && (
                        <Badge variant="mist">Completed</Badge>
                    )}
                </div>
            </div>

            {error && <Alert type="error">{error}</Alert>}

            {/* Event Info */}
            <Card className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-phantom-900/50 flex items-center justify-center">
                            <Calendar className="w-5 h-5 text-phantom-400" />
                        </div>
                        <div>
                            <p className="text-sm text-mist-500">Duration</p>
                            <p className="text-mist-200">
                                {formatDate(event.starts_at)} - {formatDate(event.ends_at)}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-specter-900/50 flex items-center justify-center">
                            <Users className="w-5 h-5 text-specter-400" />
                        </div>
                        <div>
                            <p className="text-sm text-mist-500">Teams</p>
                            <p className="text-mist-200">
                                {event.registered_teams_count} registered
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-blood-900/50 flex items-center justify-center">
                            <Clock className="w-5 h-5 text-blood-400" />
                        </div>
                        <div>
                            <p className="text-sm text-mist-500">
                                {event.is_active ? 'Time Remaining' : 'Starts'}
                            </p>
                            <p className="text-mist-200">
                                {event.is_active
                                    ? formatTimeRemaining(event.ends_at)
                                    : formatDateTime(event.starts_at)}
                            </p>
                        </div>
                    </div>
                </div>

                {event.description && (
                    <div className="mt-6 pt-6 border-t border-phantom-900/20">
                        <p className="text-mist-300">{event.description}</p>
                    </div>
                )}
            </Card>

            {/* Registration */}
            {!isRegistered && event.is_registration_open && (
                <Card className="p-6 border-phantom-700/50">
                    {!teamStatus?.has_team ? (
                        <div className="text-center">
                            <p className="text-mist-400 mb-4">
                                You need to be on a team to register for this event.
                            </p>
                            <Link to="/team">
                                <Button variant="primary">
                                    <Users className="w-4 h-4" />
                                    Join or Create a Team
                                </Button>
                            </Link>
                        </div>
                    ) : (
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="text-lg font-semibold text-white">
                                    Ready to join the hunt?
                                </h3>
                                <p className="text-mist-400 mt-1">
                                    Register with your team: {teamStatus.team?.name}
                                </p>
                            </div>
                            <Button
                                variant="primary"
                                onClick={handleRegister}
                                loading={actionLoading}
                            >
                                Register Team
                            </Button>
                        </div>
                    )}
                </Card>
            )}

            {/* Registered but not started */}
            {isRegistered && !event.is_active && event.status === 'registration' && (
                <Alert type="info">
                    Your team is registered! The hunt begins {formatDateTime(event.starts_at)}.
                </Alert>
            )}

            {/* Active Event Content */}
            {isRegistered && event.is_active && (
                <>
                    {/* Progress */}
                    <Card className="p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-white">Your Progress</h2>
                            <Button variant="ghost" size="sm" onClick={loadData}>
                                <RefreshCw className="w-4 h-4" />
                                Refresh
                            </Button>
                        </div>
                        <div className="grid grid-cols-3 gap-4">
                            <div className="text-center">
                                <div className="text-3xl font-bold text-phantom-400">{totalPoints}</div>
                                <div className="text-sm text-mist-500">Points</div>
                            </div>
                            <div className="text-center">
                                <div className="text-3xl font-bold text-specter-400">
                                    {solvedCount}/{challenges.length}
                                </div>
                                <div className="text-sm text-mist-500">Solved</div>
                            </div>
                            <div className="text-center">
                                <div className="text-3xl font-bold text-blood-400">
                                    {leaderboard?.entries.find((e) => e.team_id === teamStatus?.team?.id)?.rank || '-'}
                                </div>
                                <div className="text-sm text-mist-500">Rank</div>
                            </div>
                        </div>
                    </Card>

                    {/* Tabs */}
                    <div className="flex gap-2 border-b border-phantom-900/20">
                        <button
                            onClick={() => setActiveTab('challenges')}
                            className={`px-4 py-3 font-medium transition-colors ${
                                activeTab === 'challenges'
                                    ? 'text-phantom-400 border-b-2 border-phantom-400'
                                    : 'text-mist-500 hover:text-mist-300'
                            }`}
                        >
                            Challenges
                        </button>
                        <button
                            onClick={() => setActiveTab('leaderboard')}
                            className={`px-4 py-3 font-medium transition-colors ${
                                activeTab === 'leaderboard'
                                    ? 'text-phantom-400 border-b-2 border-phantom-400'
                                    : 'text-mist-500 hover:text-mist-300'
                            }`}
                        >
                            <Trophy className="w-4 h-4 inline mr-2" />
                            Leaderboard
                        </button>
                    </div>

                    {/* Tab Content */}
                    {activeTab === 'challenges' ? (
                        <div className="space-y-4">
                            {challenges.map((cs) => (
                                <ChallengeCard
                                    key={cs.challenge.id}
                                    challengeStatus={cs}
                                    onUpdate={loadData}
                                />
                            ))}
                        </div>
                    ) : (
                        leaderboard && (
                            <Leaderboard
                                leaderboard={leaderboard}
                                currentTeamId={teamStatus?.team?.id}
                            />
                        )
                    )}
                </>
            )}

            {/* Completed Event - Show Results */}
            {event.status === 'completed' && leaderboard && (
                <div>
                    <h2 className="section-title mb-4">
                        <Trophy className="w-5 h-5 inline mr-2 text-phantom-400" />
                        Final Results
                    </h2>
                    <Leaderboard
                        leaderboard={leaderboard}
                        currentTeamId={teamStatus?.team?.id}
                    />
                </div>
            )}
        </div>
    );
}
