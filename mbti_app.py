import streamlit as st
import json
from datetime import datetime
from ai_helper import ask_ai
import pandas as pd

st.set_page_config(page_title="우리 반 MBTI 수집소", layout="wide")

st.title("🎯 우리 반 MBTI 수집소")

def load_records():
    try:
        with open("mbti.json", encoding="utf-8") as f:
            return json.load(f)["records"]
    except FileNotFoundError:
        return []

def save_records(records):
    data = {"title": "우리 반 MBTI 수집소", "records": records}
    with open("mbti.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_mbti(answers):
    """AI를 사용하여 MBTI 결과 생성"""
    prompt = f"""
    다음 4개의 질문에 대한 답변을 바탕으로 MBTI 유형을 결정하고, 별명과 설명, 해설을 만들어 주세요.

    답변:
    1번 문항: {answers[0]}
    2번 문항: {answers[1]}
    3번 문항: {answers[2]}
    4번 문항: {answers[3]}

    응답 형식 (JSON):
    {{
        "mbti": "ENFP",
        "nickname": "별명",
        "description": "한 줄 설명",
        "explanation": "상세 해설"
    }}

    JSON만 응답해주세요.
    """

    response = ask_ai(prompt)
    try:
        result = json.loads(response)
        return result
    except:
        return None

def analyze_class_vibe(records):
    """반 전체의 분위기 분석"""
    if not records:
        return None

    mbti_types = [r["mbti"] for r in records]
    mbti_counts = {}
    for mbti in mbti_types:
        mbti_counts[mbti] = mbti_counts.get(mbti, 0) + 1

    prompt = f"""
    우리 반의 MBTI 분포가 다음과 같습니다:
    {json.dumps(mbti_counts, ensure_ascii=False, indent=2)}

    이 분포를 바탕으로 우리 반의 전체적인 분위기와 특징을 분석해주세요.
    (2-3문단, 친근한 톤으로)
    """

    analysis = ask_ai(prompt)
    return analysis

# 탭 분리: 참여하기 / 결과 보기
tab1, tab2 = st.tabs(["📝 참여하기", "📊 결과 보기"])

with tab1:
    st.header("나의 MBTI 찾기")

    with st.form("mbti_form"):
        name = st.text_input("이름을 입력하세요")

        st.subheader("다음 4개의 질문에 답해주세요")

        questions = [
            "1. 주말을 어떻게 보내는 것을 선호하나요?",
            "2. 어려운 상황이 생기면 어떻게 하나요?",
            "3. 새로운 일을 시작할 때 당신의 스타일은?",
            "4. 친구들과의 관계에서 당신은?"
        ]

        options = [
            ["집에서 휴식하기", "새로운 곳 탐험하기"],
            ["먼저 생각한 후 행동하기", "직감에 따라 행동하기"],
            ["계획을 세워서 시작하기", "상황에 따라 유연하게 하기"],
            ["주도적으로 리드하기", "함께 조화 맞추기"]
        ]

        answers = []
        for i, (question, opts) in enumerate(zip(questions, options)):
            st.write(f"**{question}**")
            answer = st.radio(
                "선택하세요",
                opts,
                key=f"q{i}",
                label_visibility="collapsed"
            )
            answers.append(answer)

        submitted = st.form_submit_button("✨ 나의 MBTI 결과 보기", use_container_width=True)

        if submitted:
            if not name:
                st.error("이름을 입력해주세요!")
            else:
                with st.spinner("당신의 MBTI를 분석하는 중..."):
                    mbti_result = generate_mbti(answers)

                if mbti_result:
                    st.success("결과가 나왔습니다!")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("MBTI 유형", mbti_result["mbti"])
                        st.metric("별명", mbti_result["nickname"])
                    with col2:
                        st.write(f"**설명**: {mbti_result['description']}")

                    with st.expander("📖 상세 해설 보기"):
                        st.write(mbti_result["explanation"])

                    if st.button("💾 결과 저장하기", use_container_width=True):
                        records = load_records()
                        today = datetime.now().strftime("%Y-%m-%d")
                        records.append({
                            "nick": name,
                            "mbti": mbti_result["mbti"],
                            "answers": answers,
                            "day": today
                        })
                        save_records(records)
                        st.success(f"✅ {name}의 MBTI가 저장되었습니다!")
                        st.balloons()
                else:
                    st.error("MBTI 분석에 실패했습니다. 다시 시도해주세요.")

with tab2:
    st.header("📊 반 친구들의 MBTI 결과")

    records = load_records()

    if records:
        st.metric("👥 참여한 친구 수", len(records))
        st.divider()

        # 테이블로 표시
        df_data = []
        for record in records:
            df_data.append({
                "이름": record["nick"],
                "MBTI": record["mbti"],
                "참여 날짜": record["day"]
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

        st.divider()

        # 반 분위기 분석
        st.subheader("🎨 우리 반의 분위기 분석")
        with st.spinner("반 전체의 분위기를 분석하는 중..."):
            analysis = analyze_class_vibe(records)

        if analysis:
            st.write(analysis)

        # MBTI 분포 시각화
        st.subheader("📈 MBTI 분포")
        mbti_counts = {}
        for record in records:
            mbti = record["mbti"]
            mbti_counts[mbti] = mbti_counts.get(mbti, 0) + 1

        if mbti_counts:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.bar_chart(pd.DataFrame({
                    "MBTI": list(mbti_counts.keys()),
                    "인원": list(mbti_counts.values())
                }).set_index("MBTI"))

            with col2:
                st.write("**MBTI 분포**")
                for mbti, count in sorted(mbti_counts.items(), key=lambda x: -x[1]):
                    st.write(f"{mbti}: {count}명")

        # 기록 삭제 섹션
        st.divider()
        st.subheader("🗑️ 기록 관리")
        with st.expander("기록 삭제하기"):
            if records:
                target = st.selectbox(
                    "삭제할 친구 선택",
                    [r["nick"] for r in records]
                )
                if st.button("선택한 기록 삭제", use_container_width=True):
                    records = [r for r in records if r["nick"] != target]
                    save_records(records)
                    st.success(f"✅ {target}의 기록이 삭제되었습니다!")
                    st.rerun()
    else:
        st.info("아직 참여한 친구가 없습니다. 위의 '📝 참여하기' 탭에서 MBTI를 등록해주세요!")
