import streamlit as st
import openai
import requests
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------
# API KEYS (형이 여기 넣으면 됨)
# --------------------------
openai.api_key = "YOUR_API_KEY"
SD_API_KEY = "YOUR_STABLE_DIFFUSION_API_KEY"


# --------------------------
# 페이지 제목
# --------------------------
st.title("AI Ideal Type Generator — Ideal Persona Synthesizer")
st.caption("Create your personalized ideal type using AI ✨")


# --------------------------
# 사용자 입력 섹션
# --------------------------
st.header("1. Describe Your Ideal Type")

col1, col2 = st.columns(2)

with col1:
    extro = st.slider("Extroversion", 0, 10, 5)
    empathy = st.slider("Empathy", 0, 10, 5)
    humor = st.slider("Humor Style", 0, 10, 5)
    stability = st.slider("Stability vs Spontaneity", 0, 10, 5)

with col2:
    vibe = st.selectbox(
        "Overall Vibe",
        ["Warm", "Cool", "Dreamy", "Minimal", "Modern"]
    )
    hair = st.selectbox(
        "Hair Style",
        ["Short", "Medium", "Long", "Wavy", "Straight", "Curly"]
    )
    style = st.selectbox(
        "Character Style",
        ["Realistic", "Anime", "Ghibli", "Illustration"]
    )

keywords = st.text_input("Keywords (comma separated)")
free_text = st.text_area("Short Description")


# --------------------------
# 이상형 프로필 생성 함수
# --------------------------
def generate_profile(extro, empathy, humor, stability, vibe, hair, style, keywords, free_text):
    prompt = f"""
    Create an 'ideal type' character personality profile based on the following traits:

    - Extroversion: {extro}/10
    - Empathy: {empathy}/10
    - Humor: {humor}/10
    - Stability vs Spontaneity: {stability}/10

    Appearance vibe: {vibe}
    Hair style: {hair}
    Art style: {style}
    Keywords: {keywords}
    Description: {free_text}

    Please provide:
    1. Detailed personality profile
    2. Communication style
    3. Estimated MBTI
    4. Lifestyle description
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# --------------------------
# Stable Diffusion 이미지 생성
# --------------------------
def generate_image(prompt):
    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {
        "authorization": f"Bearer {SD_API_KEY}",
        "accept": "image/*"
    }
    payload = {
        "prompt": prompt,
        "output_format": "png"
    }
    response = requests.post(url, headers=headers, files=payload)

    if response.status_code == 200:
        return response.content
    else:
        st.error("Image generation failed.")
        return None


# --------------------------
# 버튼 클릭 → 이상형 생성
# --------------------------
if st.button("Generate Ideal Type"):
    st.subheader("🎭 Ideal Type Profile")
    profile = generate_profile(extro, empathy, humor, stability, vibe, hair, style, keywords, free_text)
    st.write(profile)

    # 이미지 프롬프트 자동 생성
    img_prompt = f"{vibe}, {style} style, {hair} hair, dreamy lighting, gentle expression"
    st.subheader("🖼 Generated Image")
    image_bytes = generate_image(img_prompt)

    if image_bytes:
        st.image(image_bytes)


    # --------------------------
    # 데이터 레이더 차트
    # --------------------------
    st.subheader("📊 Personality Radar Chart")

    data = {
        "Trait": ["Extroversion", "Empathy", "Humor", "Stability"],
        "Score": [extro, empathy, humor, stability]
    }

    df = pd.DataFrame(data)

    plt.figure(figsize=(5,5))
    plt.plot(df["Trait"], df["Score"])
    plt.fill(df["Trait"], df["Score"], alpha=0.2)
    plt.ylim(0,10)
    plt.title("Personality Radar Chart")
    st.pyplot(plt)
