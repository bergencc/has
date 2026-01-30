import React, { useState } from 'react';
import {
    Lock,
    Unlock,
    CheckCircle,
    HelpCircle,
    Send,
    Lightbulb,
    Star,
} from 'lucide-react';
import { Card, Badge, Button, Input, Alert } from '../ui';
import { api } from '@/lib/api';
import type { ChallengeStatus } from '@/lib/types';

interface ChallengeCardProps {
    challengeStatus: ChallengeStatus;
    onUpdate: () => void;
}

export function ChallengeCard({ challengeStatus, onUpdate }: ChallengeCardProps) {
    const { challenge, is_unlocked, is_solved, attempts_made, hints_revealed, points_possible } = challengeStatus;

    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    const [hintLoading, setHintLoading] = useState(false);
    const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!answer.trim()) return;

        setLoading(true);
        setFeedback(null);

        try {
            const result = await api.submitAnswer(challenge.id, answer);

            setFeedback({
                type: result.is_correct ? 'success' : 'error',
                message: result.message,
            });

            if (result.is_correct) {
                setAnswer('');
            }

            onUpdate();
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };

            setFeedback({
                type: 'error',
                message: error.response?.data?.detail || 'Failed to submit answer',
            });
        } finally {
            setLoading(false);
        }
    };

    const handleRequestHint = async () => {
        setHintLoading(true);

        try {
            await api.requestHint(challenge.id);

            onUpdate();
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };

            setFeedback({
                type: 'error',
                message: error.response?.data?.detail || 'Failed to get hint',
            });
        } finally {
            setHintLoading(false);
        }
    };

    const hintsRemaining = challenge.hints_available - hints_revealed.length;

    return (
        <Card className={`overflow-hidden ${is_solved ? 'border-specter-700/50' : ''}`}>
            {/* Header */}
            <div className="p-5 border-b border-phantom-900/20">
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                        {!is_unlocked ? (
                            <div className="w-10 h-10 rounded-lg bg-void-200 flex items-center justify-center">
                                <Lock className="w-5 h-5 text-mist-500" />
                            </div>
                        ) : is_solved ? (
                            <div className="w-10 h-10 rounded-lg bg-specter-900/50 flex items-center justify-center">
                                <CheckCircle className="w-5 h-5 text-specter-400" />
                            </div>
                        ) : (
                            <div className="w-10 h-10 rounded-lg bg-phantom-900/50 flex items-center justify-center">
                                <Unlock className="w-5 h-5 text-phantom-400" />
                            </div>
                        )}
                        <div>
                            <h3 className="font-semibold text-white">{challenge.title}</h3>
                            <div className="flex items-center gap-2 mt-1">
                                <Badge variant={challenge.type === 'riddle' ? 'phantom' : 'specter'}>
                                    {challenge.type === 'riddle' ? (
                                        <>
                                            <HelpCircle className="w-3 h-3 mr-1" />
                                            Riddle
                                        </>
                                    ) : (
                                        <>
                                            <Star className="w-3 h-3 mr-1" />
                                            Scavenger
                                        </>
                                    )}
                                </Badge>
                            </div>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-2xl font-bold text-white">{points_possible}</div>
                        <div className="text-xs text-mist-500">points</div>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="p-5">
                {!is_unlocked ? (
                    <p className="text-mist-400 italic">Complete previous challenges to unlock this one.</p>
                ) : (
                    <>
                        {/* Prompt */}
                        <div className="bg-void-200 rounded-lg p-4 mb-4">
                            <p className="text-mist-200 whitespace-pre-wrap">{challenge.prompt}</p>
                        </div>

                        {/* Hints */}
                        {hints_revealed.length > 0 && (
                            <div className="space-y-2 mb-4">
                                {hints_revealed.map((hint, i) => (
                                    <div
                                        key={i}
                                        className="flex items-start gap-2 p-3 bg-phantom-900/30 rounded-lg border border-phantom-700/30"
                                    >
                                        <Lightbulb className="w-4 h-4 text-phantom-400 shrink-0 mt-0.5" />
                                        <p className="text-sm text-phantom-200">{hint}</p>
                                    </div>
                                ))}
                            </div>
                        )}

                        {is_solved ? (
                            <Alert type="success">
                                Solved! You earned {challengeStatus.points_awarded} points.
                            </Alert>
                        ) : (
                            <>
                                {/* Feedback */}
                                {feedback && (
                                    <div className="mb-4">
                                        <Alert type={feedback.type}>{feedback.message}</Alert>
                                    </div>
                                )}

                                {/* Answer form */}
                                <form onSubmit={handleSubmit} className="flex gap-2">
                                    <Input
                                        placeholder="Enter your answer..."
                                        value={answer}
                                        onChange={(e) => setAnswer(e.target.value)}
                                        className="flex-1"
                                    />
                                    <Button type="submit" variant="primary" loading={loading}>
                                        <Send className="w-4 h-4" />
                                    </Button>
                                </form>

                                {/* Actions */}
                                <div className="flex items-center justify-between mt-4 pt-4 border-t border-phantom-900/20">
                                    <div className="text-sm text-mist-500">
                                        {attempts_made > 0 && (
                                            <span>
                        {attempts_made} attempt{attempts_made !== 1 && 's'} made
                                                {challenge.max_attempts && ` / ${challenge.max_attempts} max`}
                      </span>
                                        )}
                                    </div>
                                    {hintsRemaining > 0 && (
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={handleRequestHint}
                                            loading={hintLoading}
                                        >
                                            <Lightbulb className="w-4 h-4" />
                                            Get Hint ({hintsRemaining} left, -{challenge.hint_cost} pts)
                                        </Button>
                                    )}
                                </div>
                            </>
                        )}
                    </>
                )}
            </div>
        </Card>
    );
}
