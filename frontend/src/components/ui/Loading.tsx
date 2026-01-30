import { Ghost } from 'lucide-react';

interface LoadingProps {
    message?: string;
}

export function Loading({ message = 'Loading...' }: LoadingProps) {
    return (
        <div className="flex flex-col items-center justify-center py-12">
            <Ghost className="w-12 h-12 text-phantom-500 animate-float" />
            <p className="mt-4 text-mist-400 animate-pulse">{message}</p>
        </div>
    );
}

export function LoadingPage() {
    return (
        <div className="min-h-[60vh] flex items-center justify-center">
            <Loading message="Summoning spirits..." />
        </div>
    );
}

export function LoadingSpinner({ className = 'w-5 h-5' }: { className?: string }) {
    return (
        <svg
            className={`animate-spin text-phantom-500 ${className}`}
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
        >
            <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
            />
            <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
        </svg>
    );
}
