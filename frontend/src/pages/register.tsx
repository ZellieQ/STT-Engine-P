import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { register, clearError } from '../store/slices/authSlice';
import { 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Box, 
  Paper, 
  Link, 
  Alert,
  CircularProgress
} from '@mui/material';
import NextLink from 'next/link';

const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [passwordError, setPasswordError] = useState('');
  
  const dispatch = useDispatch<AppDispatch>();
  const router = useRouter();
  
  const { isAuthenticated, isLoading, error } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    // Clear any previous errors
    dispatch(clearError());
    
    // If user is already authenticated, redirect to dashboard
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, dispatch, router]);

  const validateForm = () => {
    if (password !== confirmPassword) {
      setPasswordError('Passwords do not match');
      return false;
    }
    
    if (password.length < 8) {
      setPasswordError('Password must be at least 8 characters long');
      return false;
    }
    
    setPasswordError('');
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    if (username && email && password) {
      const result = await dispatch(register({ 
        username, 
        email, 
        password,
        full_name: fullName || undefined
      }));
      
      if (!result.hasOwnProperty('error')) {
        // Registration successful, redirect to login
        router.push('/login');
      }
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ my: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" align="center" gutterBottom>
            Create an Account
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleSubmit} noValidate>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isLoading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
            />
            <TextField
              margin="normal"
              fullWidth
              id="fullName"
              label="Full Name (Optional)"
              name="fullName"
              autoComplete="name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              disabled={isLoading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              error={!!passwordError}
              helperText={passwordError}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="confirmPassword"
              label="Confirm Password"
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={isLoading}
              error={!!passwordError}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading || !username || !email || !password || !confirmPassword}
            >
              {isLoading ? <CircularProgress size={24} /> : 'Sign Up'}
            </Button>
            
            <Box sx={{ textAlign: 'center' }}>
              <NextLink href="/login" passHref>
                <Link variant="body2">
                  {"Already have an account? Log In"}
                </Link>
              </NextLink>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default RegisterPage;
