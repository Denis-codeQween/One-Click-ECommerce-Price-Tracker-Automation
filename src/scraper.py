import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def fetch_catalog():
    """
    Scrapes product data cleanly and reliably across multiple pages 
    without fragile UI localization clicks, running in a minimized window mode.
    """
    base_url = "https://aliexpress.ru/category/1270/remote-control-toys?g=y&page=1&searchInfo=AzT%2BtiZWqR6GNiTNxKD6OEWkWrdKC1N7wqbtkGxTni4oMNU%2BDZrCYIjzOCqhLffMVNbNGAoboEQ3Ju%2FWVCP9SmMQf6zFG2z10nszvc%2Bv6y2LAdZIJKZyAmA1ytxqgonf8%2BeJqq3eWff0gIPR%2FVgLEJrQPHb9zLpltL%2BbFQAcgOaA%2BgFXRpNirQhM&spm=a2g2w.home.0.0.388d250591L5yb"
    print("🚀 Initializing Chrome browser...")

    options = Options()
    options.add_argument("--start-minimized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    
    # Принудительно сворачиваем окно браузера в панель задач
    try:
        driver.minimize_window()
    except Exception:
        pass

    products_data = []
    seen_titles = set()

    try:
        for page_num in range(1, 6):
            if len(products_data) >= 100:
                break

            page_url = f"{base_url}&page={page_num}"
            print(f"🌐 Navigating to page {page_num}: {page_url}")
            
            driver.get(page_url)
            time.sleep(4)

            current_url = driver.current_url
            page_source = driver.page_source

            if "punish" in current_url or "captcha" in page_source.lower():
                print("\n" + "=" * 65)
                print("⚠️ [WARNING] AliExpress security check (Captcha) detected!")
                print("👉 Please solve the captcha manually in the browser window.")
                print("=" * 65 + "\n")
                
                input("⏸️ Press Enter in this console AFTER you have solved the captcha...")
                time.sleep(3)

            print(f"📜 Scrolling down on page {page_num}...")
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1.5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            cards = soup.find_all("div", attrs={"data-type": "UniversalSnippet"})
            print(f"📦 Found {len(cards)} raw product cards on page {page_num}.")

            for card in cards:
                if len(products_data) >= 100:
                    break
                try:
                    # 1. Title extraction
                    title_elem = card.find("div", attrs={"data-type": "PartWrap-Text"}, title=True)
                    if title_elem and title_elem.get("title"):
                        title = title_elem["title"].strip()
                    else:
                        title_elem = card.find("div", attrs={"data-type": "PartWrap-Text"})
                        title = title_elem.text.strip() if title_elem else "Unknown Title"

                    if title == "Unknown Title" or title in seen_titles:
                        continue

                    text_blocks = card.find_all("div", attrs={"data-type": "PartWrap-Text"})

                    # 2. Price extraction
                    price_str = ""
                    for block in text_blocks:
                        text = block.text.strip()
                        if any(curr in text for curr in ["$", "US $", "USD", "₸", "₽"]) and "sold" not in text and "★" not in text:
                            price_str = text
                            break

                    if not price_str:
                        for block in text_blocks:
                            text = block.text.strip()
                            if len(text) > 2 and any(char.isdigit() for char in text) and "sold" not in text and "★" not in text:
                                if "." in text or "," in text:
                                    price_str = text
                                    break

                    price = 0.0
                    if price_str:
                        cleaned = re.sub(r'[^\d\.]', '', price_str.replace(',', '.'))
                        try:
                            price = float(cleaned)
                        except ValueError:
                            price = 0.0

                    if price > 0.5:
                        seen_titles.add(title)
                        sku = f"ALI-{len(products_data) + 1:03d}"
                        products_data.append({
                            "sku": sku,
                            "title": title,
                            "price": price
                        })
                except Exception:
                    continue

    finally:
        driver.quit()
        print("🔒 Browser session closed.")

    print(f"[INFO] Successfully collected total of {len(products_data)} unique products.")
    return products_data

if __name__ == "__main__":
    print(fetch_catalog()[:3])
