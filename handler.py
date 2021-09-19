from twilio.twiml.messaging_response import MessagingResponse

from bot_brain.serve import serve

from bot_brain import API

api = API()

def whatsapp(event, context):
    resp = MessagingResponse()

    params = event['body']
    print(params)

    user_id = params.get('WaId')
    message = params.get('Body')

    latitude, longitude = params.get('Latitude'), params.get('Longitude')
    coordinates = (latitude, longitude) if (latitude != None and longitude != None) else None

    image_url = params.get('MediaUrl0') if params.get('NumMedia') else None

    response, response_image = api.serve(user_id, message, coordinates, image_url)

    # Put it in a TwiML response
    msg = resp.message(response)

    if response_image:
        msg.media(response_image)

    return str(resp)
