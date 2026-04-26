ERROR_CODES = {
    # Authentication / Account Errors
    "AUTH_001": "Wrong username or password.",
    "AUTH_002": "Username already exists.",
    "AUTH_003": "Username cannot be blank.",
    "AUTH_004": "Password cannot be blank.",
    "AUTH_005": "Username and password cannot be blank.",
    "AUTH_006": "User must be logged in to perform this action.",

    # Search Errors
    "SEARCH_001": "No cards matched the search criteria.",
    "SEARCH_002": "Invalid search field value.",
    "SEARCH_003": "Card search error.",
    "SEARCH_004": "Search request was missing required data.",

    # Card Errors
    "CARD_001": "Card not found.",
    "CARD_002": "Invalid card ID.",
    "CARD_003": "Unable to retrieve card details.",

    # Deck Errors
    "DECK_001": "Deck name cannot be blank.",
    "DECK_002": "Deck already exists.",
    "DECK_003": "Deck not found.",
    "DECK_004": "Unable to create deck.",
    "DECK_005": "Unable to delete deck.",
    "DECK_006": "Card is already in this deck.",
    "DECK_007": "Card is not in this deck.",

    # Database Errors
    "DB_001": "Unable to connect to the card database.",
    "DB_002": "Database query failed.",
    "DB_003": "Deck storage could not be updated.",

    # Server / Protocol Errors
    "SERVER_001": "Invalid protocol message.",
    "SERVER_002": "Unsupported command.",
    "SERVER_003": "Internal server error.",
    "SERVER_004": "Client disconnected unexpectedly."
}


def get_error_message(error_code):
    return ERROR_CODES.get(error_code, "Unknown error occurred.")