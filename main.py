from dotenv import load_dotenv
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
# Load environment variables from .env file
load_dotenv()

# Access the email-related variables
smtp_server = os.environ.get('SMTP_SERVER')
smtp_port = os.environ.get('SMTP_PORT')
email_address = os.environ.get('EMAIL_ADDRESS')
email_password = os.environ.get('SENDER_EMAIL_PASSWORD')
sender_name = os.environ.get('SENDER_NAME')
sender_email = os.environ.get('SENDER_EMAIL')
recipient_email = os.environ.get('RECIPIENT_EMAIL')
appointment_date = os.environ.get('APPOINTMENT_DATE')
visa_email = os.environ.get('VISA_EMAIL')
visa_password = os.environ.get('VISA_PASSWORD')


def parse_date(date_str):
    # Define a dictionary to map month names to month numbers
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }

    # Split the date string into day, month, and year parts
    day, month_name, year = date_str.split()

    # Use the month map to get the month number
    month = month_map[month_name]

    # Create a datetime object
    parsed_date = datetime(int(year), month, int(day))

    return parsed_date

def send_email(content):
    try:
       #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = 'Sistema de Mensajes'   #The subject line
        #The body and the attachments for the mail
        message.attach(MIMEText(content, 'plain'))
        #Create SMTP session for sending the mail
        session = smtplib.SMTP(smtp_server, smtp_port) #use gmail with port
        session.starttls() #enable security
        session.login(email_address, email_password) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_email, email_address, text)
        session.quit()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def get_available_date(element):
    for row in element.find_elements(By.TAG_NAME, "td"):
        class_t = row.text, row.get_attribute("class")
        
        if row.text.strip() and not "disabled" in class_t[1]:
            month = row.parent.find_elements(By.CLASS_NAME, "ui-datepicker-title")[0].text
            date = row.text
            return f"{date} {month}"
    return None
                

if __name__=="__main__":
    driver = webdriver.Chrome()
    driver.get("https://ais.usvisa-info.com/en-ar/niv/users/sign_in")
    time.sleep(2)
    email_input = driver.find_element(By.ID,"user_email")
    email_input.send_keys(visa_email)
    time.sleep(2)
    password_input = driver.find_element(By.ID,"user_password")
    password_input.send_keys(visa_password)
    time.sleep(2)
    policy_confirm_input = driver.find_element(By.CLASS_NAME, "icheckbox")
    policy_confirm_input.click()
    time.sleep(2)
    login_form = driver.find_element(By.TAG_NAME,"form")
    login_form.submit()
    time.sleep(2)
    continue_button = driver.find_element(By.XPATH,"//a[@href='/en-ar/niv/schedule/51699052/continue_actions']")
    continue_button.click()
    time.sleep(2)
    schedule_button = driver.find_element(By.CLASS_NAME,"fa-calendar-minus")
    schedule_button.click()
    time.sleep(2)
    continue_button = driver.find_element(By.XPATH,"//a[@href='/en-ar/niv/schedule/51699052/appointment']")
    continue_button.click()
    time.sleep(2)
    continue_button2 = driver.find_element(By.NAME,"commit")
    continue_button2.click()
    time.sleep(2)
    location_select = driver.find_element(By.ID,"appointments_consulate_appointment_facility_id")
    location_select.click()
    time.sleep(2)
    location_option = driver.find_element(By.XPATH,"//option[contains(text(), 'Buenos Aires')]")
    location_option.click()
    time.sleep(2)

    location_select = driver.find_element(By.ID,"appointments_consulate_appointment_date")
    location_select.click()
    time.sleep(2)
    #element = driver.find_element(By.ID,"consulate_date_time")

    calendar = driver.find_element(By.ID,"ui-datepicker-div")
    appointment_date = parse_date(appointment_date)

    while True:
        i = 0
        first_calendar = calendar.find_element(By.CLASS_NAME,"ui-datepicker-group-first")
        second_calendar = calendar.find_element(By.CLASS_NAME,"ui-datepicker-group-last")
        
        available_date = get_available_date(first_calendar)
        if not available_date:
            available_date = get_available_date(second_calendar)
            

        if available_date:
            new_data = parse_date(available_date)
            if new_data > appointment_date:
                print("NEW DATE")
                send_email(available_date)
            else:
                print("New date but later")
            break
        
        if i > 12:
            print("couldn't find")
            send_email("Didn't find a date")
            break
        i += 1
        time.sleep(2)
        next_button = calendar.find_element(By.CLASS_NAME,"ui-datepicker-next")
        next_button.click()
        time.sleep(2)
        