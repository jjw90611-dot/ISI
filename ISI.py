import streamlit as st
import sqlite3
import datetime
import random
import requests

# ==========================================
# [초기 설정] 페이지 세팅
# ==========================================
st.set_page_config(page_title="산업안전지도사 AI 학습 센터", page_icon="⚙️", layout="centered")

# ==========================================
# [Groq API 키 설정] (기출문제 첨삭용)
# ==========================================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ 스트림릿 설정(Settings) -> Secrets에 'GROQ_API_KEY'를 먼저 입력해주세요!")
    st.stop()

# ==========================================
# [데이터베이스 설정] SQLite3 (학습 기록용)
# ==========================================
conn = sqlite3.connect('safety_study.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS study_records (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, question TEXT, user_answer TEXT, ai_feedback TEXT)''')
conn.commit()

# ==========================================
# [기출문제 데이터베이스]
# ==========================================
QUESTIONS = [
    "산업용 로봇의 작동범위에서 교시 등의 작업을 하는 경우 지침에 포함되어야 할 사항 5가지를 쓰시오.",
    "위험기계ㆍ기구 자율안전확인 고시에 따라 산업용 로봇의 보기 쉬운 곳에 표시해야 하는 사항 5가지를 쓰시오.",
    "크레인의 방호장치 중 권과방지장치(Over-hoisting limiter)와 과부하방지장치(Overload limiter)에 대하여 각각 설명하시오.",
    "줄걸이용 와이어로프 단말처리 방법 5가지를 쓰고, 각각 설명하시오.",
    "보일러에서 발생되는 이상연소현상 4가지를 쓰고, 각각에 대하여 설명하시오.",
    "보일러 가동시 발생증기 이상 요인으로서 프라이밍, 포밍, 캐리오버 현상에 대하여 설명하고, 캐리오버 방지대책 5가지를 쓰시오.",
    "지게차 재해방지대책 중 방호장치 5가지를 쓰고, 각 장치에 관하여 설명하시오.",
    "기계ㆍ기구ㆍ설비를 설계할 때 사용하는 S-N 곡선의 가로축, 세로축의 의미와 수평부분에 해당하는 세로축 값을 쓰시오.",
    "기계의 운동형태에 따라 기계설비의 위험점을 분류할 때, 6가지 위험점을 쓰고 각 위험점에 관하여 설명하시오.",
    "기계ㆍ기구의 고장률과 사용시간의 관계를 나타내는 욕조곡선의 고장종류 3가지와 그 정의를 쓰시오.",
    "산업안전보건기준에 관한 규칙상 동력을 사용하는 항타기 또는 항발기에 대하여 무너짐을 방지하기 위한 준수사항 5가지를 쓰시오.",
    "프레스 및 전단기의 방호장치 5가지를 쓰시오."
]

# ==========================================
# [응원 메시지 리스트]
# ==========================================
ENCOURAGEMENTS = [
    "힘내면 무조건 할 수 있다! 포기하지 마세요. 💪",
    "사랑하는 많은 사람들이 당신의 도전을 진심으로 응원합니다. ❤️",
    "잘할 수 있다 지연아! 우리는 늘 널 응원해! ✨",
    "오늘 흘린 땀방울이 합격의 기쁨으로 돌아올 거예요. 아자쓰! 🔥",
    "조금만 더 힘내요! 합격증을 손에 쥐는 그날까지 화이팅! 🍀",
    "지연아, 넌 충분히 해낼 수 있는 사람이야. 자신감을 가져! 🌟",
    "지치고 힘들 땐 잠시 쉬어가도 괜찮아. 넌 이미 너무 잘하고 있어! 💛"
]

# ==========================================
# [CSS] 전역 서울남산체 적용 및 UI 디자인
# ==========================================
st.markdown("""
<style>
    @font-face {
        font-family: 'SeoulNamsan';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/SeoulNamsanM.woff') format('woff');
        font-weight: normal; font-style: normal;
    }

    html, body, [class*="st-"], p, h1, h2, h3, h4, h5, h6, label, input, textarea, button, li, a, strong, b, div, span {
        font-family: 'SeoulNamsan', sans-serif !important;
    }

    span[data-testid="stIconMaterial"], .material-icons, i {
        font-family: 'Material Icons', 'Material Symbols Rounded', sans-serif !important;
    }

    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: #f8fafc; }
    
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
        background-color: #1e293b !important; border: 2px solid #00A3E0 !important; border-radius: 10px !important;
    }
    input, textarea { color: #ffffff !important; font-size: 16px !important; }
    
    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(45deg, #00A3E0, #003876) !important; 
        color: #ffffff !important; font-weight: 900 !important; font-size: 16px !important; 
        border: none !important; border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(0, 163, 224, 0.4) !important; transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(0, 163, 224, 0.6) !important; }

    .stTabs [data-baseweb="tab-list"] { gap: 5px; justify-content: center; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(255,255,255,0.1); border-radius: 8px 8px 0 0; padding: 10px 15px; color: #cbd5e1; font-size: 14px; }
    .stTabs [aria-selected="true"] { background-color: rgba(0, 163, 224, 0.3); color: #7dd3fc !important; border-bottom: 3px solid #00A3E0; font-weight: bold; }

    /* 아코디언(Expander) 디자인 수정 - 클릭해도 제목이 노란색으로 잘 보이게 설정 */
    [data-testid="stExpander"] { background-color: rgba(30, 41, 59, 0.8) !important; border: 1px solid #00A3E0 !important; border-radius: 10px !important; }
    [data-testid="stExpander"] summary p { color: #fde047 !important; font-weight: bold !important; font-size: 16px !important; }
    [data-testid="stExpanderDetails"] { background-color: transparent !important; }
    [data-testid="stExpanderDetails"] p, [data-testid="stExpanderDetails"] li { color: #f8fafc !important; font-size: 15px !important; line-height: 1.6 !important; }

    .neon-title { font-size: 40px; font-weight: 900; color: #ffffff; text-align: center; margin-top: 20px; margin-bottom: 10px; letter-spacing: 1px; text-shadow: 0 0 10px #00A3E0, 0 0 20px #00A3E0; }
    .sub-title { color: #94a3b8; font-size: 16px; margin-bottom: 30px; text-align: center; }
    
    .question-box { background: rgba(255,255,255,0.05); border-left: 5px solid #facc15; padding: 20px; border-radius: 10px; font-size: 18px; font-weight: bold; margin-bottom: 20px; line-height: 1.5; }
    .ai-box { background: rgba(16, 185, 129, 0.1); border-left: 5px solid #10b981; padding: 20px; border-radius: 10px; font-size: 16px; line-height: 1.6; margin-top: 20px; white-space: pre-wrap; }
    
    /* 링크 버튼 호버 효과 */
    .link-btn-container:hover { transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# [세션 상태 관리]
# ==========================================
if 'current_question' not in st.session_state: st.session_state['current_question'] = ""
if 'ai_feedback' not in st.session_state: st.session_state['ai_feedback'] = ""
if 'cheer_msg' not in st.session_state: st.session_state['cheer_msg'] = random.choice(ENCOURAGEMENTS)

# ==========================================
# [화면 구성] 메인 학습 화면 (로그인 없이 바로 진입)
# ==========================================
st.markdown("<div class='neon-title'>POSCO FUTURE M<br>산업안전지도사 AI 센터</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>기계안전공학 완벽 대비! 30년 차 출제위원 AI가 당신의 답안을 첨삭합니다.</div>", unsafe_allow_html=True)

st.markdown(f"""
<div style="background: rgba(255, 193, 7, 0.15); border-left: 5px solid #ffc107; padding: 15px; border-radius: 10px; margin-bottom: 25px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
    <span style="font-size: 18px; font-weight: bold; color: #fde047;">"{st.session_state['cheer_msg']}"</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🔥 빈출 핵심 테마", "🎲 랜덤 기출 풀이", "📚 나의 오답 노트", "🔍 법령 및 KOSHA 가이드"])

# ------------------------------------------
# [탭 1] 빈출 핵심 테마
# ------------------------------------------
with tab1:
    st.markdown("### 📊 최근 기출 기반 출제 빈도 Top 5")
    st.info("아래 테마들은 무조건 암기하고 시험장에 들어가셔야 합니다.")
    
    with st.expander("🥇 1순위: 산업용 로봇 안전 (출제율 최상)"):
        st.write("- 로봇 교시 작업 시 지침 포함 사항")
        st.write("- 로봇 운전 중 위험 방지 조치 및 특별안전보건교육")
        st.write("- 산업용 로봇 구성 요소 및 동작 형태별 분류")
        st.write("- 자율안전확인 표시 사항")
        
    with st.expander("🥈 2순위: 크레인, 양중기 및 와이어로프"):
        st.write("- 이동식 크레인 재해유형 및 방지대책")
        st.write("- 양중기 방호장치 종류 (권과방지, 과부하방지 등)")
        st.write("- 와이어로프 안전계수 계산 및 단말처리 방법")
        
    with st.expander("🥉 3순위: 보일러 및 압축기"):
        st.write("- 보일러 이상증기 발생 (프라이밍, 포밍, 캐리오버) 및 방지대책")
        st.write("- 보일러 이상연소현상 및 고저수위 조절장치")
        st.write("- 공기압축기 작업 전 점검사항")
        
    with st.expander("🏅 4순위: 지게차 및 하역운반기계"):
        st.write("- 지게차 방호장치 5가지 및 설명")
        st.write("- 지게차 낙하물 재해 예방 장치")
        
    with st.expander("🏅 5순위: 기계설계 안전 및 재료역학"):
        st.write("- 기계설계 시 위험요소 및 위험점 6가지")
        st.write("- 욕조곡선(Bathtub curve) 고장 종류")
        st.write("- 응력집중계수, 사용응력 및 허용응력, S-N 곡선")

# ------------------------------------------
# [탭 2] 랜덤 기출 풀이 및 AI 첨삭
# ------------------------------------------
with tab2:
    st.markdown("### ✍️ 실전 모의고사")
    
    if st.button("🎲 새로운 기출문제 뽑기", use_container_width=True):
        st.session_state['current_question'] = random.choice(QUESTIONS)
        st.session_state['ai_feedback'] = ""
        st.session_state['cheer_msg'] = random.choice(ENCOURAGEMENTS)
        st.rerun()
        
    if st.session_state['current_question']:
        st.markdown(f"<div class='question-box'>Q. {st.session_state['current_question']}</div>", unsafe_allow_html=True)
        
        user_answer = st.text_area("답안을 작성하세요 (실제 시험처럼 키워드 위주로 작성해보세요)", height=200)
        
        if st.button("✨ AI 출제위원에게 정답 보완 및 첨삭 받기", use_container_width=True):
            if not user_answer.strip():
                st.warning("답안을 조금이라도 작성해야 첨삭이 가능합니다.")
            else:
                with st.spinner("30년 차 출제위원이 답안을 분석하고 모범 답안을 작성 중입니다... ⏳"):
                    try:
                        prompt = f"""
                        당신은 30년 경력의 산업안전지도사(기계안전) 출제 위원입니다.
                        문제: {st.session_state['current_question']}
                        수험생의 답변: {user_answer}
                        
                        [지시사항]
                        1. 수험생의 답변을 100점 만점 기준으로 채점하고 짧은 총평을 해주세요.
                        2. 누락된 핵심 법적 키워드나 공학적 개념을 추가하여 완벽한 모범 답안을 제시해주세요.
                        3. 수식을 포함한 답변을 작성할 때, 수식 전후에 반드시 개행을 두 번 추가하여 수식이 명확하게 구분되도록 하세요.
                        4. 전문적이고 명확한 어조(~합니다, ~입니다)를 사용하세요.
                        """
                        
                        url = "https://api.groq.com/openai/v1/chat/completions"
                        headers = {
                            "Authorization": f"Bearer {GROQ_API_KEY}",
                            "Content-Type": "application/json"
                        }
                        data = {
                            "model": "llama-3.3-70b-versatile", # 최신 지원 모델로 변경 완료
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.3
                        }
                        
                        response = requests.post(url, headers=headers, json=data, timeout=15)
                        
                        if response.status_code == 200:
                            feedback = response.json()['choices'][0]['message']['content']
                            st.session_state['ai_feedback'] = feedback
                            
                            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            c.execute("INSERT INTO study_records (user_id, date, question, user_answer, ai_feedback) VALUES (?, ?, ?, ?, ?)", 
                                      ("지연", now, st.session_state['current_question'], user_answer, feedback))
                            conn.commit()
                        else:
                            st.error(f"🚨 API 호출 오류가 발생했습니다. (상태 코드: {response.status_code})")
                            st.error(f"상세 에러 내용: {response.text}")
                    except Exception as e:
                        st.error(f"🚨 통신 오류가 발생했습니다: {e}")
                        
        if st.session_state['ai_feedback']:
            st.markdown(f"<div class='ai-box'><b>💡 [AI 출제위원의 첨삭 결과]</b><br><br>{st.session_state['ai_feedback']}</div>", unsafe_allow_html=True)
    else:
        st.info("위의 '새로운 기출문제 뽑기' 버튼을 눌러 학습을 시작하세요.")

# ------------------------------------------
# [탭 3] 나의 오답 노트
# ------------------------------------------
with tab3:
    st.markdown("### 📚 내가 작성한 답안 및 AI 피드백 기록")
    
    c.execute("SELECT id, date, question, user_answer, ai_feedback FROM study_records WHERE user_id=? ORDER BY id DESC", ("지연",))
    records = c.fetchall()
    
    if not records:
        st.info("아직 학습 기록이 없습니다. 실전 모의고사를 풀어보세요!")
    else:
        for record in records:
            r_id, date, q, ans, ai = record
            with st.expander(f"📝 {date} 학습 기록 (클릭하여 펼치기)"):
                st.markdown(f"**Q. {q}**")
                st.markdown(f"<div style='background:rgba(255,255,255,0.1); padding:10px; border-radius:5px;'><b>나의 답안:</b><br>{ans}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background:rgba(16,185,129,0.1); padding:10px; border-radius:5px; margin-top:10px;'><b>AI 피드백:</b><br>{ai}</div>", unsafe_allow_html=True)
                
                if st.button("🗑️ 이 기록 삭제", key=f"del_{r_id}"):
                    c.execute("DELETE FROM study_records WHERE id=?", (r_id,))
                    conn.commit()
                    st.rerun()

# ------------------------------------------
# [탭 4] 법령 및 KOSHA 가이드 외부 링크
# ------------------------------------------
with tab4:
    st.markdown("### 🔍 안전보건 법령 및 KOSHA 가이드")
    st.write("아래 버튼을 클릭하면 해당 사이트로 이동하여 원문을 검색할 수 있습니다.")
    st.write("")
    
    # asdfg.kr (법령 검색) 바로가기 버튼
    st.markdown("""
    <a href="https://asdfg.kr" target="_blank" style="text-decoration: none;">
        <div class="link-btn-container" style="background: linear-gradient(135deg, #00A3E0 0%, #003876 100%); padding: 18px; border-radius: 10px; text-align: center; color: white; font-weight: bold; font-size: 18px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0, 163, 224, 0.4); transition: transform 0.2s;">
            ⚖️ 안전보건 법령 통합 검색 (asdfg.kr) 바로가기
        </div>
    </a>
    """, unsafe_allow_html=True)

    # KOSHA 가이드 바로가기 버튼
    st.markdown("""
    <a href="https://portal.kosha.or.kr/archive/resources/tech-support/revision/RevisionNoticePage" target="_blank" style="text-decoration: none;">
        <div class="link-btn-container" style="background: linear-gradient(135deg, #00B188 0%, #007A5E 100%); padding: 18px; border-radius: 10px; text-align: center; color: white; font-weight: bold; font-size: 18px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0, 177, 136, 0.4); transition: transform 0.2s;">
            📗 KOSHA GUIDE (안전보건기술지침) 제·개정 공표 바로가기 
        </div>
    </a>
    """, unsafe_allow_html=True)

# ==========================================
# [푸터]
# ==========================================
st.markdown("""
<hr style="border-color: rgba(255,255,255,0.1); margin-top: 40px;">
<div style="text-align: center; color: #64748b; font-size: 12px;">
    © POSCO FUTURE M Assistant. 지연님의 산업안전지도사 합격을 진심으로 기원합니다!
</div>
""", unsafe_allow_html=True)
