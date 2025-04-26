import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { uploadTranscription } from '../store/slices/transcriptionSlice';
import {
  Box,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Paper,
  LinearProgress,
  Alert,
  IconButton,
  CircularProgress
} from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';

interface RecordTranscriptionProps {
  onSuccess?: () => void;
}

const RecordTranscription: React.FC<RecordTranscriptionProps> = ({ onSuccess }) => {
  const [title, setTitle] = useState('');
  const [language, setLanguage] = useState('en-US');
  const [isPublic, setIsPublic] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState('');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  
  const dispatch = useDispatch<AppDispatch>();
  const { isLoading, error: uploadError, uploadProgress } = useSelector((state: RootState) => state.transcription);

  useEffect(() => {
    // Create audio element for playback
    audioRef.current = new Audio();
    
    // Clean up on unmount
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = '';
      }
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
        
        // Generate default title if not set
        if (!title) {
          const now = new Date();
          setTitle(`Recording ${now.toLocaleDateString()} ${now.toLocaleTimeString()}`);
        }
        
        // Stop all tracks in the stream
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
      setError('');
    } catch (err) {
      console.error('Error accessing microphone:', err);
      setError('Could not access microphone. Please check your browser permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Stop timer
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const playRecording = () => {
    if (audioBlob && audioRef.current) {
      const audioUrl = URL.createObjectURL(audioBlob);
      audioRef.current.src = audioUrl;
      audioRef.current.onended = () => setIsPlaying(false);
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const pausePlayback = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const deleteRecording = () => {
    setAudioBlob(null);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = '';
    }
    setIsPlaying(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!audioBlob) {
      setError('Please record audio before submitting.');
      return;
    }
    
    if (!title) {
      return;
    }
    
    // Create a File object from the Blob
    const audioFile = new File([audioBlob], `${title}.wav`, { type: 'audio/wav' });
    
    const result = await dispatch(uploadTranscription({
      file: audioFile,
      title,
      language_code: language,
      is_public: isPublic
    }));
    
    if (!result.hasOwnProperty('error') && onSuccess) {
      onSuccess();
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Record Audio for Transcription
      </Typography>
      
      {(error || uploadError) && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error || uploadError}
        </Alert>
      )}
      
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <TextField
          margin="normal"
          required
          fullWidth
          id="title"
          label="Transcription Title"
          name="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={isLoading || isRecording}
          sx={{ mb: 2 }}
        />
        
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel id="language-select-label">Language</InputLabel>
          <Select
            labelId="language-select-label"
            id="language-select"
            value={language}
            label="Language"
            onChange={(e) => setLanguage(e.target.value)}
            disabled={isLoading || isRecording}
          >
            <MenuItem value="en-US">English (US)</MenuItem>
            <MenuItem value="es-ES">Spanish (Spain)</MenuItem>
            <MenuItem value="fr-FR">French (France)</MenuItem>
            <MenuItem value="de-DE">German (Germany)</MenuItem>
            <MenuItem value="it-IT">Italian (Italy)</MenuItem>
            <MenuItem value="pt-BR">Portuguese (Brazil)</MenuItem>
            <MenuItem value="ja-JP">Japanese (Japan)</MenuItem>
            <MenuItem value="zh-CN">Chinese (Simplified)</MenuItem>
          </Select>
        </FormControl>
        
        <FormControlLabel
          control={
            <Switch
              checked={isPublic}
              onChange={(e) => setIsPublic(e.target.checked)}
              disabled={isLoading || isRecording}
            />
          }
          label="Make transcription public"
          sx={{ mb: 3 }}
        />
        
        <Box sx={{ 
          border: '2px dashed #ccc', 
          borderRadius: 2, 
          p: 3, 
          textAlign: 'center',
          mb: 3
        }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Box sx={{ 
              width: 100, 
              height: 100, 
              borderRadius: '50%', 
              bgcolor: isRecording ? 'error.main' : 'primary.main',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              mb: 2,
              transition: 'background-color 0.3s'
            }}>
              {isRecording ? (
                <StopIcon sx={{ fontSize: 48, color: 'white' }} />
              ) : (
                <MicIcon sx={{ fontSize: 48, color: 'white' }} />
              )}
            </Box>
            
            <Typography variant="h6" gutterBottom>
              {isRecording ? `Recording: ${formatTime(recordingTime)}` : 'Ready to Record'}
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              {!isRecording && !audioBlob && (
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<MicIcon />}
                  onClick={startRecording}
                  disabled={isLoading}
                >
                  Start Recording
                </Button>
              )}
              
              {isRecording && (
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<StopIcon />}
                  onClick={stopRecording}
                >
                  Stop Recording
                </Button>
              )}
              
              {audioBlob && !isRecording && (
                <>
                  <Button
                    variant="outlined"
                    startIcon={isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
                    onClick={isPlaying ? pausePlayback : playRecording}
                    disabled={isLoading}
                  >
                    {isPlaying ? 'Pause' : 'Play'}
                  </Button>
                  
                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={<DeleteIcon />}
                    onClick={deleteRecording}
                    disabled={isLoading}
                  >
                    Delete
                  </Button>
                  
                  <Button
                    variant="outlined"
                    color="primary"
                    startIcon={<MicIcon />}
                    onClick={startRecording}
                    disabled={isLoading}
                  >
                    Record Again
                  </Button>
                </>
              )}
            </Box>
          </Box>
        </Box>
        
        {isLoading && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Uploading: {uploadProgress}%
            </Typography>
            <LinearProgress variant="determinate" value={uploadProgress} />
          </Box>
        )}
        
        <Button
          type="submit"
          fullWidth
          variant="contained"
          disabled={isLoading || isRecording || !audioBlob || !title}
        >
          {isLoading ? 'Uploading...' : 'Upload and Transcribe'}
        </Button>
      </Box>
    </Paper>
  );
};

export default RecordTranscription;
