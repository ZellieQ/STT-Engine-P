# Speech-to-Text Transcription Service Setup Guide

This guide will help you set up and run the Speech-to-Text Transcription Service on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/downloads)
- [FFmpeg](https://ffmpeg.org/download.html) (required for audio processing)

## Quick Start with Docker

The easiest way to get started is using Docker Compose, which will set up all the required services automatically.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stt-engine.git
   cd stt-engine
   ```

2. Start the services:
   ```bash
   docker-compose up
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Manual Setup

If you prefer to set up the components manually, follow these steps:

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a `.env` file):
   ```
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=stt_service
   MONGODB_URL=mongodb://localhost:27017
   MONGODB_DB=stt_transcriptions
   REDIS_HOST=localhost
   SECRET_KEY=your-secret-key-for-development-only
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Database Setup

#### PostgreSQL

1. Install PostgreSQL or use Docker:
   ```bash
   docker run -d --name postgres -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=stt_service postgres:14
   ```

2. Create the database:
   ```bash
   createdb -U postgres stt_service
   ```

#### MongoDB

1. Install MongoDB or use Docker:
   ```bash
   docker run -d --name mongodb -p 27017:27017 mongo:6
   ```

#### Redis

1. Install Redis or use Docker:
   ```bash
   docker run -d --name redis -p 6379:6379 redis:7
   ```

## Initial Database Setup

When you first run the application, the database tables will be created automatically. However, you'll need to create an initial admin user:

1. Register a new user through the API or frontend
2. Connect to the PostgreSQL database and update the user's role:
   ```sql
   UPDATE users SET is_superuser = TRUE WHERE username = 'your_username';
   ```

## Configuration Options

### Backend Configuration

The backend configuration is located in `backend/api/core/config.py`. You can modify the following settings:

- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time
- `SUPPORTED_LANGUAGES`: List of supported languages
- `UPLOAD_FOLDER`: Directory for uploaded audio files
- `MAX_CONTENT_LENGTH`: Maximum file size for uploads

### Speech Recognition Models

The application uses OpenAI's Whisper model for speech recognition. You can configure the model size in `backend/api/services/transcription_service.py`:

- `tiny`: Fastest, least accurate
- `base`: Good balance of speed and accuracy
- `small`: Better accuracy, slower
- `medium`: High accuracy, much slower
- `large`: Highest accuracy, very slow

## Troubleshooting

### Common Issues

1. **Docker container fails to start**:
   - Check if the required ports are already in use
   - Ensure you have sufficient permissions to run Docker

2. **Speech recognition is slow**:
   - Consider using a smaller Whisper model
   - Check if your machine has GPU support for faster processing

3. **Audio upload fails**:
   - Check the maximum file size configuration
   - Ensure the audio format is supported

### Logs

- Docker container logs: `docker-compose logs -f [service_name]`
- Backend logs: Check the terminal where the backend server is running
- Frontend logs: Check the browser console

## Deployment

For production deployment, consider the following:

1. Use a proper secret key for JWT tokens
2. Set up HTTPS with a valid SSL certificate
3. Configure proper authentication for databases
4. Use a production-ready web server like Nginx
5. Set up proper monitoring and logging

## License

This project is licensed under the MIT License - see the LICENSE file for details.
