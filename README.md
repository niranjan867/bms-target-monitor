# BookMyShow AI Monitor 📡

A highly resilient, serverless, cloud-based monitoring system for BookMyShow pages. Powered by Python 3.12, BeautifulSoup, and headless Playwright (Chromium) to cleanly bypass Cloudflare blockades. Designed to run unattended inside GitHub Actions for months, executing every 5 minutes and triggering exactly **one** instant Telegram alert when ticket sales go live.

---

## 🚀 Key Features

* **Dual-Layer Scraping**: Utilizes `requests` for fast execution, with automatic, intelligent fallback to a headless `Playwright` browser if Cloudflare challenge screens, JavaScript-rendering blocks, or empty DOMs are encountered.
* **Confidence-Based Detection Engine**: Evaluates active seat layouts, JSON-LD structured schema parsing, regex class indicators, and clock strings while penalizing negative blocks (e.g., "Coming Soon") rather than searching simple strings.
* **Anti-Spam Sentinels**: Computes SHA-256 hashes of normalised markup to track changes and leverages a local git-committed state marker to ensure exactly **one** Telegram alert is sent.
* **Modern AI Operations UI**: Displays an high-end terminal dashboard utilizing `Rich` for deep visibility into latency variations, memory consumption, backoffs, and execution logs.
