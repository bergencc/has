import { useEffect, useState } from 'react';
import { Users, BarChart3, HelpCircle, Coins, User } from 'lucide-react';
import { Card, Loading, EmptyState, Alert } from '@/components/ui';
import { api } from '@/lib/api';
import type { TeamRankingEntry, UserTreatRankingEntry } from '@/lib/types';

export function TeamRankingsPage() {
    const [rankings, setRankings] = useState<TeamRankingEntry[]>([]);
    const [userRankings, setUserRankings] = useState<UserTreatRankingEntry[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadRankings = async () => {
            try {
                const [teamData, userData] = await Promise.all([
                    api.getTeamRankings(),
                    api.getUserTreatRankings(),
                ]);

                setRankings(teamData);
                setUserRankings(userData);
            } catch (error) {
                console.error('Failed to load team rankings:', error);
            } finally {
                setLoading(false);
            }
        };

        loadRankings();
    }, []);

    if (loading) {
        return <Loading message="Loading rankings..." />;
    }

    if (rankings.length === 0 && userRankings.length === 0) {
        return (
            <EmptyState
                title="No rankings yet"
                description="Team and treat rankings will appear once users and teams start scoring."
            />
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <Alert type="info">
                Hint usage score is calculated as <strong className="text-white">hints used per solved challenge</strong>.
                Lower scores indicate fewer hints used.
            </Alert>

            <Card className="p-0 overflow-hidden">
                <div className="hidden md:grid grid-cols-5 gap-4 px-6 py-3 text-xs uppercase tracking-wider text-mist-500 border-b border-phantom-900/20">
                    <div>Team</div>
                    <div>Points</div>
                    <div>Events</div>
                    <div>Members</div>
                    <div>Hint Usage</div>
                </div>
                <div className="divide-y divide-phantom-900/20">
                    {rankings.map((entry) => {
                        const hintScore =
                            entry.hint_usage_score === null
                                ? '—'
                                : entry.hint_usage_score.toFixed(2);

                        return (
                            <div
                                key={entry.team_id}
                                className="px-4 py-4 md:px-6"
                            >
                                {/* Mobile card */}
                                <div className="md:hidden">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className="w-9 h-9 rounded-full bg-phantom-900/40 flex items-center justify-center text-phantom-300 font-semibold">
                                                {entry.rank}
                                            </div>
                                            <div>
                                                <p className="font-semibold text-white">{entry.team_name}</p>
                                                <p className="text-xs text-mist-500 flex items-center gap-1">
                                                    <Users className="w-3 h-3" />
                                                    {entry.member_count} members
                                                </p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-lg font-semibold text-phantom-300">
                                                {entry.total_points}
                                            </p>
                                            <p className="text-xs text-mist-500">points</p>
                                        </div>
                                    </div>
                                    <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
                                        <div className="rounded-lg border border-phantom-900/30 bg-void-100/40 p-2">
                                            <p className="text-xs text-mist-500">Events</p>
                                            <p className="text-mist-100 font-semibold">
                                                {entry.events_registered}
                                            </p>
                                        </div>
                                        <div className="rounded-lg border border-phantom-900/30 bg-void-100/40 p-2">
                                            <p className="text-xs text-mist-500">Members</p>
                                            <p className="text-mist-100 font-semibold">
                                                {entry.member_count}
                                            </p>
                                        </div>
                                        <div className="col-span-2 rounded-lg border border-phantom-900/30 bg-void-100/40 p-2">
                                            <p className="text-xs text-mist-500">Hint Usage</p>
                                            <div className="flex items-center gap-2">
                                                <HelpCircle className="w-4 h-4 text-phantom-400" />
                                                <span className="text-mist-100 font-semibold">{hintScore}</span>
                                                <span className="text-xs text-mist-500">
                                                    ({entry.hints_used} hints / {entry.completed_challenges} solves)
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Desktop row */}
                                <div className="hidden md:grid grid-cols-5 gap-4 items-center">
                                    <div className="flex items-center gap-3">
                                        <div className="w-9 h-9 rounded-full bg-phantom-900/40 flex items-center justify-center text-phantom-300 font-semibold">
                                            {entry.rank}
                                        </div>
                                        <div>
                                            <p className="font-semibold text-white">{entry.team_name}</p>
                                            <p className="text-xs text-mist-500 flex items-center gap-1">
                                                <Users className="w-3 h-3" />
                                                {entry.member_count} members
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2 text-mist-200">
                                        <BarChart3 className="w-4 h-4 text-phantom-400" />
                                        <span className="font-semibold text-white">
                                            {entry.total_points}
                                        </span>
                                    </div>

                                    <div className="text-mist-200">
                                        <span className="font-semibold text-white">
                                            {entry.events_registered}
                                        </span>
                                    </div>

                                    <div className="text-mist-200 md:text-sm">
                                        {entry.member_count}
                                    </div>

                                    <div className="text-mist-200">
                                        <div className="flex items-center gap-2">
                                            <HelpCircle className="w-4 h-4 text-phantom-400" />
                                            <span className="font-semibold text-white">
                                                {hintScore}
                                            </span>
                                        </div>
                                        <p className="text-xs text-mist-500 mt-1">
                                            {entry.hints_used} hints / {entry.completed_challenges} solves
                                        </p>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </Card>

            <Card className="p-0 overflow-hidden">
                <div className="px-6 py-3 text-xs uppercase tracking-wider text-mist-500 border-b border-phantom-900/20">
                    Top Users by Treat
                </div>
                <div className="divide-y divide-phantom-900/20">
                    {userRankings.map((entry) => (
                        <div key={entry.user_id} className="px-4 py-4 md:px-6">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-9 h-9 rounded-full bg-specter-900/40 flex items-center justify-center text-specter-300 font-semibold">
                                        {entry.rank}
                                    </div>
                                    <div>
                                        <p className="font-semibold text-white flex items-center gap-2">
                                            <User className="w-4 h-4 text-mist-400" />
                                            {entry.dog_tag}
                                        </p>
                                        <p className="text-xs text-mist-500">
                                            Total Attributes: {entry.total_attributes}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2 text-mist-200">
                                    <Coins className="w-4 h-4 text-specter-400" />
                                    <span className="font-semibold text-white">{entry.treat}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </Card>
        </div>
    );
}
