import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { LoadingPage } from '@/components/ui';
import { api } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

export function AuthCallbackPage() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { initialize } = useAuthStore();

    useEffect(() => {
        const token = searchParams.get('token');

        if (token) {
            api.setToken(token);

            initialize().then(() => {
                navigate('/');
            });
        } else {
            navigate('/login');
        }
    }, [searchParams, navigate, initialize]);

    return <LoadingPage />;
}