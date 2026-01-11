import sys, subprocess, importlib.util, threading, json, urllib.parse, os

def install_and_import(pkg):
    if importlib.util.find_spec(pkg) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
    globals()[pkg] = __import__(pkg)

for m in ["requests", "pyperclip"]:
    install_and_import(m)

OPTIONS = [
    "EAAAAU","EAAD","EAAAAAY","EAADYP","EAAD6V7","EAAC2SPKT",
    "EAAGOfO","EAAVB","EAAC4","EAACW5F","EAAB","EAAQ",
    "EAAGNO4","EAAH","EAAC","EAAClA","EAATK","EAAI7",
]
API_BASE = "https://adidaphat.site/facebook/tokentocookie"

def find_token(obj):
    if isinstance(obj, dict):
        if 'token' in obj:
            return obj['token']
        for v in obj.values():
            t = find_token(v)
            if t: return t
    elif isinstance(obj, list):
        for i in obj:
            t = find_token(i)
            if t: return t
    return None

def fetch_token(t, cookie):
    try:
        params = {'type': t, 'cookie': cookie}
        url = API_BASE + '?' + urllib.parse.urlencode(params)
        r = requests.get(url, timeout=20)
        try:
            data = r.json()
        except:
            print("Server lỗi\n", r.text); return
        token = find_token(data)
        if token:
            print("Token:", token)
            try: pyperclip.copy(token); print("Đã copy clipboard")
            except: pass
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print("Lỗi:", str(e))

if __name__ == '__main__':
    os.system("cls" if os.name == "nt" else "clear")
    print("=== Tool Lấy Token Facebook ===")
    for i, opt in enumerate(OPTIONS, 1):
        print(f"{i}. {opt}")
    try:
        choice = int(input("Chọn số loại token: ").strip())
        token_type = OPTIONS[choice - 1]
    except: sys.exit("Lựa chọn không hợp lệ")
    cookie = input("Nhập cookie: ").strip()
    if not cookie: sys.exit("Cookie rỗng")
    print("Đang lấy token...")
    t = threading.Thread(target=fetch_token, args=(token_type, cookie), daemon=True)
    t.start(); t.join()
