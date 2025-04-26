"""
Download a sample audio file for testing the speech-to-text functionality
"""

import os
import requests
import sys

def download_file(url, output_path):
    """
    Download a file from a URL to the specified output path
    """
    print(f"Downloading from {url}...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Get file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download the file
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Print progress
                    if total_size > 0:
                        percent = int(100 * downloaded / total_size)
                        sys.stdout.write(f"\rProgress: {percent}% ({downloaded} / {total_size} bytes)")
                        sys.stdout.flush()
        
        print("\nDownload complete!")
        return True
    
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def main():
    # Sample audio files from Common Voice dataset and other public domain sources
    sample_files = [
        {
            "url": "https://cdn.openai.com/whisper/draft-20220913a/micro-machines.wav",
            "output": "samples/micro-machines.wav",
            "description": "Short English commercial audio (Micro Machines)"
        },
        {
            "url": "https://cdn.openai.com/whisper/draft-20220913a/jfk.wav",
            "output": "samples/jfk.wav",
            "description": "JFK speech excerpt"
        },
        {
            "url": "https://github.com/openai/whisper/raw/main/tests/jfk.flac",
            "output": "samples/jfk.flac",
            "description": "JFK speech excerpt (FLAC format)"
        }
    ]
    
    print("Available sample files:")
    for i, sample in enumerate(sample_files):
        print(f"{i+1}. {sample['description']} - {sample['output']}")
    
    choice = input("\nEnter the number of the file to download (or press Enter for all): ")
    
    if choice.strip() == "":
        # Download all samples
        for sample in sample_files:
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sample["output"])
            download_file(sample["url"], output_path)
    else:
        try:
            index = int(choice) - 1
            if 0 <= index < len(sample_files):
                sample = sample_files[index]
                output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sample["output"])
                download_file(sample["url"], output_path)
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    main()
