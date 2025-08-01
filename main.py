import io
import os
import logging
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from PIL import Image, ImageEnhance
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import time

# --- Configuration and Constants ---
IMG_SIZE = 256 # Using 256 for faster performance on CPU
MODEL_PATH = 'model/stylized_decoder.h5'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_FORMATS = {'image/jpeg', 'image/jpg', 'image/png', 'image/webp'}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Define Custom Layers and Helper Functions ---
class AdaIN(layers.Layer):
    def __init__(self, epsilon=1e-5, **kwargs):
        super().__init__(**kwargs)
        self.epsilon = epsilon

    def call(self, inputs):
        content_features, style_features = inputs
        style_mean, style_variance = tf.nn.moments(style_features, axes=[1, 2], keepdims=True)
        content_mean, content_variance = tf.nn.moments(content_features, axes=[1, 2], keepdims=True)
        normalized_content = tf.nn.batch_normalization(
            content_features, content_mean, content_variance, None, None, self.epsilon
        )
        return (normalized_content * tf.sqrt(style_variance + self.epsilon)) + style_mean

    def get_config(self):
        config = super().get_config()
        config.update({"epsilon": self.epsilon})
        return config

def validate_image(file: UploadFile):
    if file.content_type not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Use: {', '.join(SUPPORTED_FORMATS)}")
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB")

def preprocess_image(image: Image.Image) -> tf.Tensor:
    image = image.convert("RGB")
    image_array = np.array(image, dtype=np.float32)
    img_tensor = tf.image.resize(image_array, [IMG_SIZE, IMG_SIZE], preserve_aspect_ratio=True)
    img_tensor = tf.image.resize_with_pad(img_tensor, IMG_SIZE, IMG_SIZE)
    img_tensor = tf.expand_dims(img_tensor, axis=0)
    return (img_tensor / 127.5) - 1.0

def deprocess_image(tensor: tf.Tensor) -> tf.Tensor:
    tensor = (tensor + 1) * 127.5
    tensor = tf.clip_by_value(tensor, 0, 255)
    return tf.cast(tensor, tf.uint8)

def enhance_result(image: Image.Image, factor: float = 1.1) -> Image.Image:
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(factor)
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)

# --- Global Models ---
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    try:
        logger.info("Loading ML models...")
        models['decoder'] = tf.keras.models.load_model(
            MODEL_PATH, custom_objects={'AdaIN': AdaIN}, compile=False
        )
        vgg19 = tf.keras.applications.VGG19(include_top=False, weights='imagenet')
        vgg19.trainable = False
        models['encoder'] = Model(inputs=vgg19.input, outputs=vgg19.get_layer('block4_conv1').output)
        logger.info("✅ Models loaded successfully!")
    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")
    yield
    logger.info("Application shutdown.")

app = FastAPI(title="Neural Style Transfer API", version="5.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/stylize/")
async def stylize_image(
    content_file: UploadFile = File(...),
    style_file: UploadFile = File(...)
):
    if not all(k in models for k in ['encoder', 'decoder']):
        raise HTTPException(status_code=503, detail="Models are not loaded.")
    
    validate_image(content_file)
    validate_image(style_file)
    
    try:
        content_image = Image.open(io.BytesIO(await content_file.read()))
        style_image = Image.open(io.BytesIO(await style_file.read()))

        content_tensor = preprocess_image(content_image)
        style_tensor = preprocess_image(style_image)

        content_features = models['encoder'](content_tensor, training=False)
        style_features = models['encoder'](style_tensor, training=False)
        
        # Style strength logic removed. Always apply 100% style.
        stylized_features = AdaIN()([content_features, style_features])
        
        final_image_tensor = models['decoder'](stylized_features, training=False)
        final_image_array = deprocess_image(final_image_tensor[0])
        final_image = Image.fromarray(final_image_array.numpy())
        final_image = enhance_result(final_image)
        
        buffer = io.BytesIO()
        final_image.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)
        
        return StreamingResponse(buffer, media_type="image/jpeg")
        
    except Exception as e:
        logger.error(f"Error during stylization: {e}")
        raise HTTPException(status_code=500, detail=str(e))
