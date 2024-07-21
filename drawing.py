import requests
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import getpass
from bs4 import BeautifulSoup

#prompt user for email account credentials and recipient's email address
smtp_user = input("enter your email address: ")
smtp_password = getpass.getpass("enter your email password: ")
recipient_email = input("enter the recipient's email address: ")

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587

#create a MIMEMultipart message, set headers(from, to , subject)
message = MIMEMultipart()
message['From'] = smtp_user
message['To'] = recipient_email
message['Subject'] = 'Attached Drawing file.'

# Create an email message object
body = 'please find attached the drawing CSV file(open it with Excel).'
message.attach(MIMEText(body, 'plain'))


extracted_data = []
for i in range(1, 13, 1):
    link = "https://onelife.tw/%E5%8D%B3%E5%B0%87%E5%88%B0%E6%9C%9F?page=" + str(i) + ""

    # print("Page "+str(i)+":")
    response = requests.get(link)

    #parse the whole webpage
    soup = BeautifulSoup(response.text, 'html.parser')

    #find all spans of brand name:
    spans = soup.find_all('span', class_='text-brown')
    dates = soup.find_all('span', class_='text-success float-end')
    titles = soup.find_all('h2', class_="fs-5")

    #iterate brand name, date, titles. Append them to a list
    i = 0
    for span, date, title in zip(spans, dates, titles):
        # get text of brand name, date
        text_brand_name = span.get_text(strip=True)
        text_date = date.get_text(strip=True)

        #find and extract title
        a_id = f"c1_ItemBox_r1_aTitle_{i}"
        a_tag = title.find('a', id=a_id)
        text_a_tag = a_tag.get_text(strip=True)
        i += 1

        #extract connected-url and then concatenate them to become url
        endpoint = a_tag.get('href')
        domain_name = "https://onelife.tw"
        url = domain_name + endpoint

        #dates
        start_date, end_date = text_date.split(' ~ ')
        #add to list
        extracted_data.append([text_brand_name, start_date, end_date, text_a_tag, url])

csv_file = 'extracted_data.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Brand Name', 'Start Date', 'End Date', 'title', 'URL(link)'])
    writer.writerows(extracted_data)


# Attach the CSV file
filename = csv_file

#set the payload (the content of the attachment)
with open(filename, 'rb') as file:

    # to define a MIME type and encapsulate the binary file data
    part = MIMEBase('application', 'octet-stream')

    #Read file content and set as payload(actual data being sent)
    part.set_payload(file.read())

    #encode the payload to base64 to ensure safe transmission
    encoders.encode_base64(part)

    # the part should be treated as an attachment
    # file as it should appear when recipient downloads it
    # adds a 'Content-Disposition' header to the MIME part
    part.add_header('Content-Disposition', f'attachment; filename={filename}')

    #attach the MIME part to the message
    message.attach(part)

# Send the email
try:
    #establish a connection to an SMTP server for sending email
    with smtplib.SMTP(smtp_server, smtp_port) as server:

        #secure the connection by Transport Layer Security (TLS)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipient_email, message.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f'Failed to send email: {e}')
