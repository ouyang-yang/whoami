import streamlit as st
import os
import random
from PIL import Image
from pypinyin import pinyin, Style
from difflib import SequenceMatcher

# 設定網頁標題
st.set_page_config(page_title="認人大賽", page_icon="🏆")

# 設定資料夾路徑
IMAGE_FOLDER = 'people'

# 1. 取得所有人名與對應的檔案完整路徑
@st.cache_data
def get_people_data():
    data = {}
    if os.path.exists(IMAGE_FOLDER):
        for f in os.listdir(IMAGE_FOLDER):
            # 支援多種副檔名，且不論大小寫 (.jpg, .JPG, .png...)
            if f.lower().endswith(('.jpg', '.png', '.jpeg')):
                name = os.path.splitext(f)[0]
                data[name] = f
    return data

people_dict = get_people_data()
people_names = list(people_dict.keys())

# 2. 初始化遊戲狀態
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_name' not in st.session_state:
    if people_names:
        st.session_state.current_name = random.choice(people_names)
    else:
        st.session_state.current_name = None

# 3. 定義換題函數
def next_question():
    if people_names:
        # 避免抽到跟上一題一樣的人
        new_name = random.choice(people_names)
        st.session_state.current_name = new_name
        
# 定義判斷讀音是否相同的函數
def is_same_pronunciation(str1, str2):
    if not str1 or not str2:
        return False
    # 轉為拼音清單（不含聲調），例如 "小明" -> ['xiao', 'ming']
    p1 = [item[0] for item in pinyin(str1, style=Style.NORMAL)]
    p2 = [item[0] for item in pinyin(str2, style=Style.NORMAL)]
    return p1 == p2
        
# --- 嘲諷清單 ---
insults = [
    "你怎麼可以打錯名字呢嘖嘖...",
    "雖然音是對的，但字錯了啦！",
    "字打錯了喔，你的朋友在哭泣...",
    "把學長的名字打錯值得一張策進表喔"
]

# --- 好棒棒清單 ---
kudos = [
    "✅ 太強了！竟然連這都認得出來！",
    "✅ 沒錯！就是 **{}**。",
    "✅ 認人比賽當天也會答對的吧！",
    "✅ 叮咚叮咚！答對！",
    "✅ 這麼模糊你也認得出來？你是人臉辨識機吧！",
    "✅ 葛萊芬多加10分！"
]

# 4. UI 介面
st.title("🏆 認人大賽")
st.write(f"### 目前分數： :orange[{st.session_state.score}]")

if not st.session_state.current_name:
    st.error("❌ 找不到照片！請確認 'people' 資料夾內有 .jpg 或 .png 檔案。")
else:
    # 顯示照片
    current_name = st.session_state.current_name
    file_name = people_dict[current_name]
    img_path = os.path.join(IMAGE_FOLDER, file_name)
    
    try:
        img = Image.open(img_path)
        st.image(img, caption="猜猜我是誰？", use_container_width=True)
    except Exception as e:
        st.error(f"無法讀取圖片: {file_name}")

    # 輸入介面
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_input("輸入名字：", placeholder="打完後按 Enter 或提交按鈕")
        submit_clicked = st.form_submit_button("提交答案")

if submit_clicked:
    user_guess = user_input.strip()
    correct_name = st.session_state.current_name
    
    # 1. 檢查字是否完全正確
    if user_guess == correct_name:
        st.success(f"✅ 沒錯！他就是 **{correct_name}**")
        if random.random() < 0.2: st.balloons()
        st.session_state.score += 10
        time.sleep(1.2)
        next_question()
        st.rerun()

    # 2. 檢查音是否正確 (文字錯但音對)
    elif is_same_pronunciation(user_guess, correct_name):
        st.success(f"勉強算你對啦，他是 **{correct_name}** (雖然你字打錯了嘖嘖)")
        # 音對了給比較少分，或是照樣給分也可以
        st.session_state.score += 5

        next_question()
        st.rerun()

    # 3. 答錯
    else:
        st.error(f"❌ 猜錯囉！他是 **{correct_name}**")
        next_question()
        st.rerun()
        