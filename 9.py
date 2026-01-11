import os
import re
import time
import requests
import pyfiglet
import threading
import random
import json
import pyfiglet
from termcolor import colored
from colorama import Fore, Style, init
from datetime import datetime
import sys
import builtins

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colorful_box():
    start_rgb = (255, 105, 180)
    end_rgb   = (30, 144, 255)

    def rgb_to_ansi(r, g, b):
        return f"\033[38;2;{r};{g};{b}m"

    reset = "\033[0m"

    banner = pyfiglet.figlet_format("  NamAnh", font="slant")
    text = banner + "       Tool Treo Mess Đa Cookie By CteVcl🧸\n" + "-" * 55

    length = sum(1 for ch in text if ch.strip() != "")
    out, i = "", 0

    for ch in text:
        if ch.strip() != "":
            ratio = i / length
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            out += rgb_to_ansi(r, g, b) + ch + reset
            i += 1
        else:
            out += ch

    print(out)

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

        sites = ['https://web.facebook.com', 'https://mbasic.facebook.com']

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
            'Origin': 'https://web.facebook.com',
            'Referer': 'https://web.facebook.com/',
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

            raw_text = response.text.strip()
            if raw_text.startswith("["):
                json_objects = [json.loads(obj) for obj in raw_text.splitlines() if obj.strip()]
                data = json_objects[0] if json_objects else {}
            else:
                response_text = raw_text.split('{"successful_results"')[0]
                data = json.loads(response_text)

            if "o0" not in data:
                return {"error": "Không tìm thấy dữ liệu thread list."}

            if "errors" in data["o0"]:
                err = data["o0"]["errors"][0].get("summary", "Lỗi không xác định.")
                return {"error": f"Facebook API Error: {err}"}

            threads = data["o0"]["data"]["viewer"]["message_threads"]["nodes"]
            thread_list = []
            for thread in threads:
                if not thread.get("thread_key") or not thread["thread_key"].get("thread_fbid"):
                    continue

                name = thread.get("name")
                if not name:
                    participants = thread.get("all_participants", {}).get("nodes", [])
                    names = [p["messaging_actor"]["name"] for p in participants if "messaging_actor" in p]
                    name = ", ".join(names) if names else "Không có tên"

                thread_list.append({
                    "thread_id": thread["thread_key"]["thread_fbid"],
                    "thread_name": name
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

def get_uid(cookie):
    try:
        return re.search(r'c_user=(\d+)', cookie).group(1)
    except:
        return '0'

def get_fb_dtsg_jazoest(cookie, target_id):
    try:
        response = requests.get(
            f'https://mbasic.facebook.com/privacy/touch/block/confirm/?bid={target_id}',
            headers={'cookie': cookie, 'user-agent': 'Mozilla/5.0'}
        ).text
        fb_dtsg = re.search('name="fb_dtsg" value="([^"]+)"', response).group(1)
        jazoest = re.search('name="jazoest" value="([^"]+)"', response).group(1)
        return fb_dtsg, jazoest
    except:
        return None, None

def get_eaag_token(cookie):
    try:
        res = requests.get(
            'https://business.facebook.com/business_locations',
            headers={'cookie': cookie, 'user-agent': 'Mozilla/5.0'}
        )
        token = re.search(r'EAAG\w+', res.text)
        return token.group() if token else None
    except:
        return None

def send_message(idbox, fb_dtsg, jazoest, cookie, message_body):
    try:
        uid = get_uid(cookie)
        timestamp = int(time.time() * 1000)
        data = {
            'thread_fbid': idbox,
            'action_type': 'ma-type:user-generated-message',
            'body': message_body,
            'client': 'mercury',
            'author': f'fbid:{uid}',
            'timestamp': timestamp,
            'offline_threading_id': str(timestamp),
            'message_id': str(timestamp),
            'source': 'source:chat:web',
            '__user': uid,
            '__a': '1',
            '__req': '1b',
            '__rev': '1015919737',
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest
        }
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post('https://www.facebook.com/messaging/send/', data=data, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f'Lỗi gửi tới ID {idbox}: {e}')
        return False

def worker(cookie_data, id_list, message_list, base_delay):
    cookie = cookie_data['cookie']
    while True:
        try:
            fb_dtsg, jazoest = get_fb_dtsg_jazoest(cookie, id_list[0])
            if not fb_dtsg or not jazoest:
                print("Không lấy được fb_dtsg/jazoest")
                time.sleep(60)
                continue

            for idbox in id_list:
                for message_body in message_list:
                    success = send_message(idbox, fb_dtsg, jazoest, cookie, message_body)
                    if success:
                        print(f"✅ Gửi tin nhắn thành công tới: {idbox}")
                    else:
                        print(f"❌ Gửi tin nhắn thất bại tới: {idbox}")

                    delay = base_delay + random.uniform(-0.5, 0.5)
                    if delay < 0:
                        delay = 0
                    time.sleep(delay)
        except Exception as err:
            print(f"Lỗi không xác định: {err}")
            time.sleep(60)

def treo_mess():
    cookie_list = []
    id_list = []
    while True:
        ck = input(colored("=> Nhập cookie (Hoặc ấn 'enter' để dừng): ", 'yellow', attrs=['bold'])).strip()
        if ck == '':
            break
        if 'c_user=' in ck and 'xs=' in ck:
            print(colored("Đang lấy danh sách box 🔍...", 'cyan'))
            extractor = FacebookThreadExtractor(ck)
            result = extractor.get_thread_list(limit=50)
            if "error" in result:
                print(colored(f"⚠️ {result['error']}", 'red'))
                cookie_list.append(ck)
                continue

            threads = result.get("threads", [])
            if not threads:
                print(colored("Không tìm thấy box nào từ cookie này.", 'red'))
                cookie_list.append(ck)
                continue

            print(colored(f"➤ Đã liệt kê {len(threads)} danh sách box:", 'green'))
            for idx, t in enumerate(threads, 1):
                print(colored(f"[{idx}] {t['thread_name']}  —  ID: {t['thread_id']}", 'white'))

            choice = input(colored("Chọn box (vd: 1,2,3) hoặc gõ 'all' & 'Enter' để bỏ qua: ", 'yellow', attrs=['bold'])).strip()
            if choice.lower() == 'all':
                for t in threads:
                    if str(t['thread_id']) not in id_list:
                        id_list.append(str(t['thread_id']))
                print(colored(f"Đã thêm tất cả ({len(threads)}) box vào danh sách ID.", 'green'))
            elif choice:
                try:
                    indices = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
                    added = 0
                    for i in indices:
                        if 1 <= i <= len(threads):
                            tid = str(threads[i-1]['thread_id'])
                            if tid not in id_list:
                                id_list.append(tid)
                                added += 1
                        else:
                            print(colored(f"Chỉ số {i} không hợp lệ, bỏ qua.", 'red'))
                    print(colored(f"Đã thêm {added} ID từ lựa chọn.", 'green'))
                except Exception as e:
                    print(colored(f"Lỗi khi parse lựa chọn: {e}", 'red'))
            else:
                print(colored("Bỏ qua!", 'yellow'))
                cookie_list.append(ck)
            if ck not in cookie_list:
                cookie_list.append(ck)
        else:
            print(colored("Cookie không hợp lệ (thiếu c_user= hoặc xs=). Bỏ qua.", 'red'))

    if not id_list:
        while True:
            idbox = input(colored("=> Nhập ID Box (Hoặc ấn 'enter' để dừng): ", 'yellow', attrs=['bold'])).strip()
            if idbox == '':
                break
            if idbox.isdigit():
                id_list.append(idbox)

    file_list = []
    while True:
        name_file = input(colored("=> Nhập file.txt (Hoặc 'enter' để bỏ qua): ", 'yellow', attrs=['bold'])).strip()
        if name_file == '':
            break
        if name_file.endswith('.txt'):
            file_list.append(name_file)

    try:
        base_delay = int(input(colored('=> Nhập delay: ', 'yellow', attrs=['bold'])))
    except:
        base_delay = 1

    user_data_list = []
    for index, ck in enumerate(cookie_list, 1):
        try:
            uid = get_uid(ck)
            token = get_eaag_token(ck)

            if token:
                try:
                    res = requests.get(
                        f'https://graph.facebook.com/{uid}?fields=name&access_token={token}',
                        headers={'cookie': ck, 'user-agent': 'Mozilla/5.0'},
                        timeout=10
                    ).json()
                    name = res.get('name', f'User_{index}')
                except:
                    name = f'User_{index}'
            else:
                name = f'User_{index}'

            user_data_list.append({'name': name, 'id': uid, 'cookie': ck})
        except Exception as e:
            print(colored(f"[{index}] Lỗi lấy thông tin user: {e}", 'red'))

    message_list = []
    for f in file_list:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if content:
                    message_list.append(content)
        except Exception as e:
            print(colored(f'Lỗi đọc file {f}: {e}', 'red'))

    if not user_data_list:
        print(colored("❌ cookie không hợp lệ!", 'red'))
        return
    if not id_list:
        print(colored("❌ Không có ID Box!", 'red'))
        return
    if not message_list:
        print(colored("Không có nội dung tin nhắn để gửi", 'red'))
        return

    for data in user_data_list:
        thread = threading.Thread(target=worker, args=(data, id_list, message_list, base_delay), daemon=True)
        thread.start()

    print(Fore.GREEN + "\n===🚀 BẮT ĐẦU GỬI===")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print(pastel(255, 182, 193, "👋 Goodbye!"))

def nhay_mess():
    cookie_list = []
    id_list = []

    while True:
        ck = input(colored("=> Nhập cookie (Hoặc ấn 'enter' để dừng): ", 'yellow', attrs=['bold'])).strip()
        if ck == "":
            break
        if 'c_user=' in ck and 'xs=' in ck:
            print(colored("Đang lấy danh sách box 🔍...", 'cyan'))
            extractor = FacebookThreadExtractor(ck)
            result = extractor.get_thread_list(limit=50)
            if "error" in result:
                print(colored(f"⚠️ {result['error']}", 'red'))
                cookie_list.append(ck)
                continue

            threads = result.get("threads", [])
            if not threads:
                print(colored("Không tìm thấy box nào từ cookie này.", 'red'))
                cookie_list.append(ck)
                continue

            print(colored(f"➤ Đã liệt kê {len(threads)} danh sách box:", 'green'))
            for idx, t in enumerate(threads, 1):
                print(colored(f"[{idx}] {t['thread_name']}  —  ID: {t['thread_id']}", 'white'))

            choice = input(colored("Chọn box (vd: 1,2,3) hoặc gõ 'all' & 'Enter' để bỏ qua: ", 'yellow', attrs=['bold'])).strip()
            if choice.lower() == 'all':
                for t in threads:
                    if str(t['thread_id']) not in id_list:
                        id_list.append(str(t['thread_id']))
                print(colored(f"Đã thêm tất cả ({len(threads)}) box vào danh sách ID.", 'green'))
            elif choice:
                try:
                    indices = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
                    added = 0
                    for i in indices:
                        if 1 <= i <= len(threads):
                            tid = str(threads[i - 1]['thread_id'])
                            if tid not in id_list:
                                id_list.append(tid)
                                added += 1
                        else:
                            print(colored(f"Chỉ số {i} không hợp lệ, bỏ qua.", 'red'))
                    print(colored(f"Đã thêm {added} ID từ lựa chọn.", 'green'))
                except Exception as e:
                    print(colored(f"Lỗi khi parse lựa chọn: {e}", 'red'))
            else:
                print(colored("Bỏ qua việc thêm ID tự động cho cookie này.", 'yellow'))
                cookie_list.append(ck)
            if ck not in cookie_list:
                cookie_list.append(ck)
        else:
            print(colored("Cookie không hợp lệ (thiếu c_user= hoặc xs=). Bỏ qua.", 'red'))

    if not id_list:
        while True:
            idbox = input(colored("=> Nhập ID Box (Hoặc ấn 'enter' để dừng): ", 'yellow', attrs=['bold'])).strip()
            if idbox == "":
                break
            if idbox.isdigit():
                id_list.append(idbox)

    name_file = input(colored("=> Nhập tên file (ví dụ file.txt): ", 'yellow', attrs=['bold'])).strip()
    if name_file == "":
        name_file = ""

    base_delay = int(input(colored('=> Nhập delay: ', 'yellow', attrs=['bold'])))

    user_data_list = []
    for index, ck in enumerate(cookie_list, 1):
        try:
            uid = get_uid(ck)
            token = get_eaag_token(ck)

            if token:
                res = requests.get(
                    f'https://graph.facebook.com/{uid}?fields=name&access_token={token}',
                    headers={'cookie': ck, 'user-agent': 'Mozilla/5.0'}
                ).json()
                name = res.get('name', f'User_{index}')
            else:
                name = f'User_{index}'

            user_data_list.append({'name': name, 'id': uid, 'cookie': ck})
        except Exception as e:
            print(f"[{index}] Lỗi lấy thông tin user: {e}")

    try:
        with open(name_file, 'r', encoding='utf-8') as file:
            message_list = [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f'Lỗi đọc file {name_file}: {e}')
        return

    if not user_data_list:
        print("Không có cookie hợp lệ để chạy")
        return
    if not id_list:
        print("Không có ID Box nào được nhập")
        return
    if not message_list:
        print(f"File {name_file} không có nội dung")
        return

    def auto_worker(cookie_data, id_list, message_list, base_delay):
        cookie = cookie_data['cookie']
        index = 0
        while True:
            try:
                fb_dtsg, jazoest = get_fb_dtsg_jazoest(cookie, id_list[0])
                if not fb_dtsg or not jazoest:
                    print(f"Không lấy được fb_dtsg/jazoest")
                    time.sleep(60)
                    continue

                for idbox in id_list:
                    message_body = message_list[index]
                    success = send_message(idbox, fb_dtsg, jazoest, cookie, message_body)
                    if success:
                        print(f"✅ Gửi tin nhắn thành công tới: {idbox}")
                    else:
                        print(f"❌ Gửi tin nhắn thất bại tới: {idbox}")

                    index = (index + 1) % len(message_list)
                    delay = base_delay + random.uniform(-0.5, 0.5)
                    if delay < 0:
                        delay = 0
                    time.sleep(delay)
            except Exception as err:
                print(f"Lỗi không xác định: {err}")
                time.sleep(60)

    for data in user_data_list:
        thread = threading.Thread(target=auto_worker, args=(data, id_list, message_list, base_delay), daemon=True)
        thread.start()

    print(Fore.GREEN + "\n===🚀 BẮT ĐẦU GỬI===")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print(pastel(255, 182, 193, "👋 Goodbye!"))

def parse_cookie_string(cookie_string):
    cookie_dict = {}
    for cookie in cookie_string.split(";"):
        if "=" in cookie:
            key, value = cookie.strip().split("=", 1)
            cookie_dict[key] = value
    return cookie_dict

def Headers(setCookies, dataForm=None, Host="web.facebook.com"):
    headers = {
        "Host": Host,
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": f"https://{Host}",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": f"https://{Host}/",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    if dataForm:
        headers["Content-Length"] = str(len(str(dataForm)))
    return headers

def gen_threading_id():
    return str(
        int(format(int(time.time() * 1000), "b") +
        ("0000000000000000000000" +
        format(int(random.random() * 4294967295), "b"))[-22:], 2)
    )

def dataGetHome(setCookies):
    headers = {
        'Cookie': setCookies,
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
    }

    dictValueSaved = {}
    try:
        c_user = re.search(r"c_user=(\d+)", setCookies)
        dictValueSaved["FacebookID"] = c_user.group(1) if c_user else "0"
    except:
        dictValueSaved["FacebookID"] = "0"

    response = requests.get("https://web.facebook.com", headers=headers)
    fb_dtsg_match = re.search(r'"token":"(.*?)"', response.text)
    if not fb_dtsg_match:
        fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
    dictValueSaved["fb_dtsg"] = fb_dtsg_match.group(1) if fb_dtsg_match else ""
    jazoest_match = re.search(r'jazoest=(\d+)', response.text)
    if not jazoest_match:
        jazoest_match = re.search(r'name="jazoest" value="(\d+)"', response.text)
    dictValueSaved["jazoest"] = jazoest_match.group(1) if jazoest_match else "22036"
    dictValueSaved["clientRevision"] = "1015919737"
    dictValueSaved["cookieFacebook"] = setCookies
    return dictValueSaved

def tenbox(newTitle, threadID, dataFB):
    try:
        message_id = gen_threading_id()
        timestamp = int(time.time() * 1000)
        form_data = {
            "client": "mercury",
            "action_type": "ma-type:log-message",
            "author": f"fbid:{dataFB['FacebookID']}",
            "thread_id": str(threadID),
            "timestamp": timestamp,
            "timestamp_relative": str(int(time.time())),
            "source": "source:chat:web",
            "source_tags[0]": "source:chat",
            "offline_threading_id": message_id,
            "message_id": message_id,
            "threading_id": gen_threading_id(),
            "thread_fbid": str(threadID),
            "thread_name": str(newTitle),
            "log_message_type": "log:thread-name",
            "fb_dtsg": dataFB["fb_dtsg"],
            "jazoest": dataFB["jazoest"],
            "__user": str(dataFB["FacebookID"]),
            "__a": "1",
            "__req": "1",
            "__rev": dataFB.get("clientRevision", "1015919737")
        }

        response = requests.post(
            "https://web.facebook.com/messaging/set_thread_name/",
            data=form_data,
            headers=Headers(dataFB["cookieFacebook"], form_data),
            cookies=parse_cookie_string(dataFB["cookieFacebook"]),
            timeout=10
        )

        if response.status_code == 200:
            return True, f"✅ Đã đổi tên thành: {newTitle}"
        else:
            return False, f"❌ HTTP {response.status_code}"
    except Exception as e:
        return False, f"❌ Lỗi: {e}"

def nhay_name_box():
    cookie_list = []
    cookie_to_ids = {}

    while True:
        ck = input(colored("=> Nhập cookie (Hoặc ấn 'enter' để dừng): ", 'yellow', attrs=['bold'])).strip()
        if ck == "":
            break
        if 'c_user=' in ck and 'xs=' in ck:
            print(colored("Đang lấy danh sách box 🔍...", 'cyan'))
            extractor = FacebookThreadExtractor(ck)
            result = extractor.get_thread_list(limit=50)
            if "error" in result:
                print(colored(f"⚠️ {result['error']}", 'red'))
                cookie_list.append(ck)
                cookie_to_ids[ck] = []
                continue

            threads = result.get("threads", [])
            if not threads:
                print(colored("Không tìm thấy box nào từ cookie này.", 'red'))
                cookie_list.append(ck)
                cookie_to_ids[ck] = []
                continue

            print(colored(f"➤ Đã liệt kê {len(threads)} danh sách box:", 'green'))
            for idx, t in enumerate(threads, 1):
                print(colored(f"[{idx}] {t['thread_name']}  —  ID: {t['thread_id']}", 'white'))

            choice = input(colored("Chọn box (vd: 1,2,3) hoặc gõ 'all' & 'Enter' để bỏ qua: ", 'yellow', attrs=['bold'])).strip()
            ids = []
            if choice.lower() == 'all':
                ids = [str(t['thread_id']) for t in threads]
                print(colored(f"Đã thêm tất cả là ({len(ids)}) box.", 'green'))
            elif choice:
                try:
                    indices = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
                    for i in indices:
                        if 1 <= i <= len(threads):
                            ids.append(str(threads[i-1]['thread_id']))
                        else:
                            print(colored(f"Chỉ số {i} không hợp lệ, bỏ qua.", 'red'))
                    if ids:
                        print(colored(f"Đã thêm {len(ids)} box.", 'green'))
                except Exception as e:
                    print(colored(f"Lỗi khi parse lựa chọn: {e}", 'red'))
            else:
                print(colored("Bỏ qua việc chọn box!", 'yellow'))

            cookie_list.append(ck)
            cookie_to_ids[ck] = ids
        else:
            print(colored("Cookie không hợp lệ (thiếu c_user= hoặc xs=). Bỏ qua.", 'red'))

    for ck in cookie_list:
        if not cookie_to_ids.get(ck):
            print(colored(f"Cookie: {ck[:40]}... chưa có ID box được chọn.", 'yellow'))
            while True:
                idbox = input(colored(f"=> Nhập ID Box (hoặc 'enter' để bỏ qua): ", 'yellow')).strip()
                if idbox == "":
                    break
                if idbox.isdigit():
                    cookie_to_ids.setdefault(ck, []).append(idbox)
                    print(colored(f"Thêm ID {idbox}", 'green'))

    final_cookies = []
    for ck in cookie_list:
        ids = cookie_to_ids.get(ck, [])
        if ids:
            final_cookies.append(ck)
        else:
            print(colored(f"⚠️ Cookie (ẩn) không có ID box, sẽ không chạy.", 'red'))

    if not final_cookies:
        print(colored("❌ Không có cookie + ID hợp lệ để chạy", 'red'))
        return

    name_file = input(colored("=> Nhập file ngôn (ví dụ file.txt): ", 'yellow', attrs=['bold'])).strip()
    try:
        with open(name_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(colored(f"❌ Không tìm thấy file {name_file}", 'red'))
        return
    except Exception as e:
        print(colored(f"❌ Lỗi đọc file {name_file}: {e}", 'red'))
        return

    if not lines:
        print(colored(f"❌ File {name_file} không có nội dung!", 'red'))
        return

    try:
        delay = float(input(colored("=> Nhập delay: ", 'yellow', attrs=['bold'])))
    except:
        delay = 1.0

    def nhay_name_worker(cookie, ids, lines, delay):
        dataFB = dataGetHome(cookie)
        try:
            uid = dataFB.get("FacebookID", "0")
            print(colored(f"[User-{uid}] Spam – {len(ids)} box — {len(lines)} dòng", 'green'))
        except:
            print(colored("[Worker] Khởi động", 'green'))

        while True:
            for name_line in lines:
                for thread_id in ids:
                    success, log = tenbox(name_line, thread_id, dataFB)
                    print(colored(f"[{dataFB.get('FacebookID','?')}] {log}", 'white'))
                    time.sleep(delay + random.uniform(0.1, 0.3))

    for ck in final_cookies:
        ids = cookie_to_ids.get(ck, [])
        if not ids:
            continue
        thread = threading.Thread(target=nhay_name_worker, args=(ck, ids, lines, delay), daemon=True)
        thread.start()

    print(colored("\n===🚀 BẮT ĐẦU NHÂY NAME BOX===", 'green'))
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print(colored("👋 Goodbye", 'yellow'))

def get_auth_tokens(cookie):
    headers = {'User-Agent': 'Mozilla/5.0', 'Cookie': cookie}
    try:
        r = requests.get("https://mbasic.facebook.com/", headers=headers, timeout=10)
    except Exception as e:
        print("Lỗi kết nối:", e)
        return None, None, None, None, None, None

    if r.status_code != 200:
        print("Không thể truy cập mbasic.facebook.com (status:", r.status_code, "). Cookie có thể không hợp lệ.")
        return None, None, None, None, None, None

    html = r.text
    c_user = None
    m = re.search(r'c_user=(\d+)', cookie)
    if m:
        c_user = m.group(1)

    fb_dtsg = None
    m2 = re.search(r'name="fb_dtsg" value="([^"]+)"', html)
    if m2:
        fb_dtsg = m2.group(1)

    if not c_user:
        m3 = re.search(r'\/profile.php\?id=(\d+)', html)
        if m3:
            c_user = m3.group(1)

    rev = "1"
    a = "1"
    req = "1b"
    jazoest = None
    m4 = re.search(r'name="jazoest" value="(\d+)"', html)
    if m4:
        jazoest = m4.group(1)

    return c_user, fb_dtsg, rev, req, a, jazoest

_uid_name_cache = {}

def fetch_user_name(uid, cookie):
    if uid in _uid_name_cache:
        return _uid_name_cache[uid]

    tokens = get_auth_tokens(cookie)
    if not tokens or not tokens[0] or not tokens[1]:
        return None
    c_user, fb_dtsg, rev, req, a, jazoest = tokens
    form = {"ids[0]": uid, "fb_dtsg": fb_dtsg, "__a": a, "__req": req, "__rev": rev}
    headers = {'User-Agent': 'Mozilla/5.0', 'Cookie': cookie, 'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        r = requests.post("https://web.facebook.com/chat/user_info/", headers=headers, data=form, timeout=10)
        txt = r.text
        if txt.startswith("for (;;);"):
            txt = txt[9:]
        data = json.loads(txt)
        if "payload" in data and "profiles" in data["payload"]:
            first = list(data["payload"]["profiles"].keys())[0]
            name = data["payload"]["profiles"][first].get("name")
            _uid_name_cache[uid] = name
            return name
    except Exception:
        pass
    return None

def send_message_tag(cookie, thread_id, tag_uid, tag_name, body):
    tokens = get_auth_tokens(cookie)
    if not tokens or not tokens[0] or not tokens[1]:
        print(Fore.RED + "[send_message_tag] Cookie không hợp lệ.")
        return False
    c_user, fb_dtsg, rev, req, a, jazoest = tokens
    ts = str(int(time.time() * 1000))
    payload = {
        "thread_fbid": thread_id,
        "action_type": "ma-type:user-generated-message",
        "body": body,
        "client": "mercury",
        "author": f"fbid:{c_user}",
        "timestamp": ts,
        "offline_threading_id": ts,
        "message_id": ts,
        "source": "source:chat:web",
        "ephemeral_ttl_mode": "0",
        "__user": c_user,
        "__a": a,
        "__req": req,
        "__rev": rev,
        "fb_dtsg": fb_dtsg,
        "source_tags[0]": "source:chat",
        "profile_xmd[0][id]": tag_uid,
        "profile_xmd[0][offset]": 0,
        "profile_xmd[0][length]": len(f"@{tag_name}"),
        "profile_xmd[0][type]": "p",
    }
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Cookie': cookie,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': f'https://web.facebook.com/messages/t/{thread_id}'
    }
    try:
        r = requests.post("https://www.facebook.com/messaging/send/", data=payload, headers=headers, timeout=15)
        if r.status_code == 200:
            print(f"✅ Gửi tin nhắn thành công tới: [{thread_id}]")
            return True
        else:
            print(Fore.RED + f"[{thread_id}] ❌ HTTP {r.status_code}")
            return False
    except Exception as e:
        print(Fore.RED + f"[{thread_id}] Lỗi khi gửi: {e}")
        return False

def nhay_tag_mess():
    cookie_list = []
    while True:
        ck = input(colored("=> Nhập cookie (Hoặc ấn 'enter' để dừng): ", 'yellow', attrs=['bold'])).strip()
        if ck == "":
            break
        if 'c_user=' in ck and 'xs=' in ck:
            cookie_list.append(ck)
        else:
            print(colored("Cookie không hợp lệ (thiếu c_user= hoặc xs=). Bỏ qua.", 'red'))

    if not cookie_list:
        print(colored("❌ Bạn chưa nhập cookie nào. Hủy.", 'red'))
        return

    cookie_to_ids = {}
    for ck in cookie_list:
        print(colored(f"Đang lấy danh sách box 🔍...", 'cyan'))
        extractor = FacebookThreadExtractor(ck)
        result = extractor.get_thread_list(limit=100)
        if "error" in result:
            print(colored(f"⚠️ {result['error']}", 'red'))
            cookie_to_ids[ck] = []
            continue

        threads = result.get("threads", [])
        if not threads:
            print(colored("Không tìm thấy box nào từ cookie này.", 'red'))
            cookie_to_ids[ck] = []
            continue

        for idx, t in enumerate(threads, 1):
            print(colored(f"[{idx}] {t['thread_name']}  —  ID: {t['thread_id']}", 'white'))

        choice = input(colored("Chọn box (vd: 1,2,3) hoặc gõ 'all' & 'Enter' để bỏ qua: ", 'yellow', attrs=['bold'])).strip()
        ids = []
        if choice.lower() == 'all':
            ids = [str(t['thread_id']) for t in threads]
            print(colored(f"Đã thêm tất cả ({len(ids)}) box.", 'green'))
        elif choice:
            try:
                indices = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
                for i in indices:
                    if 1 <= i <= len(threads):
                        ids.append(str(threads[i-1]['thread_id']))
                    else:
                        print(colored(f"Chỉ số {i} không hợp lệ, bỏ qua.", 'red'))
                if ids:
                    print(colored(f"Đã thêm {len(ids)} box.", 'green'))
            except Exception as e:
                print(colored(f"Lỗi parse lựa chọn: {e}", 'red'))
        else:
            print(colored("Bỏ qua việc tự động chọn box (bạn sẽ nhập ID tay nếu muốn).", 'yellow'))

        cookie_to_ids[ck] = ids

    for ck in cookie_list:
        if not cookie_to_ids.get(ck):
            while True:
                id_input = input(colored(f"Nhập ID Box (hoặc enter để bỏ qua): ", 'yellow', attrs=['bold'])).strip()
                if id_input == "":
                    break
                parts = [p.strip() for p in id_input.split(',') if p.strip()]
                for p in parts:
                    if p.isdigit():
                        cookie_to_ids.setdefault(ck, []).append(p)
                    else:
                        print(colored(f"ID {p} không phải số, bỏ qua.", 'red'))
                if cookie_to_ids.get(ck):
                    break

    uid_input = input(colored('=> Nhập UID cần tag: ', 'yellow', attrs=['bold'])).strip()
    global_uids = []
    if uid_input:
        global_uids = [u.strip() for u in uid_input.split(',') if u.strip().isdigit()]

    cookie_to_uids = {}
    if global_uids:
        for ck in cookie_list:
            cookie_to_uids[ck] = list(global_uids)
    else:
        for ck in cookie_list:
            uids = []
            while True:
                u = input(colored(f"=> Cookie {ck[:20]}... - Nhập UID(s) cho cookie này (hoặc enter để bỏ qua): ", 'yellow')).strip()
                if u == "":
                    break
                for part in [p.strip() for p in u.split(',') if p.strip()]:
                    if part.isdigit():
                        uids.append(part)
                    else:
                        print(colored(f"UID {part} không hợp lệ, bỏ qua.", 'red'))
                if uids:
                    break
            cookie_to_uids[ck] = uids

    name_file = input(colored('=> Nhập tên file (ví dụ: file.txt): ', 'yellow', attrs=['bold'])).strip()
    messages = []
    if name_file:
        try:
            with open(name_file, 'r', encoding='utf-8') as f:
                messages = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(colored(f"❌ Lỗi đọc file {name_file}: {e}", 'red'))
            return
    else:
        ngonnhay_default = [
            "sao kia", "manh di ma", "kem ak", "run ak", "cay tao ak", "chay de",
            "clm dot ak", "lien tuc de", "speed ma", "le em", "slow kia", "anh speed vkl",
            "sua de", "oc cho ak", "m ngu ak", "sua chill v", "nhanh ti", "tiep de m",
            "bat luc ak", "ga ak", "slow ak", "speed vl", "lien tuc di", "anh man mak"
        ]
        messages = ngonnhay_default

    if not messages:
        print(colored("❌ Không có nội dung để gửi.", 'red'))
        return

    delay_input = input(colored('=> Nhập delay: ', 'yellow', attrs=['bold'])).strip()
    min_delay, max_delay = 2.0, 5.0
    if delay_input:
        if "-" in delay_input:
            try:
                parts = delay_input.replace(" ", "").split("-")
                min_delay, max_delay = float(parts[0]), float(parts[1])
            except:
                pass
        else:
            try:
                v = float(delay_input)
                min_delay = max_delay = v
            except:
                pass

    valid_runners = []
    for ck in cookie_list:
        ids = cookie_to_ids.get(ck, [])
        uids = cookie_to_uids.get(ck, [])
        if not ids:
            print(colored(f"⚠️ Cookie {ck[:20]}... không có ID box, sẽ bỏ qua.", 'red'))
            continue
        if not uids:
            print(colored(f"⚠️ Cookie {ck[:20]}... không có UID để tag, sẽ bỏ qua.", 'red'))
            continue
        valid_runners.append((ck, ids, uids))

    if not valid_runners:
        print(colored("❌ Không có cấu hình hợp lệ để chạy.", 'red'))
        return

    def tag_worker(cookie, ids, uids, messages, min_d, max_d):
        name_map = {}
        for uid in uids:
            try:
                nm = fetch_user_name(uid, cookie)
                name_map[uid] = nm if nm else uid
            except:
                name_map[uid] = uid
        try:
            while True:
                for thread_id in ids:
                    for uid in uids:
                        tag_name = name_map.get(uid, uid)
                        for msg in messages:
                            body = f"{msg} *@{tag_name}*"
                            ok = send_message_tag(cookie, thread_id, uid, tag_name, body)
                            if not ok:
                                time.sleep(3)
                            if min_d == max_d:
                                time.sleep(min_d)
                            else:
                                time.sleep(random.uniform(min_d, max_d))
        except Exception as e:
            print(colored(f"[Worker] Lỗi không xác định: {e}", 'red'))

    for ck, ids, uids in valid_runners:
        t = threading.Thread(target=tag_worker, args=(ck, ids, uids, messages, min_delay, max_delay), daemon=True)
        t.start()

    print(colored("\n===🚀 BẮT ĐẦU GỬI===", 'cyan'))
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print(colored("\n🛑 Stop!", 'yellow'))

def nhay_code_lag():
    cookie_list = []
    id_list = []

    while True:
        ck = input(colored("=> Nhập cookie (Hoặc ấn 'enter' để dừng): ", 'yellow', attrs=['bold'])).strip()
        if ck == "":
            break
        if 'c_user=' in ck and 'xs=' in ck:
            print(colored("Đang lấy danh sách box 🔍...", 'cyan'))
            extractor = FacebookThreadExtractor(ck)
            result = extractor.get_thread_list(limit=50)
            if "error" in result:
                print(colored(f"⚠️ {result['error']}", 'red'))
                cookie_list.append(ck)
                continue

            threads = result.get("threads", [])
            if not threads:
                print(colored("Không tìm thấy box nào từ cookie này.", 'red'))
                cookie_list.append(ck)
                continue

            print(colored(f"➤ Đã liệt kê {len(threads)} danh sách box:", 'green'))
            for idx, t in enumerate(threads, 1):
                print(colored(f"[{idx}] {t['thread_name']}  —  ID: {t['thread_id']}", 'white'))

            choice = input(colored("Chọn box (vd: 1,2,3) hoặc gõ 'all' & 'Enter' để bỏ qua: ", 'yellow', attrs=['bold'])).strip()
            if choice.lower() == 'all':
                for t in threads:
                    if str(t['thread_id']) not in id_list:
                        id_list.append(str(t['thread_id']))
                print(colored(f"Đã thêm tất cả ({len(threads)}) box vào danh sách ID.", 'green'))
            elif choice:
                try:
                    indices = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
                    added = 0
                    for i in indices:
                        if 1 <= i <= len(threads):
                            tid = str(threads[i - 1]['thread_id'])
                            if tid not in id_list:
                                id_list.append(tid)
                                added += 1
                        else:
                            print(colored(f"Chỉ số {i} không hợp lệ, bỏ qua.", 'red'))
                    print(colored(f"Đã thêm {added} ID từ lựa chọn.", 'green'))
                except Exception as e:
                    print(colored(f"Lỗi khi parse lựa chọn: {e}", 'red'))
            else:
                print(colored("Bỏ qua việc thêm ID tự động cho cookie này.", 'yellow'))
                cookie_list.append(ck)
            if ck not in cookie_list:
                cookie_list.append(ck)
        else:
            print(colored("Cookie không hợp lệ (thiếu c_user= hoặc xs=). Bỏ qua.", 'red'))

    if not id_list:
        while True:
            idbox = input(colored("=> Nhập ID Box (Hoặc ấn 'enter' để dừng): ", 'yellow', attrs=['bold'])).strip()
            if idbox == "":
                break
            if idbox.isdigit():
                id_list.append(idbox)

    name_file = input(colored("=> Nhập tên file (ví dụ file.txt): ", 'yellow', attrs=['bold'])).strip()
    if name_file == "":
        name_file = ""

    base_delay = int(input(colored('=> Nhập delay: ', 'yellow', attrs=['bold'])))

    codelag = """ 
⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟/꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟/꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰"L̸̢͝҉̷̧̕҉̴̨͠҉̵̷̡̨̛͊͝҉̵̢̆̕҈̢͠҉̶̷̈́̕͢͜͡҉̶̷̨̧̊͠͠҉҉̷̢̧̎͝͞҉҈̸̨̧͒҇̕҉҉̵̢̡̛̌̕҉̶̷̧̡̛҇̈҉̸̶̢̢̉͠͡҉̴̢҇̅҈̡̕҉̵̵̨҇͑͜͠҉̸̸̧̅͢͡͡҉̴̶̢́҇͢͠҉̷̸̧̢҇̄͠҉҈̷̧̒̕͜͞҉҈̢̛͒҉̨҇҉̷̇͜͠҈̨҇҉҉̛̀͜҉̧̕҉̶̵̧̧͗̕͝҉̵̴̢̡̇͠͝҉̵̸̡̓̕̕͜҉̷̵̡̨̅̕͠҉̷͖͢͠҈̧̕҉҉̸̨͍̕̕͜҉҉̪҇͜҈̨̕҉̷̢̫͞҉̨҇҉̴̸̨̧̩͠͞҉̸̞̕͢҉̨҇҉҈̶̧̢̛̛̥҉̵̶̧̨̛͎͝҉̶̶̡̧̛̜͝҉҈̨͔͠҉̧̛҉̵̧͙͞҉̧͞҉҉̶̙͜͜͞͠҉̷̷̢̠̕͢͝҉̴̴̢̡̛͇͡҉̵̨͕͠҉̧͡҉̷̢͞҉̷͢͡҉҉̷̸̡̕͢͠҉̵̵̡̨҇̐҇҉̷̶̧̛҇̐͢҉̸̡́͞҉̢͠҉̷̸̢̧҇̔҇҉҉̢̈́͠҉̡͡҉̷̢̅͝҉͢͡҉̴̵̧̀͜͠͡҉҈̧͆̕҉̡̛҉̶̶̨̧͗͠͡҉̴̸̡̡̛̉҇҉̶̸̢̢̀͞͡҉̷̶̧̢̋҇̕҉̵̷̢̨͗͠͡҉̷̸̢̢̈́̕̕҉̵̶̢̡̏͝͝҉̸̵̧̾͜͡͞҉̵̶̧̈̕͜͞҉̷̴̨̛͐̕͜҉̶̴̧̓͢͡͞҉̶̴̡̨̛̅̕҉҈̶͆͢͢͡͡҉҉̸̢̧̯̕͝҉̶̡͙҇҉͢͠҉҉̷̧̧̟҇͡҉̸͍͢͡҈̧͝҉҈̶̧̢̛̳͝҉̵̸̨͇͢͝͞҉҈̷̧̛͈̕͢҉҉̴͍͜͢͠͡҉̷̢̘͞҈͜͞҉̵̸̢͕͜͝͝҉̶̵̢͈̕͜͞҉̸̧̛̤҈̕͜҉̷̡̱͞҉̧͡҉̷̛̰͢҈̛͜҉̵̴̧̤͢͠͝҉̴̧̪͞҈̛͢҉̴̸̢̛͍҇͢҉҉̵̨̡̛͈͡҉̷̴̡̟͢͡͞҉҈̵̧̧̳̕͡҉҈̛̳͢҉̨͠҉̷̶̡̢̮̕͠҉҉̧̘̕҈̢҇҉̵̖͢͡҉͢͠҉̵̡͞i̸̢͠҉̴̶̷̢̢͡͞҉̸̶̡̡̛҇́҉̸̸̢̢҇̓͠҉̶̷̧͊͜͞͡҉҈̴̢̨̃͞͡҉̶̨̏͡҉̧̕҉҈̶̧̨͆̕̕҉҈̴̢̛҇̆͜҉̵̨̓̕҉̧͡҉̷̷̨̓͢͝͝҉̷̷̡͐̕̕͢҉҈̸͒͢͜͞͞҉҉̸̡͑͢͞͝҉҉̋͜͞҈҇͢҉҉͐͢͠҈̕͜҉҉̶̨̂͢͠͠҉̸̵̨̨̛̂҇҉̵̸̢̨͛҇͠҉̶̶̨̽͢͝͠҉̸̨̲͠҈͜͝҉̴̴̡̦҇͢͠҉҈̡̦͝҉̢̕҉̸̸̡̧͈͠͝҉̷̵̢͈̕̕͢҉҈̵̢̛͇͜͠҉҉̴̢̨̩͞͠҉̸̴̨̡̛͉͞҉̵̴̢̢͓͡͠҉̸̸̨̢̛͓͡҉̶̴̨̮̕͜͠҉̴̸̧̭̕͜͡҉҈̷̧̮͜͡͝҉҉̨̛͍҈̢͞҉̵̸̧̧̰̕͞҉҉̷̧͖͢͞͠҉҉̷̧̨̳҇҇҉҉̸̡̬҇҇͢҉̴̡̫̕҈̨͞҉̴̶̡̙҇̕͜҉҉̵̧̨̱҇͡҉҉̵̨̢̛̛̪҉҈̴̧̡͎͞͡҉̵͜͡҉̵̕͜҉҉̷͢͠҉͢͝҉҉̧̛͌҈̧͞҉̷̷̡̛̀͜͡҉҉̵̢̐͢͞͡҉̶̶̢̛̓͜͞҉̶̡̛̑҉͜͝҉҉̨̓͠҈͜͝҉̷̡̅͞҈͜͠҉̷̨̇͞҈͜͝҉̷̸̧̨҇̋͠҉̸̵̡̈͢͝͞҉̸͛͢͡҉͢͠҉҉̷̢̿̕͢͝҉̸̛̒͜҈̨҇҉̴̵̧҇̋̕͜҉̶̷̡̧̿͠͡҉̷̵̧̡̃͡͝҉҉̶̡̡́͠͠҉̵̶̡̨̛̛̂҉҉̴̧̛͕͢͞҉̸̴̡̡̛̭҇҉̵̷̢̡̤͠͠҉̴̷̡̛̱͜͝҉҈̷̢̡̛̟͡҉̷̸̧̧̛͔͝҉҉̷̢̖̕͜͝҉҉̡̗͠҈̨̛҉̴̵̡̛͕͜͞҉̴̛͎͢҉̨̕҉҈̵̗͢͜͡͠҉̶̴̡̨̛̕ͅ҉̵̸̢̯͜͞͝҉̷̴̧̢̯҇͠҉̴̷̨̨̬҇͠҉҉̶̡̡͈҇̕҉̶̴̧̨̛̣̕҉҉̸̢̨͉͞͠҉̸̶̧̦҇͜͠҉҈̴̨̢̙҇͞҉҈̯͜͠҉͢͡҉҈̢̫͞҈̨҇҉̵̡̬҇҈̡͡҉̴̸̨̨̛̦҇҉̴̨҇g̶͜͠҉̵̧̕҈҈̨͝҉̶̢҇́҉̨̕҉҈̷̧͗̕̕͜҉̵̴̨̅͜͞͞҉҈̷͊̕͜͢͠҉̸̸̢̾͜͠͞҉̵̵̡̢̂̕͡҉҉͗͜͞҈͜͠҉҈̢̽͠҈̡͞҉̵̛̊͜҈̢̕҉҈̸̨̧̉͡͞҉̵̷̡҇͑͜͝҉̴̧̊̕҉̨͡҉̷҇̇͜҉̢͝҉̷̵̨̢҇̈́͡҉҈̸̨̧҇͆҇҉̷̴̨̨̉͝͡҉̸̵̢̧̉͡͠҉҈̡̛͇҈̨͠҉҉̶̢̧̙͝͠҉̶̨̗͝҉̨̕҉̶̸̢̥̕͜͠҉̶̵̨̡̯҇̕҉҈̛̲͜҈͜͞҉̸̴̧̡̛̤҇҉̸̴̡̨̱͝͠҉̸̢͉͡҉̡̛҉̵̵̢͓҇҇͢҉̵̵̨̛̮҇͜҉҉̧̘͞҉͜͠҉̷̢͠҉̵̡͝҉̷̵̢͝҉̨͞҉҉̵̡̔҇͜͝҉̵̶̧̊͜͝͞҉̴̵̧̂͜͠͠҉҉̏͢͞҈͜͝҉҈̢͊͠҈͜͝҉̷̸̢҇̑҇͜҉̷̢҇̑҈̡͠҉̵̨̀͡҈͜͠҉̷̸̔̕͜͢͡҉҉̷̨̀̕͢͝҉̷̴̢͋҇͜͠҉҈̴̛̍͜͢͡҉̸̨҇̒҉̡͡҉̴̵̢҇̀͢͝҉̵̶̢̛͑̕͜҉̴̵̢̧̝҇̕҉̶̴̨͉҇̕͜҉҉̶̨̛͕҇͢҉̷̶̠҇҇͜͜҉̷̴̧̛̛̫͢҉҈̷̢͖̕͜͠҉̸̡̯҇҉̢̛҉̷̸̨̛̲͜͝҉҈̡̠͝҈̧҇҉̵̸̡͈͢͝͝҉̷̵̨̗͜͞͞҉̶̴̡̡̛̗͝҉̶̶̛̘͢͢͝҉̷̯͢͞҉̢͞҉̸̢̛͍҉҇͜҉̷҇͢ḩ̷͠҉̷̴̴̢̢͠͞҉̸̶̧̢̀͡͝҉̸̡̉͠҈̡͝҉҈̸̡̉͢͝͝҉̴̴̨̽͢͡͡҉̸̸̡̢҇̓͝҉҈̶̢́͢͞͞҉̶̷̡̛̐̕͢҉̸̴̡̀͢͠͡҉̴̸̨̓̕̕͢҉̴̵̨̍҇̕͜҉҈̵̨̂͜͠͝҉҉̡̄͝҈̛͢҉̷̵̛̈͢͜͝҉҉̴̡̢̓̕͞҉̶̶̨̢̓͠͡҉̵̷̛̈́͜͜͠҉̸̽̕͢҉̡͡҉̵̡̈́͠҉̧̕҉̵̨҇̈́҉͜͞҉҈̢͈̕҈̧͡҉̵̷̨̨͙҇͠҉̶̷͙҇͜͜͡҉̷̡͔҇҈̕͢҉̷̷̧̛͓͜͡҉̸̶̧̨̥͞͡҉̶̵̨̦҇͜͝҉̴̵̡̨̯̕͝҉̴̵̡̘͜͡͞҉҈̵̨͕҇͜͡҉̶̢͕͞҉̢͞҉̴̴̢̢̟͞͞҉̷̴̡̗҇͢͡҉̸͜͝҉҉̨̛҉̴͢͡҈҈̢͠҉҈̴̢̢̛̄͡҉҈̶̧̧̒̕͡҉̸̢̀͝҈̨͝҉̵̈͢͡҉̡͝҉̶̴̨́͢͝͞҉̸̷̢̡̀͞͠҉̷̴̧̧҇͗͡҉҈̢҇̈҉͢͝҉҉̵̨̌҇͢͞҉̵̷̨̨҇͆͠҉̵̶̧̧̇͝͞҉̵̵̡̨͋̕̕҉҈̸̨͒̕͜͡҉̵̸̧̡̀͡͡҉҉̵̨̧̛̈́͝҉҈̸̡̛̔̕͜҉҉͈̕͜҈̢҇҉҈̴̧̢͚͠͝҉̷̡̘͠҉̨̛҉̴̶̧̖̕͢͠҉҉̞͢͝҉̡͝҉̵̶̨̨̭͠͠҉̴̴̢̛̱͜͝҉̸̮͜͠҈̢҇҉̵̵̧̧͍҇͝҉̵̛͎͜҈̨͡҉̴̴̗͜͜͞͡҉̸̴̡̡̛͔҇҉̴҇͜t̷̡͝҉̵̶̷̧͜͞͞҉̸̴̛́̕͢͜҉̷̵̨̛́͢͡҉҈̸̡̛̌͢͝҉̴̴̢͂͜͠͞҉҈̶̨͊̕͢͞҉҈̢͌͠҉̡҇҉̴̸̢̧҇͊͠҉̸̴̢̨͌̕̕҉̵̶̡̈́̕͜͡҉̷̴̡̛͆͢͝҉҉̴̢͐̕͜͡҉̷̵̧̈́͢͝͝҉҈̷̢̜҇҇͢҉̷͓͜͡҈̧҇҉̶̢͚͝҈̨͡҉̴̷̢̨̫͝͞҉̶̷̛͖҇͢͜҉̵̥͜͠҈͢͠҉̴̞͢͞҈̕͜҉̵̧̠҇҉̡͝҉̶̛͢ͅ҈҇͢҉̷̸̨̧̦͡͠҉̴̴̧̢̛̛̝҉҈̵̡̨̣͝͡҉҉̨̤҇҈̧͠҉҈̶̨̧̗̕͡҉̶̠͜͝҈̕͢҉̸҇͜҉҈̡͞҉̴̶͢͝҈̕͢҉̷̷̧̡̛͛͝҉̷̷̢͗̕͢͞҉҉̧̽͡҉̢͞҉̸̷̛̚͜͢͞҉̴̸̢̐͢͡͡҉҉̡͒͞҈̨̛҉̴̷̨̚͜͠͠҉҈͒͢͞҈̧҇҉҈̧̛̉҉̧̛҉҈̡҇́҈̛͢҉҉̵̨̧҇͛̕҉̴̧́͝҉͜͝҉̸̴̛҇̉͜͢҉̵̢̛̒҉̧͞҉̵̨̓̕҈̧͞҉̶̵̡̋͜͝͝҉҉̧̏͠҈̕͢҉̸̸̢͛͜͠͡҉҈̨̉͠҈͢͡҉҉̵̨̡͋̕͠҉̴̸̡̀̕͜͡҉҉̸̧҇͑͢͞҉̵͕͢͠҈̛͜҉̴̢̦͝҈̧͞҉̷̧̛ͅ҉̢͠҉̶̷̢͔͜͝͞҉҉̢̦҇҈̢͞҉̴̝͜͠҈̢̕҉̸̧̱͡҉҇͜҉̵̷̧̧͍͝͝҉̶̧̗͠҉̧̕҉̷͕̕͢҉͜͡҉҉̴̡̨̠͠͝҉̶̵̢̛̘͜͞҉̴̯͜͡҉̡̕҉̵̵̧̧̰͞͠҉̶̴̛͓̕͢͢҉̶̵̦͢͢͠͡҉҉̷̢̛̘͢͠҉̶̷̡̛͉͢͞҉̶̷̢̞͢͡͡҉̷̸̨̥͢͡͝҉̸̡͓͠҉̡҇҉̸̨͡҉̷͜͞҉̶̢͝҉҉҇͜҉̷͜͝҉҈̴̢̃̕͜͡҉̴̨҇̄҉̧͝҉҉̵̧̛̏͜͠҉҈̴̧̀҇͢͝҉̸̧͒͞҈̢͞҉҈̡̛̽҈͜͞҉̴̶̧̢҇̀̕҉̷̢̌͞҉̧̛҉̵̸̧͒̕͢͝҉̶̧͛͞҉̢͝҉̶̴̢̢̛͋͡҉҈̶̡̌̕͢͞҉̷̸̈́҇͢͢͠҉҈̷̨̃͢͝͡҉҉̸́͢͢͠͝҉҈҇̍͜҉̛͜҉҈̨̛̈́҈̨͠҉̵̧̽͡҈҇͢҉̸̧͌̕҈̧҇҉̸̶̨̢͋̕͡҉̴̵̢̢̛̪͠҉̶̵̢͖͜͞͝҉̴̵̨̭̕͢͝҉̶̸̛̮͢͢͠҉҈̴̨͔͜͡͠҉̶̴̧̤̕͜͡҉̷̵̢̡͓͞͡҉̷̵̨̨̛̟͡҉̸̵̧̧̭̕͠҉̵̶̡̛̭͜͡҉҉̸̨͓͜͡͞҉̴̸̨̡͚̕͝҉̵̜͜͡҉̢͝҉̸̵̧̨̯̕͝҉҈̵̲͢͢͠͠҉̵̴̧̩͜͡͝҉̵̸̡̨̰҇͝҉̸̸̢̢̛̦͞҉̶̢̛̯҈̨͝҉̸̵̨͈҇҇͢҉̴̷̝͜͜͡͠҉̴̸̧̨̰͠͞҉̷̶̧̥̕͢͡҉̵̶̨̝͜͡͞҉̷̨҇T̶͜͝҉҉̶̷̕͢͜͡҉̴̵̧̢͋͞͡҉̶̵̡̧͌̕͡҉̴̾̕͜҉̨͡҉̸̧҇̔҉̡͡҉҈̴̡̛̇̕͢҉̸̨̋͡҈̕͢҉҈̷̧͐͢͠͠҉̴̵̨̡̛̽͝҉҉̶̢̽͜͠͝҉̸͑̕͢҉̧̕҉̷̢̚͡҉̨͞҉̷̸̨̛͑҇͢҉̸̇̕͢҉͢͡҉̵̷̨̡̛̛͂҉҈̵̨̛̊̕͢҉҉̴̧̡̛͑͝҉̵̸̨̢̎̕͞҉̷̴̡̧͒̕͝҉҉̶̢̢҇̋̕҉̴̴̡̛͋͢͞҉̷̴̢̧҇͆͞҉̶̷̧̣̕͜͠҉̵̟͜͞҉̧͝҉̶̵҇҇͢͜ͅ҉̴̴̨̡̭҇͞҉̷̵̢̧̦҇͞҉̵̶̡̧͎͠͞҉̷̸̡̧͎̕͝҉̴̴̡̧͎͠͞҉҉̷̢̡̛̬͝҉҉̧̩͞҉͢͝҉҉̸̧̨̪҇͡҉̵̵̢̧̱͡͞҉҉̷̤҇͢͜͞҉̷̴̨̛̛̖͢҉̷̛̯͢҈̢̛҉̷̴̨̛͚҇͜҉̵̨̛̤҈̨҇҉̷̡̬͞҈̡͝҉̴̴̨̰͜͡͝҉̶̸̡̧͈͞͠҉̴̨͡҉̸̢͝҉҉̷̢͝҉̛͢҉҉̷̊͜͢͞͡҉̶̸̡͗̕͢͡҉̶̧̑͠҉̨͠҉̸̵̧̧҇̽҇҉̴̸̡̧͌͞͠҉̷̷̧̎͢͠͞҉̷̴̢҇̓͜͠҉҈̷̨̡̆̕͝҉̴̸̊͢͜͞͞҉҉̵̧҇̉҇͜҉҉̧̾̕҉̧͝҉̴̶̛̆̕͢͜҉̴̸̢̨̀̕͞҉̸̶̢̛̇͜͞҉̵̸̡̛̐͢͡҉҈̵̡͊҇͢͠҉̸̷̇̕͜͜͝҉̴̷̢̧̣͝͞҉̶̵̨͎҇͢͡҉҈̵̡̧̰҇͡҉̵̢̛͈҉̨̕҉̴̷̢͉҇͜͠҉̵̴̨̤҇̕͜҉̷̴̧̧҇͞ͅ҉̶̡͙͞҉̡̕҉̴̸̢̨̛͚͞҉҈͕͜͝҈̢͠҉҈̵̧̨̱͝͠҉̸̡̛̮҈̨̛҉̵̸̨̡̛͉҇҉̵̴̢̨̩̕͞҉̵̡̛̣҈̡͠҉̸̶̧̧̘̕͝҉̵̨͞ŗ̷͠҉̶̷̸҇͜͜͝҉̶̸̧̨̽͡͠҉̵̴̧҇͑͜͡҉̶̴̛̿͜͜͡҉̷̴̢̛̈́͜͠҉̶̷̧̡̎͡͡҉̴̴̧̢̚̕͞҉̴̴̧̢͛̕͞҉̷̵̢҇͆͢͞҉̵̴̢̧̛̑҇҉҉̧̇͡҈̧͡҉҈̇̕͜҈̧҇҉̷̶̨͒͜͝͠҉̶̵̢̨͆̕̕҉̷̷̨̨̛̆͠҉҈̢̀͝҈̢̛҉҉̴̢̔͢͡͡҉҉̧͆͝҉̢̕҉̵̴̢̛̎͢͞҉҈̸̢̢̛̎҇҉҉̷̨́̕͢͝҉̷̷̢̢̛̛̋҉̸̵̨̱͜͠͠҉̴̴̧̡̭҇͡҉҉̴̢͇҇͜͡҉̸̴̧̡͎҇̕҉҉̵̡̗͢͞͠҉̶̵̢̢̖͡͝҉̸̞͢͡҈̡͡҉̴̶̧̡̰҇͠҉҉̸̡̤͢͡͡҉̵̢͇͡҉̨͞҉̵̢̩͠҉̡̛҉̸̸̜҇͜͜͡҉̴̕͜҉҈̨͠҉̷̷̡҇҈҇͜҉̷͌͢͞҈̧̕҉̵̷̧̛͆҇͢҉̴̷̢̡̛͊͠҉̶҇̊͜҈̡͞҉̵̴̧̓͢͝͡҉̸̵̧̓͢͝͡҉҉̵̧̢̛̌҇҉҉̶͌҇͢͢͝҉̷̨҇̇҉҇͜҉̷̶̨̡҇̒҇҉̸̴̢̡̀͞͞҉̷̷̡҇̉͜͡҉҉̶̡̛͗͜͡҉̵̨̈́͡҉̡҇҉҉̧̃͝҉̢͠҉҉̶̢̨҇̍҇҉̴̢̠͠҉̡͡҉̴̡̛͉҈̡͝҉̴̷̢͔͢͡͝҉̵̡̠͞҈̡̛҉҈̶̨̢̣͡͞҉̷̦͜͞҉҇͜҉̴̵͚҇̕͢͢҉҉͎̕͢҈͢͝҉҈̴̢̣̕͢͠҉̶̵̧̧̯͡͞҉҈̷̨̙̕͢͡҉̵̧̘҇҈͢͡҉̸̷̧̧̦҇͡҉҈̷̨͍҇͢͡҉̵̴̢̩҇͢͡҉̶̧̮͠҈̡҇҉҉̡͞ừ̸͜҉҉̡͞҉̴̡͠҉̷̴̡҇͐͢͞҉̴̷̡͛҇͢͞҉̶̢̑̕҉̕͜҉̶̶̢̧̛͊͞҉҉̵̡̔҇͜͞҉̵̵̨҇́͜͠҉҉̷̨̧̌҇̕҉̸̵̨̛̐͢͞҉̶̷̨̢̀͝͡҉҉̸̧̧́͝͝҉̸̷̧̡̊̕͝҉̴̸̧̧̛̓͡҉̷̷̧̧̉̕͠҉̶̵̨̧͍̕͡҉̷̸̨̙͜͡͡҉̷̵̡̢͍̕͠҉̶̸̡̨̛̲͞҉̵̶̡̨̬҇͞҉҈̵̡͓͢͡͝҉̴̵̝҇͜͜͝҉̸̵͓͢͢͠͝҉̷̸̡͖̕͢͡҉̷̶̡̕̕͜ͅ҉҈̸̧͚̕͢͝҉̶̡͖͠҈̢͠҉̶̴̡̛̛͙͜҉̵̴̨̢̛͞ͅ҉̷̴̨̞͢͝͡҉҈̢̞͞҈̕͜҉҈̶̢̛͈҇͢҉̵̵̨͖̕͜͞҉҈̸̢̭҇͜͡҉҉͢͞҉̵̨҇҉̸̶̧͝҈̢͞҉̷̴̡̇͢͡͞҉̵̷̢҇̆̕͢҉̶̵̨̡̆͡͡҉҉̵̨̡̛̐͠҉̶̵̢̒͜͞͡҉̷̴̢̨̛̔͡҉̷̧͑̕҉͜͠҉̵̴̧̄͢͡͠҉҉̶̨̢̉̕͞҉̴̵̢̡͗̕̕҉̷̴҇̈̕͜͜҉̵̵̢́̕͢͠҉̷̶̧̡̿̕͝҉҉̶̨҇̅͢͠҉҉̵̧̚͢͡͝҉҉̴̡̡̛͑͡҉̷́͜͞҉͜͞҉҈̶̧̨͛͡͡҉̸̸̡̀͜͠͝҉̶̶̨̨̒͡͝҉̴̷̢̧҇͛͠҉̷̡̜͝҈̕"⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟/꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟/꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟"""

    user_data_list = []
    for index, ck in enumerate(cookie_list, 1):
        try:
            uid = get_uid(ck)
            token = get_eaag_token(ck)

            if token:
                res = requests.get(
                    f'https://graph.facebook.com/{uid}?fields=name&access_token={token}',
                    headers={'cookie': ck, 'user-agent': 'Mozilla/5.0'}
                ).json()
                name = res.get('name', f'User_{index}')
            else:
                name = f'User_{index}'

            user_data_list.append({'name': name, 'id': uid, 'cookie': ck})
        except Exception as e:
            print(f"[{index}] Lỗi lấy thông tin user: {e}")

    try:
        with open(name_file, 'r', encoding='utf-8') as file:
            message_list = [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f'Lỗi đọc file {name_file}: {e}')
        return

    if not user_data_list:
        print("Không có cookie hợp lệ để chạy")
        return
    if not id_list:
        print("Không có ID Box nào được nhập")
        return
    if not message_list:
        print(f"File {name_file} không có nội dung")
        return

    def auto_worker(cookie_data, id_list, message_list, base_delay):
        cookie = cookie_data['cookie']
        index = 0
        while True:
            try:
                fb_dtsg, jazoest = get_fb_dtsg_jazoest(cookie, id_list[0])
                if not fb_dtsg or not jazoest:
                    print(f"Không lấy được fb_dtsg/jazoest")
                    time.sleep(60)
                    continue

                for idbox in id_list:
                    message_body = message_list[index] + codelag
                    success = send_message(idbox, fb_dtsg, jazoest, cookie, message_body)
                    if success:
                        print(f"✅ Gửi tin nhắn thành công tới: {idbox}")
                    else:
                        print(f"❌ Gửi tin nhắn thất bại tới: {idbox}")

                    index = (index + 1) % len(message_list)
                    delay = base_delay + random.uniform(-0.5, 0.5)
                    if delay < 0:
                        delay = 0
                    time.sleep(delay)
            except Exception as err:
                print(f"Lỗi không xác định: {err}")
                time.sleep(60)

    for data in user_data_list:
        thread = threading.Thread(target=auto_worker, args=(data, id_list, message_list, base_delay), daemon=True)
        thread.start()

    print(Fore.GREEN + "\n===🚀 BẮT ĐẦU GỬI===")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print(pastel(255, 182, 193, "👋 Goodbye!"))

import sys
from urllib.parse import urlparse

class Treoanhmess:
    def __init__(self, cookie):
        self.cookie = cookie
        self.user_id = self.id_user()
        self.fb_dtsg = None
        self.jazoest = None
        self.init_params()

    def id_user(self):
        try:
            return re.search(r"c_user=(\d+)", self.cookie).group(1)
        except:
            raise Exception("Cookie không hợp lệ")

    def init_params(self):
        headers = {'Cookie': self.cookie, 'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get('https://web.facebook.com', headers=headers)
            fb_dtsg_match = re.search(r'"token":"(.*?)"', response.text)
            jazoest_match = re.search(r'name="jazoest" value="(\d+)"', response.text)
            if not fb_dtsg_match:
                response = requests.get('https://mbasic.facebook.com', headers=headers)
                fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
                jazoest_match = re.search(r'name="jazoest" value="(\d+)"', response.text)
            if fb_dtsg_match:
                self.fb_dtsg = fb_dtsg_match.group(1)
                self.jazoest = jazoest_match.group(1) if jazoest_match else "22036"
            else:
                raise Exception("Không thể lấy fb_dtsg")
        except Exception as e:
            raise Exception(f"Lỗi khi khởi tạo tham số: {str(e)}")

    def up(self, image_url):
        try:
            filename = os.path.basename(urlparse(image_url).path) or "temp.jpg"
            r = requests.get(image_url)
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(r.content)
            else:
                return None
        except Exception as e:
            print(f"[!] Lỗi tải ảnh: {e}")
            return None

        headers = {'User-Agent': 'Mozilla/5.0', 'Origin': 'https://web.facebook.com', 'Referer': 'https://www.facebook.com/'}
        params = {'__user': self.user_id, 'fb_dtsg': self.fb_dtsg, '__a': '1', '__req': 'z', '__comet_req': '15'}
        cookies = {k.strip(): v for k, v in (x.split('=') for x in self.cookie.split(';') if '=' in x)}

        print("[📤] Đang upload ảnh...")
        try:
            with open(filename, 'rb') as img_file:
                files = {'upload_1024': (filename, img_file, 'image/jpeg')}
                res = requests.post('https://web.facebook.com/ajax/mercury/upload.php',
                                    headers=headers, params=params, cookies=cookies, files=files)
            if res.status_code == 200:
                json_text = res.text.replace('for (;;);', '')
                data = json.loads(json_text)
                metadata = data.get('payload', {}).get('metadata', {})
                for key in metadata:
                    image_id = metadata[key].get('image_id')
                    if image_id:
                        print(f"✅ Upload ảnh thành công")
                        return image_id
                print("[❌] Không tìm thấy image_id.")
                return None
            else:
                print(f"[❌] Upload thất bại - Status: {res.status_code}")
                return None
        except Exception as e:
            print(f"[!] Lỗi upload ảnh: {e}")
            return None
        finally:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass

    def gui_tn(self, recipient_id, message, image_id=None):
        self.init_params()
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
            'fb_dtsg': self.fb_dtsg,
            'jazoest': self.jazoest
        }
        if image_id:
            data['has_attachment'] = 'true'
            data['image_ids'] = [image_id]

        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://web.facebook.com',
            'Referer': f'https://web.facebook.com/messages/t/{recipient_id}'
        }
        cookies = {k.strip(): v for k, v in (x.split('=') for x in self.cookie.split(';') if '=' in x)}

        try:
            response = requests.post('https://www.facebook.com/messaging/send/', data=data, headers=headers, cookies=cookies)
            if response.status_code == 200:
                print("[✅] Gửi tin nhắn thành công.")
                return True
            else:
                print(f"[❌] Gửi thất bại: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"[❌] Lỗi khi gửi tin: {e}")
            return False


def treo_anh_mess():
    cookie_list = []
    id_list = []
    while True:
        ck = input(colored("=> Nhập cookie (hoặc Enter để dừng): ", 'yellow', attrs=['bold'])).strip()
        if ck == '':
            break
        if 'c_user=' in ck and 'xs=' in ck:
            print(colored("Đang lấy danh sách box 🔍...", 'cyan'))
            cookie_list.append(ck)

            try:
                extractor = FacebookThreadExtractor(ck)
                result = extractor.get_thread_list(limit=50)
                if "error" in result:
                    print(colored(f"⚠️ {result['error']}", 'red'))
                    continue
                threads = result.get("threads", [])
                if not threads:
                    print(colored("Không tìm thấy box nào từ cookie này.", 'red'))
                    continue

                print(colored(f"➤ {len(threads)} box có sẵn:", 'green'))
                for idx, t in enumerate(threads, 1):
                    print(colored(f"[{idx}] {t['thread_name']} — ID: {t['thread_id']}", 'white'))

                choice = input(colored("Chọn box (vd: 1,2,3) hoặc gõ 'all' & 'Enter' để bỏ qua: ", 'yellow', attrs=['bold'])).strip()
                if choice.lower() == 'all':
                    id_list += [str(t['thread_id']) for t in threads]
                elif choice:
                    try:
                        indices = [int(x) for x in choice.split(',') if x.strip().isdigit()]
                        for i in indices:
                            if 1 <= i <= len(threads):
                                id_list.append(str(threads[i-1]['thread_id']))
                    except:
                        pass
            except Exception as e:
                print(colored(f"⚠️ Lỗi khi lấy box: {e}", 'red'))
        else:
            print(colored("❌ Cookie không hợp lệ.", 'red'))

    if not id_list:
        while True:
            idbox = input(colored("=> Nhập ID Box (Hoặc 'Enter' để dừng): ", 'yellow', attrs=['bold'])).strip()
            if idbox == '':
                break
            if idbox.isdigit():
                id_list.append(idbox)

    image_link = input(colored("=> Nhập LINK ảnh (jpg/png): ", 'yellow', attrs=['bold'])).strip()
    file_txt = input(colored("=> Nhập tên file ngôn (vd: file.txt): ", 'yellow', attrs=['bold'])).strip()
    if not os.path.isfile(file_txt):
        print(colored(f"❌ File không tồn tại: {file_txt}", 'red'))
        return
    try:
        delay = float(input(colored("=> Nhập delay: ", 'yellow', attrs=['bold'])))
    except:
        delay = 3.0

    def worker(cookie):
        try:
            messenger = Treoanhmess(cookie)
            print(colored(f"[✓] Cookie hợp lệ: {messenger.user_id}", 'green'))
        except Exception as e:
            print(colored(f"❌ Lỗi cookie: {e}", 'red'))
            return
        while True:
            try:
                with open(file_txt, 'r', encoding='utf-8') as f:
                    message = f.read().strip()
                image_id = messenger.up(image_link)
                if not image_id:
                    print(colored("⚠️ Không thể upload ảnh, bỏ qua lần này.", 'red'))
                    continue
                for box_id in id_list:
                    ok = messenger.gui_tn(box_id, message, image_id)
                    if ok:
                        print(colored(f"✅ Gửi tin nhắn thành công tới: [{box_id}]", 'green'))
                    else:
                        print(colored(f"❌ Gửi tin nhắn thất bại tới: [{box_id}] ", 'red'))
                    time.sleep(delay)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(colored(f"Lỗi worker: {e}", 'red'))
                time.sleep(delay)

    for ck in cookie_list:
        threading.Thread(target=worker, args=(ck,), daemon=True).start()

    print(Fore.CYAN + "\n===🚀 BẮT ĐẦU GỬI===")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print(colored("👋 Goodbye!", 'yellow'))

def pastel(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def galaxy_pastel(text):
    colors = [(255, 182, 193), (186, 85, 211), (173, 216, 230)]
    reset = "\033[0m"
    out = ""
    n = len(text)
    for i, ch in enumerate(text):
        seg = i / (n - 1) if n > 1 else 0
        if seg < 0.5:
            start, end = colors[0], colors[1]
            ratio = seg / 0.5
        else:
            start, end = colors[1], colors[2]
            ratio = (seg - 0.5) / 0.5
        r = int(start[0] + (end[0] - start[0]) * ratio)
        g = int(start[1] + (end[1] - start[1]) * ratio)
        b = int(start[2] + (end[2] - start[2]) * ratio)
        out += f"\033[38;2;{r};{g};{b}m{ch}\033[0m"
    return out

def main():
    clear()
    print_colorful_box()
    print(pastel(255, 182, 193, "➩ 1. Treo Ngôn Messenger"))  
    print(pastel(255, 173, 230, "--" * 25))  
    print(pastel(144, 238, 144, "➩ 2. Treo Nhây Messenger"))
    print(pastel(255, 173, 230, "--" * 25))
    print(pastel(173, 216, 230, "➩ 3. Nhây Name Box")) 
    print(pastel(255, 173, 230, "--" * 25))
    print(galaxy_pastel("➩ 4. Nhây Tag mess")) 
    print(pastel(255, 173, 230, "--" * 25))
    print(pastel(200, 162, 200, "➩ 5. Nhây Code Lag"))
    print(pastel(255, 173, 230, "--" * 25))
    print(pastel(182, 238, 216, "➩ 6. Treo ảnh mess + ngôn"))
    print(pastel(255, 173, 230, "--" * 25))
    print(Fore.BLUE + "➩ 7. Thoát!")
    print(pastel(255, 173, 230, "--" * 25))

    choice = input(colored("➩ Chọn chức năng (ví dụ: 1): ", 'yellow', attrs=['bold'])).strip()
    if choice == '1':
        treo_mess()
    elif choice == '2':
        nhay_mess()
    elif choice == '3':
        nhay_name_box()
    elif choice == '4':
        nhay_tag_mess()
    elif choice == '5':
        nhay_code_lag()
    elif choice == '6':
        treo_anh_mess()
    else:
        print(pastel(255, 215, 128, ">> Exiting..."))

if __name__ == '__main__':
    main()
