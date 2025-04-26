import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchTranscriptions } from '../store/slices/transcriptionSlice';
import { fetchUserProfile } from '../store/slices/authSlice';
import { 
  Container, 
  Typography, 
  Box, 
  Tabs, 
  Tab, 
  CircularProgress,
  Alert
} from '@mui/material';
import TranscriptionList from '../components/TranscriptionList';
import UploadTranscription from '../components/UploadTranscription';
import RecordTranscription from '../components/RecordTranscription';
import Header from '../components/Header';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const Dashboard = () => {
  const [tabValue, setTabValue] = useState(0);
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  
  const { isAuthenticated, isLoading: authLoading, user } = useSelector((state: RootState) => state.auth);
  const { transcriptions, isLoading: transcriptionsLoading, error } = useSelector((state: RootState) => state.transcription);

  useEffect(() => {
    // If user is not authenticated, redirect to login
    if (!isAuthenticated && !authLoading) {
      router.push('/login');
      return;
    }

    // Fetch user profile and transcriptions
    if (isAuthenticated) {
      dispatch(fetchUserProfile());
      dispatch(fetchTranscriptions());
    }
  }, [isAuthenticated, authLoading, dispatch, router]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (authLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <>
      <Header />
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Dashboard
          </Typography>
          {user && (
            <Typography variant="subtitle1" color="text.secondary">
              Welcome back, {user.full_name || user.username}!
            </Typography>
          )}
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="dashboard tabs">
            <Tab label="My Transcriptions" id="tab-0" aria-controls="tabpanel-0" />
            <Tab label="Upload Audio" id="tab-1" aria-controls="tabpanel-1" />
            <Tab label="Record Audio" id="tab-2" aria-controls="tabpanel-2" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <TranscriptionList 
            transcriptions={transcriptions} 
            isLoading={transcriptionsLoading} 
          />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <UploadTranscription onSuccess={() => setTabValue(0)} />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <RecordTranscription onSuccess={() => setTabValue(0)} />
        </TabPanel>
      </Container>
    </>
  );
};

export default Dashboard;
