from twilio.twiml.messaging_response import MessagingResponse

from bot_brain.serve import serve

def whatsapp(event, context):
    resp = MessagingResponse()

    params = event['body']
    print(params)

    user_id = params.get('WaId')
    message = params.get('Body')
    coordinates = (params.get('Latitude'), params.get('Longitude'))

    response = serve(user_id, message, coordinates)

    # Put it in a TwiML response
    resp.message(response)
    return str(resp)
