export const API_BASE_URL = 'http://localhost:8000';

export const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const setToken = (token: string) => {
  localStorage.setItem('token', token);
};

export const getToken = (): string | null => {
  return localStorage.getItem('token');
};

export const removeToken = () => {
  localStorage.removeItem('token');
};

export const isAuthenticated = (): boolean => {
  return !!getToken();
};

export const getUserFromToken = () => {
  const token = getToken();
  if (!token) return null;
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return {
      id: payload.sub, // Use sub as the user ID
      username: payload.username, // Now included in token
      email: payload.email, // Now included in token
      role: payload.role,
    };
  } catch (error) {
    console.error('Error parsing token:', error);
    removeToken();
    return null;
  }
};
