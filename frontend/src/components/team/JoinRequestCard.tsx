import { Clock, Check, X } from 'lucide-react';
import { Card, Badge, Button } from '../ui';
import { formatDateTime } from '@/lib/utils';
import type { JoinRequest } from '@/lib/types';

interface JoinRequestCardProps {
    request: JoinRequest;
    onVote?: (requestId: number, vote: 'accept' | 'reject') => void;
    onCancel?: (requestId: number) => void;
    isTeamMember?: boolean;
    currentUserId?: number;
    loading?: boolean;
}

export function JoinRequestCard(
    {
        request,
        onVote,
        onCancel,
        isTeamMember = false,
        currentUserId,
        loading = false,
    }: JoinRequestCardProps
) {
    const hasVoted = request.votes.some((v) => v.voter.id === currentUserId);
    const isMyRequest = request.user.id === currentUserId;
    const isExpired = new Date(request.expires_at) < new Date();

    return (
        <Card className="p-4">
            <div className="flex items-start justify-between">
                <div>
                    <div className="flex items-center gap-2">
                        <span className="font-semibold text-white">{request.user.nickname}</span>
                        {isMyRequest && <Badge variant="phantom">You</Badge>}
                    </div>
                    <p className="text-sm text-mist-400 mt-1">
                        wants to join <strong className="text-mist-200">{request.team_name}</strong>
                    </p>
                </div>
                <Badge
                    variant={
                        request.status === 'pending'
                            ? 'phantom'
                            : request.status === 'accepted'
                                ? 'specter'
                                : 'blood'
                    }
                >
                    {request.status}
                </Badge>
            </div>

            {/* Progress */}
            {request.status === 'pending' && (
                <div className="mt-3">
                    <div className="flex items-center justify-between text-xs text-mist-400 mb-1">
            <span>
              {request.votes_received} / {request.votes_needed} votes
            </span>
                        {!isExpired && (
                            <span className="flex items-center">
                <Clock className="w-3 h-3 mr-1" />
                Expires {formatDateTime(request.expires_at)}
              </span>
                        )}
                    </div>
                    <div className="h-1.5 bg-void-200 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-phantom-500 transition-all"
                            style={{ width: `${(request.votes_received / request.votes_needed) * 100}%` }}
                        />
                    </div>
                </div>
            )}

            {/* Votes list */}
            {request.votes.length > 0 && (
                <div className="mt-3 pt-3 border-t border-phantom-900/20">
                    <p className="text-xs text-mist-500 mb-2">Votes</p>
                    <div className="flex flex-wrap gap-2">
                        {request.votes.map((vote) => (
                            <Badge
                                key={vote.id}
                                variant={vote.vote === 'accept' ? 'specter' : 'blood'}
                            >
                                {vote.voter.nickname}
                                {vote.vote === 'accept' ? (
                                    <Check className="w-3 h-3 ml-1" />
                                ) : (
                                    <X className="w-3 h-3 ml-1" />
                                )}
                            </Badge>
                        ))}
                    </div>
                </div>
            )}

            {/* Actions */}
            {request.status === 'pending' && !isExpired && (
                <div className="mt-4 flex gap-2">
                    {isTeamMember && !hasVoted && onVote && (
                        <>
                            <Button
                                variant="primary"
                                size="sm"
                                onClick={() => onVote(request.id, 'accept')}
                                loading={loading}
                            >
                                <Check className="w-4 h-4" />
                                Accept
                            </Button>
                            <Button
                                variant="danger"
                                size="sm"
                                onClick={() => onVote(request.id, 'reject')}
                                loading={loading}
                            >
                                <X className="w-4 h-4" />
                                Reject
                            </Button>
                        </>
                    )}
                    {isMyRequest && onCancel && (
                        <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => onCancel(request.id)}
                            loading={loading}
                        >
                            Cancel Request
                        </Button>
                    )}
                    {isTeamMember && hasVoted && (
                        <p className="text-sm text-mist-400">You have already voted</p>
                    )}
                </div>
            )}
        </Card>
    );
}
