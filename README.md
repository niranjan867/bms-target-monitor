# BookMyShow AI Monitor 📡

A highly resilient, serverless, cloud-based monitoring system for BookMyShow pages. Powered by Python 3.12, BeautifulSoup, and headless Playwright (Chromium) to cleanly bypass Cloudflare blockades. Designed to run unattended inside GitHub Actions for months, executing every 5 minutes and triggering exactly **one** instant Telegram alert when ticket sales go live.

---

## 🚀 Key Features

* **Dual-Layer Scraping**: Utilizes `requests` for fast execution, with automatic, intelligent fallback to a headless `Playwright` browser if Cloudflare challenge screens, JavaScript-rendering blocks, or empty DOMs are encountered.
* **Confidence-Based Detection Engine**: Evaluates active seat layouts, JSON-LD structured schema parsing, regex class indicators, and clock strings while penalizing negative blocks (e.g., "Coming Soon") rather than searching simple strings.
* **Anti-Spam Sentinels**: Computes SHA-256 hashes of normalised markup to track changes and leverages a local git-committed state marker to ensure exactly **one** Telegram alert is sent.
* **Modern AI Operations UI**: Displays an high-end terminal dashboard utilizing `Rich` for deep visibility into latency variations, memory consumption, backoffs, and execution logs.

---

## 🛠️ Step-by-Step Production Setup Guide

Follow these steps to deploy and activate your BookMyShow Monitor in minutes:

### 1. Create a Telegram Bot
1. Open the Telegram app and search for [@BotFather](https://t.me/BotFather).
2. Start a conversation and send `/newbot`.
3. Give your bot a user-friendly name (e.g., `BookMyShow Monitor Bot`) and a unique username ending in `_bot` (e.g., `bms_ticket_sentinel_bot`).
4. Copy the **HTTP API Token** provided by BotFather (looks like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`). This will be your `BOT_TOKEN`.

### 2. Retrieve Your Telegram Chat ID
1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram and tap `/start`.
2. It will reply with your personal numerical **Chat ID** (e.g., `987654321`). This will be your `CHAT_ID`.
3. **CRITICAL STEP**: Open a direct chat with your newly created Bot and press **Start** or send any message. Bots cannot initiate messages with users who haven't started a chat first!

### 3. Add GitHub Secrets
To secure your credentials and prevent leaking them in code:
1. Navigate to your GitHub repository in your browser.
2. Go to **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret** and add:
   * **`BOT_TOKEN`**: Paste your Telegram HTTP API Token.
   * **`CHAT_ID`**: Paste your numerical Chat ID.
4. (Optional) To enable committing the persistent state marker file (`monitor_state.json`) back to the repo, GitHub Actions automatically handles the permissions via the workflow settings, but you must make sure that **"Read and write permissions"** are enabled under **Settings** > **Actions** > **General** > **Workflow permissions**.

### 4. Upload Files to GitHub
If you are initializing a new repository:
```bash
git init
git add .
git commit -m "feat: init bms ticket sentinel monitor"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### 5. Enable GitHub Actions
By default, GitHub workflows containing scheduled cron tasks may be paused in newly created or imported repositories.
1. Click on the **Actions** tab in your repository.
2. If you see a warning about workflows, click **"I understand my workflows, go ahead and enable them"**.

### 6. Run the Workflow Manually
1. In the **Actions** tab, click on the **BookMyShow AI Monitor** workflow on the left sidebar.
2. Click the **Run workflow** dropdown on the right side.
3. Keep the branch as `main` and click the green **Run workflow** button.
4. Refresh the page after 5 seconds to watch the workflow initialize and execute!

### 7. Verifying Telegram Notifications
To test that your bot can successfully deliver messages:
1. Temporarily modify the `confidence` score check in `monitor.py` or trigger a fake alert manually to test.
2. Check your Telegram chat; you should instantly receive a structured alert detailing the venue, date, and link!

### 8. Changing the Monitored URL
To monitor a different cinema venue, movie, or date:
1. Open `monitor.py` in your code editor.
2. Locate the **Configuration Constants** section near the top:
   ```python
   TARGET_URL = "https://in.bookmyshow.com/cinemas/coimbatore/cosmo-cinemas-peelamedu-ac-4k-rgb-lasecoimbatore/buytickets/CCCB/20260720"
   CINEMA_NAME = "Cosmo Cinemas Peelamedu"
   SHOW_DATE = "20 July 2026"
   ```
3. Replace these values with your target page's URL and names, then commit and push the changes back to GitHub.

---

## 🔍 Troubleshooting Common Failures

| Issue | Root Cause | Resolution |
| :--- | :--- | :--- |
| **Telegram messages aren't arriving** | Bot not started, or incorrect token/chat ID. | Verify credentials with `curl https://api.telegram.org/bot<TOKEN>/getMe`. Ensure you started a chat with your bot. |
| **Workflow failing on setup** | Missing Playwright system dependencies. | Ensure the `.github/workflows/monitor.yml` contains `playwright install chromium --with-deps` before executing the script. |
| **No state committed back to repo** | Actions have read-only permissions by default. | Go to **Settings** > **Actions** > **General** > **Workflow permissions**, select **"Read and write permissions"**, and save. |
| **Frequent false alarms (hashes changed)** | Unstable HTML nodes (advertisements, session IDs, tracking tokens). | Our `normalize_html` parser cleans classes, inline styles, SVGs, and query params. Ensure no custom dynamic attributes are causing differences. |

---

## 🔮 Future Improvements

1. **Multi-Date Scanning**: Extend configuration to scan an array of URLs for multiple consecutive days.
2. **Auto-Reset Marker**: Allow the Telegram bot to receive incoming command messages (e.g., `/reset`) to clear the state and alert markers without manual intervention.
3. **SMS/WhatsApp Backup**: Integrate Twilio or Twilio-like APIs as secondary alarm routes.
