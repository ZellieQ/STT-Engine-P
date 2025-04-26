import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  subscription_tier: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

export const login = createAsyncThunk(
  'auth/login',
  async ({ username, password }: { username: string; password: string }, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post('/api/auth/token', formData);
      const { access_token } = response.data;

      // Save token to localStorage
      localStorage.setItem('token', access_token);

      // Get user profile
      const userResponse = await axios.get('/api/users/me', {
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      });

      return {
        token: access_token,
        user: userResponse.data,
      };
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        return rejectWithValue(error.response.data.detail || 'Authentication failed');
      }
      return rejectWithValue('Authentication failed');
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (
    { username, email, password, full_name }: { username: string; email: string; password: string; full_name?: string },
    { rejectWithValue }
  ) => {
    try {
      const response = await axios.post('/api/auth/register', {
        username,
        email,
        password,
        full_name,
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        return rejectWithValue(error.response.data.detail || 'Registration failed');
      }
      return rejectWithValue('Registration failed');
    }
  }
);

export const fetchUserProfile = createAsyncThunk('auth/fetchUserProfile', async (_, { getState, rejectWithValue }) => {
  try {
    const { auth } = getState() as { auth: AuthState };
    
    if (!auth.token) {
      return rejectWithValue('No authentication token');
    }

    const response = await axios.get('/api/users/me', {
      headers: {
        Authorization: `Bearer ${auth.token}`,
      },
    });

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return rejectWithValue(error.response.data.detail || 'Failed to fetch user profile');
    }
    return rejectWithValue('Failed to fetch user profile');
  }
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      localStorage.removeItem('token');
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action: PayloadAction<{ token: string; user: User }>) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.token = action.payload.token;
        state.user = action.payload.user;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Register
      .addCase(register.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.isLoading = false;
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch User Profile
      .addCase(fetchUserProfile.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUserProfile.fulfilled, (state, action: PayloadAction<User>) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload;
      })
      .addCase(fetchUserProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
