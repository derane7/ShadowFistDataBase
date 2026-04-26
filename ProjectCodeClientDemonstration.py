# Client program for the Shadowfist Deck Manager
# Purpose:
# This client connects to the Shadowfist Deck Manager server and allows a user
# to create an account, log in, search cards, view card details, and manage decks.
# The connection remains open until the user chooses to exit.
# Designed as a demontration of the networking protocol and client functionality, not as a full-featured client application.
# The primary method of interaction for this project is web-based

from socket import *


def send_request(client_socket, message):
    """
    Sends one protocol message to the server and waits for one response.
    The client socket remains open for future requests.
    """
    try:
        if not message.endswith("\n"):
            message += "\n"

        client_socket.send(message.encode())

        response = client_socket.recv(4096).decode()

        if not response:
            return "Error SERVER_004 Server closed the connection."

        return response.strip()

    except Exception as e:
        return "Error SERVER_003 " + str(e)


def create_account(client_socket):
    username = input("Create username: ").strip()
    password = input("Create password: ").strip()

    message = "createAccount username={} password={}".format(username, password)
    response = send_request(client_socket, message)

    print("\nServer Response:")
    print(response)


def login(client_socket):
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    message = "checkLogin username={} password={}".format(username, password)
    response = send_request(client_socket, message)

    print("\nServer Response:")
    print(response)

    if "loginSuccess" in response:
        return username

    return None


def logout(client_socket):
    response = send_request(client_socket, "logout")

    print("\nServer Response:")
    print(response)

    return None


def search_cards(client_socket):
    print("\nLeave fields blank if you do not want to search by that value.")

    subtype = input("Subtype: ").strip()
    cost = input("Cost: ").strip()
    fight = input("Fight: ").strip()
    bod = input("Bod: ").strip()
    res = input("Res: ").strip()
    keywords = input("Keywords: ").strip()

    message = (
        "searchForCard "
        "subtype={} cost={} fight={} bod={} res={} keywords={}"
    ).format(subtype, cost, fight, bod, res, keywords)

    response = send_request(client_socket, message)

    print("\nServer Response:")
    print(response)


def get_card_details(client_socket):
    card_id = input("Enter card ID: ").strip()

    message = "getCardDetails cardID={}".format(card_id)
    response = send_request(client_socket, message)

    print("\nServer Response:")
    print(response)


def create_deck(client_socket, username):
    deck_name = input("Deck name: ").strip()

    message = "createDeck username={} deckName={}".format(username, deck_name)
    response = send_request(client_socket, message)

    print("\nServer Response:")
    print(response)


def select_deck(client_socket, username):
    deck_name = input("Deck name to load: ").strip()

    message = "selectDeck username={} deckName={}".format(username, deck_name)
    response = send_request(client_socket, message)

    print("\nServer Response:")
    print(response)


def remove_deck(client_socket, username):
    deck_name = input("Deck name to delete: ").strip()

    message = "removeDeck username={} deckName={}".format(username, deck_name)
    response = send_request(client_socket, message)

    print("\nServer Response:")
    print(response)


def add_card_to_deck(client_socket, username):
    deck_name = input("Deck name: ").strip()
    card_id = input("Card ID to add: ").strip()

    message = "addCard username={} deckName={} cardID={}".format(
        username, deck_name, card_id
    )

    response = send_request(client_socket, message)

    print("\nServer Response:")
    print(response)


def remove_card_from_deck(client_socket, username):
    deck_name = input("Deck name: ").strip()
    card_id = input("Card ID to remove: ").strip()

    message = "removeCard username={} deckName={} cardID={}".format(
        username, deck_name, card_id
    )

    response = send_request(client_socket, message)

    print("\nServer Response:")
    print(response)


def print_menu(username):
    print("\n===== Shadowfist Deck Manager Client =====")

    if username is None:
        print("Current user: Guest / Not logged in")
    else:
        print("Current user:", username)

    print("\n1. Create account")
    print("2. Log in")
    print("3. Log out")
    print("4. Search cards")
    print("5. View card details")
    print("6. Create deck")
    print("7. Load deck")
    print("8. Delete deck")
    print("9. Add card to deck")
    print("10. Remove card from deck")
    print("11. Exit")


def main():
    # Replace with the server's actual IP address when testing across machines/VMs.
    server_ip = "127.0.0.1"
    server_port = 12345

    logged_in_user = None

    client_socket = socket(AF_INET, SOCK_STREAM)

    try:
        client_socket.connect((server_ip, server_port))
        print("Connected to Shadowfist server at {}:{}.".format(server_ip, server_port))

        while True:
            print_menu(logged_in_user)
            choice = input("Choose an option: ").strip()

            if choice == "1":
                create_account(client_socket)

            elif choice == "2":
                logged_in_user = login(client_socket)

            elif choice == "3":
                if logged_in_user is None:
                    print("No user is currently logged in.")
                else:
                    logged_in_user = logout(client_socket)

            elif choice == "4":
                search_cards(client_socket)

            elif choice == "5":
                get_card_details(client_socket)

            elif choice == "6":
                if logged_in_user is None:
                    print("You must log in before creating a deck.")
                else:
                    create_deck(client_socket, logged_in_user)

            elif choice == "7":
                if logged_in_user is None:
                    print("You must log in before loading a deck.")
                else:
                    select_deck(client_socket, logged_in_user)

            elif choice == "8":
                if logged_in_user is None:
                    print("You must log in before deleting a deck.")
                else:
                    remove_deck(client_socket, logged_in_user)

            elif choice == "9":
                if logged_in_user is None:
                    print("You must log in before adding a card to a deck.")
                else:
                    add_card_to_deck(client_socket, logged_in_user)

            elif choice == "10":
                if logged_in_user is None:
                    print("You must log in before removing a card from a deck.")
                else:
                    remove_card_from_deck(client_socket, logged_in_user)

            elif choice == "11":
                print("Closing client.")
                send_request(client_socket, "exit")
                break

            else:
                print("Invalid menu option. Please choose a number from 1 to 11.")

    except ConnectionRefusedError:
        print("Could not connect to the server. Make sure the server is running.")

    except Exception as e:
        print("Client error:", e)

    finally:
        client_socket.close()
        print("Client socket closed.")


if __name__ == "__main__":
    main()