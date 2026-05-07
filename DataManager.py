import csv
import os
from werkzeug.security import generate_password_hash, check_password_hash

DATA_FOLDER = "data"
ACCOUNTS_FILE = os.path.join(DATA_FOLDER, "accounts.csv")
DECKS_FILE = os.path.join(DATA_FOLDER, "decks.csv")

ACCOUNT_FIELDS = ["username", "password_hash"]
DECK_FIELDS = ["username", "deck_name", "card_id", "name"]


def success_response(message, **extra):
    response = {
        "status": "success",
        "message": message
    }
    response.update(extra)
    return response


def error_response(message):
    return {
        "status": "error",
        "message": message
    }


def ensure_data_files():
    os.makedirs(DATA_FOLDER, exist_ok=True)

    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=ACCOUNT_FIELDS)
            writer.writeheader()

    if not os.path.exists(DECKS_FILE):
        with open(DECKS_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=DECK_FIELDS)
            writer.writeheader()


def read_csv(filename):
    ensure_data_files()

    with open(filename, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_csv(filename, fieldnames, rows):
    ensure_data_files()

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def create_account(username, password):
    ensure_data_files()

    username = username.strip()
    password = password.strip()

    if not username and not password:
        return error_response("Username and password cannot be blank.")

    if not username:
        return error_response("Username cannot be blank.")

    if not password:
        return error_response("Password cannot be blank.")

    accounts = read_csv(ACCOUNTS_FILE)

    for account in accounts:
        if account.get("username") == username:
            return error_response("Username already exists.")

    accounts.append({
        "username": username,
        "password_hash": generate_password_hash(password)
    })

    write_csv(ACCOUNTS_FILE, ACCOUNT_FIELDS, accounts)

    return success_response("Account created successfully.")


def login(username, password):
    ensure_data_files()

    username = username.strip()
    password = password.strip()

    if not username and not password:
        return error_response("Username and password cannot be blank.")

    if not username:
        return error_response("Username cannot be blank.")

    if not password:
        return error_response("Password cannot be blank.")

    accounts = read_csv(ACCOUNTS_FILE)

    for account in accounts:
        if account.get("username") == username:
            stored_hash = account.get("password_hash", "")

            if check_password_hash(stored_hash, password):
                return success_response(
                    "Login successful.",
                    username=username
                )

            return error_response("Wrong username or password.")

    return error_response("No account with that username exists. Please create an account first.")


def create_deck(username, deck_name):
    ensure_data_files()

    username = username.strip()
    deck_name = deck_name.strip()

    if not username:
        return error_response("User must be logged in to perform this action.")

    if not deck_name:
        return error_response("Deck name cannot be blank.")

    decks = read_csv(DECKS_FILE)

    for deck in decks:
        if deck.get("username") == username and deck.get("deck_name") == deck_name:
            return error_response("Deck already exists.")

    decks.append({
        "username": username,
        "deck_name": deck_name,
        "card_id": "",
        "name": ""
    })

    write_csv(DECKS_FILE, DECK_FIELDS, decks)

    return success_response(
        "Deck created successfully.",
        deckName=deck_name
    )


def delete_deck(username, deck_name):
    ensure_data_files()

    username = username.strip()
    deck_name = deck_name.strip()

    if not username:
        return error_response("User must be logged in to perform this action.")

    if not deck_name:
        return error_response("Deck name cannot be blank.")

    decks = read_csv(DECKS_FILE)

    matching_rows = [
        deck for deck in decks
        if deck.get("username") == username and deck.get("deck_name") == deck_name
    ]

    if not matching_rows:
        return error_response("Deck not found.")

    updated_decks = [
        deck for deck in decks
        if not (deck.get("username") == username and deck.get("deck_name") == deck_name)
    ]

    write_csv(DECKS_FILE, DECK_FIELDS, updated_decks)

    return success_response(
        "Deck deleted successfully.",
        deckName=deck_name
    )


def add_card_to_deck(username, deck_name, card_id, card_name):
    ensure_data_files()

    username = username.strip()
    deck_name = deck_name.strip()
    card_id = card_id.strip()
    card_name = card_name.strip()

    if not username:
        return error_response("User must be logged in to perform this action.")

    if not deck_name:
        return error_response("Deck name cannot be blank.")

    if not card_id:
        return error_response("Invalid card ID.")

    if not card_name:
        card_name = card_id

    decks = read_csv(DECKS_FILE)

    deck_exists = False

    for deck in decks:
        if deck.get("username") == username and deck.get("deck_name") == deck_name:
            deck_exists = True

            if deck.get("card_id") == card_id:
                return error_response("Card is already in this deck.")

    if not deck_exists:
        return error_response("Deck not found.")

    decks.append({
        "username": username,
        "deck_name": deck_name,
        "card_id": card_id,
        "name": card_name
    })

    write_csv(DECKS_FILE, DECK_FIELDS, decks)

    return success_response(
        "Card added to deck.",
        deckName=deck_name,
        cardID=card_id,
        cardName=card_name
    )


def remove_card_from_deck(username, deck_name, card_id):
    ensure_data_files()

    username = username.strip()
    deck_name = deck_name.strip()
    card_id = card_id.strip()

    if not username:
        return error_response("User must be logged in to perform this action.")

    if not deck_name:
        return error_response("Deck name cannot be blank.")

    if not card_id:
        return error_response("Invalid card ID.")

    decks = read_csv(DECKS_FILE)

    card_found = False
    updated_decks = []

    for deck in decks:
        same_card = (
            deck.get("username") == username and
            deck.get("deck_name") == deck_name and
            deck.get("card_id") == card_id
        )

        if same_card:
            card_found = True
        else:
            updated_decks.append(deck)

    if not card_found:
        return error_response("Card is not in this deck.")

    write_csv(DECKS_FILE, DECK_FIELDS, updated_decks)

    return success_response(
        "Card removed from deck.",
        deckName=deck_name,
        cardID=card_id
    )


def get_user_decks(username):
    ensure_data_files()

    username = username.strip()

    if not username:
        return error_response("User must be logged in to view decks.")

    decks = read_csv(DECKS_FILE)

    user_decks = {}

    for deck in decks:
        if deck.get("username") == username:
            deck_name = deck.get("deck_name", "")
            card_id = deck.get("card_id", "")
            card_name = deck.get("name", "")

            if not deck_name:
                continue

            if deck_name not in user_decks:
                user_decks[deck_name] = []

            if card_id:
                user_decks[deck_name].append({
                    "card_id": card_id,
                    "name": card_name or card_id
                })

    return success_response(
        "Decks loaded successfully.",
        decks=user_decks
    )