import streamlit as st
import os
import random
import time
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
total_people_count = len(people_names)

# --- 1. 初始化狀態 ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'correct_count' not in st.session_state: st.session_state.correct_count = 0  # 名字全對的計數
if 'finished_one_round' not in st.session_state: st.session_state.finished_one_round = False

# 待考驗清單
if 'remaining_people' not in st.session_state:
    st.session_state.remaining_people = list(people_names)
    random.shuffle(st.session_state.remaining_people)

# 當前要猜的人
if 'current_name' not in st.session_state:
    if st.session_state.remaining_people:
        st.session_state.current_name = st.session_state.remaining_people.pop()
    else:
        st.session_state.current_name = None

# --- 2. 邏輯函數 ---
def is_same_pronunciation(str1, str2):
    if not str1 or not str2: return False
    p1 = [item[0] for item in pinyin(str1, style=Style.NORMAL)]
    p2 = [item[0] for item in pinyin(str2, style=Style.NORMAL)]
    return p1 == p2

def next_question():
    if st.session_state.remaining_people:
        st.session_state.current_name = st.session_state.remaining_people.pop()
    else:
        st.session_state.current_name = None
        st.session_state.finished_one_round = True  # 標記整輪結束
        
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

# 判斷是否要顯示結算畫面
if st.session_state.finished_one_round:
    st.balloons()
    st.header("🎊 挑戰結束！結算時間 🎊")
    st.divider()
    
    # 你的結算需求
    st.subheader(f"📚 題庫共有： {total_people_count} 人")
    st.subheader(f"✅ 你總共認出（名字全對）： :green[{st.session_state.correct_count}] 人")
    st.write(f"💰 最終得分： {st.session_state.score}")
    
    if st.session_state.correct_count == total_people_count:
        st.success("🎉 太神啦！你是認人的神吧？全部都對！比賽當天就靠你了！")
    
    if st.button("再玩一輪"):
        # 重置所有狀態
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

elif not st.session_state.current_name:
    st.error("❌ 找不到照片！請檢查 'people' 資料夾。")

else:
    # 遊戲進行中的介面
    st.write(f"### 目前分數： :orange[{st.session_state.score}]")
    st.write(f"📊 進度： 第 {total_people_count - len(st.session_state.remaining_people)} / {total_people_count} 人")
    
    current_name = st.session_state.current_name
    img_path = os.path.join(IMAGE_FOLDER, people_dict[current_name])
    st.image(Image.open(img_path), use_container_width=True)

    with st.form(key='quiz_form', clear_on_submit=True):
        user_input = st.text_input("猜猜我是誰？")
        submit_clicked = st.form_submit_button("提交答案")

    if submit_clicked:
        user_guess = user_input.strip()
        
        # 1. 字完全對
        if user_guess == current_name:
            st.success(f"✅ BINGO！他是 **{current_name}**")
            st.session_state.correct_count += 1  # 增加全對計數
            st.session_state.score += 10
            time.sleep(1.2)
            next_question()
            st.rerun()
        
        # 2. 音對了
        elif is_same_pronunciation(user_guess, current_name):
            st.info(f"🎊 勉強算你對啦，他是 **{current_name}** (雖然你字打錯了嘖嘖)")
            st.session_state.score += 5 # 音對給 5 分
            time.sleep(2.0)
            next_question()
            st.rerun()
            
        # 3. 錯得離譜
        else:
            st.error(f"❌ 猜錯囉！他是 **{current_name}**")
            next_question()
            st.rerun()