

import streamlit as st
import tensorflow as tf
import torch
import timm
import os
import json
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model


CONFIG_PATH = os.path.join("config", "model_config.json")
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

@st.cache_resource
def load_model(model_key):

    if model_key not in CONFIG["models"]:
        st.error(f"Model key '{model_key}' not found in config")
        return None, None

    info = CONFIG["models"][model_key]
    model_path = os.path.join("models", info["file"])
    model_type = info["type"]

    # ---------------- TENSORFLOW ----------------
    if model_type == "tensorflow":
     try:
        # Special handling for pumpkin_wheat
        if model_key == "pumpkin_wheat":
            base_model = EfficientNetB0(
                include_top=False,
                weights=None,
                input_shape=(224, 224, 3)
            )

            x = base_model.output
            x = GlobalAveragePooling2D()(x)
            output = Dense(
                CONFIG["models"][model_key]["num_classes"],
                activation="softmax"
            )(x)

            model = Model(inputs=base_model.input, outputs=output)

            # 🔥 LOAD WEIGHTS (not full model)
            model.load_weights(model_path)

            return model, model_type

        # Normal TF models (rice_potato etc.)
        model = tf.keras.models.load_model(model_path)
        return model, model_type

     except Exception as e:
        st.error(f"Error loading TF model: {e}")
        return None, model_type


    # ---------------- PYTORCH (COTTON/TOMATO) ----------------
    if model_type == "torch":
        try:
            model = timm.create_model(
                info["architecture"],
                pretrained=False,
                num_classes=info.get("num_classes",17)
            )

            checkpoint = torch.load(model_path, map_location="cpu")

            if "model_state_dict" in checkpoint:
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

    if model_type == "tensorflow":
        return model.predict(processed_image)

    if model_type == "torch":
        with torch.no_grad():
            outputs = model(processed_image)
            return torch.softmax(outputs, dim=1).cpu().numpy()
