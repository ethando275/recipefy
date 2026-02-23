# Recipefy AR - Unity Meta Quest Version

## Overview
Unity-based AR application for Meta Quest headsets with native passthrough camera support and real-time ingredient detection.

## Advantages over Web Version
- **Native Performance**: Better FPS and lower latency
- **Full Camera Access**: Direct passthrough camera control
- **No Browser Limitations**: No HTTPS/cors issues
- **Better AR Integration**: Native Unity AR Foundation
- **Offline Capability**: Can run without internet connection

## Requirements
- Unity 2022.3 LTS or later
- Meta Quest Link or Developer Mode
- Meta Quest 2/3/3S headset

## Setup Instructions

### 1. Install Unity Packages
```
Window > Package Manager
Install:
- XR Interaction Toolkit
- AR Foundation (4.2+)
- Meta XR Simulator (for testing)
```

### 2. Configure XR Settings
```
Edit > Project Settings > XR Plug-in Management
Enable:
- Meta Quest (Oculus)
- OpenXR
```

### 3. Set Build Settings
```
File > Build Settings
- Platform: Android
- Texture Compression: ASTC
- Minimum API Level: 32
- Target API Level: 33
```

### 4. Meta Quest Developer Mode
1. Enable Developer Mode on Quest
2. Connect via USB/WiFi
3. Allow USB debugging

## Project Structure
```
Assets/
├── Scripts/
│   ├── CameraManager.cs
│   ├── APIClient.cs
│   ├── IngredientDetector.cs
│   └── ARUIManager.cs
├── Prefabs/
│   ├── BoundingBox.prefab
│   └── IngredientLabel.prefab
├── Materials/
│   └── AROverlay.mat
└── Scenes/
    └── RecipefyAR.unity
```

## Key Features

### Passthrough Camera
- Native Quest passthrough integration
- Real-time camera texture processing
- Automatic camera permission handling

### AR Overlays
- 3D bounding boxes around ingredients
- Floating labels with ingredient names
- Interactive recipe panels

### API Integration
- HTTP requests to backend server
- Image compression for bandwidth
- Error handling and retry logic

### Performance Optimization
- GPU-accelerated image processing
- Object pooling for AR overlays
- Adaptive quality settings

## Building for Quest

### 1. Build APK
```
File > Build Settings > Build
Select connected Quest device or create APK
```

### 2. Install via ADB
```bash
adb install RecipefyAR.apk
```

### 3. Side-loading
1. Transfer APK to Quest via USB
2. Use Quest Browser to install
3. Enable "Unknown Sources" in settings

## Testing

### In Editor
- Use Meta XR Simulator
- Test camera passthrough simulation
- Validate AR overlay positioning

### On Device
- Test real camera performance
- Validate API connectivity
- Check battery usage

## Troubleshooting

### Camera Issues
- Check camera permissions in Quest settings
- Verify passthrough is enabled
- Restart application

### Build Errors
- Update Unity to latest LTS
- Clear Library folder
- Reinstall XR packages

### Performance
- Lower texture quality
- Reduce update frequency
- Optimize mesh complexity

## Next Steps
- Add hand tracking integration
- Implement voice commands
- Create recipe selection UI
- Add nutritional information
