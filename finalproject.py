# app.py
import streamlit as st
import os
import random
from datetime import datetime

# Optional: OpenAI 사용 (있으면 더 정교하게 생성)
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

st.set_page_config(page_title="Script Booster — Multilingual", layout="wide")

# ----------------------------
# 역할(롤) 시스템 프롬프트 (Korean + English)
# ----------------------------
ROLE_PROMPTS_KO = {
    "시나리오 작가": (
        "당신은 경험 많은 시나리오 작가입니다. "
        "주어진 장면의 콘셉트, 등장인물 감정선, 비트를 구조화하여 드라마틱한 장면 대본을 만들어 주세요. "
        "대화(Dialogue), 행동(Blocking), 감정(Emotion) 표기를 명확히 하고, 장면의 의도와 핵심 갈등을 한 문장으로 요약해 주세요."
    ),
    "인물 분석가": (
        "당신은 캐릭터 분석 전문가입니다. "
        "주어진 등장인물들의 동기, 과거사, 심리적 갈등을 분석하고 자연스러운 반응을 문장과 대사 예시로 작성하세요."
    ),
    "서사 구조 전문가": (
        "당신은 서사 구조 전문가입니다. "
        "입력받은 장면을 이야기 구조에서 어디에 배치할지, 장면의 기능을 설명하고 강화 아이디어를 제안하세요."
    ),
    "극작가": (
        "당신은 극작가입니다. 무대 연출 관점으로 대사, 동선, 소품, 음향 큐, 배우 지시를 쓰세요."
    ),
    "카메라 워크 감독": (
        "당신은 촬영감독입니다. 샷리스트, 무빙, 컷 편집 아이디어, 조명 톤을 제시하고 시각적 포커스를 설명하세요."
    )
}

ROLE_PROMPTS_EN = {
    "Screenwriter": (
        "You are an experienced screenwriter. "
        "Structure the given scene concept into clear beats, character emotional arcs, and a dramatic script. "
        "Include Dialogue, Blocking, and Emotion annotations, and summarize the scene's intention and core conflict in one sentence."
    ),
    "Character Analyst": (
        "You are a character analysis expert. "
        "Analyze characters' motivations, backstories, and psychological conflicts; provide likely reactions and sample lines."
    ),
    "Narrative Structure Expert": (
        "You are an expert in narrative structure. "
        "Place the scene within a larger story (act/sequence), explain its narrative function, and suggest pre/post scene ideas and pacing."
    ),
    "Playwright": (
        "You are a playwright. Rewrite the scene for the stage including dialogue, blocking, props, sound cues, and acting notes."
    ),
    "Cinematographer": (
        "You are a cinematographer. Reinterpret the scene visually: shot list, camera moves, edit ideas, lighting, and visual focus."
    )
}

# ----------------------------
# 로컬(오프라인) 템플릿 영어/한글
# ----------------------------
SAMPLE_BEATS_KO = [
    "시작: 불편한 침묵이 흐른다.",
    "중반: 갈등이 폭발하고 비밀이 드러난다.",
    "클라이맥스: 선택의 순간이 온다.",
    "엔딩: 여운이 남는 한 문장으로 마무리."
]
SAMPLE_LINES_KO = [
    "“그때 네가 없었더라면 난 아무것도 아니었을 거야.”",
    "“그건 네가 알 바 아니야.”",
    "“미안해. 나도 몰랐어.”",
    "“우리가 원한 결말은 아니더라도 살아야 해.”",
    "“조용히 해. 지금 말하면 안 돼.”"
]

SAMPLE_BEATS_EN = [
    "Start: An awkward silence settles in.",
    "Middle: Tension erupts and a secret is revealed.",
    "Climax: A decisive moment forces a choice.",
    "End: The scene closes on a resonant line."
]
SAMPLE_LINES_EN = [
    "\"If you hadn't been there then, I'd be nothing.\"",
    "\"That's none of your business.\"",
    "\"I'm sorry. I didn't know either.\"",
    "\"Even if it's not the ending we wanted, we have to survive.\"",
    "\"Be quiet. This isn't the time to talk.\""
]

def local_generate_en(role, prompt, characters, tone, length):
    random.seed(hash(prompt) + len(role) + len(tone))
    title = f"[Scene] {prompt[:40]}".strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    beats = random.sample(SAMPLE_BEATS_EN, k=min(3, len(SAMPLE_BEATS_EN)))
    lines = random.sample(SAMPLE_LINES_EN, k=5)
    txt = []
    txt.append(f"Title: {title}")
    txt.append(f"Created at: {now}")
    txt.append(f"Role: {role} / Tone: {tone} / Length: {length}")
    txt.append("")
    txt.append("One-sentence summary:")
    txt.append(f"- {prompt}")
    txt.append("")
    txt.append("Key beats:")
    for b in beats:
        txt.append(f"- {b}")
    txt.append("")
    txt.append("Characters & notes:")
    if characters.strip():
        for c in [x.strip() for x in characters.split(",") if x.strip()]:
            txt.append(f"- {c}: brief note (personality/goal)")
    else:
        txt.append("- None provided")
    txt.append("")
    txt.append("Sample script:")
    txt.append("")
    for i, ln in enumerate(lines, 1):
        speaker = random.choice([c for c in (characters.split(",") if characters.strip() else ["A", "B"])])
        txt.append(f"{speaker.strip() if isinstance(speaker, str) else 'A'}: {ln}")
        txt.append(f"    (Action) {random.choice(['turns away.', 'clenches a fist.', 'avoids eye contact.'])}")
        if i % 2 == 0:
            txt.append("")
    txt.append("")
    txt.append("Director notes:")
    if role == "Cinematographer":
        txt.append("- Shot1: Close-up for emotion / slow zoom out")
        txt.append("- Lighting: low-key, cool blue tones")
    elif role == "Playwright":
        txt.append("- Stage: minimal props, single doorway")
        txt.append("- Acting note: speak slowly, use long breaths")
    else:
        txt.append("- (role-based general suggestions) emphasize emotional rhythm and pacing")
    return "\n".join(txt)

def local_generate_ko(role, prompt, characters, tone, length):
    random.seed(hash(prompt) + len(role) + len(tone))
    title = f"[장면] {prompt[:40]}".strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    beats = random.sample(SAMPLE_BEATS_KO, k=min(3, len(SAMPLE_BEATS_KO)))
    lines = random.sample(SAMPLE_LINES_KO, k=5)
    txt = []
    txt.append(f"제목: {title}")
    txt.append(f"생성일시: {now}")
    txt.append(f"선택 롤: {role} / 톤: {tone} / 길이: {length}")
    txt.append("")
    txt.append("요약(한 문장):")
    txt.append(f"- {prompt}")
    txt.append("")
    txt.append("핵심 비트:")
    for b in beats:
        txt.append(f"- {b}")
    txt.append("")
    txt.append("등장인물 및 메모:")
    if characters.strip():
        for c in [x.strip() for x in characters.split(",") if x.strip()]:
            txt.append(f"- {c}: 간단 메모 (성격/목표)")
    else:
        txt.append("- 없음 (입력하지 않음)")
    txt.append("")
    txt.append("장면 대본 (샘플):")
    txt.append("")
    for i, ln in enumerate(lines, 1):
        speaker = random.choice([c for c in (characters.split(",") if characters.strip() else ["A", "B"])])
        txt.append(f"{speaker.strip() if isinstance(speaker, str) else 'A'}: {ln}")
        txt.append(f"    (Action) {random.choice(['몸을 돌린다.', '주먹을 쥔다.', '눈을 피한다.'])}")
        if i % 2 == 0:
            txt.append("")
    txt.append("")
    txt.append("연출 메모:")
    if role == "카메라 워크 감독":
        txt.append("- 샷1: 클로즈업으로 감정 전달 / 느린 줌 아웃")
        txt.append("- 조명: 저채도, 차가운 블루 톤")
    elif role == "극작가":
        txt.append("- 무대: 단출한 소품, 문 하나")
        txt.append("- 배우지시: 천천히 말하되 숨을 길게 사용")
    else:
        txt.append("- (역할 기반 일반 추천) 감정선 강조, 리듬 조절")
    return "\n".join(txt)

# ----------------------------
# OpenAI 호출 유틸 (언어 반영)
# ----------------------------
def openai_generate(role, prompt, characters, tone, length, language):
    if language == "English":
        system = ROLE_PROMPTS_EN.get(role, "You are an expert.")
        user_msg = (
            f"Scene description: {prompt}\n"
            f"Characters (comma separated): {characters}\n"
            f"Tone: {tone}\n"
            f"Desired length: {length}\n\n"
            "Request: From the perspective of the selected role, write a scene script including one-sentence summary, key beats, character actions, sample dialogue, and directing/visual notes."
        )
    else:
        system = ROLE_PROMPTS_KO.get(role, "당신은 전문가입니다.")
        user_msg = (
            f"장면 설명: {prompt}\n"
            f"등장인물(콤마로 구분): {characters}\n"
            f"톤: {tone}\n"
            f"원하는 길이: {length}\n\n"
            "요청: 선택된 롤 관점으로 한 문장 요약, 핵심 비트, 등장인물 행동, 대사 예시, 연출/촬영/연기 지시를 포함한 장면 대본을 작성해 주세요."
        )

    # API 키 확인 (st.secrets 우선)
    api_key = None
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        api_key = os.getenv("OPENAI_API_KEY", None)

    if not api_key:
        raise RuntimeError("OpenAI API key not found in st.secrets or OPENAI_API_KEY env var.")

    openai.api_key = api_key

    # 모델 선택 (환경에 맞게 수정)
    model = "gpt-4o-mini" if OPENAI_AVAILABLE else "gpt-4o-mini"
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg}
    ]
    try:
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.8,
            max_tokens=900
        )
        content = completion.choices[0].message["content"]
        return content
    except Exception as e:
        raise e

# ----------------------------
# UI
# ----------------------------
st.title("🎬 Script Booster — Multilingual (Korean / English)")
st.write("Choose a role and write a short scene idea. Select language -> results will be generated in that language.")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    language = st.selectbox("Language / 언어 선택", ["English", "한국어"], index=0)
    if language == "English":
        role_options = list(ROLE_PROMPTS_EN.keys())
    else:
        role_options = list(ROLE_PROMPTS_KO.keys())

    role = st.selectbox("Role / 롤 선택", role_options, index=0)
    if language == "English":
        prompt = st.text_area("Scene one-line description (situation/emotion/purpose):", height=140,
                              placeholder="e.g. On a snowy dawn, two former lovers meet outside an apartment. One hides a secret.")
        chars = st.text_input("Characters (comma separated) — e.g. Iru, Solbit", placeholder="leave blank if none")
        tone = st.selectbox("Tone", ["Poetic", "Serious", "Bleak", "Comedic", "Tense", "Dreamy"], index=0)
        length = st.selectbox("Desired length", ["Short sample (6-10 lines)", "Medium (10-30 lines)", "Long (expanded scene)"], index=1)
    else:
        prompt = st.text_area("장면 한 줄 설명 (상황/감정/목적):", height=140,
                              placeholder="예: 폭설 내리는 새벽, 전 연인이 자취방 앞 골목에서 마주친다.")
        chars = st.text_input("등장인물 (콤마로 구분) — 예: 이루, 솔빛", placeholder="없으면 비워두기")
        tone = st.selectbox("톤", ["서정적", "진지", "암울한", "희극적", "긴장감", "몽환적"], index=0)
        length = st.selectbox("원하는 길이", ["짧음(대사 6~10줄)", "중간(10~30줄)", "긴(장면 확장)"], index=1)

    run_with_ai = st.checkbox("Use OpenAI API (requires key) / OpenAI API 사용", value=False)
    if run_with_ai:
        st.info("Set your API key in Streamlit secrets as OPENAI_API_KEY or export OPENAI_API_KEY as env var.")

    if st.button("Generate Scene / 장면 생성"):
        if not prompt.strip():
            st.warning("Please enter a scene description / 장면 설명을 입력하세요.")
        else:
            with st.spinner("Generating..."):
                try:
                    if run_with_ai and OPENAI_AVAILABLE:
                        content = openai_generate(role, prompt, chars, tone, length, language)
                    elif run_with_ai and not OPENAI_AVAILABLE:
                        st.warning("openai library not available — falling back to local template.")
                        content = local_generate_en(role, prompt, chars, tone, length) if language == "English" else local_generate_ko(role, prompt, chars, tone, length)
                    else:
                        content = local_generate_en(role, prompt, chars, tone, length) if language == "English" else local_generate_ko(role, prompt, chars, tone, length)
                except Exception as e:
                    st.error(f"Generation error: {e}")
                    content = local_generate_en(role, prompt, chars, tone, length) if language == "English" else local_generate_ko(role, prompt, chars, tone, length)

            st.markdown("### Result / 결과")
            st.code(content, language="")

            # Download button
            safe_role = role.replace(" ", "_")
            file_name = f"scene_{safe_role}_{language}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            st.download_button("Download TXT / TXT로 다운로드", data=content, file_name=file_name, mime="text/plain")

with col2:
    st.markdown("## Quick guide / 사용 가이드")
    if language == "English":
        st.write("- Enter a short scene prompt. Select Role and Tone. Optionally enable OpenAI for richer output.")
        st.write("- The output will be in English when 'English' is selected.")
    else:
        st.write("- 간단한 장면 설명을 입력하고 롤과 톤을 선택하세요. OpenAI 사용 시 더 풍부한 출력이 생성됩니다.")
        st.write("- '한국어' 선택 시 출력은 한국어로 생성됩니다.")
    st.markdown("### Roles / 롤 활용 팁")
    if language == "English":
        st.write("- Screenwriter: strengthen beats and conflict.")
        st.write("- Character Analyst: deepen motivations and reactions.")
        st.write("- Narrative Structure Expert: place scene in story.")
        st.write("- Playwright: stage directions and acting notes.")
        st.write("- Cinematographer: shot list and visual ideas.")
    else:
        st.write("- 시나리오 작가: 플롯 비트와 갈등 강화.")
        st.write("- 인물 분석가: 동기와 반응 구체화.")
        st.write("- 서사 구조 전문가: 이야기 내 위치 설명.")
        st.write("- 극작가: 무대 지시와 배우 노트.")
        st.write("- 카메라 워크 감독: 시각적 연출 제안.")

st.markdown("---")
st.caption("Made for: 형 — English class friendly. Want sample outputs for the snowy-dawn scene in English? Say the word.")
