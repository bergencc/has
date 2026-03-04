import React, { useState } from 'react';
import { Ghost } from 'lucide-react';
import { Button, Card, Alert } from '@/components/ui';
import { api } from '@/lib/api';

export function LoginPage() {
    const [googleLoading, setGoogleLoading] = useState(false);
    const [error, setError] = useState('');

    const handleGoogleLogin = async () => {
        setError('');
        setGoogleLoading(true);

        try {
            const { auth_url } = await api.getGoogleAuthUrl();
            window.location.href = auth_url;
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };
            setError(error.response?.data?.detail || 'Google sign-in failed');
            setGoogleLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col p-4">
            {/* Background effects */}
            <div className="fixed inset-0 fog-overlay pointer-events-none" />

            <div className="flex-1 flex items-center justify-center">
                <div className="w-full max-w-md animate-fade-in">
                    {/* Logo */}
                    <div className="text-center mb-8">
                        <Ghost className="w-16 h-16 text-phantom-500 mx-auto animate-float" />
                        <h1 className="mt-4 font-display text-4xl font-bold text-white">
                            Hide and <span className="text-phantom-400">Seek</span>
                        </h1>
                        <p className="mt-2 text-mist-400">Beyond the bricks of Bergen lies a mystery</p>
                    </div>

                    <Card className="p-6">
                        {error && (
                            <div className="mb-4">
                                <Alert type="error">{error}</Alert>
                            </div>
                        )}

                        <Button
                            type="button"
                            variant="secondary"
                            className="w-full"
                            loading={googleLoading}
                            onClick={handleGoogleLogin}
                        >
                            Sign in with your student email
                        </Button>
                    </Card>

                    <p className="mt-6 text-center text-sm text-mist-500">
                        By signing in, you agree to embrace the mystery.
                    </p>
                </div>
            </div>

            <footer className="text-center text-xs text-mist-600 pb-2">
                Bergen Open Source Foundation | Bergen Community College
            </footer>
        </div>
    );
}
