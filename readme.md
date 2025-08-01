# 🎨 Neural Style Transfer Web Application

This project hosts a deep learning model for arbitrary neural style transfer, allowing you to combine the content of one image with the style of another. The application is built with a high-performance **FastAPI** backend that serves both the model and a clean, modern user interface.

![Demo Screenshot](static/image.png)

## ✨ Features

- **FastAPI Backend**: A single, robust Python server handles everything.
- **Modern UI**: A clean and responsive user interface built with HTML, CSS, and JavaScript.
- **High-Quality Model**: Uses a TensorFlow/Keras model with Adaptive Instance Normalization (AdaIN) to produce high-resolution stylized images.
- **Easy to Use**: Simple drag-and-drop or click-to-upload interface for images.
- **Deployable**: Unified structure makes it easy to deploy on services like Render.

## 🛠️ Technology Stack

- **Backend**: FastAPI, Uvicorn
- **Machine Learning**: TensorFlow / Keras
- **Image Processing**: Pillow, NumPy
- **Frontend**: HTML5, CSS3, JavaScript

## 📂 Project Structure


style-transfer-app/
├── app/
│   ├── static/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   ├── model/
│   │   └── stylized_decoder.h5   # <-- Place your trained model here
│   └── main.py
├── .gitignore
├── requirements.txt
└── README.md


## 🚀 Getting Started

Follow these instructions to get the project running on your local machine.

### Prerequisites

- Python 3.8+
- An IDE or code editor (e.g., VS Code)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
    cd style-transfer-app
    ```

2.  **Create and activate a virtual environment** (recommended):
    ```bash
    # For Windows
    python -m venv myenv
    myenv\Scripts\activate

    # For macOS/Linux
    python3 -m venv myenv
    source myenv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Add the Model File:**
    Make sure you have placed your trained `stylized_decoder.h5` file inside the `app/model/` directory.

### Running the Application

1.  Navigate to the `app` directory:
    ```bash
    cd app
    ```

2.  Start the FastAPI server using Uvicorn:
    ```bash
    uvicorn main:app --reload
    ```

3.  Open your web browser and go to the following address:
    [**http://127.0.0.1:8000**](http://127.0.0.1:8000)

You should now see the web application running and ready to use!
