import { User, Shield, Sparkles } from 'lucide-react';
import { Card, Badge } from '@/components/ui';
import { useAuthStore } from '@/lib/store';

interface StatItem {
    key: 'decoding' | 'perception' | 'logic' | 'resilience' | 'arcane' | 'insight';
    label: string;
    value: number;
}

export function ProfilePage() {
    const { user } = useAuthStore();

    if (!user) {
        return null;
    }

    const stats: StatItem[] = [
        { key: 'decoding', label: 'Decoding', value: user.decoding },
        { key: 'perception', label: 'Perception', value: user.perception },
        { key: 'logic', label: 'Logic', value: user.logic },
        { key: 'resilience', label: 'Resilience', value: user.resilience },
        { key: 'arcane', label: 'Arcane', value: user.arcane },
        { key: 'insight', label: 'Insight', value: user.insight },
    ];

    const totalAttributes = stats.reduce((sum, stat) => sum + stat.value, 0);

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center gap-3">
                <User className="w-8 h-8 text-phantom-500" />
                <h1 className="page-title">Profile</h1>
            </div>

            <Card className="p-6">
                <div className="flex flex-wrap items-center gap-3">
                    <Badge variant="phantom" className="text-sm">
                        Dog Tag: {user.dog_tag}
                    </Badge>
                    <Badge variant="specter" className="text-sm">
                        Treat: {user.treat}
                    </Badge>
                    <Badge variant="mist" className="text-sm">
                        Total Attributes: {totalAttributes}
                    </Badge>
                </div>
                <p className="text-mist-400 mt-4">{user.email}</p>
            </Card>

            <Card className="p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-specter-400" />
                    Attributes
                </h2>

                <div className="space-y-4">
                    {stats.map((stat) => (
                        <div key={stat.key}>
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-mist-200">{stat.label}</span>
                                <span className="text-mist-400 text-sm">{stat.value}/100</span>
                            </div>
                            <div className="h-2 rounded-full bg-void-200 overflow-hidden">
                                <div
                                    className="h-full bg-linear-to-r from-phantom-500 to-specter-400 transition-all"
                                    style={{ width: `${stat.value}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </Card>

            <Card className="p-6">
                <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <Shield className="w-5 h-5 text-phantom-400" />
                    Account
                </h2>
                <div className="text-sm text-mist-400 space-y-1">
                    <p>Role: {user.role}</p>
                    <p>Status: {user.is_active ? 'Active' : 'Inactive'}</p>
                </div>
            </Card>
        </div>
    );
}
