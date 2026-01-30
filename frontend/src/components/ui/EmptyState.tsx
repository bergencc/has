import React from 'react';
import { Ghost } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
    icon?: React.ReactNode;
    title: string;
    description?: string;
    action?: React.ReactNode;
    className?: string;
}

export function EmptyState(
    {
        icon,
        title,
        description,
        action,
        className,
    }: EmptyStateProps
) {
    return (
        <div className={cn('flex flex-col items-center justify-center py-12 text-center', className)}>
            <div className="w-16 h-16 rounded-full bg-void-50 flex items-center justify-center mb-4">
                {icon || <Ghost className="w-8 h-8 text-phantom-500" />}
            </div>
            <h3 className="text-lg font-semibold text-mist-200">{title}</h3>
            {description && (
                <p className="mt-2 text-mist-400 max-w-sm">{description}</p>
            )}
            {action && <div className="mt-4">{action}</div>}
        </div>
    );
}