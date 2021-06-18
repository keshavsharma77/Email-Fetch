from __future__ import print_function
import os.path
import pickle
import time
import email
from bs4 import BeautifulSoup
import base64
import email
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    # results = service.users().labels().list(userId='me').execute()
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    # labels = results.get('labels', [])
    # if not labels:

    message_count = int(input('How many messages do you want to fetch?: '))
    if not messages:
        print('No labels found.')
    else:
        print('Fetching Messages...:')
        i = 1
        for message in messages[:message_count]:
            # msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
            msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
            print('Message No. :', i)
            #print('Message snippet: %s' % msg['snippet'])
            msg_str = base64.urlsafe_b64decode(msg['raw'].encode("utf-8")).decode("utf-8")
            mime_msg = email.message_from_string(msg_str)
            #print(mime_msg)

            message1 = service.users().messages().get(userId='me', id=message['id']).execute()
            payload = message1['payload']
            headers = payload['headers']
            for d in headers:
                if d['name'] == 'Subject':
                    subject = d['value']
                if d['name'] == 'From':
                    sender = d['value']

            soup = BeautifulSoup(msg['snippet'], "lxml")
            body = soup.body()
            print("Subject: ", subject)
            print("From: ", sender)
            print("Message: ", body)
            print('\n')

            for part in message1['payload']['parts']:
                if (part['filename'] and part['body'] and part['body']['attachmentId']):
                    attachment = service.users().messages().attachments().get(id=part['body']['attachmentId'], userId='me', messageId=message['id']).execute()
                    file_data = base64.urlsafe_b64decode(attachment['data'].encode('utf-8'))
                    path = ''.join(['attachments/', part['filename']])
                    f = open(path, 'wb')
                    f.write(file_data)
                    f.close()
                    print('File saved successfully in Attachments folder')
                    print('File Location:')
                    print('\t', path)
                    print('\n')
            i = i + 1
            time.sleep(2)


if __name__ == '__main__':
    main()