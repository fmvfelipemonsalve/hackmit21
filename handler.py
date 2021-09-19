from urllib.parse import unquote
from twilio.twiml.messaging_response import MessagingResponse

def whatsapp(event, context):

    body = event['body']

    print(body)

    # Put it in a TwiML response
    resp = MessagingResponse()
    resp.message('hi')

    return str(resp)
