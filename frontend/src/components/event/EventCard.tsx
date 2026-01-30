import { Calendar, Users, Clock, Trophy } from 'lucide-react';
import { Card, Badge } from '../ui';
import { formatDate, formatTimeRemaining } from '@/lib/utils';
import type { Event, EventListItem } from '@/lib/types';

interface EventCardProps {
    event: Event | EventListItem;
    onClick?: () => void;
}

export function EventCard({ event, onClick }: EventCardProps) {
    const getStatusBadge = () => {
        if (event.is_active) {
            return <Badge variant="specter">Live</Badge>;
        }

        if (event.is_registration_open) {
            return <Badge variant="phantom">Registration Open</Badge>;
        }

        if (event.status === 'completed') {
            return <Badge variant="mist">Completed</Badge>;
        }

        if (event.status === 'cancelled') {
            return <Badge variant="blood">Cancelled</Badge>;
        }

        return <Badge variant="mist">{event.status}</Badge>;
    };

    return (
        <Card hover={!!onClick} onClick={onClick} className="p-5">
            <div className="flex items-start justify-between mb-3">
                <div>
                    <h3 className="text-lg font-display font-semibold text-white">{event.title}</h3>
                    <p className="text-sm text-phantom-400 font-mono">{event.code}</p>
                </div>
                {getStatusBadge()}
            </div>

            <div className="space-y-2 text-sm text-mist-400">
                <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>
            {formatDate(event.starts_at)} - {formatDate(event.ends_at)}
          </span>
                </div>

                <div className="flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    <span>{event.registered_teams_count} teams registered</span>
                </div>

                {event.is_active && (
                    <div className="flex items-center gap-2 text-specter-400">
                        <Clock className="w-4 h-4" />
                        <span>{formatTimeRemaining(event.ends_at)}</span>
                    </div>
                )}

                {event.status === 'completed' && (
                    <div className="flex items-center gap-2 text-phantom-400">
                        <Trophy className="w-4 h-4" />
                        <span>View results</span>
                    </div>
                )}
            </div>
        </Card>
    );
}
