import React from 'react';
import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AlertProps {
    type?: 'info' | 'success' | 'warning' | 'error';
    title?: string;
    children: React.ReactNode;
    className?: string;
}

export function Alert({ type = 'info', title, children, className }: AlertProps) {
    const styles = {
        info: {
            container: 'bg-phantom-900/30 border-phantom-700/50 text-phantom-200',
            icon: <Info className="w-5 h-5 text-phantom-400" />,
        },
        success: {
            container: 'bg-specter-900/30 border-specter-700/50 text-specter-200',
            icon: <CheckCircle className="w-5 h-5 text-specter-400" />,
        },
        warning: {
            container: 'bg-yellow-900/30 border-yellow-700/50 text-yellow-200',
            icon: <AlertCircle className="w-5 h-5 text-yellow-400" />,
        },
        error: {
            container: 'bg-blood-900/30 border-blood-700/50 text-blood-200',
            icon: <XCircle className="w-5 h-5 text-blood-400" />,
        },
    };

    const style = styles[type];

    return (
        <div className={cn('flex gap-3 p-4 rounded-lg border', style.container, className)}>
            <div className="shrink-0">{style.icon}</div>
            <div className="flex-1">
                {title && <h4 className="font-semibold mb-1">{title}</h4>}
                <div className="text-sm opacity-90">{children}</div>
            </div>
        </div>
    );
}