import subprocess
import os

def batch_convert_to_small_mov(input_dir, output_dir):
    """
    將帶有透明背景的 WebM 轉換為體積更小的高效壓縮 MOV (H.265 / HEVC)
    """
    if not os.path.exists(input_dir):
        print(f"❌ 找不到指定的輸入資料夾：{input_dir}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 已建立輸出資料夾：{output_dir}")

    webm_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.webm')]

    if not webm_files:
        print(f"⚠️ 在 {input_dir} 中找不到任何 WebM 檔案。")
        return

    print(f"📂 共找到 {len(webm_files)} 個 WebM 檔案，準備開始「瘦身版」批次轉換...\n")
    print("-" * 50)

    success_count = 0
    for filename in webm_files:
        input_path = os.path.join(input_dir, filename)
        output_filename = os.path.splitext(filename)[0] + '.mov'
        output_path = os.path.join(output_dir, output_filename)

        # 瘦身版 FFmpeg 指令參數設定
        command = [
            'ffmpeg',
            '-v', 'warning',
            '-i', input_path,
            '-c:v', 'libx265',           # 影像編碼器：改用 H.265 (HEVC) 高效壓縮
            '-preset', 'medium',         # 壓縮運算速度 (medium 是速度與大小的良好平衡)
            '-crf', '26',                # 畫質與大小控制 (數值 0-51，越小畫質越好但檔案越大。26 是非常好的瘦身平衡點)
            '-pix_fmt', 'yuva420p10le',  # 像素格式：確保包含 Alpha 透明通道
            '-vtag', 'hvc1',             # 標記：讓 Apple 系統與 Adobe 軟體能正確識別這支 HEVC 影片
            '-c:a', 'aac',               # 音訊編碼器：改用有損壓縮 AAC 節省空間
            '-b:a', '128k',              # 音訊位元率限制在 128k
            '-y',
            output_path
        ]

        print(f"⏳ 正在處理並壓縮：{filename} ...", end="", flush=True)
        
        try:
            subprocess.run(command, check=True)
            print(f"\r✅ 瘦身轉換成功：{output_filename}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"\r❌ 轉換失敗：{filename}")
            print(f"   錯誤詳情: {e}")
        except FileNotFoundError:
            print("\r❌ 找不到 FFmpeg！請確認已安裝並加入環境變數中。")
            return

    print("-" * 50)
    print(f"🎉 批次處理完成！共成功轉換 {success_count} / {len(webm_files)} 個檔案。")

# ==========================================
# 執行區塊
# ==========================================
if __name__ == "__main__":
    INPUT_DIRECTORY = "./webm_folder"      
    OUTPUT_DIRECTORY = "./mov_folder_small" # 換一個資料夾名稱以防與之前的搞混

    batch_convert_to_small_mov(INPUT_DIRECTORY, OUTPUT_DIRECTORY)