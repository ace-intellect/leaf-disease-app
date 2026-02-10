import numpy as np
from PIL import Image
import tensorflow as tf
import torch
from torchvision import transforms

# TensorFlow preprocessors
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
from tensorflow.keras.applications.efficientnet import preprocess_input as effnet_preprocess


def preprocess_image(image, model_type="tensorflow", target_size=(224, 224), model_key=None):
    """
    Prepares an image for prediction.
    Chooses preprocessing based on model_key.
    """

    # 1. Ensure RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    # 2. Resize
    image = image.resize(target_size)

    # ---------------- TENSORFLOW ----------------
    if model_type == "tensorflow":
        img_array = np.array(image)
        img_array = np.expand_dims(img_array, axis=0)

        # EfficientNet-based models
        if model_key in ["corn_blackgram", "pumpkin_wheat"]:
            img_array = effnet_preprocess(img_array)

        # Default: ResNet-based models
        else:
            img_array = resnet_preprocess(img_array)

        return img_array

    # ---------------- PYTORCH ----------------
    elif model_type == "torch":
        transform = transforms.Compose([
            transforms.Resize(target_size),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        img_tensor = transform(image).unsqueeze(0)
        return img_tensor
