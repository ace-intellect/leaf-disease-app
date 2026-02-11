import streamlit as st
import tensorflow as tf
import torch
import timm
import os
import json

# Load config
CONFIG_PATH = os.path.join("config", "model_config.json")
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)


@st.cache_resource
def load_model(model_key):
    """Loads TensorFlow or PyTorch model based on config."""

    if model_key not in CONFIG["models"]:
        st.error(f"Model key '{model_key}' not found in config")
        return None, None

    info = CONFIG["models"][model_key]
    model_path = os.path.join("models", info["file"])
    model_type = info["type"]

    # ===================== TENSORFLOW =====================
    if model_type == "tensorflow":
        try:
            # For ALL full .h5 models (rice, corn, pumpkin etc.)
            model = tf.keras.models.load_model(
                model_path,
                compile=False
            )
            return model, model_type

        except Exception as e:
            st.error(f"Error loading TF model: {e}")
            return None, model_type

    # ===================== PYTORCH =====================
    elif model_type == "torch":
        try:
            model = timm.create_model(
                info["architecture"],
                pretrained=False,
                num_classes=info.get("num_classes", 17)
            )

            checkpoint = torch.load(model_path, map_location="cpu")

            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                state_dict = checkpoint["model_state_dict"]
            else:
                state_dict = checkpoint

            model.load_state_dict(state_dict, strict=True)
            model.eval()

            return model, model_type

        except Exception as e:
            st.error(f"Error loading PyTorch model: {e}")
            return None, model_type


def predict_image(model, model_type, processed_image):
    """Runs prediction and returns probability array."""

    if model_type == "tensorflow":
        return model.predict(processed_image)

    elif model_type == "torch":
        with torch.no_grad():
            outputs = model(processed_image)
            return torch.softmax(outputs, dim=1).cpu().numpy()
