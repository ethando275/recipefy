using System;
using System.Collections;
using UnityEngine;
using UnityEngine.XR;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.Management;

#if UNITY_XR_OCULUS
using UnityEngine.XR.Oculus;
#endif

public class CameraManager : MonoBehaviour
{
    [Header("Camera Settings")]
    public ARCameraManager arCameraManager;
    public Camera mainCamera;
    public Material passthroughMaterial;
    
    [Header("Capture Settings")]
    public int captureWidth = 1920;
    public int captureHeight = 1080;
    public float captureInterval = 3.0f;
    
    private RenderTexture renderTexture;
    private Texture2D captureTexture;
    private bool isCapturing = false;
    private float lastCaptureTime;
    
    public static CameraManager Instance { get; private set; }
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private IEnumerator Start()
    {
        // Initialize XR
        yield return StartCoroutine(InitializeXR());
        
        // Setup camera
        SetupCamera();
        
        // Create render texture
        renderTexture = new RenderTexture(captureWidth, captureHeight, 24, RenderTextureFormat.ARGB32);
        captureTexture = new Texture2D(captureWidth, captureHeight, TextureFormat.RGB24, false);
        
        Debug.Log("Camera Manager initialized");
    }
    
    private IEnumerator InitializeXR()
    {
        // Initialize XR Loader
        var xrLoader = UnityEngine.XR.Management.XRGeneralSettings.Instance.Manager.activeLoader;
        
        if (xrLoader == null)
        {
            Debug.LogError("XR Loader not found");
            yield break;
        }
        
        // Wait for XR to initialize
        while (!XRSettings.isDeviceActive)
        {
            yield return null;
        }
        
        // Enable passthrough on Meta Quest
#if UNITY_XR_OCULUS
        if (OVRPlugin.GetSystemHeadsetType() == OVRPlugin.SystemHeadsetType.Meta_Quest_2 ||
            OVRPlugin.GetSystemHeadsetType() == OVRPlugin.SystemHeadsetType.Meta_Quest_3 ||
            OVRPlugin.GetSystemHeadsetType() == OVRPlugin.SystemHeadsetType.Meta_Quest_Pro)
        {
            // Enable passthrough
            OVRManager.instance.isInsightPassthroughEnabled = true;
            OVRManager.instance.insightPassthroughStyle = OVRManager.InsightPassthroughStyle.Transparent;
            
            Debug.Log("Passthrough enabled for Meta Quest");
        }
#endif
        
        yield return new WaitForSeconds(1.0f);
    }
    
    private void SetupCamera()
    {
        if (arCameraManager != null)
        {
            arCameraManager.frameReceived += OnCameraFrameReceived;
        }
        
        // Setup main camera for AR
        if (mainCamera == null)
        {
            mainCamera = Camera.main;
        }
        
        if (mainCamera != null)
        {
            mainCamera.clearFlags = CameraClearFlags.SolidColor;
            mainCamera.backgroundColor = new Color(0, 0, 0, 0);
        }
    }
    
    private void OnCameraFrameReceived(ARCameraFrameEventArgs eventArgs)
    {
        // Process camera frame if needed
        if (Time.time - lastCaptureTime >= captureInterval && !isCapturing)
        {
            StartCoroutine(CaptureFrame());
        }
    }
    
    private IEnumerator CaptureFrame()
    {
        isCapturing = true;
        lastCaptureTime = Time.time;
        
        // Wait for end of frame
        yield return new WaitForEndOfFrame();
        
        try
        {
            // Capture camera view
            if (mainCamera != null)
            {
                // Render camera to texture
                var tempRT = RenderTexture.GetTemporary(captureWidth, captureHeight, 24);
                mainCamera.targetTexture = tempRT;
                
                yield return new WaitForEndOfFrame();
                
                mainCamera.Render();
                
                // Copy to texture
                RenderTexture.active = tempRT;
                captureTexture.ReadPixels(new Rect(0, 0, captureWidth, captureHeight), 0, 0);
                captureTexture.Apply();
                
                mainCamera.targetTexture = null;
                RenderTexture.active = null;
                RenderTexture.ReleaseTemporary(tempRT);
                
                // Send to API
                byte[] imageData = captureTexture.EncodeToJPG(80);
                StartCoroutine(APIClient.Instance.AnalyzeFrame(imageData));
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Camera capture failed: {e.Message}");
        }
        finally
        {
            isCapturing = false;
        }
    }
    
    public Texture2D GetCameraTexture()
    {
        return captureTexture;
    }
    
    public bool IsPassthroughActive()
    {
#if UNITY_XR_OCULUS
        return OVRManager.instance != null && OVRManager.instance.isInsightPassthroughEnabled;
#else
        return false;
#endif
    }
    
    private void OnDestroy()
    {
        if (arCameraManager != null)
        {
            arCameraManager.frameReceived -= OnCameraFrameReceived;
        }
        
        if (renderTexture != null)
        {
            Destroy(renderTexture);
        }
        
        if (captureTexture != null)
        {
            Destroy(captureTexture);
        }
    }
}
