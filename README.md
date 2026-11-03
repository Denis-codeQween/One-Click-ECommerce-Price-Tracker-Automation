# 1-Click E-Commerce Price Tracker (AliExpress Edition)

A robust, modular Python automation tool designed for real-time e-commerce price monitoring, automated historical change detection, Telegram alerts, and formatted Excel reporting.

---

## 🚀 Key Features

- **Automated Web Scraping**: Utilizes Selenium and BeautifulSoup to extract live catalog listings, product names, IDs, and prices (configured for KZT `₸`).
- **Smart Historical Comparison**: Compares live snapshots against local CSV history (`utf-8-sig` with semicolon separation) to detect new arrivals, price drops, and price increases.
- **Telegram Notifications**: Sends instant alerts for price fluctuations with automatic chunking for long lists and robust plain-text formatting to avoid entity parsing errors.
- **Professional Reporting**: Automatically compiles structured data into clean, formatted Excel reports (`openpyxl`) with dynamic serial numbering (`№`).

---

## 🛠️ Project Architecture

```text
├── data/
│   ├── raw/                 # Historical snapshots (previous_snapshot.csv)
│   └── reports/             # Generated Excel analytics reports
├── src/
│   ├── scraper.py           # Selenium catalog parser
│   ├── reporter.py          # Excel generator (openpyxl)
│   └── notifier.py          # Telegram bot integration module
├── main.py                  # Main execution pipeline
└── requirements.txt         # Project dependencies
```

---

## 📦 Installation & Setup

1. **Clone or download** the repository to your local machine.
2. **Install dependencies** using the requirements file:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Telegram Credentials**:
   Ensure your Bot Token and Chat ID are properly configured in `src/notifier.py`. Make sure you have started a chat with your bot by sending `/start` in Telegram.

---

## 🏃‍♂️ Usage

Run the complete monitoring pipeline with a single command:
```bash
python main.py
```

### What happens during execution:
1. **Scraping**: The browser launches, pages are scrolled, and live product data is collected.
2. **Analysis**: Current prices are compared against `data/raw/previous_snapshot.csv` strictly by product title/SKU.
3. **Alerts**: If price changes are detected in existing items, clean text alerts are instantly dispatched to your Telegram chat.
4. **Reporting**: A fresh Excel spreadsheet is compiled and saved under `data/reports/`.
5. **History Update**: The historical snapshot is safely overwritten with the latest crawl data for the next run.