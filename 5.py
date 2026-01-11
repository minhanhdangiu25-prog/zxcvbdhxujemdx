import os
import sys
import time
import json
import random
import hashlib
import re
import threading
from datetime import datetime
import requests
from urllib.parse import urlparse
import paho.mqtt.client as mqtt
import pyfiglet
from termcolor import colored

def install(package):
    try:
        __import__(package)
    except ImportError:
        os.system(f"{sys.executable} -m pip install {package}")

install("requests")
install("paho.mqtt.client")
install("pyfiglet")
install("termcolor")

class Counter:
    def __init__(self, initial_value=0):
        self.value = initial_value
        
    def increment(self):
        self.value += 1
        return self.value
        
    @property
    def counter(self):
        return self.value

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    ascii_banner = pyfiglet.figlet_format("  Namanh", font="slant")
    print(colored(ascii_banner, 'cyan', attrs=['bold']))
    print("=" * 60)
    print(colored("       Tool treo sớ đa cookie by Cte Vcl 🧸", 'white', attrs=['bold']))
    print("=" * 60)

def parse_cookie_string(cookie_string):
    cookie_dict = {}
    cookies = cookie_string.split(";")
    for cookie in cookies:
        if "=" in cookie:
            key, value = cookie.strip().split("=", 1)
            cookie_dict[key] = value
    return cookie_dict

def generate_offline_threading_id() -> str:
    ret = int(time.time() * 1000)
    value = random.randint(0, 4294967295)
    binary_str = format(value, "022b")[-22:]
    msgs = bin(ret)[2:] + binary_str
    return str(int(msgs, 2))

def str_base(number, base):
    def digitToChar(digit):
        if digit < 10:
            return str(digit)
        return chr(ord('a') + digit - 10)
    
    if number < 0:
        return "-" + str_base(-number, base)
    (d, m) = divmod(number, base)
    if d > 0:
        return str_base(d, base) + digitToChar(m)
    return digitToChar(m)

def generate_session_id():
    return random.randint(1, 2 ** 53)

def generate_client_id():
    import string
    def gen(length):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return gen(8) + '-' + gen(4) + '-' + gen(4) + '-' + gen(4) + '-' + gen(12)

def json_minimal(data):
    return json.dumps(data, separators=(",", ":"))

class fbTools:
    def __init__(self, dataFB, threadID="0"):
        self.threadID = threadID
        self.dataGet = None
        self.dataFB = dataFB
        self.ProcessingTime = None
        self.last_seq_id = None

    def formAll(self, dataFB, FBApiReqFriendlyName=None, docID=None, requireGraphql=None):
        if '_req_counter' not in globals():
            global _req_counter
            _req_counter = Counter(0)
        
        __reg = _req_counter.increment()
        dataForm = {}
        
        if requireGraphql is None:
            dataForm["fb_dtsg"] = dataFB["fb_dtsg"]
            dataForm["jazoest"] = dataFB["jazoest"]
            dataForm["__a"] = 1
            dataForm["__user"] = str(dataFB["FacebookID"])
            dataForm["__req"] = str_base(__reg, 36) 
            dataForm["__rev"] = dataFB["clientRevision"]
            dataForm["av"] = dataFB["FacebookID"]
            dataForm["fb_api_caller_class"] = "RelayModern"
            dataForm["fb_api_req_friendly_name"] = FBApiReqFriendlyName
            dataForm["server_timestamps"] = "true"
            dataForm["doc_id"] = str(docID)
        else:
            dataForm["fb_dtsg"] = dataFB["fb_dtsg"]
            dataForm["jazoest"] = dataFB["jazoest"]
            dataForm["__a"] = 1
            dataForm["__user"] = str(dataFB["FacebookID"])
            dataForm["__req"] = str_base(__reg, 36) 
            dataForm["__rev"] = dataFB["clientRevision"]
            dataForm["av"] = dataFB["FacebookID"]

        return dataForm

    def getAllThreadList(self):
        randomNumber = str(int(format(int(time.time() * 1000), "b") + ("0000000000000000000000" + format(int(random.random() * 4294967295), "b"))[-22:], 2))
        dataForm = self.formAll(self.dataFB, requireGraphql=0)

        dataForm["queries"] = json.dumps({
            "o0": {
                "doc_id": "3336396659757871",
                "query_params": {
                    "limit": 20,
                    "before": None,
                    "tags": ["INBOX"],
                    "includeDeliveryReceipts": False,
                    "includeSeqID": True,
                }
            }
        })
        
        headers = {
            "authority": "www.facebook.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,vi;q=0.8",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www.facebook.com",
            "referer": "https://www.facebook.com/",
            "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "x-fb-friendly-name": "FriendingCometFriendRequestsRootQueryRelayPreloader",
            "x-fb-lsd": "YCb7tYCGWDI6JLU5Aexa1-"
        }

        sendRequests = requests.post(
            "https://www.facebook.com/api/graphqlbatch/",
            data=dataForm,
            headers=headers,
            cookies=parse_cookie_string(self.dataFB["cookieFacebook"]),
            timeout=10
        )
        response_text = sendRequests.text
        self.ProcessingTime = sendRequests.elapsed.total_seconds()
        
        if response_text.startswith("for(;;);"):
            response_text = response_text[9:]
        
        if not response_text.strip():
            print("Error: Empty response from Facebook API")
            return False
            
        try:
            response_parts = response_text.split("\n")
            first_part = response_parts[0]
            
            if first_part.strip():
                response_data = json.loads(first_part)
                self.dataGet = first_part
                
                if "o0" in response_data and "data" in response_data["o0"] and "viewer" in response_data["o0"]["data"] and "message_threads" in response_data["o0"]["data"]["viewer"]:
                    self.last_seq_id = response_data["o0"]["data"]["viewer"]["message_threads"]["sync_sequence_id"]
                    return True
                else:
                    print("Error: Expected fields not found in response")
                    return False
            else:
                print("Error: Empty first part of response")
                return False
                
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Response first part: {response_parts[0][:100]}")
            return False
        except KeyError as e:
            print(f"Key Error: {e}")
            print("The expected data structure wasn't found in the response")
            return False

class MessageSender:
    def __init__(self, fbt, dataFB, fb_instance):
        self.fbt = fbt
        self.dataFB = dataFB
        self.fb_instance = fb_instance
        self.mqtt = None
        self.ws_req_number = 0
        self.ws_task_number = 0
        self.syncToken = None
        self.lastSeqID = None
        self.req_callbacks = {}
        self.cookie_hash = hashlib.md5(dataFB['cookieFacebook'].encode()).hexdigest()
        self.connect_attempts = 0
        self.last_cleanup = time.time()
        self.is_running = True

    def cleanup_memory(self):
        current_time = time.time()
        if current_time - self.last_cleanup > 3600:
            self.req_callbacks.clear()
            import gc
            gc.collect()
            self.last_cleanup = current_time

    def get_last_seq_id(self):
        success = self.fbt.getAllThreadList()
        if success:
            self.lastSeqID = self.fbt.last_seq_id
            return True
        else:
            return False

    def connect_mqtt(self):
        import ssl
        from urllib.parse import urlparse
        
        if not self.lastSeqID:
            print(colored("Error: No last_seq_id Available. Cannot Connect To MQTT.", 'red'))
            return False

        chat_on = json_minimal(True)
        session_id = generate_session_id()
        user = {
            "u": self.dataFB["FacebookID"],
            "s": session_id,
            "chat_on": chat_on,
            "fg": False,
            "d": generate_client_id(),
            "ct": "websocket",
            "aid": 219994525426954,
            "mqtt_sid": "",
            "cp": 3,
            "ecp": 10,
            "st": ["/t_ms", "/messenger_sync_get_diffs", "/messenger_sync_create_queue"],
            "pm": [],
            "dc": "",
            "no_auto_fg": True,
            "gas": None,
            "pack": [],
        }

        host = f"wss://edge-chat.messenger.com/chat?region=eag&sid={session_id}"
        options = {
            "client_id": "mqttwsclient",
            "username": json_minimal(user),
            "clean": True,
            "ws_options": {
                "headers": {
                    "Cookie": self.dataFB['cookieFacebook'],
                    "Origin": "https://www.messenger.com",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-G973U Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36",
                    "Referer": "https://www.messenger.com/",
                    "Host": "edge-chat.messenger.com",
                },
            },
            "keepalive": 10,
        }

        self.mqtt = mqtt.Client(
            client_id="mqttwsclient",
            clean_session=True,
            protocol=mqtt.MQTTv31,
            transport="websockets",
        )

        self.mqtt.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
        self.mqtt.username_pw_set(username=options["username"])

        parsed_host = urlparse(host)
        self.mqtt.ws_set_options(
            path=f"{parsed_host.path}?{parsed_host.query}",
            headers=options["ws_options"]["headers"],
        )

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                topics = [("/t_ms", 0)]
                client.subscribe(topics)

                queue = {
                    "sync_api_version": 10,
                    "max_deltas_able_to_process": 1000,
                    "delta_batch_size": 500,
                    "encoding": "JSON",
                    "entity_fbid": self.dataFB['FacebookID']
                }

                if self.syncToken is None:
                    topic = "/messenger_sync_create_queue"
                    queue["initial_titan_sequence_id"] = self.lastSeqID
                    queue["device_params"] = None
                else:
                    topic = "/messenger_sync_get_diffs"
                    queue["last_seq_id"] = self.lastSeqID
                    queue["sync_token"] = self.syncToken

                client.publish(
                    topic,
                    json_minimal(queue),
                    qos=1,
                    retain=False,
                )
            else:
                pass

        self.mqtt.on_connect = on_connect

        try:
            self.mqtt.connect(
                host="edge-chat.messenger.com",
                port=443,
                keepalive=options["keepalive"],
            )

            self.mqtt.loop_start()
            time.sleep(2)
            return True
        except Exception as e:
            return False

    def stop(self):
        self.is_running = False
        if self.mqtt:
            try:
                self.mqtt.disconnect()
                self.mqtt.loop_stop()
            except:
                pass
        self.cleanup_memory()

    def sendTypingIndicatorMqtt(self, isTyping, thread_id):
        if self.mqtt is None:
            return False

        self.cleanup_memory()

        self.ws_req_number += 1
        label = '3'
        is_group_thread = 1
        attribution = 0

        task_payload = {
            "thread_key": thread_id,
            "is_group_thread": is_group_thread,
            "is_typing": 1 if isTyping else 0,
            "attribution": attribution,
        }

        content = {
            "app_id": "2220391788200892",
            "payload": json.dumps({
                "label": label,
                "payload": json.dumps(task_payload, separators=(",", ":")),
                "version": "25393437286970779",
            }, separators=(",", ":")),
            "request_id": self.ws_req_number,
            "type": 4,
        }

        try:
            self.mqtt.publish(
                topic="/ls_req",
                payload=json.dumps(content, separators=(",", ":")),
                qos=1,
                retain=False,
            )
            return True
        except Exception as e:
            return False

    def send_message(self, text=None, thread_id=None):
        if self.mqtt is None:
            return False

        if thread_id is None:
            return False

        if text is None:
            return False

        self.cleanup_memory()

        self.ws_req_number += 1
        content = {
            "app_id": "2220391788200892",
            "payload": {
                "data_trace_id": None,
                "epoch_id": int(generate_offline_threading_id()),
                "tasks": [],
                "version_id": "7545284305482586",
            },
            "request_id": self.ws_req_number,
            "type": 3,
        }

        text = str(text) if text is not None else ""
        if len(text) > 0:
            self.ws_task_number += 1
            task_payload = {
                "initiating_source": 0,
                "multitab_env": 0,
                "otid": generate_offline_threading_id(),
                "send_type": 1,
                "skip_url_preview_gen": 0,
                "source": 0,
                "sync_group": 1,
                "text": text,
                "text_has_links": 0,
                "thread_id": int(thread_id),
            }

            task = {
                "failure_count": None,
                "label": "46",
                "payload": json.dumps(task_payload, separators=(",", ":")),
                "queue_name": str(thread_id),
                "task_id": self.ws_task_number,
            }

            content["payload"]["tasks"].append(task)

        self.ws_task_number += 1
        task_mark_payload = {
            "last_read_watermark_ts": int(time.time() * 1000),
            "sync_group": 1,
            "thread_id": int(thread_id),
        }

        task_mark = {
            "failure_count": None,
            "label": "21",
            "payload": json.dumps(task_mark_payload, separators=(",", ":")),
            "queue_name": str(thread_id),
            "task_id": self.ws_task_number,
        }

        content["payload"]["tasks"].append(task_mark)

        content["payload"] = json.dumps(content["payload"], separators=(",", ":"))

        try:
            self.mqtt.publish(
                topic="/ls_req",
                payload=json.dumps(content, separators=(",", ":")),
                qos=1,
                retain=False,
            )
            return True
        except Exception as e:
            return False

    def send_message_with_tag(self, text=None, thread_id=None, tag_uid=None, tag_name=None):
        """Gửi tin nhắn với tag người dùng"""
        if text is None or thread_id is None:
            return False
        
        # Thêm tag vào tin nhắn
        if tag_uid and tag_name:
            tagged_message = f"{text} *@{tag_name}*"
        else:
            tagged_message = text
            
        return self.send_message(tagged_message, thread_id)

class Anhnguyencoder:
    def __init__(self, cookie):
        self.cookie = cookie
        self.user_id = self.id_user()
        self.fb_dtsg = None
        self.jazoest = None
        self.rev = None
        self.init_params()

    def id_user(self):
        try:
            match = re.search(r"c_user=(\d+)", self.cookie)
            if not match:
                raise Exception("Cookie không hợp lệ")
            return match.group(1)
        except Exception as e:
            raise Exception(f"Lỗi khi lấy user_id: {str(e)}")

    def init_params(self):
        headers = {
            'Cookie': self.cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        urls = [
            'https://www.facebook.com',
            'https://mbasic.facebook.com',
            'https://m.facebook.com'
        ]

        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code != 200:
                    continue

                fb_dtsg_patterns = [
                    r'"token":"(.*?)"',
                    r'name="fb_dtsg" value="(.*?)"',
                    r'"fb_dtsg":"(.*?)"',
                    r'fb_dtsg=([^&"]+)'
                ]
                jazoest_pattern = r'name="jazoest" value="(\d+)"'
                rev_pattern = r'"__rev":"(\d+)"'

                fb_dtsg = None
                for pattern in fb_dtsg_patterns:
                    match = re.search(pattern, response.text)
                    if match:
                        fb_dtsg = match.group(1)
                        break

                jazoest_match = re.search(jazoest_pattern, response.text)
                rev_match = re.search(rev_pattern, response.text)

                if fb_dtsg:
                    self.fb_dtsg = fb_dtsg
                    self.jazoest = jazoest_match.group(1) if jazoest_match else "22036"
                    self.rev = rev_match.group(1) if rev_match else "1015919737"
                    return
            except Exception as e:
                time.sleep(2)

        raise Exception("Không thể lấy được fb_dtsg từ bất kỳ URL nào")

def get_user_info_from_cookie(cookie):
    try:
        uid_match = re.search(r'c_user=(\d+)', cookie)
        if not uid_match:
            return None
        
        uid = uid_match.group(1)
        try:
            headers = {'cookie': cookie, 'user-agent': 'Mozilla/5.0'}
            response = requests.get(f'https://mbasic.facebook.com/profile.php?id={uid}', headers=headers, timeout=10)
            
            name_patterns = [
                r'<title>([^<]+)</title>',
                r'<h1[^>]*>([^<]+)</h1>'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, response.text)
                if match:
                    name = match.group(1).split('|')[0].strip()
                    return {'id': uid, 'name': name}
        except:
            pass
        
        return {'id': uid, 'name': f'User_{uid[:5]}'}
        
    except Exception as e:
        return None

def fetch_user_name(uid, cookie):
    """Lấy tên người dùng để tag (từ file 1.py)"""
    headers = {'User-Agent': 'Mozilla/5.0', 'Cookie': cookie}
    try:
        r = requests.get("https://mbasic.facebook.com/", headers=headers, timeout=10)
    except Exception as e:
        return None

    if r.status_code != 200:
        return None

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

    form = {"ids[0]": uid, "fb_dtsg": fb_dtsg, "__a": a, "__req": req, "__rev": rev}
    headers = {'User-Agent': 'Mozilla/5.0', 'Cookie': cookie, 'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        r = requests.post("https://www.facebook.com/chat/user_info/", headers=headers, data=form, timeout=10)
        txt = r.text
        if txt.startswith("for (;;);"):
            txt = txt[9:]
        data = json.loads(txt)
        if "payload" in data and "profiles" in data["payload"]:
            first = list(data["payload"]["profiles"].keys())[0]
            return data["payload"]["profiles"][first].get("name")
    except Exception:
        pass
    return None

def collect_ids():
    id_list = []
    stt = 1
    while True:
        idbox = input(colored(f">> Nhập ID Box {stt} (Ấn 'enter' để dừng nhập): ", 'yellow', attrs=['bold'])).strip()
        if idbox.lower() in ['', 'enter']:
            if id_list:
                print(colored(f'Đã lưu {len(id_list)} ID Box', 'green'))
                for i, id_ in enumerate(id_list, 1):
                    print(f'  {i}. {id_}')
            else:
                print(colored('Không có ID Box nào được lưu', 'red'))
            break
        
        if idbox.isdigit():
            id_list.append(idbox)
            stt += 1
        else:
            print(colored("ID Box phải là số!", 'red'))
    
    return id_list

def collect_cookies():
    cookie_list = []
    stt = 1
    while True:
        ck = input(colored(f">> Nhập cookie {stt} (Ấn 'enter' để dừng nhập): ", 'yellow', attrs=['bold'])).strip()
        if ck.lower() in ['', 'enter']:
            if cookie_list:
                print(colored(f'Đã lưu {len(cookie_list)} cookie', 'green'))
                for i, c in enumerate(cookie_list, 1):
                    ck_hash = hashlib.md5(c.encode()).hexdigest()[:10]
                    print(f'  {i}. Cookie {ck_hash}...')
            else:
                print(colored('Không có cookie nào được lưu', 'red'))
            break
        
        if 'c_user=' in ck:
            cookie_list.append(ck)
            stt += 1
        else:
            print(colored("Cookie không hợp lệ! Phải có 'c_user='", 'red'))
    
    return cookie_list

def collect_message_files():
    file_list = []
    stt = 1
    while True:
        name_file = input(colored(f">> Nhập file.txt {stt} (Ấn 'enter' để dừng nhập): ", 'yellow', attrs=['bold'])).strip()
        if name_file.lower() in ['', 'enter']:
            if file_list:
                print(colored(f'Đã lưu {len(file_list)} file.txt', 'green'))
                for i, f in enumerate(file_list, 1):
                    if os.path.exists(f):
                        print(f'  {i}. {f} (Tồn tại)')
                    else:
                        print(f'  {i}. {f} (Không tồn tại!)')
            else:
                print(colored('Không có file.txt nào được lưu', 'red'))
            break
        
        if name_file.endswith('.txt'):
            file_list.append(name_file)
            stt += 1
        else:
            print(colored("File phải có đuôi .txt!", 'red'))
    
    return file_list

def collect_tag_info(cookie_list):
    """Thu thập thông tin tag cho mỗi cookie - Phiên bản nhập đa ID tag"""
    print(colored("\n--- NHẬP THÔNG TIN TAG ---", 'yellow', attrs=['bold']))
    
    tag_list = []
    
    for i, cookie in enumerate(cookie_list, 1):
        ck_hash = hashlib.md5(cookie.encode()).hexdigest()[:10]
        print(colored(f"\nCookie {i} (ID: ...{ck_hash}):", 'cyan'))
        
        tag_items = []
        stt = 1
        
        while True:
            tag_uid = input(colored(f">> Nhập UID cần tag {stt} (Ấn 'enter' để dừng nhập): ", 'yellow', attrs=['bold'])).strip()
            
            if tag_uid == '':

                if tag_items:
                    print(colored(f"Cookie {i}: Đã lưu {len(tag_items)} UID tag", 'white'))
                    for j, item in enumerate(tag_items, 1):
                        print(colored(f"    {j}. {item['name']} ({item['uid']})", 'white'))
                else:
                    print(colored(f"Cookie {i}: Không có tag", 'white'))
                break
            elif tag_uid.isdigit():

                tag_name = fetch_user_name(tag_uid, cookie)
                if tag_name:
                    tag_items.append({"uid": tag_uid, "name": tag_name})
                    print(colored(f"+ UID {stt}: {tag_name} ({tag_uid})", 'white'))
                else:

                    custom_name = input(colored(f"Không tìm thấy tên từ UID {tag_uid}. Nhập tên hiển thị (Ấn 'enter' để dừng nhập): ", 'yellow')).strip()
                    if custom_name:
                        tag_name = custom_name
                    else:
                        tag_name = f"User_{tag_uid[:5]}"
                    
                    tag_items.append({"uid": tag_uid, "name": tag_name})
                    print(colored(f"    + UID {stt}: {tag_name} ({tag_uid})", 'green'))
                
                stt += 1
            else:
                print(colored("UID phải là số! Nhập lại hoặc enter để kết thúc", 'red'))
        
        # Lưu thông tin tag cho cookie này
        if tag_items:
            # Nếu có tag, lưu tag đầu tiên làm tag chính, các tag khác trong multiple_tags
            tag_list.append({
                "uid": tag_items[0]["uid"],  # Tag chính (đầu tiên)
                "name": tag_items[0]["name"],
                "multiple_tags": tag_items  # Tất cả các tag
            })
        else:
            tag_list.append({"uid": None, "name": None, "multiple_tags": []})
    
    return tag_list

def run_cookie_thread(cookie, id_list, valid_files, delay, user_info, tag_info, thread_num, all_threads):
    try:
        cookie_hash = hashlib.md5(cookie.encode()).hexdigest()[:10]
        user_display = f"{user_info['name']} ({user_info['id']})" if user_info else f"User_{cookie_hash}"
        
        fb = Anhnguyencoder(cookie)
        
        dataFB = {
            "FacebookID": fb.user_id,
            "fb_dtsg": fb.fb_dtsg,
            "clientRevision": fb.rev,
            "jazoest": fb.jazoest,
            "cookieFacebook": cookie
        }
        
        all_messages = []
        for messages_file in valid_files:
            if os.path.exists(messages_file):
                try:
                    with open(messages_file, 'r', encoding='utf-8') as f:
                        messages = [line.strip() for line in f if line.strip()]
                        all_messages.extend(messages)
                except:
                    pass
        
        if not all_messages:
            default_messages = [
                "sao kia", "manh di ma", "kem ak", "sao kia", "son de", "run ak", "thg an hai", "cay tao ak",
                "cay lam ak", "sao roi nhi", "bat luc ak", "lien tuc de", "tiep de m", "nhay keo k e", "ga vay e",
                "hoc lom ak", "ko slow ma", "speed de", "hai vai l", "m dot ak", "thg oc cut", "chay de",
                "chat le dei", "co len", "mo coi ak", "cay ak", "ccho cayya ak", "oc cac ak", "chay ak em",
                "sua mau dei", "sua le dei", "tk dot", "tk oc dai", "sua le de", "manh kg", "manh ma e",
                "man ma em", "tk dot", "ui mo coi", "sua lej9 dei", "oc loz ak", "tk boai ngu", "son dc kg",
                "oc trau ak", "le ma em", "hot nhay ma", " tk oc dai", "sua manh kg", "m bi ngu ak",
                "sua mau kg", "oc trau ak", "speed em", "le nun ma", "tk dot cut", "bi ngu ak", "son de em",
                "ccho dien", "nhanh vl ma", "tay ma em", "slow ak", "oc boai ak", "tk dot", " bia ngu ak",
                "sua le nun", "phat bieu le", "tk dot nay", "mo coi me ak", "tk ngu", "sao da", "anh man mak",
                "cay akk", "sua mauu", "sloww akk", "le em", "nhanh em", "clmkks", "con cho dien", "sua em",
                "speed ma", "m slow ay", "m slow vl", "anh speed vkl", "le em", "clm ngu ak", "tk ga nay",
                "con loz", "sua le lun em", "clm dot ak", "keo man cai", "man off mxh de", "kg dam ak",
                "tk ngu ren", "cay r ak", "cay cmnr", "m cay ro", "nhanh ti", "le len e", "co de", "sap dc r",
                "co gang em", "bat luc r ak", "ui tk ga", "ga bat luc", "duoi r ak", "moi tay ak", "kakakak",
                "sua le nun", "chill ma", "bth ma em", "m bat on ak", "anh dg chill", "sua manh em",
                "kg dc treo nha", "tay vs bo de", "cn boai", "nao cho ak", "clm", "sua mau de", "ga ak m",
                "slow r ak m", "duoi r ak", "kh nghi ngoi", "lien tuc ma", "lien tuc nun", "chat lien tuc"
            ]
            all_messages = default_messages
            print(colored(f"[*] Thread {thread_num}: Sử dụng tin nhắn mặc định ({len(all_messages)} mẫu)", 'yellow'))

        fbt = fbTools(dataFB)
        sender = MessageSender(fbt, dataFB, fb)
        
        if not sender.get_last_seq_id():
            print(colored(f"[!] Thread {thread_num}: Không thể lấy last_seq_id", 'red'))
            return
        
        if not sender.connect_mqtt():
            print(colored(f"[!] Thread {thread_num}: Không thể kết nối MQTT", 'red'))
            return
        
        time.sleep(2)
        
        print(colored(f"[✓] Thread {thread_num}: {user_display}...", 'green'))
        
        # Hiển thị thông tin tag
        if tag_info.get("multiple_tags"):
            tag_count = len(tag_info["multiple_tags"])
            tag_names = [tag["name"] for tag in tag_info["multiple_tags"][:3]]  # Hiển thị 3 tag đầu
            tag_display = ", ".join(tag_names)
            if tag_count > 3:
                tag_display += f" và {tag_count - 3} người khác"
            print(colored(f"[✓] Thread {thread_num}: Đang tag {tag_display} ({tag_count} người)", 'cyan'))
        elif tag_info["uid"]:
            print(colored(f"[✓] Thread {thread_num}: Đang tag {tag_info['name']} ({tag_info['uid']})", 'cyan'))
        
        message_index = 0
        
        while sender.is_running:
            try:
                for thread_id in id_list:
                    if not sender.is_running:
                        break
                    
                    if message_index >= len(all_messages):
                        message_index = 0
                    message = all_messages[message_index]
                    message_index += 1
                    
                    if not message:
                        continue
                    
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    
                    # Xử lý đa tag
                    if tag_info.get("multiple_tags"):
                        # Nhiều tag
                        tag_count = len(tag_info["multiple_tags"])
                        
                        # Hiển thị thông tin
                        if tag_count <= 3:
                            tag_names = [tag["name"] for tag in tag_info["multiple_tags"]]
                            tag_display = f"Tag {', '.join(tag_names)}"
                        else:
                            tag_display = f"Tag {tag_count} người"
                        
                        print(colored(f"[{timestamp}] Thread {thread_num} -> Box {thread_id} | {tag_display}", 'cyan'))
                        print(colored(f"    Tin nhắn: {message[:50]}...", 'white'))
                        
                        # Fake typing
                        sender.sendTypingIndicatorMqtt(True, thread_id)
                        typing_duration = random.uniform(1, 3)
                        time.sleep(typing_duration)
                        sender.sendTypingIndicatorMqtt(False, thread_id)
                        
                        # Gửi tin nhắn với tất cả tag
                        tagged_message = message
                        for tag_item in tag_info["multiple_tags"]:
                            tagged_message += f" *@{tag_item['name']}*"
                        
                        sender.send_message(tagged_message, thread_id)
                        
                    elif tag_info["uid"]:
                        # 1 tag
                        print(colored(f"[{timestamp}] Thread {thread_num} -> Box {thread_id} | Tag: {tag_info['name']}", 'cyan'))
                        print(colored(f"    Tin nhắn: {message[:50]}...", 'white'))
                        
                        # Fake typing
                        sender.sendTypingIndicatorMqtt(True, thread_id)
                        typing_duration = random.uniform(1, 3)
                        time.sleep(typing_duration)
                        sender.sendTypingIndicatorMqtt(False, thread_id)
                        
                        # Gửi tin nhắn với tag
                        sender.send_message_with_tag(
                            text=message, 
                            thread_id=thread_id,
                            tag_uid=tag_info["uid"],
                            tag_name=tag_info["name"]
                        )
                    else:
                        # Không tag
                        print(colored(f"[{timestamp}] Thread {thread_num} -> Box {thread_id} | Không tag", 'cyan'))
                        print(colored(f"    Tin nhắn: {message[:50]}...", 'white'))
                        
                        # Fake typing
                        sender.sendTypingIndicatorMqtt(True, thread_id)
                        typing_duration = random.uniform(1, 3)
                        time.sleep(typing_duration)
                        sender.sendTypingIndicatorMqtt(False, thread_id)
                        
                        # Gửi tin nhắn không tag
                        sender.send_message(message, thread_id)
                    
                    time.sleep(delay)
                    
            except Exception as e:
                print(colored(f"[!] Thread {thread_num}: Lỗi - {str(e)}", 'red'))
                time.sleep(5)
        
        sender.stop()
        print(colored(f"[*] Thread {thread_num}: Đã dừng", 'yellow'))
        
    except Exception as e:
        print(colored(f"[!] Thread {thread_num}: Lỗi khởi tạo - {str(e)}", 'red'))

def main():
    clear()
    banner()
    
    try:        
        print(colored("--- NHẬP ID BOX ---", 'yellow', attrs=['bold']))
        id_list = collect_ids()
        if not id_list:
            return
        
        print(colored("\n--- NHẬP COOKIE ---", 'yellow', attrs=['bold']))
        cookie_list = collect_cookies()
        if not cookie_list:
            return
        
        print(colored("\n--- NHẬP FILE TIN NHẮN ---", 'yellow', attrs=['bold']))
        file_list = collect_message_files()
        
        valid_files = []
        for file_path in file_list:
            if os.path.exists(file_path):
                valid_files.append(file_path)
            else:
                print(colored(f"[!] File không tồn tại: {file_path}", 'red'))
        
        # Thu thập thông tin tag
        tag_info_list = collect_tag_info(cookie_list)
        
        try:
            delay = float(input(colored("\n>> Nhập delay (giây): ", 'yellow', attrs=['bold'])).strip())
            if delay < 1:
                print(colored("[!] Delay phải lớn hơn hoặc bằng 1 giây", 'red'))
                return
        except ValueError:
            print(colored("[!] Delay phải là số", 'red'))
            return
        
        print(colored("\n[*] Đang lấy thông tin người dùng...", 'yellow'))
        user_info_list = []
        for cookie in cookie_list:
            info = get_user_info_from_cookie(cookie)
            user_info_list.append(info)
        
        print(colored(f"\n{'='*60}", 'cyan'))
        print(colored("=== TỔNG HỢP ===", 'cyan', attrs=['bold']))
        print(colored(f"{'='*60}", 'cyan'))
        print(colored(f"    - Số ID box: {len(id_list)}", 'white'))
        for i, id_ in enumerate(id_list, 1):
            print(colored(f"      {i}. {id_}", 'white'))
        
        print(colored(f"\n   - Số cookie: {len(cookie_list)}", 'white'))
        for i, (cookie, info, tag_info) in enumerate(zip(cookie_list, user_info_list, tag_info_list), 1):
            ck_hash = hashlib.md5(cookie.encode()).hexdigest()[:10]
            user_display = f"{info['name']} ({info['id']})" if info else f"User_{ck_hash}"
            tag_display = f"Tag: {tag_info['name']}" if tag_info["uid"] else "Không tag"
            print(colored(f"      {i}. {user_display} | {tag_display}", 'white'))
        
        if valid_files:
            print(colored(f"\n  - Số file tin nhắn: {len(valid_files)}", 'white'))
            for i, file_path in enumerate(valid_files, 1):
                print(colored(f"      {i}. {file_path}", 'white'))
        else:
            print(colored(f"\n  - Sử dụng tin nhắn mặc định (400+ mẫu)", 'white'))
        
        print(colored(f"\n  - Delay: {delay} giây", 'white'))
        print(colored(f"{'='*60}", 'cyan'))
        
        confirm = input(colored("\n[+] Bắt đầu nhây fake soạn với tag (y/n): ", 'green', attrs=['bold'])).strip().lower()
        if confirm != 'y':
            print(colored("[*] Đã hủy", 'yellow'))
            return
        
        print(colored(f"\n{'='*60}", 'cyan'))
        print(colored("=== BẮT ĐẦU GỬI ===", 'cyan', attrs=['bold']))
        print(colored(f"[*] Đang chạy {len(cookie_list)} cookie", 'yellow'))
        print(colored(f"{'='*60}\n", 'cyan'))
        
        threads = []
        for i, (cookie, user_info, tag_info) in enumerate(zip(cookie_list, user_info_list, tag_info_list), 1):
            thread = threading.Thread(
                target=run_cookie_thread,
                args=(cookie, id_list, valid_files, delay, user_info, tag_info, i, threads),
                daemon=True
            )
            threads.append(thread)
            thread.start()
            time.sleep(1)
        
        print(colored(f"\n[*] Đã khởi động {len(threads)} thread", 'green'))
        print(colored("[*] Đang chạy...", 'yellow'))
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(colored(f"\n\n[*] ĐANG DỪNG TẤT CẢ THREAD...", 'red', attrs=['bold']))
        
        print(colored(f"\n{'='*60}", 'green'))
        print(colored("[✓] ĐÃ DỪNG TẤT CẢ!", 'green', attrs=['bold']))
        print(colored(f"{'='*60}", 'green'))
        
    except KeyboardInterrupt:
        print(colored("\n\n[*] ĐÃ DỪNG CHƯƠNG TRÌNH", 'red', attrs=['bold']))
    except Exception as e:
        print(colored(f"\n[!] Lỗi: {str(e)}", 'red'))

if __name__ == "__main__":
    main()