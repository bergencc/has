import React from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    loading?: boolean;
    children: React.ReactNode;
}

export function Button(
    {
        variant = 'primary',
        size = 'md',
        loading = false,
        disabled,
        className,
        children,
        ...props
    }: ButtonProps
) {
    const baseStyles = 'inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed';

    const variants = {
        primary: 'bg-phantom-600 text-white hover:bg-phantom-500 active:bg-phantom-700 shadow-lg shadow-phantom-900/30',
        secondary: 'bg-void-50 text-mist-200 border border-phantom-800 hover:border-phantom-600 hover:bg-void-100',
        ghost: 'text-mist-300 hover:text-white hover:bg-void-50',
        danger: 'bg-blood-700 text-white hover:bg-blood-600',
    };

    const sizes = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2',
        lg: 'px-6 py-3 text-lg',
    };

    return (
        <button
            className={cn(baseStyles, variants[variant], sizes[size], className)}
            disabled={disabled || loading}
            {...props}
        >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {children}
        </button>
    );
}
