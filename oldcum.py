import os, json, time, random, requests, argparse, platform, uuid, socket, sys, itertools, threading, shutil, glob
import log as L
sys.stdout.reconfigure(encoding='utf-8')
os.environ['CAMOUFOX_NO_UPDATE'] = '1'

# ── clean leftover browser profiles + artifacts from previous sessions ──
for _p in glob.glob('/tmp/playwright_firefoxdev_profile-*') + glob.glob('/tmp/playwright-artifacts-*'):
    try:
        shutil.rmtree(_p)
        L.debug('clean', f'removed {_p}')
    except Exception:
        pass

VERSION = "fastvpn v 2.0.0 beta"
BANNER = f"""
  ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗     ██████╗ ██╗███╗   ██╗
  ████╗  ██║██╔═══██╗██║   ██║██╔══██╗    ██╔══██╗██║████╗  ██║
  ██╔██╗ ██║██║   ██║██║   ██║███████║    ██║  ██║██║██╔██╗ ██║
  ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║    ██║  ██║██║██║╚██╗██║
  ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║    ██████╔╝██║██║ ╚████║
  ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝    ╚═════╝ ╚═╝╚═╝  ╚═══╝
                                                    {VERSION}
"""
print(BANNER)

def _device_id():
    """Stable device ID based on hostname + MAC."""
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return f"{socket.gethostname()}-{mac}"

_did = _device_id()
_sys = f"{platform.system()} {platform.release()} ({platform.machine()}) py{platform.python_version()}"
try:
    import psutil
    _mem = psutil.virtual_memory()
    _hw  = f"cpu={psutil.cpu_percent(interval=0.5)}% ram={_mem.total//(1024**3)}GB/{_mem.percent}%used"
except ImportError:
    _hw = f"cpu={platform.processor() or 'n/a'}"
print(f"[device] {_did} | {_sys} | {_hw}\n")

parser = argparse.ArgumentParser()
parser.add_argument('-c', metavar='COUNTRY', help='Use /ip/<country> endpoint and set exit IP (e.g. -c sw)')
parser.add_argument('--local', action='store_true', help='Use local tcp_files/udp_files instead of /etc/')
args = parser.parse_args()

_BASE = os.path.dirname(os.path.abspath(__file__)) if args.local else '/etc'

from camoufox.sync_api import Camoufox
from camoufox.addons import DefaultAddons
import task_action
from user_agnt import user_agent_list as _ua_pool

_UA_FILTERS = {
    'windows': lambda ua: 'Windows NT' in ua and 'Android' not in ua,
    'macos':   lambda ua: 'Macintosh' in ua or 'Mac OS X' in ua,
    'linux':   lambda ua: ('X11' in ua or 'Linux' in ua) and 'Android' not in ua and 'Macintosh' not in ua,
}
USER_AGENTS = {
    os_key: [ua for ua in _ua_pool if fn(ua)] or _ua_pool
    for os_key, fn in _UA_FILTERS.items()
}
# import creep_session

URL_2     = 'https://cryptyos.nl.eu.org/'
URL_3     = 'https://zacrypto.nl.eu.org/'
# URL_3     = 'https://cryptyos.eu.org/'
# URL_3     = 'https://cryptyos.eu.org/'
# URL_3     = 'https://cryptyos.eu.org/'
CHECK_API = 'https://f-api-s36l.onrender.com/api/v1'
REPORT_URL = os.getenv('REPORT_URL', f'{CHECK_API}/status')
# REPORT_URL = os.getenv('REPORT_URL', 'https://f-api-exb5.onrender.com/api/v1/status')

OS_PROFILES = [
    {'os': 'macos',   'window': (1440, 900)},
    {'os': 'macos',   'window': (1024, 768)},
    {'os': 'macos',   'window': (1680, 1050)},
    {'os': 'macos',   'window': (2560, 1440)},
    {'os': 'windows', 'window': (1366, 768)},
    {'os': 'windows', 'window': (1920, 1080)},
    {'os': 'windows', 'window': (1280, 800)},
    {'os': 'windows', 'window': (1600, 900)},
    {'os': 'windows', 'window': (2560, 1440)},
    {'os': 'windows', 'window': (1280, 1024)},
    {'os': 'linux',   'window': (1280, 800)},
    {'os': 'linux',   'window': (1920, 1080)},
    {'os': 'linux',   'window': (1600, 900)},
]

OS_FONTS = {
    'windows': ['Arial', 'Times New Roman', 'Georgia', 'Verdana', 'Trebuchet MS', 'Comic Sans MS', 'Impact', 'Courier New'],
    'macos':   ['Helvetica', 'Geneva', 'Monaco', 'Optima', 'Futura', 'Arial', 'Times New Roman', 'Courier New'],
    'linux':   ['DejaVu Sans', 'Liberation Sans', 'Ubuntu', 'FreeSans', 'Arial', 'Times New Roman'],
}


# ── NordVPN logic (commented out — replaced by new VPN logic) ──
# NORDVPN_COUNTRIES = [
#     'Albania', 'Andorra', 'Argentina', 'Armenia',
#     'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados',
#     'Belgium', 'Belize', 'Bermuda', 'Bhutan', 'Bolivia', 'Bosnia_And_Herzegovina',
#     'Brazil', 'Bulgaria', 'Cambodia', 'Canada', 'Cayman_Islands',
#     'Colombia', 'Costa_Rica', 'Cote_Divoire', 'Croatia',
#     'Cyprus', 'Czech_Republic', 'Denmark', 'Ecuador', 'Egypt',
#     'El_Salvador', 'Estonia', 'Finland', 'France', 'Georgia',
#     'Germany', 'Greece', 'Greenland', 'Guam', 'Guatemala', 'Honduras',
#     'Hong_Kong', 'Hungary', 'Iceland', 'Indonesia', 'Ireland',
#     'Isle_Of_Man', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jersey',
#     'Kuwait', 'Lao_Peoples_Democratic_Republic', 'Latvia',
#     'Lebanon', 'Libyan_Arab_Jamahiriya', 'Liechtenstein', 'Lithuania', 'Luxembourg',
#     'Malaysia', 'Malta', 'Mauritius', 'Mexico', 'Moldova', 'Monaco',
#     'Mongolia', 'Montenegro', 'Nepal',
#     'Netherlands', 'New_Zealand', 'North_Macedonia', 'Norway', 'Pakistan',
#     'Panama', 'Papua_New_Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland',
#     'Portugal', 'Puerto_Rico', 'Qatar', 'Romania', 'Serbia',
#     'Singapore', 'Slovakia', 'Slovenia', 'Somalia', 'South_Africa', 'South_Korea',
#     'Spain', 'Sri_Lanka', 'Suriname', 'Sweden', 'Switzerland', 'Taiwan',
#     'Thailand', 'Tunisia', 'Turkey',
#     'Ukraine', 'United_Arab_Emirates', 'United_Kingdom', 'United_States', 'Uruguay',
#     'Uzbekistan', 'Venezuela', 'Vietnam',
# ]
#
# _country_queue = []
#
# def _next_country():
#     global _country_queue
#     if not _country_queue:
#         _country_queue = NORDVPN_COUNTRIES[:]
#         random.shuffle(_country_queue)
#     return _country_queue.pop()
#
# import subprocess
#
# def nordvpn_connect(country=None):
#     """Connect NordVPN, optionally to a specific country. Returns True on success."""
#     cmd = ['nordvpn', 'connect'] + ([country] if country else [])
#     result = subprocess.run(cmd, capture_output=True, text=True, check=False)
#     out = result.stdout + result.stderr
#     if "couldn't connect" in out or "Please check your internet" in out:
#         return False
#     for _ in range(2):
#         try:
#             status = subprocess.check_output(['nordvpn', 'status'], text=True)
#             if 'Connected' in status:
#                 return True
#             if "couldn't connect" in status or 'Disconnected' in status:
#                 return False
#         except Exception:
#             pass
#         time.sleep(1)
#     return False
#
# def nordvpn_disconnect():
#     subprocess.run(['nordvpn', 'disconnect'], check=False, capture_output=True)
#     for _ in range(30):
#         try:
#             out = subprocess.check_output(['nordvpn', 'status'], text=True)
#             if 'Disconnected' in out:
#                 time.sleep(2)
#                 return
#             if 'Disconnecting' in out:
#                 print('[nordvpn] disconnecting, waiting...')
#         except Exception:
#             pass
#         time.sleep(2)
#     print('[nordvpn] warning: disconnect timed out')
#
# def nordvpn_current_ip(retries=30, delay=4):
#     """Poll `nordvpn status` until Connected and return the IP."""
#     time.sleep(5)
#     for attempt in range(retries):
#         try:
#             out = subprocess.check_output(['nordvpn', 'status'], text=True)
#             if 'Connected' in out:
#                 for line in out.splitlines():
#                     if 'IP:' in line:
#                         return line.split('IP:')[-1].strip()
#         except Exception:
#             pass
#         print(f'[nordvpn] waiting for IP... ({attempt+1}/{retries})')
#         time.sleep(delay)
#     raise RuntimeError('NordVPN did not connect in time')
#
# FAILED_COUNTRIES_FILE = os.path.join(os.path.dirname(__file__), 'failed_countries.txt')
#
# def _log_failed_country(country):
#     with open(FAILED_COUNTRIES_FILE, 'a') as f:
#         f.write(f"{country}\n")
#
# def rotate_nordvpn(current_ip=None, country=None):
#     """Disconnect, reconnect (random or to country), wait for new IP."""
#     print('[nordvpn] disconnecting...')
#     nordvpn_disconnect()
#     current_country = country
#     while True:
#         msg = f'[nordvpn] connecting{"  to " + current_country if current_country else " randomly"}...'
#         stop = threading.Event()
#         def _spin(m=msg):
#             for f in itertools.cycle('⣾⣽⣻⢿⡿⣟⣯⣷'):
#                 if stop.is_set(): break
#                 sys.stdout.write(f'\r{f} {m}')
#                 sys.stdout.flush()
#                 time.sleep(0.1)
#             sys.stdout.write('\r' + ' ' * (len(m) + 4) + '\r')
#         t = threading.Thread(target=_spin, daemon=True)
#         t.start()
#         ok = nordvpn_connect(current_country)
#         stop.set(); t.join()
#         if ok:
#             break
#         print(f'[nordvpn] ❌ connect failed for {current_country}, switching...')
#         _log_failed_country(current_country)
#         nordvpn_disconnect()
#         current_country = _next_country()
#         print(f'[nordvpn] 🌍 trying → {current_country}')
#         time.sleep(5)
#     new_ip = nordvpn_current_ip()
#     if current_ip and new_ip == current_ip:
#         print('[nordvpn] same IP, rotating again...')
#         return rotate_nordvpn(current_ip, current_country)
#     print(f'[nordvpn] new IP: {new_ip}')
#     return new_ip
#
# # CHECK_API = 'https://f-api-exb5.onrender.com/api/v1'
#
# def check_ip(ip):
#     """Return (approved, response). Retries on API errors with 1s sleep."""
#     for attempt in range(3):
#         try:
#             r = requests.get(f'{CHECK_API}/{ip}', timeout=10).json()
#             return r.get('used') != 'yes', r
#         except Exception as e:
#             print(f"[check_ip] ⚠️  attempt {attempt+1}/3 failed: {type(e).__name__}: {e}")
#             if attempt < 2:
#                 time.sleep(1)
#     print(f"[check_ip] ❌ all retries failed for {ip}, treating as rejected")
#     return False, {'error': 'api_unreachable'}
#
# def get_approved_ip(country=None):
#     """Connect NordVPN and keep rotating until the check API approves the IP."""
#     ip = rotate_nordvpn(country=country)
#     while True:
#         stop = threading.Event()
#         def _spin(msg=f"[*] testing {ip} ..."):
#             for f in itertools.cycle('⣾⣽⣻⢿⡿⣟⣯⣷'):
#                 if stop.is_set(): break
#                 sys.stdout.write(f'\r{f} {msg}')
#                 sys.stdout.flush()
#                 time.sleep(0.1)
#             sys.stdout.write('\r' + ' ' * (len(msg) + 4) + '\r')
#         t = threading.Thread(target=_spin, daemon=True)
#         t.start()
#         approved, resp = check_ip(ip)
#         stop.set(); t.join()
#         if approved:
#             print(f"[*] ✅ approved: {ip} → {resp}")
#             return ip
#         country = _next_country()
#         print(f"[*] ❌ rejected: {ip} → {resp}, switching country → {country}")
#         ip = rotate_nordvpn(current_ip=ip, country=country)

CC_LANG = {
    'US': ('en-US', 'America/New_York'),
    'GB': ('en-GB', 'Europe/London'),
    'DE': ('de-DE', 'Europe/Berlin'),
    'FR': ('fr-FR', 'Europe/Paris'),
    'NL': ('nl-NL', 'Europe/Amsterdam'),
    'ES': ('es-ES', 'Europe/Madrid'),
    'IT': ('it-IT', 'Europe/Rome'),
    'PL': ('pl-PL', 'Europe/Warsaw'),
    'SE': ('sv-SE', 'Europe/Stockholm'),
    'NO': ('nb-NO', 'Europe/Oslo'),
    'FI': ('fi-FI', 'Europe/Helsinki'),
    'RO': ('ro-RO', 'Europe/Bucharest'),
    'CZ': ('cs-CZ', 'Europe/Prague'),
    'AT': ('de-AT', 'Europe/Vienna'),
    'CH': ('de-CH', 'Europe/Zurich'),
    'CA': ('en-CA', 'America/Toronto'),
    'AU': ('en-AU', 'Australia/Sydney'),
    'JP': ('ja-JP', 'Asia/Tokyo'),
    'BR': ('pt-BR', 'America/Sao_Paulo'),
    'IN': ('en-IN', 'Asia/Kolkata'),
    'PT': ('pt-PT', 'Europe/Lisbon'),
    'BE': ('nl-BE', 'Europe/Brussels'),
    'DK': ('da-DK', 'Europe/Copenhagen'),
    'HU': ('hu-HU', 'Europe/Budapest'),
    'SK': ('sk-SK', 'Europe/Bratislava'),
    'HR': ('hr-HR', 'Europe/Zagreb'),
    'BG': ('bg-BG', 'Europe/Sofia'),
    'GR': ('el-GR', 'Europe/Athens'),
    'TR': ('tr-TR', 'Europe/Istanbul'),
    'RU': ('ru-RU', 'Europe/Moscow'),
    'UA': ('uk-UA', 'Europe/Kiev'),
    'LT': ('lt-LT', 'Europe/Vilnius'),
    'LV': ('lv-LV', 'Europe/Riga'),
    'EE': ('et-EE', 'Europe/Tallinn'),
    'RS': ('sr-RS', 'Europe/Belgrade'),
    'SI': ('sl-SI', 'Europe/Ljubljana'),
    'MX': ('es-MX', 'America/Mexico_City'),
    'AR': ('es-AR', 'America/Argentina/Buenos_Aires'),
    'CL': ('es-CL', 'America/Santiago'),
    'CO': ('es-CO', 'America/Bogota'),
    'PE': ('es-PE', 'America/Lima'),
    'ZA': ('en-ZA', 'Africa/Johannesburg'),
    'NG': ('en-NG', 'Africa/Lagos'),
    'EG': ('ar-EG', 'Africa/Cairo'),
    'SA': ('ar-SA', 'Asia/Riyadh'),
    'AE': ('ar-AE', 'Asia/Dubai'),
    'IL': ('he-IL', 'Asia/Jerusalem'),
    'KR': ('ko-KR', 'Asia/Seoul'),
    'CN': ('zh-CN', 'Asia/Shanghai'),
    'TW': ('zh-TW', 'Asia/Taipei'),
    'HK': ('zh-HK', 'Asia/Hong_Kong'),
    'SG': ('en-SG', 'Asia/Singapore'),
    'MY': ('ms-MY', 'Asia/Kuala_Lumpur'),
    'TH': ('th-TH', 'Asia/Bangkok'),
    'ID': ('id-ID', 'Asia/Jakarta'),
    'PH': ('en-PH', 'Asia/Manila'),
    'VN': ('vi-VN', 'Asia/Ho_Chi_Minh'),
    'PK': ('ur-PK', 'Asia/Karachi'),
    'BD': ('bn-BD', 'Asia/Dhaka'),
    'NZ': ('en-NZ', 'Pacific/Auckland'),
}

def get_ip_info(ip):
    try:
        d = requests.get(f'http://ipwho.is/{ip}', timeout=8).json()
        cc = d.get('country_code', 'US')
        locale, tz = CC_LANG.get(cc, ('en-US', 'America/New_York'))
        return {
            'ip':       ip,
            'country':  d.get('country', '?'),
            'cc':       cc,
            'city':     d.get('city', '?'),
            'locale':   locale,
            'timezone': d.get('timezone', {}).get('id', tz),
        }
    except Exception:
        return {'ip': ip, 'country': '?', 'cc': 'US', 'city': '?', 'locale': 'en-US', 'timezone': 'America/New_York'}
        return {'ip': ip, 'country': '?', 'cc': 'US', 'city': '?', 'locale': 'en-US', 'timezone': 'America/New_York'}

# ── OpenVPN connect + API approval ──
import subprocess

OVPN_DIRS   = [f'{_BASE}/tcp_files', f'{_BASE}/udp_files']
AUTH_FILE   = f'{_BASE}/auth_fvpn'
_ovpn_proc  = None

def _all_configs():
    cfgs = []
    for d in OVPN_DIRS:
        cfgs += glob.glob(os.path.join(d, '*.ovpn'))
    return cfgs

def _kill_ovpn():
    global _ovpn_proc
    if _ovpn_proc:
        try:
            _ovpn_proc.terminate()
            _ovpn_proc.wait(timeout=5)
        except Exception:
            pass
        _ovpn_proc = None
    subprocess.run([ 'pkill', '-f', 'openvpn'], capture_output=True)
    # subprocess.run(['sudo', 'pkill', '-f', 'openvpn'], capture_output=True)
    time.sleep(2)

def _ovpn_connect(cfg):
    global _ovpn_proc
    _kill_ovpn()
    L.nav('ovpn', f'connecting → {os.path.basename(cfg)}')
    open('/tmp/ovpn.log', 'w').close()  # clear log before new attempt
    up_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'openvpn-up.sh') \
                if args.local else '/etc/openvpn-up.sh'
    log_fh = open('/tmp/ovpn.log', 'w')
    _ovpn_proc = subprocess.Popen(
        ['openvpn', '--config', cfg, '--auth-user-pass', AUTH_FILE,
         '--script-security', '2', '--up', up_script],
        stdout=log_fh, stderr=log_fh
    )
    # wait up to 30s for "Initialization Sequence Completed" in log
    with L.Spinner('ovpn', f'connecting {os.path.basename(cfg)}'):
        for _ in range(30):
            time.sleep(1)
            try:
                log = open('/tmp/ovpn.log').read()
                if 'Initialization Sequence Completed' in log:
                    return True
            except Exception:
                pass
    return False

def _current_ip():
    for _ in range(5):
        try:
            return requests.get('https://api.ipify.org', timeout=6).text.strip()
        except Exception:
            time.sleep(2)
    return None

def check_ip(ip):
    for attempt in range(3):
        try:
            r = requests.get(f'{CHECK_API}/{ip}', timeout=10).json()
            return r.get('used') != 'yes', r
        except Exception as e:
            L.warn('check_ip', f'attempt {attempt+1}/3: {e}')
            if attempt < 2: time.sleep(1)
    return False, {'error': 'api_unreachable'}

def get_approved_ip_ovpn():
    configs = _all_configs()
    if not configs:
        raise RuntimeError('No .ovpn configs found in /etc/tcp_files or /etc/udp_files')
    random.shuffle(configs)
    tried = set()
    while True:
        available = [c for c in configs if c not in tried]
        if not available:
            tried.clear()
            random.shuffle(configs)
            available = configs[:]
        cfg = available[0]
        tried.add(cfg)
        connected = _ovpn_connect(cfg)
        if not connected:
            L.err('ovpn', f'failed to connect with {os.path.basename(cfg)}, trying next...')
            continue
        ip = _current_ip()
        if not ip:
            L.err('ovpn', 'could not get IP, trying next config...')
            continue
        approved, resp = check_ip(ip)
        if approved:
            L.ok('ovpn', f'approved: {ip} → {resp}')
            return ip
        L.err('ovpn', f'rejected: {ip} → {resp}, rotating...')

# ── connect OpenVPN + resolve geo ──
raw_ip = get_approved_ip_ovpn()
geo    = get_ip_info(raw_ip)
profile = random.choice(OS_PROFILES)

session_report = {
    'device_id': _device_id(),
    'ip':        geo['ip'],
    'country':   geo['country'],
    'cc':        geo['cc'],
    'city':      geo['city'],
    'locale':    geo['locale'],
    'timezone':  geo['timezone'],
    'os':        profile['os'],
    'window':    list(profile['window']),
    'titles':    [],
    'iframes':   [],
}

L.section('SESSION')
L.info('geo',     f"{geo['ip']} [{geo['cc']}] {geo['country']}, {geo['city']} | {geo['locale']} / {geo['timezone']}")
L.info('browser', f"os={profile['os']} window={profile['window']}")

with Camoufox(
    # headless="virtual",
    headless=False,
    os=profile['os'],
    window=profile['window'],
    geoip=geo['ip'],
    block_webrtc=True,
    fonts=OS_FONTS.get(profile['os'], []),
    config={'navigator.hardwareConcurrency': random.choice([4, 8, 12, 16])},
    exclude_addons=[DefaultAddons.UBO],
    i_know_what_im_doing=True,
    firefox_user_prefs={
        'network.dns.disablePrefetch': True,
        'general.useragent.override': random.choice(USER_AGENTS[profile['os']]),
    },
) as browser:
    page = browser.new_page()

    # ── creep_session capture (commented out) ──
    # report = creep_session.capture(page, tor_ip=geo['ip'])
    # sess_path = os.path.join(creep_session.SESSIONS_DIR, report['session_id'], 'creepjs.json')
    # with open(sess_path) as f:
    #     saved = json.load(f)
    # saved['geo'] = geo
    # with open(sess_path, 'w') as f:
    #     json.dump(saved, f, indent=2)
    # print(f"[geo] saved to session {report['session_id']}")

    # ── visit URL_3 first, then switch to URL_2 in the same tab ──
    def lik():
        L.section('TAB INTERACTION')
        iframes = page.query_selector_all('iframe')
        for i, fr in enumerate(iframes):
            try:
                box = fr.bounding_box()
                if not box:
                    continue
                tx = box['x'] + box['width']  * random.uniform(0.3, 0.7)
                ty = box['y'] + box['height'] * random.uniform(0.3, 0.7)
                page.mouse.move(tx, ty, steps=2)
                L.debug('tab', f'hovering iframe-{i}')
                time.sleep(0.1)

                with page.context.expect_page() as new_page_info:
                    page.mouse.click(tx, ty)
                new_tab = new_page_info.value
                new_tab.bring_to_front()
                new_tab.wait_for_load_state('load', timeout=20000)
                L.info('tab', 'new tab opened')
                last_title = None
                idle = 0
                while idle < 15:
                    try:
                        title = new_tab.title()
                        L.nav('tab', f'{repr(title)} | {new_tab.url}')
                        key = title or new_tab.url
                        if key and key != last_title:
                            last_title = key
                            idle = 0
                            if task_action.run(title, new_tab.url, new_tab):
                                break
                        else:
                            idle += 1
                    except Exception:
                        if new_tab.is_closed():
                            L.warn('tab', 'tab closed itself, exiting loop')
                            break
                        idle += 1
                    time.sleep(1)

                new_tab.close()
                pages = page.context.pages
                L.debug('tab', f'closed, tabs remaining: {len(pages)}')
                if pages:
                    pages[0].bring_to_front()
                    L.debug('tab', f'back to main: {pages[0].url}')

            except Exception as e:
                L.warn('tab', f'iframe-{i}: {e}')

    L.section('NAVIGATE')
    try:
        with L.Spinner('nav', f'loading {URL_3}'):
            page.goto(URL_3, wait_until='domcontentloaded', timeout=60000)
            page.wait_for_load_state('load', timeout=30000)
    except Exception as e:
        L.warn('nav', f'goto/load warning: {e}')
    if page.is_closed():
        L.warn('nav', f'page closed during navigation to {URL_3}, skipping')
    else:
        L.ok('nav', f'{page.title()} ({page.url})')
    time.sleep(5)

    # human mouse movement over iframe
    try:
        iframe_el = page.query_selector('iframe')
        if iframe_el:
            box = iframe_el.bounding_box()
            if box:
                safe_above = max(box['y'] - random.randint(80, 180), 5)
                page.mouse.move(box['x'] + box['width'] * random.uniform(0.2, 0.8), safe_above, steps=5)
                time.sleep(random.uniform(0.3, 0.7))
                for _ in range(2):
                    page.mouse.move(box['x'] + box['width'] * random.uniform(0.1, 0.9),
                                    box['y'] + box['height'] * random.uniform(0.05, 0.2), steps=5)
                    time.sleep(random.uniform(0.3, 0.6))
                for _ in range(3):
                    page.mouse.move(box['x'] + box['width'] * random.uniform(0.15, 0.85),
                                    box['y'] + box['height'] * random.uniform(0.2, 0.75), steps=5)
                    time.sleep(random.uniform(0.3, 0.6))
                page.mouse.move(box['x'] + box['width'] * random.uniform(0.2, 0.8),
                                max(box['y'] - random.randint(30, 80), 5), steps=5)
                L.ok('tab', 'human movement over iframe done')
    except Exception as e:
        L.warn('tab', f'hover: {e}')

    # ── read iframe content after hover ──
    L.section('IFRAME SCAN')
    try:
        iframes_on_page = page.query_selector_all('iframe')
        L.info('iframe', f'{len(iframes_on_page)} iframes on page')
        for i, fr in enumerate(iframes_on_page):
            try:
                cf = fr.content_frame()
                if not cf:
                    continue
                cf.wait_for_load_state('domcontentloaded', timeout=10000)
                seen = set()
                alts = []
                for el in cf.query_selector_all('img'):
                    alt = (el.get_attribute('alt') or '').strip()
                    if alt and alt not in seen:
                        seen.add(alt)
                        alts.append(alt)
                body_text = cf.inner_text('body').strip()[:300].replace('\n', ' ')
                entry = {'index': i, 'text': body_text, 'alts': alts}
                session_report['iframes'].append(entry)
                session_report['titles'].extend(alts)
                L.info('iframe', f'fr{i}: alts={alts} | text={body_text[:80]}')

                AD_ALTS = {'Best game to win crypto!', 'Earn While Playing', 'Advertise in this ad space', 'Top Crypto Game with BTC Dividends!'}
                NAV_ITEMS = ["Home", "Chart", "Trades", "Token", "Search", "Swap", "Portfolio", "Chains"]
                for attempt in range(3):
                    if not any(a in AD_ALTS for a in alts):
                        break
                    nav_text = random.choice(NAV_ITEMS)
                    L.nav('iframe', f'fr{i}: ad detected ({[a for a in alts if a in AD_ALTS]}), clicking nav \'{nav_text}\' (attempt {attempt+1}/3)')
                    try:
                        # escape the iframe focus by clicking outside it on the main page
                        page.mouse.click(10, 10)
                        time.sleep(random.uniform(0.2, 0.4))

                        nav_el = page.query_selector(f"text={nav_text}")
                        if nav_el:
                            box = nav_el.bounding_box()
                            if box:
                                x = box['x'] + box['width'] * random.uniform(0.3, 0.7)
                                y = box['y'] + box['height'] * random.uniform(0.3, 0.7)
                                page.mouse.move(x, y, steps=random.randint(8, 15))
                                time.sleep(random.uniform(0.2, 0.5))
                                page.mouse.click(x, y)
                                L.ok('iframe', f'fr{i}: clicked \'{nav_text}\' on main page')
                            else:
                                nav_el.click()
                        else:
                            L.warn('iframe', f'fr{i}: nav \'{nav_text}\' not found on main page')
                        cf.wait_for_load_state('domcontentloaded', timeout=10000)
                        time.sleep(random.uniform(0.8, 1.5))
                    except Exception as nav_err:
                        L.warn('iframe', f'fr{i} nav click error: {nav_err}')
                    seen = set()
                    alts = []
                    for el in cf.query_selector_all('img'):
                        alt = (el.get_attribute('alt') or '').strip()
                        if alt and alt not in seen:
                            seen.add(alt)
                            alts.append(alt)
                    body_text = cf.inner_text('body').strip()[:300].replace('\n', ' ')
                    L.info('iframe', f'fr{i} retry {attempt+1}: alts={alts} | text={body_text[:80]}')
                else:
                    if any(a in AD_ALTS for a in alts):
                        L.warn('iframe', f'fr{i}: still ad after 3 attempts, giving up')

                # if iframe resolved to a known task page, run it
                if not any(a in AD_ALTS for a in alts):
                    task_action.run(body_text[:80], '', page)

                entry = {'index': i, 'text': body_text, 'alts': alts}
                session_report['iframes'].append(entry)
                session_report['titles'].extend(alts)
            except Exception as e:
                L.warn('iframe', f'fr{i}: {e}')
    except Exception as e:
        L.warn('iframe', str(e))

    time.sleep(20)
    #new step
    lik()

    # ── load URL_2 and analyse ──
    # print(f"\n🌐  Navigating to {URL_2} ...")
    # page.goto(URL_2, wait_until='networkidle', timeout=60000)
    # print(f"✅  {page.title()} ({page.url})")

    # # ── find all iframes ──
    # iframes = page.query_selector_all('iframe')
    # print(f"[iframe] {len(iframes)} found: " + " | ".join(
    #     (fr.get_attribute('name') or fr.get_attribute('id') or f'#{i}')
    #     for i, fr in enumerate(iframes)
    # ))

    # # ── collect iframe-0 attrs + alts for report ──
    # if iframes:
    #     fr = iframes[0]
    #     iframe0_attrs = [v for a in ('src','id','name','alt','title','class') if (v := fr.get_attribute(a))]
    #     session_report['iframe0_attrs'] = iframe0_attrs
    #     try:
    #         cf = fr.content_frame()
    #         if cf:
    #             cf.wait_for_load_state('domcontentloaded', timeout=15000)
    #             seen = set()
    #             unique_alts = [alt for el in cf.query_selector_all('img')
    #                            if (alt := (el.get_attribute('alt') or '').strip()) and alt not in seen and not seen.add(alt)]
    #             if unique_alts:
    #                 print(f"[ad]     {' • '.join(unique_alts)}")
    #             session_report['iframe0_alts'] = unique_alts
    #     except Exception as e:
    #         print(f"[iframe] ⚠️  iframe-0 read error: {e}")
    # else:
    #     print("[iframe] ⚠️  no iframes found")

    # def read_iframes():
    #     """Collect ad alts from every iframe; return compact string."""
    #     parts = []
    #     try:
    #         for i, fr in enumerate(page.query_selector_all('iframe')):
    #             try:
    #                 cf = fr.content_frame()
    #                 if not cf:
    #                     continue
    #                 cf.wait_for_load_state('domcontentloaded', timeout=10000)
    #                 seen = set()
    #                 alts = [alt for el in cf.query_selector_all('img')
    #                         if (alt := (el.get_attribute('alt') or '').strip()) and alt not in seen and not seen.add(alt)]
    #                 if alts:
    #                     parts.append(f"place {i+1}: {' • '.join(alts)}")
    #                     session_report['titles'].extend(alts)
    #             except Exception:
    #                 pass
    #     except Exception:
    #         pass
    #     return '  '.join(parts)

    # def human_click(el):
    #     box = el.bounding_box()
    #     if not box:
    #         el.click()
    #         return
    #     tx = box['x'] + box['width']  * random.uniform(0.3, 0.7)
    #     ty = box['y'] + box['height'] * random.uniform(0.3, 0.7)
    #     sx = tx + random.uniform(-120, 120)
    #     sy = ty + random.uniform(-80, 80)
    #     page.mouse.move(sx, sy, steps=random.randint(5, 12))
    #     time.sleep(random.uniform(0.05, 0.15))
    #     mx = (sx + tx) / 2 + random.uniform(-40, 40)
    #     my = (sy + ty) / 2 + random.uniform(-40, 40)
    #     page.mouse.move(mx, my, steps=random.randint(8, 18))
    #     time.sleep(random.uniform(0.05, 0.12))
    #     page.mouse.move(tx, ty, steps=random.randint(6, 14))
    #     time.sleep(random.uniform(0.08, 0.25))
    #     page.mouse.click(tx, ty)

    # # ── nav links to randomly click ──
    # NAV_HREFS = ['/', '/', '/gainers']
    # # NAV_HREFS = ['/', '/', '/gainers', '/losers', '/watchlist']
    # random.shuffle(NAV_HREFS)

    # for href in NAV_HREFS:
    #     time.sleep(random.uniform(1.5, 4.0))
    #     try:
    #         el = page.query_selector(f'a[href="{href}"]')
    #         if not el:
    #             print(f"⚠️  Could not find link href={href}")
    #             continue
    #         text = (el.inner_text() or '').strip()[:40]
    #         human_click(el)
    #         try:
    #             page.wait_for_load_state('networkidle', timeout=10000)
    #         except Exception:
    #             page.wait_for_load_state('domcontentloaded', timeout=10000)
    #         ads = read_iframes()
    #         print(f"[nav] → '{text}' ({href})  [ad] {ads}")

    #         # ── after Gainers: click a random pair link ──
    #         if href == '/gainers':
    #             time.sleep(random.uniform(1.5, 3.0))
    #             pair_links = page.query_selector_all('a[href^="/pair/"]')
    #             if pair_links:
    #                 pick = random.choice(pair_links)
    #                 pair_text = (pick.inner_text() or '').strip()[:40].replace('\n', ' ')
    #                 human_click(pick)
    #                 page.wait_for_load_state('networkidle', timeout=20000)
    #                 ads = read_iframes()
    #                 print(f"[nav] → pair '{pair_text}'  [ad] {ads}")
    #                 time.sleep(random.uniform(6.5, 8.0))
    #             else:
    #                 print("[nav] ⚠️  no pair links on /gainers")

    #         # ── after Losers: click random pair, then logo ──
    #         if href == '/losers':
    #             time.sleep(random.uniform(1.5, 3.0))
    #             pair_links = page.query_selector_all('a[href^="/pair/"]')
    #             if pair_links:
    #                 pick = random.choice(pair_links)
    #                 pair_text = (pick.inner_text() or '').strip()[:40].replace('\n', ' ')
    #                 human_click(pick)
    #                 page.wait_for_load_state('networkidle', timeout=20000)
    #                 ads = read_iframes()
    #                 print(f"[nav] → pair '{pair_text}'  [ad] {ads}")
    #             else:
    #                 print("[nav] ⚠️  no pair links on /losers")
    #             time.sleep(random.uniform(6.5, 8.0))
    #             logo = page.query_selector('a.text-accent.font-bold.text-lg.tracking-tight.shrink-0[href="/"]')
    #             if logo:
    #                 human_click(logo)
    #                 page.wait_for_load_state('networkidle', timeout=20000)
    #                 ads = read_iframes()
    #                 print(f"[nav] → home logo  [ad] {ads}")
    #             else:
    #                 print("[nav] ⚠️  logo not found")
    #             time.sleep(random.uniform(4.5, 8.0))

    #     except Exception as e:
    #         print(f"[nav] ⚠️  {href}: {e}")

    # print("[done] analysis complete")

    # # ── re-read iframes after analysis (collect data only, compact print) ──
    # for i, fr in enumerate(page.query_selector_all('iframe')):
    #     try:
    #         cf = fr.content_frame()
    #         if not cf:
    #             continue
    #         cf.wait_for_load_state('domcontentloaded', timeout=10000)
    #         text = cf.inner_text('body').strip()[:300].replace('\n', ' ')
    #         seen = set()
    #         alts = [alt for el in cf.query_selector_all('img')
    #                 if (alt := (el.get_attribute('alt') or '').strip()) and alt not in seen and not seen.add(alt)]
    #         if alts:
    #             print(f"[ad]  fr{i}: {' • '.join(alts)}")
    #         session_report['iframes'].append({'index': i, 'text': text, 'alts': alts})
    #     except Exception as e:
    #         print(f"[ad]  fr{i} ⚠️  {e}")

    # ── send report ──
    print(f"\n📋  session report:\n{json.dumps(session_report, indent=2)}")
    if REPORT_URL:
        try:
            r = requests.post(REPORT_URL, json=session_report, timeout=30)
            print(f"[report] sent → {r.status_code}")
        except Exception as e:
            print(f"[report] ⚠️  {e}")

    # lik()

