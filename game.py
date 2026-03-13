import streamlit as st
import os
import random
from PIL import Image

# 設定網頁標題
st.set_page_config(page_title="認人大賽", page_icon="🏆")

# 1. 初始化遊戲狀態 (只在第一次執行時執行)
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_person' not in st.session_state:
    st.session_state.current_person = None
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

IMAGE_FOLDER = '/Users/ouyangxuan/Documents/北宜路/code/people'

# 取得所有人名（從檔名）
@st.cache_data # 快取名單，避免每次重新讀取資料夾
def get_people_list():
    if not os.path.exists(IMAGE_FOLDER):
        return []
    return [f.split('.')[0] for f in os.listdir(IMAGE_FOLDER) if f.endswith(('.jpg', '.png', '.jpeg'))]

people = get_people_list()

# 2. 遊戲邏輯函數
def next_question():
    if people:
        st.session_state.current_person = random.choice(people)
    else:
        st.error("找不到照片，請檢查 'people' 資料夾！")

# 如果還沒有題目，選一個
if st.session_state.current_person is None:
    next_question()

# 3. UI 介面設計
st.title("🏆 認人大賽")
st.write(f"### 目前分數： **{st.session_state.score}**")

# 顯示照片
if st.session_state.current_person:
    # 尋找正確副檔名
    img_path = ""
    for ext in ['.jpg', '.png', '.jpeg']:
        if os.path.exists(os.path.join(IMAGE_FOLDER, f"{st.session_state.current_person}{ext}")):
            img_path = os.path.join(IMAGE_FOLDER, f"{st.session_state.current_person}{ext}")
            break
    
    if img_path:
        img = Image.open(img_path)
        st.image(img, caption="猜猜我是誰？", width=400)

# 使用 Form 讓輸入更流暢
with st.form(key='answer_form', clear_on_submit=True):
    user_input = st.text_input("輸入名字後按 Enter 或點擊提交：")
    submit_button = st.form_submit_button(label='提交答案')

if submit_button:
    if user_input.strip().lower() == st.session_state.current_person.lower():
        st.success(f"✅ 答對了！是 {st.session_state.current_person}")
        st.session_state.score += 10
        next_question()
        st.rerun() # 立即重新整理顯示下一題
    else:
        st.error(f"❌ 蛤怎麼會！這明明就是 {st.session_state.current_person}")
        # 如果想猜錯也下一題：
        next_question()
        st.rerun()

# 重新開始按鈕
if st.button("重置分數"):
    st.session_state.score = 0
    next_question()
    st.rerun()