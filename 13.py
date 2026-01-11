import os
import sys
import time
import json
import threading
import random
import logging
from pyfiglet import figlet_format
from zlapi.models import *
from datetime import datetime
from zlapi import ZaloAPI, ThreadType, Message
from zlapi.models import Mention, MultiMention, MessageStyle, MultiMsgStyle

def show_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = figlet_format("Mdung w Qhung", font="slant")
    print(banner)
    print("Tool Spam pool by Mdung".center(60))
    print("=" * 60)

def parse_cookie_string(cookie_str):
    try:
        cleaned = cookie_str.strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("❌ Cookie không hợp lệ!")
        return None

__VERSION__ = '1.0'
admin_cre = "Manh Dung"
admin_zalo = "Manh Dung W Quang Hung"
func_admin = "Tool attack acc zalo"

def banner():
    banner_text = f"""
{xduong}╔════════════════════════════════════════════════════════════════{end}
{vang}║▂▃▅▇█▓▒░{luc}HƯỚNG DẪN{vang}░▒▓█▇▅▃▂{end}
{vang}║➣ Nhập IMEI và cookie để sử dụng tool
{vang}║➣ Tool sẽ spam nhóm, bạn bè, rời nhóm, chặn và xóa bạn bè, spam report
{vang}║➣ Sau mỗi chu kỳ, tool sẽ nghỉ 5 giây
{vang}║➣ Nếu có lỗi, tool sẽ thử lại tối đa 3 lần
{xduong}╠
{vang}║▂▃▅▇█▓▒░{luc}THÔNG TIN TOOL{vang}░▒▓█▇▅▃▂{end}
{vang}║➣ Version: {luc}{__VERSION__}{end}
{vang}║➣ Author: {luc}{admin_cre}{end}
{vang}║➣ Function: {luc}{func_admin}{end}
{xduong}╚════════════════════════════════════════════════════════════════{end}
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.00125)

# Hàm Tạo màu
xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;37m"
end = '\033[0m'

# Danh sách màu ngẫu nhiên
COLOR_LIST = [
    "#DB342E",  # đỏ
    "#15A85F",  # xanh lá
    "#F27806",  # cam
    "#F7B503",  # vàng
    "#FFFFFF",  # trắng
    "#000000"   # đen
]

UI_WIDTH = 70

class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def draw_box(title, lines, color=Colors.CYAN):
    print(color + "╔" + "═"*50 + "╗")
    print("║ " + title.center(48) + " ║")
    print("╠" + "═"*50 + "╣")
    for line in lines:
        print("║ " + line.ljust(48) + " ║")
    print("╚" + "═"*50 + "╝" + Colors.RESET)

def custom_print(msg):
    print(f"{Colors.YELLOW}{msg}{Colors.RESET}")

def read_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return ""

def read_list_file(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def normalize_ttl_value(ttl):
    if ttl is None:
        return None
    try:
        t = int(ttl)
    except Exception:
        return None
    if t <= 0:
        return None
    if t < 1000:
        return t * 1000
    return t

class Bot(ZaloAPI):
    def __init__(self, imei, cookies, delay, message):
        super().__init__("api_key", "secret_key", imei, cookies)
        self.delay = delay
        self.message = message
        self.threads = {}
        self.lock = threading.Lock()

    def start_spam(self, gid, gtype):
        with self.lock:
            if gid in self.threads:
                log(f"⚠️ Nhóm {gid} đã chạy!", Color.YELLOW)
                return

            stop_event = threading.Event()
            t = threading.Thread(target=self._loop, args=(gid, gtype, stop_event), daemon=True)
            self.threads[gid] = {"t": t, "stop": stop_event}
            t.start()
            log(f"🚀 Bắt đầu treo nhóm {gid}", Color.GREEN)

    def _loop(self, gid, gtype, stop_event):
        while not stop_event.is_set():
            try:
                self.setTyping(gid, gtype)
                time.sleep(3)
                self.send(Message(text=self.message, mention=Mention("-1", len(self.message), 0)),
                          thread_id=gid, thread_type=gtype)
                log(f"💬 Gửi tới {gid}", Color.CYAN)
            except Exception as e:
                log(f"❌ Lỗi: {e}", Color.RED)
            if stop_event.wait(self.delay):
                break

    def stop_spam(self, gid):
        with self.lock:
            if gid in self.threads:
                self.threads[gid]["stop"].set()
                self.threads[gid]["t"].join(timeout=2)
                self.threads.pop(gid, None)
                log(f"🛑 Dừng nhóm {gid}", Color.YELLOW)

    def fetch_groups(self):
        try:
            data = self.fetchAllGroups()
            result = []
            grid_map = getattr(data, "gridVerMap", {}) or getattr(data, "gridInfoMap", {})
            for gid in grid_map.keys():
                try:
                    info = self.fetchGroupInfo(gid)
                    name = info.gridInfoMap[gid].get("name", str(gid))
                except:
                    name = str(gid)
                result.append(type("G", (), {"grid": gid, "name": name})())
            return result
        except Exception as e:
            log(f"❌ Lỗi lấy nhóm: {e}", Color.RED)
            return []

def menu(bot):
    while True:
        print("\n[1] Thêm nhóm treo\n[2] Dừng nhóm\n[3] Quay lại")
        c = input("→ Chọn: ").strip()

        if c == "1":
            imei = input("IMEI: ").strip()
            cookie_input = input("Cookie (JSON): ").strip()
            try:
                cookies = json.loads(cookie_input)
            except:
                log("❌ Cookie sai định dạng JSON!", Color.RED)
                continue

            b2 = Bot(imei, cookies, bot.delay, bot.message)
            groups = b2.fetch_groups()
            for i, g in enumerate(groups, 1):
                print(f"{i}. {g.get('name')} ({g.get('grid')})") 

            s = input("Chọn nhóm (vd: 1,3): ").strip()
            for n in s.split(","):
                try:
                    gid = groups[int(n) - 1].grid
                    b2.start_spam(gid, ThreadType.GROUP)
                    GLOBAL[gid] = b2
                except:
                    pass

        elif c == "2":
            if not GLOBAL:
                log("⚠️ Không có nhóm đang chạy!", Color.YELLOW)
                continue

            for i, gid in enumerate(GLOBAL.keys(), 1):
                print(f"{i}. {gid}")
            s = input("Nhập số nhóm cần dừng (vd: 1,3 hoặc all): ").lower()

            if s == "all":
                for gid, inst in list(GLOBAL.items()):
                    inst.stop_spam(gid)
                    GLOBAL.pop(gid, None)
            else:
                for n in s.split(","):
                    try:
                        i = int(n)
                        gid = list(GLOBAL.keys())[i - 1]
                        GLOBAL[gid].stop_spam(gid)
                        GLOBAL.pop(gid, None)
                    except:
                        pass

        elif c == "3":
            break

def run_mode_treongon():
    imei = input("IMEI: ").strip()
    cookie_input = input("Cookie (JSON): ").strip()

    try:
        cookies = json.loads(cookie_input)
    except:
        log("❌ Cookie sai định dạng JSON!", Color.RED)
        return

    try:
        delay = float(input("Delay (giây): ").strip())
    except:
        log("❌ Delay không hợp lệ!", Color.RED)
        return

    msg_file = input("File chứa nội dung: ").strip()
    try:
        with open(msg_file, "r", encoding="utf-8") as f:
            msg = f.read().strip()
    except Exception as e:
        log(f"❌ Lỗi đọc file: {e}", Color.RED)
        return

    bot = Bot(imei, cookies, delay, msg)
    groups = bot.fetch_groups()

    for i, g in enumerate(groups, 1):
        print(f"{i}. {g.get('name')} ({g.get('grid')})")

    s = input("Chọn nhóm muốn treo (vd: 1,3): ").strip()
    for n in s.split(","):
        try:
            gid = groups[int(n) - 1].grid
            bot.start_spam(gid, ThreadType.GROUP)
            GLOBAL[gid] = bot
        except:
            pass

    print("✅ Đang treo ngôn...")

    while True:
        cmd = input("\nNhập 'menu' để mở menu hoặc 'exit' để thoát: ").lower()
        if cmd == "menu":
            menu(bot)
        elif cmd == "exit":
            for gid, inst in list(GLOBAL.items()):
                inst.stop_spam(gid)
                GLOBAL.pop(gid, None)
            log("👋 Thoát!", Color.YELLOW)
            break


GLOBAL = {}

class TagClient(ZaloAPI):
    def __init__(self, imei=None, session_cookies=None, label=None):
        super().__init__("dummy_api_key", "dummy_secret_key", imei, session_cookies)
        self.label = label or "NoLabel"
        self.running = threading.Event()
        self.running.clear()

    def fetch_groups(self):
        try:
            all_groups = self.fetchAllGroups()
            group_list = []
            for group_id, _ in all_groups.gridVerMap.items():
                ginfo = super().fetchGroupInfo(group_id)
                gname = ginfo.gridInfoMap[group_id]["name"] if gid_in_ginfo(ginfo, group_id) else f"Group_{group_id}"
                group_list.append({'id': group_id, 'name': gname})
            return group_list
        except Exception as e:
            print(f"[{self.label}] ❌ Lỗi khi lấy danh sách nhóm: {e}")
            return []

    def fetch_group_members(self, group_id):
        try:
            ginfo = super().fetchGroupInfo(group_id)
            mem_ver_list = ginfo.gridInfoMap.get(group_id, {}).get("memVerList", [])
            member_ids = [m.split("_")[0] for m in mem_ver_list]
            members = []
            for uid in member_ids:
                try:
                    uinfo = self.fetchUserInfo(uid)
                    ud = uinfo.changed_profiles.get(uid, {})
                    members.append({'id': ud.get('userId', uid), 'name': ud.get('displayName', f"[{uid}]")})
                except Exception:
                    members.append({'id': uid, 'name': f"[Không lấy tên {uid}]"})
            return members
        except Exception as e:
            print(f"[{self.label}] ❌ Lỗi lấy thành viên nhóm {group_id}: {e}")
            return []

    def send_tag_message(self, thread_id, message_text, user_ids, batch_size=10, delay_between_batch=0.5):
        """Tag nhiều user theo batch (không màu)"""
        try:
            if not user_ids:
                # gửi 1 tin ko tag
                self.send(Message(text=message_text), thread_id=thread_id, thread_type=ThreadType.GROUP)
                print(f"[{self.label}] ✅ Gửi tin không tag vào nhóm {thread_id}")
                return

            for i in range(0, len(user_ids), batch_size):
                batch = user_ids[i:i+batch_size]
                mentions = []
                formatted = (message_text or "").rstrip() + " "
                for uid in batch:
                    try:
                        uinfo = self.fetchUserInfo(uid)
                        name = uinfo.changed_profiles.get(uid, {}).get('displayName', uid)
                    except Exception:
                        name = uid
                    tag = f"@{name}"
                    offset = len(formatted)
                    formatted += tag + " "
                    mentions.append(Mention(uid=uid, length=len(tag), offset=offset, auto_format=False))
                multi = MultiMention(mentions) if mentions else None
                self.send(Message(text=formatted, mention=multi),
                          thread_id=thread_id, thread_type=ThreadType.GROUP)
                print(f"[{self.label}] ✅ Gửi {len(batch)} tag vào nhóm {thread_id}")
                time.sleep(delay_between_batch)
        except Exception as e:
            print(f"[{self.label}] ❌ Lỗi gửi tag: {e}")

    def send_all_message(self, thread_id, message_text):
        try:
            tag_text = "@All"
            formatted = (message_text or "").rstrip() + " " + tag_text
            offset = len(formatted) - len(tag_text)
            mention = Mention(uid="-1", length=len(tag_text), offset=offset, auto_format=False)
            multi = MultiMention([mention])
            self.send(Message(text=formatted, mention=multi),
                      thread_id=thread_id, thread_type=ThreadType.GROUP)
            print(f"[{self.label}] ✅ Gửi @All vào nhóm {thread_id}")
        except Exception as e:
            print(f"[{self.label}] ❌ Lỗi gửi @All: {e}")

    # ---- MỚI: các phương thức hỗ trợ gửi MÀU (dùng MessageStyle) ----
    def _make_style_for_text(self, text, color_hex=None, font_size=100):
        color = color_hex if color_hex else random.choice(COLOR_LIST)
        try:
            styles = [
                MessageStyle(offset=0, length=len(text), style="color", color=color, auto_format=False),
                MessageStyle(offset=0, length=len(text), style="font", size=str(font_size), auto_format=False)
            ]
            return MultiMsgStyle(styles)
        except Exception:
            return None

    def send_tag_message_colored(self, thread_id, message_text, user_ids, batch_size=10, delay_between_batch=0.5):
        """Tag nhiều user theo batch, mỗi message có style màu (random nếu không truyền)"""
        try:
            if not user_ids:
                style = self._make_style_for_text(message_text)
                self.send(Message(text=message_text, style=style), thread_id=thread_id, thread_type=ThreadType.GROUP)
                print(f"[{self.label}] ✅ Gửi tin không tag (màu) vào nhóm {thread_id}")
                return

            for i in range(0, len(user_ids), batch_size):
                batch = user_ids[i:i+batch_size]
                mentions = []
                formatted = (message_text or "").rstrip() + " "
                for uid in batch:
                    try:
                        uinfo = self.fetchUserInfo(uid)
                        name = uinfo.changed_profiles.get(uid, {}).get('displayName', uid)
                    except Exception:
                        name = uid
                    tag = f"@{name}"
                    offset = len(formatted)
                    formatted += tag + " "
                    mentions.append(Mention(uid=uid, length=len(tag), offset=offset, auto_format=False))
                multi = MultiMention(mentions) if mentions else None
                style = self._make_style_for_text(formatted)
                self.send(Message(text=formatted, mention=multi, style=style),
                          thread_id=thread_id, thread_type=ThreadType.GROUP)
                print(f"[{self.label}] 🌈 Gửi {len(batch)} tag màu vào nhóm {thread_id}")
                time.sleep(delay_between_batch)
        except Exception as e:
            print(f"[{self.label}] ❌ Lỗi gửi tag màu: {e}")

    def send_all_message_colored(self, thread_id, message_text):
        try:
            tag_text = "@All"
            formatted = (message_text or "").rstrip() + " " + tag_text
            offset = len(formatted) - len(tag_text)
            mention = Mention(uid="-1", length=len(tag_text), offset=offset, auto_format=False)
            multi = MultiMention([mention])
            style = self._make_style_for_text(formatted)
            self.send(Message(text=formatted, mention=multi, style=style),
                      thread_id=thread_id, thread_type=ThreadType.GROUP)
            print(f"[{self.label}] 🌈 Gửi @All màu vào nhóm {thread_id}")
        except Exception as e:
            print(f"[{self.label}] ❌ Lỗi gửi @All màu: {e}")

    def loop_send_from_file(self, thread_id, filename, delay, users):
        """Đọc file rồi gửi lặp lại tới khi stop (bản không màu)"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            if not lines:
                print(f"[{self.label}] ❌ File {filename} rỗng.")
                return
        except FileNotFoundError:
            print(f"[{self.label}] ❌ Không tìm thấy file: {filename}")
            return
        except Exception as e:
            print(f"[{self.label}] ❌ Lỗi đọc file: {e}")
            return

        self.running.set()
        while self.running.is_set():
            for line in lines:
                if not self.running.is_set():
                    break
                if users == ["@all"]:
                    self.send_all_message(thread_id, line)
                else:
                    self.send_tag_message(thread_id, line, users)
                time.sleep(delay)
        print(f"[{self.label}] 🚦 Dừng gửi nhóm {thread_id}")

    def loop_send_from_file_colored(self, thread_id, filename, delay, users):
        """Đọc file rồi gửi lặp lại tới khi stop (bản có màu)"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            if not lines:
                print(f"[{self.label}] ❌ File {filename} rỗng.")
                return
        except FileNotFoundError:
            print(f"[{self.label}] ❌ Không tìm thấy file: {filename}")
            return
        except Exception as e:
            print(f"[{self.label}] ❌ Lỗi đọc file: {e}")
            return

        self.running.set()
        while self.running.is_set():
            for line in lines:
                if not self.running.is_set():
                    break
                if users == ["@all"]:
                    self.send_all_message_colored(thread_id, line)
                else:
                    self.send_tag_message_colored(thread_id, line, users)
                time.sleep(delay)
        print(f"[{self.label}] 🚦 Dừng gửi nhóm màu {thread_id}")

    def stop(self):
        self.running.clear()

# small helper for defensive reading of gridInfoMap
def gid_in_ginfo(ginfo, gid):
    try:
        return gid in ginfo.gridInfoMap and 'name' in ginfo.gridInfoMap[gid]
    except:
        return False

class MultiAccountManager:
    def __init__(self):
        self.accounts = []  # list of dicts: {client: TagClient, threads: []}

    def add_account(self, imei, cookies, label):
        client = TagClient(imei=imei, session_cookies=cookies, label=label)
        entry = {'client': client, 'threads': []}
        self.accounts.append(entry)
        return client

    def start_thread(self, client, thread_id, filename, delay, users, colored=False):
        if colored:
            t = threading.Thread(target=client.loop_send_from_file_colored, args=(thread_id, filename, delay, users))
        else:
            t = threading.Thread(target=client.loop_send_from_file, args=(thread_id, filename, delay, users))
        t.daemon = True
        t.start()
        for e in self.accounts:
            if e['client'] is client:
                e['threads'].append(t)
                break

    def stop_all(self):
        for e in self.accounts:
            try:
                e['client'].stop()
            except:
                pass
        time.sleep(0.5)
        print("🚦 Yêu cầu dừng đã được gửi cho tất cả account.")

class TreongonBot(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies,
                 delay=5, message_text="", ttl=None,
                 media_source="videos.txt"):
        super().__init__(api_key, secret_key, imei, session_cookies)
        self.delay = delay
        self.message_text = message_text
        self.ttl = int(ttl) if ttl is not None else None
        self.media_source = media_source
        self.running_flag = threading.Event()
        self.running_flag.set()
        self.thumb_url = None
        self.font_size = 20
        self.color_mode = 'y'

    def spam_messages(self, thread_id, thread_type, ttl=None):
        while self.running_flag.is_set():
            try:
                self.setTyping(thread_id, thread_type)
                time.sleep(4)
                vids = read_list_file(self.media_source)
                if vids:
                    url = random.choice(vids)
                    thumb = self.thumb_url if self.thumb_url else ""
                    ttl_to_send = normalize_ttl_value(ttl if ttl is not None else self.ttl)
                    self.sendRemoteVideo(
                        url, thumb, duration="100000",
                        thread_id=thread_id, thread_type=thread_type,
                        width=1920, height=1080,
                        ttl=ttl_to_send
                    )

                if self.message_text:
                    lines = self.message_text.strip().splitlines()
                    styles = []
                    formatted_text = ""
                    offset = 0
                    if self.color_mode == 'n':
                        chosen_color = random.choice(COLOR_LIST)
                    for line in lines:
                        if self.color_mode == 'y':
                            color = random.choice(COLOR_LIST)
                        else:
                            color = chosen_color
                        line_text = line + "\n"
                        formatted_text += line_text
                        styles.append(MessageStyle(offset=offset, length=len(line_text),
                                                   style="color", color=color, auto_format=False))
                        styles.append(MessageStyle(offset=offset, length=len(line_text),
                                                   style="font", size=str(self.font_size), auto_format=False))
                        offset += len(line_text)
                    style = MultiMsgStyle(styles)
                    mention = Mention("-1", length=len(formatted_text), offset=0)
                    ttl_to_send = normalize_ttl_value(ttl if ttl is not None else self.ttl)
                    self.send(Message(text=formatted_text, mention=mention, style=style),
                              thread_id=thread_id, thread_type=thread_type,
                              ttl=ttl_to_send)

                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"{Colors.CYAN}[{timestamp}] Treo Video + Ngôn file.txt -> {thread_id}{Colors.RESET}")
            except Exception as e:
                custom_print(f"Lỗi: {e}")
            time.sleep(self.delay)

class TreongonTextBot(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies,
                 delay=5, message_text="", ttl=None):
        super().__init__(api_key, secret_key, imei, session_cookies)
        self.delay = delay
        self.message_text = message_text
        self.ttl = int(ttl) if ttl is not None else None
        self.running_flag = threading.Event()
        self.running_flag.set()
        self.font_size = 18
        self.color_mode = 'y'

    def spam_messages(self, thread_id, thread_type, ttl=None):
        while self.running_flag.is_set():
            try:
                if self.message_text:
                    lines = self.message_text.strip().splitlines()
                    styles = []
                    formatted_text = ""
                    offset = 0
                    if self.color_mode == 'n':
                        chosen_color = random.choice(COLOR_LIST)
                    for line in lines:
                        if self.color_mode == 'y':
                            color = random.choice(COLOR_LIST)
                        else:
                            color = chosen_color
                        line_text = line + "\n"
                        formatted_text += line_text
                        styles.append(MessageStyle(offset=offset, length=len(line_text),
                                                   style="color", color=color, auto_format=False))
                        styles.append(MessageStyle(offset=offset, length=len(line_text),
                                                   style="font", size=str(self.font_size), auto_format=False))
                        offset += len(line_text)
                    style = MultiMsgStyle(styles)
                    ttl_to_send = normalize_ttl_value(ttl if ttl is not None else self.ttl)
                    self.send(Message(text=formatted_text, style=style),
                              thread_id=thread_id, thread_type=thread_type,
                              ttl=ttl_to_send)

                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"{Colors.GREEN}[{timestamp}] Treo Ngôn Text -> {thread_id}{Colors.RESET}")
            except Exception as e:
                custom_print(f"Lỗi: {e}")
            time.sleep(self.delay)

class TreoAnhBot(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies,
                 delay=5, message_text="", ttl=None, image_folder="Gbao",
                 font_size=40, color_mode="y", mentions=None):
        super().__init__(api_key, secret_key, imei, session_cookies)
        self.delay = delay
        self.message_text = message_text
        self.ttl = int(ttl) if ttl is not None else None
        self.running_flag = threading.Event()
        self.running_flag.set()
        self.image_folder = image_folder
        self.font_size = font_size
        self.color_mode = color_mode
        self.mentions = mentions or []

    def spam_messages(self, thread_id, thread_type, ttl=None):
        while self.running_flag.is_set():
            try:
                if os.path.exists(self.image_folder):
                    images = [f for f in os.listdir(self.image_folder)
                              if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))]
                    if images:
                        img_file = random.choice(images)
                        img_path = os.path.join(self.image_folder, img_file)
                        ttl_to_send = normalize_ttl_value(ttl if ttl is not None else self.ttl)
                        self.sendLocalImage(img_path,
                                            thread_id=thread_id,
                                            thread_type=thread_type,
                                            ttl=ttl_to_send)

                if self.message_text:
                    lines = self.message_text.strip().splitlines()
                    styles = []
                    formatted_text = ""
                    offset = 0
                    if self.color_mode == 'n':
                        chosen_color = random.choice(COLOR_LIST)
                    for line in lines:
                        color = random.choice(COLOR_LIST) if self.color_mode == 'y' else chosen_color
                        line_text = line + "\n"
                        formatted_text += line_text
                        styles.append(MessageStyle(offset=offset, length=len(line_text),
                                                   style="color", color=color, auto_format=False))
                        styles.append(MessageStyle(offset=offset, length=len(line_text),
                                                   style="font", size=str(self.font_size), auto_format=False))
                        offset += len(line_text)
                    style = MultiMsgStyle(styles)
                    ttl_to_send = normalize_ttl_value(ttl if ttl is not None else self.ttl)
                    multi_mention = None
                    if self.mentions:
                        multi_mention = MultiMention([
                            Mention(uid=uid, length=5, offset=len(formatted_text), auto_format=False)
                            for uid in self.mentions
                        ])
                    self.send(Message(text=formatted_text, style=style, mention=multi_mention),
                              thread_id=thread_id, thread_type=thread_type,
                              ttl=ttl_to_send)

                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"{Colors.MAGENTA}[{timestamp}] Treo Ảnh -> {thread_id}{Colors.RESET}")
            except Exception as e:
                custom_print(f"Lỗi khi gửi ảnh + ngôn: {e}")
            time.sleep(self.delay)

# quản lý active threads chung cho cả chế độ thường và chế độ màu
active_threads = {}  # {group_id: {"thread": Thread, "bot": TagClient, "users": [...], "file": str, "delay": float, "colored": bool}}

def start_spam_for_group_global(client, group, filename, delay, users, colored=False):
    if colored:
        t = threading.Thread(target=client.loop_send_from_file_colored, args=(group['id'], filename, delay, users))
    else:
        t = threading.Thread(target=client.loop_send_from_file, args=(group['id'], filename, delay, users))
    t.daemon = True
    t.start()
    active_threads[group['id']] = {"thread": t, "bot": client, "users": users, "file": filename, "delay": delay, "colored": colored}
    print(f"🚀 Đã bắt đầu spam cho nhóm {group['name']} (ID: {group['id']}) - colored={colored}")

def stop_spam_for_group(group_id):
    if group_id in active_threads:
        active_threads[group_id]["bot"].stop()
        del active_threads[group_id]
        print(f"🚦 Đã dừng spam cho nhóm {group_id}")
    else:
        print("⚠️ Nhóm này không chạy hoặc đã dừng bọn ngu ơi (bố mdung nói).")

# --- run_tag_spam (option 2: multi-acc tag bình thường) ---
def run_tag_spam():
    """Chức năng Réo Nhiều Người (thay bằng bản multi-acc) - option 2"""
    clear_screen()
    draw_box("MULTI-ACC - NHƯ CŨ (RÉO NHIỀU NGƯỜI)", [
        "Nhập số account, mỗi account sẽ lấy danh sách nhóm, bạn chọn nhóm và thành viên như trước.",
        "Mỗi account có thể chọn nhiều nhóm; cho phép @All hoặc tag member list."
    ], Colors.CYAN)

    try:
        num_acc = int(input(" Nhập số account muốn chạy (1-10): ").strip())
    except:
        print("⚠️ Số không hợp lệ. Hủy.")
        return

    manager = MultiAccountManager()

    for i in range(num_acc):
        draw_box(f"ACCOUNT {i+1} - NHẬP THÔNG TIN", [
            "Nhập IMEI và Cookie JSON (giống phiên bản cũ)."
        ], Colors.GREEN)
        imei = input("IMEI: ").strip()
        cookie_str = input("Cookie JSON: ").strip()
        try:
            cookies = json.loads(cookie_str)
        except Exception as e:
            print(f"❌ Cookie không hợp lệ ({e}). Bỏ acc này.")
            continue

        label = f"Acc{i+1}"
        client = manager.add_account(imei, cookies, label=label)

        groups = client.fetch_groups()
        if not groups:
            print(f"[{label}] ⚠️ Không lấy được nhóm, bỏ acc này.")
            continue

        lines = [f"{idx}. {g['name']} (ID: {g['id']})" for idx, g in enumerate(groups, start=1)]
        draw_box(f"DANH SÁCH NHÓM - {label}", lines, Colors.CYAN)

        choice_str = input(" Chọn nhóm (vd: 1,2,3) hoặc '0' để bỏ acc: ").strip()
        if choice_str == "0" or not choice_str:
            print(f"[{label}] Bỏ acc.")
            continue
        choices = [int(x) for x in choice_str.split(",") if x.strip().isdigit()]
        selected_groups = [groups[c-1] for c in choices if 1 <= c <= len(groups)]
        if not selected_groups:
            print(f"[{label}] Không có nhóm hợp lệ. Bỏ acc.")
            continue

        filename = input("📄 Tên file chứa nội dung (mỗi dòng 1 tin): ").strip()
        if not os.path.exists(filename):
            print("❌ File không tồn tại. Bỏ acc.")
            continue

        try:
            delay = float(input("⏳ Delay giữa tin (giây, VD 5): ").strip())
        except:
            delay = 5.0

        for group in selected_groups:
            members = client.fetch_group_members(group['id'])
            if not members:
                print(f"[{label}] ⚠️ Không lấy được thành viên cho nhóm {group['name']}. Bạn có muốn dùng @All thay thế? (y/n)")
                yn = input().strip().lower()
                if yn == "y":
                    users = ["@all"]
                else:
                    print("Bỏ nhóm này.")
                    continue
            else:
                lines = [f"{idx}. {m['name']} (ID: {m['id']})" for idx, m in enumerate(members, start=1)]
                draw_box(f"THÀNH VIÊN NHÓM: {group['name']}", lines, Colors.YELLOW)
                choice = input("Nhập số thành viên để tag (vd: 1,2,3), gõ 'all' để @All, '0' để bỏ nhóm: ").strip().lower()
                if choice == "0" or not choice:
                    print("Bỏ nhóm này.")
                    continue
                if choice == "all":
                    users = ["@all"]
                else:
                    try:
                        ids = [int(x) for x in choice.split(",") if x.strip().isdigit()]
                        users = [members[idx-1]['id'] for idx in ids if 1 <= idx <= len(members)]
                        if not users:
                            print("Không có id hợp lệ, bỏ nhóm này.")
                            continue
                    except Exception as e:
                        print(f"Lỗi chọn thành viên: {e}. Bỏ nhóm.")
                        continue

            manager.start_thread(client, group['id'], filename, delay, users, colored=False)
            print(f"[{label}] 🚀 Bắt đầu gửi vào nhóm '{group['name']}' với users={('ALL' if users==['@all'] else str(len(users))+' user(s)')}")

    if not manager.accounts:
        print("❌ Không có account hợp lệ. Kết thúc.")
        return

    print("\n🚀 TẤT CẢ ĐÃ CHẠY. Nhấn Enter để dừng toàn bộ và quay lại menu.")
    input()
    manager.stop_all()
    time.sleep(1)

# --- Chức năng 6: Réo nhiều người màu (multi-acc, mỗi tin random 1 màu) ---
def run_tag_spam_color():
    """Chức năng Réo Nhiều Người MÀU (multi-acc) - option 6"""
    clear_screen()
    draw_box("MULTI-ACC - RÉO MÀU (MỖI TIN RANDOM MÀU)", [
        "Nhập số account, mỗi account sẽ lấy danh sách nhóm, bạn chọn nhóm và thành viên như trước.",
        "Mỗi account có thể chọn nhiều nhóm; mỗi tin sẽ có màu ngẫu nhiên."
    ], Colors.CYAN)

    try:
        num_acc = int(input(" Nhập số account muốn chạy (1-10): ").strip())
    except:
        print("⚠️ Số không hợp lệ. Hủy.")
        return

    manager = MultiAccountManager()

    for i in range(num_acc):
        draw_box(f"ACCOUNT {i+1} - NHẬP THÔNG TIN", [
            "Nhập IMEI và Cookie JSON (giống phiên bản cũ)."
        ], Colors.GREEN)
        imei = input("IMEI: ").strip()
        cookie_str = input("Cookie JSON: ").strip()
        try:
            cookies = json.loads(cookie_str)
        except Exception as e:
            print(f"❌ Cookie không hợp lệ ({e}). Bỏ acc này.")
            continue

        label = f"Acc{i+1}"
        client = manager.add_account(imei, cookies, label=label)

        groups = client.fetch_groups()
        if not groups:
            print(f"[{label}] ⚠️ Không lấy được nhóm, bỏ acc này.")
            continue

        lines = [f"{idx}. {g['name']} (ID: {g['id']})" for idx, g in enumerate(groups, start=1)]
        draw_box(f"DANH SÁCH NHÓM - {label}", lines, Colors.CYAN)

        choice_str = input(" Chọn nhóm (vd: 1,2,3) hoặc '0' để bỏ acc: ").strip()
        if choice_str == "0" or not choice_str:
            print(f"[{label}] Bỏ acc.")
            continue
        choices = [int(x) for x in choice_str.split(",") if x.strip().isdigit()]
        selected_groups = [groups[c-1] for c in choices if 1 <= c <= len(groups)]
        if not selected_groups:
            print(f"[{label}] Không có nhóm hợp lệ. Bỏ acc.")
            continue

        filename = input("📄 Tên file chứa nội dung (mỗi dòng 1 tin): ").strip()
        if not os.path.exists(filename):
            print("❌ File không tồn tại. Bỏ acc.")
            continue

        try:
            delay = float(input("⏳ Delay giữa tin (giây, VD 5): ").strip())
        except:
            delay = 5.0

        for group in selected_groups:
            members = client.fetch_group_members(group['id'])
            if not members:
                print(f"[{label}] ⚠️ Không lấy được thành viên cho nhóm {group['name']}. Bạn có muốn dùng @All thay thế? (y/n)")
                yn = input().strip().lower()
                if yn == "y":
                    users = ["@all"]
                else:
                    print("Bỏ nhóm này.")
                    continue
            else:
                lines = [f"{idx}. {m['name']} (ID: {m['id']})" for idx, m in enumerate(members, start=1)]
                draw_box(f"THÀNH VIÊN NHÓM: {group['name']}", lines, Colors.YELLOW)
                choice = input("Nhập số thành viên để tag (vd: 1,2,3), gõ 'all' để @All, '0' để bỏ nhóm: ").strip().lower()
                if choice == "0" or not choice:
                    print("Bỏ nhóm này.")
                    continue
                if choice == "all":
                    users = ["@all"]
                else:
                    try:
                        ids = [int(x) for x in choice.split(",") if x.strip().isdigit()]
                        users = [members[idx-1]['id'] for idx in ids if 1 <= idx <= len(members)]
                        if not users:
                            print("Không có id hợp lệ, bỏ nhóm này.")
                            continue
                    except Exception as e:
                        print(f"Lỗi chọn thành viên: {e}. Bỏ nhóm.")
                        continue

            manager.start_thread(client, group['id'], filename, delay, users, colored=True)
            print(f"[{label}] 🌈 Bắt đầu gửi màu vào nhóm '{group['name']}' với users={('ALL' if users==['@all'] else str(len(users))+' user(s)')}")

    if not manager.accounts:
        print("❌ Không có account hợp lệ. Kết thúc.")
        return

    print("\n🌈 TẤT CẢ CHẾ ĐỘ RÉO MÀU ĐÃ CHẠY. Nhấn Enter để dừng toàn bộ và quay lại menu.")
    input()
    manager.stop_all()
    time.sleep(1)

# --- run_treongon (option 3) ---
def run_treongon():
    """Option 3 - Treo Video + text"""
    clear_screen()
    try:
        num_acc = int(input(" Nhập số lượng acc: ").strip())
    except:
        print("Số lượng acc không hợp lệ.")
        return

    bots = []
    for i in range(num_acc):
        imei = input("Imei: ").strip()
        cookie_str = input("Cookie: ").strip()
        try:
            cookies = json.loads(cookie_str)
        except:
            print("Cookie không hợp lệ, bỏ qua acc này.")
            continue

        file_txt = input("File(.txt): ").strip()
        message_text = read_file_content(file_txt)
        try:
            delay = int(input("Delay: ").strip() or "5")
        except:
            delay = 5

        ttl_input = input("Ttl (giây, 0 = không): ").strip()
        ttl = int(ttl_input) if ttl_input.isdigit() and int(ttl_input) > 0 else None
        media_source = "videos.txt"
        thumb_url = input("👉 Nhập URL ảnh làm bìa video: ").strip()
        font_size_input = input("👉 Nhập size chữ (tối đa 500, mặc định 40): ").strip()
        font_size = int(font_size_input) if font_size_input.isdigit() else 40
        if font_size > 500:
            font_size = 500

        bot = TreongonBot("api", "secret", imei, cookies, delay,
                          message_text, ttl, media_source=media_source)
        bot.thumb_url = thumb_url
        bot.font_size = font_size
        color_choice = input("👉 Chọn chế độ màu (y = mỗi dòng 1 màu, n = cả tin 1 màu): ").strip().lower()
        bot.color_mode = 'y' if color_choice == 'y' else 'n'
        bots.append(bot)

        groups = []
        try:
            all_groups = bot.fetchAllGroups()
            for gid, _ in all_groups.gridVerMap.items():
                ginfo = bot.fetchGroupInfo(gid)
                gname = ginfo.gridInfoMap[gid]["name"] if gid in ginfo.gridInfoMap else "Unknown"
                groups.append({"id": gid, "name": gname})
        except Exception as e:
            custom_print(f"Lỗi lấy nhóm: {e}")

        if not groups:
            print("Không có nhóm để chọn cho acc này.")
            continue

        print("\nDanh sách nhóm:")
        for idx, g in enumerate(groups, 1):
            print(f"{idx}. {g['name']} (ID: {g['id']})")
        choice_str = input(" Chọn nhóm (vd: 1,2,3): ").strip()
        choices = [int(x) for x in choice_str.split(",") if x.strip().isdigit()]
        for choice in choices:
            if 1 <= choice <= len(groups):
                gid = groups[choice-1]['id']
                threading.Thread(target=bot.spam_messages,
                                        args=(gid, ThreadType.GROUP, ttl), daemon=True).start()

    if not bots:
        draw_box("KẾT QUẢ", ["❌ Không có acc nào hợp lệ."], Colors.RED)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for b in bots:
            try:
                b.running_flag.clear()
            except:
                pass
        print("\nĐã dừng Treo Video.")

# --- run_treongon_text (option 4) ---
def run_treongon_text():
    """Option 4 - Treo ngôn 5 màu (text only)"""
    clear_screen()
    try:
        num_acc = int(input(" Nhập số lượng acc: ").strip())
    except:
        print("Số lượng acc không hợp lệ.")
        return

    bots = []
    for i in range(num_acc):
        imei = input("Imei: ").strip()
        cookie_str = input("Cookie: ").strip()
        try:
            cookies = json.loads(cookie_str)
        except:
            print("Cookie không hợp lệ, bỏ qua acc này.")
            continue

        file_txt = input("File(.txt): ").strip()
        message_text = read_file_content(file_txt)
        try:
            delay = int(input("Delay: ").strip() or "5")
        except:
            delay = 5

        ttl_input = input("Ttl (giây, 0 = không): ").strip()
        ttl = int(ttl_input) if ttl_input.isdigit() and int(ttl_input) > 0 else None

        bot = TreongonTextBot("api", "secret", imei, cookies, delay,
                              message_text, ttl)

        font_size_input = input("👉 Nhập size chữ (tối đa 500, mặc định 40): ").strip()
        font_size = int(font_size_input) if font_size_input.isdigit() else 40
        if font_size > 500:
            font_size = 500
        bot.font_size = font_size

        color_choice = input("👉 Chọn chế độ màu (y = mỗi dòng 1 màu, n = cả tin 1 màu): ").strip().lower()
        bot.color_mode = 'y' if color_choice == 'y' else 'n'

        bots.append(bot)
        groups = []
        try:
            all_groups = bot.fetchAllGroups()
            for gid, _ in all_groups.gridVerMap.items():
                ginfo = bot.fetchGroupInfo(gid)
                gname = ginfo.gridInfoMap[gid]["name"] if gid in ginfo.gridInfoMap else "Unknown"
                groups.append({"id": gid, "name": gname})
        except Exception as e:
            custom_print(f"Lỗi lấy nhóm: {e}")

        if not groups:
            print("Không có nhóm để chọn cho acc này.")
            continue

        print("\nDanh sách nhóm:")
        for idx, g in enumerate(groups, 1):
            print(f"{idx}. {g['name']} (ID: {g['id']})")
        choice_str = input(" Chọn nhóm (vd: 1,2,3): ").strip()
        choices = [int(x) for x in choice_str.split(",") if x.strip().isdigit()]
        for choice in choices:
            if 1 <= choice <= len(groups):
                gid = groups[choice-1]['id']
                threading.Thread(target=bot.spam_messages,
                                        args=(gid, ThreadType.GROUP, ttl), daemon=True).start()

    if not bots:
        draw_box("KẾT QUẢ", ["❌ Không có acc nào hợp lệ."], Colors.RED)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for b in bots:
            try:
                b.running_flag.clear()
            except:
                pass
        print("\nĐã dừng Treo Ngôn Text.")

# --- run_treoanh (option 5) ---
def run_treoanh():
    """Option 5 - Treo ảnh + ngôn + tag"""
    clear_screen()
    try:
        num_acc = int(input(" Nhập số lượng acc: ").strip())
    except:
        print("Số lượng acc không hợp lệ.")
        return

    bots = []
    for i in range(num_acc):
        imei = input("Imei: ").strip()
        cookie_str = input("Cookie: ").strip()
        try:
            cookies = json.loads(cookie_str)
        except:
            print("Cookie không hợp lệ, bỏ qua acc này.")
            continue

        file_txt = input("File ngôn (.txt): ").strip()
        message_text = read_file_content(file_txt)

        try:
            delay = int(input("Delay (giây): ").strip() or "5")
        except:
            delay = 5

        ttl_input = input("TTL (giây, 0 = không): ").strip()
        ttl = int(ttl_input) if ttl_input.isdigit() and int(ttl_input) > 0 else None

        font_size_input = input("👉 Nhập size chữ (tối đa 500, mặc định 40): ").strip()
        font_size = int(font_size_input) if font_size_input.isdigit() else 40
        if font_size > 500:
            font_size = 500

        color_choice = input("👉 Chọn chế độ màu (y = mỗi dòng 1 màu, n = cả tin 1 màu): ").strip().lower()
        color_mode = 'y' if color_choice == 'y' else 'n'

        bot_tmp = ZaloAPI("api", "secret", imei, cookies)
        groups = []
        try:
            all_groups = bot_tmp.fetchAllGroups()
            for gid, _ in all_groups.gridVerMap.items():
                ginfo = bot_tmp.fetchGroupInfo(gid)
                gname = ginfo.gridInfoMap[gid]["name"] if gid in ginfo.gridInfoMap else "Unknown"
                groups.append({"id": gid, "name": gname})
        except Exception as e:
            custom_print(f"Lỗi lấy nhóm: {e}")

        if not groups:
            print("Không có nhóm để chọn.")
            continue

        print("\nDanh sách nhóm:")
        for idx, g in enumerate(groups, 1):
            print(f"{idx}. {g['name']} (ID: {g['id']})")

        choice_str = input(" Chọn nhóm (vd: 1,2,3): ").strip()
        choices = [int(x) for x in choice_str.split(",") if x.strip().isdigit()]
        for choice in choices:
            if 1 <= choice <= len(groups):
                gid = groups[choice-1]['id']
                tag_all_choice = input("👉 Có tag tất cả thành viên? (y/n): ").strip().lower()
                mentions = []
                if tag_all_choice == "y":
                    try:
                        members = bot_tmp.fetchGroupInfo(gid).gridInfoMap[gid]["memVerList"]
                        mentions = [m.split("_")[0] for m in members]
                    except:
                        mentions = []
                bot = TreoAnhBot("api", "secret", imei, cookies,
                                 delay=delay, message_text=message_text, ttl=ttl,
                                 image_folder="Gbao", font_size=font_size,
                                 color_mode=color_mode, mentions=mentions)
                bots.append(bot)
                threading.Thread(target=bot.spam_messages,
                                 args=(gid, ThreadType.GROUP, ttl), daemon=True).start()

    if not bots:
        draw_box("KẾT QUẢ", ["❌ Không có acc nào hợp lệ."], Colors.RED)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for b in bots:
            try:
                b.running_flag.clear()
            except:
                pass
        print("\nĐã dừng Treo Ảnh.")

def print_success_message():
    message = f"╭{'─'*50}╮\n│ Đúng Mật Khẩu!Welcome To Tools By  Mdung w Qhung! {' '*(14)}│\n╰{'─'*50}╯"
    print(message)

def print_loading_system():
    message = "Đang tiến hành vào hệ thống"
    print(message, end='', flush=True)
    for _ in range(5):
        print(f".", end='', flush=True)
        time.sleep(0.5)
    print()
    time.sleep(1)

def check_password():
    print(r"""
Tool treo zalo by mdung
nhập mật khẩu vào tool
""")
    password = "mdung"
    attempts = 3
    while attempts > 0:
        input_pass = input("\n🔐 Nhập mật khẩu để vào tool: ").strip()
        if input_pass == password:
            print_success_message()
            print_loading_system()
            return True
        else:
            attempts -= 1
            if attempts > 0:
                print(f"\n❌ Mật Khẩu Sai !!! Còn {attempts} lần nhập lại")
            else:
                print("\n Lien He 0946572012 De Mua Tool ")
                print(" Sai mật khẩu rồi Thz Cặc, tool sẽ tắt trong 3 giây sau...")
                for i in range(3, 0, -1):
                    print(f" {i}...")
                    time.sleep(1)
                sys.exit()
    return False

class BotMute(ZaloAPI):
    def __init__(self, imei, session_cookies):
        super().__init__('api_key', 'secret_key', imei, session_cookies)

    def fetch_groups(self):
        try:
            all_groups = self.fetchAllGroups()
            group_list = []
            for group_id in all_groups.gridVerMap:
                group_info = self.fetchGroupInfo(group_id)
                group_name = group_info.gridInfoMap[group_id]["name"]
                group_list.append({'id': group_id, 'name': group_name})
            return group_list
        except Exception as e:
            print(f"❌ Lỗi lấy nhóm: {e}")
            return []

    def fetch_members(self, group_id):
        try:
            group_info = self.fetchGroupInfo(group_id)
            mem_ver_list = group_info.gridInfoMap[group_id]["memVerList"]
            members = []
            for mem in mem_ver_list:
                uid = mem.split("_")[0]
                try:
                    user_info = self.fetchUserInfo(uid)
                    name = user_info.changed_profiles[uid]["displayName"]
                except:
                    name = f"User_{uid}"
                members.append({"id": uid, "name": name})
            return members
        except Exception as e:
            print(f"❌ Lỗi lấy thành viên: {e}")
            return []

def parse_cookie_string(cookie_str):
    """
    Chuyển chuỗi cookie JSON hoặc dạng key=value;key2=value2 thành dict Python
    """
    try:
        # Nếu là JSON
        if cookie_str.strip().startswith("{"):
            return json.loads(cookie_str)
        # Nếu là dạng key=value;key2=value2
        cookies = {}
        for part in cookie_str.split(";"):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                cookies[k.strip()] = v.strip()
        return cookies
    except Exception as e:
        print(f"❌ Cookie không hợp lệ: {e}")
        return {}

def auto_mute_box():
    imei = input("🔑 Nhập IMEI: ").strip()
    cookie_str = input("🍪 Nhập Cookie JSON: ").strip()
    cookies = parse_cookie_string(cookie_str)
    if not cookies:
        sys.exit()

    bot = BotMute(imei, cookies)
    groups = bot.fetch_groups()
    if not groups:
        print("⚠️ Không tìm thấy nhóm.")
        return

    print("\n📋 Danh sách nhóm:")
    for idx, g in enumerate(groups, 1):
        print(f"{idx}. {g['name']} | ID: {g['id']}")

    try:
        gidx = int(input("\n👉 STT nhóm cần mute: ")) - 1
        group_id = groups[gidx]['id']
    except:
        print("❌ STT không hợp lệ.")
        return

    members = bot.fetch_members(group_id)
    if not members:
        print("⚠️ Nhóm này không có thành viên.")
        return

    print("\n👤 Danh sách thành viên:")
    for idx, m in enumerate(members, 1):
        print(f"{idx}. {m['name']} | UID: {m['id']}")

    stt_input = input("\n🔇 Nhập STT thành viên cần mute (phân cách dấu ,): ").strip()
    try:
        stt_indices = [int(i.strip())-1 for i in stt_input.split(',') if i.strip().isdigit()]
    except:
        print("❌ Dữ liệu STT không hợp lệ.")
        return

    mute_list = []
    for idx in stt_indices:
        if 0 <= idx < len(members):
            mute_list.append(members[idx]['id'])
        else:
            print(f"⚠️ STT {idx+1} không hợp lệ, bỏ qua.")

    try:
        initial_data = bot.getRecentGroup(group_id)
        initial_messages = initial_data.get("groupMsgs", [])
        last_seen_id = int(initial_messages[-1].get("msgId")) if initial_messages else 0
    except:
        print("❌ Không thể xác định msgId ban đầu.")
        last_seen_id = 0

    print(f"\n🚀 Đang theo dõi nhóm ID {group_id}... Tự động xoá tin nhắn mới từ UID mute.\n")

    def mute_loop():
        nonlocal last_seen_id
        while True:
            try:
                group_data = bot.getRecentGroup(group_id)
                messages = group_data.get("groupMsgs", [])

                for msg in messages:
                    msg_id = msg.get("msgId")
                    cli_msg_id = msg.get("cliMsgId")
                    uid = str(msg.get("uidFrom",""))

                    if not msg_id or not cli_msg_id:
                        continue

                    if uid in mute_list and int(msg_id) > last_seen_id:
                        try:
                            res = bot.deleteGroupMsg(int(msg_id), uid, cli_msg_id, group_id)
                            if getattr(res, "status", None) == 0:
                                print(f"🔇 Đã xoá tin nhắn từ UID {uid}")
                        except:
                            pass
                        last_seen_id = int(msg_id)
            except:
                pass
            time.sleep(0.05)

    t = threading.Thread(target=mute_loop, daemon=True)
    t.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⛔ Đã dừng auto mute.")

def get_device_info():
    while True:
        try:
            imei = input(f"{ndp_tool}Nhập IMEI: ")
            if not imei.strip():
                print(f"{do}IMEI không được để trống! Vui lòng nhập lại.{end}")
                continue
            cookie_input = input(f"{ndp_tool}Nhập cookie (JSON format): ")
            cookie = json.loads(cookie_input)
            if "zpw_sek" not in cookie or not cookie["zpw_sek"]:
                print(f"{do}Cookie thiếu zpw_sek hoặc zpw_sek không hợp lệ! Vui lòng nhập lại.{end}")
                continue
            return imei, cookie
        except json.JSONDecodeError:
            print(f"{do}Định dạng cookie không hợp lệ! Vui lòng nhập lại.{end}")
        except Exception as e:
            print(f"{do}Lỗi khi nhập thông tin: {e}{end}")

def get_random_images_from_folder(folder_path='./pha', count=1):
    try:
        if not os.path.exists(folder_path):
            print(f"{do}Thư mục {folder_path} không tồn tại!{end}")
            logging.error(f"Image folder {folder_path} does not exist")
            return None
        all_files = os.listdir(folder_path)
        image_files = [file for file in all_files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if not image_files:
            print(f"{do}Không tìm thấy ảnh trong thư mục {folder_path}!{end}")
            logging.error(f"No images found in folder {folder_path}")
            return None
        return [os.path.join(folder_path, random.choice(image_files)) for _ in range(min(count, len(image_files)))]
    except Exception as e:
        print(f"{do}Lỗi khi lấy ảnh: {e}{end}")
        logging.error(f"Error getting images: {e}")
        return None

def generate_random_name():
    first_names = ["Attack By"]
    last_names = ["Erik"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def check_api_response(response):
    if not response or response is None:
        print(f"{do}API không trả về dữ liệu.{end}")
        logging.error("API response is empty or None")
        return False
    return True

def spam_all_groups(client, tagall_message, image_paths=None, spam_count=30):
    try:
        groups = client.fetchAllGroups()
        if not check_api_response(groups) or 'gridVerMap' not in groups:
            print(f"{do}Không thể lấy danh sách nhóm.{end}")
            logging.error("Failed to fetch group list")
            return False

        group_ids = list(groups['gridVerMap'].keys())
        spammed_count = 0

        for thread_id in group_ids:
            if spammed_count >= spam_count:
                break

            group_info = client.fetchGroupInfo(thread_id).gridInfoMap[thread_id]
            members = group_info.get('memVerList', [])
            if not members:
                print(f"{do}Nhóm {thread_id} không có thành viên để tag.{end}")
                logging.warning(f"Group {thread_id} has no members")
                continue

            # Construct message with manual mentions
            text = f"<b>{tagall_message}</b> "
            for member in members:
                member_parts = member.split('_', 1)
                if len(member_parts) != 2:
                    continue
                user_id, user_name = member_parts
                text += f"@{user_name} "

            message = Message(
                text=text,
                style={"bold": True, "color": "red"}
            )

            if image_paths and all(os.path.exists(img) for img in image_paths):
                client.sendMultiLocalImage(
                    imagePathList=image_paths,
                    thread_id=thread_id,
                    thread_type=ThreadType.GROUP,
                    width=2560,
                    height=2560,
                    message=message,
                )
            else:
                client.sendMessage(
                    message=message,
                    thread_id=thread_id,
                    thread_type=ThreadType.GROUP
                )

            print(f"{luc}Đã gửi tin nhắn đến nhóm {thread_id}{end}")
            logging.info(f"Sent message to group {thread_id}")
            spammed_count += 1
            time.sleep(random.uniform(3, 5))  # Increased delay to avoid rate limits

        return True
    except Exception as e:
        print(f"{do}Lỗi khi spam nhóm: {e}{end}")
        logging.error(f"Error spamming groups: {e}")
        if "rate limit" in str(e).lower():
            print(f"{do}Đã vượt quá giới hạn API, nghỉ 60 giây...{end}")
            time.sleep(60)
        return False

def spam_all_friends(client, message_text, image_paths=None, spam_count=30):
    try:
        friends = client.fetchAllFriends()
        if not check_api_response(friends):
            print(f"{do}Không thể lấy danh sách bạn bè.{end}")
            logging.error("Failed to fetch friend list")
            return False

        spammed_count = 0
        for friend in friends[:spam_count]:
            thread_id = friend.get('userId')
            if not thread_id:
                continue

            message = Message(
                text=message_text,
                style={"bold": True, "color": "red"}
            )

            if image_paths and all(os.path.exists(img) for img in image_paths):
                client.sendMultiLocalImage(
                    imagePathList=image_paths,
                    thread_id=thread_id,
                    thread_type=ThreadType.USER,
                    width=2560,
                    height=2560,
                    message=message,
                )
            else:
                client.sendMessage(
                    message=message,
                    thread_id=thread_id,
                    thread_type=ThreadType.USER
                )

            print(f"{luc}Đã gửi tin nhắn đến bạn {thread_id}{end}")
            logging.info(f"Sent message to friend {thread_id}")
            spammed_count += 1
            time.sleep(random.uniform(3, 5))  # Increased delay

        return True
    except Exception as e:
        print(f"{do}Lỗi khi spam bạn bè: {e}{end}")
        logging.error(f"Error spamming friends: {e}")
        if "rate limit" in str(e).lower():
            print(f"{do}Đã vượt quá giới hạn API, nghỉ 60 giây...{end}")
            time.sleep(60)
        return False

def leave_all_groups(client, imei):
    try:
        groups = client.fetchAllGroups()
        if not check_api_response(groups) or 'gridVerMap' not in groups:
            print(f"{do}Không thể lấy danh sách nhóm để rời.{end}")
            logging.error("Failed to fetch group list for leaving")
            return

        for group_id in groups['gridVerMap'].keys():
            client.leaveGroup(group_id, imei=imei)
            print(f"{luc}Đã rời nhóm {group_id}{end}")
            logging.info(f"Left group {group_id}")
            time.sleep(2)  # Increased delay

    except Exception as e:
        print(f"{do}Lỗi khi rời nhóm: {e}{end}")
        logging.error(f"Error leaving groups: {e}")

def block_and_unfriend_all_friends(client):
    try:
        friends = client.fetchAllFriends()
        if not check_api_response(friends):
            print(f"{do}Không thể lấy danh sách bạn bè để chặn và xóa.{end}")
            logging.error("Failed to fetch friend list for blocking/unfriending")
            return

        for friend in friends:
            user_id = friend.get('userId')
            if user_id:
                client.blockUser(user_id)
                client.unfriendUser(user_id)
                print(f"{luc}Đã chặn và xóa bạn {user_id}{end}")
                logging.info(f"Blocked and unfriended {user_id}")
                time.sleep(2)  # Increased delay

    except Exception as e:
        print(f"{do}Lỗi khi chặn và xóa bạn bè: {e}{end}")
        logging.error(f"Error blocking/unfriending: {e}")

def spam_report(client, report_count=10):
    try:
        friends = client.fetchAllFriends()
        if not check_api_response(friends):
            print(f"{do}Không thể lấy danh sách bạn bè để report.{end}")
            logging.error("Failed to fetch friend list for reporting")
            return

        reported_count = 0
        for friend in friends[:report_count]:
            user_id = friend.get('userId')
            if user_id:
                client.sendReport(
                    target_id=user_id,
                    reason="Spam or harassment",
                    target_type="user"
                )
                print(f"{luc}Đã gửi report cho {user_id}{end}")
                logging.info(f"Reported user {user_id}")
                reported_count += 1
                time.sleep(2)  # Increased delay

    except Exception as e:
        print(f"{do}Lỗi khi spam report: {e}{end}")
        logging.error(f"Error sending reports: {e}")

def change_avatar(client, image_paths):
    try:
        if image_paths and all(os.path.exists(img) for img in image_paths):
            client.changeAccountAvatar(image_paths[0])
            print(f"{luc}Đã thay đổi avatar thành công{end}")
            logging.info("Changed avatar successfully")
        else:
            print(f"{do}Không tìm thấy ảnh để thay đổi avatar{end}")
            logging.error("No valid image for avatar change")
    except Exception as e:
        print(f"{do}Lỗi khi thay đổi avatar: {e}{end}")
        logging.error(f"Error changing avatar: {e}")
        if "zpw_sek" in str(e):
            print(f"{do}Kiểm tra lại cookie - zpw_sek có thể bị thiếu hoặc không đúng.{end}")
            logging.error("Invalid or missing zpw_sek in cookie")
            return False
        return False
    return True

def run_main_ngu():
    clear_screen()
    banner()

    imei, cookie = get_device_info()
    print(f"{vang}IMEI: {imei}{end}")
    print(f"{vang}Cookie: {json.dumps(cookie, indent=2)}{end}")
    logging.info(f"Using IMEI: {imei}, Cookie: {json.dumps(cookie)}")

    client = ZaloAPI('</>', '</>', imei=imei, session_cookies=cookie)
    
    try:
        profile = client.fetchAccountInfo().profile
        print(f"{luc}Đã xác thực tài khoản: {profile.get('displayName', 'Unknown')}{end}")
        logging.info(f"Authenticated account: {profile.get('displayName', 'Unknown')}")
    except Exception as e:
        print(f"{do}Không thể xác thực tài khoản: {e}{end}")
        print(f"{do}Vui lòng kiểm tra lại IMEI và cookie.{end}")
        logging.error(f"Authentication failed: {e}")
        return

    message_text = "Attack By Mdung"
    max_retries = 3

    while True:
        retry_count = 0
        try:
            image_paths = get_random_images_from_folder('./pha', count=3)
            if not change_avatar(client, image_paths):
                print(f"{do}Thất bại khi thay đổi avatar, bỏ qua bước này.{end}")
                logging.warning("Skipped avatar change due to failure")

            user = client.fetchAccountInfo().profile
            random_name = generate_random_name()
            client.changeAccountSetting(
                name=random_name,
                dob='2000-01-01',
                gender=int(user.get('gender', 1)),
                biz={}
            )
            print(f"{luc}Đã đổi tên thành: {random_name}{end}")
            logging.info(f"Changed name to: {random_name}")

            spam_all_groups(client, message_text, image_paths, spam_count=30)
            spam_all_friends(client, message_text, image_paths, spam_count=30)
            leave_all_groups(client, imei)
            block_and_unfriend_all_friends(client)
            spam_report(client, report_count=10)

            print(f"{luc}Hoàn thành một chu kỳ, nghỉ 5 giây...{end}")
            logging.info("Completed one cycle, resting for 5 seconds")
            time.sleep(5)
        except Exception as e:
            print(f"{do}Lỗi trong vòng lặp chính: {e}{end}")
            logging.error(f"Main loop error: {e}")
            if "zpw_sek" in str(e):
                print(f"{do}Session có thể đã hết hạn. Vui lòng lấy cookie mới và khởi động lại.{end}")
                logging.error("Session expired, zpw_sek error")
                break
            retry_count += 1
            if retry_count >= max_retries:
                print(f"{do}Đã vượt quá số lần thử lại ({max_retries}), thoát chương trình.{end}")
                logging.error(f"Exceeded max retries ({max_retries}), exiting")
                break
            print(f"{vang}Thử lại sau 5 giây... (Lần {retry_count}/{max_retries}){end}")
            logging.info(f"Retrying after 5 seconds, attempt {retry_count}/{max_retries}")
            time.sleep(5)

class Bot(ZaloAPI):
    def __init__(self, imei, session_cookies):
        super().__init__('api_key', 'secret_key', imei, session_cookies)

    def fetch_groups(self):
        try:
            all_groups = self.fetchAllGroups()
            group_list = []
            for group_id in all_groups.gridVerMap:
                group_info = self.fetchGroupInfo(group_id)
                group_name = group_info.gridInfoMap[group_id]["name"]
                group_list.append({'id': group_id, 'name': group_name})
            return group_list
        except Exception as e:
            print(f"❌ Lỗi lấy nhóm: {e}")
            return []

    def fetch_members(self, group_id):
        try:
            group_info = self.fetchGroupInfo(group_id)
            mem_ver_list = group_info.gridInfoMap[group_id]["memVerList"]
            member_ids = [mem.split("_")[0] for mem in mem_ver_list]
            members = []
            for uid in member_ids:
                try:
                    user_info = self.fetchUserInfo(uid)
                    user_data = user_info.changed_profiles[uid]
                    members.append({'id': user_data['userId'], 'name': user_data['displayName']})
                except:
                    members.append({'id': uid, 'name': f"User_{uid}"})
            return members
        except Exception as e:
            print(f"❌ Lỗi lấy thành viên: {e}")
            return []
def run_poll_loop():
    show_banner()

    imei = input("🔑 Nhập IMEI: ").strip()
    cookie_str = input("🍪 Nhập Cookie JSON: ").strip()
    cookies = parse_cookie_string(cookie_str)
    if not cookies:
        sys.exit()

    bot = Bot(imei, cookies)
    groups = bot.fetch_groups()

    if not groups:
        print("⚠️ Không tìm thấy nhóm.")
        sys.exit()

    print("\n📋 Danh sách nhóm:")
    for i, g in enumerate(groups, 1):
        print(f"{i}. {g['name']} | ID: {g['id']}")

    pick = input("👉 Nhập STT nhóm muốn gửi poll: ").strip()
    selected_indexes = parse_selection(pick, len(groups))
    if not selected_indexes:
        sys.exit()

    poll_file = input("📁 Nhập tên file chứa lựa chọn poll (vd: abc.txt): ").strip()
    if not os.path.exists(poll_file):
        print("❌ File không tồn tại.")

class Bot(ZaloAPI):
    def __init__(self, imei, cookies, delay, msg):
        super().__init__('api_key', 'secret_key', imei, cookies)
        self.imei = imei
        self.cookies = cookies
        self.delay = delay
        self.msg = msg

    def fetch_groups(self):
        try:
            data = self.fetchAllGroups()
            groups = []
            for gid in data.gridVerMap:
                try:
                    info = self.fetchGroupInfo(gid)
                    name = info.gridInfoMap[gid]["name"]
                    groups.append({'id': gid, 'name': name})
                    time.sleep(0.5)
                except Exception as e:
                    print(f"[{self.imei}] Lỗi lấy nhóm: {e}")
            return groups
        except Exception as e:
            print(f"[{self.imei}] ❌ Lỗi fetch nhóm: {e}")
            return []

    def spam(self, gid, name, delay, ttl, stop_event):
        count = 0
        while not stop_event.is_set():
            try:
                self.sendSticker(
                    stickerType=7,
                    stickerId=27598,
                    cateId=10425,
                    thread_id=gid,
                    thread_type=ThreadType.GROUP,
                    ttl=ttl if ttl > 0 else None  
                )
                count += 1
                print(f"[{self.imei}] 📤 {count} → {name}")
            except Exception as e:
                print(f"[{self.imei}] ⚠️ Lỗi: {e}")
            time.sleep(delay)

def run_input_bot():
    imei = input("\n📱 IMEI: ")
    cookie = input("🍪 Cookie (dạng {'zalo_session':'abc123'}): ")
    try:
        cookies = eval(cookie)
        if not isinstance(cookies, dict):
            print("❌ Cookie phải là dict!")
            return None
    except:
        print("❌ Cookie không hợp lệ!")
        return None
    return Bot(imei, cookies)

    print("===Địt Mẹ Mày ===")

    bots = []
    while True:
        bot = input_bot()
        if bot:
            bots.append(bot)
            if input("Thêm tài khoản khác? (y/n): ").lower() != 'y':
                break
    if not bots:
        print("❌ Không có tài khoản!")
        return

    for bot in bots:
        print(f"\n🔍 Lấy nhóm cho IMEI {bot.imei}...")
        bot.groups = bot.fetch_groups()
        for i, g in enumerate(bot.groups, 1):
            print(f"{i}. {g['name']}")

    choice = input("\n👉 Chọn nhóm (vd: 1,2,3): ")
    delay = float(input("⏱ Delay (giây): "))

    
    ttl = 0  
    while True:
        try:
            ttl_seconds = float(input("⏰ Nhập thời gian tự hủy (giây): "))
            if ttl_seconds <= 0:
                print("Thời gian TTL phải lớn hơn 0!")
                continue
            ttl = int(ttl_seconds * 6000)
            break
        except ValueError:
            print("Thời gian TTL phải là số!")

    try:
        idx = [int(x.strip()) - 1 for x in choice.split(',')]
    except:
        print("❌ Lỗi nhập nhóm!")
        return

    stop = threading.Event()
    threads = []

    for bot in bots:
        for i in idx:
            if 0 <= i < len(bot.groups):
                g = bot.groups[i]
                t = threading.Thread(target=bot.spam, args=(g['id'], g['name'], delay, ttl, stop))
                t.start()
                threads.append(t)
                print(f"🚀 {bot.imei} spam {g['name']}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Dừng tất cả...")
        stop.set()
        for t in threads:
            t.join()
        print("✅ Đã dừng bot.")
        
def main_menu():
    while True:
        clear_screen()
        draw_box("CÁC CHỨC NĂNG CỦA TOOL Mdung W Qhung", [
            "1. 🚀 Treo Ngôn",
            "2. ✨ Réo Nhiều Người",
            "3. 🍭Treo Video",
            "4. 📝 Treo Ngôn 5 Màu Không Tag",
            "5. 🖼️ Treo Ảnh",
            "6. 🌈 Réo Màu",
            "7. 🤐 Mute Thành Viên",
            "8. 💬 Attack Acc",
            "9. 📤 Treo Poll",
            "10. 🌌 Treo Stikcer",
            "0. ❌ Thoát tool ",
            "Tool Treo Zalo By Manh Dung W Quang Hung | Mua Tool Đa App Ib Zalo 0946572012"
        ], Colors.CYAN)
        choice = input("👉 Chọn chức năng: ").strip()
        if choice == "1":
            run_mode_treongon()
        elif choice == "2":
            run_tag_spam()
        elif choice == "3":
            run_treongon()
        elif choice == "4":
            run_treongon_text()
        elif choice == "5":
            run_treoanh()
        elif choice == "6":
            run_tag_spam_color()
        elif choice == "7":
            auto_mute_box()
        elif choice == "8":
            run_main_ngu()
        elif choice == "9":
            run_poll_loop()
        elif choice == "10":
            run_input_bot()
        elif choice == "0":
            break
        else:
            input("⚠️ Sai lựa chọn, nhấn Enter thử lại...")

if __name__ == "__main__":
    if check_password():
        main_menu()
