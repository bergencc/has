import axios, { AxiosError, type AxiosInstance } from 'axios';
import type {
    User,
    Team,
    TeamListItem,
    TeamMembershipStatus,
    JoinRequest,
    Event,
    EventListItem,
    EventRegistration,
    EventLeaderboard,
    ChallengeStatus,
    AttemptResponse,
    HintResponse,
    TokenResponse,
    TeamRankingEntry,
} from './types';

const API_BASE = '/api';

class ApiClient {
    private client: AxiosInstance;
    private token: string | null = null;

    constructor() {
        this.client = axios.create({
            baseURL: API_BASE,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Load token from storage
        this.token = localStorage.getItem('auth_token');
        if (this.token) {
            this.setAuthHeader(this.token);
        }

        // Response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            (error: AxiosError) => {
                if (error.response?.status === 401) {
                    this.clearAuth();
                    window.location.href = '/login';
                }

                return Promise.reject(error);
            }
        );
    }

    private setAuthHeader(token: string) {
        this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }

    setToken(token: string) {
        this.token = token;

        localStorage.setItem('auth_token', token);

        this.setAuthHeader(token);
    }

    clearAuth() {
        this.token = null;

        localStorage.removeItem('auth_token');

        delete this.client.defaults.headers.common['Authorization'];
    }

    isAuthenticated(): boolean {
        return !!this.token;
    }

    // Auth endpoints
    async getGoogleAuthUrl(): Promise<{ auth_url: string }> {
        const { data } = await this.client.get('/auth/google');

        return data;
    }

    async devLogin(email: string, nickname: string): Promise<TokenResponse> {
        const { data } = await this.client.post('/auth/dev-login', null, {
            params: { email, nickname },
        });

        this.setToken(data.access_token);

        return data;
    }

    async getMe(): Promise<User> {
        const { data } = await this.client.get('/auth/me');

        return data;
    }

    async updateMe(update: { nickname?: string }): Promise<User> {
        const { data } = await this.client.patch('/auth/me', update);

        return data;
    }

    // Team endpoints
    async getMyTeamStatus(): Promise<TeamMembershipStatus> {
        const { data } = await this.client.get('/teams/my-status');

        return data;
    }

    async createTeam(name: string, description?: string): Promise<Team> {
        const { data } = await this.client.post('/teams', { name, description });

        return data;
    }

    async listTeams(search?: string, limit = 20, offset = 0): Promise<TeamListItem[]> {
        const { data } = await this.client.get('/teams', {
            params: { search, limit, offset },
        });

        return data;
    }

    async getTeamRankings(): Promise<TeamRankingEntry[]> {
        const { data } = await this.client.get('/teams/rankings');

        return data;
    }

    async getTeam(teamId: number): Promise<Team> {
        const { data } = await this.client.get(`/teams/${teamId}`);

        return data;
    }

    async requestToJoinTeam(teamId: number): Promise<JoinRequest> {
        const { data } = await this.client.post(`/teams/${teamId}/join-request`);

        return data;
    }

    async getTeamJoinRequests(teamId: number): Promise<JoinRequest[]> {
        const { data } = await this.client.get(`/teams/${teamId}/join-requests`);

        return data;
    }

    async voteOnJoinRequest(requestId: number, vote: 'accept' | 'reject'): Promise<JoinRequest> {
        const { data } = await this.client.post(`/teams/join-requests/${requestId}/vote`, { vote });

        return data;
    }

    async cancelJoinRequest(requestId: number): Promise<void> {
        await this.client.post(`/teams/join-requests/${requestId}/cancel`);
    }

    async leaveTeam(teamId: number): Promise<void> {
        await this.client.post(`/teams/${teamId}/leave`);
    }

    // Event endpoints
    async listEvents(statusFilter?: string, includePast = false): Promise<EventListItem[]> {
        const { data } = await this.client.get('/events', {
            params: { status_filter: statusFilter, include_past: includePast },
        });

        return data;
    }

    async getEvent(eventId: number): Promise<Event> {
        const { data } = await this.client.get(`/events/${eventId}`);

        return data;
    }

    async getEventByCode(code: string): Promise<Event> {
        const { data } = await this.client.get(`/events/code/${code}`);

        return data;
    }

    async registerForEvent(eventId: number): Promise<EventRegistration> {
        const { data } = await this.client.post(`/events/${eventId}/register`);

        return data;
    }

    async getEventRegistrations(eventId: number): Promise<EventRegistration[]> {
        const { data } = await this.client.get(`/events/${eventId}/registrations`);

        return data;
    }

    async getEventLeaderboard(eventId: number): Promise<EventLeaderboard> {
        const { data } = await this.client.get(`/events/${eventId}/leaderboard`);

        return data;
    }

    async withdrawFromEvent(eventId: number): Promise<void> {
        await this.client.post(`/events/${eventId}/withdraw`);
    }

    // Challenge endpoints
    async getEventChallenges(eventId: number): Promise<ChallengeStatus[]> {
        const { data } = await this.client.get(`/challenges/event/${eventId}`);

        return data;
    }

    async submitAnswer(challengeId: number, answer: string): Promise<AttemptResponse> {
        const { data } = await this.client.post('/challenges/submit', {
            challenge_id: challengeId,
            answer,
        });

        return data;
    }

    async requestHint(challengeId: number): Promise<HintResponse> {
        const { data } = await this.client.post('/challenges/hint', {
            challenge_id: challengeId,
        });

        return data;
    }

    // Admin endpoints
    async createEvent(eventData: Partial<Event>): Promise<Event> {
        const { data } = await this.client.post('/events', eventData);

        return data;
    }

    async updateEvent(eventId: number, eventData: Partial<Event>): Promise<Event> {
        const { data } = await this.client.patch(`/events/${eventId}`, eventData);

        return data;
    }

    async getAdminChallenges(eventId: number): Promise<unknown[]> {
        const { data } = await this.client.get(`/challenges/admin/event/${eventId}`);

        return data;
    }

    async createChallenge(challengeData: unknown): Promise<unknown> {
        const { data } = await this.client.post('/challenges', challengeData);

        return data;
    }

    async updateChallenge(challengeId: number, challengeData: unknown): Promise<unknown> {
        const { data } = await this.client.patch(`/challenges/${challengeId}`, challengeData);

        return data;
    }

    async deleteChallenge(challengeId: number): Promise<void> {
        await this.client.delete(`/challenges/${challengeId}`);
    }
}

export const api = new ApiClient();
