# app.py
import streamlit as st
import os
import random
import textwrap
from datetime import datetime

# Optional: OpenAI 사용 (있으면 더 정교하게 생성)
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

st.set_page_config(page_title="창작 대본 발전기 — Role-based Script Booster", layout="wide")

# ----------------------------
# 역할(롤) 시스템 프롬프트 템플릿
# ----------------------------
ROLE_PROMPTS = {
    "시나리오 작가": (
        "당신은 경험 많은 시나리오 작가입니다. "
        "주어진 장면의 콘셉트, 등장인물 감정선, 비트(장면 전개)를 구조화하여 드라마틱한 장면 대본을 만들어 주세요. "
        "대화(Dialogue), 행동(Blocking), 감정(Emotion) 표기를 명확히 하고, 장면의 의도와 핵심 갈등을 한 문장으로 요약해 주세요."
    ),
    "인물 분석가": (
        "당신은 캐릭터 분석 전문가입니다. "
        "주어진 등장인물들의 동기, 과거사, 심리적 갈등을 분석하고 그들이 장면에서 보일 자연스러운 반응을 문장과 대사 예시로 작성하세요. "
        "캐릭터 간 미묘한 힘의 역학과 숨은 욕구를 지적해 주세요."
    ),
    "서사 구조 전문가": (
        "당신은 서사 구조 전문가입니다. "
        "입력받은 장면을 전체 이야기 구조(3막, 8시퀀스 등)에서 어디에 배치할지, 이 장면이 의미하는 이야기적 기능(촉발, 반전, 결단 등)을 설명하고, 장면을 강화하기 위한 전/후속 아이디어를 제안하세요. "
        "구체적 지시(장면 길이, 템포, 전환 아이디어)를 포함하세요."
    ),
    "극작가": (
        "당신은 극작가입니다. "
        "무대극의 시점으로 장면을 재작성하세요. 대사, 동선, 소품, 음향 큐 등을 포함하고 배우 지시(Acting Notes)를 구체적으로 적어주세요."
    ),
    "카메라 워크 감독": (
        "당신은 촬영감독(카메라 워크 전문가)입니다. "
        "해당 장면을 영화 혹은 드라마 촬영 관점에서 재해석하여 샷리스트(카메라 앵글·렌즈 제안), 무빙, 컷 편집 아이디어, 조명 톤을 제시하세요. "
        "감정 전달을 위한 시각적 포커스와 컷 전환 포인트를 명확히 하세요."
    )
}

# ----------------------------
# 로컬(오프라인) 템플릿 생성 유틸
# ----------------------------
SAMPLE_BEATS = [
    "시작: 불편한 침묵이 흐른다. 한 인물이 과거를 떠올린다.",
    "중반: 갈등이 폭발하고 비밀이 드러난다.",
    "클라이맥스: 선택의 순간, 인물이 결단을 내린다.",
    "엔딩: 여운이 남는 대사 한 줄로 장면을 마무리한다."
]

SAMPLE_LINES = [
    "“그때 네가 없었더라면 난... 아무도 아니었을 거야.”",
    "“그건 네가 알 바 아니야.”",
    "“미안해. 나도 몰랐어.”",
    "“우리가 원하던 결말이 아니어도, 살아남아야 해.”",
    "“조용히 해. 지금은 말하면 안 돼.”"
]

def local_generate(role, prompt, characters, tone, length):
    """간단한 템플릿 기반 로컬 생성기 (OpenAI API 없을 때)"""
    random.seed(hash(prompt) + len(role) + len(tone))
    title = f"[장면] {prompt[:40]}".strip()
    beats = random.sample(SAMPLE_BEATS, k=min(3, len(SAMPLE_BEATS)))
    lines = random.sample(SAMPLE_LINES, k=5)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
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
            txt.append(f"- {c}: 간단 메모 (여기에 성격/목표 입력)")
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
# OpenAI 호출 유틸 (있으면 사용)
# ----------------------------
def openai_generate(role, prompt, characters, tone, length):
    system = ROLE_PROMPTS.get(role, "당신은 전문가입니다.")
    user_msg = (
        f"장면 설명: {prompt}\n"
        f"등장인물(콤마로 구분): {characters}\n"
        f"톤: {tone}\n"
        f"원하는 길이: {length}\n\n"
        "요청: 해당 역할의 관점으로 장면 대본(대사/액션/연출노트)을 작성해 주세요. "
        "한 문장 요약, 핵심 비트, 등장인물 행동, 대사 예시, 연출/촬영/연기 지시를 포함해 주세요."
    )
    # 우선 환경변수 OPENAI_API_KEY 확인 (st.secrets 또는 os.environ)
    api_key = None
    # streamlit secrets 우선
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        api_key = os.getenv("OPENAI_API_KEY", None)

    if not api_key:
        raise RuntimeError("OpenAI API key not found in st.secrets or OPENAI_API_KEY env var.")

    # 설정
    openai.api_key = api_key
    # 모델은 사용환경에 따라 바꿔쓰기 (gpt-4o 계열 사용 권장)
    model = "gpt-4o-mini" if OPENAI_AVAILABLE else "gpt-4o-mini"
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg}
    ]
    # ChatCompletion (chat api)
    try:
        # 최신 openai 라이브러리 호환성 고려
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.8,
            max_tokens=900
        )
        content = completion.choices[0].message["content"]
        return content
    except Exception as e:
        # 실패 시 예외 전파
        raise e

# ----------------------------
# UI
# ----------------------------
st.title("🎬 창작 대본 발전기 — Role-based Script Booster")
st.write("롤을 고르고 장면 아이디어를 써 넣으면, 그 롤 관점으로 장면을 발전시켜줍니다.")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    role = st.selectbox("역할(Role) 선택", list(ROLE_PROMPTS.keys()), index=0)
    prompt = st.text_area("장면(씬) 한 줄 설명 — 상황/감정/목적을 자유롭게 적어라:", height=140,
                          placeholder="예: 폭설 내리는 역에서 두 사람이 우연히 재회한다. 한 명은 과거를 숨기고 있다.")
    chars = st.text_input("등장인물 (콤마로 구분) — 예: 지훈, 수아, 역무원", placeholder="없으면 비워두기")
    tone = st.selectbox("톤(Style)", ["진지", "서정적", "암울한", "희극적", "긴장감", "몽환적"], index=1)
    length = st.selectbox("원하는 길이", ["짧은 샘플(대사 6~10줄)", "중간(대사 10~30줄)", "긴(장면 확장)"], index=1)

    st.write("")
    run_with_ai = st.checkbox("OpenAI API 사용 (키 필요) — 더 정교한 결과", value=False)
    if run_with_ai:
        st.info("OpenAI API 키는 `st.secrets['OPENAI_API_KEY']` 또는 환경변수 OPENAI_API_KEY에 설정하세요.")

    if st.button("장면 생성"):
        if not prompt.strip():
            st.warning("장면 한 줄 설명을 적어줘. 대충 적어도 돼.")
        else:
            with st.spinner("장면 생성 중..."):
                try:
                    if run_with_ai and OPENAI_AVAILABLE:
                        content = openai_generate(role, prompt, chars, tone, length)
                    elif run_with_ai and not OPENAI_AVAILABLE:
                        st.warning("openai 라이브러리를 찾을 수 없습니다. 로컬 템플릿으로 생성합니다.")
                        content = local_generate(role, prompt, chars, tone, length)
                    else:
                        content = local_generate(role, prompt, chars, tone, length)
                except Exception as e:
                    st.error(f"생성 중 오류: {e}")
                    content = local_generate(role, prompt, chars, tone, length)

            st.markdown("### 결과 (미리보기)")
            st.code(content, language="")

            # 다운로드 버튼 (txt)
            file_name = f"scene_{role.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            st.download_button("TXT로 다운로드", data=content, file_name=file_name, mime="text/plain")

with col2:
    st.markdown("## 사용 가이드")
    st.write(
        """
- 간단한 문장(상황/장르/감정)을 입력하면 해당 롤 관점으로 장면을 확장합니다.
- OpenAI API 키가 있으면 더 자연스럽고 깊이 있는 대본을 생성할 수 있습니다.
- 결과를 TXT로 받아 교수님 보고서에 그대로 첨부하면 편함.
"""
    )
    st.markdown("### 역할별 활용 팁")
    st.write("- **시나리오 작가**: 플롯 비트와 갈등을 강화하고 싶을 때.")
    st.write("- **인물 분석가**: 캐릭터 동기와 감정선을 구체화할 때.")
    st.write("- **서사 구조 전문가**: 해당 장면의 이야기적 위치와 기능을 고민할 때.")
    st.write("- **극작가**: 무대 연출 지시와 배우 디렉션이 필요할 때.")
    st.write("- **카메라 워크 감독**: 시각적 연출과 샷리스트가 필요할 때.")

st.markdown("---")
st.caption("Made for: 형 — 창작 과제용 (원하면 README, 깃허브 구조도 만들어줌)")
