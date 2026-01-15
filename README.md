# Tesseract OCR - Passport MRZ Scanner

A Python-based real-time passport MRZ (Machine Readable Zone) scanner using FastMRZ and OpenCV. The project includes both a standalone application and a client-server architecture for distributed scanning.

## Features

- **Real-time MRZ Detection**: Live camera feed with instant passport scanning
- **Multiple Implementations**:
  - Standalone scanner with local processing
  - WebSocket-based client-server architecture
- **Visual Feedback**: On-screen status indicators during scanning
- **Automatic Detection**: Stops scanning once MRZ is successfully captured
- **Rate-Limited Processing**: Efficient frame processing to reduce CPU usage

## Architecture

The project consists of three main components:

1. **main.py**: Standalone scanner with threaded processing
2. **server.py**: FastAPI WebSocket server for remote MRZ processing
3. **client.py**: Async WebSocket client with camera interface

## Requirements

- Python 3.8+
- Webcam/Camera access
- Dependencies:
  - `fastmrz` - MRZ extraction library
  - `opencv-python` (cv2) - Camera and image processing
  - `fastapi` - WebSocket server (server mode)
  - `websockets` - WebSocket client (client mode)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd teserract-ocr
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Standalone Scanner

Run the standalone scanner with local processing:

```bash
python main.py
```

### Option 2: Client-Server Mode

1. Start the server:
```bash
uvicorn server:app --host 127.0.0.1 --port 8000
```

2. Run the client (in a separate terminal):
```bash
python client.py
```

### Controls

- **q**: Quit the application
- The scanner automatically stops after successfully detecting MRZ data

## How It Works

### Standalone Mode (main.py)
- Captures frames from the default camera (device 0)
- Processes frames in a background thread at 0.3-second intervals
- Displays real-time feedback on the video feed
- Outputs JSON-formatted MRZ data to console upon success

### Client-Server Mode
**Server (server.py:13-61)**:
- FastAPI WebSocket endpoint at `/ws/mrz-scanner`
- Receives JPEG frames from clients
- Processes images using FastMRZ
- Returns scan results or status updates

**Client (client.py:58-122)**:
- Async camera interface using OpenCV
- Background network task for WebSocket communication
- Sends frames at configurable intervals (default 0.3s)
- Non-blocking UI with real-time connection status

## Project Structure

```
teserract-ocr/
├── main.py          # Standalone scanner
├── server.py        # WebSocket server
├── client.py        # WebSocket client
├── test.py          # Test utilities
├── requirements.txt # Python dependencies
├── passport.jpg     # Sample image
├── out.txt          # Output file
└── .venv/           # Virtual environment
```

## MRZ Data Format

The scanner extracts standard MRZ fields including:
- Document type
- Country code
- Surname and given names
- Passport number
- Nationality
- Date of birth
- Sex
- Expiration date
- Personal number
- Check digits

## Configuration

### Frame Processing Interval
Adjust the `FRAME_INTERVAL` constant to change processing frequency:
```python
FRAME_INTERVAL = 0.3  # seconds between frame processing
```

### Server URL (Client Mode)
Modify the server connection in `client.py`:
```python
SERVER_URL = "ws://127.0.0.1:8000/ws/mrz-scanner"
```

## Troubleshooting

**Camera not opening**:
- Ensure camera permissions are granted
- Check if another application is using the camera
- Try changing camera index in `cv2.VideoCapture(0)` to `1` or `2`

**Connection errors (client-server mode)**:
- Verify server is running on the correct port
- Check firewall settings
- Ensure WebSocket URL is correct

**MRZ not detected**:
- Ensure good lighting conditions
- Hold passport steady with MRZ clearly visible
- Check that MRZ lines are horizontal and in focus



## Credits

Built with:
- [FastMRZ](https://pypi.org/project/fastmrz/) - MRZ extraction
- [OpenCV](https://opencv.org/) - Computer vision
- [FastAPI](https://fastapi.tiangolo.com/) - WebSocket server

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
