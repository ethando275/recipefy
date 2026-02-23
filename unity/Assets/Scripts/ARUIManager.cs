using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ARUIManager : MonoBehaviour
{
    [Header("UI Panels")]
    public GameObject statusPanel;
    public GameObject ingredientsPanel;
    public GameObject recipesPanel;
    public GameObject errorPanel;
    
    [Header("UI Elements")]
    public TextMeshProUGUI statusText;
    public TextMeshProUGUI ingredientsText;
    public TextMeshProUGUI recipesText;
    public TextMeshProUGUI errorText;
    public Button retryButton;
    
    [Header("Settings")]
    public TMP_InputField serverURLInput;
    public Button connectButton;
    
    private bool isShowingError = false;
    
    public static ARUIManager Instance { get; private set; }
    
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
    
    private void Start()
    {
        SetupUI();
        ShowStatus("Initializing Recipefy AR...");
        
        // Load saved server URL
        string savedURL = APIClient.Instance.GetServerURL();
        if (serverURLInput != null)
        {
            serverURLInput.text = savedURL;
        }
    }
    
    private void SetupUI()
    {
        // Setup button listeners
        if (retryButton != null)
        {
            retryButton.onClick.AddListener(OnRetryClicked);
        }
        
        if (connectButton != null)
        {
            connectButton.onClick.AddListener(OnConnectClicked);
        }
        
        // Hide panels initially
        HideAllPanels();
        ShowStatus("Ready to start");
    }
    
    public void UpdateIngredients(Ingredient[] ingredients)
    {
        if (ingredientsText == null) return;
        
        if (ingredients.Length > 0)
        {
            string ingredientList = "🥗 Ingredients Detected:\n\n";
            foreach (Ingredient ingredient in ingredients)
            {
                ingredientList += $"• {CapitalizeFirst(ingredient.label)}\n";
            }
            
            ingredientsText.text = ingredientList;
            ShowPanel(ingredientsPanel);
        }
        else
        {
            ingredientsText.text = "🥗 No ingredients detected";
            ShowPanel(ingredientsPanel);
        }
    }
    
    public void UpdateRecipes(Recipe[] recipes)
    {
        if (recipesText == null) return;
        
        if (recipes.Length > 0)
        {
            string recipeList = "🍳 Recipe Suggestions:\n\n";
            foreach (Recipe recipe in recipes)
            {
                recipeList += $"\n<b>{recipe.title}</b>\n";
                recipeList += $"{recipe.description}\n";
                recipeList += $"Uses: {string.Join(", ", recipe.uses)}\n";
                recipeList += "─" + new string('─', 30) + "\n";
            }
            
            recipesText.text = recipeList;
            ShowPanel(recipesPanel);
        }
        else
        {
            recipesText.text = "🍳 No recipes available";
            ShowPanel(recipesPanel);
        }
    }
    
    public void ShowStatus(string message)
    {
        if (statusText == null) return;
        
        statusText.text = $"🔍 {message}";
        ShowPanel(statusPanel);
        HideError();
    }
    
    public void ShowError(string errorMessage)
    {
        if (errorText == null) return;
        
        errorText.text = $"❌ {errorMessage}";
        ShowPanel(errorPanel);
        isShowingError = true;
        
        // Auto-hide after 5 seconds
        StartCoroutine(HideErrorAfterDelay(5.0f));
    }
    
    public void HideError()
    {
        if (errorPanel != null)
        {
            errorPanel.SetActive(false);
        }
        isShowingError = false;
    }
    
    private IEnumerator HideErrorAfterDelay(float delay)
    {
        yield return new WaitForSeconds(delay);
        HideError();
    }
    
    private void ShowPanel(GameObject panel)
    {
        if (panel == null) return;
        
        // Hide all panels first
        HideAllPanels();
        
        // Show requested panel
        panel.SetActive(true);
    }
    
    private void HideAllPanels()
    {
        if (statusPanel != null) statusPanel.SetActive(false);
        if (ingredientsPanel != null) ingredientsPanel.SetActive(false);
        if (recipesPanel != null) recipesPanel.SetActive(false);
        if (errorPanel != null) errorPanel.SetActive(false);
    }
    
    private void OnRetryClicked()
    {
        HideError();
        ShowStatus("Retrying analysis...");
        
        // Trigger new analysis
        StartCoroutine(CameraManager.Instance.StartCoroutine(CameraManager.Instance.CaptureFrame()));
    }
    
    private void OnConnectClicked()
    {
        if (serverURLInput != null)
        {
            string newURL = serverURLInput.text.Trim();
            if (!string.IsNullOrEmpty(newURL))
            {
                APIClient.Instance.SetServerURL(newURL);
                ShowStatus("Testing connection...");
                StartCoroutine(APIClient.Instance.TestConnection());
            }
        }
    }
    
    private string CapitalizeFirst(string input)
    {
        if (string.IsNullOrEmpty(input))
            return input;
            
        return char.ToUpper(input[0]) + input.Substring(1).ToLower();
    }
    
    private void Update()
    {
        // Handle controller input for UI interactions
        HandleControllerInput();
    }
    
    private void HandleControllerInput()
    {
        // Example: Right trigger to force analysis
        if (Input.GetButtonDown("Oculus_CrossPlatform_Button4")) // Right trigger
        {
            ShowStatus("Manual analysis triggered...");
            StartCoroutine(CameraManager.Instance.StartCoroutine(CameraManager.Instance.CaptureFrame()));
        }
        
        // Example: A button to toggle UI visibility
        if (Input.GetButtonDown("Oculus_CrossPlatform_Button1")) // A button
        {
            ToggleUIVisibility();
        }
        
        // Example: B button to show settings
        if (Input.GetButtonDown("Oculus_CrossPlatform_Button2")) // B button
        {
            ToggleSettings();
        }
    }
    
    private void ToggleUIVisibility()
    {
        bool currentState = statusPanel != null && statusPanel.activeSelf;
        HideAllPanels();
        
        if (!currentState)
        {
            ShowPanel(statusPanel);
        }
    }
    
    private void ToggleSettings()
    {
        // Toggle settings panel visibility
        if (serverURLInput != null)
        {
            bool isVisible = serverURLInput.gameObject.activeSelf;
            serverURLInput.gameObject.SetActive(!isVisible);
            if (connectButton != null)
            {
                connectButton.gameObject.SetActive(!isVisible);
            }
        }
    }
    
    // Visual feedback for controller haptics
    public void TriggerHapticFeedback(float intensity = 0.5f, float duration = 0.1f)
    {
#if UNITY_XR_OCULUS
        OVRInput.SetControllerVibration(intensity, duration, OVRInput.Controller.RTouch);
        OVRInput.SetControllerVibration(intensity, duration, OVRInput.Controller.LTouch);
#endif
    }
}
