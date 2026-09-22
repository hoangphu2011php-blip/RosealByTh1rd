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
        # Đồng bộ lệnh slash với Discord
        await self.tree.sync()
        print("Đã đồng bộ lệnh Slash thành công!")

client = MyClient()

@client.event
async def on_ready():
    print(f'Bot đã đăng nhập thành công với tên: {client.user}')

# --- PHẦN 3: Lệnh /roseal chuyển đổi Roblox username sang link Roseal ---
@client.tree.command(name="roseal", description="Chuyển đổi tên người dùng Roblox thành liên kết Roseal")
@app_commands.describe(username="Nhập tên người dùng Roblox")
async def roseal(interaction: discord.Interaction, username: str):
    await interaction.response.defer(thinking=True) # Đợi vì gọi API có thể mất chút thời gian
    
    try:
        # Gọi Roblox API để lấy ID từ Username
        url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": True}
        response = requests.post(url, json=payload)
        data = response.json()
        
        if data.get("data") and len(data["data"]) > 0:
            user_id = data["data"][0]["id"]
            display_name = data["data"][0]["displayName"]
            
            # Tạo link Roseal dựa trên ID hoặc thông tin người dùng
            roseal_link = f"https://www.roblox.com/users/{user_id}/profile"
            
            embed = discord.Embed(
                title="✨ Roseal Link Converter",
                description=f"**Tài khoản:** {display_name} (@{username})",
                color=discord.Color.green()
            )
            embed.add_field(name="Liên kết Roseal / Profile", value=f"[Nhấn vào đây để mở]({roseal_link})", inline=False)
            
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"Không tìm thấy người dùng Roblox có tên `{username}`!", ephemeral=True)
            
    except Exception as e:
        await interaction.followup.send(f"Đã xảy ra lỗi khi kết nối tới API Roblox: {str(e)}", ephemeral=True)

# --- KHỞI ĐỘNG ---
if __name__ == '__main__':
    keep_alive()
    if TOKEN:
        client.run(TOKEN)
    else:
        print("Lỗi: Không tìm thấy DISCORD_TOKEN trong biến môi trường!")
