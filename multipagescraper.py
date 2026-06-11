from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import time
import os

def get_filename_from_url(url):
    # Extracts the last part of the URL to use as filename
    clean_url = url.strip('/').split('/')[-1]
    return f"{clean_url}.json"

def scrape_all_pages(start_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    all_data = []
    current_url = start_url
    
    try:
        while current_url and current_url != "#":
            print(f"Scraping: {current_url}")
            driver.get(current_url)
            
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'bix-div-container')))
            time.sleep(2)
            
            containers = driver.find_elements(By.CLASS_NAME, 'bix-div-container')
            for container in containers:
                try:
                    qtxt = container.find_element(By.CLASS_NAME, 'bix-td-qtxt').text
                    opts = [o.text for o in container.find_elements(By.CLASS_NAME, 'bix-td-option-val')]
                    ans = container.find_element(By.CLASS_NAME, 'jq-hdnakq').get_attribute('value')
                    exp = container.find_element(By.CLASS_NAME, 'bix-ans-description').text
                    
                    all_data.append({
                        "question": qtxt,
                        "A": opts[0] if len(opts) > 0 else "",
                        "B": opts[1] if len(opts) > 1 else "",
                        "C": opts[2] if len(opts) > 2 else "",
                        "D": opts[3] if len(opts) > 3 else "",
                        "Correct Opt": ans,
                        "Explaination": exp
                    })
                except Exception:
                    continue
            
            # Pagination Logic
            try:
                pagination = driver.find_elements(By.CSS_SELECTOR, 'ul.pagination li.page-item a')
                next_button = pagination[-1] if pagination else None
                next_url = next_button.get_attribute('href') if next_button else "#"
                
                if next_url == current_url or next_url == "#" or "javascript" in next_url:
                    current_url = None
                else:
                    current_url = next_url
            except Exception:
                current_url = None
    finally:
        driver.quit()
    return all_data

# Main Execution Loop
if __name__ == "__main__":
    if os.path.exists('urls.txt'):
        with open('urls.txt', 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
            
        for url in urls:
            filename = get_filename_from_url(url)
            print(f"--- Starting: {url} ---")
            data = scrape_all_pages(url)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Saved {len(data)} questions to {filename}")
    else:
        print("Error: urls.txt not found.")