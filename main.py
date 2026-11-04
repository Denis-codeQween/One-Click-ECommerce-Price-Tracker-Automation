import sys
import os
import ctypes
import pandas as pd

# Add the current src directory to module search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import fetch_catalog
from reporter import generate_excel_report
from notifier import send_telegram_alert

def minimize_console():
    """Minimizes the command prompt console window to the taskbar."""
    if sys.platform == "win32":
        try:
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd != 0:
                # 6 = SW_MINIMIZE (minimize window)
                ctypes.windll.user32.ShowWindow(hwnd, 6)
        except Exception as e:
            print(f"[WARNING] Could not minimize console window: {e}")

def process_price_fluctuations(current_data):
    """
    Compares fresh data with the baseline CSV file by PRODUCT TITLE,
    tracks any price fluctuations, and automatically updates the baseline.
    """
    current_df = pd.DataFrame(current_data)
    
    raw_dir = "data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    latest_raw_path = os.path.join(raw_dir, "latest_catalog.csv")
    
    changes_detected = []
    
    if os.path.exists(latest_raw_path):
        try:
            old_df = pd.read_csv(latest_raw_path, sep=';')
            
            name_col = "title" if "title" in old_df.columns else "Product Name"
            price_col = "price" if "price" in old_df.columns else "Price"
            
            new_prices_map = dict(zip(current_df["title"], current_df["price"]))
            
            rows_final = []
            
            for idx, row in old_df.iterrows():
                title = row[name_col]
                
                raw_old_price = str(row[price_col]).replace(',', '.').strip()
                price_old = round(float(raw_old_price), 2)
                
                if title in new_prices_map:
                    raw_new_price = str(new_prices_map[title]).replace(',', '.').strip()
                    price_new = round(float(raw_new_price), 2)
                else:
                    price_new = price_old
                    
                price_change = round(price_new - price_old, 2)
                
                # Track any deviation (both price increases and decreases)
                if abs(price_change) >= 0.01:
                    status = "CHANGED"
                    changes_detected.append({
                        "title": title,
                        "old_price": price_old,
                        "new_price": price_new,
                        "change": price_change
                    })
                else:
                    status = "STABLE"
                    
                rows_final.append({
                    "No": idx + 1,
                    "sku": row.get("sku", f"ALI-{idx+1:03d}"),
                    "Product Name": title,
                    "Price": price_new,
                    "Status": status,
                    "Price Change": price_change,
                    "Old Price": price_old
                })
                
            df_final = pd.DataFrame(rows_final)
            
            # IMPORTANT: Automatically update the baseline catalog with current prices,
            # so that new prices become the baseline (old_price) on the next run.
            save_df = pd.DataFrame({
                "sku": df_final["sku"],
                "title": df_final["Product Name"],
                "price": df_final["Price"]
            })
            save_df.to_csv(latest_raw_path, index=False, encoding="utf-8-sig", sep=';')
            print(f"[INFO] Baseline catalog successfully updated at {latest_raw_path}")
            
            return df_final, changes_detected
            
        except Exception as e:
            print(f"[WARNING] Error reading baseline CSV: {e}")
            
    # Save initial snapshot
    current_df.to_csv(latest_raw_path, index=False, encoding="utf-8-sig", sep=';')
    print(f"[INFO] Saved initial baseline to {latest_raw_path}")
    
    return create_default_dataframe(current_df), changes_detected

def create_default_dataframe(current_df):
    rows_final = []
    for idx, row in current_df.iterrows():
        price = round(float(str(row["price"]).replace(',', '.')), 2)
        rows_final.append({
            "No": idx + 1,
            "sku": row.get("sku", f"ALI-{idx+1:03d}"),
            "Product Name": row["title"],
            "Price": price,
            "Status": "NEW",
            "Price Change": 0,
            "Old Price": price
        })
    return pd.DataFrame(rows_final)

if __name__ == "__main__":
    # Minimize console window on startup
    minimize_console()
    
    print("=== Starting 1-Click E-Commerce Price Tracker ===")
    print("[INFO] Fetching live catalog data...")
    
    current_data = fetch_catalog()
    
    if current_data:
        print("[INFO] Processing report and checking price fluctuations...")
        
        # 1. Process data, look for changes, and update database
        df_final, changes_detected = process_price_fluctuations(current_data)
        
        # 2. Generate Excel report
        generate_excel_report(df_final)
        
        # 3. Send Telegram notifications if prices changed
        if changes_detected:
            print(f"[INFO] {len(changes_detected)} price change(s) detected! Sending Telegram alert...")
            
            # Compact notification format with correct currency (₸)
            msg = "🚨 AliExpress Price Fluctuations Detected!\n\n"
            for item in changes_detected:
                sign = "+" if item["change"] > 0 else ""
                msg += f"📦 {item['title']}\n"
                msg += f"💰 Price: {item['new_price']} ₸ (Old: {item['old_price']} ₸, Diff: {sign}{item['change']} ₸)\n\n"
                
            send_telegram_alert(msg.strip())
        else:
            print("[INFO] No price changes detected. Status is stable.")
            
        print("=== Price Tracking Cycle Completed Successfully ===")
    else:
        print("[ERROR] Failed to fetch product catalog.")