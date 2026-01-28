import streamlit as st
import time
import os
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="阿美語 - 移動與動作", 
    page_icon="🚶", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 視覺魔法 (大地與探索主題 - 活力版) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Noto+Sans+TC:wght@400;700&display=swap');

    /* 全局背景：大地綠與晨曦橘漸層 */
    .stApp { 
        background-color: #FFF3E0;
        background-image: linear-gradient(180deg, #FFF3E0 0%, #DCEDC8 50%, #C8E6C9 100%);
        font-family: 'Noto Sans TC', sans-serif;
        color: #33691E;
    }
    
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }

    /* --- Header --- */
    .header-container {
        background: rgba(255, 255, 255, 0.6);
        border: 3px solid #8BC34A;
        box-shadow: 0 4px 15px rgba(51, 105, 30, 0.2);
        border-radius: 25px;
        padding: 25px;
        text-align: center;
        margin-bottom: 30px;
        backdrop-filter: blur(5px);
    }
    
    .main-title {
        font-family: 'Roboto Mono', monospace;
        color: #558B2F;
        font-size: 36px;
        font-weight: 800;
        letter-spacing: 1px;
        text-shadow: 2px 2px 0px #DCEDC8;
        margin: 0;
    }
    
    .sub-title { color: #33691E; font-size: 20px; margin-top: 5px; font-weight: bold; letter-spacing: 1px; }
    
    .teacher-tag { 
        display: inline-block; 
        margin-top: 12px; 
        padding: 6px 18px; 
        background: #FF9800; 
        color: #FFF; 
        border-radius: 50px; 
        font-size: 13px; 
        font-weight: bold; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.2); 
    }

    /* --- Cards (單字卡) --- */
    .word-card {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 15px 5px;
        text-align: center;
        border-bottom: 6px solid #FFB74D; /* 橘色底部 */
        height: 100%;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
        transition: all 0.2s ease-in-out;
        color: #424242 !important;
    }
    
    .word-card h3 {
        color: #EF6C00 !important; /* 深橘色標題 */
        font-weight: 800;
        margin: 0;
        padding-bottom: 5px;
    }

    .word-card:hover { transform: translateY(-5px); border-bottom-color: #F57C00; }
    
    .icon-box { font-size: 36px; margin-bottom: 5px; }
    .amis-word { font-size: 17px; font-weight: 700; color: #2E7D32; margin-bottom: 4px; font-family: 'Roboto Mono', monospace; }
    .zh-word { font-size: 14px; color: #616161; font-weight: bold; }

    /* --- Sentences (句子框) --- */
    .sentence-box {
        background: rgba(255, 255, 255, 0.9);
        border-left: 6px solid #558B2F; /* 深綠色邊框 */
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 12px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        color: #37474F !important;
    }
    .sentence-amis { font-size: 18px; color: #1B5E20; font-weight: 700; margin-bottom: 8px; }
    .sentence-zh { font-size: 15px; color: #546E7A; }

    /* --- Buttons --- */
    .stButton>button { width: 100%; border-radius: 30px; background: linear-gradient(to right, #81C784, #66BB6A); border: none; color: #1B5E20 !important; font-weight: bold; box-shadow: 0 3px 0 #388E3C; }
    .stButton>button:hover { transform: translateY(1px); box-shadow: 0 1px 0 #388E3C; background: #A5D6A7; }
    .stButton>button:active { transform: translateY(3px); box-shadow: none; }

    /* --- Tabs --- */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        color: #33691E !important; 
        background-color: rgba(255, 255, 255, 0.5) !important;
        border-radius: 20px;
        padding: 8px 16px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFF !important;
        color: #EF6C00 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 資料設定 (主題：Nanuwang 移動類) ---
VOCABULARY = [
    {"amis": "remakatay", "zh": "行走(正在...)", "emoji": "🚶‍♂️", "file": "v_remakatay"},
    {"amis": "tayra",     "zh": "去",           "emoji": "👉", "file": "v_tayra"},
    {"amis": "tayni",     "zh": "來",           "emoji": "👈", "file": "v_tayni"},
    {"amis": "natayni tu","zh": "來過了",       "emoji": "🕰️", "file": "v_natayni_tu"},
    {"amis": "yaratu",    "zh": "去了",         "emoji": "🏁", "file": "v_yaratu"},
    {"amis": "liyas",     "zh": "離開",         "emoji": "👋", "file": "v_liyas"},
    {"amis": "remakat",   "zh": "走路",         "emoji": "👣", "file": "v_remakat"},
    {"amis": "tangasa",   "zh": "抵達",         "emoji": "📍", "file": "v_tangasa"},
    {"amis": "pasaira",   "zh": "走向...",       "emoji": "🧭", "file": "v_pasaira"},
    {"amis": "vaher",     "zh": "飛",           "emoji": "🦅", "file": "v_vaher"},
    {"amis": "laliw",     "zh": "逃跑",         "emoji": "💨", "file": "v_laliw"},
    {"amis": "vekac",     "zh": "跑",           "emoji": "🏃", "file": "v_vekac"},
    {"amis": "nukas",     "zh": "折返",         "emoji": "↩️", "file": "v_nukas"},
    {"amis": "milisu'",   "zh": "拜訪",         "emoji": "🏘️", "file": "v_milisu"},
    {"amis": "tahekal",   "zh": "出去",         "emoji": "🚪", "file": "v_tahekal"},
    {"amis": "misarakarakat", "zh": "逛一逛",    "emoji": "🛍️", "file": "v_misarakarakat"},
    {"amis": "midungdung tu lilis", "zh": "沿山走", "emoji": "⛰️", "file": "v_midungdung"},
    {"amis": "lakec",     "zh": "越溪",         "emoji": "🛶", "file": "v_lakec"},
    {"amis": "sacakat",   "zh": "上坡",         "emoji": "📈", "file": "v_sacakat"},
    {"amis": "navuy",     "zh": "爬行",         "emoji": "🦎", "file": "v_navuy"},
]

SENTENCES = [
    {"amis": "Micakat ku mi’adupay i sacakat nu lutuk.", 
     "zh": "獵人在山坡上爬行(攀爬)。", 
     "emoji": "🏹", "file": "s_micakat"},
     
    {"amis": "Milisu’ kami tu i kalingkuay a malinaay.", 
     "zh": "我們拜訪花蓮的親戚。", 
     "emoji": "🤝", "file": "s_milisu"},
     
    {"amis": "Midungdung kami tu lilis nu lutuk a remakat.", 
     "zh": "我們沿著山脈走。", 
     "emoji": "⛰️", "file": "s_midungdung"},
     
    {"amis": "Milakec Ci La’is Akung tu sauwac, tayla i Dawlik a paluma tu kudasing.", 
     "zh": "La’is 阿公越過溪流，去月眉種花生。", 
     "emoji": "🥜", "file": "s_milakec"},
]

# 測驗題庫 (針對移動類設計)
QUIZ_DATA = [
    {"q": "鳥兒在天上 ______ / 飛", "zh": "飛", "ans": "vaher", "opts": ["vaher", "navuy", "lakec"]},
    {"q": "我要 ______ 家裡 / 折返", "zh": "折返", "ans": "nukas", "opts": ["nukas", "tahekal", "liyas"]},
    {"q": "我們去 ______ 親戚 / 拜訪", "zh": "拜訪", "ans": "milisu'", "opts": ["milisu'", "vekac", "remakat"]},
    {"q": "______ / 越過溪流", "zh": "越溪", "ans": "lakec", "opts": ["lakec", "sacakat", "tangasa"]},
    {"q": "tayra vs tayni (去 vs 來)", "zh": "來", "ans": "tayni", "opts": ["tayni", "tayra", "liyas"]},
]

# --- 1.5 語音核心 ---
def play_audio(text, filename_base=None):
    if filename_base:
        extensions = ['m4a', 'mp3', 'wav']
        folders = ['audio', '.'] 
        
        for folder in folders:
            for ext in extensions:
                path = os.path.join(folder, f"{filename_base}.{ext}")
                if os.path.exists(path):
                    mime = 'audio/mp4' if ext == 'm4a' else 'audio/mp3'
                    st.audio(path, format=mime)
                    return 

        # 找不到檔案時顯示提示
        st.markdown(f"<span style='color:#E65100; font-size:12px;'>⚠️ 待錄音: {filename_base}</span>", unsafe_allow_html=True)

    else:
        try:
            speak_text = text.split('/')[0].strip()
            tts = gTTS(text=speak_text, lang='id') 
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            st.audio(fp, format='audio/mp3')
        except:
            st.caption("🔇")

# --- 2. 測驗邏輯 ---
def init_quiz():
    st.session_state.score = 0
    st.session_state.current_q = 0
    
    # Q1: 聽力
    q1_target = random.choice(VOCABULARY)
    others = [v for v in VOCABULARY if v['amis'] != q1_target['amis']]
    q1_options = random.sample(others, 2) + [q1_target]
    random.shuffle(q1_options)
    st.session_state.q1_data = {"target": q1_target, "options": q1_options}

    # Q2: 填空
    q2_data = random.choice(QUIZ_DATA)
    random.shuffle(q2_data['opts'])
    st.session_state.q2_data = q2_data

    # Q3: 句子理解
    q3_target = random.choice(SENTENCES)
    other_sentences = [s['zh'] for s in SENTENCES if s['zh'] != q3_target['zh']]
    if len(other_sentences) < 2:
        q3_options = other_sentences + [q3_target['zh']] + ["去山上打獵"]
        q3_options = q3_options[:3]
    else:
        q3_options = random.sample(other_sentences, 2) + [q3_target['zh']]
    random.shuffle(q3_options)
    st.session_state.q3_data = {"target": q3_target, "options": q3_options}

if 'q1_data' not in st.session_state:
    init_quiz()

# --- 3. 介面呈現 ---
def show_learning_mode():
    st.markdown("<h3 style='color:#558B2F; text-align:center; margin-bottom:20px;'>單字卡 (Vocabulary)</h3>", unsafe_allow_html=True)
    
    # 3 欄排列
    cols = st.columns(3)
    for idx, item in enumerate(VOCABULARY):
        with cols[idx % 3]:
            display_amis = item['amis']
            # 處理長單字換行
            if len(display_amis) > 10:
                display_amis = display_amis.replace(" ", "<br>")
                
            st.markdown(f"""
            <div class="word-card">
                <div class="icon-box">{item['emoji']}</div>
                <div class="amis-word">{display_amis}</div>
                <div class="zh-word">{item['zh']}</div>
            </div>
            """, unsafe_allow_html=True)
            play_audio(item['amis'], filename_base=item['file'])
            st.write("") 

    st.markdown("---")
    st.markdown("<h3 style='color:#558B2F; text-align:center; margin-bottom:20px;'>句子練習 (Sentences)</h3>", unsafe_allow_html=True)
    
    for item in SENTENCES:
        st.markdown(f"""
        <div class="sentence-box">
            <div class="sentence-amis">{item['emoji']} {item['amis']}</div>
            <div class="sentence-zh">{item['zh']}</div>
        </div>
        """, unsafe_allow_html=True)
        play_audio(item['amis'], filename_base=item['file'])

def show_quiz_mode():
    st.markdown("<h3 style='text-align: center; color: #EF6C00;'>👣 移動大挑戰</h3>", unsafe_allow_html=True)
    st.progress((st.session_state.current_q) / 3)
    st.write("")

    if st.session_state.current_q == 0:
        data = st.session_state.q1_data
        target = data['target']
        st.markdown(f"""<div class="word-card" style="border-color:#8BC34A;"><h3>👂 這是什麼動作？</h3></div>""", unsafe_allow_html=True)
        play_audio(target['amis'], filename_base=target['file'])
        st.write("")
        
        cols = st.columns(3)
        for idx, opt in enumerate(data['options']):
            with cols[idx]:
                if st.button(f"{opt['zh']}", key=f"q1_{idx}"):
                    if opt['amis'] == target['amis']:
                        st.balloons()
                        st.success("答對了！")
                        time.sleep(1)
                        st.session_state.score += 1
                        st.session_state.current_q += 1
                        st.rerun()
                    else:
                        st.error("再聽一次")

    elif st.session_state.current_q == 1:
        data = st.session_state.q2_data
        st.markdown(f"""
        <div class="word-card" style="border-color:#8BC34A;">
            <h3>🧩 填空題</h3>
            <h2 style="color:#2E7D32;">{data['q']}</h2>
            <p style="color:#546E7A;">{data['zh']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, opt in enumerate(data['opts']):
            with cols[i]:
                if st.button(opt, key=f"q2_{i}"):
                    if opt in data['ans'] or data['ans'] in opt:
                        st.balloons()
                        st.success("太棒了！")
                        time.sleep(1)
                        st.session_state.score += 1
                        st.session_state.current_q += 1
                        st.rerun()
                    else:
                        st.error("不正確喔")

    elif st.session_state.current_q == 2:
        data = st.session_state.q3_data
        target = data['target']
        st.markdown(f"""
        <div class="word-card" style="border-color:#8BC34A;">
            <h3>🗣️ 這句話是什麼意思？</h3>
            <h3 style="color:#1B5E20;">{target['amis']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        play_audio(target['amis'], filename_base=target['file'])
        
        for opt in data['options']:
            if st.button(opt):
                if opt == target['zh']:
                    st.balloons()
                    st.success("全對！")
                    time.sleep(1)
                    st.session_state.score += 1
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    st.error("不正確")

    else:
        st.markdown(f"""
        <div class="word-card" style="border-color: #FFB74D;">
            <h1 style='color: #EF6C00;'>挑戰成功！</h1>
            <p>得分: {st.session_state.score} / 3</p>
            <div style='font-size: 60px;'>🎉</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("再玩一次"):
            init_quiz()
            st.rerun()

# --- 4. 診斷工具 ---
def show_debug_info():
    st.markdown("---")
    st.markdown("### 📂 檔案診斷中心")
    
    files_audio = []
    if os.path.exists("audio"):
        files_audio = [f for f in os.listdir('audio') if f.endswith('.m4a') or f.endswith('.mp3')]

    if not files_audio:
        st.info("💡 提示：請建立 'audio' 資料夾並放入 .m4a 檔案，即可啟用真人發音功能。")
    else:
        st.success(f"✅ 系統就緒！在 audio 資料夾找到 {len(files_audio)} 個音檔。")

# --- 主程式 ---
def main():
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">Nanuwang</h1>
        <div class="sub-title">移動與動作篇</div>
        <div class="teacher-tag">講師：孫秀蘭 | 教材提供者：孫秀蘭</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📖 學習模式", "🎮 移動挑戰"])
    
    with tab1:
        show_learning_mode()
    with tab2:
        show_quiz_mode()
        
    show_debug_info()

if __name__ == "__main__":
    main()
