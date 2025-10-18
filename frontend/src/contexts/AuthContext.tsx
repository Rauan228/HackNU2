import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { type User, authAPI } from '../services/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    phone?: string;
    user_type: 'job_seeker' | 'employer';
  }) => Promise<void>;
  logout: () => void;
  isEmployer: boolean;
  isJobSeeker: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const response = await authAPI.getMe();
          setUser(response.data);
        } catch (error) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await authAPI.login({ email, password });
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      
      const userResponse = await authAPI.getMe();
      setUser(userResponse.data);
      localStorage.setItem('user', JSON.stringify(userResponse.data));
    } catch (error) {
      throw error;
    }
  };

  const register = async (data: {
    email: string;
    password: string;
    full_name: string;
    phone?: string;
    user_type: 'job_seeker' | 'employer';
  }) => {
    try {
      await authAPI.register(data);
      await login(data.email, data.password);
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const isEmployer = user?.user_type === 'employer';
  const isJobSeeker = user?.user_type === 'job_seeker';

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isEmployer,
    isJobSeeker,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};