# Telegram Link Finder Bot

This project is a Telegram bot designed to help users find links based on their queries. It utilizes web scraping techniques to extract relevant links from specified websites and provides a user-friendly interface for interaction.

## Features

- Search for links on specified websites using keywords.
- Extract streaming links and relevant content from web pages.
- Handle user commands and messages effectively.

## Project Structure

```
telegram-link-finder-bot/
├── src/
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── commands.py
│   │   │   └── messages.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── search_engine.py
│   │       └── precise_playwright_adapter.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   └── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/telegram-link-finder-bot.git
   ```

2. Navigate to the project directory:
   ```
   cd telegram-link-finder-bot
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables by copying `.env.example` to `.env` and filling in the necessary values.

## Usage

To run the bot, execute the following command:
```
python src/main.py
```

Once the bot is running, you can interact with it on Telegram by sending commands to search for links.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.