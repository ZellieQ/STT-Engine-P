#!/bin/bash

# Create a backup directory with timestamp
BACKUP_DIR="/Users/Mblahdiri/STT-Engine-Backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Copy files to backup directory, excluding large files and virtual environments
rsync -av --exclude="venv/" \
         --exclude="__pycache__/" \
         --exclude="*.wav" \
         --exclude="*.mp3" \
         --exclude="*.mp4" \
         --exclude="*.m4a" \
         --exclude="uploads/*" \
         --exclude=".git/" \
         /Users/Mblahdiri/STT-Engine/ "$BACKUP_DIR/"

echo "Backup created at $BACKUP_DIR"

# Optional: Add a comment for this backup
read -p "Enter a comment for this backup (optional): " COMMENT
if [ ! -z "$COMMENT" ]; then
    echo "$COMMENT" > "$BACKUP_DIR/BACKUP_COMMENT.txt"
fi

# List recent backups
echo "Recent backups:"
ls -lt /Users/Mblahdiri/STT-Engine-Backups/ | head -n 5
