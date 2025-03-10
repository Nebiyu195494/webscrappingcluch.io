# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from bs4 import BeautifulSoup
# import time
# import re
# import pandas as pd


# def wait_for_cloudflare(driver):
#     try:
#         # Wait for Cloudflare challenge to appear
#         challenge = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "cf-browser-verification"))
#         )
#         print("Cloudflare challenge detected, waiting...")
        
#         # Wait for challenge to complete
#         WebDriverWait(driver, 30).until(
#             EC.invisibility_of_element_located((By.CLASS_NAME, "cf-browser-verification"))
#         )
#         print("Challenge completed")
#     except:
#         print("No Cloudflare challenge detected")

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# driver.get('https://clutch.co/directory/mobile-application-developers?page=0')
# wait_for_cloudflare(driver)

# html_text = driver.page_source
# soup = BeautifulSoup(html_text, 'lxml')
# companies = soup.find_all('li', class_='provider-list-item')

# for company in companies:
#     name = company.find('h3', class_='provider__title').text
#     rating = company.find('span', class_='sg-rating__number')
    
#     reviews = company.find('a', class_='sg-rating__reviews directory_profile')    
#     reviews_list = [review for review in reviews] if reviews is not None else []    
    
#     vertification = company.find('span', class_='provider__verified-mark provider__verified-mark--premier')
#     # The Company vertification : {vertification}


#     minprojectsize = company.find('div', class_='provider__highlights-item sg-tooltip-v2 min-project-size').text
#     hourlyrate =company.find('div', class_='provider__highlights-item sg-tooltip-v2 hourly-rate').text
#     employees = company.find('div', class_='provider__highlights-item sg-tooltip-v2 employees-count').text
#     location =company.find('div', class_='provider__highlights-item sg-tooltip-v2 location').text
    
    
#     services =company.find_all('div', class_='provider__services-list-item')
        
#     cleaned_services = [service.text for service in services]

#     services_string = ', '.join(cleaned_services)
#     services_string = re.sub(r'\s*\+\d+\s*service[s]?', '', services_string)

#     # Step 2: Remove extra whitespace
#     services_string = re.sub(r'\s+', ' ', services_string).strip()
    
#     print(f'''
#         The Company name: {name.strip()}
#         The Company rating : {rating.text.strip()}
#         The Company reviews : {reviews_list[0].strip().replace('\n', ' ').replace('                           ', ' ')}

#         The Company min project size : {minprojectsize.strip()}
#         The Company hourly rate : {hourlyrate.strip()}
#         The Company employee size : {employees.strip()}
#         The Company location : {location.strip()}
#         The Company services : {services_string}
#     ''')
    

# driver.quit()           












from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re

def wait_for_cloudflare(driver):
    try:
        # Wait for Cloudflare challenge to appear
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "cf-browser-verification"))
        )
        print("Cloudflare challenge detected, waiting...")

        # Wait for challenge to complete
        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "cf-browser-verification"))
        )
        print("Challenge completed")
    except Exception as e:
        print(f"No Cloudflare challenge detected or error occurred: {e}")

def scrape_page(driver, page_number):
    url = f'https://clutch.co/directory/mobile-application-developers?page={page_number}'
    driver.get(url)
    wait_for_cloudflare(driver)
    
    # Wait for the page content to load (dynamic wait based on page elements)
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'provider-list-item'))
    )
    
    # Fetch page source after content is loaded
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'lxml')

    # Debugging: Print part of the page source to check if the content exists
    print(f"Page {page_number} source length: {len(html_text)}")
    
    companies = soup.find_all('li', class_='provider-list-item')
    if not companies:
        print(f"No companies found on page {page_number}. Here’s the page content:\n")
        print(soup.prettify())  # Print the prettified HTML of the page
        return []

    company_data = []

    for company in companies:
        try:
            name = company.find('h3', class_='provider__title').text.strip()
            rating = company.find('span', class_='sg-rating__number')
            reviews = company.find('a', class_='sg-rating__reviews directory_profile')
            reviews_list = [review for review in reviews] if reviews else []
            
            min_project_size = company.find('div', class_='provider__highlights-item sg-tooltip-v2 min-project-size').text.strip()
            hourly_rate = company.find('div', class_='provider__highlights-item sg-tooltip-v2 hourly-rate').text.strip()
            employees = company.find('div', class_='provider__highlights-item sg-tooltip-v2 employees-count').text.strip()
            location = company.find('div', class_='provider__highlights-item sg-tooltip-v2 location').text.strip()
            
            services = company.find_all('div', class_='provider__services-list-item')
            cleaned_services = [service.text.strip() for service in services]

            services_string = ', '.join(cleaned_services)
            services_string = re.sub(r'\s*\+\d+\s*service[s]?', '', services_string)
            services_string = re.sub(r'\s+', ' ', services_string).strip()

            # Add company data to the list
            company_data.append({
                'name': name,
                'rating': rating.text.strip() if rating else 'N/A',
                'reviews': reviews_list[0].strip() if reviews_list else 'N/A',
                'min_project_size': min_project_size,
                'hourly_rate': hourly_rate,
                'employee_size': employees,
                'location': location,
                'services': services_string
            })
        
        except AttributeError as e:
            print(f"Error extracting data for one company: {e}")
            continue  # Skip this company and move on to the next

    return company_data

# Main function to run the scraper
def run_scraper():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        while True:
            page_number = int(input("Enter the page number to scrape (or '0' to exit): "))
            if page_number == 0:
                print("Exiting the scraper.")
                break
            
            print(f"Scraping page {page_number}...")
            page_data = scrape_page(driver, page_number)
            
            if not page_data:
                print(f"No data found on page {page_number}. Moving to next page...\n")
            else:
                print(f"Scraped data for page {page_number}:")
                for company in page_data:
                    print(f"{company['name']} - Rating: {company['rating']}")
    
    finally:
        driver.quit()

# Run the scraper
run_scraper()







































































































































































































































































































# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from bs4 import BeautifulSoup
# import time
# import re
# import pandas as pd

# def wait_for_cloudflare(driver):
#     try:
#         # Wait for Cloudflare challenge to appear
#         challenge = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "cf-browser-verification"))
#         )
#         print("Cloudflare challenge detected, waiting...")
        
#         # Wait for challenge to complete
#         WebDriverWait(driver, 30).until(
#             EC.invisibility_of_element_located((By.CLASS_NAME, "cf-browser-verification"))
#         )
#         print("Challenge completed")
#     except:
#         print("No Cloudflare challenge detected")

# # Initialize the driver
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# driver.get('https://clutch.co/directory/mobile-application-developers')
# wait_for_cloudflare(driver)

# html_text = driver.page_source
# soup = BeautifulSoup(html_text, 'lxml')
# companies = soup.find_all('li', class_='provider-list-item')

# # List to hold company data
# company_data = []

# for company in companies:
#     name = company.find('h3', class_='provider__title').text.strip()
#     rating = company.find('span', class_='sg-rating__number')
#     rating_text = rating.text.strip() if rating else "N/A"
    
#     reviews = company.find('a', class_='sg-rating__reviews directory_profile')
#     reviews_list = [review for review in reviews] if reviews is not None else []
#     reviews_text = reviews_list[0].strip().replace('\n', ' ').replace('                           ', '') if reviews_list else "N/A"

#     minprojectsize = company.find('div', class_='provider__highlights-item sg-tooltip-v2 min-project-size').text.strip()
#     hourlyrate = company.find('div', class_='provider__highlights-item sg-tooltip-v2 hourly-rate').text.strip()
#     employees = company.find('div', class_='provider__highlights-item sg-tooltip-v2 employees-count').text.strip()
#     location = company.find('div', class_='provider__highlights-item sg-tooltip-v2 location').text.strip()
    
#     services = company.find_all('div', class_='provider__services-list-item')
#     cleaned_services = [service.text for service in services]
#     services_string = ', '.join(cleaned_services)
#     services_string = re.sub(r'\s*\+\d+\s*service[s]?', '', services_string)
#     services_string = re.sub(r'\s+', ' ', services_string).strip()

#     # Append data to the list
#     company_data.append({
#         'Company Name': name,
#         'Company Rating': rating_text,
#         'Company Reviews': reviews_text,
#         'Min Project Size': minprojectsize,
#         'Hourly Rate': hourlyrate,
#         'Employee Size': employees,
#         'Location': location,
#         'Services': services_string
#     })

# # Convert to DataFrame
# df = pd.DataFrame(company_data)

# # Save to Excel
# excel_file = 'company_info.xlsx'
# df.to_excel(excel_file, index=False)

# print(f"Data saved to {excel_file}")

# # Quit the driver
# driver.quit()


# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from bs4 import BeautifulSoup
# import pandas as pd
# import re

# def wait_for_cloudflare(driver):
#     try:
#         # Wait for Cloudflare challenge to appear
#         challenge = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "cf-browser-verification"))
#         )
#         print("Cloudflare challenge detected, waiting...")
        
#         # Wait for challenge to complete
#         WebDriverWait(driver, 30).until(
#             EC.invisibility_of_element_located((By.CLASS_NAME, "cf-browser-verification"))
#         )
#         print("Challenge completed")
#     except:
#         print("No Cloudflare challenge detected")

# # Initialize the driver
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# home_url = 'https://clutch.co/directory/mobile-application-developers?page='

# # List to hold company data
# company_data = []

# # Loop through the first 10 pages
# for page in range(0, 10):
#     url = f'{home_url}{page}'
#     driver.get(url)
#     wait_for_cloudflare(driver)

#     html_text = driver.page_source
#     soup = BeautifulSoup(html_text, 'lxml')
#     companies = soup.find_all('li', class_='provider-list-item')

#     for company in companies:
#         name = company.find('h3', class_='provider__title').text.strip()
#         rating = company.find('span', class_='sg-rating__number')
#         rating_text = rating.text.strip() if rating else "N/A"
        
#         reviews = company.find('a', class_='sg-rating__reviews directory_profile')
#         reviews_list = [review for review in reviews] if reviews is not None else []
#         reviews_text = reviews_list[0].strip().replace('\n', ' ').replace('                           ', '') if reviews_list else "N/A"

#         minprojectsize = company.find('div', class_='provider__highlights-item sg-tooltip-v2 min-project-size').text.strip()
#         hourlyrate = company.find('div', class_='provider__highlights-item sg-tooltip-v2 hourly-rate').text.strip()
#         employees = company.find('div', class_='provider__highlights-item sg-tooltip-v2 employees-count').text.strip()
#         location = company.find('div', class_='provider__highlights-item sg-tooltip-v2 location').text.strip()
        
#         services = company.find_all('div', class_='provider__services-list-item')
#         cleaned_services = [service.text for service in services]
#         services_string = ', '.join(cleaned_services)
#         services_string = re.sub(r'\s*\+\d+\s*service[s]?', '', services_string)
#         services_string = re.sub(r'\s+', ' ', services_string).strip()

#         # Append data to the list
#         company_data.append({
#             'Company Name': name,
#             'Company Rating': rating_text,
#             'Company Reviews': reviews_text,
#             'Min Project Size': minprojectsize,
#             'Hourly Rate': hourlyrate,
#             'Employee Size': employees,
#             'Location': location,
#             'Services': services_string
#         })
        
#         print(f"on page {page}")
        

# # Convert to DataFrame
# df = pd.DataFrame(company_data)

# # Save to Excel
# excel_file = 'company_info_clutch.xlsx'
# df.to_excel(excel_file, index=False)

# print(f"Data saved to {excel_file}")

# # Quit the driver
# driver.quit()










# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from bs4 import BeautifulSoup
# import pandas as pd
# import re
# import time

# def wait_for_cloudflare(driver):
#     try:
#         # Wait for Cloudflare challenge to appear
#         challenge = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "cf-browser-verification"))
#         )
#         print("Cloudflare challenge detected, waiting...")
#         # Wait for challenge to complete
#         WebDriverWait(driver, 30).until(
#             EC.invisibility_of_element_located((By.CLASS_NAME, "cf-browser-verification"))
#         )
#         print("Challenge completed")
#     except:
#         print("No Cloudflare challenge detected")

# # Initialize the driver
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# base_url = 'https://clutch.co/directory/mobile-application-developers?page='
# company_data = []

# # Navigate to first page and handle Cloudflare
# driver.get(base_url)
# wait_for_cloudflare(driver)

# # Loop through pages using URL navigation
# for page in range(10):
#     # Get current page content
#     html_text = driver.page_source
#     soup = BeautifulSoup(html_text, 'lxml')
#     companies = soup.find_all('li', class_='provider-list-item')
    
#     # Extract company data (same as previous example)
#     for company in companies:
#         name = company.find('h3', class_='provider__title').text.strip()
#         rating = company.find('span', class_='sg-rating__number')
#         rating_text = rating.text.strip() if rating else "N/A"
#         reviews = company.find('a', class_='sg-rating__reviews directory_profile')
#         reviews_list = [review for review in reviews] if reviews is not None else []
#         reviews_text = reviews_list[0].strip().replace('\n', ' ').replace(' ', '') if reviews_list else "N/A"
#         minprojectsize = company.find('div', class_='provider__highlights-item sg-tooltip-v2 min-project-size').text.strip()
#         hourlyrate = company.find('div', class_='provider__highlights-item sg-tooltip-v2 hourly-rate').text.strip()
#         employees = company.find('div', class_='provider__highlights-item sg-tooltip-v2 employees-count').text.strip()
#         location = company.find('div', class_='provider__highlights-item sg-tooltip-v2 location').text.strip()
#         services = company.find_all('div', class_='provider__services-list-item')
#         cleaned_services = [service.text for service in services]
#         services_string = ', '.join(cleaned_services)
#         services_string = re.sub(r'\s*\+\d+\s*service[s]?', '', services_string)
#         services_string = re.sub(r'\s+', ' ', services_string).strip()
        
#         company_data.append({
#             'Company Name': name,
#             'Company Rating': rating_text,
#             'Company Reviews': reviews_text,
#             'Min Project Size': minprojectsize,
#             'Hourly Rate': hourlyrate,
#             'Employee Size': employees,
#             'Location': location,
#             'Services': services_string
#         })
#     print(f"saved page {page}")    
    
#     # Navigate to next page
#     if page < 9:  # Only navigate if not on last page
#         next_url = f'{base_url}{page + 1}'
#         driver.get(next_url)
#         wait_for_cloudflare(driver)
#         time.sleep(2)  # Wait for page to load

# # Convert to DataFrame and save
# df = pd.DataFrame(company_data)
# df.to_excel('company_info_clutch.xlsx', index=False)
# print(f"Data saved to company_info_clutch.xlsx")
# driver.quit()
