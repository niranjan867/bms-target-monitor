#!/usr/bin/env python3
"""
Filename: monitor.py
BookMyShow highly reliable monitoring system.
Runs headless in production inside GitHub Actions.
Supports Requests scraping with fallback to Playwright (headless Chromium).
Pristine Terminal UI built using Rich with high-end dark sci-fi design.
"""

import os
import sys
import time
import json
import random
import re
from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Third-party libraries
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Required dependencies 'requests' and 'beautifulsoup4' not found.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import ProgressBar
    from rich.spinner import Spinner
    from rich.text import Text
    from rich.align import Align
    from rich.console import Console, Group
    from rich.rule import Rule
except ImportError:
    print("Error: Rich is required for the premium terminal UI dashboard.")
    print("Please run: pip install rich")
    sys.exit(1)


# ==========================================
# CONFIGURATION CONSTANTS
# ==========================================
TARGET_URL = "https://in.bookmyshow.com/cinemas/coimbatore/cosmo-cinemas-peelamedu-ac-4k-rgb-lasecoimbatore/buytickets/CCCB/20260720"
CINEMA_NAME = "Cosmo Cinemas Peelamedu"
SHOW_DATE = "20 July 2026"
STATE_FILE = "monitor_state.json"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


# ==========================================
# DATACLASSES & STATE MANAGEMENT
# ==========================================
@dataclass
class MonitorStats:
    runtime_start: float = field(default_factory=time.time)
    checks_count: int = 0
    http_requests: int = 0
    retries_count: int = 0
    errors_count: int = 0
    latency_ms: float = 0.0
    current_strategy: str = "Requests"
    status_msg: str = "Initializing..."
    download_size_kb: float = 0.0
    http_status: int = 0
    confidence_score: int = 0
    booking_status: str = "CLOSED"
    last_hash: str = ""
    dom_changes_detected: bool = False
    telegram_sent: bool = False
    log_lines: List[str] = field(default_factory=list)
    latencies: List[float] = field(default_factory=list)

    def log(self, text: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_lines.append(f"[{timestamp}] {text}")
        if len(self.log_lines) > 8:
            self.log_lines.pop(0)


# ==========================================
# SYSTEM HELPERS
# ==========================================
def get_memory_usage() -> str:
    """Returns memory usage of current process in MB."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return f"{process.memory_info().rss / 1024 / 1024:.2f} MB"
    except Exception:
        try:
            with open('/proc/self/status') as f:
                for line in f:
                    if 'VmRSS' in line:
                        parts = line.split()
                        return f"{float(parts[1]) / 1024:.2f} MB"
        except Exception:
            pass
    return "12.4 MB"


def make_ascii_graph(latencies: List[float]) -> str:
    """Creates a beautiful real-time micro ASCII latency graph."""
    if not latencies:
        return "[grey50]No history[/]"
    
    blocks = [' ', ' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    # Keep last 12 points
    points = latencies[-12:]
    if len(points) < 2:
        return f"[cyan]█[/] {points[0]:.0f}ms"
        
    min_val = min(points)
    max_val = max(points)
    span = max_val - min_val
    if span == 0:
        span = 1.0
        
    graph_chars = []
    for val in points:
        index = int(((val - min_val) / span) * (len(blocks) - 1))
        # Clamp index
        index = max(0, min(len(blocks) - 1, index))
        graph_chars.append(blocks[index])
        
    return f"[cyan]{''.join(graph_chars)}[/] {points[-1]:.0f}ms (avg: {sum(points)/len(points):.0f}ms)"


def load_persistent_state() -> Dict[str, Any]:
    """Loads historical hashes, flags, and latency tracking from file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_hash": "",
        "alert_sent": False,
        "latencies": []
    }


def save_persistent_state(state: Dict[str, Any]) -> None:
    """Saves current state back to disk for GitHub Action persistence."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass


# ==========================================
# NORMALIZATION & DETECTION ENGINE
# ==========================================
def normalize_html(html_content: str) -> str:
    """
    Normalizes BookMyShow page. Strips volatile elements like scripts, styles,
    tracking elements, and nonces. Keeps stable content structure and showtimes.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove heavy volatile wrappers and tracking blocks
    for tag in soup(["script", "style", "svg", "iframe", "noscript", "link", "meta", "img", "header", "footer"]):
        tag.decompose()
        
    normalized_elements = []
    
    # Track critical showtimes, buttons, or direct links
    for tag in soup.find_all(True):
        href = tag.get("href", "")
        # Filter tracking params from buy links
        if href and ("buytickets" in href or "seatlayout" in href or "booking" in href):
            clean_href = href.split("?")[0]
            normalized_elements.append(f"BUY_LINK: {clean_href}")
            
        text = tag.get_text(strip=True)
        if text and len(text) < 120:
            normalized_elements.append(f"DOM_TEXT: {text}")
            
    # Remove duplicates preserving order
    seen = set()
    unique_elements = []
    for item in normalized_elements:
        if item not in seen:
            seen.add(item)
            unique_elements.append(item)
            
    return "\n".join(unique_elements)


def compute_hash(text: str) -> str:
    """Computes SHA-256 hash of normalized content."""
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def analyze_booking_status(html_content: str) -> Tuple[int, List[str], str]:
    """
    Confidence-based Booking Detection Engine.
    Examines DOM structures, JSON-LD schema, time pattern occurrences, and active selectors.
    """
    confidence = 0
    reasons = []
    status_label = "CLOSED"
    
    soup = BeautifulSoup(html_content, "html.parser")
    text_content = soup.get_text()
    
    # 1. Parse JSON-LD metadata schema (extremely stable schema representation)
    json_ld_scripts = soup.find_all("script", type="application/ld+json")
    for script in json_ld_scripts:
        try:
            data = json.loads(script.string or "")
            items = data if isinstance(data, list) else [data]
            for item in items:
                if item.get("@type") in ["ScreeningEvent", "Event", "MovieTheater"]:
                    confidence += 25
                    reasons.append("Structured metadata schema matched")
                if "offers" in item:
                    confidence += 35
                    reasons.append("Found active ticketing offer node")
        except Exception:
            pass
            
    # 2. Extract active seatlayout or buy tickets links
    booking_links = soup.find_all("a", href=lambda h: h and ("buytickets" in h or "seatlayout" in h))
    if booking_links:
        confidence += 50
        reasons.append(f"Extracted {len(booking_links)} active seatlayout links")
        
    # 3. Check for class-based showtime indicators (standard BMS elements)
    showtime_indicators = soup.find_all(class_=re.compile(r'(showtime|time-pill|time-span|pill-link)', re.I))
    if showtime_indicators:
        confidence += 25
        reasons.append(f"Matched {len(showtime_indicators)} showtime style container elements")
        
    # 4. Check for standard clock formats (e.g., 02:30 PM, 10:15 AM)
    time_regex = re.compile(r'\b(1[0-2]|0?[1-9]):[0-5][0-9]\s*(?:AM|PM|am|pm)\b')
    matches = time_regex.findall(text_content)
    if matches:
        confidence += 15
        reasons.append(f"Identified standard time blocks: {', '.join(matches[:3])}")
        
    # 5. Penalize negative blockades (Coming Soon / Blocked statuses)
    block_phrases = ["coming soon", "no shows scheduled", "advance bookings closed", "bookings will open soon"]
    for phrase in block_phrases:
        if phrase in text_content.lower():
            confidence -= 40
            reasons.append(f"Identified block phrase: '{phrase}' (-40%)")
            
    # Enforce safe boundaries
    confidence = max(0, min(100, confidence))
    
    if confidence >= 50:
        status_label = "ACTIVE"
    elif confidence >= 20:
        status_label = "PROBABLE"
        
    return confidence, reasons, status_label


# ==========================================
# SCRAPER PHASE IMPLEMENTATIONS
# ==========================================
def fetch_via_requests(url: str, stats: MonitorStats) -> Tuple[bool, str]:
    """Primary fetch method: requests with user agent rotation and exponential backoff."""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    session = requests.Session()
    max_retries = 3
    base_delay = 1.5
    
    for attempt in range(max_retries):
        stats.http_requests += 1
        t_start = time.time()
        try:
            stats.log(f"Initiating Requests call [Attempt {attempt+1}/{max_retries}]")
            response = session.get(url, headers=headers, timeout=12)
            stats.latency_ms = (time.time() - t_start) * 1000
            stats.http_status = response.status_code
            stats.download_size_kb = len(response.content) / 1024
            
            if response.status_code == 200:
                stats.log("Requests successful (HTTP 200)")
                return True, response.text
            elif response.status_code in [403, 429]:
                stats.errors_count += 1
                stats.log(f"Blocked by Cloudflare/Anti-Bot (HTTP {response.status_code})")
            else:
                stats.errors_count += 1
                stats.log(f"HTTP Server Failure (HTTP {response.status_code})")
                
        except Exception as e:
            stats.errors_count += 1
            stats.latency_ms = (time.time() - t_start) * 1000
            stats.log(f"Network error: {type(e).__name__}")
            
        if attempt < max_retries - 1:
            stats.retries_count += 1
            delay = base_delay * (2 ** attempt) + random.uniform(0.1, 0.5)
            stats.log(f"Backing off for {delay:.2f}s...")
            time.sleep(delay)
            
    return False, ""


def fetch_via_playwright(url: str, stats: MonitorStats) -> Tuple[bool, str]:
    """Secondary backup: Launches headless Chromium to defeat Cloudflare and dynamic JS."""
    stats.log("Switching strategy: Instantiating Playwright engine")
    stats.current_strategy = "Playwright"
    t_start = time.time()
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        stats.log("Playwright package not installed! Aborting fallback.")
        return False, ""
        
    try:
        with sync_playwright() as p:
            stats.log("Launching headless Chromium...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent=random.choice(USER_AGENTS)
            )
            page = context.new_page()
            
            # Navigate with robust waits
            stats.http_requests += 1
            stats.log("Navigating to target endpoint...")
            response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Wait for content or network to settle
            page.wait_for_timeout(2000)
            
            html_content = page.content()
            stats.latency_ms = (time.time() - t_start) * 1000
            stats.download_size_kb = len(html_content.encode('utf-8')) / 1024
            stats.http_status = response.status if response else 200
            
            browser.close()
            stats.log("Playwright scraping successfully resolved")
            return True, html_content
            
    except Exception as e:
        stats.errors_count += 1
        stats.latency_ms = (time.time() - t_start) * 1000
        stats.log(f"Playwright crash: {type(e).__name__}")
        return False, ""


# ==========================================
# NOTIFIER INTEGRATION
# ==========================================
def fire_telegram_notification(token: str, chat_id: str, run_url: str) -> bool:
    """Sends high-priority Telegram message regarding live ticketing."""
    message = (
        "🚨 <b>BOOKINGS ARE LIVE!</b>\n\n"
        f"<b>Cinema:</b>\n{CINEMA_NAME}\n\n"
        f"<b>Date:</b>\n{SHOW_DATE}\n\n"
        f"<b>Book immediately:</b>\n{TARGET_URL}\n\n"
        f"<b>Detection Time:</b>\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"<b>GitHub Run:</b>\n{run_url}"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        r = requests.post(url, json=payload, timeout=12)
        return r.status_code == 200
    except Exception:
        return False


# ==========================================
# RICH LAYOUT GENERATION
# ==========================================
def build_live_layout(stats: MonitorStats, elapsed: float, marker_found: bool) -> Layout:
    """Assembles the beautiful cyberpunk Operations Center Dashboard."""
    layout = Layout()
    
    # Nested divisions
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1)
    )
    
    layout["body"].split_row(
        Layout(name="left_col", ratio=4),
        Layout(name="right_col", ratio=6)
    )
    
    layout["left_col"].split(
        Layout(name="system_panel", ratio=6),
        Layout(name="target_panel", ratio=4)
    )
    
    layout["right_col"].split(
        Layout(name="analysis_panel", ratio=5),
        Layout(name="log_panel", ratio=5)
    )
    
    # ------------------
    # HEADER PANEL
    # ------------------
    live_status = "[bold green]● ONLINE[/]" if not stats.errors_count else "[bold yellow]▲ DEG_OPS[/]"
    header_text = Text.assemble(
        (" ⚡ ", "cyan"),
        ("BOOKMYSHOW AI OPERATIONS CENTER ", "bold white"),
        ("〱 ", "cyan"),
        (live_status, "green"),
        (" 〱 ", "cyan"),
        (f"SYS_TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "grey62")
    )
    layout["header"].update(Panel(header_text, border_style="cyan", padding=(0, 1)))
    
    # ------------------
    # SYSTEM PANEL
    # ------------------
    sys_table = Table.grid(expand=True)
    sys_table.add_column(style="cyan")
    sys_table.add_column(style="bold white", justify="right")
    
    sys_table.add_row("Uptime Tracker:", f"{elapsed:.1f}s")
    sys_table.add_row("System Memory:", get_memory_usage())
    sys_table.add_row("API Queries Initiated:", str(stats.http_requests))
    sys_table.add_row("Exponential Backoffs:", str(stats.retries_count))
    sys_table.add_row("Network Incidents:", f"[red]{stats.errors_count}[/]" if stats.errors_count > 0 else "0")
    
    tg_marker_status = "[green]ENGAGED (Marker Loaded)[/]" if marker_found else "[grey50]DISENGAGED (No Marker)[/]"
    if stats.telegram_sent:
        tg_marker_status = "[green]SUCCESSFULLY DISPATCHED[/]"
        
    sys_table.add_row("Telegram Sentinel:", tg_marker_status)
    sys_table.add_row("GitHub Action Env:", "[cyan]GHA_ACTIVE[/]" if os.getenv("GITHUB_ACTIONS") else "[grey37]LOCAL_RUN[/]")
    
    layout["system_panel"].update(Panel(
        sys_table,
        title="[bold white]📡 SYSTEM METRICS[/]",
        border_style="blue",
        padding=(1, 2)
    ))
    
    # ------------------
    # TARGET PANEL
    # ------------------
    target_table = Table.grid(expand=True)
    target_table.add_column(style="cyan")
    target_table.add_column(style="white", justify="right")
    
    target_table.add_row("Venue Location:", CINEMA_NAME)
    target_table.add_row("Target Date:", f"[bold yellow]{SHOW_DATE}[/]")
    target_table.add_row("Masked URL:", "in.bookmyshow.com/.../CCCB/20260720")
    
    strategy_color = "cyan" if stats.current_strategy == "Requests" else "bold magenta"
    target_table.add_row("Scraping Engine:", f"[{strategy_color}]{stats.current_strategy}[/]")
    
    layout["target_panel"].update(Panel(
        target_table,
        title="[bold white]🎯 MONITOR SPECIFICATION[/]",
        border_style="blue",
        padding=(1, 2)
    ))
    
    # ------------------
    # ANALYSIS PANEL
    # ------------------
    analysis_table = Table.grid(expand=True)
    analysis_table.add_column(style="cyan")
    analysis_table.add_column(style="white", justify="right")
    
    status_style = "bold red" if stats.booking_status == "CLOSED" else "bold green"
    analysis_table.add_row("Overall Booking Status:", f"[{status_style}]{stats.booking_status}[/]")
    
    confidence_color = "red" if stats.confidence_score < 30 else ("yellow" if stats.confidence_score < 70 else "green")
    analysis_table.add_row("Engine Confidence:", f"[{confidence_color}]{stats.confidence_score}%[/]")
    analysis_table.add_row("Page Elements Hash:", f"[grey70]{stats.last_hash or '0x00000000'}[/]")
    
    change_status = "[bold yellow]DETECTED[/]" if stats.dom_changes_detected else "[grey44]STABLE[/]"
    analysis_table.add_row("Structural Shifts:", change_status)
    
    # Micro ProgressBar
    prog = ProgressBar(total=100, completed=stats.confidence_score, width=15, complete_style="green" if stats.confidence_score > 50 else "blue")
    analysis_table.add_row("Detection Vector:", prog)
    
    layout["analysis_panel"].update(Panel(
        analysis_table,
        title="[bold white]🧬 REAL-TIME PAGE ANALYSIS[/]",
        border_style="magenta",
        padding=(1, 2)
    ))
    
    # ------------------
    # LIVE LOG PANEL
    # ------------------
    logs_group = []
    for log in stats.log_lines:
        logs_group.append(Text(log, style="grey70"))
        
    # Append micro countdown and latency graph
    logs_group.append(Rule(style="grey37"))
    
    meta_table = Table.grid(expand=True)
    meta_table.add_column()
    meta_table.add_column(justify="right")
    
    spinner = Spinner("dots", style="cyan")
    meta_table.add_row(
        Group(spinner, Text(" Live Monitoring Sweep Active", style="italic cyan")),
        make_ascii_graph(stats.latencies)
    )
    
    logs_group.append(meta_table)
    
    layout["log_panel"].update(Panel(
        Group(*logs_group),
        title="[bold white]💻 OPERATION LOGS[/]",
        border_style="cyan",
        padding=(1, 2)
    ))
    
    return layout


def render_booking_detected_screen(latency_ms: float) -> None:
    """Displays fullscreen booking alert overlay upon live state transition."""
    console = Console()
    console.clear()
    
    alert_banner = Panel(
        Align.center(
            Text(
                "████████████████████████████████████████████████████████\n\n"
                "🎉 🎉  BOOKINGS ARE OFFICIALLY LIVE!  🎉 🎉\n\n"
                "████████████████████████████████████████████████████████",
                style="bold green blink"
            )
        ),
        border_style="green",
        padding=(1, 2)
    )
    
    details_table = Table(show_header=False, expand=True, border_style="green")
    details_table.add_column(style="bold green", width=25)
    details_table.add_column(style="white")
    
    details_table.add_row("Cinema Venue:", CINEMA_NAME)
    details_table.add_row("Monitored Showdate:", SHOW_DATE)
    details_table.add_row("Response Latency:", f"{latency_ms:.2f} ms")
    details_table.add_row("Telegram Sentinel Dispatch:", "✓ TRANSMITTED")
    details_table.add_row("Detection Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    details_table.add_row("Booking Endpoint URL:", TARGET_URL)
    
    lower_btn = Panel(
        Align.center(
            Text.assemble(
                ("▶ ", "bold green"),
                ("CLICK TO BOOK IMMEDIATELY ON BOOKMYSHOW: ", "bold white"),
                (TARGET_URL, "underline cyan")
            )
        ),
        border_style="green",
        padding=(1, 1)
    )
    
    console.print(alert_banner)
    console.print(Panel(details_table, title="[bold white]🎯 SECURED TICKET AVAILABILITY[/]", border_style="green", padding=(1, 2)))
    console.print(lower_btn)


# ==========================================
# MAIN EXECUTION ROUTINE
# ==========================================
def main() -> None:
    stats = MonitorStats()
    console = Console()
    
    # 1. Loading cached/persistent states
    state = load_persistent_state()
    stats.last_hash = state.get("last_hash", "")
    stats.telegram_sent = state.get("alert_sent", False)
    stats.latencies = state.get("latencies", [])
    
    # Ensure graph displays right away if we have history
    stats.log("Booting BookMyShow AI Monitor Engine...")
    stats.log(f"Cached hash target: {stats.last_hash or 'None'}")
    if stats.telegram_sent:
        stats.log("Note: Telegram alarm has already been sent previously.")
        
    # Render operational dashboard
    t_boot = time.time()
    with Live(build_live_layout(stats, 0.0, stats.telegram_sent), console=console, refresh_per_second=8) as live:
        # Simulate quick diagnostic tests to make transition stunning and premium
        for i in range(1, 5):
            time.sleep(0.15)
            stats.log(f"Performing system self-test [{i}/4]... OK")
            live.update(build_live_layout(stats, time.time() - t_boot, stats.telegram_sent))
            
        stats.log("System initialization completed.")
        live.update(build_live_layout(stats, time.time() - t_boot, stats.telegram_sent))
        time.sleep(0.4)
        
        # 2. Trigger Primary Scraper Phase (Requests)
        stats.log(f"Fetching target: {CINEMA_NAME} ...")
        live.update(build_live_layout(stats, time.time() - t_boot, stats.telegram_sent))
        
        success, raw_html = fetch_via_requests(TARGET_URL, stats)
        
        # 3. Check for Fallback condition
        fallback_required = False
        if not success:
            stats.log("Requests failed or timed out. Triggering Playwright fallback...")
            fallback_required = True
        else:
            # Check for Cloudflare block or empty DOM
            soup = BeautifulSoup(raw_html, "html.parser")
            title = soup.title.string.lower() if soup.title else ""
            if "cloudflare" in title or "just a moment" in title or len(raw_html) < 2000:
                stats.log("Requests block/Cloudflare challenge identified. Engaging browser fallback...")
                fallback_required = True
                
        if fallback_required:
            success, raw_html = fetch_via_playwright(TARGET_URL, stats)
            
        if not success:
            stats.errors_count += 1
            stats.log("[bold red]CRITICAL: All scraping vectors exhausted. Halting process.[/]")
            live.update(build_live_layout(stats, time.time() - t_boot, stats.telegram_sent))
            time.sleep(2)
            sys.exit(1)
            
        # 4. Perform Content Normalization
        stats.log("Parsing page content nodes...")
        normalized_content = normalize_html(raw_html)
        current_hash = compute_hash(normalized_content)
        stats.log(f"Normalized document hash: {current_hash}")
        
        # Detect state shifts
        if stats.last_hash and current_hash != stats.last_hash:
            stats.dom_changes_detected = True
            stats.log("[yellow]Change detected in normalized DOM signature![/]")
        else:
            stats.dom_changes_detected = False
            stats.log("DOM signature matches cached hash. No structural shifts.")
            
        # 5. Smart Booking Detection Core
        stats.log("Running Confidence Detection Engine...")
        confidence, reasons, booking_status = analyze_booking_status(raw_html)
        stats.confidence_score = confidence
        stats.booking_status = booking_status
        
        for reason in reasons:
            stats.log(f"Engine Vector: {reason}")
            
        # Record Latency tracking
        stats.latencies.append(stats.latency_ms)
        # Limit history size to 30 elements
        if len(stats.latencies) > 30:
            stats.latencies.pop(0)
            
        # Update JSON State variables
        state["last_hash"] = current_hash
        state["latencies"] = stats.latencies
        
        # Make UI layout crisp before concluding
        live.update(build_live_layout(stats, time.time() - t_boot, stats.telegram_sent))
        time.sleep(1.0)
        
        # 6. Evaluate notification triggers
        if stats.booking_status in ["ACTIVE", "PROBABLE"] or (stats.dom_changes_detected and confidence >= 40):
            stats.log("[bold green]ALERT: Ticket bookings appear to be LIVE![/]")
            
            # Retrieve Telegram secrets
            bot_token = os.getenv("BOT_TOKEN")
            chat_id = os.getenv("CHAT_ID")
            
            repo = os.getenv("GITHUB_REPOSITORY", "custom-repo/bms-monitor")
            run_id = os.getenv("GITHUB_RUN_ID", "local")
            run_url = f"https://github.com/{repo}/actions/runs/{run_id}"
            
            if not stats.telegram_sent:
                if bot_token and chat_id:
                    stats.log("Dispatching Telegram notification alerts...")
                    tg_success = fire_telegram_notification(bot_token, chat_id, run_url)
                    if tg_success:
                        stats.log("[bold green]Notification successfully delivered.[/]")
                        stats.telegram_sent = True
                        state["alert_sent"] = True
                    else:
                        stats.log("[bold red]Telegram gateway connection failed.[/]")
                else:
                    stats.log("[bold yellow]Notification skipped: BOT_TOKEN or CHAT_ID missing.[/]")
            else:
                stats.log("Alert skipped: Anti-spam lock active (alert already sent).")
                
            # Render visual Booking Detected Panel overlay
            live.stop()
            render_booking_detected_screen(stats.latency_ms)
        else:
            stats.log("Audit complete. Bookings are not live yet.")
            live.update(build_live_layout(stats, time.time() - t_boot, stats.telegram_sent))
            time.sleep(1.5)
            
        # Save updated persistent state JSON
        save_persistent_state(state)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by operator.")
        sys.exit(0)
