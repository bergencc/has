import { create } from 'zustand';
import { api } from './api';
import type { User } from './types';

interface AuthState {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;

    // Actions
    initialize: () => Promise<void>;
    login: (email: string, nickname: string) => Promise<void>;
    logout: () => void;
    updateUser: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
    user: null,
    isLoading: true,
    isAuthenticated: false,

    initialize: async () => {
        if (!api.isAuthenticated()) {
            set({ isLoading: false, isAuthenticated: false });

            return;
        }

        try {
            const user = await api.getMe();

            set({ user, isLoading: false, isAuthenticated: true });
        } catch {
            api.clearAuth();

            set({ user: null, isLoading: false, isAuthenticated: false });
        }
    },

    login: async (email: string, nickname: string) => {
        const response = await api.devLogin(email, nickname);

        set({ user: response.user, isAuthenticated: true });
    },

    logout: () => {
        api.clearAuth();

        set({ user: null, isAuthenticated: false });
    },

    updateUser: (updates: Partial<User>) => {
        const { user } = get();

        if (user) {
            set({ user: { ...user, ...updates } });
        }
    },
}));
