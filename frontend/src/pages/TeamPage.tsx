import { useEffect, useState } from 'react';
import { Users, Plus, Search, Clock, LogOut } from 'lucide-react';
import {
    Card,
    Button,
    Input,
    Loading,
    EmptyState,
    Badge,
    Alert,
} from '@/components/ui';
import { JoinRequestCard, CreateTeamModal } from '@/components/team';
import { useAuthStore } from '@/lib/store';
import { api } from '@/lib/api';
import { formatDate, formatTimeRemaining } from '@/lib/utils';
import type { TeamMembershipStatus, TeamListItem, JoinRequest } from '@/lib/types';

export function TeamPage() {
    const { user } = useAuthStore();
    const [teamStatus, setTeamStatus] = useState<TeamMembershipStatus | null>(null);
    const [availableTeams, setAvailableTeams] = useState<TeamListItem[]>([]);
    const [joinRequests, setJoinRequests] = useState<JoinRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const status = await api.getMyTeamStatus();

            setTeamStatus(status);

            if (!status.has_team) {
                const teams = await api.listTeams();

                setAvailableTeams(teams);
            } else if (status.team) {
                const requests = await api.getTeamJoinRequests(status.team.id);

                setJoinRequests(requests);
            }
        } catch (error) {
            console.error('Failed to load team data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleJoinRequest = async (teamId: number) => {
        setActionLoading(true);
        setError('');

        try {
            await api.requestToJoinTeam(teamId);
            await loadData();
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };

            setError(error.response?.data?.detail || 'Failed to send join request');
        } finally {
            setActionLoading(false);
        }
    };

    const handleVote = async (requestId: number, vote: 'accept' | 'reject') => {
        setActionLoading(true);

        try {
            await api.voteOnJoinRequest(requestId, vote);
            await loadData();
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };

            setError(error.response?.data?.detail || 'Failed to vote');
        } finally {
            setActionLoading(false);
        }
    };

    const handleCancelRequest = async (requestId: number) => {
        setActionLoading(true);

        try {
            await api.cancelJoinRequest(requestId);
            await loadData();
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };

            setError(error.response?.data?.detail || 'Failed to cancel request');
        } finally {
            setActionLoading(false);
        }
    };

    const handleLeaveTeam = async () => {
        if (!teamStatus?.team) return;
        if (!confirm('Are you sure you want to leave this team?')) return;

        setActionLoading(true);
        try {
            await api.leaveTeam(teamStatus.team.id);
            await loadData();
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };

            setError(error.response?.data?.detail || 'Failed to leave team');
        } finally {
            setActionLoading(false);
        }
    };

    const filteredTeams = availableTeams.filter((team) =>
        team.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    if (loading) {
        return <Loading message="Gathering team spirits..." />;
    }

    return (
        <div className="space-y-8 animate-fade-in">
            <div className="flex items-center justify-between">
                <h1 className="page-title">
                    <Users className="w-8 h-8 inline mr-3 text-phantom-500" />
                    Team
                </h1>
            </div>

            {error && (
                <Alert type="error" className="animate-slide-up">
                    {error}
                </Alert>
            )}

            {/* Has Team */}
            {teamStatus?.has_team && teamStatus.team && (
                <>
                    {/* Team Info */}
                    <Card className="p-6">
                        <div className="flex items-start justify-between mb-6">
                            <div>
                                <h2 className="text-2xl font-display font-bold text-white">
                                    {teamStatus.team.name}
                                </h2>
                                {teamStatus.team.description && (
                                    <p className="mt-2 text-mist-400">{teamStatus.team.description}</p>
                                )}
                            </div>
                            <Badge variant="phantom">
                                {teamStatus.team.member_count} / 4 members
                            </Badge>
                        </div>

                        {/* Membership Info */}
                        {teamStatus.membership && (
                            <div className="p-4 bg-void-200 rounded-lg mb-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-mist-500">Your membership</p>
                                        <p className="text-mist-200">
                                            Joined {formatDate(teamStatus.membership.joined_at)}
                                        </p>
                                    </div>
                                    {teamStatus.membership.is_locked ? (
                                        <div className="text-right">
                                            <Badge variant="phantom">
                                                <Clock className="w-3 h-3 mr-1" />
                                                Locked
                                            </Badge>
                                            <p className="text-xs text-mist-500 mt-1">
                                                {formatTimeRemaining(teamStatus.membership.lock_expires_at)}
                                            </p>
                                        </div>
                                    ) : (
                                        <Button
                                            variant="danger"
                                            size="sm"
                                            onClick={handleLeaveTeam}
                                            loading={actionLoading}
                                        >
                                            <LogOut className="w-4 h-4" />
                                            Leave Team
                                        </Button>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Members */}
                        <div>
                            <h3 className="text-lg font-semibold text-white mb-4">Members</h3>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {teamStatus.team.members.map((member) => (
                                    <div
                                        key={member.id}
                                        className="flex items-center justify-between p-3 bg-void-200 rounded-lg"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-full bg-phantom-900/50 flex items-center justify-center">
                        <span className="text-phantom-400 font-semibold">
                          {member.user.dog_tag[0].toUpperCase()}
                        </span>
                                            </div>
                                            <div>
                                                <p className="font-medium text-white">
                                                    {member.user.dog_tag}
                                                    {member.user.id === user?.id && (
                                                        <span className="text-phantom-400 text-sm ml-2">(you)</span>
                                                    )}
                                                </p>
                                                <p className="text-xs text-mist-500">
                                                    {member.role === 'captain' ? '★ Captain' : 'Member'}
                                                </p>
                                            </div>
                                        </div>
                                        {member.is_locked && (
                                            <Badge variant="mist" className="text-xs">
                                                <Clock className="w-3 h-3 mr-1" />
                                                Locked
                                            </Badge>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </Card>

                    {/* Join Requests */}
                    {joinRequests.length > 0 && (
                        <section>
                            <h2 className="section-title mb-4">
                                Pending Join Requests ({joinRequests.length})
                            </h2>
                            <div className="space-y-3">
                                {joinRequests.map((request) => (
                                    <JoinRequestCard
                                        key={request.id}
                                        request={request}
                                        onVote={handleVote}
                                        isTeamMember
                                        currentUserId={user?.id}
                                        loading={actionLoading}
                                    />
                                ))}
                            </div>
                        </section>
                    )}
                </>
            )}

            {/* No Team */}
            {!teamStatus?.has_team && (
                <>
                    {/* Pending Requests */}
                    {teamStatus?.pending_requests && teamStatus.pending_requests.length > 0 && (
                        <section>
                            <h2 className="section-title mb-4">Your Pending Requests</h2>
                            <div className="space-y-3">
                                {teamStatus.pending_requests.map((request) => (
                                    <JoinRequestCard
                                        key={request.id}
                                        request={request}
                                        onCancel={handleCancelRequest}
                                        currentUserId={user?.id}
                                        loading={actionLoading}
                                    />
                                ))}
                            </div>
                        </section>
                    )}

                    {/* Create or Join */}
                    <Card className="p-6">
                        <div className="text-center mb-6">
                            <Users className="w-12 h-12 text-phantom-500 mx-auto mb-4" />
                            <h2 className="text-xl font-semibold text-white">Join the Hunt</h2>
                            <p className="text-mist-400 mt-2">
                                Create your own team or join an existing one
                            </p>
                        </div>

                        <Button
                            variant="primary"
                            className="w-full"
                            onClick={() => setShowCreateModal(true)}
                        >
                            <Plus className="w-4 h-4" />
                            Create a Team
                        </Button>

                        <div className="relative my-6">
                            <div className="absolute inset-0 flex items-center">
                                <div className="w-full border-t border-phantom-800" />
                            </div>
                            <div className="relative flex justify-center">
                <span className="bg-void-100 px-4 text-sm text-mist-500">
                  or join an existing team
                </span>
                            </div>
                        </div>

                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-mist-500" />
                            <Input
                                placeholder="Search teams..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-10"
                            />
                        </div>
                    </Card>

                    {/* Available Teams */}
                    <section>
                        <h2 className="section-title mb-4">
                            Available Teams ({filteredTeams.length})
                        </h2>
                        {filteredTeams.length === 0 ? (
                            <EmptyState
                                title="No teams found"
                                description={
                                    searchQuery
                                        ? 'Try a different search term'
                                        : 'Be the first to create a team!'
                                }
                                action={
                                    <Button variant="primary" onClick={() => setShowCreateModal(true)}>
                                        <Plus className="w-4 h-4" />
                                        Create Team
                                    </Button>
                                }
                            />
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {filteredTeams.map((team) => (
                                    <Card key={team.id} className="p-5">
                                        <div className="flex items-start justify-between mb-3">
                                            <div>
                                                <h3 className="font-semibold text-white">{team.name}</h3>
                                                {team.description && (
                                                    <p className="text-sm text-mist-400 mt-1 line-clamp-2">
                                                        {team.description}
                                                    </p>
                                                )}
                                            </div>
                                            <Badge variant="phantom">
                                                <Users className="w-3 h-3 mr-1" />
                                                {team.member_count}/4
                                            </Badge>
                                        </div>
                                        <Button
                                            variant="secondary"
                                            size="sm"
                                            className="w-full"
                                            onClick={() => handleJoinRequest(team.id)}
                                            loading={actionLoading}
                                            disabled={team.member_count >= 4}
                                        >
                                            {team.member_count >= 4 ? 'Team Full' : 'Request to Join'}
                                        </Button>
                                    </Card>
                                ))}
                            </div>
                        )}
                    </section>
                </>
            )}

            {/* Create Team Modal */}
            <CreateTeamModal
                isOpen={showCreateModal}
                onClose={() => setShowCreateModal(false)}
                onSuccess={loadData}
            />
        </div>
    );
}
