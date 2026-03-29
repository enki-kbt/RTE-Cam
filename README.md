# RTE-Cam
A computer vision dashboard that uses Python, OpenCV, and Streamlit. It captures live webcam feeds, processes facial features using a pre-trained deep learning model, and visualizes the user's emotional state (happy, sad, angry, etc.) through a live updating chart. 

## What it does

This app opens your webcam, detects faces in real-time, and predicts the probability of 7 basic emotions for each detected face.

| Emotion | Theoretical Basis |
|---|---|
| Angry | Ekman's Basic Emotions (1992) |
| Disgust | Ekman's Basic Emotions (1992) |
| Fear | Ekman's Basic Emotions (1992) |
| Happy | Ekman's Basic Emotions (1992) |
| Sad | Ekman's Basic Emotions (1992) |
| Surprise | Ekman's Basic Emotions (1992) |
| Neutral | Added to cover non-expressive states |

Results are displayed through a live annotated video feed with a bounding box and dominant emotion labels, and a real-time bar chart of current frame emotion probabilities, an other chart composed as a rolling line showing emotion trends over the last ~10 seconds.

## Architecture

```
┌─────────────┐     BGR frames      ┌──────────────────┐     scores dict     ┌──────────────────┐
│   OpenCV    │ ──────────────────► │   FER Detector   │ ──────────────────► │    Streamlit     │
│  (Capture)  │                     │  MTCNN + CNN     │                     │  (Visualisation) │
└─────────────┘                     └──────────────────┘                     └──────────────────┘
      ▲                                      │
      │                               Bounding box
      └──────────── Annotated frame ◄────────┘
```
---

## Setup and installation

### Prerequisites
- Python 3.9 or higher
- A working webcam
- ~2 GB free disk space (TensorFlow dependency)

### Step 1: Clone repository
```bash
git clone https://github.com/enki-kbt/RTE-Cam.git
cd emotion-dashboard
```

### Step 2 (strongly recommended): Create a virtual environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **TensorFlow note:** The first install downloads ~500 MB. On Apple Silicon (M1/M2/M3), you may need `tensorflow-macos` instead — see [Apple's guide](https://developer.apple.com/metal/tensorflow-plugin/).

### Step 4: Run the app
```bash
streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`.

---

## Usage

1. Open the app in your browser
2. In the sidebar, choose your camera source (usually `0` for built-in webcam)
3. Adjust the **"Detect every N frames"** slider (higher values are faster; lower values are more accurate)
4. Click **Start** to begin the live feed.
5. Position your face in view of the camera.
6. Click **Stop** when finished.

---

## Design rationale and system limitations

This project was designed to prioritize conceptual clarity and practical execution over complex software engineering. I selected Streamlit rather than a traditional full-stack architecture, like FastAPI paired with React, to keep the focus strictly on machine learning mechanics using pure Python, though a production environment would naturally decouple the model server from the frontend. For the core recognition task, I opted for the lightweight FER library rather than DeepFace; because while DeepFace offers higher accuracy, FER’s sub-10 MB model footprint makes it vastly more practical for a CPU-bound laptop webcam demonstration, while leveraging Python's collections.deque to efficiently manage the sliding window of emotion history with O(1) operations instead of computationally expensive list slicing.

But despite these optimizations, the system operates within several practical and theoretical constraints that I find important to acknowledge in an academic context. The application currently processes only the highest-confidence face in the frame and is highly sensitive to environmental factors, with performance degrading significantly in low-light conditions. Furthemore, the underlying model is bound by the inherent demographic biases of the FER2013 training dataset and relies on the simplified seven-category Ekman model of emotion. Because real human emotional expression is culturally influenced ad highly context-dependent, this categorical approach represents a structural simplification rather than an absolute measure of human sentiment.

---

## References

- Ekman, P. (1992). *An argument for basic emotions.* Cognition & Emotion, 6(3–4), 169–200.
- Goodfellow, I., et al. (2013). *Challenges in representation learning: A report on three machine learning contests.* ICML.
- Zhang, K., et al. (2016). *Joint face detection and alignment using multitask cascaded convolutional networks.* IEEE Signal Processing Letters.
- [FER Library](https://github.com/justinshenk/fer) — Justin Shenk
- [FER2013 Dataset](https://www.kaggle.com/datasets/msambare/fer2013) — Kaggle

---


