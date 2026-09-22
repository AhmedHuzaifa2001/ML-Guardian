import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  // Check if the user has a JWT token saved in their browser
  const token = localStorage.getItem('token');
  
  if (!token) {
    // If they don't have a token, kick them back to the login page immediately
    return <Navigate to="/login" replace />;
  }
  
  // If they do have a token, render the page they requested (like Chat)
  return children;
}
