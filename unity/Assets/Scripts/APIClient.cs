using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;

[System.Serializable]
public class Ingredient
{
    public string label;
    public int[] box_2d;
}

[System.Serializable]
public class Recipe
{
    public string title;
    public string description;
    public string[] uses;
}

[System.Serializable]
public class AnalysisResponse
{
    public Ingredient[] ingredients;
    public Recipe[] recipes;
}

public class APIClient : MonoBehaviour
{
    [Header("API Settings")]
    public string serverUrl = "http://YOUR_COMPUTER_IP:4444";
    public float timeoutSeconds = 15.0f;
    
    public static APIClient Instance { get; private set; }
    
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
    
    public IEnumerator AnalyzeFrame(byte[] imageData)
    {
        Debug.Log("Sending frame to API for analysis...");
        
        // Create form data
        List<IMultipartFormSection> formData = new List<IMultipartFormSection>();
        formData.Add(new MultipartFormSection(imageData, "frame.jpg", "image/jpeg"));
        
        // Create web request
        using (UnityWebRequest request = UnityWebRequest.Post($"{serverUrl}/analyze_frame", formData))
        {
            request.timeout = (int)(timeoutSeconds * 1000);
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    string jsonResponse = request.downloadHandler.text;
                    AnalysisResponse response = JsonUtility.FromJson<AnalysisResponse>(jsonResponse);
                    
                    // Update UI with results
                    ARUIManager.Instance.UpdateIngredients(response.ingredients);
                    ARUIManager.Instance.UpdateRecipes(response.recipes);
                    
                    // Create AR overlays
                    IngredientDetector.Instance.CreateBoundingBoxes(response.ingredients);
                    
                    Debug.Log($"Analysis complete: {response.ingredients.Length} ingredients, {response.recipes.Length} recipes");
                }
                catch (Exception e)
                {
                    Debug.LogError($"Failed to parse API response: {e.Message}");
                    ARUIManager.Instance.ShowError("Failed to parse analysis results");
                }
            }
            else
            {
                Debug.LogError($"API request failed: {request.error}");
                ARUIManager.Instance.ShowError($"API Error: {request.error}");
            }
        }
    }
    
    public void SetServerURL(string url)
    {
        serverUrl = url;
        PlayerPrefs.SetString("ServerURL", url);
        PlayerPrefs.Save();
        Debug.Log($"Server URL updated to: {url}");
    }
    
    public string GetServerURL()
    {
        if (PlayerPrefs.HasKey("ServerURL"))
        {
            return PlayerPrefs.GetString("ServerURL");
        }
        return serverUrl;
    }
    
    private void Start()
    {
        // Load saved server URL
        serverUrl = GetServerURL();
        
        // Test connection
        StartCoroutine(TestConnection());
    }
    
    private IEnumerator TestConnection()
    {
        using (UnityWebRequest request = UnityWebRequest.Get($"{serverUrl}/"))
        {
            request.timeout = 5000;
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Successfully connected to server");
                ARUIManager.Instance.ShowStatus("Connected to server");
            }
            else
            {
                Debug.LogWarning($"Failed to connect to server: {request.error}");
                ARUIManager.Instance.ShowStatus($"Server connection failed: {request.error}");
            }
        }
    }
    
    public IEnumerator PingServer()
    {
        using (UnityWebRequest request = UnityWebRequest.Get($"{serverUrl}/ping"))
        {
            request.timeout = 3000;
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                ARUIManager.Instance.ShowStatus("Server online");
            }
            else
            {
                ARUIManager.Instance.ShowStatus("Server offline");
            }
        }
    }
}
