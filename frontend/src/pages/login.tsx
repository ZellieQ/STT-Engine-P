import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { login, clearError } from '../store/slices/authSlice';
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

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (username && password) {
      await dispatch(login({ username, password }));
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ my: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" align="center" gutterBottom>
            Log In
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
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading || !username || !password}
            >
              {isLoading ? <CircularProgress size={24} /> : 'Log In'}
            </Button>
            
            <Box sx={{ textAlign: 'center' }}>
              <NextLink href="/register" passHref>
                <Link variant="body2">
                  {"Don't have an account? Sign Up"}
                </Link>
              </NextLink>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;
