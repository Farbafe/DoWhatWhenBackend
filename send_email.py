from mailjet_rest import Client
import os
from dotenv import load_dotenv
import argparse


parser = argparse.ArgumentParser("Send emails via Mailjet!")
parser.add_argument('to_email')
parser.add_argument('to_name')
parser.add_argument('question')
parser.add_argument('link')
parser.add_argument('data_subject', default='Greetings', nargs='*')
parser.add_argument('data_text_part', default='Hello World!', nargs='*')
parser.add_argument('data_html_part', default='<b>Hello World</b>', nargs='*')
parser.add_argument('data_custom_id', default='customid', nargs='*')
args, unkwn = parser.parse_known_args()
load_dotenv()
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
from_email = os.getenv("FROM_EMAIL")
from_name = os.getenv("FROM_NAME")
to_email = args.to_email
to_name = args.to_name
data_subject = args.data_subject
data_text_part = args.data_text_part
data_html_part = args.data_html_part
data_custom_id = args.data_custom_id
email_template = '''
    <h1>Greetings from DoWhatWhen.</h1>
    Your event with question {} has now reached the voting deadline. Please visit the result at <a href='{}'>this link</a>.
'''.format(args.question, args.link)
mailjet = Client(auth=(api_key, api_secret), version='v3.1')
data = {
  'Messages': [
    {
      "From": {
        "Email": from_email,
        "Name": from_name
      },
      "To": [
        {
          "Email": to_email,
          "Name": to_name
        }
      ],
      "Subject": data_subject,
      "TextPart": data_text_part,
      "HTMLPart": email_template,
      "CustomID": data_custom_id
    }
  ]
}
result = mailjet.send.create(data=data)
print(result.status_code)
print(result.json())
