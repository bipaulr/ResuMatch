import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { ReactNode } from 'react';
import { authService } from '../services/authService';
import { setToken, removeToken, getUserFromToken } from '../utils/auth';
import type { User, AuthContextType, SignupData } from '../types';

// Auth state management
interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'SET_USER'; payload: User }
  | { type: 'CLEAR_ERROR' };

const initialState: AuthState = {
  user: null,
  token: null,
  loading: false,
  error: null,
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, loading: true, error: null };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        loading: false,
        user: action.payload.user,
        token: action.payload.token,
        error: null,
      };
    case 'LOGIN_FAILURE':
      return { ...state, loading: false, error: action.payload };
    case 'LOGOUT':
      return { ...initialState };
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
};

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
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state from localStorage
  useEffect(() => {
    const user = getUserFromToken();
    const token = localStorage.getItem('token');
    if (user) {
      dispatch({ type: 'SET_USER', payload: user });
    }
    if (token) {
      // Hydrate token in state so consumers like ChatContext have it
      dispatch({ type: 'LOGIN_SUCCESS', payload: { user: user as any, token } });
    }
  }, []);

  const login = async (email: string, password: string) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await authService.login({ email, password });
      setToken(response.access_token);
      
      // Extract user info from JWT token
      const userFromToken = getUserFromToken();
      if (!userFromToken) {
        const error = new Error('Invalid token received');
        dispatch({ type: 'LOGIN_FAILURE', payload: 'Invalid token received' });
        return { success: false, error: error.message };
      }
      
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user: userFromToken, token: response.access_token },
      });
      return { success: true };
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      dispatch({ type: 'LOGIN_FAILURE', payload: errorMessage });
      return { success: false, error: errorMessage, originalError: error };
    }
  };

  const signup = async (userData: SignupData) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await authService.signup(userData);
      
      // Signup doesn't return tokens, so we need to login after signup
      if (response.access_token) {
        setToken(response.access_token);
        
        // Extract user info from JWT token
        const userFromToken = getUserFromToken();
        if (!userFromToken) {
          throw new Error('Invalid token received');
        }
        
        dispatch({
          type: 'LOGIN_SUCCESS',
          payload: { user: userFromToken, token: response.access_token },
        });
      } else {
        // If no token returned, login with the new credentials
        const loginResult = await login(userData.email, userData.password);
        if (!loginResult.success) {
          throw new Error(loginResult.error || 'Failed to login after signup');
        }
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Signup failed';
      dispatch({ type: 'LOGIN_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  const logout = () => {
    removeToken();
    dispatch({ type: 'LOGOUT' });
  };

  const value: AuthContextType = {
    user: state.user,
    token: state.token,
    login,
    signup,
    logout,
    loading: state.loading,
    error: state.error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
