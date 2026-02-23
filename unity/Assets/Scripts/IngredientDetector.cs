using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class IngredientDetector : MonoBehaviour
{
    [Header("AR Overlay Settings")]
    public GameObject boundingBoxPrefab;
    public GameObject labelPrefab;
    public float overlayDistance = 2.0f;
    public float labelOffset = 0.1f;
    
    [Header("Visual Settings")]
    public Material boundingBoxMaterial;
    public Color boundingBoxColor = Color.green;
    public float boundingBoxOpacity = 0.3f;
    
    private Dictionary<string, GameObject> activeOverlays = new Dictionary<string, GameObject>();
    private Camera arCamera;
    
    public static IngredientDetector Instance { get; private set; }
    
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
        arCamera = Camera.main;
        
        // Create prefabs if not assigned
        if (boundingBoxPrefab == null)
        {
            boundingBoxPrefab = CreateBoundingBoxPrefab();
        }
        
        if (labelPrefab == null)
        {
            labelPrefab = CreateLabelPrefab();
        }
        
        Debug.Log("Ingredient Detector initialized");
    }
    
    public void CreateBoundingBoxes(Ingredient[] ingredients)
    {
        // Clear existing overlays
        ClearOverlays();
        
        foreach (Ingredient ingredient in ingredients)
        {
            if (ingredient.box_2d != null && ingredient.box_2d.Length >= 4)
            {
                CreateBoundingBox(ingredient);
            }
        }
    }
    
    private void CreateBoundingBox(Ingredient ingredient)
    {
        // Convert normalized coordinates to world space
        int[] box = ingredient.box_2d;
        float ymin = box[0] / 1000f;
        float xmin = box[1] / 1000f;
        float ymax = box[2] / 1000f;
        float xmax = box[3] / 1000f;
        
        // Convert screen coordinates to world coordinates
        Vector3 bottomLeft = ScreenToWorldPoint(new Vector2(xmin * Screen.width, (1 - ymax) * Screen.height));
        Vector3 topRight = ScreenToWorldPoint(new Vector2(xmax * Screen.width, (1 - ymin) * Screen.height));
        
        // Calculate center and size
        Vector3 center = (bottomLeft + topRight) / 2;
        center.z = overlayDistance; // Place at fixed distance
        
        Vector3 size = new Vector3(
            Mathf.Abs(topRight.x - bottomLeft.x),
            Mathf.Abs(topRight.y - bottomLeft.y),
            0.01f // Small depth
        );
        
        // Create bounding box
        GameObject box = Instantiate(boundingBoxPrefab, center, Quaternion.identity);
        box.transform.localScale = size;
        
        // Set material properties
        Renderer renderer = box.GetComponent<Renderer>();
        if (renderer != null && boundingBoxMaterial != null)
        {
            Material material = new Material(boundingBoxMaterial);
            Color color = boundingBoxColor;
            color.a = boundingBoxOpacity;
            material.color = color;
            renderer.material = material;
        }
        
        // Create label
        Vector3 labelPosition = center + Vector3.up * (size.y / 2 + labelOffset);
        GameObject label = CreateLabel(ingredient.label, labelPosition);
        
        // Parent label to box
        label.transform.SetParent(box.transform);
        
        // Store overlay
        activeOverlays[ingredient.label] = box;
        
        Debug.Log($"Created AR overlay for: {ingredient.label}");
    }
    
    private GameObject CreateLabel(string text, Vector3 position)
    {
        GameObject label = Instantiate(labelPrefab, position, Quaternion.identity);
        
        // Update text mesh
        TextMesh textMesh = label.GetComponent<TextMesh>();
        if (textMesh != null)
        {
            textMesh.text = text.ToUpper();
            textMesh.fontSize = 50;
            textMesh.color = Color.white;
            textMesh.anchor = TextAnchor.MiddleCenter;
        }
        
        // Make label face camera
        label.transform.LookAt(arCamera.transform);
        label.transform.Rotate(0, 180, 0); // Flip to face forward
        
        return label;
    }
    
    private Vector3 ScreenToWorldPoint(Vector2 screenPoint)
    {
        if (arCamera != null)
        {
            return arCamera.ScreenToWorldPoint(new Vector3(screenPoint.x, screenPoint.y, overlayDistance));
        }
        return Vector3.zero;
    }
    
    private GameObject CreateBoundingBoxPrefab()
    {
        GameObject prefab = new GameObject("BoundingBoxPrefab");
        
        // Create cube mesh
        MeshFilter meshFilter = prefab.AddComponent<MeshFilter>();
        MeshRenderer renderer = prefab.AddComponent<MeshRenderer>();
        
        Mesh mesh = new Mesh();
        mesh.vertices = new Vector3[]
        {
            new Vector3(-0.5f, -0.5f, 0),
            new Vector3(0.5f, -0.5f, 0),
            new Vector3(0.5f, 0.5f, 0),
            new Vector3(-0.5f, 0.5f, 0)
        };
        
        mesh.triangles = new int[]
        {
            0, 2, 1, 0, 3, 2
        };
        
        mesh.uv = new Vector2[]
        {
            new Vector2(0, 0),
            new Vector2(1, 0),
            new Vector2(1, 1),
            new Vector2(0, 1)
        };
        
        mesh.RecalculateNormals();
        meshFilter.mesh = mesh;
        
        return prefab;
    }
    
    private GameObject CreateLabelPrefab()
    {
        GameObject prefab = new GameObject("LabelPrefab");
        
        TextMesh textMesh = prefab.AddComponent<TextMesh>();
        MeshRenderer renderer = prefab.AddComponent<MeshRenderer>();
        
        // Set default font
        textMesh.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        textMesh.alignment = TextAlignment.Center;
        
        return prefab;
    }
    
    public void ClearOverlays()
    {
        foreach (var overlay in activeOverlays.Values)
        {
            if (overlay != null)
            {
                Destroy(overlay);
            }
        }
        
        activeOverlays.Clear();
    }
    
    public void UpdateOverlaysVisibility(bool visible)
    {
        foreach (var overlay in activeOverlays.Values)
        {
            if (overlay != null)
            {
                overlay.SetActive(visible);
            }
        }
    }
    
    private void LateUpdate()
    {
        // Make all labels face camera
        foreach (var overlay in activeOverlays.Values)
        {
            if (overlay != null)
            {
                Transform label = overlay.transform.GetChild(0); // First child is label
                if (label != null)
                {
                    label.LookAt(arCamera.transform);
                    label.Rotate(0, 180, 0);
                }
            }
        }
    }
}
