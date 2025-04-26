# Speech-to-Text Simple Demo

This is a simple web-based demo for testing the speech-to-text functionality using OpenAI's Whisper model.

## Features

- Web interface for testing speech-to-text transcription
- Sample audio files included for testing
- Option to simulate transcription (fast) or run the actual Whisper model (more accurate)
- Support for different Whisper model sizes (tiny, base, small, medium)

## Setup and Usage

1. Make sure you have all the required dependencies installed:

```bash
pip install flask whisper torch
```

2. Download sample audio files (if not already done):

```bash
python download_sample.py
```

3. Run the web demo:

```bash
python simple_web_demo.py
```

4. Open your browser and navigate to:

```
http://localhost:8080
```

5. Select a sample audio file from the dropdown menu and click either:
   - "Simulate Transcription" for a quick demo
   - "Run Actual Whisper Model" to process the audio using the Whisper model

## Sample Audio Files

The demo includes several sample audio files:
- `micro-machines.wav`: A short English commercial audio
- `smoke_test.wav`: A short test audio file

## Whisper Model Sizes

You can select different model sizes based on your needs:
- **Tiny**: Fastest, least accurate (~39M parameters)
- **Base**: Good balance of speed and accuracy (~74M parameters)
- **Small**: More accurate, slower (~244M parameters)
- **Medium**: High accuracy, much slower (~769M parameters)

Note that larger models will take longer to load and process audio, but will generally provide more accurate transcriptions.

## Troubleshooting

- If you encounter port conflicts, you can change the port in `simple_web_demo.py`
- If you have SSL certificate issues when downloading models, make sure you have the `certifi` package installed
- For macOS users, you may need to install additional dependencies for audio processing:
  ```bash
  brew install ffmpeg
  ```

## Next Steps

For a more comprehensive speech-to-text solution, check out the full application in this repository, which includes:
- User authentication
- Database storage of transcriptions
- Real-time transcription
- Custom vocabulary support
- Multi-language support
