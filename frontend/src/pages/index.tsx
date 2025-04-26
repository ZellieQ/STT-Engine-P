import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { Container, Typography, Button, Box, Paper } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import HistoryIcon from '@mui/icons-material/History';

const HomePage = () => {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  const router = useRouter();

  useEffect(() => {
    // If user is authenticated, redirect to dashboard
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4, textAlign: 'center' }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Speech-to-Text Transcription Service
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Convert spoken language into written text with high accuracy
        </Typography>
        
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
          <Button 
            variant="contained" 
            size="large" 
            onClick={() => router.push('/login')}
            sx={{ mx: 2 }}
          >
            Log In
          </Button>
          <Button 
            variant="outlined" 
            size="large" 
            onClick={() => router.push('/register')}
            sx={{ mx: 2 }}
          >
            Sign Up
          </Button>
        </Box>
      </Box>

      <Box sx={{ my: 8 }}>
        <Typography variant="h4" component="h2" gutterBottom textAlign="center">
          Key Features
        </Typography>
        
        <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 4, mt: 4 }}>
          <Paper elevation={3} sx={{ p: 3, width: 300, textAlign: 'center' }}>
            <MicIcon color="primary" sx={{ fontSize: 60, mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Real-time Transcription
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Convert speech to text in real-time with minimal latency.
            </Typography>
          </Paper>
          
          <Paper elevation={3} sx={{ p: 3, width: 300, textAlign: 'center' }}>
            <CloudUploadIcon color="primary" sx={{ fontSize: 60, mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Batch Processing
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Upload audio files for high-accuracy transcription.
            </Typography>
          </Paper>
          
          <Paper elevation={3} sx={{ p: 3, width: 300, textAlign: 'center' }}>
            <HistoryIcon color="primary" sx={{ fontSize: 60, mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Multiple Languages
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Support for multiple languages and custom vocabularies.
            </Typography>
          </Paper>
        </Box>
      </Box>

      <Box sx={{ my: 8, textAlign: 'center' }}>
        <Typography variant="h4" component="h2" gutterBottom>
          How It Works
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 4, width: '100%', maxWidth: 800 }}>
            <Box sx={{ 
              width: 50, 
              height: 50, 
              borderRadius: '50%', 
              bgcolor: 'primary.main', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              color: 'white',
              mr: 2
            }}>
              1
            </Box>
            <Typography variant="body1">
              Upload your audio file or start real-time recording.
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 4, width: '100%', maxWidth: 800 }}>
            <Box sx={{ 
              width: 50, 
              height: 50, 
              borderRadius: '50%', 
              bgcolor: 'primary.main', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              color: 'white',
              mr: 2
            }}>
              2
            </Box>
            <Typography variant="body1">
              Our advanced AI processes the audio and converts it to text.
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 4, width: '100%', maxWidth: 800 }}>
            <Box sx={{ 
              width: 50, 
              height: 50, 
              borderRadius: '50%', 
              bgcolor: 'primary.main', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              color: 'white',
              mr: 2
            }}>
              3
            </Box>
            <Typography variant="body1">
              Review, edit, and export your transcription in various formats.
            </Typography>
          </Box>
        </Box>
        
        <Button 
          variant="contained" 
          size="large" 
          onClick={() => router.push('/register')}
          sx={{ mt: 4 }}
        >
          Get Started Now
        </Button>
      </Box>
    </Container>
  );
};

export default HomePage;
