// Recipefy AR - Meta Quest Version
class RecipefyAR {
    constructor() {
        this.isAnalyzing = false;
        this.lastAnalysis = null;
        this.analysisInterval = 3000; // 3 seconds between analyses
        this.backendUrl = 'http://localhost:4444/analyze_frame';
        this.ingredients = [];
        this.recipes = [];
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.checkWebXRSupport();
    }

    setupEventListeners() {
        const startButton = document.getElementById('startButton');
        startButton.addEventListener('click', () => this.startAR());
    }

    checkWebXRSupport() {
        if (!navigator.xr) {
            this.showError('WebXR is not supported on this device');
            return;
        }
        
        this.updateStatus('WebXR supported - ready to start');
    }

    async startAR() {
        const startButton = document.getElementById('startButton');
        const loading = document.getElementById('loading');
        const scene = document.getElementById('ar-scene');
        const overlay = document.getElementById('ui-overlay');
        
        startButton.style.display = 'none';
        loading.style.display = 'block';
        
        try {
            // Request WebXR session with passthrough
            const session = await navigator.xr.requestSession('immersive-ar', {
                requiredFeatures: ['local', 'dom-overlay'],
                domOverlay: { root: document.getElementById('ui-overlay') }
            });
            
            loading.style.display = 'none';
            scene.style.display = 'block';
            overlay.style.display = 'block';
            
            await this.setupXRSession(session);
            this.startAnalysisLoop();
            
        } catch (error) {
            console.error('Failed to start AR session:', error);
            // Fallback to regular camera access
            await this.startCameraFallback();
        }
    }

    async startCameraFallback() {
        const loading = document.getElementById('loading');
        const scene = document.getElementById('ar-scene');
        const overlay = document.getElementById('ui-overlay');
        
        loading.style.display = 'none';
        scene.style.display = 'block';
        overlay.style.display = 'block';
        
        // Use regular camera access as fallback
        await this.setupCameraAccess();
        this.startAnalysisLoop();
    }

    async setupCameraAccess() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' }
            });
            
            // Create video element for camera feed
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();
            
            // Add video to scene
            const scene = document.getElementById('ar-scene');
            scene.appendChild(video);
            
            this.videoStream = stream;
            this.videoElement = video;
            
            this.updateStatus('Camera access granted');
            
        } catch (error) {
            console.error('Camera access failed:', error);
            this.showError('Failed to access camera');
        }
    }

    async setupXRSession(session) {
        this.xrSession = session;
        
        // Setup render loop
        session.requestAnimationFrame(this.onXRFrame.bind(this));
        
        // Handle session end
        session.addEventListener('end', () => {
            this.updateStatus('AR session ended');
        });
        
        this.updateStatus('AR session active');
    }

    onXRFrame(time, frame) {
        if (this.xrSession) {
            this.xrSession.requestAnimationFrame(this.onXRFrame.bind(this));
        }
        
        // Process frame for analysis
        this.processFrame(frame);
    }

    processFrame(frame) {
        // In a real implementation, you would extract camera data from the XR frame
        // For now, we'll use the fallback video element
        if (this.videoElement && !this.isAnalyzing) {
            this.captureAndAnalyze();
        }
    }

    startAnalysisLoop() {
        setInterval(() => {
            if (!this.isAnalyzing && this.videoElement) {
                this.captureAndAnalyze();
            }
        }, this.analysisInterval);
    }

    async captureAndAnalyze() {
        if (this.isAnalyzing) return;
        
        this.isAnalyzing = true;
        this.updateStatus('Analyzing ingredients...');
        
        try {
            // Capture frame from video
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = this.videoElement.videoWidth;
            canvas.height = this.videoElement.videoHeight;
            context.drawImage(this.videoElement, 0, 0);
            
            // Convert to blob
            const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8));
            
            // Send to backend
            const result = await this.sendToBackend(blob);
            this.processAnalysisResult(result);
            
        } catch (error) {
            console.error('Analysis failed:', error);
            this.updateStatus('Analysis failed');
        } finally {
            this.isAnalyzing = false;
        }
    }

    async sendToBackend(imageBlob) {
        const formData = new FormData();
        formData.append('file', imageBlob, 'frame.jpg');
        
        const response = await fetch(this.backendUrl, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    processAnalysisResult(result) {
        this.lastAnalysis = result;
        this.ingredients = result.ingredients || [];
        this.recipes = result.recipes || [];
        
        this.updateUI();
        this.updateStatus('Analysis complete');
        
        // Add AR overlays for detected ingredients
        this.addAROverlays();
    }

    updateUI() {
        // Update ingredients list
        const ingredientsList = document.getElementById('ingredients-list');
        if (this.ingredients.length > 0) {
            ingredientsList.innerHTML = this.ingredients
                .map(ing => `<div>• ${ing.label}</div>`)
                .join('');
        } else {
            ingredientsList.innerHTML = 'No ingredients detected';
        }
        
        // Update recipes list
        const recipesList = document.getElementById('recipes-list');
        if (this.recipes.length > 0) {
            recipesList.innerHTML = this.recipes
                .map(recipe => `
                    <div class="recipe-item">
                        <div class="recipe-title">${recipe.title}</div>
                        <div class="recipe-desc">${recipe.description}</div>
                    </div>
                `).join('');
        } else {
            recipesList.innerHTML = 'No recipes available';
        }
    }

    addAROverlays() {
        // Clear existing overlays
        const arContent = document.getElementById('ar-content');
        arContent.innerHTML = '';
        
        // Add bounding boxes for detected ingredients
        this.ingredients.forEach((ingredient, index) => {
            if (ingredient.box_2d) {
                const box = this.createARBox(ingredient, index);
                arContent.appendChild(box);
            }
        });
    }

    createARBox(ingredient, index) {
        const box = document.createElement('a-box');
        const [ymin, xmin, ymax, xmax] = ingredient.box_2d;
        
        // Convert normalized coordinates to 3D space
        const x = ((xmin + xmax) / 2000) - 0.5; // Convert to -0.5 to 0.5 range
        const y = -((ymin + ymax) / 2000) + 0.5; // Invert Y and convert
        const z = -2; // Place 2 meters in front
        const width = (xmax - xmin) / 1000;
        const height = (ymax - ymin) / 1000;
        
        box.setAttribute('position', `${x} ${y} ${z}`);
        box.setAttribute('width', width);
        box.setAttribute('height', height);
        box.setAttribute('depth', 0.01);
        box.setAttribute('color', '#00ff00');
        box.setAttribute('opacity', '0.3');
        
        // Add label
        const label = document.createElement('a-text');
        label.setAttribute('value', ingredient.label.toUpperCase());
        label.setAttribute('position', `${x} ${y + height/2 + 0.1} ${z}`);
        label.setAttribute('align', 'center');
        label.setAttribute('color', '#ffffff');
        label.setAttribute('scale', '0.5 0.5 0.5');
        
        arContent.appendChild(label);
        
        return box;
    }

    updateStatus(message) {
        const status = document.getElementById('status');
        status.textContent = message;
    }

    showError(message) {
        const status = document.getElementById('status');
        status.textContent = `ERROR: ${message}`;
        status.style.color = '#ff0000';
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new RecipefyAR();
});
