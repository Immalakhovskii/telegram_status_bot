# Telegram Bot: Project Status Checker #
*This project uploaded to Heroku*
****
### Description ###
This Telegram bot checked status of a projects (homeworks) sent to a review via simple Practicum API. This API has only one endpoint with accesses by token. Practicum API returns JSON with 2 keys: "current_date" with unix time stamp of a time of sending request and "homeworks" which leads to list of dictionaries of homeworks' data and their statuses. The bot once in 10 minutes sends request to the endpoint and checks if response has homeworks and if they changed status (all statuses listed in dictionary HOMEWORK_VERDICTS). If status changed the bot sends message with new status. Also it sends messages with descriptions of variety of possible errors and logs events on four levels.

### Technology Stack ###
Python 3.7 / python-telegram-bot 13.7 (Python interface for the Telegram Bot API)

### Exceptions and Errors ###
The bot expects such exceptions and errors:
- Error during sending message
- Missing valid environment tokens
- Unavailability of Practicum API endpoint
- Incorrect response received from API

### Logging ###
The bot logs:
- No changes in homework status (debug)
- Sending of every message (info)
- Error during sending message (error)
- Unavailability of Practicum API endpoint (error)
- Incorrect response received from API (error)
- Missing valid environment tokens (critical)