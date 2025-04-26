import React, { useState, useRef } from 'react';
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
  IconButton
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CloseIcon from '@mui/icons-material/Close';

interface UploadTranscriptionProps {
  onSuccess?: () => void;
}

const UploadTranscription: React.FC<UploadTranscriptionProps> = ({ onSuccess }) => {
  const [title, setTitle] = useState('');
  const [language, setLanguage] = useState('en-US');
  const [isPublic, setIsPublic] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const dispatch = useDispatch<AppDispatch>();
  const { isLoading, error, uploadProgress } = useSelector((state: RootState) => state.transcription);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      
      // Check file type
      const allowedTypes = ['audio/mp3', 'audio/wav', 'audio/mpeg', 'audio/ogg', 'audio/m4a', 'audio/flac'];
      if (!allowedTypes.includes(file.type)) {
        setFileError('Invalid file type. Please upload an audio file (MP3, WAV, M4A, FLAC, OGG).');
        setSelectedFile(null);
        return;
      }
      
      // Check file size (max 100MB)
      if (file.size > 100 * 1024 * 1024) {
        setFileError('File is too large. Maximum size is 100MB.');
        setSelectedFile(null);
        return;
      }
      
      setSelectedFile(file);
      setFileError('');
      
      // Auto-fill title if not already set
      if (!title) {
        // Remove extension from filename
        const fileName = file.name.replace(/\.[^/.]+$/, '');
        setTitle(fileName);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setFileError('Please select an audio file to upload.');
      return;
    }
    
    if (!title) {
      return;
    }
    
    const result = await dispatch(uploadTranscription({
      file: selectedFile,
      title,
      language_code: language,
      is_public: isPublic
    }));
    
    if (!result.hasOwnProperty('error') && onSuccess) {
      onSuccess();
    }
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setFileError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Upload Audio for Transcription
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
          id="title"
          label="Transcription Title"
          name="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={isLoading}
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
            disabled={isLoading}
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
              disabled={isLoading}
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
          mb: 3,
          position: 'relative'
        }}>
          <input
            type="file"
            accept="audio/*"
            onChange={handleFileChange}
            style={{ display: 'none' }}
            id="audio-file-input"
            ref={fileInputRef}
            disabled={isLoading}
          />
          
          {selectedFile ? (
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CloudUploadIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography>
                  {selectedFile.name} ({(selectedFile.size / (1024 * 1024)).toFixed(2)} MB)
                </Typography>
              </Box>
              <IconButton onClick={handleClearFile} disabled={isLoading}>
                <CloseIcon />
              </IconButton>
            </Box>
          ) : (
            <>
              <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
              <Typography variant="body1" gutterBottom>
                Drag and drop an audio file here, or
              </Typography>
              <label htmlFor="audio-file-input">
                <Button
                  variant="contained"
                  component="span"
                  disabled={isLoading}
                >
                  Select File
                </Button>
              </label>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Supported formats: MP3, WAV, M4A, FLAC, OGG (Max 100MB)
              </Typography>
            </>
          )}
          
          {fileError && (
            <Typography color="error" sx={{ mt: 1 }}>
              {fileError}
            </Typography>
          )}
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
          disabled={isLoading || !selectedFile || !title}
        >
          {isLoading ? 'Uploading...' : 'Upload and Transcribe'}
        </Button>
      </Box>
    </Paper>
  );
};

export default UploadTranscription;
