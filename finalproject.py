import streamlit as st
from openai import OpenAI
import os

# -------------------------
# OpenAI Client
# -------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# Profile Generation Function
# -------------------------
def generate_profile(extro, empathy, humor, stability, vibe, hair, style, keywords, free_text):
    prompt = f"""
    Create a short persona description based on these settings:

    Extroversion: {extro}/10
    Empathy: {empathy}/10
    Humor: {humor}/10
    Emotional Stability: {stability}/10

    Vibe: {vibe}
    Hair Style: {hair}
    Fashion Style: {style}

    Keywords: {keywords}
    Extra Notes: {free_text}

    Produce a friendly, creative profile in 5~7 sentences.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message["content"]


# -------------------------
# Streamlit UI
# -------------------------
st.title("AI Personality Generator ✨")

st.write("Adjust the sliders and options to generate a unique AI character profile!")

st.subheader("Personality Settings")

extro = st.slider("Extroversion", 0, 10, 5)
empathy = st.slider("Empathy", 0, 10, 5)
humor = st.slider("Humor", 0, 10, 5)
stability = st.slider("Emotional Stability", 0, 10, 5)

st.subheader("Appearance & Style")

vibe = st.selectbox("Overall Vibe", ["Cute", "Cool", "Mysterious", "Elegant", "Chaotic"])
hair = st.selectbox("Hair Style", ["Short", "Medium", "Long", "Curly", "Dyed"])
style = st.selectbox("Fashion Style", ["Street", "Modern", "Classic", "Gothic", "Minimal"])

keywords = st.text_input("Keywords (comma-separated)", "")
free_text = st.text_area("Additional Notes")

if st.button("Generate Profile"):
    with st.spinner("Generating..."):
        try:
            profile = generate_profile(extro, empathy, humor, stability, vibe, hair, style, keywords, free_text)
            st.success("Profile Created!")
            st.write(profile)
        except Exception as e:
            st.error("Error occurred. Check your API key or code.")
            st.code(str(e))
