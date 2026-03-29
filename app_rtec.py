"""
Real-Time Emotion Recognition Dashboard
"""

import time
import cv2
import numpy as np
import pandas as pd
import streamlit as st
from fer.fer import FER
from collections import deque

# ---------------------------------------------------------------------------
# Page configuration and custom CSS 
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Emotion Recognition Dashboard",
    layout="wide",          
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Dark, neutral background for a "lab dashboard" feel */
    .stApp { background-color: #0f1117; }

    /* Tighten up metric card spacing */
    [data-testid="metric-container"] {
        background: #1e2130;
        border: 1px solid #2e3250;
        border-radius: 8px;
        padding: 12px 16px;
    }

    /* Subtle section headers */
    h2, h3 { color: #c8d0e0; letter-spacing: 0.04em; }

    /* Make the sidebar a slightly lighter shade */
    [data-testid="stSidebar"] { background-color: #161922; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EMOTION_COLORS = {
    "angry":    "#e05c5c",
    "disgust":  "#8e6bbf",
    "fear":     "#e08c3c",
    "happy":    "#6bc96b",
    "sad":      "#5c8ee0",
    "surprise": "#e0c45c",
    "neutral":  "#9aaabb",
}

HISTORY_LENGTH = 100
EMOTIONS = list(EMOTION_COLORS.keys())

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "emotion_history" not in st.session_state:
    st.session_state.emotion_history = {
        emotion: deque(maxlen=HISTORY_LENGTH) for emotion in EMOTIONS
    }

if "frame_count" not in st.session_state:
    st.session_state.frame_count = 0

if "running" not in st.session_state:
    st.session_state.running = False

if "dominant_emotion" not in st.session_state:
    st.session_state.dominant_emotion = "—"

if "fps_tracker" not in st.session_state:
    st.session_state.fps_tracker = deque(maxlen=30)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("Emotion Dashboard")
    st.caption("Real-time facial expression analysis")
    st.divider()

    camera_index = st.selectbox(
        "Camera Source",
        options=[0, 1, 2],
        index=0,
        help="0 = built-in webcam. Try 1 or 2 for external cameras.",
    )

    detect_every_n = st.slider(
        "Detect every N frames",
        min_value=1,
        max_value=10,
        value=3,
        help="Higher = faster loop, lower accuracy. Lower = slower loop, higher accuracy.",
    )

    confidence_threshold = st.slider(
        "Minimum face confidence",
        min_value=0.5,
        max_value=1.0,
        value=0.85,
        step=0.05,
        help="MTCNN confidence score required to accept a detected face.",
    )

    chart_type = st.radio(
        "Live chart type",
        options=["Bar Chart (current frame)", "Line Chart (history)"],
        index=0,
    )

    st.divider()
    st.markdown("**How it works**")
    st.caption(
        "1. OpenCV captures frames from your webcam.  \n"
        "2. MTCNN detects faces in each frame.  \n"
        "3. A CNN predicts 7 emotion probabilities.  \n"
        "4. Results are plotted live in the dashboard."
    )
    st.divider()

    col_start, col_stop = st.columns(2)
    start_btn = col_start.button("Start", use_container_width=True, type="primary")
    stop_btn  = col_stop.button("Stop",  use_container_width=True)

    if start_btn:
        st.session_state.running = True
        for emotion in EMOTIONS:
            st.session_state.emotion_history[emotion].clear()
        st.session_state.frame_count = 0
        st.session_state.fps_tracker.clear()

    if stop_btn:
        st.session_state.running = False

# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
st.markdown("## Live Feed")

col_video, col_chart = st.columns([3, 2], gap="large")

with col_video:
    video_placeholder = st.empty()

with col_chart:
    st.markdown("### Emotion Probabilities")
    chart_placeholder = st.empty()

st.divider()
st.markdown("### Emotion History")
history_chart_placeholder = st.empty()
st.markdown("### Session Stats")
m1, m2, m3, m4 = st.columns(4)
metric_emotion   = m1.empty()
metric_frames    = m2.empty()
metric_fps       = m3.empty()
metric_face      = m4.empty()

# ---------------------------------------------------------------------------
# FER initialisation
# ---------------------------------------------------------------------------

@st.cache_resource  
def load_fer_model():
    """
    Load the FER detector once and cache it.

    `@st.cache_resource` persists the object across reruns and users.
    This is critical: without it, Streamlit's rerun model would reload
    the ~50MB MTCNN weights on every frame render.
    """
    return FER(mtcnn=True)

detector = load_fer_model()

# ---------------------------------------------------------------------------
# Main capture and inference loop
# ---------------------------------------------------------------------------
if st.session_state.running:
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        st.error(
            f"❌ Could not open camera at index {camera_index}. "
            "Check your camera is connected and not in use by another app."
        )
        st.session_state.running = False
    else:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        last_scores = {emotion: 0.0 for emotion in EMOTIONS}
        face_detected = False

        try:
            while st.session_state.running:
                loop_start = time.time()
                ret, frame = cap.read()
                if not ret:
                    st.warning("Failed to read frame. Retrying...")
                    time.sleep(0.05)
                    continue
                frame = cv2.flip(frame, 1)
                st.session_state.frame_count += 1

                if st.session_state.frame_count % detect_every_n == 0:
                    results = detector.detect_emotions(frame)
                    if results:
                        best = max(results, key=lambda r: r["box"][2] * r["box"][3])

                        face_detected = True
                        last_scores = best["emotions"]  
                        x, y, w, h = best["box"]
                            dominant = max(last_scores, key=last_scores.get)
                            st.session_state.dominant_emotion = dominant
                            cv2.rectangle(frame, (x, y), (x + w, y + h),
                                          (0, 255, 120), 2)

                            label = f"{dominant} ({last_scores[dominant]:.0%})"
                            cv2.putText(
                                frame, label, (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                                (0, 255, 120), 2, cv2.LINE_AA,
                            )
                        else:
                            face_detected = False
                    else:
                        face_detected = False

                for emotion in EMOTIONS:
                    st.session_state.emotion_history[emotion].append(
                        last_scores.get(emotion, 0.0)
                    )

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                video_placeholder.image(
                    frame_rgb,
                    channels="RGB",
                    use_container_width=True,
                )

                chart_df = pd.DataFrame({
                    "Emotion": list(last_scores.keys()),
                    "Probability": list(last_scores.values()),
                })
                chart_df = chart_df.sort_values("Probability", ascending=False)

                if chart_type == "Bar Chart (current frame)":
                    chart_placeholder.bar_chart(
                        chart_df.set_index("Emotion"),
                        color="#ef5ecf",
                        height=300,
                    )
                else:
                    history_df = pd.DataFrame({
                        e: list(st.session_state.emotion_history[e])
                        for e in EMOTIONS
                    })
                    if not history_df.empty:
                        chart_placeholder.line_chart(history_df, height=300)

                history_df = pd.DataFrame({
                    e: list(st.session_state.emotion_history[e])
                    for e in EMOTIONS
                })
                if not history_df.empty:
                    history_chart_placeholder.line_chart(history_df, height=200)

                st.session_state.fps_tracker.append(loop_start)
                if len(st.session_state.fps_tracker) > 1:
                    elapsed = (
                        st.session_state.fps_tracker[-1]
                        - st.session_state.fps_tracker[0]
                    )
                    fps = len(st.session_state.fps_tracker) / max(elapsed, 1e-9)
                else:
                    fps = 0.0

                metric_emotion.metric(
                    "Dominant Emotion",
                    st.session_state.dominant_emotion.capitalize(),
                )
                metric_frames.metric("Frames Processed", st.session_state.frame_count)
                metric_fps.metric("FPS (rolling)", f"{fps:.1f}")
                metric_face.metric(
                    "Face Detected",
                    "Yes" if face_detected else "No",
                )

                elapsed_loop = time.time() - loop_start
                sleep_time = max(0.0, (1 / 15) - elapsed_loop)
                time.sleep(sleep_time)

        finally:
            cap.release()

else:
    video_placeholder.info(
        "Click **Start** in the sidebar to begin the live feed."
    )
    metric_emotion.metric("Dominant Emotion", "—")
    metric_frames.metric("Frames Processed", st.session_state.frame_count)
    metric_fps.metric("FPS (rolling)", "0.0")
    metric_face.metric("Face Detected", "—")
