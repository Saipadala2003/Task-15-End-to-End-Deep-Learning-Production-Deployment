import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("TASK15_API_URL", "http://127.0.0.1:5000").rstrip("/")

st.set_page_config(page_title="Task 15 Production CIFAR-10", page_icon="🧠")
st.title("Task 15 - Production CIFAR-10 Classifier")
st.write("End-to-end deep learning production deployment demo.")

uploaded = st.file_uploader("Upload an RGB image", type=["png","jpg","jpeg"])

if uploaded:
    st.image(uploaded, caption="Uploaded Image", width=320)
    if st.button("Predict", type="primary"):
        try:
            r = requests.post(
                f"{API_URL}/predict",
                files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")},
                timeout=60,
            )
            data = r.json()
            if r.ok and data.get("success"):
                st.success(f"Predicted class: {data['predicted_class']}")
                st.metric("Confidence", f"{data['confidence_percent']:.2f}%")
                st.caption(f"Model version: {data['version']} | Latency: {data['latency_ms']:.2f} ms")
                chart = pd.DataFrame(
                    {"Class": list(data["probabilities"].keys()),
                     "Probability": list(data["probabilities"].values())}
                ).set_index("Class")
                st.bar_chart(chart)
            else:
                st.error(data.get("error", r.text))
        except requests.RequestException as exc:
            st.error(f"API connection failed: {exc}")
else:
    st.info("Upload a CIFAR-10 style image to begin.")
