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
        await self.tree.sync()
        print("Đã đồng bộ lệnh Slash thành công!")

client = MyClient()

@client.event
async def on_ready():
    print(f'Bot đã đăng nhập thành công với tên: {client.user}')

# --- PHẦN 3: Lệnh /roseal ---
@client.tree.command(name="roseal", description="Tạo link Roseal join game của người chơi Roblox")
@app_commands.describe(username="Nhập tên người dùng Roblox")
async def roseal(interaction: discord.Interaction, username: str):
    await interaction.response.defer(thinking=True)
    
    try:
        user_url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": True}
        res = requests.post(user_url, json=payload).json()
        
        if not res.get("data") or len(res["data"]) == 0:
            await interaction.followup.send(f"Không tìm thấy người dùng Roblox có tên `{username}`!", ephemeral=True)
            return
            
        user_id = res["data"][0]["id"]
        display_name = res["data"][0]["displayName"]
        
        presence_url = "https://presence.roblox.com/v1/presence/users"
        presence_res = requests.post(presence_url, json={"userIds": [user_id]}).json()
        
        if not presence_res.get("userPresences") or len(presence_res["userPresences"]) == 0:
            await interaction.followup.send(f"Không thể kiểm tra trạng thái của người dùng `{username}`.", ephemeral=True)
            return
            
        presence_data = presence_res["userPresences"][0]
        if presence_data.get("userPresenceType") != 2:
            await interaction.followup.send(f"Người chơi **{display_name}** (`{username}`) hiện không trong game hoặc đang ẩn trạng thái hoạt động!", ephemeral=True)
            return
            
        place_id = presence_data.get("rootPlaceId")
        game_instance_id = presence_data.get("gameId")
        
        if not place_id or not game_instance_id:
            await interaction.followup.send(f"Người chơi **{display_name}** đang chơi game nhưng không lấy được thông tin server cụ thể.", ephemeral=True)
            return
            
        roseal_link = f"https://www.roseal.live/join?placeId={place_id}&gameInstanceId={game_instance_id}"
        
        message = (
            f"**Link Roseal của {display_name} (@{username}):**\n"
            f"🔗 [Bấm vào đây để join game nhanh]({roseal_link})\n\n"
            f"Hoặc copy link bên dưới:\n"
            f"```\n{roseal_link}\n```"
        )
        await interaction.followup.send(message)
            
    except Exception as e:
        await interaction.followup.send(f"Đã xảy ra lỗi khi xử lý: {str(e)}", ephemeral=True)

# --- PHẦN 4: Lệnh /profilelink ---
@client.tree.command(name="profilelink", description="Tra cứu link profile Roblox chính thức qua API")
@app_commands.describe(username="Nhập tên người dùng Roblox")
async def profilelink(interaction: discord.Interaction, username: str):
    await interaction.response.defer(thinking=True)
    try:
        url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": True}
        response = requests.post(url, json=payload).json()
        
        if response.get("data") and len(response["data"]) > 0:
            user_id = response["data"][0]["id"]
            display_name = response["data"][0]["displayName"]
            profile_link = f"https://www.roblox.com/users/{user_id}/profile"
            
            message = (
                f"**Profile của {display_name} (@{username}):**\n"
                f"🔗 [Bấm vào đây để mở profile]({profile_link})\n\n"
                f"```\n{profile_link}\n```"
            )
            await interaction.followup.send(message)
        else:
            await interaction.followup.send(f"Không tìm thấy người dùng Roblox `{username}`!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Lỗi: {str(e)}", ephemeral=True)

# --- PHẦN 5: Lệnh /callraid (Đã bỏ ping thừa ở đầu) ---
@client.tree.command(name="callraid", description="Tạo thông báo điều phối chiến dịch Raid")
@app_commands.describe(
    username="Tên người dùng Roblox mục tiêu",
    region="Khu vực server (VD: Singapore)",
    targets="Mục tiêu raid (VD: MHL, ALL, FTW)",
    ping="Chọn role cần ping thông báo"
)
async def callraid(interaction: discord.Interaction, username: str, region: str, targets: str, ping: discord.Role):
    await interaction.response.defer(thinking=True)
    
    try:
        user_url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": True}
        res = requests.post(user_url, json=payload).json()
        
        if not res.get("data") or len(res["data"]) == 0:
            await interaction.followup.send(f"Không tìm thấy người dùng Roblox có tên `{username}`!", ephemeral=True)
            return
            
        user_id = res["data"][0]["id"]
        display_name = res["data"][0]["displayName"]
        profile_link = f"https://www.roblox.com/users/{user_id}/profile"
        
        presence_url = "https://presence.roblox.com/v1/presence/users"
        presence_res = requests.post(presence_url, json={"userIds": [user_id]}).json()
        
        roseal_link = "https://www.roseal.live"
        if presence_res.get("userPresences") and len(presence_res["userPresences"]) > 0:
            p_data = presence_res["userPresences"][0]
            if p_data.get("userPresenceType") == 2:
                place_id = p_data.get("rootPlaceId")
                game_instance_id = p_data.get("gameId")
                if place_id and game_instance_id:
                    roseal_link = f"https://www.roseal.live/join?placeId={place_id}&gameInstanceId={game_instance_id}"

        # Bỏ dòng ping ở trên, chỉ giữ lại phần PINGS ở dưới
        raid_message = (
            f"⚔️ **SYSTEM // RAID DEPLOYMENT** ⚔️\n\n"
            f"🔹 **ACCOUNT:** [{username}] ({display_name})\n"
            f"🔗 **PROFILE:** [Click here to view]({profile_link})\n"
            f"🔗 **ROSEAL LINK:** [Click here to view]({roseal_link})\n"
            f"🌐 **REGION:** [{region}]\n"
            f"🎯 **TARGETS:** [{targets}]\n"
            f"🔔 **PINGS:** {ping.mention}"
        )
        
        await interaction.followup.send(raid_message)
        
    except Exception as e:
        await interaction.followup.send(f"Đã xảy ra lỗi khi tạo raid call: {str(e)}", ephemeral=True)

# --- KHỞI ĐỘNG ---
if __name__ == '__main__':
    keep_alive()
    if TOKEN:
        client.run(TOKEN)
    else:
        print("Lỗi: Không tìm thấy DISCORD_TOKEN trong biến môi trường!")
