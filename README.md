# Recipefy 🍳

An AI-powered food recognition and recipe suggestion system that combines computer vision with large language models to identify ingredients from webcam feeds and generate personalized recipe recommendations.

## Features

- **Real-time Food Detection**: Uses YOLO models to identify food items in webcam feeds
- **AI-Powered Recipe Generation**: Leverages Google Gemini 2.0 Flash to generate recipes based on detected ingredients
- **Augmented Reality Interface**: Live webcam overlay with ingredient bounding boxes and recipe suggestions
- **Motion Detection**: Smart scanning that adapts to scene changes and movement
- **Stability Locking**: Prevents unnecessary API calls when ingredients are stable
- **Multi-threaded Processing**: Non-blocking AI analysis for smooth real-time performance

## Architectureq

The system consists of two main components:

### Backend Server (`backend.py`)
- Flask API server running on port 4444
- Handles image analysis requests using Google Gemini 2.0 Flash
- Structured output with Pydantic models for consistent responses
- Returns ingredient detection and recipe suggestions in JSON format

### AR Webcam Viewer (`webcam_viewer.py`)
- Real-time webcam processing with OpenCV
- YOLO-based food detection (food_yolo.pt model)
- Motion detection and stability analysis
- Asynchronous communication with backend API
- Live AR overlay with ingredients and recipes

## Installation

### Prerequisites
- Python 3.8+
- macOS, Windows, or Linux
- Webcam access
- Google Gemini API key

### Setup

1. **Clone and navigate to the project**:
   ```bash
   cd recipefy
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download required models**:
   - `food_yolo.pt` - Food detection YOLO model (22MB)
   - `yolov8n.pt` - General YOLOv8 model (6MB)
   - `pytorch_model.bin` - Additional model weights (347MB)

5. **Set up environment variables**:
   Create a `.env` file with:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

### 1. Start the Backend Server
```bash
python backend.py
```
The server will start on `http://0.0.0.0:4444`

### 2. Launch the AR Webcam Viewer
In a separate terminal:
```bash
python webcam_viewer.py
```

### 3. Using the Application
- Point your webcam at food ingredients
- The system will automatically detect and label food items
- Recipe suggestions will appear in the side panel
- Press 'q' to quit the application

## Configuration

### Key Settings in `webcam_viewer.py`:
- `YOLO_CONF`: Detection confidence threshold (default: 0.35)
- `SCAN_INTERVAL_SECONDS`: Time between AI scans (default: 3.0s)
- `LOCKED_REFRESH_SECONDS`: Refresh interval when locked (default: 10.0s)
- `YOLO_DEVICE`: Processing device ("mps" for Apple Silicon, "cpu" fallback)

### Backend Settings in `backend.py`:
- `MODEL_ID`: Gemini model version ("gemini-2.0-flash")
- Server runs on port 4444 by default

## API Endpoints

### POST `/analyze_frame`
Analyzes an uploaded image frame and returns ingredient detection and recipe suggestions.

**Request**: 
- multipart/form-data with file field named "file"

**Response**:
```json
{
  "ingredients": [
    {
      "label": "tomato",
      "box_2d": [ymin, xmin, ymax, xmax]
    }
  ],
  "recipes": [
    {
      "title": "Fresh Tomato Salad",
      "description": "Simple salad with fresh tomatoes...",
      "uses": ["tomato", "onion", "basil"]
    }
  ]
}
```

## Technical Details

### Performance Optimizations
- **Motion Detection**: Only triggers AI analysis when significant motion is detected
- **Stability Locking**: Reduces API calls when ingredient composition is stable
- **Asynchronous Processing**: Non-blocking HTTP requests to maintain smooth UI
- **GPU Acceleration**: MPS support for Apple Silicon, CPU fallback

### Model Information
- **Food Detection**: Custom YOLO model trained on food datasets
- **Recipe Generation**: Google Gemini 2.0 Flash with structured output
- **Bounding Box Normalization**: Coordinates normalized to 0-1000 range

## Dependencies

Key libraries include:
- `flask` - Web server framework
- `opencv-python` - Computer vision and webcam processing
- `ultralytics` - YOLO model inference
- `google-genai` - Gemini API client
- `pydantic` - Data validation and structured output
- `httpx` - Async HTTP client
- `torch` - PyTorch for model inference

## Troubleshooting

### Common Issues

1. **Webcam not opening**: Check camera permissions and ensure no other app is using the camera
2. **MPS device errors**: The app automatically falls back to CPU if MPS fails
3. **API errors**: Verify your Gemini API key in the `.env` file
4. **Model loading errors**: Ensure all model files are present in the project directory

### Performance Tips
- Use CPU if MPS causes instability on your Mac
- Adjust `SCAN_INTERVAL_SECONDS` for different scanning frequencies
- Lower `YOLO_CONF` if detection is too strict
- Increase `MAX_BOXES` if you need to detect more items

## License

This project is for educational and personal use. Please respect the terms of service of the APIs and models used.

## Contributing

Feel free to submit issues and enhancement requests! Key areas for improvement:
- Additional food categories and models
- Nutritional information integration
- Recipe filtering by dietary restrictions
- Mobile app development