import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.title("Real-Time Webcam Filters with OpenCV")

# Filter controls
threshold1 = st.slider("Canny Threshold 1", 50, 300, 100)
threshold2 = st.slider("Canny Threshold 2", 50, 300, 150)
filter_type = st.selectbox("Choose Filter", ["None", "Canny Edge", "Gray", "Blur"])

# Start webcam
cap = cv2.VideoCapture(0)
stframe = st.empty()

# Snapshot button
snapshot = st.button("Take Snapshot")

if cap.isOpened():
    while True:
        ret, frame = cap.read()
        if not ret:
            st.write("Camera not available.")
            break

        # Apply filter
        if filter_type == "Gray":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        elif filter_type == "Canny Edge":
            frame = cv2.Canny(frame, threshold1, threshold2)
        elif filter_type == "Blur":
            frame = cv2.GaussianBlur(frame, (15, 15), 0)

        # Convert for display
        if len(frame.shape) == 2:
            frame_display = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        else:
            frame_display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        stframe.image(frame_display, channels="RGB")

        # Save snapshot
        if snapshot:
            cv2.imwrite("snapshot.png", frame)
            st.success("Snapshot saved as snapshot.png")
            break

    cap.release()
