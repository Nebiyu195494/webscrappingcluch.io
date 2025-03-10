from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd

# Set Chrome options
chrome_options = Options()
chrome_options.binary_location = "/usr/bin/google-chrome"  # Adjust the path if necessary

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Prepare a list to store the scraped data
scraped_data = []

# Loop through the pages
for page in range(1, 3):
    # Open a new window for each page
    driver.execute_script("window.open('');")
    
    # Switch to the new window
    driver.switch_to.window(driver.window_handles[-1])
    
    # Open the URL for the page
    driver.get(f'https://clutch.co/directory/mobile-application-developers?page={page}')
    
    # Wait for the page to load (you may want to implement a more robust wait here)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'provider-list-item')))
    
    # Scrape the data
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'lxml')
    companies = soup.find_all('li', class_='provider-list-item')

    for company in companies:
        name = company.find('h3', class_='provider__title').text.strip()
        rating = company.find('span', class_='sg-rating__number')
        rating_text = rating.text.strip() if rating else "No rating available"
        reviews = company.find('a', class_='sg-rating__reviews directory_profile')
        reviews_text = reviews.text.strip() if reviews else "No reviews available"
        
        # Add data to the scraped_data list
        scraped_data.append({
            'Company Name': name,
            'Rating': rating_text,
            'Reviews': reviews_text
        })
    
    # Close the current window after scraping
    driver.close()

    # Switch back to the main window
    driver.switch_to.window(driver.window_handles[0])

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(scraped_data)

# Export the DataFrame to an Excel file
df.to_excel('scraped_companies_data.xlsx', index=False)

print("Data exported to 'scraped_companies_data.xlsx' successfully.")

# Quit the driver
driver.quit()
