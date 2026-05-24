import random
import string
import time
import os
from camoufox.sync_api import Camoufox
from browserforge.fingerprints import Screen

os.environ['DISPLAY'] = ':1'

TARGET_URL = "https://landingbc.com/ac2026/crypto.html?trace_id=JXDLHP-1779529825817&od=playwc01.com"
EMAIL_DOMAINS = ["techxbox.eu.org", "beta-sig.eu.org", "itchigho.eu.org", "sec4891.eu.org", "youoneshell.eu.org"]

def human_scroll(page):
    total_height = page.evaluate("document.body.scrollHeight")
    current = 0
    while current < total_height:
        step = random.randint(200, 500)
        page.evaluate(f"window.scrollBy(0, {step})")
        current += step
        time.sleep(random.uniform(0.3, 0.9))
        total_height = page.evaluate("document.body.scrollHeight")
    time.sleep(random.uniform(0.8, 1.5))
    while current > 0:
        step = random.randint(150, 400)
        page.evaluate(f"window.scrollBy(0, -{step})")
        current -= step
        time.sleep(random.uniform(0.2, 0.6))


def gen_email():
    user = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(6, 10)))
    return f"{user}@{random.choice(EMAIL_DOMAINS)}"


def gen_password():
    chars = string.ascii_letters + string.digits + "!@#$"
    return ''.join(random.choices(chars, k=12))


def click_join(page):
    selectors = [
        'a[href*="register"], a[href*="signup"], a[href*="join"]',
        '[class*="register" i], [class*="signup" i], [class*="join" i]',
        '[id*="register" i], [id*="signup" i], [id*="join" i]',
        '[data-action*="register" i], [data-action*="join" i]',
        'button:has-text("Join"), a:has-text("Join")',
    ]
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.click()
                print("[1/3] join clicked")
                return True
        except Exception:
            continue
    print("[1/3] ⚠️  join button not found")
    return False


def click_accept(page):
    accept_selectors = [
        '[class*="accept" i], [id*="accept" i]',
        '[data-action*="accept" i]',
        'button:has-text("Accept"), a:has-text("Accept")',
    ]
    deadline = time.time() + 60
    while time.time() < deadline:
        for sel in accept_selectors:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    el.click()
                    print("[2/3] accept clicked")
                    return True
            except Exception:
                continue
        time.sleep(0.5)


def click_signup(page):
    signup_selectors = [
        'button.button-brand',
        'button.button-brand.button-m',
        'a[href*="signup"], a[href*="sign-up"], a[href*="register"]',
        '[class*="signup" i], [class*="sign-up" i], [class*="register" i]',
        '[id*="signup" i], [id*="sign-up" i], [id*="register" i]',
        '[data-action*="signup" i], [data-action*="register" i]',
        'button:has-text("Sign Up"), a:has-text("Sign Up")',
        'button:has-text("Sign up"), a:has-text("Sign up")',
        'button:has-text("Register"), a:has-text("Register")',
    ]
    for sel in signup_selectors:
        try:
            page.wait_for_selector(sel, timeout=120000)
            break
        except Exception:
            continue
    for sel in signup_selectors:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.click()
                print("[3/3] signup clicked")
                return True
        except Exception:
            continue
    print("[3/3] ⚠️  signup button not found")
    return False


def fill_signup_form(page):
    email = gen_email()
    password = gen_password()

    try:
        page.wait_for_selector('div.login-layout-dialog input[type=password]', timeout=120000)
    except Exception:
        print("[form] ⚠️  form not found")
        return False

    dialog = page.query_selector('div.login-layout-dialog')

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
    print(f"[form] ✅ submitted — email={email} password={password}")

    try:
        page.wait_for_selector('button[type=submit]', state='hidden', timeout=10000)
        print("[form] ✅ signup complete")
    except Exception:
        print("[form] ⚠️  submit button still visible")
    time.sleep(10)
    return True


def run_test(page):
    print("→ navigating...")
    page.goto(TARGET_URL, wait_until='domcontentloaded', timeout=120000)
    if click_join(page):
        try:
            click_accept(page)
        except Exception:
            pass
        if click_signup(page):
            fill_signup_form(page)


with Camoufox(
    os=["windows", "macos", "linux"],
    screen=Screen(max_width=1920, max_height=1080),
    geoip=True,
    humanize=False,
    headless=False,
    block_webrtc=True,
    locale="en-US",
) as browser:
    page = browser.new_page()
    run_test(page)
    time.sleep(10)
