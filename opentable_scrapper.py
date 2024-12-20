import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
import time

# Configure logging
logging.basicConfig(
    filename="script.log",  # Log file path
    level=logging.INFO,     # Logging level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables from .env file
load_dotenv()

def update_date(web_driver, date_id, new_date):
    logging.info("Updating date...")
    try:
        web_driver.find_element(By.ID, date_id).click()
        # web_driver.find_element(By.CSS_SELECTOR, ".z-IxWXLCX-M-").click()
        wait = WebDriverWait(web_driver, 10)
        wait.until(EC.visibility_of_element_located((By.ID, "dtp-picker-day-picker-wrapper")))

        date = f"//td[@class='NhswJpa89v8-']/button[text()='{new_date}']"
        button = web_driver.find_element(By.XPATH, date)
        button.click()
        logging.info(f"Date updated to {new_date}.")
    except Exception as e:
        logging.error(f"Error updating date: {e}")

def update_time(web_driver, time_selector, new_time):
    logging.info("Updating time...")
    try:
        time_selector = WebDriverWait(web_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, time_selector))
        )
        select = Select(time_selector)
        select.select_by_visible_text(new_time)
        logging.info(f"Time updated to {new_time}.")
    except Exception as e:
        logging.error(f"Error selecting time: {e}")

def update_num_people(web_driver, people_selector, num_people):
    logging.info("Updating number of people...")
    try:
        time_selector = WebDriverWait(web_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, people_selector))
        )
        select = Select(time_selector)
        select.select_by_visible_text(num_people)
        logging.info(f"Number of people updated to {num_people}.")
    except Exception as e:
        logging.error(f"Error selecting number of people: {e}")

def click_find_table_button(web_driver, submit_selector):
    logging.info("Clicking 'Find a Table' button...")
    try:
        button = WebDriverWait(web_driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, submit_selector))
        )
        button.click()
        logging.info("Button clicked successfully!")
    except Exception as e:
        logging.error(f"Error clicking the button: {e}")

def check_available_time(web_driver):
    logging.info("Checking available times...")
    wait = WebDriverWait(web_driver, 10)
    try:
        span_element = wait.until(EC.presence_of_element_located((By.XPATH, "//span[starts-with(text(), 'At the moment')]")))
        span_text = span_element.text
        if span_text:
            logging.info(f"Availability message: {span_text}")
            return False
        return True
    except TimeoutException:
        logging.warning("Element not found, assuming times are available.")
        return True

def send_text_via_gmail(recipient_number, carrier_gateway, message):
    logging.info("Sending text via Gmail...")
    sender_email = os.getenv("GMAIL_EMAIL")
    sender_password = os.getenv("GMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        logging.error("Gmail email or password is not set in the environment file.")
        return

    sms_gateway = f"{recipient_number}@{carrier_gateway}"
    msg = MIMEText(message)
    msg['From'] = sender_email
    msg['To'] = sms_gateway

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, sms_gateway, msg.as_string())
            logging.info("Text message sent successfully!")
    except Exception as e:
        logging.error(f"Failed to send text message: {e}")

### MAIN ###
def main():
    logging.info("Script started.")

    # Setup Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU (optional)
    chrome_options.add_argument("--no-sandbox")  # For running in environments like Docker
    chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent resource issues
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.204 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")


    service = Service(executable_path="chromedriver.exe")
    # driver = webdriver.Chrome(service=service)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver_url = "https://www.opentable.com/booking/restref/availability?lang=en-US&restRef=1211938&otSource=Restaurant%20website"
    driver.get(driver_url)
    
    date_id = "dtp-picker-day-picker-label"
    new_date = "26" #TEST 30
    update_date(driver, date_id, new_date)
    
    time_selector = 'select[data-test="time-picker"]'
    new_time = "7:00 PM" #TEST 11 AM
    update_time(driver, time_selector, new_time)

    people_selector = 'select[data-test="party-size-picker"]'
    num_people = "4 people"
    update_num_people(driver, people_selector, num_people)

    submit_selector = '[data-test="dtpPicker-submit"]'
    click_find_table_button(driver, submit_selector)

    if check_available_time(driver):
        logging.info("Sending notification text message...")
        recipient_number = os.getenv("CELL")
        carrier_gateway = "txt.att.net"
        message = "Table is open: https://www.opentable.com/booking/restref/availability?lang=en-US&restRef=1211938&otSource=Restaurant%20website"
        send_text_via_gmail(recipient_number, carrier_gateway, message)

    time.sleep(5)
    driver.quit()
    logging.info("Script completed.")

if __name__ == "__main__":
    main()
