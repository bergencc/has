import { Outlet } from 'react-router-dom';
import { Header } from './Header';

export function Layout() {
    return (
        <div className="min-h-screen flex flex-col">
            <Header />
            <main className="flex-1">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <Outlet />
                </div>
            </main>
            <footer className="border-t border-phantom-900/20 py-6">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <p className="text-center text-mist-500 text-sm">
                        &copy; {new Date().getFullYear()} Hide and Seek. SGA, SAB and BOSF.
                    </p>
                </div>
            </footer>
        </div>
    );
}
