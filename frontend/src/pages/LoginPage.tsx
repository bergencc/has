import React, { useState } from 'react';
import { Ghost } from 'lucide-react';
import { Button, Card } from '@/components/ui';

export function LoginPage() {
    const [googleLoading, setGoogleLoading] = useState(false);

    const handleGoogleLogin = () => {
        setGoogleLoading(true);
        window.location.href = '/api/auth/google';
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
