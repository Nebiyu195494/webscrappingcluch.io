from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re
import pandas as pd

def wait_for_cloudflare(driver):
    try:
        # Wait for Cloudflare challenge to appear
        challenge = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "cf-browser-verification"))
        )
        print("Cloudflare challenge detected, waiting...")
        
        # Wait for challenge to complete
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "cf-browser-verification"))
        )
        print("Challenge completed")
    except:
        print("No Cloudflare challenge detected")

# Set Chrome options and specify the binary location
chrome_options = Options()
chrome_options.binary_location = "/usr/bin/google-chrome"  # Adjust the path if necessary

# Prepare a list to store the scraped data
scraped_data = []

# Function to scrape data from a single page
def scrape_page(page_number):
    # Initialize WebDriver with the specified options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    url = f'https://clutch.co/directory/mobile-application-developers?page={page_number}'
    driver.get(url)
    wait_for_cloudflare(driver)

    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'lxml')
    companies = soup.find_all('li', class_='provider-list-item')

    for company in companies:
        name = company.find('h3', class_='provider__title').text
        
        # Check if the rating exists before accessing it
        rating = company.find('span', class_='sg-rating__number')
        rating_text = rating.text.strip() if rating else "No rating available"
        
        reviews = company.find('a', class_='sg-rating__reviews directory_profile')
        reviews_list = [review for review in reviews] if reviews is not None else []
        reviews_text = reviews_list[0].strip().replace('\n', ' ').replace('                           ', ' ') if reviews_list else "No reviews available"
        
        vertification = company.find('span', class_='provider__verified-mark provider__verified-mark--premier')

        minprojectsize = company.find('div', class_='provider__highlights-item sg-tooltip-v2 min-project-size').text
        hourlyrate = company.find('div', class_='provider__highlights-item sg-tooltip-v2 hourly-rate').text
        employees = company.find('div', class_='provider__highlights-item sg-tooltip-v2 employees-count').text
        location = company.find('div', class_='provider__highlights-item sg-tooltip-v2 location').text
        
        services = company.find_all('div', class_='provider__services-list-item')
        
        cleaned_services = [service.text for service in services]

        services_string = ', '.join(cleaned_services)
        services_string = re.sub(r'\s*\+\d+\s*service[s]?', '', services_string)

        # Step 2: Remove extra whitespace
        services_string = re.sub(r'\s+', ' ', services_string).strip()

        # Add the data to the scraped_data list as a dictionary
        scraped_data.append({
            'Company Name': name.strip(),
            'Rating': rating_text,
            'Reviews': reviews_text,
            'Min Project Size': minprojectsize.strip(),
            'Hourly Rate': hourlyrate.strip(),
            'Employees': employees.strip(),
            'Location': location.strip(),
            'Services': services_string
        })

    # Close the browser after scraping the page
    driver.quit()

# Loop through multiple pages
for page in range(1, 6):  # Change 6 to the number of pages you want to scrape
    print(f"Scraping page {page}...")
    scrape_page(page)
    time.sleep(2)  # Optional: add a delay between requests to prevent overloading the server

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(scraped_data)

# Export the DataFrame to an Excel file
df.to_excel('scraped_companies_data_multiple_pages.xlsx', index=False)

print("Data exported to 'scraped_companies_data_multiple_pages.xlsx' successfully.")
