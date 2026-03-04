/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Core dark palette
                void: {
                    50: '#1a1a1f',
                    100: '#151518',
                    200: '#111114',
                    300: '#0d0d0f',
                    400: '#09090a',
                    500: '#050506',
                },
                // Spooky purple accent
                phantom: {
                    50: '#f3e8ff',
                    100: '#e4ccff',
                    200: '#c994ff',
                    300: '#a855f7',
                    400: '#8b3fcf',
                    500: '#6b21a8',
                    600: '#581c87',
                    700: '#4a1772',
                    800: '#3b1259',
                    900: '#2d0d45',
                },
                // Eerie green
                specter: {
                    50: '#ecfdf5',
                    100: '#d1fae5',
                    200: '#a7f3d0',
                    300: '#6ee7b7',
                    400: '#34d399',
                    500: '#10b981',
                    600: '#059669',
                    700: '#047857',
                    800: '#065f46',
                    900: '#064e3b',
                },
                // Blood red for alerts
                blood: {
                    50: '#fef2f2',
                    100: '#fee2e2',
                    200: '#fecaca',
                    300: '#fca5a5',
                    400: '#f87171',
                    500: '#ef4444',
                    600: '#dc2626',
                    700: '#b91c1c',
                    800: '#991b1b',
                    900: '#7f1d1d',
                },
                // Ghostly gray
                mist: {
                    50: '#f9fafb',
                    100: '#f3f4f6',
                    200: '#e5e7eb',
                    300: '#d1d5db',
                    400: '#9ca3af',
                    500: '#6b7280',
                    600: '#4b5563',
                    700: '#374151',
                    800: '#1f2937',
                    900: '#111827',
                },
            },
            fontFamily: {
                display: ['Macondo', 'system-ui', 'sans-serif'],
                body: ['Macondo', 'system-ui', 'sans-serif'],
                mono: ['Macondo', 'system-ui', 'sans-serif'],
            },
            boxShadow: {
                'glow-purple': '0 0 20px rgba(139, 63, 207, 0.3)',
                'glow-green': '0 0 20px rgba(16, 185, 129, 0.3)',
                'inner-dark': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.5)',
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'gradient-spooky': 'linear-gradient(135deg, #0d0d0f 0%, #1a1a1f 50%, #2d0d45 100%)',
                'noise': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E\")",
            },
            animation: {
                'float': 'float 6s ease-in-out infinite',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'flicker': 'flicker 3s ease-in-out infinite',
                'fade-in': 'fadeIn 0.5s ease-out',
                'slide-up': 'slideUp 0.4s ease-out',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                flicker: {
                    '0%, 100%': { opacity: '1' },
                    '50%': { opacity: '0.8' },
                },
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
            },
        },
    },
    plugins: [],
}
