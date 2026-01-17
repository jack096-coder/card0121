import json
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import platform

class AnswerCardGUI:
    def __init__(self, json_path):
        self.json_path = json_path
        self.width = 1240
        self.height = 1754
        self.img = None
        
        # 初始化 Tkinter 視窗
        self.root = tk.Tk()
        self.root.title("答案卡繪製預覽器")
        
        # 載入資料並繪製
        self.load_and_draw()
        
        # 介面佈局
        self.setup_ui()

    def get_chinese_font(self, size):
        """尋找系統中的中文字型，解決方塊字問題"""
        system = platform.system()
        font_paths = []
        if system == "Windows":
            font_paths = [
                "C:/Windows/Fonts/msjh.ttc",   # 微軟正黑體
                "C:/Windows/Fonts/msyh.ttc",   # 微软雅黑
                "C:/Windows/Fonts/mingliu.ttc" # 細明體
            ]
        elif system == "Darwin": # macOS
            font_paths = ["/Library/Fonts/Arial Unicode.ttf", "/System/Library/Fonts/STHeiti Light.ttc"]
        else: # Linux
            font_paths = ["/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]

        for path in font_paths:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    def load_and_draw(self):
        """讀取 JSON 並使用 Pillow 繪圖"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("錯誤", f"無法讀取 JSON 檔案: {e}")
            return

        self.img = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(self.img)
        
        # 設定字型
        font_title = self.get_chinese_font(32)
        font_sm = self.get_chinese_font(20)

        # 1. 繪製定位點 (Anchors)
        for anchor in data.get('anchors', []):
            p1, p3 = anchor[0], anchor[2]
            draw.rectangle([p1[0], p1[1], p3[0], p3[1]], fill='black')

        # 2. 繪製圓圈 (Bubbles)
        for bubble in data.get('bubbles', []):
            cx, cy = bubble['center']
            r = bubble['radius']
            label = str(bubble['label'])
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline='black', width=1)
            # 文字置中計算
            bbox = draw.textbbox((0, 0), label, font=font_sm)
            tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text((cx - tw/2, cy - th/2 - 2), label, fill='black', font=font_sm)

        # 3. 繪製混合題區 (Mixed Area)
        ma = data.get('mixed_area')
        if ma:
            draw.rectangle([ma[0][0], ma[0][1], ma[2][0], ma[2][1]], outline='black', width=2)
            draw.line([ma[0][0], ma[0][1]+60, ma[1][0], ma[1][1]+60], fill='black', width=2)
            draw.text((ma[0][0]+10, ma[0][1]+20), "混合題（務必依序標示題號寫答案）", fill='black', font=font_sm)

        # 4. 繪製表頭 (根據您上傳的圖片樣式)
        draw.text((60, 70), "國立臺南大學附屬高級中學試卷答案卡", fill='black', font=font_title)
        draw.rectangle([60, 120, 550, 210], outline='black', width=2)
        draw.line([220, 120, 220, 210], fill='black', width=2)
        draw.line([400, 120, 400, 210], fill='black', width=2)
        draw.text((70, 150), "年   班   號 姓名：", fill='black', font=font_sm)
        draw.text((410, 150), "科目：", fill='black', font=font_sm)

    def setup_ui(self):
        """建立 GUI 介面"""
        # 縮放圖片以適應螢幕顯示
        display_scale = 0.4
        display_size = (int(self.width * display_scale), int(self.height * display_scale))
        preview_img = self.img.resize(display_size, Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(preview_img)

        # 顯示畫布
        canvas = tk.Canvas(self.root, width=display_size[0], height=display_size[1])
        canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        canvas.pack(pady=10, padx=10)

        # 按鈕區
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, pady=5)
        
        save_btn = tk.Button(btn_frame, text="儲存為圖檔", command=self.save_image, bg="#4CAF50", fg="white", padx=20)
        save_btn.pack(side=tk.BOTTOM, pady=10)

    def save_image(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
            initialfile="answer_card_output.png"
        )
        if file_path:
            self.img.save(file_path)
            messagebox.showinfo("成功", f"檔案已儲存至：\n{file_path}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # 這裡請確保 coordinates.json 檔案與此程式在同一資料夾
    json_filename = 'coordinates.json'
    
    if os.path.exists(json_filename):
        app = AnswerCardGUI(json_filename)
        app.run()
    else:
        print(f"錯誤：找不到 {json_filename} 檔案！")
