from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get('https://clutch.co/directory/mobile-application-developers?page=0')
wait_for_cloudflare(driver)

html_text = driver.page_source
soup = BeautifulSoup(html_text, 'lxml')
companies = soup.find_all('li', class_='provider-list-item')

for company in companies:
    name = company.find('h3', class_='provider__title').text
    rating = company.find('span', class_='sg-rating__number')
    
    reviews = company.find('a', class_='sg-rating__reviews directory_profile')    
    reviews_list = [review for review in reviews] if reviews is not None else []    
    
    vertification = company.find('span', class_='provider__verified-mark provider__verified-mark--premier')
    # The Company vertification : {vertification}


    minprojectsize = company.find('div', class_='provider__highlights-item sg-tooltip-v2 min-project-size').text
    hourlyrate =company.find('div', class_='provider__highlights-item sg-tooltip-v2 hourly-rate').text
    employees = company.find('div', class_='provider__highlights-item sg-tooltip-v2 employees-count').text
    location =company.find('div', class_='provider__highlights-item sg-tooltip-v2 location').text
    
    
    services =company.find_all('div', class_='provider__services-list-item')
        
    cleaned_services = [service.text for service in services]

    services_string = ', '.join(cleaned_services)
    services_string = re.sub(r'\s*\+\d+\s*service[s]?', '', services_string)

    # Step 2: Remove extra whitespace
    services_string = re.sub(r'\s+', ' ', services_string).strip()
    
    print(f'''
        The Company name: {name.strip()}
        The Company rating : {rating.text.strip()}
        The Company reviews : {reviews_list[0].strip().replace('\n', ' ').replace('                           ', ' ')}

        The Company min project size : {minprojectsize.strip()}
        The Company hourly rate : {hourlyrate.strip()}
        The Company employee size : {employees.strip()}
        The Company location : {location.strip()}
        The Company services : {services_string}
    ''')
    

driver.quit()           