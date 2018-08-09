# coding:utf-8

import logging
import traceback
import get_message
import util
import os


logger = logging.getLogger()
logger.setLevel(util.logger_level())

def lambda_handler(event, context):
    try:
        logger.debug(event)
        bot_name = os.environ.get('BOT_NAME', '')
        text = event['text'].replace(bot_name, '').replace('@', '').strip()

        user_name = event['from']['name']

        msg = user_name + 'さん '
        if text == '':
            msg += 'はい！'
        elif text.find('って何') > -1:
            msg += get_message.wikipedia_search(text)
        elif text.find('天気') > -1:
            msg += get_message.weather_info(text)
        elif text.find('雨') > -1:
            msg += get_message.weather_info(text)
        elif text.find('雪') > -1:
            msg += get_message.weather_info(text)
        elif text.find('晴') > -1:
            msg += get_message.weather_info(text)
        else:
            msg += get_message.docomo_response(text)

        payload = {
            'type': 'message',
            'text': msg
        }
        return payload

    except:
        logger.error(traceback.format_exc())
        return traceback.format_exc()
