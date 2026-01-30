import React from 'react';
import { Trophy, Clock, Lightbulb, XCircle } from 'lucide-react';
import { Card } from '../ui';
import { formatDuration } from '@/lib/utils';
import type { EventLeaderboard, LeaderboardEntry } from '@/lib/types';

interface LeaderboardProps {
    leaderboard: EventLeaderboard;
    currentTeamId?: number;
}

export function Leaderboard({ leaderboard, currentTeamId }: LeaderboardProps) {
    const getRankStyle = (rank: number) => {
        switch (rank) {
            case 1:
                return 'bg-gradient-to-r from-yellow-600/20 to-yellow-500/10 border-yellow-600/50';
            case 2:
                return 'bg-gradient-to-r from-gray-400/20 to-gray-300/10 border-gray-400/50';
            case 3:
                return 'bg-gradient-to-r from-orange-700/20 to-orange-600/10 border-orange-700/50';
            default:
                return '';
        }
    };

    const getRankIcon = (rank: number) => {
        if (rank <= 3) {
            return (
                <Trophy
                    className={`w-5 h-5 ${
                        rank === 1
                            ? 'text-yellow-500'
                            : rank === 2
                                ? 'text-gray-400'
                                : 'text-orange-600'
                    }`}
                />
            );
        }
        return <span className="text-mist-500 font-mono">{rank}</span>;
    };

    return (
        <Card>
            <div className="p-4 border-b border-phantom-900/20">
                <h2 className="text-lg font-display font-semibold text-white flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-phantom-400" />
                    Leaderboard
                </h2>
            </div>

            <div className="divide-y divide-phantom-900/20">
                {leaderboard.entries.length === 0 ? (
                    <div className="p-8 text-center text-mist-500">
                        No teams have scored yet. Be the first!
                    </div>
                ) : (
                    leaderboard.entries.map((entry) => (
                        <LeaderboardRow
                            key={entry.team_id}
                            entry={entry}
                            isCurrentTeam={entry.team_id === currentTeamId}
                            rankStyle={getRankStyle(entry.rank)}
                            rankIcon={getRankIcon(entry.rank)}
                        />
                    ))
                )}
            </div>
        </Card>
    );
}

interface LeaderboardRowProps {
    entry: LeaderboardEntry;
    isCurrentTeam: boolean;
    rankStyle: string;
    rankIcon: React.ReactNode;
}

function LeaderboardRow({ entry, isCurrentTeam, rankStyle, rankIcon }: LeaderboardRowProps) {
    return (
        <div
            className={`flex items-center gap-4 p-4 ${rankStyle} ${
                isCurrentTeam ? 'bg-phantom-900/20 border-l-2 border-phantom-500' : ''
            }`}
        >
            {/* Rank */}
            <div className="w-8 h-8 flex items-center justify-center">{rankIcon}</div>

            {/* Team info */}
            <div className="flex-1 min-w-0">
                <div className="font-semibold text-white truncate">
                    {entry.team_name}
                    {isCurrentTeam && (
                        <span className="ml-2 text-xs text-phantom-400">(Your team)</span>
                    )}
                </div>
                <div className="flex items-center gap-4 text-xs text-mist-500 mt-1">
                    <span>{entry.completed_challenges} solved</span>
                    {entry.total_time_seconds && (
                        <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
                            {formatDuration(entry.total_time_seconds)}
            </span>
                    )}
                </div>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-4 text-sm">
                {entry.hints_used > 0 && (
                    <span className="flex items-center gap-1 text-phantom-400">
            <Lightbulb className="w-4 h-4" />
                        {entry.hints_used}
          </span>
                )}
                {entry.wrong_attempts > 0 && (
                    <span className="flex items-center gap-1 text-blood-400">
            <XCircle className="w-4 h-4" />
                        {entry.wrong_attempts}
          </span>
                )}
            </div>

            {/* Points */}
            <div className="text-right">
                <div className="text-xl font-bold text-white">{entry.total_points}</div>
                <div className="text-xs text-mist-500">pts</div>
            </div>
        </div>
    );
}
