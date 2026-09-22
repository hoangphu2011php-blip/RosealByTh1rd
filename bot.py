import os
import threading
import discord
from discord import app_commands
import requests
from flask import Flask

# --- PHẦN 1: Tạo Web Server giả lập cho Render (Web Service yêu cầu) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    # Render tự cấp biến môi trường PORT, nếu không có thì mặc định dùng port 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.start()

# --- PHẦN 2: Code Bot Discord của bạn ---
TOKEN = os.getenv("DISCORD_TOKEN")

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Đã đồng bộ lệnh Slash thành công!")

client = MyClient()

@client.event
async def on_ready():
    print(f'Bot đã đăng nhập thành công với tên: {client.user}')

# (Phần lệnh /roseal và logic cũ của bạn giữ nguyên ở đây...)

# --- KHỞI ĐỘNG ---
if __name__ == '__main__':
    # Chạy web server ngầm trước
    keep_alive()
    # Chạy bot Discord
    if TOKEN:
        client.run(TOKEN)
    else:
        print("Lỗi: Không tìm thấy DISCORD_TOKEN trong biến môi trường!")