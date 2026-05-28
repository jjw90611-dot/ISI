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
# [Groq API 키 설정] (기출문제 첨삭 및 출제용)
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
# [기출문제 데이터베이스] (2013~2024년 전체 반영)
# ==========================================
QUESTIONS = [
    "위험기계·기구 방호조치 기준상 원심기의 회전체 접촉예방장치 설치방법 3가지를 쓰시오.",
    "산업안전보건법령상 안전인증대상기계등이 아닌 유해·위험기계 등의 안전인증의 표시 및 표시방법 5가지를 서술하시오.",
    "산업안전보건법령상 유해위험 방지를 위한 방호조치가 필요한 기계·기구를 5가지만 쓰시오.",
    "프레스 금형작업의 안전에 관한 기술지침(KOSHA GUIDE M-138-2013)에 따라 금형 해체 시 위험방지를 위한 안전규칙 3가지를 쓰시오.",
    "산업안전보건기준에 관한 규칙상 사업주가 양중기에 사용해서는 안되는 와이어로프의 사용금지 기준을 5가지만 쓰시오.",
    "공장자동화설비를 위한 산업용 로봇에 관련하여 다음 물음에 답하시오. (1) 사용용도별 5가지 구분 (2) 안전방책 설치방법 5가지 (3) 안전매트 설치방법 3가지",
    "산업안전보건기준에 관한 규칙상 차량계 하역운반기계인 고소작업대를 사용하는 경우 사업주가 준수하여야 할 사항 8가지를 서술하시오.",
    "위험기계·기구방호조치 기준상 동력에 의해서 구동되고 토출압력이 0.2MPa 이상으로 토출량이 분당 1세제곱미터 이상인 공기압축기에 설치하는 안전밸브의 적합요건 2가지와 설치방법 3가지를 각각 서술하시오.",
    "산업용 로봇의 사용 등에 관한 안전 기술지침(KOSHA GUIDE M-61-2017)에 따라 사업주가 산업용 로봇에 대한 정기 검사시 점검사항을 8가지만 서술하시오.",
    "크레인의 방호장치 중 권과방지장치(Over-hoisting limiter)와 과부하방지장치(Overload limiter)에 대하여 각각 설명하시오.",
    "기계 위험요소 사고체인(accident chain)의 5요소를 쓰고, 각 요소에 대하여 설명하시오.",
    "줄걸이용 와이어로프 단말처리 방법 5가지를 쓰고, 각각 설명하시오.",
    "공장자동화에서 FMS(Flexible Manufacturing System)로서 구비하여야 할 기본기능에 대하여 5가지만 쓰시오.",
    "위험기계ㆍ기구 안전인증 고시에 따라 사출성형기에 사용되는 III형식(type III) 방호장치의 작동 설계조건 4가지를 쓰시오.",
    "한국산업표준에 따라 기중기에 체결하여 근로자를 운반하기 위한 탑승설비(플랫폼)의 설계와 설치 규칙에 대하여 설명하시오.",
    "보일러 관리와 관련하여 다음 물음에 답하시오. (1) 불순물이 포함된 보일러수를 사용할 경우의 문제점 (2) 이상연소현상 4가지 (3) 고저수위 조절장치 설명",
    "금속재료의 소성가공과 관련하여 다음 물음에 답하시오. (1) 압연, 인발, 압출, 전조, 판금가공 설명 (2) 압출가공 시 발생되는 위험요인",
    "산업안전보건기준에 관한 규칙에 따라 다음 물음에 답하시오. (1) 작업장 출입구 설치 시 준수사항 5가지 (2) 동력으로 작동되는 문의 설치 조건 5가지 (3) 가설통로 설치 시 준수사항 5가지",
    "위험기계ㆍ기구 자율안전확인 고시에 따라 산업용 로봇의 보기 쉬운 곳에 쉽게 지워지지 않는 방법으로 표시해야 하는 사항 중 5가지를 쓰시오.",
    "압연가공 시 위험요인 4가지를 쓰시오.",
    "산업안전보건기준에 관한 규칙상 기계설비 설치를 위하여 사업주가 사다리식 통로 등을 설치하는 경우 준수하여야 하는 사항에 관하여 빈칸(발판 간격, 폭, 상단 여유, 계단참, 기울기 등)의 기준을 쓰시오.",
    "공장자동화 추진 시 안전을 위한 방호대책 중 5가지를 쓰시오.",
    "기계ㆍ기구ㆍ설비를 설계할 때 사용하는 S-N 곡선과 관련하여 가로축, 세로축의 의미와 수평부분에 해당하는 세로축 값을 쓰시오.",
    "보일러 가동시 발생증기 이상 요인으로서 프라이밍, 포밍, 캐리오버 현상에 대하여 각각 설명하고, 캐리오버 방지대책 중 5가지를 쓰시오.",
    "산업안전보건기준에 관한 규칙에 따른 기어 및 감속기의 유지보수에 관한 기술지침상 “기어 및 감속기의 보수시 유의사항” 중 5가지를 쓰시오.",
    "컨베이어에 관하여 다음 물음에 답하시오. (1) 종류 5가지 (2) 작업 시작 전 점검사항 4가지 (3) 안전작업수칙 5가지",
    "산업안전보건기준에 관한 규칙상 동력을 사용하는 항타기 또는 항발기에 대하여 무너짐을 방지하기 위하여 사업주가 준수하여야 하는 사항 중 5가지를 쓰시오.",
    "절삭가공에서 절삭제의 사용목적 3가지를 쓰시오.",
    "기계ㆍ기구ㆍ설비의 설계 제작에 관련된 사용응력(Working Stress) 및 허용응력(Allowable Stress)에 관하여 각각 쓰시오.",
    "산업안전보건기준에 관한 규칙상 진동작업에 해당하는 작업 3가지를 쓰시오.",
    "산업용 로봇을 동작 형태별로 분류할 때, 그 종류 4가지를 쓰시오.",
    "산업안전보건기준에 관한 규칙상 항타기 또는 항발기를 조립할 때 점검사항 3가지를 쓰시오.",
    "산업안전보건기준에 관한 규칙상 용접ㆍ용단 작업 등의 화재위험작업을 할 때 작업을 시작하기 전에 관리감독자가 확인할 점검사항 5가지를 쓰시오.",
    "지게차 재해방지대책 중 방호장치 5가지를 쓰고, 각 장치에 관하여 설명하시오.",
    "산업안전보건기준에 관한 규칙상 건축물이나 고정된 시설물에 설치되어 일정한 경로에 따라 사람이나 화물을 승강장으로 옮기는 데에 사용되는 설비(기계) 5가지를 쓰고, 각 설비(기계)에 관하여 설명하시오.",
    "기계의 운동형태에 따라 기계설비의 위험점을 분류할 때, 6가지 위험점을 쓰고 각 위험점에 관하여 설명하시오.",
    "산업안전보건기준에 관한 규칙상 로봇의 작동 범위에서 그 로봇에 관하여 교시 등의 작업을 할 때, 작업시작 전 점검사항 3가지를 쓰시오.",
    "생산공정 자동화에 이용되는 수치제어(NC) 공작기계의 작동원리에 대하여 설명하시오.",
    "유압시스템의 고장 증상 중 유압의 저하(실린더 추력의 감소) 원인 5가지를 쓰시오.",
    "기계의 고장률 추이를 나타내는 욕조곡선의 3가지 구간을 쓰고 전동기 베어링이 미스얼라인먼트로 파손되었다면 이것은 욕조 곡선의 어느 구간에 속하는지 쓰시오.",
    "하중이 반복하여 작용함에 따라 균열이 발생하고 성장하여 부품이 파단되는 현상과 하중을 유지하여도 부품의 변형이 계속 증가하는 현상에 대한 용어를 쓰시오.",
    "프레스의 광전자식 방호장치를 레이저식으로 설치하는 경우 설치기준 2가지와 시험 만족기준 3가지를 쓰시오.",
    "설비의 신뢰성을 나타내는 척도로 신뢰도, 평균 고장 간격 시간, 평균 고장 수리 시간, 고장률 각각의 정의를 쓰고, 평균 고장 간격 시간과 고장률의 관계를 쓰시오.",
    "산업안전보건기준에 관한 규칙상 지게차 헤드가드 안전기준 2가지와 양중기에 사용하는 와이어로프 등 달기구의 안전계수 기준 3가지를 쓰시오.",
    "기계설비의 안전화 방안으로 풀 프루프(fool proof)와 페일 세이프(fail safe) 각각의 정의를 쓰고, 해당하는 사례를 각각 3가지씩 쓰시오.",
    "위험기계ㆍ기구 안전인증 고시에 따라 고소작업대의 무게중심 및 주행장치를 분류하고 설명하시오.",
    "기계ㆍ기구ㆍ설비의 설계 제작에 관련된 응력집중 계수(Stress Concentration Factor)에 관하여 쓰시오.",
    "지게차에 있어야 하는 장치 명칭과 장치의 3가지 설치기준을 쓰시오. (낙하물 재해 예방)",
    "금속의 용접ㆍ용단 또는 가열에 사용되는 가스 등의 용기를 취급하는 경우, 사용ㆍ설치ㆍ저장 또는 방치하지 않아야 할 3가지 장소에 관하여 쓰시오.",
    "원심펌프가 흡수면으로부터 높게 설치되고 흡입배관이 복잡할 때 발생할 수 있는 문제를 방지하기 위한 5가지 대책을 쓰시오.",
    "공기압축기를 가동할 때 작업을 시작하기 전에 관리 감독자가 확인할 점검사항에 관하여 쓰시오.",
    "줄걸이용 와이어로프의 안전계수를 구하고 사용가능 여부를 판단하며, 고리부분을 꼬아넣기(아이 스플라이스)로 제작하는 방법에 관하여 쓰시오.",
    "공장 자동화에 필요한 산업용 로봇의 4가지 구성 요소에 관하여 쓰시오.",
    "천장주행 크레인의 거더 단면의 형상이 주어졌을 때, 단면 2차 모멘트와 단면계수의 값을 구하시오.",
    "로봇의 운전 중 위험을 방지하기 위해 필요한 조치사항을 쓰시오.",
    "과부하방지장치, 권과방지장치, 비상정지장치 및 제동장치, 그 밖의 방호장치가 정상적으로 작동될 수 있도록 미리 조정해 두어야 하는 양중기의 종류 5가지를 쓰시오.",
    "프레스 및 전단기의 방호장치 5가지를 쓰시오.",
    "기계ㆍ기구에 주로 사용되는 풀프루프(fool proof)의 종류 5가지를 쓰시오.",
    "분진 등을 배출하기 위한 국소배기장치의 덕트 설치기준 5가지를 쓰시오.",
    "기계ㆍ기구의 고장률과 사용시간의 관계를 나타내는 욕조곡선의 고장종류 3가지와 그 정의, 이와 연관된 고장유형을 쓰시오.",
    "화학설비와 그 부속 설비를 사용하여 작업 시 작성하여야 하는 작업계획서의 내용 10가지를 쓰시오.",
    "자동제어장치의 주요 구성 요소 3가지에 관하여 설명하시오.",
    "로봇작업 시 특별안전ㆍ보건교육 내용 4가지를 쓰시오.",
    "윤활유의 점도지수(Viscosity Index)에 관하여 쓰시오.",
    "고소작업대를 사용하여 작업을 할 때 작업시작 전 점검사항 5가지를 쓰시오.",
    "고속회전체의 회전시험을 하는 경우 파괴로 인한 위험을 방지하기 위하여 지켜야 할 안전기준과 비파괴검사를 실시하여야 할 대상을 쓰시오.",
    "로봇 및 자동화 기계설비에 사용되는 물체 감지용 센서의 종류 3가지를 쓰시오.",
    "중량물의 취급작업 시 작성해야 하는 작업계획서 내용 5가지를 쓰시오.",
    "평와셔(Plain Washer)의 용도를 쓰고, 너트(Nut)의 풀림방지법 5가지를 쓰고 설명하시오.",
    "산업용 로봇의 위험성과 방호장치의 종류, 사용 단계에서의 안전대책을 쓰시오.",
    "안전난간의 구조 및 설치요건 5가지를 쓰시오.",
    "공장자동화 기계설비에 사용하는 PLC(Programmable Logic Controller) 기능에 관하여 5가지를 쓰시오.",
    "구내운반차를 사용하여 작업을 할 때 작업시작 전 점검사항 5가지를 쓰시오.",
    "크레인 작업 시 사업주가 관계 근로자에게 준수하도록 해야 할 조치사항 5가지를 쓰시오.",
    "입력정보교시에 의한 산업용 로봇 종류 5가지를 쓰시오.",
    "유해하거나 위험한 기계·기구 중 동력으로 작동하는 기계·기구에 추가적인 방호조치를 해야 할 해당부분 3가지와 그 방호조치를 쓰시오.",
    "안전검사 대상 유해·위험기계 10가지를 쓰시오.",
    "산업현장에서 사용되는 컨베이어(conveyer)의 안전장치 및 보수상의 주의사항을 쓰시오.",
    "고소작업대 설치 시 사업주가 조치해야 할 설치사항 6가지를 쓰시오.",
    "기계·기구에 적용되고 있는 페일세이프(fail safe)의 정의와 기능적 측면에서 3단계로 분류하여 각각 쓰시오.",
    "선반의 방호장치 3가지와 작업 시 안전대책 10가지를 쓰시오.",
    "산업용 로봇의 작동범위에서 교시 등의 작업을 하는 경우 지침에 포함되어야 할 사항 5가지를 쓰시오.",
    "연삭숫돌에 표시된 WA46H8V 의미를 쓰시오.",
    "방호조치를 해야 하는 기계ㆍ기구의 종류 6가지와 설치하여야 하는 해당 방호장치를 쓰시오.",
    "디젤발전기 엔진에서 화재발생 가능성이 있는 발화요인 4가지를 쓰시오.",
    "비파괴시험의 종류 6가지를 쓰시오.",
    "기계설계 시 고려하여야 하는 위험요소(hazards) 7가지와 각각의 원인 및 그 결과에 관하여 쓰시오.",
    "기계설비의 정비(maintenance) 종류와 정비작업 시 조치하여야할 안전수칙 4가지를 쓰시오.",
    "이동식 크레인에서 발생할 수 있는 재해유형을 서술하고, 재해방지대책 4가지를 쓰시오.",
    "공작기계에 사용하는 유공압장치가 공통으로 구비해야할 안전사항 8가지를 쓰시오.",
    "방호장치를 선정할 때 고려해야 할 사항 5가지를 쓰시오.",
    "작용방향에 따른 하중의 종류 3가지와 그 내용을 쓰시오.",
    "공장설비의 배치 계획시 고려해야 할 사항 5가지를 쓰시오.",
    "설비보전활동 중 예방보전의 종류 3가지와 그 내용을 쓰시오.",
    "사업주가 안전밸브 등으로부터 배출되는 위험물을 안전한 장소로 유도하여 외부로 직접 배출할 수 있는 경우 3가지를 쓰시오.",
    "산업용 로봇의 설계 및 계획 단계에서 안전방호를 위해 고려되어야 할 사항과 로봇을 사용하는 단계에서 안전방호를 위한 조치사항을 쓰시오.",
    "작업용 리프트에 설치된 와이어 로프의 교체기준을 제시하고 검사의 판정결과 및 사유를 쓰시오.",
    "크레인 작업 시 발생될 수 있는 재해유형별 원인과 방지대책을 쓰시오.",
    "공장자동화설비가 안전측면에서 미치는 문제점과 방호대책을 쓰시오.",
    "기계의 운동형태에 따른 위험점 6가지를 예를 들어 간단히 쓰시오.",
    "방호조치를 해야하는 위험기계·기구를 명시하고 각각에 대한 방호조치를 쓰시오.",
    "프레스 작업을 시작하기 전에 관리감독자가 점검해야 할 사항(점검 내용)을 5가지 쓰시오.",
    "기어(Gear) 손상의 종류 5가지와 각각에 대한 손상방지 대책을 간단히 쓰시오.",
    "와이어로프와 달기체인의 사용금지 기준을 쓰시오.",
    "연삭작업에서 숫돌의 파괴원인과 재해예방을 위한 구조면에서의 방호대책을 설명하시오.",
    "보일러의 사고원인과 주요 방호장치 3가지를 설명하시오.",
    "산업용 로봇의 교시 등의 작업을 하는 경우에 있어서 안전조치에 대하여 설명하시오.",
    "체결된 볼트·너트의 풀림에 대한 발생원인과 풀림방지방법에 대하여 설명하시오."
]

# ==========================================
# [테마별 역대 기출문제 매핑 (AI 변형 출제용)]
# ==========================================
THEME_PAST_QUESTIONS = {
    "1. 산업용 로봇 (교시, 방호장치, 분류 등)": [
        "산업용 로봇의 작동범위에서 교시 등의 작업을 하는 경우 지침에 포함되어야 할 사항 5가지를 쓰시오.",
        "로봇의 운전 중 위험을 방지하기 위해 필요한 조치사항을 쓰시오.",
        "산업용 로봇을 동작 형태별로 분류할 때, 그 종류 4가지를 쓰시오.",
        "산업용 로봇의 사용 등에 관한 안전 기술지침(KOSHA GUIDE)에 따라 정기 검사시 점검사항을 8가지만 서술하시오.",
        "공장자동화설비를 위한 산업용 로봇에 관련하여 다음 물음에 답하시오. (1) 사용용도별 5가지 구분 (2) 안전방책 설치방법 5가지 (3) 안전매트 설치방법 3가지"
    ],
    "2. 양중기(크레인) 및 와이어로프": [
        "사업주가 양중기에 사용해서는 안되는 와이어로프의 사용금지 기준을 5가지만 쓰시오.",
        "크레인의 방호장치 중 권과방지장치와 과부하방지장치에 대하여 각각 설명하시오.",
        "줄걸이용 와이어로프 단말처리 방법 5가지를 쓰고, 각각 설명하시오.",
        "이동식 크레인에서 발생할 수 있는 재해유형을 서술하고, 재해방지대책 4가지를 쓰시오.",
        "줄걸이용 와이어로프의 안전계수를 구하고 사용가능 여부를 판단하며, 고리부분을 꼬아넣기(아이 스플라이스)로 제작하는 방법에 관하여 쓰시오."
    ],
    "3. 기계설비 안전화 설계 원리 및 신뢰성 공학": [
        "기계설비의 안전화 방안으로 풀 프루프(fool proof)와 페일 세이프(fail safe) 각각의 정의를 쓰고, 해당하는 사례를 각각 3가지씩 쓰시오.",
        "기계의 고장률 추이를 나타내는 욕조곡선의 3가지 구간을 쓰고 전동기 베어링이 미스얼라인먼트로 파손되었다면 이것은 욕조 곡선의 어느 구간에 속하는지 쓰시오.",
        "기계의 운동형태에 따라 기계설비의 위험점을 분류할 때, 6가지 위험점을 쓰고 각 위험점에 관하여 설명하시오.",
        "기계 위험요소 사고체인(accident chain)의 5요소를 쓰고, 각 요소에 대하여 설명하시오."
    ],
    "4. 공장자동화(FA) 설비 (FMS, PLC 등)": [
        "공장자동화에서 FMS(Flexible Manufacturing System)로서 구비하여야 할 기본기능에 대하여 5가지만 쓰시오.",
        "공장자동화 추진 시 안전을 위한 방호대책 중 5가지를 쓰시오.",
        "공장자동화 기계설비에 사용하는 PLC(Programmable Logic Controller) 기능에 관하여 5가지를 쓰시오.",
        "생산공정 자동화에 이용되는 수치제어(NC) 공작기계의 작동원리에 대하여 설명하시오."
    ],
    "5. 하역운반기계 (고소작업대, 지게차)": [
        "차량계 하역운반기계인 고소작업대를 사용하는 경우 사업주가 준수하여야 할 사항 8가지를 서술하시오.",
        "지게차 재해방지대책 중 방호장치 5가지를 쓰고, 각 장치에 관하여 설명하시오.",
        "지게차에 있어야 하는 장치 명칭과 장치의 3가지 설치기준을 쓰시오. (낙하물 재해 예방)",
        "고소작업대를 사용하여 작업을 할 때 작업시작 전 점검사항 5가지를 쓰시오."
    ],
    "6. 보일러 및 압력용기 (공기압축기)": [
        "보일러 가동시 발생증기 이상 요인으로서 프라이밍, 포밍, 캐리오버 현상에 대하여 각각 설명하고, 캐리오버 방지대책 중 5가지를 쓰시오.",
        "공기압축기를 가동할 때 작업을 시작하기 전에 관리 감독자가 확인할 점검사항에 관하여 쓰시오.",
        "보일러의 사고원인과 주요 방호장치 3가지를 설명하시오.",
        "위험기계·기구방호조치 기준상 동력에 의해서 구동되고 토출압력이 0.2MPa 이상으로 토출량이 분당 1세제곱미터 이상인 공기압축기에 설치하는 안전밸브의 적합요건 2가지와 설치방법 3가지를 각각 서술하시오."
    ]
}

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
# [CSS] 전역 서울남산체 적용 및 반응형 UI 디자인
# ==========================================
st.markdown("""
<style>
    /* 기본 폰트 및 데스크탑 UI */
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
    
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {
        background-color: #1e293b !important; border: 2px solid #00A3E0 !important; border-radius: 10px !important;
    }
    input, textarea { color: #ffffff !important; font-size: 16px !important; }
    
    /* Selectbox (드롭다운) 글씨 색상 강제 흰색 적용 */
    div[data-baseweb="select"] > div {
        background-color: #1e293b !important; 
        border: 2px solid #00A3E0 !important; 
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] * { color: #ffffff !important; font-weight: bold !important; }
    div[data-baseweb="select"] svg { fill: #ffffff !important; }
    div[role="listbox"] ul { background-color: #1e293b !important; }
    div[role="listbox"] li { color: #ffffff !important; font-size: 15px !important; }
    div[role="listbox"] li:hover { background-color: #00A3E0 !important; color: #ffffff !important; }
    
    label { color: #f8fafc !important; font-weight: bold !important; font-size: 15px !important; }

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

    /* ==========================================
       [수정됨] Expander (아코디언) 배경 강제 어둡게 설정
       ========================================== */
    [data-testid="stExpander"] { 
        background-color: #1e293b !important; 
        border: 1px solid #00A3E0 !important; 
        border-radius: 10px !important; 
        overflow: hidden !important;
    }
    /* 아코디언 제목 부분 배경을 확실히 어둡게 */
    [data-testid="stExpander"] summary { 
        background-color: #1e293b !important; 
    }
    [data-testid="stExpander"] summary:hover {
        background-color: #0f172a !important; 
    }
    /* 아코디언 제목 글씨 (노란색 유지) */
    [data-testid="stExpander"] summary p { 
        color: #fde047 !important; 
        font-weight: bold !important; 
        font-size: 16px !important; 
    }
    /* 아코디언 화살표 아이콘 색상 */
    [data-testid="stExpander"] svg {
        fill: #fde047 !important; 
    }
    /* 아코디언 펼쳤을 때 내용 배경 및 글씨 */
    [data-testid="stExpanderDetails"] { 
        background-color: #1e293b !important; 
    }
    [data-testid="stExpanderDetails"] p, [data-testid="stExpanderDetails"] li { 
        color: #f8fafc !important; 
        font-size: 15px !important; 
        line-height: 1.6 !important; 
    }

    .neon-title { font-size: 40px; font-weight: 900; color: #ffffff; text-align: center; margin-top: 20px; margin-bottom: 10px; letter-spacing: 1px; text-shadow: 0 0 10px #00A3E0, 0 0 20px #00A3E0; }
    .sub-title { color: #94a3b8; font-size: 16px; margin-bottom: 30px; text-align: center; }
    
    .question-box { background: rgba(255,255,255,0.05); border-left: 5px solid #facc15; padding: 20px; border-radius: 10px; font-size: 18px; font-weight: bold; margin-bottom: 20px; line-height: 1.5; }
    .ai-box { background: rgba(16, 185, 129, 0.1); border-left: 5px solid #10b981; padding: 20px; border-radius: 10px; font-size: 16px; line-height: 1.6; margin-top: 20px; white-space: pre-wrap; }
    
    .link-btn-container:hover { transform: translateY(-2px); }

    /* ==========================================
       [모바일 전용 반응형 CSS] 
       ========================================== */
    @media (max-width: 768px) {
        .neon-title { font-size: 28px !important; line-height: 1.4 !important; margin-top: 10px !important; }
        .sub-title { font-size: 14px !important; line-height: 1.6 !important; padding: 0 10px !important; word-break: keep-all !important; }
        .question-box { font-size: 16px !important; padding: 15px !important; line-height: 1.7 !important; word-break: keep-all !important; }
        .ai-box { font-size: 15px !important; padding: 15px !important; line-height: 1.8 !important; word-break: keep-all !important; }
        [data-testid="stExpander"] summary p { font-size: 15px !important; line-height: 1.5 !important; word-break: keep-all !important; }
        [data-testid="stExpanderDetails"] p, [data-testid="stExpanderDetails"] li { font-size: 14px !important; line-height: 1.7 !important; word-break: keep-all !important; }
        .stTabs [data-baseweb="tab"] { font-size: 13px !important; padding: 8px 10px !important; }
        .link-btn-container { font-size: 15px !important; padding: 15px !important; word-break: keep-all !important; line-height: 1.5 !important; }
        .mobile-br { display: block !important; content: ""; margin-top: 5px; }
    }

    @media (min-width: 769px) {
        .mobile-br { display: none !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# [세션 상태 관리]
# ==========================================
if 'current_question' not in st.session_state: st.session_state['current_question'] = ""
if 'ai_feedback' not in st.session_state: st.session_state['ai_feedback'] = ""
if 'ai_new_question' not in st.session_state: st.session_state['ai_new_question'] = ""
if 'ai_new_feedback' not in st.session_state: st.session_state['ai_new_feedback'] = ""
if 'cheer_msg' not in st.session_state: st.session_state['cheer_msg'] = random.choice(ENCOURAGEMENTS)

# ==========================================
# [화면 구성] 메인 학습 화면
# ==========================================
st.markdown("<div class='neon-title'>지연만을 위한<br>산업안전지도사 AI 센터</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>기계안전공학 완벽 대비! <br class='mobile-br'>30년 차 출제위원 AI가 <br class='mobile-br'>당신의 답안을 첨삭합니다.</div>", unsafe_allow_html=True)

st.markdown(f"""
<div style="background: rgba(255, 193, 7, 0.15); border-left: 5px solid #ffc107; padding: 15px; border-radius: 10px; margin-bottom: 25px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
    <span style="font-size: 18px; font-weight: bold; color: #fde047; word-break: keep-all;">"{st.session_state['cheer_msg']}"</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab_new, tab3, tab4 = st.tabs(["🔥 빈출 핵심 테마", "🎲 랜덤 기출 풀이", "💡 AI 신출 모의고사", "📚 나의 오답 노트", "🔍 법령 및 KOSHA 가이드"])

# ------------------------------------------
# [탭 1] 빈출 핵심 테마
# ------------------------------------------
with tab1:
    st.markdown("### 📊 최근 기출 기반 출제 빈도 Top 6")
    st.info("아래 테마들은 무조건 암기하고 시험장에 들어가셔야 합니다.")
    
    with st.expander("🥇 1순위: 산업용 로봇 (거의 매년 출제되는 0순위 주제)"):
        st.write("- 교시(Teaching) 작업 시 안전조치/점검사항")
        st.write("- 로봇의 방호장치 및 안전대책")
        st.write("- 로봇의 분류 및 구성요소 (용도별, 동작형태별 등)")
        
    with st.expander("🥈 2순위: 양중기(크레인) 및 와이어로프 (절대 빠지지 않는 단골)"):
        st.write("- 와이어로프 사용금지(폐기) 기준")
        st.write("- 크레인/양중기 방호장치 (권과/과부하방지 등)")
        st.write("- 와이어로프 안전계수 및 단말처리")
        
    with st.expander("🥉 3순위: 기계설비 안전화 설계 원리 및 신뢰성 공학"):
        st.write("- 풀 프루프(Fool Proof)와 페일 세이프(Fail Safe)")
        st.write("- 욕조곡선(Bath-tub curve) 고장률 추이")
        st.write("- 기계의 위험점 분류 (6가지)")
        
    with st.expander("🏅 4순위: 공장자동화(FA) 설비"):
        st.write("- 공장자동화 방호대책 및 문제점")
        st.write("- 자동화 관련 시스템 (FMS, NC, PLC 등)")
        
    with st.expander("🏅 5순위: 하역운반기계 (고소작업대, 지게차)"):
        st.write("- 고소작업대 준수사항 및 점검사항")
        st.write("- 지게차 방호장치 및 안전기준 (헤드가드 등)")
        
    with st.expander("🏅 6순위: 보일러 및 압력용기 (공기압축기)"):
        st.write("- 보일러 이상 현상 (프라이밍, 포밍, 캐리오버 등)")
        st.write("- 공기압축기 점검 및 안전밸브")

# ------------------------------------------
# [탭 2] 랜덤 기출 풀이 및 AI 첨삭
# ------------------------------------------
with tab2:
    st.markdown("### ✍️ 실전 모의고사 (역대 기출문제)")
    
    if st.button("🎲 새로운 기출문제 뽑기", use_container_width=True):
        st.session_state['current_question'] = random.choice(QUESTIONS)
        st.session_state['ai_feedback'] = ""
        st.session_state['cheer_msg'] = random.choice(ENCOURAGEMENTS)
        st.rerun()
        
    if st.session_state['current_question']:
        st.markdown(f"<div class='question-box'>Q. {st.session_state['current_question']}</div>", unsafe_allow_html=True)
        
        user_answer = st.text_area("답안을 작성하세요 (실제 시험처럼 키워드 위주로 작성해보세요)", height=200, key="ans_real")
        
        if st.button("✨ AI 출제위원에게 정답 보완 및 첨삭 받기", use_container_width=True, key="btn_real"):
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
                        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
                        
                        response = requests.post(url, headers=headers, json=data, timeout=15)
                        
                        if response.status_code == 200:
                            feedback = response.json()['choices'][0]['message']['content']
                            st.session_state['ai_feedback'] = feedback
                            
                            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            c.execute("INSERT INTO study_records (user_id, date, question, user_answer, ai_feedback) VALUES (?, ?, ?, ?, ?)", 
                                      ("지연", now, "[기출] " + st.session_state['current_question'], user_answer, feedback))
                            conn.commit()
                        else:
                            st.error(f"🚨 API 호출 오류가 발생했습니다. (상태 코드: {response.status_code})")
                    except Exception as e:
                        st.error(f"🚨 통신 오류가 발생했습니다: {e}")
                        
        if st.session_state['ai_feedback']:
            st.markdown(f"<div class='ai-box'><b>💡 [AI 출제위원의 첨삭 결과]</b><br><br>{st.session_state['ai_feedback']}</div>", unsafe_allow_html=True)
    else:
        st.info("위의 '새로운 기출문제 뽑기' 버튼을 눌러 학습을 시작하세요.")

# ------------------------------------------
# [탭 3] AI 신출 모의고사 (기출 변형 문제)
# ------------------------------------------
with tab_new:
    st.markdown("### 💡 AI 기출 변형 신출 모의고사")
    st.write("역대 기출문제를 바탕으로 상황 제시형, 주변 조항 연계 등 최신 트렌드가 반영된 꼬아낸 문제를 풀어보세요.")
    
    themes = list(THEME_PAST_QUESTIONS.keys())
    selected_theme = st.selectbox("출제 테마를 선택하세요:", themes)
    
    if st.button("🚀 선택한 테마로 기출 변형 문제 출제하기", use_container_width=True):
        with st.spinner("AI 출제위원이 역대 기출문제를 분석하여 변형 문제를 출제 중입니다... ⏳"):
            try:
                past_qs_text = "\n".join([f"- {q}" for q in THEME_PAST_QUESTIONS[selected_theme]])
                
                prompt = f"""
                당신은 산업안전지도사 2차 기계안전공학 출제위원입니다.
                사용자가 선택한 테마: '{selected_theme}'
                
                [해당 테마의 역대 기출문제]
                {past_qs_text}
                
                [출제 지침]
                위 기출문제들을 분석하여, 이와 연관되지만 똑같지는 않은 **'기출 변형 신출 모의고사' 1문제**를 출제하세요.
                단순히 묻는 방식을 바꾸는 것을 넘어 아래 4가지 전략 중 하나 이상을 반드시 적용하여 문제를 꼬아서 내세요.
                1. 주변 조항 연계: 기출에 나온 법령/가이드의 바로 앞뒤 연관 조항이나 예외 조항을 묻기
                2. 상황 제시형(시나리오): "A공장에서 B작업을 하던 중 C사고가 발생했다..." 와 같이 구체적 상황을 주고 원인/대책/방호장치를 묻기
                3. 원리 이해 및 적용: 단순 암기가 아닌, 왜 그런 안전장치가 필요한지 공학적 원리나 계산, 적용 사례를 묻기
                4. 최신 동향 반영: 스마트 팩토리, 무인화 설비 등 최신 산업 트렌드를 기존 기계안전 개념과 엮어서 묻기
                
                반드시 문제만 출력하고, 정답이나 해설은 절대 포함하지 마세요.
                """
                
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
                
                response = requests.post(url, headers=headers, json=data, timeout=15)
                
                if response.status_code == 200:
                    st.session_state['ai_new_question'] = response.json()['choices'][0]['message']['content']
                    st.session_state['ai_new_feedback'] = ""
                else:
                    st.error("🚨 문제 출제 중 오류가 발생했습니다.")
            except Exception as e:
                st.error(f"🚨 통신 오류: {e}")

    if st.session_state['ai_new_question']:
        st.markdown(f"<div class='question-box'>Q. {st.session_state['ai_new_question']}</div>", unsafe_allow_html=True)
        
        user_new_answer = st.text_area("답안을 작성하세요 (상황에 맞는 법적/공학적 근거를 제시하세요)", height=200, key="ans_new")
        
        if st.button("✨ AI 출제위원에게 정답 보완 및 첨삭 받기", use_container_width=True, key="btn_new"):
            if not user_new_answer.strip():
                st.warning("답안을 조금이라도 작성해야 첨삭이 가능합니다.")
            else:
                with st.spinner("AI 출제위원이 답안을 분석하고 모범 답안을 작성 중입니다... ⏳"):
                    try:
                        prompt = f"""
                        당신은 30년 경력의 산업안전지도사(기계안전) 출제 위원입니다.
                        문제: {st.session_state['ai_new_question']}
                        수험생의 답변: {user_new_answer}
                        
                        [지시사항]
                        1. 수험생의 답변을 100점 만점 기준으로 채점하고 짧은 총평을 해주세요.
                        2. 누락된 핵심 법적 키워드나 공학적 개념을 추가하여 완벽한 모범 답안을 제시해주세요.
                        3. 수식을 포함한 답변을 작성할 때, 수식 전후에 반드시 개행을 두 번 추가하여 수식이 명확하게 구분되도록 하세요.
                        4. 전문적이고 명확한 어조(~합니다, ~입니다)를 사용하세요.
                        """
                        
                        url = "https://api.groq.com/openai/v1/chat/completions"
                        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
                        
                        response = requests.post(url, headers=headers, json=data, timeout=15)
                        
                        if response.status_code == 200:
                            feedback = response.json()['choices'][0]['message']['content']
                            st.session_state['ai_new_feedback'] = feedback
                            
                            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            c.execute("INSERT INTO study_records (user_id, date, question, user_answer, ai_feedback) VALUES (?, ?, ?, ?, ?)", 
                                      ("지연", now, "[AI 신출] " + st.session_state['ai_new_question'], user_new_answer, feedback))
                            conn.commit()
                        else:
                            st.error(f"🚨 API 호출 오류가 발생했습니다. (상태 코드: {response.status_code})")
                    except Exception as e:
                        st.error(f"🚨 통신 오류가 발생했습니다: {e}")
                        
        if st.session_state['ai_new_feedback']:
            st.markdown(f"<div class='ai-box'><b>💡 [AI 출제위원의 첨삭 결과]</b><br><br>{st.session_state['ai_new_feedback']}</div>", unsafe_allow_html=True)

# ------------------------------------------
# [탭 4] 나의 오답 노트
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
                st.markdown(f"<div style='background:rgba(255,255,255,0.1); padding:10px; border-radius:5px; word-break: keep-all;'><b>나의 답안:</b><br>{ans}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background:rgba(16,185,129,0.1); padding:10px; border-radius:5px; margin-top:10px; word-break: keep-all;'><b>AI 피드백:</b><br>{ai}</div>", unsafe_allow_html=True)
                
                if st.button("🗑️ 이 기록 삭제", key=f"del_{r_id}"):
                    c.execute("DELETE FROM study_records WHERE id=?", (r_id,))
                    conn.commit()
                    st.rerun()

# ------------------------------------------
# [탭 5] 법령 및 KOSHA 가이드 외부 링크
# ------------------------------------------
with tab4:
    st.markdown("### 🔍 안전보건 법령 및 KOSHA 가이드")
    st.write("아래 버튼을 클릭하면 해당 사이트로 이동하여 원문을 검색할 수 있습니다.")
    st.write("")
    
    st.markdown("""
    <a href="https://asdfg.kr" target="_blank" style="text-decoration: none;">
        <div class="link-btn-container" style="background: linear-gradient(135deg, #00A3E0 0%, #003876 100%); padding: 18px; border-radius: 10px; text-align: center; color: white; font-weight: bold; font-size: 18px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0, 163, 224, 0.4); transition: transform 0.2s;">
            ⚖️ 안전보건 법령 통합 검색 <br class='mobile-br'>(asdfg.kr) 바로가기
        </div>
    </a>
    """, unsafe_allow_html=True)

    st.markdown("""
    <a href="https://portal.kosha.or.kr/archive/resources/tech-support/revision/RevisionNoticePage" target="_blank" style="text-decoration: none;">
        <div class="link-btn-container" style="background: linear-gradient(135deg, #00B188 0%, #007A5E 100%); padding: 18px; border-radius: 10px; text-align: center; color: white; font-weight: bold; font-size: 18px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0, 177, 136, 0.4); transition: transform 0.2s;">
            📗 KOSHA GUIDE (안전보건기술지침) <br class='mobile-br'>제·개정 공표 바로가기 
        </div>
    </a>
    """, unsafe_allow_html=True)

# ==========================================
# [푸터]
# ==========================================
st.markdown("""
<hr style="border-color: rgba(255,255,255,0.1); margin-top: 40px;">
<div style="text-align: center; color: #64748b; font-size: 12px;">
    © Eunho's Family Assistant. 지연님의 산업안전지도사 합격을 진심으로 기원합니다!
</div>
""", unsafe_allow_html=True)
