import requests
import json

from secrets import GOOGLE_KEY


QUIT = "('quit' to exit)"
BUY_OR_SELL = "Would you like to browse for products or sell them? Send 'buy' or 'sell'. " + QUIT
SELL_LOCATION = "Please share where you will be selling. LAT, LONG"
BUY_LOCATION = "Please share your location with us. LAT, LONG"
BUY_CATEGORY = "What kind of food are you looking for today?"

SELL_CREATE_MESSAGE = "What are you selling? ex: popcicles - $1.25"

SELL_EDIT = "You have a store associated with that number! Want to delete this store? Y/N"

SELL_PHONE = "What is your phone number? Send your 10 digit phone number."
SELL_CREATE = "We cannot find your number in our system. Please help us create your account by providing the following information. "
SELL_CREATE_CATEGORY = "Please indicate the cateogry of your product below (i.e. 'tacos', 'mangonadas')"
SELL_CREATE_PRODUCTS = "Please indicate specific products you sell or additional items (i.e. 'carne asada', 'sandia') This is optional. To skip, type 'skip'."
state_properties = ["category", "products", "picture", "address", "open?"]
HELP = "We cannot help you. Please make sure you are spelling your response correctly."



class Convo():

    
    def __init__(self, api, user_id):
        self.user_id = user_id
        self.api = api
        self.current_node = BUY_OR_SELL
        self.location = (0, 0)
        self.category = "food"
        self.products = None
    
    def update(self, message, coordinates, image_url):
        if message == "quit":
            self.current_node == BUY_OR_SELL
        
        elif self.current_node == BUY_OR_SELL:
            if message == "buy":
                self.current_node = BUY_CATEGORY
                return BUY_CATEGORY + "\n"+ self.api.get_all_stores_TEXT(coordinates)
            elif message == "sell":
                stores = api.get_my_stores(user_id)
                if len(stores) == 0:
                    self.current_node = SELL_CREATE_MESSAGE
                else:
                    self.current_node = SELL_EDIT
        elif self.current_node == SELL_EDIT:
            if message == "Y":
                self.api.delete_store(user_id)
                self.current_node = BUY_OR_SELL
                return "Your store was deleted!\n" + BUY_OR_SELL  
            elif message == "N":
                self.current_node = BUY_OR_SELL
        
        
        elif self.current_node == BUY_CATEGORY:
            i = int(message)
            self.current_node = BUY_OR_SELL
            return json.dumps(self.api.stores[i], indent=4) + "\n" + BUY_OR_SELL, self.api.stores[i]["image_url"]

        
        elif self.current_node == SELL_CREATE_MESSAGE:
            self.api.stores.append({"message": message, "user_id": self.user_id, "coordinates": coordinates, "image_url": image_url})
            self.current_node = BUY_OR_SELL

            return "Your store is live! Type 'buy' to see it!"
        
        return self.current_node

def get_distance(origin, stores):
    origin = ",".join([str(each) for each in origin])
    destinations = "|".join([",".join([str(each) for each in store["coordinates"]]) for store in stores])
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destinations}&key={GOOGLE_KEY}'
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Request reurned an error  %s : %s" % (response.status_code, response.text))

    parsed = json.loads(response.text)
    return parsed


        

class API():

    def __init__(self):
        self.users = []
        self.conversations = []
        self.stores = [{"message": "tacos", "user_id": "9722949822", "coordinates": (42, -72), "image_url": "https://picsum.photos/200/300"}, {"message": "pupusas", "user_id": "9722949823", "coordinates": (42, -71), "image_url": "https://picsum.photos/200/300"}]
    
    
    

    def add_user(self, user_id):
        user = {"user_id": user_id, "conversation": Convo(self, user_id)}
        self.users += [user]
        return user["conversation"].current_node
    
    def user_exists(self, user_id):
        for user in self.users:
            if user["user_id"] == user_id:
                return True
        return False
    
    def get_user(self, user_id):
        return [user for user in self.users if user["user_id"] == user_id][0]
    

    def delete_store(self, user_id):
        self.stores = [store for store in self.stores if not store['user_id'] == user_id]

    def get_all_stores_TEXT(self, coordinates):
        res = get_distance(coordinates, self.stores)
        stores = self.stores
        for i, store in enumerate(stores):
            store["address"] = res["destination_addresses"][i]
            store["duration"] = res["rows"][0]['elements'][i]['duration']['text']
            store["distance"] = res["rows"][0]['elements'][i]['duration']['value']
        
        stores.sort(key=lambda x: x["distance"])

        stores_list = ""
        for i, store in enumerate(stores):
            stores_list += "({}) {} - {} \n".format(i, store["message"], store["duration"])
        return stores_list[:-1]

    def get_my_stores_TEXT(self, user_id):
        stores = self.get_my_stores(user_id)
        stores_list = ""
        for i, store in enumerate(self.stores):
            stores_list += "({}) {} \n".format(i, store["message"])
        return stores_list[:-1]
    
    def get_my_stores(self, user_id):
        return [store for store in self.stores if store["user_id"] == user_id]

    def serve(self, user_id, message, coordinates, image_url = ""):
        if not self.user_exists(user_id):
            self.add_user(user_id)
        user = self.get_user(user_id)

        reply = user["conversation"].update(message, coordinates, image_url)

        image_url = None
        if type(reply) is tuple:
            reply, image_url = reply
        return reply, image_url



if __name__ == "__main__":
    api = API()

    user_id = "9722949822"
    reply = api.serve(user_id, "opening message", [42,-71])

    while(True):
        print(reply)
        message = input()
        if message == 'quit':
            break
        reply = api.serve(user_id, message, [42,-71], "https://picsum.photos/200/300")