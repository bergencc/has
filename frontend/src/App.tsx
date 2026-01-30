import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from '@/components/layout';
import { LoadingPage } from '@/components/ui';
import {
    LoginPage,
    AuthCallbackPage,
    DashboardPage,
    TeamPage,
    EventsPage,
    EventDetailPage,
    TeamRankingsPage,
    AdminPage,
    AdminEventPage,
} from '@/pages';
import { useAuthStore } from '@/lib/store';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, isLoading } = useAuthStore();

    if (isLoading) {
        return <LoadingPage />;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
}

function AdminRoute({ children }: { children: React.ReactNode }) {
    const { user, isAuthenticated, isLoading } = useAuthStore();

    if (isLoading) {
        return <LoadingPage />;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (user?.role !== 'admin') {
        return <Navigate to="/" replace />;
    }

    return <>{children}</>;
}

export default function App() {
    const { initialize, isLoading } = useAuthStore();

    useEffect(() => {
        initialize();
    }, [initialize]);

    if (isLoading) {
        return <LoadingPage />;
    }

    return (
        <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/auth/callback" element={<AuthCallbackPage />} />

            {/* Protected routes */}
            <Route
                element={
                    <ProtectedRoute>
                        <Layout />
                    </ProtectedRoute>
                }
            >
                <Route path="/" element={<DashboardPage />} />
                <Route path="/team" element={<TeamPage />} />
                <Route path="/rankings" element={<TeamRankingsPage />} />
                <Route path="/events" element={<EventsPage />} />
                <Route path="/events/:eventId" element={<EventDetailPage />} />
            </Route>

            {/* Admin routes */}
            <Route
                path="/admin"
                element={
                    <AdminRoute>
                        <Layout />
                    </AdminRoute>
                }
            >
                <Route index element={<AdminPage />} />
                <Route path="events/:eventId" element={<AdminEventPage />} />
            </Route>

            {/* Catch all */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}
