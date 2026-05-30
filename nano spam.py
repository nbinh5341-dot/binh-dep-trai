# spam_gmail_aio.py - Spam chat Gmail qua a-shell
# Chi dung thu vien chuan, khong can cai them
# CHAY: python3 spam_gmail_aio.py

import urllib.request
import urllib.parse
import json
import time
import random
import os
from datetime import datetime

class SpamGmail:
    def __init__(self):
        self.sent = 0
        self.log_file = "spam_log.txt"
        
    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {msg}"
        print(line)
        with open(self.log_file, "a") as f:
            f.write(line + "\n")
            
    def send_via_webhook(self, webhook_url, message):
        """Gui qua Google Chat Webhook"""
        try:
            payload = json.dumps({"text": message}).encode()
            req = urllib.request.Request(webhook_url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except:
            return False
    
    def send_via_email_api(self, to_email, subject, body):
        """Gui email qua API (mo phong - can SMTP that)"""
        # Ghi chu: De gui email that can SMTP, nhung a-shell khong ho tro smtplib tot
        # Day la mo phong luu vao file
        self.log(f"[MO PHONG] Gui den {to_email}: {subject}")
        with open("emails_sent.txt", "a") as f:
            f.write(f"To: {to_email}\nSubject: {subject}\nBody: {body}\n---\n")
        return True
    
    def generate_chat_content(self, custom_text=""):
        """Sinh noi dung chat spam"""
        templates = [
            "Xin chao, ban co the ket ban khong?",
            "Chao ban, hom nay the nao?",
            "Hello, co ranh khong?",
            "Chao, toi can hoi mot chut!",
            "Hi, ban dang lam gi day?",
            "Chao buoi sang, chuc mot ngay tot lanh!",
            "Hey, co gi hot khong?",
            "Chao, toi la nguoi moi!",
            "Halo, ban oi!",
            "Chao, cho toi lam quen nhe!"
        ]
        if custom_text:
            return custom_text
        return random.choice(templates)
    
    def spam_webhook(self, webhook_url, content, count=50, delay=1):
        """Spam chat qua webhook"""
        self.log(f"[+] BAT DAU SPAM WEBHOOK: {count} lan")
        
        for i in range(count):
            msg = f"{content} [{i+1}]" if content else self.generate_chat_content()
            if self.send_via_webhook(webhook_url, msg):
                self.sent += 1
                self.log(f"[✓] {i+1}/{count} - Da gui: {msg[:30]}...")
            else:
                self.log(f"[✗] {i+1}/{count} - That bai")
            time.sleep(delay)
            
        self.log(f"[+] KET THUC! Thanh cong: {self.sent}/{count}")
        
    def show_menu(self):
        while True:
            print("\n" + "="*50)
            print("   SPAM CHAT GMAIL - a-shell")
            print("="*50)
            print("  [1] Spam qua Webhook (Google Chat)")
            print("  [2] Spam qua Email (luu file - mo phong)")
            print("  [3] Tuy chinh noi dung spam")
            print("  [4] Xem log")
            print("  [0] Thoat")
            print("="*50)
            
            choice = input("\n[>] Chon: ").strip()
            
            if choice == "1":
                webhook = input("  Nhap Webhook URL: ").strip()
                if not webhook:
                    print("[!] URL khong duoc de trong")
                    continue
                    
                try:
                    count = int(input("  So lan spam (toi da 100): ") or "50")
                    count = min(count, 100)
                    delay = float(input("  Delay giay (0.1-5): ") or "0.5")
                    delay = max(0.1, min(delay, 5))
                except:
                    count, delay = 50, 0.5
                    
                content = input("  Noi dung spam (bo trong = random): ").strip()
                self.spam_webhook(webhook, content, count, delay)
                input("\n[*] Enter de tiep tuc...")
                
            elif choice == "2":
                email = input("  Email nguoi nhan: ").strip()
                if not email:
                    print("[!] Email khong duoc de trong")
                    continue
                    
                subject = input("  Tieu de: ").strip() or "Xin chao"
                body = input("  Noi dung: ").strip() or "Hello ban!"
                count = int(input("  So lan (toi da 100): ") or "30")
                count = min(count, 100)
                
                for i in range(count):
                    self.send_via_email_api(email, f"{subject} [{i+1}]", f"{body}\n--\nLan {i+1}")
                    self.sent += 1
                    print(f"\r[*] Da gui: {i+1}/{count}", end="")
                    time.sleep(0.5)
                print(f"\n[+] Da luu {count} email vao emails_sent.txt")
                input("\n[*] Enter de tiep tuc...")
                
            elif choice == "3":
                new_content = input("  Nhap noi dung spam (max 500 ky tu): ").strip()
                if new_content:
                    with open("spam_content.txt", "w") as f:
                        f.write(new_content)
                    print(f"[+] Da luu noi dung: {new_content[:50]}...")
                else:
                    print("[!] Noi dung rong")
                    
            elif choice == "4":
                if os.path.exists(self.log_file):
                    with open(self.log_file, "r") as f:
                        print("\n" + f.read()[-1000:])
                else:
                    print("[!] Chua co log")
                input("\n[*] Enter de tiep tuc...")
                
            elif choice == "0":
                print("\n[+] Thoat spam tool")
                break
                
            else:
                print("[!] Chon sai")

def get_webhook_guide():
    print("""
    === CACH TAO WEBHOOK GOOGLE CHAT ===
    1. Mo Google Chat (chat.google.com)
    2. Tao phong moi hoac chon phong co san
    3. Nhan vao ten phong -> Quan ly webhook
    4. Tao webhook moi -> Copy URL
    5. Dan URL vao tool
    """)

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════╗
    ║   SPAM GMAIL CHAT - a-shell      ║
    ║   Chi can Gmail/Webhook          ║
    ╚══════════════════════════════════╝
    """)
    
    get_webhook_guide()
    tool = SpamGmail()
    tool.show_menu()
