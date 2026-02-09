import numpy as np
from PIL import Image
import tensorflow as tf
import torch
from torchvision import transforms
# --- CRITICAL IMPORT FOR YOUR RESNET MODEL ---
from tensorflow.keras.applications.resnet50 import preprocess_input

def preprocess_image(image, model_type="tensorflow", target_size=(224, 224)):
    """
    Prepares an image for prediction.
    """
    # 1. Ensure RGB (remove Alpha channel if PNG)
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # 2. Resize Image
    image = image.resize(target_size)

    # --- TENSORFLOW PIPELINE (ResNet50 Specific) ---
    if model_type == "tensorflow":
        img_array = np.array(image) # Keeps values 0-255
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        
        # CRITICAL FIX: Use the exact function from your training
        # This handles RGB->BGR conversion and mean subtraction automatically.
        # DO NOT divide by 255 manually here.
        img_array = preprocess_input(img_array) 
        
        return img_array

    # --- PYTORCH PIPELINE ---
    elif model_type == "torch":
        transform = transforms.Compose([
            transforms.Resize(target_size),
            transforms.ToTensor(),
            transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]) # This converts 0-255 to 0-1
             # ImageNet standards
        ])
        img_tensor = transform(image).unsqueeze(0)
        return img_tensor
    