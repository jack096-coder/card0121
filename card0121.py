import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import json
import io
import os

# --- 字體處理函數 ---
def get_chinese_font(size):
    # 定義可能的字體路徑 (支援 Linux/Cloud 環境)
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", # Streamlit Cloud 常用
        "C:/Windows/Fonts/msjh.ttc",                    # Windows 預設
        "/System/Library/Fonts/STHeiti Light.ttc"       # macOS 預設
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# --- 繪圖核心函數 ---
def draw_card_from_data(data):
    width, height = 1240, 1754
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    font_title = get_chinese_font(32)
    font_sm = get_chinese_font(20)

    # 1. 繪製定位點
    for anchor in data.get('anchors', []):
        p1, p3 = anchor[0], anchor[2]
        draw.rectangle([p1[0], p1[1], p3[0], p3[1]], fill='black')

    # 2. 繪製圓圈
    for bubble in data.get('bubbles', []):
        cx, cy = bubble['center']
        r = bubble['radius']
        label = str(bubble['label'])
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline='black', width=1)
        bbox = draw.textbbox((0, 0), label, font=font_sm)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text((cx - tw/2, cy - th/2 - 2), label, fill='black', font=font_sm)

    # 3. 繪製混合題區
    ma = data.get('mixed_area')
    if ma:
        draw.rectangle([ma[0][0], ma[0][1], ma[2][0], ma[2][1]], outline='black', width=2)
        draw.line([ma[0][0], ma[0][1]+60, ma[1][0], ma[1][1]+60], fill='black', width=2)
        draw.text((ma[0][0]+10, ma[0][1]+20), "混合題（務必依序標示題號寫答案）", fill='black', font=font_sm)

    # 4. 繪製表頭
    draw.text((60, 70), "國立臺南大學附屬高級中學試卷答案卡", fill='black', font=font_title)
    draw.rectangle([60, 120, 550, 210], outline='black', width=2)
    draw.line([220, 120, 220, 210], fill='black', width=2)
    draw.line([400, 120, 400, 210], fill='black', width=2)
    draw.text((70, 150), "年   班   號 姓名：", fill='black', font=font_sm)
    draw.text((410, 150), "科目：", fill='black', font=font_sm)
    
    return img

# --- Streamlit 網頁介面 ---
st.title("答案卡繪製與預覽工具")

# 1. 檔案上傳
uploaded_file = st.file_uploader("請選擇一個 .json 座標檔", type=["json"])

if uploaded_file is not None:
    # 讀取 JSON 資料
    data = json.load(uploaded_file)
    
    # 繪製圖片
    card_img = draw_card_from_data(data)
    
    # 2. 顯示在螢幕上
    st.subheader("預覽圖")
    st.image(card_img, caption="生成的答案卡 (已自動縮放以適應螢幕)", use_container_width=True)
    
    # 3. 儲存為圖檔功能 (提供下載按鈕)
    buf = io.BytesIO()
    card_img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="點此存為圖檔 (PNG)",
        data=byte_im,
        file_name="answer_card_drawn.png",
        mime="image/png"
    )
