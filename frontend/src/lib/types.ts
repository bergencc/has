export interface User {
    id: number;
    email: string;
    dog_tag: string;
    decoding: number;
    perception: number;
    logic: number;
    resilience: number;
    arcane: number;
    insight: number;
    treat: number;
    institution: string | null;
    role: 'student' | 'admin';
    is_active: boolean;
    created_at: string;
}

export interface UserPublic {
    id: number;
    dog_tag: string;
}

export interface TeamMember {
    id: number;
    user: UserPublic;
    role: 'member' | 'captain';
    joined_at: string;
    lock_expires_at: string;
    is_locked: boolean;
    can_leave: boolean;
}

export interface Team {
    id: number;
    name: string;
    description: string | null;
    created_at: string;
    disbanded_at: string | null;
    members: TeamMember[];
    member_count: number;
}

export interface TeamListItem {
    id: number;
    name: string;
    description: string | null;
    member_count: number;
    created_at: string;
}

export interface TeamRankingEntry {
    rank: number;
    team_id: number;
    team_name: string;
    member_count: number;
    events_registered: number;
    total_points: number;
    completed_challenges: number;
    hints_used: number;
    hint_usage_score: number | null;
}

export interface JoinRequestVote {
    id: number;
    voter: UserPublic;
    vote: 'accept' | 'reject';
    voted_at: string;
}

export interface JoinRequest {
    id: number;
    team_id: number;
    team_name: string;
    user: UserPublic;
    requested_at: string;
    expires_at: string;
    status: 'pending' | 'accepted' | 'rejected' | 'expired' | 'cancelled';
    resolved_at: string | null;
    votes: JoinRequestVote[];
    votes_needed: number;
    votes_received: number;
}

export interface TeamMembershipStatus {
    has_team: boolean;
    team: Team | null;
    membership: TeamMember | null;
    pending_requests: JoinRequest[];
}

export interface Event {
    id: number;
    title: string;
    description: string | null;
    code: string;
    starts_at: string;
    ends_at: string;
    registration_opens_at: string | null;
    registration_closes_at: string | null;
    min_team_size: number;
    max_team_size: number;
    ranking_point: number;
    treat_point: number;
    decoding_point: number;
    perception_point: number;
    logic_point: number;
    resilience_point: number;
    arcane_point: number;
    insight_point: number;
    team_lock_mode: 'open' | 'locked';
    rules: Record<string, unknown> | null;
    status: 'draft' | 'registration' | 'active' | 'completed' | 'cancelled';
    is_registration_open: boolean;
    is_active: boolean;
    created_by: number;
    created_at: string;
    updated_at: string;
    registered_teams_count: number;
    challenges_count: number;
}

export interface EventListItem {
    id: number;
    title: string;
    code: string;
    status: string;
    starts_at: string;
    ends_at: string;
    is_registration_open: boolean;
    is_active: boolean;
    registered_teams_count: number;
}

export interface EventRegistration {
    id: number;
    event_id: number;
    team: TeamListItem;
    registered_at: string;
    status: string;
}

export interface LeaderboardEntry {
    rank: number;
    team_id: number;
    team_name: string;
    total_points: number;
    completed_challenges: number;
    total_time_seconds: number | null;
    hints_used: number;
    wrong_attempts: number;
}

export interface EventLeaderboard {
    event_id: number;
    event_title: string;
    entries: LeaderboardEntry[];
    updated_at: string;
}

export interface Challenge {
    id: number;
    event_id: number;
    type: 'riddle' | 'scavenger_code';
    title: string;
    prompt: string;
    ranking_point: number;
    treat_point: number;
    decoding_point: number;
    perception_point: number;
    logic_point: number;
    resilience_point: number;
    arcane_point: number;
    insight_point: number;
    hint_cost: number;
    max_attempts: number | null;
    point_decay_per_attempt: number;
    hints_available: number;
    sort_order: number;
    is_active: boolean;
}

export interface ChallengeStatus {
    challenge: Challenge;
    is_unlocked: boolean;
    is_solved: boolean;
    attempts_made: number;
    hints_used: number;
    hints_revealed: string[];
    points_possible: number;
    solved_at: string | null;
    points_awarded: number | null;
}

export interface AttemptResponse {
    id: number;
    challenge_id: number;
    is_correct: boolean;
    points_awarded: number;
    submitted_at: string;
    message: string;
    attempts_remaining: number | null;
}

export interface HintResponse {
    hint_index: number;
    hint_text: string;
    penalty_applied: number;
    hints_remaining: number;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
    user: User;
}
