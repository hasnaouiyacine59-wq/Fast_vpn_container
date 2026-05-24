import time, random, os, re, cv2, numpy as np


def _human_scroll(page):
    """Scroll down to bottom then back up like a human."""
    # get total page height
    total_height = page.evaluate("document.body.scrollHeight")
    current = 0
    # scroll down in chunks until bottom
    while current < total_height:
        step = random.randint(200, 500)
        page.evaluate(f"window.scrollBy(0, {step})")
        current += step
        time.sleep(random.uniform(0.3, 0.9))
        # re-check height in case page loaded more content
        total_height = page.evaluate("document.body.scrollHeight")
    time.sleep(random.uniform(0.8, 1.5))
    # scroll back up in chunks
    while current > 0:
        step = random.randint(150, 400)
        page.evaluate(f"window.scrollBy(0, -{step})")
        current -= step
        time.sleep(random.uniform(0.2, 0.6))


TEMPLATE_OK = os.path.join(os.path.dirname(__file__), 'src', 'ok.png')

def _find_and_click_ok(page, timeout=30):
    """Take screenshots and use OpenCV template matching to find and click ok.png."""
    template = cv2.imread(TEMPLATE_OK, cv2.IMREAD_COLOR)
    if template is None:
        print("   [journy] ⚠️  src/ok.png not found")
        return False
    th, tw = template.shape[:2]
    deadline = time.time() + timeout
    while time.time() < deadline:
        # screenshot as numpy array
        png = page.screenshot()
        arr = np.frombuffer(png, np.uint8)
        screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= 0.85:
            cx = max_loc[0] + tw // 2
            cy = max_loc[1] + th // 2
            print(f"   [journy] ✅ ok.png found (conf={max_val:.2f}) clicking ({cx},{cy})")
            page.mouse.click(cx, cy)
            return True
        time.sleep(1)
    print("   [journy] ⚠️  ok.png not matched within timeout")
    return False


def journy_func(page):
    """Task for 'Just a moment...' title (Cloudflare challenge)."""
    print("   [journy] waiting 10s...")
    time.sleep(10)
    _find_and_click_ok(page)
    # wait for Cloudflare to resolve and title to change
    print("   [journy] waiting for redirect after ok click...")
    for _ in range(30):
        try:
            t = page.title()
            if t and "just a moment" not in t.lower() and "nur einen moment" not in t.lower() and "..." not in t.lower():
                print(f"   [journy] ✅ resolved → {t}")
                return False  # return False so caller keeps looping to pick up new title
        except Exception:
            pass
        time.sleep(1)
    print("   [journy] ⚠️  timed out waiting for resolution")


def error_502(page):
    """Task for 502 error — reload and retry scroll."""
    print("   [task] 502 error: reloading...")
    try:
        page.reload(wait_until='networkidle', timeout=30000)
        print("   [task] 502 reloaded, scrolling...")
        _human_scroll(page)
    except Exception as e:
        print(f"   [task] 502 reload failed: {e}")


def statewins(page):
    """Task for Statewins title."""
    print("   [task] statewins: scrolling...")
    _human_scroll(page)
    print("   [task] statewins: done")


DOMAINS = ["techxbox.eu.org", "beta-sig.eu.org", "itchigho.eu.org", "sec4891.eu.org", "youoneshell.eu.org"]

def _gen_email():
    user = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(6, 10)))
    return f"{user}@{random.choice(DOMAINS)}"

def crypto_gateway(page):
    """Task for Crypto payment gateway — click accept button and wait."""
    accept = page.query_selector(
        'button:has-text("Accept"), button:has-text("accept"), '
        'button:has-text("Agree"), button:has-text("Continue"), '
        'input[value*="Accept" i], input[value*="Agree" i]'
    )
    if accept:
        print(f"   [crypto] ✅ accept button found: {(accept.inner_text() or '').strip()}")
        accept.click()
        print("   [crypto] ✅ clicked")
    else:
        print("   [crypto] ⚠️  accept button not found")
    time.sleep(random.uniform(3, 5))

def lock_com(page):
    """Task for Lock.com — find email field, fill generated email, press Enter."""
    selectors = [
        '#email-mobile',
        'input[name="email"]',
        'input[type="email"]',
        'input[placeholder*="email" i]',
    ]
    email_field = None
    for sel in selectors:
        try:
            page.wait_for_selector(sel, timeout=10000)
            email_field = page.query_selector(sel)
            if email_field:
                print(f"   [lock] ✅ email field found via: {sel}")
                break
        except Exception:
            continue

    if email_field:
        email = _gen_email()
        print(f"   [lock] filling: {email}")
        email_field.click()
        time.sleep(random.uniform(0.4, 0.8))
        email_field.fill('')
        email_field.type(email, delay=random.randint(60, 130))
        time.sleep(random.uniform(0.3, 0.6))
        email_field.press('Enter')
        print("   [lock] ✅ Enter pressed")
        wait = random.uniform(4, 7)
        print(f"   [lock] waiting {wait:.1f}s for submit...")
        time.sleep(wait)
    else:
        print("   [lock] ⚠️  email field not found")


def _hostinger_horizons(page):
    """Task for Hostinger Horizons — wait for full load, dump all elements."""
    print(f"   [horizons] title: {page.title()} | url: {page.url}")
    try:
        page.wait_for_load_state('networkidle', timeout=30000)
    except Exception:
        pass
    time.sleep(3)
    elements = page.query_selector_all('*')
    print(f"   [horizons] {len(elements)} elements on page")
    for el in elements:
        try:
            tag = el.evaluate("e => e.tagName")
            txt = (el.inner_text() or '').strip()[:80].replace('\n', ' ')
            print(f"      <{tag}> {txt}")
        except Exception:
            pass


def _bc_fill_form(page):
    """Fill the BC.Game signup dialog with generated email/password."""
    try:
        page.wait_for_selector('div.login-layout-dialog input[type=password]', timeout=120000)
    except Exception:
        print("   [bc.game] ⚠️  signup form not found")
        return False

    dialog = page.query_selector('div.login-layout-dialog')
    email = _gen_email()
    password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$', k=12))

    email_input = dialog.query_selector('input:not([type=password])')
    if email_input:
        email_input.click()
        email_input.click(click_count=3)
        email_input.fill(email)
        box = email_input.bounding_box()
        page.mouse.click(box['x'] + box['width'] / 2, box['y'] - 30)

    pwd_input = dialog.query_selector('input[type=password]')
    if pwd_input:
        pwd_input.click(click_count=3)
        pwd_input.fill(password)

    checkbox = dialog.query_selector('button.checkbox')
    if checkbox:
        already_checked = checkbox.evaluate("""e => {
            if (e.getAttribute('aria-checked') === 'true') return true;
            if (e.classList.contains('checked') || e.classList.contains('active') || e.classList.contains('btn-like--active')) return true;
            const ico = e.querySelector('.checkbox-ico');
            if (ico) {
                const s = window.getComputedStyle(ico);
                if (s.opacity !== '0' && s.display !== 'none' && s.visibility !== 'hidden') return true;
            }
            return false;
        }""")
        if not already_checked:
            checkbox.click()

    submit = dialog.query_selector('button[type=submit]')
    if submit:
        submit.click()
    else:
        page.keyboard.press('Enter')
    print(f"   [bc.game] ✅ form submitted — email={email} password={password}")

    try:
        page.wait_for_selector('button[type=submit]', state='hidden', timeout=10000)
        print("   [bc.game] ✅ signup complete")
    except Exception:
        print("   [bc.game] ⚠️  submit button still visible")
    time.sleep(10)
    return True


def bc_game_func(page):
    """Task for 'BC.Game' title — find and click Join button."""
    print(f"   [bc.game] title: {page.title()} | url: {page.url}")
    try:
        page.wait_for_load_state('networkidle', timeout=30000)
    except Exception:
        pass
    time.sleep(3)

    join_selector = (
        'button:has-text("Join"), a:has-text("Join"), '
        'button:has-text("join"), a:has-text("join"), '
        '[class*="join" i], [id*="join" i]'
    )
    try:
        page.wait_for_selector(join_selector, timeout=10000)
        btn = page.query_selector(join_selector)
        if btn:
            txt = (btn.inner_text() or '').strip()
            print(f"   [bc.game] ✅ Join button found: '{txt}' — clicking")
            btn.click()
            print("   [bc.game] waiting 10s for form to load...")
            time.sleep(10)

            # find Sign Up button by innerText — language agnostic
            signup_texts = ["sign up", "signup", "register", "s'inscrire", "registrarse",
                            "registrar", "cadastrar", "anmelden", "registrieren", "注册", "가입"]
            signup_btn = page.evaluate("""(texts) => {
                for (const el of document.querySelectorAll('button, a')) {
                    const t = (el.innerText || '').trim().toLowerCase();
                    if (texts.some(s => t === s || t.startsWith(s))) {
                        el.click();
                        return el.innerText.trim();
                    }
                }
                return null;
            }""", signup_texts)
            if signup_btn:
                print(f"   [bc.game] ✅ Sign Up clicked: '{signup_btn}'")
                # fill the signup form
                _bc_fill_form(page)
            else:
                print("   [bc.game] ⚠️  Sign Up button not found")
        else:
            print("   [bc.game] ⚠️  Join button not found")
    except Exception as e:
        print(f"   [bc.game] ⚠️  Join button error: {e}")


def flirtbate(page):
    """Task for Flirtbate title — dismiss age gate, fill email, submit."""
    # 1. Age gate: click "I Agree"
    try:
        page.wait_for_selector('button:has-text("I Agree")', timeout=10000)
        page.click('button:has-text("I Agree")')
        print("   [flirtbate] ✅ age gate dismissed")
        time.sleep(random.uniform(1, 2))
    except Exception as e:
        print(f"   [flirtbate] ⚠️  age gate not found: {e}")

    # 2. Fill email and submit
    lock_com(page)


TASKS = {
    "bc.game": bc_game_func,
    "bc": bc_game_func,
    "statewins": statewins,
    "flirtbate": flirtbate,
    "error 502": error_502,
    "eloniai": lambda page: _human_scroll(page),
    "just a moment": journy_func,
    "nur einen moment": journy_func,
    "...": journy_func,
    "lock.com": lock_com,
    "crypto payment gateway": crypto_gateway,
    "hostinger horizons": lambda page: _hostinger_horizons(page),
}

# def landingbc(page):
#     """Task for landingbc.com — click Join Now then dump."""
#     try:
#         page.wait_for_selector('button:has-text("Join Now"), a:has-text("Join Now")', timeout=15000)
#         page.click('button:has-text("Join Now"), a:has-text("Join Now")')
#         print("   [landingbc] ✅ Join Now clicked")
#         time.sleep(random.uniform(2, 4))
#     except Exception as e:
#         print(f"   [landingbc] ⚠️  Join Now not found: {e}")
#     _dump_page(page)


URL_TASKS = {
#    "landingbc.com": landingbc,
}


def run(title: str, url: str, page):
    """Match on title first, fallback to URL if title is empty."""
    if title:
        for key, fn in TASKS.items():
            if key in title.lower():
                fn(page)
                return True
    else:
        for key, fn in URL_TASKS.items():
            if key in url:
                fn(page)
                return True
    return False
