import requests
import json
import os

QUIT = "('quit' to exit)"
BUY_OR_SELL = "Would you like to browse for products or sell them? Send 'buy' or 'sell'. " + QUIT
SELL_LOCATION = "Please share where you will be selling. LAT, LONG"
BUY_LOCATION = "Please share your location with us. LAT, LONG"
BUY_CATEGORY = "What kind of food are you looking for today? Type 0 for more on (0)"

SELL_EDIT = "You have a store associated with that number! Want to delete this store? Y/N"

SELL_CREATE_TITLE = "What are you selling? ex: popcicles!"
SELL_CREATE_PRICE = "How much in $ does each unit cost?"
SELL_CREATE_DESCRIPTION = "Describe what you are selling in more detail!"
SELL_CREATE_IMAGES = "Share an image of what you are selling!"
SELL_CONFIRM = "Does this look correct? Y/N"
SELL_READY = "Your store is live! Type 'buy' to see it!" 


class Convo():

    
    def __init__(self, api, user_id):
        self.user_id = user_id
        self.api = api
        self.current_node = BUY_OR_SELL

        self.coordinates = (0, 0)
        self.title = ""
        self.price = 0
        self.description = ""
        self.image = ""

        self.store = None
        
    
    def update(self, message, coordinates, image):

        if message == "quit":
            self.current_node == BUY_OR_SELL

        elif self.current_node == BUY_OR_SELL:
            if message == "buy":
                self.current_node = BUY_LOCATION
                return BUY_LOCATION
            elif message == "sell":
                stores = self.api.get_my_stores(user_id)
                if len(stores) == 0:
                    self.current_node = SELL_LOCATION 
                else:
                    self.current_node = SELL_EDIT

        elif self.current_node == BUY_LOCATION:
            if not coordinates:
                return "You must share your Whatsapp location!"
            self.current_node = BUY_CATEGORY
            return BUY_CATEGORY + "\n"+ self.api.get_stores_sorted(coordinates)

        elif self.current_node == BUY_CATEGORY:
            i = int(message)
            self.current_node = BUY_OR_SELL
            store = self.api.stores[i]
            return f'{self.api.store_rep(store, True)}\n{BUY_OR_SELL}' , store["image"]

        
        elif self.current_node == SELL_EDIT:
            if message == "Y":
                self.api.delete_store(user_id)
                self.current_node = SELL_LOCATION
                return "Your store was deleted!\n" + SELL_LOCATION  
            elif message == "N":
                self.current_node = BUY_OR_SELL
        
        elif self.current_node == SELL_LOCATION:
            if not coordinates:
                return "You must share your Whatsapp location!"
            self.coordinates = coordinates
            self.current_node = SELL_CREATE_TITLE
        elif self.current_node == SELL_CREATE_TITLE:
            self.title = message
            self.current_node = SELL_CREATE_PRICE
        elif self.current_node == SELL_CREATE_PRICE:
            self.price = message
            self.current_node = SELL_CREATE_DESCRIPTION
        elif self.current_node == SELL_CREATE_DESCRIPTION:
            self.description = message
            self.current_node = SELL_CREATE_IMAGES
        elif self.current_node == SELL_CREATE_IMAGES:
            self.image = image
            self.current_node = SELL_CONFIRM
            self.store = {"title": self.title,"price": self.price, "description": self.description, "user_id": self.user_id, "coordinates": self.coordinates, "image": self.image}
            return self.api.store_rep(self.store) + "\n" + SELL_CONFIRM 
        elif self.current_node == SELL_CONFIRM:
            if message == "Y":
                self.api.stores.append(self.store)
                self.current_node = BUY_OR_SELL
                return SELL_READY
            elif message == "N":
                self.current_node = SELL_CREATE_TITLE
        
        return self.current_node

class API():

    def __init__(self):
        self.users = []
        self.conversations = []
        self.stores = [{"title": "pupusas", "price": 2, "description": "Pupusas hot and ready! Cheese, Beans, Chicharron", "user_id": "9722941822", "coordinates": (42.2, -72.3), "image": "https://picsum.photos/200/300"},]

    def get_distance(self, origin, stores):
        origin = ",".join([str(each) for each in origin])
        destinations = "|".join([",".join([str(each) for each in store["coordinates"]]) for store in stores])
        url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destinations}&key={os.environ.get("GOOGLE_KEY")}'
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Request reurned an error  %s : %s" % (response.status_code, response.text))

        parsed = json.loads(response.text)
        return parsed

    def store_rep(self, store, expand = False):
        if expand:
            return f'title: {store["title"]}\nprice: ${store["price"]}\ndescription: {store["description"]}\ncell: {store["user_id"]}\naddress: {store["address"]}\ndistance: {store["duration"]}\nimage: {store["image"]}' 
        return f'title: {store["title"]}\nprice: ${store["price"]}\ndescription: {store["description"]}\ncell: {store["user_id"]}\nimage: {store["image"]}' 
        

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

    def get_stores_sorted(self, coordinates):
        
        res = self.get_distance(coordinates, self.stores)

        stores = self.stores
        for i, store in enumerate(stores):
            store["address"] = res["destination_addresses"][i]
            store["duration"] = res["rows"][0]['elements'][i]['duration']['text']
            store["distance"] = res["rows"][0]['elements'][i]['duration']['value']
        
        stores.sort(key=lambda x: x["distance"])

        stores_list = ""
        for i, store in enumerate(stores):
            stores_list += "({}) ${}/{} - {} \n".format(i, store['price'], store["title"], store["duration"])
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
    reply = api.serve(user_id, "opening message", None)
    while(True):
        print(reply[0])
        message = input()
        if message == 'quit':
            break
        elif message == 'location':
            reply = api.serve(user_id, '', (42,-71), None)
        elif message == 'image':
            reply = api.serve(user_id, '', None, "https://picsum.photos/200/300")
        else:
            reply = api.serve(user_id, message, None, None)