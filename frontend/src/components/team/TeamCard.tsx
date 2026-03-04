import { Users, Clock } from 'lucide-react';
import { Card, Badge } from '../ui';
import { formatDate } from '@/lib/utils';
import type { Team, TeamListItem } from '@/lib/types';

interface TeamCardProps {
    team: Team | TeamListItem;
    onClick?: () => void;
    showMembers?: boolean;
}

export function TeamCard({ team, onClick, showMembers = false }: TeamCardProps) {
    const isFullTeam = (value: Team | TeamListItem): value is Team => 'members' in value;
    const memberCount = isFullTeam(team) ? team.members.length : team.member_count;

    return (
        <Card hover={!!onClick} onClick={onClick} className="p-5">
            <div className="flex items-start justify-between">
                <div>
                    <h3 className="text-lg font-semibold text-white">{team.name}</h3>
                    {team.description && (
                        <p className="mt-1 text-sm text-mist-400 line-clamp-2">{team.description}</p>
                    )}
                </div>
                <Badge variant="phantom">
                    <Users className="w-3 h-3 mr-1" />
                    {memberCount}
                </Badge>
            </div>

            {showMembers && isFullTeam(team) && (
                <div className="mt-4 pt-4 border-t border-phantom-900/20">
                    <p className="text-xs text-mist-500 mb-2">Members</p>
                    <div className="flex flex-wrap gap-2">
                        {team.members.map((member) => (
                            <Badge
                                key={member.id}
                                variant={member.role === 'captain' ? 'specter' : 'mist'}
                            >
                                {member.user.dog_tag}
                                {member.role === 'captain' && ' ★'}
                            </Badge>
                        ))}
                    </div>
                </div>
            )}

            <div className="mt-4 flex items-center text-xs text-mist-500">
                <Clock className="w-3 h-3 mr-1" />
                Created {formatDate(team.created_at)}
            </div>
        </Card>
    );
}
