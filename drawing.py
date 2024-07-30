import base64
import os
import requests
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
# from google.oauth2 import message
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]

def authenticate_gmail_api():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret_drawing.json", SCOPES)
            creds = flow.run_local_server(port=8080)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds
def create_message_with_attachment(sender, to, subject, message_text, file_path):
    # message = MIMEMultipart(message_text)
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = to
    message['Subject'] = subject
    ###added###
    #attach the body with the msg instance
    message.attach(MIMEText(message_text, 'plain'))
    #open the file to be sent
    filename = os.path.basename(file_path)
    attachment = open(file_path, 'rb')
    #instance of MIMEBase and named as part
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={filename}')
    #attach the instance 'part'(attachment) to instance 'message'
    message.attach(part)
    #encode the message(attachment, message) in base64 and return
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}
def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f'Message Id: {message["id"]}')
        return message
    except Exception as error:
        print(f'An error occurred: {error}')
        return None
def scraping_website():
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
def main():
    #scraping website
    scraping_website()
    #gmail api authentication
    creds = authenticate_gmail_api()
    #create the service
    service = build('gmail', 'v1', credentials=creds)
    sender = 'hydedada0129@gmail.com'
    to = 'hydedada0129@gmail.com'
    subject = 'Drawing CSV file update'
    message_text = "please find attached csv file..."
    file_path = "/home/oem/PycharmProjects/drawing/extracted_data.csv"
    message = create_message_with_attachment(sender, to, subject, message_text, file_path)
    send_message(service, 'me', message)

if __name__ == "__main__":
    main()