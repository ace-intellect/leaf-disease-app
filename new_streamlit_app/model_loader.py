import streamlit as st
import tensorflow as tf
import torch
from torchvision import models
import os
import json

# Load Configuration
CONFIG_PATH = os.path.join("config", "model_config.json")
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

@st.cache_resource
def load_model(model_key):
    """
    Loads a model (TF or Torch) based on the key from model_config.json.
    Cached to prevent reloading on every interaction.
    """
    if model_key not in CONFIG['models']:
        st.error(f"Model key '{model_key}' not found in config.")
        return None, None

    model_info = CONFIG['models'][model_key]
    model_path = os.path.join("models", model_info['file'])
    model_type = model_info['type']

    # --- TENSORFLOW LOADING ---
    if model_type == "tensorflow":
        try:
            model = tf.keras.models.load_model(model_path)
            return model, model_type
        except Exception as e:
            st.error(f"Error loading TF model: {e}")
            return None, model_type

    # --- PYTORCH LOADING ---
    elif model_type == "torch":
        try:
            # User specified EfficientNetB3 for the .pth model
            model = models.efficientnet_b3(weights=None) 
            
            # Load weights (map_location ensures it works even without a GPU)
            state_dict = torch.load(model_path, map_location=torch.device('cpu'))
            model.load_state_dict(state_dict)
            model.eval() # Set to evaluation mode
            return model, model_type
        except Exception as e:
            st.error(f"Error loading PyTorch model: {e}")
            return None, model_type

def predict_image(model, model_type, processed_image):
    """Runs the prediction and returns the raw probability array."""
    if model_type == "tensorflow":
        return model.predict(processed_image)
    elif model_type == "torch":
        with torch.no_grad():
            output = model(processed_image)
            return torch.nn.functional.softmax(output, dim=1).numpy()