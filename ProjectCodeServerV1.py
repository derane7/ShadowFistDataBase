import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 65432

# In-memory storage
users = {}
decks = {}
cards_db = [
    {"cardID": 1, "name": "Dragon", "cost": 5, "type": "Creature"},
    {"cardID": 2, "name": "Ninja", "cost": 2, "type": "Hero"},
    {"cardID": 3, "name": "Temple", "cost": 3, "type": "Location"}
]

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break

            request = json.loads(data.decode())
            response = process_request(request)

            conn.sendall(json.dumps(response).encode())

        except Exception as e:
            conn.sendall(json.dumps({
                "type": "Error",
                "message": str(e)
            }).encode())

    conn.close()


def process_request(req):
    action = req.get("action")

    # Create Account
    if action == "create":
        username = req["username"]
        password = req["password"]

        if username in users:
            return {"type": "Error", "message": "User exists"}
        
        users[username] = password
        return {"type": "addNewCredentials"}

    # Login
    elif action == "login":
        username = req["username"]
        password = req["password"]

        if users.get(username) == password:
            return {"type": "loginSuccess"}
        else:
            return {"type": "Error", "message": "Wrong username or password!"}

    # Search
    elif action == "search":
        results = []
        for card in cards_db:
            match = True
            for key, value in req["filters"].items():
                if str(card.get(key)) != str(value):
                    match = False
            if match:
                results.append(card)

        if results:
            return {"type": "searchResults", "cards": results}
        else:
            return {"type": "noCard"}

    # Card Details
    elif action == "cardDetails":
        for card in cards_db:
            if card["cardID"] == req["cardID"]:
                return {"type": "cardDetails", "card": card}
        return {"type": "Error", "message": "Card not found"}

    # Create Deck
    elif action == "createDeck":
        user = req["username"]
        deck_name = req["deckName"]

        decks.setdefault(user, {})
        if deck_name in decks[user]:
            return {"type": "Error", "message": "Deck exists"}

        decks[user][deck_name] = []
        return {"type": "deckCreated", "deckName": deck_name}

    # Get Deck
    elif action == "selectDeck":
        user = req["username"]
        deck_name = req["deckName"]

        try:
            return {
                "type": "returnDeck",
                "deckName": deck_name,
                "cards": decks[user][deck_name]
            }
        except:
            return {"type": "Error", "message": "Deck not found"}

    # Delete Deck
    elif action == "removeDeck":
        user = req["username"]
        deck_name = req["deckName"]

        try:
            del decks[user][deck_name]
            return {"type": "deckDeletion"}
        except:
            return {"type": "Error", "message": "Deck not found"}

    # Add Card
    elif action == "addCard":
        user = req["username"]
        deck_name = req["deckName"]
        card_id = req["cardID"]

        decks[user][deck_name].append(card_id)
        return {"type": "addCard"}

    # Remove Card
    elif action == "removeCard":
        user = req["username"]
        deck_name = req["deckName"]
        card_id = req["cardID"]

        try:
            decks[user][deck_name].remove(card_id)
            return {"type": "removeCard"}
        except:
            return {"type": "Error", "message": "Card not in deck"}

    return {"type": "Error", "message": "Invalid request"}


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server started...")

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()


if __name__ == "__main__":
    start_server()