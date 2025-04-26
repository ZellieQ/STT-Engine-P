#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Speech-to-Text Transcription Service${NC}"
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Function to display help
show_help() {
    echo "Usage: ./run.sh [OPTION]"
    echo "Run the Speech-to-Text Transcription Service"
    echo ""
    echo "Options:"
    echo "  start       Start all services"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  logs        Show logs from all services"
    echo "  init-db     Initialize the database"
    echo "  help        Display this help message"
}

# Function to start services
start_services() {
    echo -e "${YELLOW}Starting services...${NC}"
    docker-compose up -d
    echo -e "${GREEN}Services started!${NC}"
    echo ""
    echo -e "${YELLOW}Frontend:${NC} http://localhost:3000"
    echo -e "${YELLOW}Backend API:${NC} http://localhost:8000"
    echo -e "${YELLOW}API Documentation:${NC} http://localhost:8000/docs"
    echo ""
    echo -e "${YELLOW}Test User:${NC}"
    echo "  Username: testuser"
    echo "  Password: password123"
}

# Function to stop services
stop_services() {
    echo -e "${YELLOW}Stopping services...${NC}"
    docker-compose down
    echo -e "${GREEN}Services stopped!${NC}"
}

# Function to show logs
show_logs() {
    echo -e "${YELLOW}Showing logs (press Ctrl+C to exit)...${NC}"
    docker-compose logs -f
}

# Function to initialize the database
init_db() {
    echo -e "${YELLOW}Initializing database...${NC}"
    docker-compose exec backend python init_db.py
    echo -e "${GREEN}Database initialized!${NC}"
}

# Parse command line arguments
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        start_services
        ;;
    logs)
        show_logs
        ;;
    init-db)
        init_db
        ;;
    help)
        show_help
        ;;
    *)
        show_help
        ;;
esac
