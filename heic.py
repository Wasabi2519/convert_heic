import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import subprocess
import os
from datetime import datetime
import requests
import shutil

def create_output_folder(input_file_path):
    # 変換した日付からフォルダー名を作成
    date_today = datetime.today().strftime('%m%d')
    output_folder_name = f"png_{date_today}"

    # フォルダーを作成
    output_folder_path = os.path.join(os.path.dirname(input_file_path), output_folder_name)
    os.makedirs(output_folder_path, exist_ok=True)

    return output_folder_path

def download_heif_convert():
    # ダウンロード先のURL
    url = "https://github.com/strukturag/libheif/releases/download/v1.15.0/heif-convert"

    # ダウンロードするファイルパス
    file_path = "heif-convert"

    # ダウンロード
    response = requests.get(url)
    with open(file_path, "wb") as f:
        f.write(response.content)

    # 実行権限の付与
    os.chmod(file_path, 0o755)

    return os.path.abspath(file_path)

def add_to_path(file_path):
    # カレントディレクトリをPATHに追加
    os.environ["PATH"] += os.pathsep + os.path.dirname(file_path)

def on_input_file_select_button_click():
    input_file_paths = filedialog.askopenfilenames(
        title="HEIC画像を選択",
        filetypes=[("HEIC画像", "*.heic")])
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, ", ".join(input_file_paths))

def on_convert_button_click():
    input_file_paths = input_file_entry.get().split(", ")
    successful_conversions = 0
    total_conversions = len(input_file_paths)
    download_success = True

    # heif-convertのパスを取得
    heif_convert_path = shutil.which("heif-convert")

    # パスが見つからない場合はダウンロードしてパスを通す
    if not heif_convert_path:
        try:
            heif_convert_path = download_heif_convert()
            add_to_path(heif_convert_path)
        except Exception as e:
            messagebox.showerror("エラー", f"heif-convertのダウンロードに失敗しました。\n{e}")
            download_success = False

    if not download_success:
        return

    for input_file_path in input_file_paths:
        if not input_file_path.endswith(".heic"):
            messagebox.showerror("エラー", "HEICファイルを選択してください。")
            return

        try:
            # HEICファイルを一時的にJPEGに変換
            temp_jpeg_path = os.path.splitext(input_file_path)[0] + ".jpg"
            subprocess.run(["heif-convert", input_file_path, temp_jpeg_path])

            # JPEGをPIL形式に変換
            with Image.open(temp_jpeg_path) as img:
                output_folder_path = create_output_folder(input_file_path)
                output_file_path = os.path.join(output_folder_path, os.path.basename(input_file_path).replace(".heic", ".png"))
                img.save(output_file_path, format="png")

            # 一時的なJPEGファイルを削除
            os.remove(temp_jpeg_path)

            successful_conversions += 1
        except Exception as e:
            print(f"変換中にエラーが発生しました: {e}")

    # すべての変換が成功した場合にメッセージを表示
    if successful_conversions == total_conversions:
        messagebox.showinfo("完了", "すべての画像の変換が完了しました。")

root = tk.Tk()
root.title("HEIC to PNG変換")

input_file_label = tk.Label(text="HEIC画像ファイル")
input_file_label.pack()

input_file_entry = tk.Entry()
input_file_entry.pack()

input_file_select_button = tk.Button(
    text="HEIC画像を選択",
    command=on_input_file_select_button_click)
input_file_select_button.pack()

convert_button = tk.Button(
    text="変換",
    command=on_convert_button_click)
convert_button.pack()

root.mainloop()
