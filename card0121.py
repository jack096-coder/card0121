import json
from PIL import Image, ImageDraw, ImageFont

def draw_answer_card(json_file, output_file="reconstructed_card.png"):
    # 1. 讀取 JSON 資料
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. 建立畫布 (模擬 A4 尺寸，根據座標範圍設定)
    width, height = 1240, 1754
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    # 3. 字型設定 (嘗試載入字型以顯示圓圈內的文字)
    try:
        # Windows 常用字型路徑，若在 Linux 可改為 DejaVuSans.ttf
        font = ImageFont.truetype("arial.ttf", 20)
        font_title = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()
        font_title = ImageFont.load_default()

    # 4. 繪製角落定位點 (Anchors)
    for anchor in data['anchors']:
        # anchor 為四個角的座標列表: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
        # 取左上角與右下角來畫矩形
        top_left = anchor[0]
        bottom_right = anchor[2]
        draw.rectangle([top_left[0], top_left[1], bottom_right[0], bottom_right[1]], fill='black')

    # 5. 繪製劃記圓圈 (Bubbles)
    for bubble in data['bubbles']:
        cx, cy = bubble['center']
        r = bubble['radius']
        label = bubble['label']

        # 畫圓圈
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline='black', width=1)
        
        # 畫圓圈內的文字 (置中處理)
        # 計算文字寬高以確保置中
        left, top, right, bottom = draw.textbbox((0, 0), label, font=font)
        text_w = right - left
        text_h = bottom - top
        draw.text((cx - text_w/2, cy - text_h/2 - 2), label, fill='black', font=font)

    # 6. 繪製混合題/非選區 (Mixed Area)
    if data['mixed_area']:
        ma = data['mixed_area']
        # ma 為 [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
        p1, p3 = ma[0], ma[2]
        draw.rectangle([p1[0], p1[1], p3[0], p3[1]], outline='black', width=2)
        
        # 繪製非選區頂部的標題橫線 (固定高度偏移，約 60px)
        header_line_y = p1[1] + 60
        draw.line([p1[0], header_line_y, p3[0], header_line_y], fill='black', width=2)

    # 7. 額外補上表頭文字 (因 JSON 僅含座標，手動加入標題以求美觀)
    draw.text((60, 80), "國立臺南大學附屬高級中學試卷答案卡", fill='black', font=font_title)
    draw.rectangle([60, 120, 550, 210], outline='black', width=2) # 個人資訊框

    # 8. 儲存結果
    img.save(output_file)
    print(f"繪製完成！檔案已儲存為: {output_file}")

if __name__ == "__main__":
    draw_answer_card('coordinates.json')
