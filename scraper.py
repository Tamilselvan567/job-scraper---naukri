import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_naukri_jobs(role, location, max_jobs=500):
    """
    Scrapes jobs from Naukri.com based on role and location.
    
    Args:
        role (str): The job role to search for (e.g., 'Data Scientist').
        location (str): The location to search in (e.g., 'Chennai').
        max_jobs (int): The maximum number of jobs to scrape.
        
    Returns:
        list of dict: A list of scraped jobs.
    """
    # Format the URL by replacing spaces with hyphens
    formatted_role = role.replace(" ", "-").lower()
    formatted_location = location.replace(" ", "-").lower()
    
    # Base URL for Naukri search
    url = f"https://www.naukri.com/{formatted_role}-jobs-in-{formatted_location}"
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Add a random user agent to prevent basic bot detection
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Initialize the WebDriver using webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    scraped_jobs = []
    seen_urls = set()
    page_count = 1

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        
        while len(scraped_jobs) < max_jobs:
            print(f"Scraping page {page_count}...")
            
            # Wait for job cards to load on the page
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.srp-jobtuple-wrapper")))
            except Exception as e:
                print(f"No job list container found on page {page_count}. Assuming end of results.")
                break
            
            # Allow some time for all elements to settle
            time.sleep(3)
            
            # Find all job cards on the current page
            job_cards = driver.find_elements(By.CSS_SELECTOR, "div.srp-jobtuple-wrapper")
            
            if not job_cards:
                print("No more job cards found. Exiting.")
                break
                
            for card in job_cards:
                if len(scraped_jobs) >= max_jobs:
                    break
                    
                try:
                    # Extract Job Title
                    title_elem = card.find_element(By.CSS_SELECTOR, "a.title")
                    title = title_elem.text.strip()
                    job_url = title_elem.get_attribute("href")
                    
                    # Skip if duplicate
                    if job_url in seen_urls:
                        continue
                    
                    # Extract Company Name
                    try:
                        company_elem = card.find_element(By.CSS_SELECTOR, "a.comp-name")
                        company = company_elem.text.strip()
                    except:
                        company = "Not specified"
                        
                    # Extract Location
                    try:
                        location_elem = card.find_element(By.CSS_SELECTOR, "span.locWdth")
                        job_location = location_elem.text.strip()
                    except:
                        job_location = "Not specified"

                    # Add job details to our list
                    job_info = {
                        "Title": title,
                        "Company": company,
                        "Location": job_location,
                        "Link": job_url
                    }
                    
                    scraped_jobs.append(job_info)
                    seen_urls.add(job_url)

                except Exception as e:
                    # Silently skip cards that are malformed
                    continue
            
            print(f"Successfully scraped {len(scraped_jobs)} jobs so far.")
            
            if len(scraped_jobs) >= max_jobs:
                break
                
            # Try to click the "Next" button for pagination
            try:
                # Naukri often uses a span with text "Next" inside an anchor
                next_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Next')]/parent::a")
                driver.execute_script("arguments[0].click();", next_button)
                page_count += 1
                time.sleep(4) # Delay to avoid blocking
            except Exception as e:
                print("No 'Next' button found. Reached the last page.")
                break

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        
    finally:
        driver.quit()
        
    return scraped_jobs

if __name__ == "__main__":
    # Test the script locally
    jobs = scrape_naukri_jobs("Data Scientist", "Chennai", 10)
    for j in jobs:
        print(j)
