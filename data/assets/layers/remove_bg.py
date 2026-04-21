import cv2
import numpy as np
import subprocess
import os
import shutil
import glob

def process_video(input_path):
    base_name = os.path.splitext(input_path)[0]
    temp_webm_path = f"{base_name}_temp.webm"
    output_mov_path = f"{base_name}.mov"

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"⚠️ 無法讀取影片: {input_path}，跳過處理。")
        return False

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or np.isnan(fps):
        fps = 30.0

    temp_dir = f"temp_frames_{base_name}"
    os.makedirs(temp_dir, exist_ok=True)

    print(f"\n🎬 開始處理綠幕影片: {input_path}")
    frame_count = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # 1. 將 BGR 色彩轉換為 HSV (更能精準抓取顏色)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 2. 定義「綠幕」的顏色範圍 (H:色相, S:飽和度, V:亮度)
        # 如果你的綠幕比較暗或比較亮，可以微調這兩行數字
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])

        # 3. 建立綠色遮罩 (綠色區域會變成白色 255，其他區域變成黑色 0)
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # 4. 反轉遮罩 (我們要保留的「不是綠色」的地方，主體變 255，背景變 0)
        mask_inv = cv2.bitwise_not(mask)

        # 5. 稍微模糊遮罩邊緣，減少去背後的鋸齒感 (可選)
        mask_inv = cv2.GaussianBlur(mask_inv, (3, 3), 0)

        # 6. 將原圖轉為 BGRA (加上透明 Alpha 通道)
        frame_bgra = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

        # 7. 將透明通道直接替換成我們計算好的反轉遮罩
        frame_bgra[:, :, 3] = mask_inv

        # 儲存帶有透明通道的 PNG
        frame_filename = os.path.join(temp_dir, f"frame_{frame_count:05d}.png")
        cv2.imwrite(frame_filename, frame_bgra)
        
        frame_count += 1
        if frame_count % 60 == 0:
            print(f"  - 已處理 {frame_count} 幀...")

    cap.release()
    print(f"✅ {input_path} 綠幕消除完成！準備封裝...")

    # 使用 FFmpeg 輸出透明的 WebM 和 MOV
    webm_command = [
        'ffmpeg', '-y', '-framerate', str(fps), '-i', f'{temp_dir}/frame_%05d.png',
        '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-auto-alt-ref', '0', temp_webm_path
    ]
    
    mov_command = [
        'ffmpeg', '-y', '-framerate', str(fps), '-i', f'{temp_dir}/frame_%05d.png',
        '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le', output_mov_path
    ]

    print("  🎥 封裝透明 .webm 中...")
    subprocess.run(webm_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    
    print("  🎥 封裝透明 .mov 中...")
    subprocess.run(mov_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    print("  🧹 清理暫存圖片...")
    shutil.rmtree(temp_dir)
    
    # 覆蓋原檔案
    print(f"  🔄 正在覆寫原始檔案 {input_path} ...")
    try:
        os.remove(input_path)
        os.rename(temp_webm_path, input_path)
    except Exception as e:
        print(f"❌ 覆寫檔案時發生錯誤: {e}")
        return False

    print(f"🎉 {input_path} 處理完畢！(已覆蓋原檔，並產生 .mov)")
    return True

if __name__ == "__main__":
    webm_files = glob.glob("*.webm")
    
    if not webm_files:
        print("找不到任何 .webm 檔案！請確認影片和這個 Python 檔放在同一個資料夾。")
    else:
        print(f"🔍 找到 {len(webm_files)} 個 .webm 檔案，準備開始綠幕批次處理...")
        for file in webm_files:
            if not file.endswith("_temp.webm"):
                process_video(file)
        
        print("\n🌟 所有影片批次處理完成！")