import React from 'react';
import type { ReactNode } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, Briefcase, MessageCircle, BarChart3 } from 'lucide-react';
import { DarkModeToggle } from './DarkModeToggle';

interface LayoutProps {
  children: ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Navigation */}
      <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary-600 dark:bg-primary-500 rounded flex items-center justify-center transition-colors duration-200">
                  <span className="text-white font-bold text-sm">RM</span>
                </div>
                <span className="font-bold text-xl text-gray-900 dark:text-gray-100 transition-colors duration-200">ResuMatch</span>
              </Link>
            </div>

            {user && (
              <div className="flex items-center space-x-4">
                {/* Navigation Links */}
                <div className="hidden md:flex items-center space-x-4">
                  {user.role === 'student' && (
                    <>
                      <Link
                        to="/dashboard"
                        className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1 transition-colors duration-200"
                      >
                        <BarChart3 size={16} />
                        <span>Dashboard</span>
                      </Link>
                      <Link
                        to="/jobs"
                        className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1 transition-colors duration-200"
                      >
                        <Briefcase size={16} />
                        <span>Jobs</span>
                      </Link>
                      <Link
                        to="/resume-upload"
                        className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1 transition-colors duration-200"
                      >
                        <User size={16} />
                        <span>Resume</span>
                      </Link>
                    </>
                  )}
                  
                  {user.role === 'recruiter' && (
                    <>
                      <Link
                        to="/recruiter-dashboard"
                        className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1 transition-colors duration-200"
                      >
                        <BarChart3 size={16} />
                        <span>Dashboard</span>
                      </Link>
                      <Link
                        to="/post-job"
                        className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1 transition-colors duration-200"
                      >
                        <Briefcase size={16} />
                        <span>Post Job</span>
                      </Link>
                    </>
                  )}
                  
                  <Link
                    to="/chat"
                    className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1 transition-colors duration-200"
                  >
                    <MessageCircle size={16} />
                    <span>Chat</span>
                  </Link>
                </div>

                {/* User Menu */}
                <div className="flex items-center space-x-3">
                  <DarkModeToggle size="sm" />
                  
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center transition-colors duration-200">
                      <User size={16} className="text-primary-600 dark:text-primary-400" />
                    </div>
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300 hidden sm:block transition-colors duration-200">
                      {user.username}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-full hidden sm:block transition-colors duration-200">
                      {user.role}
                    </span>
                  </div>
                  
                  <button
                    onClick={handleLogout}
                    className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 p-2 rounded-md transition-colors duration-200"
                    title="Logout"
                  >
                    <LogOut size={16} />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
};
