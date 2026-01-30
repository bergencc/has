import React from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
    variant?: 'phantom' | 'specter' | 'blood' | 'mist';
    children: React.ReactNode;
}

export function Badge({ variant = 'phantom', className, children, ...props }: BadgeProps) {
    const variants = {
        phantom: 'bg-phantom-900/50 text-phantom-300 border border-phantom-700/30',
        specter: 'bg-specter-900/50 text-specter-400 border border-specter-700/30',
        blood: 'bg-blood-900/50 text-blood-400 border border-blood-700/30',
        mist: 'bg-mist-800/50 text-mist-300 border border-mist-600/30',
    };

    return (
        <span
            className={cn(
                'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                variants[variant],
                className
            )}
            {...props}
        >
      {children}
    </span>
    );
}
