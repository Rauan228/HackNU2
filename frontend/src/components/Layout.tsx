import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LogOut, User, Briefcase, Home, Menu, X, Plus, BarChart3 } from 'lucide-react';
import logo from '../assets/image.png';
interface LayoutProps {
  children: React.ReactNode;
}
const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout, isEmployer, isJobSeeker } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const handleLogout = () => {
    logout();
    navigate('/');
  };
  const isActive = (path: string) => location.pathname === path;
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };
  return (
    <div className="min-h-screen bg-secondary-50">
      {}
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {}
            <Link to="/" className="flex items-center space-x-2">
              <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-primary-700 bg-clip-text text-transparent">
                 <img src={logo} alt="MyLink" className="w-45 h-50 rounded-lg" />
              </span>
            </Link>
            {}
            <nav className="hidden lg:flex space-x-1">
              <Link
                to="/"
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive('/') 
                    ? 'text-primary-600 bg-primary-50 shadow-sm' 
                    : 'text-secondary-700 hover:text-primary-600 hover:bg-secondary-50'
                }`}
              >
                <Home className="h-4 w-4" />
                <span>Главная</span>
              </Link>
              <Link
                to="/jobs"
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive('/jobs') || location.pathname.startsWith('/jobs/')
                    ? 'text-primary-600 bg-primary-50 shadow-sm' 
                    : 'text-secondary-700 hover:text-primary-600 hover:bg-secondary-50'
                }`}
              >
                <Briefcase className="h-4 w-4" />
                <span>Вакансии</span>
              </Link>
              {user && (
                <>
                  {isJobSeeker && (
                    <>
                      <Link
                        to="/profile"
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                          isActive('/profile') 
                            ? 'text-primary-600 bg-primary-50 shadow-sm' 
                            : 'text-secondary-700 hover:text-primary-600 hover:bg-secondary-50'
                        }`}
                      >
                        <User className="h-4 w-4" />
                        <span>Профиль</span>
                      </Link>
                      <Link
                        to="/create-resume"
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                          isActive('/create-resume') 
                            ? 'text-primary-600 bg-primary-50 shadow-sm' 
                            : 'text-secondary-700 hover:text-primary-600 hover:bg-secondary-50'
                        }`}
                      >
                        <Plus className="h-4 w-4" />
                        <span>Создать резюме</span>
                      </Link>
                    </>
                  )}
                  {isEmployer && (
                    <>
                      <Link
                        to="/employer/dashboard"
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                          isActive('/employer/dashboard') 
                            ? 'text-primary-600 bg-primary-50 shadow-sm' 
                            : 'text-secondary-700 hover:text-primary-600 hover:bg-secondary-50'
                        }`}
                      >
                        <BarChart3 className="h-4 w-4" />
                        <span>Панель управления</span>
                      </Link>
                      <Link
                        to="/create-job"
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                          isActive('/create-job') 
                            ? 'text-primary-600 bg-primary-50 shadow-sm' 
                            : 'text-secondary-700 hover:text-primary-600 hover:bg-secondary-50'
                        }`}
                      >
                        <Plus className="h-4 w-4" />
                        <span>Создать вакансию</span>
                      </Link>
                    </>
                  )}
                </>
              )}
            </nav>
            {}
            <div className="hidden lg:flex items-center space-x-4">
              {user ? (
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-3 px-3 py-2 bg-secondary-50 rounded-lg">
                    <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <User className="h-4 w-4 text-primary-600" />
                    </div>
                    <div className="text-left">
                      <p className="text-sm font-medium text-secondary-900">{user.full_name}</p>
                      <p className="text-xs text-secondary-500">
                        {isEmployer ? 'Работодатель' : 'Соискатель'}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-secondary-700 hover:text-danger-600 hover:bg-danger-50 transition-all duration-200"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Выйти</span>
                  </button>
                </div>
              ) : (
                <div className="flex items-center space-x-3">
                  <Link
                    to="/login"
                    className="text-sm font-medium text-secondary-700 hover:text-primary-600 px-3 py-2 rounded-lg hover:bg-secondary-50 transition-all duration-200"
                  >
                    Войти
                  </Link>
                  <Link
                    to="/register"
                    className="bg-gradient-to-r from-primary-600 to-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium hover:from-primary-700 hover:to-primary-800 transition-all duration-200 shadow-sm hover:shadow-md"
                  >
                    Регистрация
                  </Link>
                </div>
              )}
            </div>
            {}
            <div className="lg:hidden">
              <button
                onClick={toggleMobileMenu}
                className="p-2 rounded-lg text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 transition-colors duration-200"
              >
                {isMobileMenuOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <Menu className="h-6 w-6" />
                )}
              </button>
            </div>
          </div>
        </div>
        {}
        {isMobileMenuOpen && (
          <div className="lg:hidden border-t border-secondary-200 bg-white">
            <div className="px-4 py-4 space-y-2">
              <Link
                to="/"
                onClick={() => setIsMobileMenuOpen(false)}
                className={`flex items-center space-x-3 px-3 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive('/') 
                    ? 'text-primary-600 bg-primary-50' 
                    : 'text-secondary-700 hover:text-primary-600 hover:bg-secondary-50'
                }`}
              >
                <Home className="h-5 w-5" />
                <span>Главная</span>
              </Link>
              {}
            </div>
          </div>
        )}
      </header>
      {}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
};
export default Layout;
