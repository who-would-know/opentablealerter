from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
import time

# Load environment variables from .env file
load_dotenv()

def update_date(web_driver, date_id, new_date):
    # Wait until the dropdown is visible and click it
    web_driver.find_element(By.ID,"dtp-picker-day-picker-label").click()

    # Set up WebDriverWait to wait up to 10 seconds
    wait = WebDriverWait(web_driver, 10)

    # Wait until the element is visible (with ID 'dtp-picker-day-picker-wrapper')
    element = wait.until(EC.visibility_of_element_located((By.ID, "dtp-picker-day-picker-wrapper")))

    # Get date
    date = "//td[@class='NhswJpa89v8-']/button[text()='" + new_date + "']"
    button = web_driver.find_element(By.XPATH, date)
    button.click()

def update_time(web_driver, time_selector, new_time):
    try:
        # Wait for the <select> element to be visible
        time_selector = WebDriverWait(web_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, time_selector))
        )

        # Create a Select object
        select = Select(time_selector)
        #Debug
        # options = select.options
        # for option in options:
        #     print(f"Option text: {option.text}")

        # Select the option with visible text "6:00 PM"
        select.select_by_visible_text(new_time)
        print("Selected 6:00 PM successfully!")

        # # Optional: Verify the selected value
        # selected_option = select.first_selected_option.text
        # print("Currently selected time:", selected_option)

    except Exception as e:
        print("Error selecting time:", e)

def update_num_people(web_driver, people_selector, num_people):
    try:
        # Wait for the <select> element to be visible
        time_selector = WebDriverWait(web_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, people_selector))
        )

        # Create a Select object
        select = Select(time_selector)
        # #Debug
        # options = select.options
        # for option in options:
        #     print(f"Option text: {option.text}")

        # Select the option with visible text 4 people
        select.select_by_visible_text(num_people)
        print("Selected 4 people successfully!")

        # # Optional: Verify the selected value
        # selected_option = select.first_selected_option.text
        # print("Currently selected people:", selected_option)

    except Exception as e:
        print("Error selecting people:", e)

def click_find_table_button(web_driver, submit_selector):
    # Locate and click the "Find a table" button
    try:
        # Wait for the button to be clickable
        button = WebDriverWait(web_driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, submit_selector))
        )
        button.click()
        print("Button clicked successfully!")
    except Exception as e:
        print("Error clicking the button:", e)

    # Optional: Verify navigation to the next page
    print("Current URL:", web_driver.current_url)

def check_available_time(web_driver):
    # Locate the <span> element inside the <div> with class 'O-z6wyHTamU-'
    wait = WebDriverWait(web_driver, 10)  # 10 seconds timeout

    try: 
        span_element = wait.until(EC.presence_of_element_located((By.XPATH, "//span[starts-with(text(), 'At the moment')]")))

        # Get the text inside the <span> element
        span_text = span_element.text

        # Print the extracted text
        if span_text:
            print(span_text)
            return False
        else:
            return True
    except TimeoutException:
        # If the element is not found in the timeout period, continue execution
        print("Element not found, continuing with the script...")
        return True

def send_text_via_gmail(recipient_number, carrier_gateway, message):
    # Load Gmail credentials from environment variables
    sender_email = os.getenv("GMAIL_EMAIL")
    sender_password = os.getenv("GMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Gmail email or password is not set in the environment file.")
        return

    # Construct the recipient's email-to-SMS address
    sms_gateway = f"{recipient_number}@{carrier_gateway}"
    
    # Create the message
    msg = MIMEText(message)
    msg['From'] = sender_email
    msg['To'] = sms_gateway
    #msg['Subject'] = "Text Message"  # Optional

    try:
        # Connect to Gmail's SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, sender_password)  # Log in to Gmail
            server.sendmail(sender_email, sms_gateway, msg.as_string())  # Send the message
            print("Text message sent successfully!")
    except Exception as e:
        print(f"Failed to send text message: {e}")


###
def main():
    # Setup Service & Driver
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    
    driver_url = "https://www.opentable.com/booking/restref/availability?lang=en-US&restRef=1211938&otSource=Restaurant%20website"
    driver.get(driver_url)
    
    # Update Date
    date_id = "dtp-picker-day-picker-label"
    new_date = "31" #Test Date 31, OG 26
    update_date(driver, date_id, new_date)
    
    # Update Time
    time_selector = 'select[data-test="time-picker"]'
    new_time = "11:00 AM" #Test time 11:00 AM, OG 7:00 PM
    update_time(driver, time_selector, new_time)

    # Update Number of People
    people_selector = 'select[data-test="party-size-picker"]'
    num_people = "4 people"
    update_num_people(driver, people_selector, num_people)

    # click "Find a Table" button
    submit_selector = '[data-test="dtpPicker-submit"]'
    click_find_table_button(driver, submit_selector)

    # Check Time
    if check_available_time(driver):
        print("Sent Text Message times are available")

        recipient_number = os.getenv("CELL")
        carrier_gateway = "txt.att.net"
        message = " Table is open, https://www.opentable.com/booking/restref/availability?lang=en-US&restRef=1211938&otSource=Restaurant%20website "

        send_text_via_gmail(recipient_number, carrier_gateway, message)

    ## Wait before closing Chrome Browser and driver
    time.sleep(5)
    driver.quit()

if __name__ == "__main__":
    main()