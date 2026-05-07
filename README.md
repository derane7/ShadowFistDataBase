# ShadowFistDatabase

ShadowFistDatabase is a web-based collectible card game database and deck management application created for a Computer Networking group project. The project is based around the Shadowfist card game and allows users to browse cards, search through the database using multiple filters, create accounts, and manage custom decks.

The project was developed using Python, Flask, HTML, CSS, JavaScript, Pandas, and Excel-based data storage.

---

## Features

* User account creation and login system
* Searchable Shadowfist card database
* Multiple card filtering options

  * Subtype
  * Cost
  * Pow
  * Bod
  * Res
  * Keywords
* Individual card result display page
* Deck creation and deletion
* Add and remove cards from decks
* CSV-based account and deck storage
* Excel spreadsheet integration for card data
* Web-based frontend interface using Flask

---

## Technologies Used

### Backend

* Python 3
* Flask
* Pandas
* OpenPyXL

### Frontend

* HTML5
* CSS3
* JavaScript

### Data Storage

* CSV files
* Excel spreadsheet database

---

## Project Structure

```text
ShadowFistDatabase/
│
├── PrimaryWebServer.py          # Main Flask web server
├── DataManager.py               # Account and deck management logic
├── ErrorCodes.py                # Error handling and return codes
├── Styles.css                   # Main site styling
│
├── Login.html                   # Login page
├── CreateAccount.html           # Account creation page
├── Account.html                 # User account and deck page
├── Search.html                  # Card search page
├── Result.html                  # Individual card result page
│
├── data/
│   ├── Shadowfist_Project_Table.xlsx   # Card database
│   ├── accounts.csv                    # User account storage
│   └── decks.csv                       # Deck storage
│
└── README.md
```

---

## Installation and Setup

### 1. Clone the Repository or Download the Zip file

Option 1 — Clone Using Git

Open Comman Prompt, Powershell, or a Terminal in the desired location and run:

```bash
git clone <repository-url>
cd ShadowFistDatabase
```

Option 2 — Download ZIP from GitHub
This method is easier for users unfamiliar with Git.

Steps
Open the GitHub repository page
Click the green Code button
Select Download ZIP
Extract the ZIP file
Open the extracted project folder

Then open Command Prompt or PowerShell inside the folder

A simple Windows method:

Hold Shift
Right-click inside the folder
Select:
“Open PowerShell window here”
OR “Open in Terminal”


### 2. Install Required Dependencies

Inside the open terminal run the command:

```bash
pip install flask flask-cors pandas openpyxl numpy
```

### 3. Run the Server

Inside the open terminal run the command:

```bash
python PrimaryWebServer.py
```

### 4. Open the Application

Once the server is running, open your browser and go to:

http://127.0.0.1:5000/


---

## How the Project Works

The Flask server loads the Shadowfist card database from the Excel spreadsheet located in the `/data` folder. Users can then interact with the web interface to:

1. Search for cards using filters
2. View card details
3. Create an account
4. Log in
5. Create decks
6. Add or remove cards from decks

User account information and deck data are stored locally using CSV files.

---

## Search System

The search functionality supports multiple filtering options and performs flexible matching against the card database.

Supported search fields include:

* Title
* Subtype
* Cost
* Pow
* Bod
* Res
* Keywords

The application also performs automatic data cleanup when loading the spreadsheet, including:

* Removing duplicate header rows
* Cleaning whitespace issues
* Handling missing values
* Normalizing numeric values
* Correcting formatting inconsistencies

---

## Notes

* The project was created for educational purposes as part of a university Computer Networking group project.
* The project currently uses local CSV and Excel file storage rather than a full SQL database.
* Some functionality and UI elements were simplified to fit project scope and timeline requirements.

---

## Future Improvements

Potential future improvements could include:

* Full SQL database integration
* Improved authentication and security
* Expanded card search functionality
* Better deck editing tools
* Mobile responsive design improvements
* User profile customization
* Cloud hosting support
* Multiplayer or social features

---

## Contributors

Developed as a group project designed to fit the criteria of two independent college courses (Networking, Database)

---

## License

This project was created for educational use only.

Shadowfist and related intellectual property belong to their respective owners.
