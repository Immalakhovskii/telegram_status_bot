import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import MissingTokens, IncorrectHTTPStatus

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Homework checked: reviewer approved it. Hooray!',
    'reviewing': 'Reviewer started checking homework',
    'rejected': 'Homework checked: reviewer has comments'
}


def send_message(bot, message):
    """Sending messages function."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Message sent: "{message}"')
    except Exception as error:
        logger.error(f'Error occurred during message sending: {error}')


def get_api_answer(current_timestamp):
    """Function for receiving responses from Practicum API."""
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code == HTTPStatus.OK:
            return response.json()

    except IncorrectHTTPStatus:
        message = (
            'Practicum API endpoint is not available, '
            f'server response code: {response.status_code}'
        )
        logger.error(message)
        raise IncorrectHTTPStatus(message)


def check_response(response):
    """Function for checking response from Practicum API."""
    if not isinstance(response['homeworks'], list):
        raise TypeError(
            'Incorrect response received from API:'
            '"homeworks" key not returning list'
        )
    try:
        response['current_date']
        return response['homeworks']
    except KeyError as expected_key:
        logger.error(f'API response does not have expected_key {expected_key}')


def parse_status(homework):
    """Function for receiving data on last homework."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS.keys():
        raise KeyError('Unknown homework status')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Homework status changed "{homework_name}". {verdict}'


def check_tokens():
    """Function for checking for tokens."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Homework status bot main logic."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    previous_message = None
    current_timestamp = int(time.time())
    while check_tokens() is True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks != []:
                message = parse_status(homeworks[0])
                send_message(bot, message)
            else:
                logger.debug('Homework status did not change')

        except Exception as error:
            message = f'Program crash: {error}'
            logger.error(message)
            if message != previous_message:
                send_message(bot, message)
                previous_message = message

        finally:
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

    else:
        message = 'Environment tokens are not available'
        logger.critical(message)
        raise MissingTokens(message)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)

    main()
