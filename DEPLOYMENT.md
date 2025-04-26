# Deployment Guide for Speech-to-Text Web App

This guide provides instructions for deploying your speech-to-text transcription app to various platforms to get a permanent, accessible URL.

## Option 1: Deploy to Render.com (Recommended for Simplicity)

Render is a cloud platform that makes it easy to deploy web applications with minimal configuration.

### Steps:

1. **Create a GitHub repository**
   - Push your code to GitHub (create a new repository and follow GitHub's instructions)

2. **Sign up for Render**
   - Go to [render.com](https://render.com) and create an account

3. **Create a new Web Service**
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Select the repository with your speech-to-text app

4. **Configure your service**
   - Name: `speech-to-text-app` (or your preferred name)
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn web_app:app`
   - Select an appropriate plan (Free tier works for testing)

5. **Add environment variables**
   - Add `PYTHON_VERSION: 3.10.0` to ensure compatibility

6. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your application
   - You'll get a URL like `https://speech-to-text-app.onrender.com`

## Option 2: Deploy to Heroku

Heroku is another popular platform for deploying web applications.

### Steps:

1. **Install the Heroku CLI**
   ```bash
   brew install heroku/brew/heroku
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create a new Heroku app**
   ```bash
   cd /Users/Mblahdiri/STT-Engine
   heroku create your-stt-app-name
   ```

4. **Add a Procfile**
   ```bash
   echo "web: gunicorn web_app:app" > Procfile
   ```

5. **Initialize Git repository (if not already done)**
   ```bash
   git init
   git add .
   git commit -m "Initial commit for deployment"
   ```

6. **Deploy to Heroku**
   ```bash
   git push heroku main
   ```

7. **Scale the app**
   ```bash
   heroku ps:scale web=1
   ```

8. **Open the app**
   ```bash
   heroku open
   ```

## Option 3: Self-Hosting with Docker

For more control, you can deploy the app on your own server using Docker.

### Prerequisites:
- A server with Docker and Docker Compose installed
- A domain name pointing to your server
- Basic knowledge of server administration

### Steps:

1. **Transfer files to your server**
   - Copy your project files to your server
   - Make sure to include:
     - `Dockerfile`
     - `docker-compose.deploy.yml`
     - `nginx/conf.d/app.conf`
     - All application files

2. **Configure your domain**
   - Edit `nginx/conf.d/app.conf` and replace `your-domain.com` with your actual domain

3. **Set up SSL certificates**
   ```bash
   mkdir -p nginx/ssl
   ```
   
   - Option A: Use Let's Encrypt for free SSL certificates
   - Option B: Use self-signed certificates for testing:
     ```bash
     openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem
     ```

4. **Start the services**
   ```bash
   docker-compose -f docker-compose.deploy.yml up -d
   ```

5. **Access your application**
   - Your app will be available at `https://your-domain.com`

## Important Considerations for Production

1. **Data Persistence**
   - Set up volume mounts for `uploads` and `transcriptions` directories
   - Consider using a database for storing transcription metadata

2. **Security**
   - Implement proper authentication for your app
   - Set up HTTPS with valid SSL certificates
   - Restrict file upload sizes and types

3. **Performance**
   - Consider using a CDN for static assets
   - Implement caching for frequently accessed transcriptions
   - Use a more robust database like PostgreSQL for production

4. **Scaling**
   - For high traffic, consider using a load balancer
   - Implement a queue system for processing large files (like Celery with Redis)

## Monitoring and Maintenance

1. **Set up monitoring**
   - Use services like New Relic, Datadog, or Prometheus for monitoring
   - Set up alerts for errors and performance issues

2. **Regular backups**
   - Back up your transcriptions and database regularly
   - Test your backup restoration process

3. **Updates**
   - Keep your dependencies updated
   - Regularly update your Whisper model to the latest version

## Troubleshooting

- **Memory issues**: If you're processing very large files, you might need to increase the memory allocation for your containers
- **Timeout errors**: Adjust the timeout settings in Nginx and your web server
- **SSL certificate issues**: Make sure your certificates are valid and properly configured
