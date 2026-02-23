using UnityEngine;

public class SetupHelper : MonoBehaviour
{
    [ContextMenu("Setup Recipefy AR Scene")]
    public void SetupScene()
    {
        Debug.Log("Setting up Recipefy AR Scene...");
        
        // Find or create required GameObjects
        GameObject cameraManager = GameObject.Find("CameraManager");
        GameObject apiClient = GameObject.Find("APIClient");
        GameObject ingredientDetector = GameObject.Find("IngredientDetector");
        GameObject arUIManager = GameObject.Find("ARUIManager");
        
        if (cameraManager == null)
        {
            cameraManager = new GameObject("CameraManager");
            cameraManager.AddComponent<CameraManager>();
            Debug.Log("Created CameraManager");
        }
        
        if (apiClient == null)
        {
            apiClient = new GameObject("APIClient");
            apiClient.AddComponent<APIClient>();
            Debug.Log("Created APIClient");
        }
        
        if (ingredientDetector == null)
        {
            ingredientDetector = new GameObject("IngredientDetector");
            ingredientDetector.AddComponent<IngredientDetector>();
            Debug.Log("Created IngredientDetector");
        }
        
        if (arUIManager == null)
        {
            arUIManager = new GameObject("ARUIManager");
            arUIManager.AddComponent<ARUIManager>();
            Debug.Log("Created ARUIManager");
        }
        
        // Setup main camera
        Camera mainCamera = Camera.main;
        if (mainCamera != null)
        {
            // Add AR components if missing
            if (mainCamera.GetComponent<UnityEngine.XR.ARFoundation.ARSessionOrigin>() == null)
            {
                mainCamera.gameObject.AddComponent<UnityEngine.XR.ARFoundation.ARSessionOrigin>();
            }
            
            if (mainCamera.GetComponent<UnityEngine.XR.ARFoundation.ARCameraManager>() == null)
            {
                mainCamera.gameObject.AddComponent<UnityEngine.XR.ARFoundation.ARCameraManager>();
            }
            
            // Setup camera properties
            mainCamera.clearFlags = CameraClearFlags.SolidColor;
            mainCamera.backgroundColor = new Color(0, 0, 0, 0);
            
            Debug.Log("Setup Main Camera for AR");
        }
        
        Debug.Log("Recipefy AR Scene setup complete!");
    }
}
