import time, random, os, re, cv2, numpy as np
import log as L


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
    template = cv2.imread(TEMPLATE_OK, cv2.IMREAD_COLOR)
    if template is None:
        L.warn('journy', 'src/ok.png not found')
        return False
    th, tw = template.shape[:2]
    deadline = time.time() + timeout
    while time.time() < deadline:
        png = page.screenshot()
        arr = np.frombuffer(png, np.uint8)
        screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= 0.85:
            cx = max_loc[0] + tw // 2
            cy = max_loc[1] + th // 2
            L.ok('journy', f'ok.png found (conf={max_val:.2f}) clicking ({cx},{cy})')
            page.mouse.click(cx, cy)
            return True
        time.sleep(1)
    L.warn('journy', 'ok.png not matched within timeout')
    return False


def journy_func(page):
    L.info('journy', 'waiting 10s...')
    time.sleep(10)
    _find_and_click_ok(page)
    L.info('journy', 'waiting for redirect after ok click...')
    for _ in range(30):
        try:
            t = page.title()
            if t and "just a moment" not in t.lower() and "nur einen moment" not in t.lower() and "..." not in t.lower():
                L.ok('journy', f'resolved → {t}')
                return False
        except Exception:
            pass
        time.sleep(1)
    L.warn('journy', 'timed out waiting for resolution')


def error_502(page):
    L.warn('task', '502 error: reloading...')
    try:
        page.reload(wait_until='networkidle', timeout=30000)
        L.ok('task', '502 reloaded, scrolling...')
        _human_scroll(page)
    except Exception as e:
        L.err('task', f'502 reload failed: {e}')


def statewins(page):
    L.info('task', 'statewins: scrolling...')
    _human_scroll(page)
    L.ok('task', 'statewins: done')


DOMAINS = ["techxbox.eu.org", "beta-sig.eu.org", "itchigho.eu.org", "sec4891.eu.org", "youoneshell.eu.org"]

def _gen_email():
    user = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(6, 10)))
    return f"{user}@{random.choice(DOMAINS)}"

def crypto_gateway(page):
    accept = page.query_selector(
        'button:has-text("Accept"), button:has-text("accept"), '
        'button:has-text("Agree"), button:has-text("Continue"), '
        'input[value*="Accept" i], input[value*="Agree" i]'
    )
    if accept:
        L.ok('crypto', f'accept button found: {(accept.inner_text() or "").strip()}')
        accept.click()
    else:
        L.warn('crypto', 'accept button not found')
    time.sleep(random.uniform(3, 5))

def lock_com(page):
    selectors = [
        '#email-mobile',
        'input[name="email"]',
        'input[type="email"]',
        'input[placeholder*="email" i]',
        'input[autocomplete*="email" i]',
        'input[class*="email" i]',
        'input[id*="email" i]',
        'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="checkbox"]):not([type="radio"])',
    ]
    email_field = None
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                email_field = el
                L.ok('lock', f'email field found via: {sel}')
                break
        except Exception:
            continue

    if not email_field:
        # dump all inputs to help diagnose
        all_inputs = page.query_selector_all('input, textarea')
        L.warn('lock', f'email field not found — {len(all_inputs)} inputs on page:')
        for el in all_inputs:
            try:
                L.debug('lock', f'  type={el.get_attribute("type")} name={el.get_attribute("name")} id={el.get_attribute("id")} placeholder={el.get_attribute("placeholder")} visible={el.is_visible()}')
            except Exception:
                pass
        return

    email = _gen_email()
    L.info('lock', f'filling: {email}')
    email_field.scroll_into_view_if_needed()
    email_field.click()
    time.sleep(random.uniform(0.4, 0.8))
    email_field.fill('')
    email_field.type(email, delay=random.randint(60, 130))
    time.sleep(random.uniform(0.3, 0.6))
    email_field.press('Enter')
    L.ok('lock', 'Enter pressed')
    wait = random.uniform(4, 7)
    L.info('lock', f'waiting {wait:.1f}s for submit...')
    time.sleep(wait)


def lock_com_full(page):
    """Wait 10s, dump all interactive elements, then fill email."""
    L.section('LOCK.COM')
    L.info('lock', f'{page.title()} | {page.url}')
    L.info('lock', 'waiting 10s for page to settle...')
    time.sleep(10)

    # dump all visible interactive + text elements
    elements = page.query_selector_all('a, button, input, select, textarea, h1, h2, h3, p, label, span')
    L.info('lock', f'{len(elements)} elements found:')
    for el in elements:
        try:
            tag  = el.evaluate("e => e.tagName.toLowerCase()")
            txt  = (el.inner_text() or el.get_attribute('placeholder') or el.get_attribute('value') or '').strip()[:80].replace('\n', ' ')
            typ  = el.get_attribute('type') or ''
            name = el.get_attribute('name') or el.get_attribute('id') or ''
            desc = f'<{tag}{"["+typ+"]" if typ else ""}{"#"+name if name else ""}> {txt}'
            L.debug('lock', desc)
        except Exception:
            pass

    lock_com(page)


def _hostinger_horizons(page):
    L.info('horizons', f'{page.title()} | {page.url}')
    try:
        page.wait_for_load_state('networkidle', timeout=30000)
    except Exception:
        pass
    time.sleep(3)
    elements = page.query_selector_all('*')
    L.info('horizons', f'{len(elements)} elements on page')
    for el in elements:
        try:
            tag = el.evaluate("e => e.tagName")
            txt = (el.inner_text() or '').strip()[:80].replace('\n', ' ')
            L.debug('horizons', f'<{tag}> {txt}')
        except Exception:
            pass


def _bc_fill_form(page):
    try:
        page.wait_for_selector('div.login-layout-dialog input[type=password]', timeout=120000)
    except Exception:
        L.warn('bc.game', 'signup form not found')
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
    L.ok('bc.game', f'form submitted — email={email} password={password}')

    try:
        page.wait_for_selector('button[type=submit]', state='hidden', timeout=10000)
        L.ok('bc.game', 'signup complete')
    except Exception:
        L.warn('bc.game', 'submit button still visible')
    time.sleep(10)
    return True


def bc_game_func(page):
    L.section('BC.GAME')
    L.info('bc.game', f'{page.title()} | {page.url}')

    join_selector = (
        'button:has-text("Join"), a:has-text("Join"), '
        'button:has-text("join"), a:has-text("join"), '
        '[class*="join" i], [id*="join" i]'
    )
    try:
        page.wait_for_selector(join_selector, timeout=15000)
        btn = page.query_selector(join_selector)
        if btn:
            txt = (btn.inner_text() or '').strip()
            L.ok('bc.game', f"Join button found: '{txt}' — clicking")
            btn.click()

            signup_selector = ', '.join(
                f'button:has-text("{t}"), a:has-text("{t}")'
                for t in ["Sign Up", "Signup", "Register", "注册", "가입"]
            )
            try:
                page.wait_for_selector(signup_selector, timeout=8000)
            except Exception:
                pass

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
                L.ok('bc.game', f"Sign Up clicked: '{signup_btn}'")
                _bc_fill_form(page)
            else:
                L.warn('bc.game', 'Sign Up button not found')
        else:
            L.warn('bc.game', 'Join button not found')
    except Exception as e:
        L.err('bc.game', f'Join button error: {e}')


def flirtbate(page):
    try:
        page.wait_for_selector('button:has-text("I Agree")', timeout=10000)
        page.click('button:has-text("I Agree")')
        L.ok('flirtbate', 'age gate dismissed')
        time.sleep(random.uniform(1, 2))
    except Exception as e:
        L.warn('flirtbate', f'age gate not found: {e}')
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
    "lock.com": lock_com_full,
    "crypto payment gateway": crypto_gateway,
    "hostinger horizons": lambda page: _hostinger_horizons(page),
    "earn while playing": bc_game_func,
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
