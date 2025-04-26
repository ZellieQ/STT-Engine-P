import React from 'react';
import { useRouter } from 'next/router';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../store';
import { deleteTranscription } from '../store/slices/transcriptionSlice';
import { Transcription } from '../store/slices/transcriptionSlice';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  CircularProgress,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';

interface TranscriptionListProps {
  transcriptions: Transcription[];
  isLoading: boolean;
}

const TranscriptionList: React.FC<TranscriptionListProps> = ({ transcriptions, isLoading }) => {
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
  const [transcriptionToDelete, setTranscriptionToDelete] = React.useState<number | null>(null);
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();

  const handleViewTranscription = (id: number) => {
    router.push(`/transcription/${id}`);
  };

  const handleDeleteClick = (id: number) => {
    setTranscriptionToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (transcriptionToDelete !== null) {
      await dispatch(deleteTranscription(transcriptionToDelete));
      setDeleteDialogOpen(false);
      setTranscriptionToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setTranscriptionToDelete(null);
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const getStatusChipColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'pending':
        return 'info';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (transcriptions.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', p: 4 }}>
        <Typography variant="h6" gutterBottom>
          No transcriptions yet
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Upload an audio file or record your voice to create your first transcription.
        </Typography>
        <Button 
          variant="contained" 
          onClick={() => router.push('/dashboard?tab=1')}
          sx={{ mt: 2 }}
        >
          Upload Audio
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="transcriptions table">
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Language</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {transcriptions.map((transcription) => (
              <TableRow
                key={transcription.id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {transcription.title}
                </TableCell>
                <TableCell>
                  <Chip 
                    label={transcription.status} 
                    color={getStatusChipColor(transcription.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{formatDuration(transcription.duration_seconds)}</TableCell>
                <TableCell>{transcription.language_code}</TableCell>
                <TableCell>{formatDate(transcription.created_at)}</TableCell>
                <TableCell align="right">
                  <IconButton 
                    aria-label="view" 
                    onClick={() => handleViewTranscription(transcription.id)}
                    disabled={transcription.status !== 'completed'}
                  >
                    <VisibilityIcon />
                  </IconButton>
                  <IconButton 
                    aria-label="download" 
                    disabled={transcription.status !== 'completed'}
                  >
                    <CloudDownloadIcon />
                  </IconButton>
                  <IconButton 
                    aria-label="delete" 
                    onClick={() => handleDeleteClick(transcription.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {"Delete Transcription?"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Are you sure you want to delete this transcription? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TranscriptionList;
