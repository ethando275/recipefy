# Recipefy AR - Meta Quest Version

## Overview
This version of Recipefy is optimized for Meta Quest headsets, using WebXR and passthrough camera technology to provide an immersive AR cooking experience.

## Features
- **WebXR Passthrough Camera**: Real-time camera feed with AR overlays
- **Ingredient Detection**: AI-powered food recognition using Gemini 2.0 Flash
- **AR Bounding Boxes**: 3D boxes around detected ingredients
- **Recipe Suggestions**: Contextual recipe recommendations
- **Mixed Reality Interface**: Floating UI panels in AR space

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
Create a `.env` file with:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Start the Backend Server
```bash
python backend.py
```
The server will run on `http://localhost:4444`

### 4. Access on Meta Quest
1. Put on your Meta Quest headset
2. Open the Meta Quest Browser
3. Navigate to your server's IP address (e.g., `http://192.168.1.100:4444`)
4. Click "Start AR Experience"

## How It Works

### WebXR Integration
- Requests immersive-ar session with passthrough
- Falls back to regular camera access if WebXR unavailable
- Renders AR overlays in 3D space

### Camera Processing
- Captures frames from passthrough camera
- Sends frames to backend for AI analysis
- Displays results in real-time AR interface

### AR Overlays
- 3D bounding boxes around detected ingredients
- Floating text labels for food items
- Recipe suggestions in side panel

## Architecture

### Frontend (`web/`)
- `index.html`: Main AR interface
- `quest-ar.js`: WebXR and camera handling
- A-Frame for 3D rendering
- AR.js for WebXR support

### Backend (`backend.py`)
- Flask server with CORS support
- Serves web frontend
- Handles image analysis requests
- Gemini AI integration

## Usage Tips

### On Meta Quest
1. Ensure good lighting for best detection
2. Hold ingredients 1-3 feet from camera
3. Move slowly for stable tracking
4. Allow 3-5 seconds for analysis

### Performance
- Analysis runs every 3 seconds to avoid API limits
- Bounding boxes update automatically
- Recipe suggestions refresh when ingredients change

## Troubleshooting

### WebXR Issues
- Ensure Meta Quest Browser is updated
- Check that WebXR is enabled in browser settings
- Try refreshing the page

### Camera Access
- Grant camera permissions when prompted
- Check that no other app is using the camera
- Restart the browser if needed

### Backend Connection
- Verify server is running on port 4444
- Check network connectivity
- Ensure CORS is properly configured

## Development Notes

### WebXR Limitations
- Passthrough camera quality varies by device
- Some features require Quest 3/3S
- Battery life impacted by continuous AR

### Performance Optimization
- Frame capture limited to 3-second intervals
- Image compression reduces bandwidth
- Efficient 3D rendering with A-Frame

### Future Enhancements
- Hand tracking for interaction
- Voice commands for navigation
- Offline mode with on-device AI
- Multi-language support

## Security Considerations
- All image processing happens on your server
- No images stored permanently
- API keys kept secure in environment variables
- HTTPS recommended for production

## License
This project is for educational and personal use. Please respect the terms of service of the APIs and platforms used.
