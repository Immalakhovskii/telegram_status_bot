import logging
import sys
import os
import requests
import time
from http import HTTPStatus

import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Фунцкция отправки сообщений."""
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logger.info(f'Отправлено сообщение: "{message}"')


def get_api_answer(current_timestamp):
    """Получение ответа от API Практикум.Домашка."""
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        else:
            message = (
                'Эндпоинт API Практикум.Домашка недоступен, '
                f'код ответа сервера: {response.status_code}'
            )
            logger.error(message)
            raise exceptions.IncorrectHTTPStatus(message)

    except Exception as error:
        logger.error(f'Ошибка при запросе к API Практикум.Домашка: {error}')


def check_response(response):
    """Проверка корректности ответа API Практикум.Домашка."""
    if not isinstance(response['homeworks'], list):
        raise TypeError(
            'Получен некорректный ответ API:'
            'ключ homeworks не возвращает список'
        )
    try:
        response['current_date']
        return response['homeworks']
    except KeyError as expected_key:
        logger.error(f'В ответе API нет ожидаемого ключа {expected_key}')


def parse_status(homework):
    """Получение данных о последней домашней работе."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES.keys():
        raise KeyError('Неизвестный статус домашней работы')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия токенов."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    previous_message = None
    while check_tokens() is True:
        try:
            current_timestamp = int(time.time())
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks != []:
                message = parse_status(homeworks[0])
                send_message(bot, message)
            else:
                logger.debug('Статус домашки не менялся')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != previous_message:
                send_message(bot, message)
                previous_message = message
            time.sleep(RETRY_TIME)
    else:
        message = 'Недоступны токены окружения'
        logger.critical(message)
        raise exceptions.MissingTokens(message)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)

    main()
