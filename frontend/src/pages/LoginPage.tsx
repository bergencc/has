import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Ghost } from 'lucide-react';
import { Button, Input, Card, Alert } from '@/components/ui';
import { useAuthStore } from '@/lib/store';

export function LoginPage() {
    const [email, setEmail] = useState('');
    const [nickname, setNickname] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { login } = useAuthStore();

    const handleDevLogin = async (e: React.FormEvent) => {
        e.preventDefault();

        setError('');
        setLoading(true);

        try {
            await login(email, nickname);

            navigate('/');
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };

            setError(error.response?.data?.detail || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            {/* Background effects */}
            <div className="fixed inset-0 fog-overlay pointer-events-none" />

            <div className="w-full max-w-md animate-fade-in">
                {/* Logo */}
                <div className="text-center mb-8">
                    <Ghost className="w-16 h-16 text-phantom-500 mx-auto animate-float" />
                    <h1 className="mt-4 font-display text-4xl font-bold text-white">
                        Hide and <span className="text-phantom-400">Seek</span>
                    </h1>
                    <p className="mt-2 text-mist-400">Enter the realm of riddles</p>
                </div>

                <Card className="p-6">
                    {error && (
                        <div className="mb-4">
                            <Alert type="error">{error}</Alert>
                        </div>
                    )}

                    {/* Dev login form */}
                    <form onSubmit={handleDevLogin} className="space-y-4">
                        <Input
                            label="Email"
                            type="email"
                            placeholder="you@bergen.edu"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />

                        <Input
                            label="Nickname"
                            placeholder="bulldog"
                            value={nickname}
                            onChange={(e) => setNickname(e.target.value)}
                            required
                            minLength={3}
                            maxLength={50}
                        />

                        <Button type="submit" variant="primary" className="w-full" loading={loading}>
                            Enter the Hunt
                        </Button>
                    </form>

                    <div className="mt-6 pt-6 border-t border-phantom-900/20">
                        <p className="text-xs text-center text-mist-500">
                            Development mode enabled. In production, Google OAuth will be used.
                        </p>
                    </div>
                </Card>

                <p className="mt-6 text-center text-sm text-mist-500">
                    By signing in, you agree to embrace the mystery.
                </p>
            </div>
        </div>
    );
}
