import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { RootState } from '../index';

interface SpeakerSegment {
  speaker_id: string;
  start_time: number;
  end_time: number;
  text: string;
  confidence: number;
}

export interface Transcription {
  id: number;
  user_id: number;
  title: string;
  language_code: string;
  status: string;
  original_filename: string;
  file_size_bytes: number;
  duration_seconds: number;
  file_format: string;
  word_count: number;
  confidence_score: number;
  has_speaker_diarization: boolean;
  speaker_count: number;
  created_at: string;
  processing_started_at?: string;
  processing_completed_at?: string;
  error_message?: string;
  is_public: boolean;
}

export interface TranscriptionResult {
  text: string;
  segments?: SpeakerSegment[];
  language_code: string;
  confidence_score: number;
  word_count: number;
  speaker_count: number;
}

interface TranscriptionState {
  transcriptions: Transcription[];
  currentTranscription: Transcription | null;
  currentResult: TranscriptionResult | null;
  isLoading: boolean;
  error: string | null;
  uploadProgress: number;
}

const initialState: TranscriptionState = {
  transcriptions: [],
  currentTranscription: null,
  currentResult: null,
  isLoading: false,
  error: null,
  uploadProgress: 0,
};

export const fetchTranscriptions = createAsyncThunk(
  'transcription/fetchTranscriptions',
  async (_, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState() as RootState;
      
      if (!auth.token) {
        return rejectWithValue('No authentication token');
      }

      const response = await axios.get('/api/transcriptions', {
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        return rejectWithValue(error.response.data.detail || 'Failed to fetch transcriptions');
      }
      return rejectWithValue('Failed to fetch transcriptions');
    }
  }
);

export const fetchTranscription = createAsyncThunk(
  'transcription/fetchTranscription',
  async (id: number, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState() as RootState;
      
      if (!auth.token) {
        return rejectWithValue('No authentication token');
      }

      const response = await axios.get(`/api/transcriptions/${id}`, {
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        return rejectWithValue(error.response.data.detail || 'Failed to fetch transcription');
      }
      return rejectWithValue('Failed to fetch transcription');
    }
  }
);

export const fetchTranscriptionResult = createAsyncThunk(
  'transcription/fetchTranscriptionResult',
  async (id: number, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState() as RootState;
      
      if (!auth.token) {
        return rejectWithValue('No authentication token');
      }

      const response = await axios.get(`/api/transcriptions/${id}/result`, {
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        return rejectWithValue(error.response.data.detail || 'Failed to fetch transcription result');
      }
      return rejectWithValue('Failed to fetch transcription result');
    }
  }
);

export const uploadTranscription = createAsyncThunk(
  'transcription/uploadTranscription',
  async (
    {
      file,
      title,
      language_code,
      is_public,
      custom_vocabulary_id,
    }: {
      file: File;
      title: string;
      language_code: string;
      is_public: boolean;
      custom_vocabulary_id?: number;
    },
    { getState, rejectWithValue, dispatch }
  ) => {
    try {
      const { auth } = getState() as RootState;
      
      if (!auth.token) {
        return rejectWithValue('No authentication token');
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title);
      formData.append('language_code', language_code);
      formData.append('is_public', is_public.toString());
      if (custom_vocabulary_id) {
        formData.append('custom_vocabulary_id', custom_vocabulary_id.toString());
      }

      const response = await axios.post('/api/transcriptions', formData, {
        headers: {
          Authorization: `Bearer ${auth.token}`,
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            dispatch(setUploadProgress(progress));
          }
        },
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        return rejectWithValue(error.response.data.detail || 'Failed to upload transcription');
      }
      return rejectWithValue('Failed to upload transcription');
    }
  }
);

export const deleteTranscription = createAsyncThunk(
  'transcription/deleteTranscription',
  async (id: number, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState() as RootState;
      
      if (!auth.token) {
        return rejectWithValue('No authentication token');
      }

      await axios.delete(`/api/transcriptions/${id}`, {
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      });

      return id;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        return rejectWithValue(error.response.data.detail || 'Failed to delete transcription');
      }
      return rejectWithValue('Failed to delete transcription');
    }
  }
);

const transcriptionSlice = createSlice({
  name: 'transcription',
  initialState,
  reducers: {
    setUploadProgress: (state, action: PayloadAction<number>) => {
      state.uploadProgress = action.payload;
    },
    clearCurrentTranscription: (state) => {
      state.currentTranscription = null;
      state.currentResult = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Transcriptions
      .addCase(fetchTranscriptions.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchTranscriptions.fulfilled, (state, action: PayloadAction<Transcription[]>) => {
        state.isLoading = false;
        state.transcriptions = action.payload;
      })
      .addCase(fetchTranscriptions.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Transcription
      .addCase(fetchTranscription.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchTranscription.fulfilled, (state, action: PayloadAction<Transcription>) => {
        state.isLoading = false;
        state.currentTranscription = action.payload;
      })
      .addCase(fetchTranscription.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Transcription Result
      .addCase(fetchTranscriptionResult.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchTranscriptionResult.fulfilled, (state, action: PayloadAction<TranscriptionResult>) => {
        state.isLoading = false;
        state.currentResult = action.payload;
      })
      .addCase(fetchTranscriptionResult.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Upload Transcription
      .addCase(uploadTranscription.pending, (state) => {
        state.isLoading = true;
        state.error = null;
        state.uploadProgress = 0;
      })
      .addCase(uploadTranscription.fulfilled, (state, action: PayloadAction<Transcription>) => {
        state.isLoading = false;
        state.uploadProgress = 100;
        state.transcriptions.unshift(action.payload);
        state.currentTranscription = action.payload;
      })
      .addCase(uploadTranscription.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        state.uploadProgress = 0;
      })
      // Delete Transcription
      .addCase(deleteTranscription.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteTranscription.fulfilled, (state, action: PayloadAction<number>) => {
        state.isLoading = false;
        state.transcriptions = state.transcriptions.filter((t) => t.id !== action.payload);
        if (state.currentTranscription && state.currentTranscription.id === action.payload) {
          state.currentTranscription = null;
          state.currentResult = null;
        }
      })
      .addCase(deleteTranscription.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setUploadProgress, clearCurrentTranscription, clearError } = transcriptionSlice.actions;
export default transcriptionSlice.reducer;
