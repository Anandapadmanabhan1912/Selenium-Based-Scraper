from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import time

def scrape_all_pages(start_url)
    chrome_options = Options()
    chrome_options.add_argument(--headless=new)
    chrome_options.add_argument(user-agent=Mozilla5.0 (Windows NT 10.0; Win64; x64) AppleWebKit537.36 (KHTML, like Gecko) Chrome122.0.0.0 Safari537.36)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    all_data = []
    current_url = start_url
    
    try
        while current_url and current_url != #
            print(fScraping {current_url})
            driver.get(current_url)
            
            # Wait for content to load
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'bix-div-container')))
            time.sleep(2)
            
            # Scrape content
            containers = driver.find_elements(By.CLASS_NAME, 'bix-div-container')
            for index, container in enumerate(containers, 1)
                try
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
                except Exception
                    continue
            
            # Find the Next button
            try
                # Looking for the last link in the pagination list
                pagination = driver.find_elements(By.CSS_SELECTOR, 'ul.pagination li.page-item a')
                next_button = pagination[-1] if pagination else None
                
                next_url = next_button.get_attribute('href') if next_button else #
                
                # If the next_url is the same as the current, or is '#', stop
                if next_url == current_url or next_url == # or javascript in next_url
                    current_url = None
                else
                    current_url = next_url
            except Exception
                current_url = None
                
    finally
        driver.quit()
        
    return all_data

# Start at the first page
start_url = httpswww.indiabix.comaptitudetime-and-distance
full_data = scrape_all_pages(start_url)

with open('all_questions.json', 'w', encoding='utf-8') as f
    json.dump(full_data, f, indent=4, ensure_ascii=False)

print(fSuccessfully scraped {len(full_data)} total questions.)