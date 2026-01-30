import React from 'react';
import { cn } from '@/lib/utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ label, error, className, ...props }, ref) => {
        return (
            <div className="w-full">
                {label && (
                    <label className="block text-sm font-medium text-mist-300 mb-2">
                        {label}
                    </label>
                )}
                <input
                    ref={ref}
                    className={cn(
                        'w-full px-4 py-3 bg-void-200 border border-phantom-900/30 rounded-lg',
                        'text-mist-100 placeholder:text-mist-600',
                        'focus:outline-none focus:border-phantom-600 focus:ring-1 focus:ring-phantom-600',
                        'transition-colors',
                        error && 'border-blood-600 focus:border-blood-500 focus:ring-blood-500',
                        className
                    )}
                    {...props}
                />
                {error && (
                    <p className="mt-1.5 text-sm text-blood-400">{error}</p>
                )}
            </div>
        );
    }
);

Input.displayName = 'Input';