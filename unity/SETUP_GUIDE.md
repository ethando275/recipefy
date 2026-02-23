# Unity Meta Quest Setup Guide

## Step 1: Create Unity Project
1. Open Unity Hub
2. Click "New Project"
3. Select **3D (Core) template**
4. Choose **Unity 2022.3 LTS** or newer
5. Name project: `RecipefyAR`
6. Click "Create Project"

## Step 2: Install Required Packages
1. Go to **Window > Package Manager**
2. Click **"+"** top-left and select:
   - **Add package from git URL**
   - Enter: `com.unity.xr.interaction.toolkit`
   - Click "Add"

3. Install these packages from Package Manager:
   - **AR Foundation** (version 4.2+)
   - **XR Plugin Management**
   - **Meta XR Simulator** (for testing)

## Step 3: Configure XR Settings
1. Go to **Edit > Project Settings**
2. Navigate to **XR Plug-in Management**
3. Under **Plug-in Providers**, enable:
   - **Meta Quest (Oculus)**
   - **OpenXR**
4. Set **Meta Quest** as the standalone plug-in

## Step 4: Configure Android Build Settings
1. Go to **File > Build Settings**
2. Switch platform to **Android**
3. Click **Player Settings**
4. Under **Company**, enter your name
5. Under **Product Name**, enter `RecipefyAR`
6. Set **Minimum API Level** to **32**
7. Set **Target API Level** to **33**
8. Set **Texture Compression** to **ASTC**
9. Enable **Auto Graphics API**

## Step 5: Import Project Files
1. Copy all files from `/unity/Assets/` to your Unity project's `Assets/` folder:
   ```
   Assets/
   ├── Scripts/
   │   ├── CameraManager.cs
   │   ├── APIClient.cs
   │   ├── IngredientDetector.cs
   │   └── ARUIManager.cs
   └── Prefabs/
       └── BoundingBox.prefab
   ```

2. Unity will automatically import the files

## Step 6: Create Scene Setup
1. Create a new scene: **File > New Scene**
2. Save as `RecipefyAR`
3. Create empty GameObjects:
   - **CameraManager** (add CameraManager script)
   - **APIClient** (add APIClient script)
   - **IngredientDetector** (add IngredientDetector script)
   - **ARUIManager** (add ARUIManager script)

## Step 7: Setup Camera
1. Select **Main Camera** in hierarchy
2. Add these components:
   - **AR Camera Manager** (from AR Foundation)
   - **AR Session Origin**
3. Set camera **Clear Flags** to **Solid Color**
4. Set **Background** to **Black (0,0,0,0)**

## Step 8: Create UI Canvas
1. Right-click hierarchy > **UI > Canvas**
2. Set Canvas **Render Mode** to **World Space**
3. Set **Position** to (0, 0, 2)
4. Set **Scale** to (0.01, 0.01, 0.01)
5. Add UI panels:
   - Status Panel
   - Ingredients Panel  
   - Recipes Panel
   - Error Panel

## Step 9: Configure Scripts
1. Select **CameraManager** GameObject
2. In Inspector, assign:
   - Main Camera to `mainCamera` field
   - AR Camera Manager to `arCameraManager` field

3. Select **APIClient** GameObject
4. Set `serverUrl` to your computer's IP:
   ```
   http://YOUR_IP:4444
   ```

## Step 10: Test in Editor
1. Click **Play** button
2. Check Console for any errors
3. Test with Meta XR Simulator if available

## Step 11: Build for Quest
1. Connect Meta Quest via USB or same WiFi
2. Go to **File > Build Settings**
3. Click **Build**
4. Choose location and wait for build
5. Install APK on Quest:
   ```bash
   adb install RecipefyAR.apk
   ```

## Step 12: Enable Developer Mode on Quest
1. Open **Quest Browser**
2. Go to `quest-developer.com`
3. Enable **Developer Mode**
4. Enable **USB Debugging**
5. Allow **Unknown Sources**

## Troubleshooting

### Build Errors
- Make sure Android SDK is installed
- Update Unity to latest LTS version
- Clear Library folder: **Assets > Delete Library**

### Camera Not Working
- Check camera permissions in Quest settings
- Verify AR Foundation is properly configured
- Test with Meta XR Simulator first

### API Connection Issues
- Verify your computer and Quest are on same WiFi
- Check firewall settings
- Test server URL in regular browser first

### Performance Issues
- Lower capture resolution in CameraManager
- Reduce update frequency
- Optimize UI elements

## Quick Start Commands

### Install ADB (if needed)
```bash
# Mac
brew install android-platform-tools

# Windows
# Download from Android Developer website
```

### Build and Deploy
```bash
# Build APK in Unity, then:
adb devices  # Check connected Quest
adb install RecipefyAR.apk
adb logcat  # View logs for debugging
```

### Test Server Connection
```bash
# Start your backend
source venv/bin/activate
python backend.py

# Test from Quest browser
http://YOUR_IP:4444
```
