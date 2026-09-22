import axios from 'axios';

// Create an Axios instance pointing to our FastAPI backend
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Automatically attach the JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;
