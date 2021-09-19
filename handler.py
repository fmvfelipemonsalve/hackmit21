from twilio.twiml.messaging_response import MessagingResponse

from bot_brain.serve import serve

def whatsapp(event, context):
    resp = MessagingResponse()

    params = event['body']
    print(params)

    user_id = params.get('WaId')
    message = params.get('Body')

    latitude, longitude = params.get('Latitude'), params.get('Longitude')
    coordinates = None if latitude == None or longitude == None else (latitude, longitude)

    response = serve(user_id, message, coordinates)

    # Put it in a TwiML response
    resp.message(response)
    return str(resp)
