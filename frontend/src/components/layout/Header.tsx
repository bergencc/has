import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Ghost, Menu, X, LogOut, User, Users, Calendar, Trophy } from 'lucide-react';
import { useAuthStore } from '@/lib/store';
import { Button } from '../ui/Button';

export function Header() {
    const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
    const { user, isAuthenticated, logout } = useAuthStore();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <header className="sticky top-0 z-40 bg-void-200/80 backdrop-blur-md border-b border-phantom-900/20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2 group">
                        <Ghost className="w-8 h-8 text-phantom-500 group-hover:animate-float transition-all" />
                        <span className="font-display text-xl font-bold text-white">
              Hide and <span className="text-phantom-400">Seek</span>
            </span>
                    </Link>

                    {/* Desktop Nav */}
                    <nav className="hidden md:flex items-center gap-6">
                        {isAuthenticated ? (
                            <>
                                <Link
                                    to="/events"
                                    className="flex items-center gap-2 text-mist-300 hover:text-white transition-colors"
                                >
                                    <Calendar className="w-4 h-4" />
                                    Events
                                </Link>
                                <Link
                                    to="/team"
                                    className="flex items-center gap-2 text-mist-300 hover:text-white transition-colors"
                                >
                                    <Users className="w-4 h-4" />
                                    Team
                                </Link>
                                <Link
                                    to="/rankings"
                                    className="flex items-center gap-2 text-mist-300 hover:text-white transition-colors"
                                >
                                    <Trophy className="w-4 h-4" />
                                    Rankings
                                </Link>
                                {user?.role === 'admin' && (
                                    <Link
                                        to="/admin"
                                        className="text-phantom-400 hover:text-phantom-300 transition-colors"
                                    >
                                        Admin
                                    </Link>
                                )}
                                <div className="flex items-center gap-3 pl-4 border-l border-phantom-800">
                                    <Link
                                        to="/profile"
                                        className="text-mist-300 text-sm hover:text-white transition-colors"
                                    >
                                        <User className="w-4 h-4 inline mr-1" />
                                        {user?.dog_tag}
                                    </Link>
                                    <Button variant="ghost" size="sm" onClick={handleLogout}>
                                        <LogOut className="w-4 h-4" />
                                    </Button>
                                </div>
                            </>
                        ) : (
                            <Link to="/login">
                                <Button variant="primary">Sign In</Button>
                            </Link>
                        )}
                    </nav>

                    {/* Mobile menu button */}
                    <button
                        className="md:hidden p-2 text-mist-300 hover:text-white"
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    >
                        {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </button>
                </div>
            </div>

            {/* Mobile menu */}
            {mobileMenuOpen && (
                <div className="md:hidden bg-void-100 border-t border-phantom-900/20 animate-slide-up">
                    <div className="px-4 py-4 space-y-3">
                        {isAuthenticated ? (
                            <>
                                <div className="pb-3 mb-3 border-b border-phantom-900/20">
                  <span className="text-mist-300 text-sm">
                    Signed in as <strong className="text-white">{user?.dog_tag}</strong>
                  </span>
                                </div>
                                <Link
                                    to="/profile"
                                    className="block px-3 py-2 rounded-lg text-mist-200 hover:bg-void-50"
                                    onClick={() => setMobileMenuOpen(false)}
                                >
                                    <User className="w-4 h-4 inline mr-2" />
                                    Profile
                                </Link>
                                <Link
                                    to="/events"
                                    className="block px-3 py-2 rounded-lg text-mist-200 hover:bg-void-50"
                                    onClick={() => setMobileMenuOpen(false)}
                                >
                                    <Calendar className="w-4 h-4 inline mr-2" />
                                    Events
                                </Link>
                                <Link
                                    to="/team"
                                    className="block px-3 py-2 rounded-lg text-mist-200 hover:bg-void-50"
                                    onClick={() => setMobileMenuOpen(false)}
                                >
                                    <Users className="w-4 h-4 inline mr-2" />
                                    Team
                                </Link>
                                <Link
                                    to="/rankings"
                                    className="block px-3 py-2 rounded-lg text-mist-200 hover:bg-void-50"
                                    onClick={() => setMobileMenuOpen(false)}
                                >
                                    <Trophy className="w-4 h-4 inline mr-2" />
                                    Rankings
                                </Link>
                                {user?.role === 'admin' && (
                                    <Link
                                        to="/admin"
                                        className="block px-3 py-2 rounded-lg text-phantom-400 hover:bg-void-50"
                                        onClick={() => setMobileMenuOpen(false)}
                                    >
                                        Admin Dashboard
                                    </Link>
                                )}
                                <button
                                    className="w-full text-left px-3 py-2 rounded-lg text-blood-400 hover:bg-void-50"
                                    onClick={handleLogout}
                                >
                                    <LogOut className="w-4 h-4 inline mr-2" />
                                    Sign Out
                                </button>
                            </>
                        ) : (
                            <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                                <Button variant="primary" className="w-full">
                                    Sign In
                                </Button>
                            </Link>
                        )}
                    </div>
                </div>
            )}
        </header>
    );
}
