from twilio.twiml.messaging_response import MessagingResponse

from bot_brain.serve import serve

def whatsapp(event, context):
    resp = MessagingResponse()

    params = event['body']
    print(params)

    user_id = params.get('WaId')
    message = params.get('Body')

    response = serve(user_id, message)

    # Put it in a TwiML response
    resp.message(response)
    return str(resp)
