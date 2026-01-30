import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    hover?: boolean;
    children: React.ReactNode;
}

export function Card({ hover = false, className, children, ...props }: CardProps) {
    return (
        <div
            className={cn(
                'bg-void-100/80 backdrop-blur-sm border border-phantom-900/30 rounded-xl',
                hover && 'transition-all duration-300 hover:border-phantom-700/50 hover:shadow-glow-purple cursor-pointer',
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
}

export function CardHeader({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn('px-6 py-4 border-b border-phantom-900/20', className)} {...props}>
            {children}
        </div>
    );
}

export function CardContent({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn('px-6 py-4', className)} {...props}>
            {children}
        </div>
    );
}

export function CardFooter({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn('px-6 py-4 border-t border-phantom-900/20', className)} {...props}>
            {children}
        </div>
    );
}
