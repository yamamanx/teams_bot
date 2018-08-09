# coding:utf-8

import logging
import requests
import wikipedia
import traceback
import json
import os
import util
from datetime import datetime


logger = logging.getLogger()
logger.setLevel(util.logger_level())


def docomo_response(text):
    docomo_app_id = os.environ.get('DOCOMO_APP_ID', '')
    docomo_api_key = os.environ.get('DOCOMO_API_KEY', '')
    docomo_endpoint = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/dialogue?APIKEY={api_key}'.format(
        api_key=docomo_api_key
    )

    headers = {
        'Content-type': 'application/json;charset=UTF-8'
    }

    payload = {
        "language": "ja-JP",
        "botId": "Chatting",
        "appId": docomo_app_id,
        "voiceText": text,
        "appRecvTime": "2018-08-02 22:44:22",
        "appSendTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    response = requests.post(
        docomo_endpoint,
        data=json.dumps(payload),
        headers=headers
    )

    data = response.json()
    return data['systemText']['expression']


def wikipedia_search(text):
    wikipedia.set_lang('ja')
    search_text = text[:text.find('って何')]
    search_response = wikipedia.search(search_text)

    logger.debug(search_response)

    if len(search_response) > 0:
        logger.debug(len(search_response))
        logger.debug('search_response[0]:' + search_response[0])

        try:
            wiki_page = wikipedia.page(search_response[0])
        except:
            try:
                wiki_page = wikipedia.page(search_response[1])
            except:
                logger.error(traceback.format_exc())

        response_string = '説明しよう\n'
        response_string += wiki_page.content[0:200] + '.....\n'
        response_string += wiki_page.url
    else:
        response_string = '今はまだ見つけられませんでした。'

    logger.debug(response_string)
    return response_string


def get_city_id(text):
    memo = ''
    if text.find('大阪') > -1:
        city_id = '270000'
    elif text.find('東京') > -1:
        city_id = '130010'
    elif text.find('北陸') > -1 or text.find('金沢') > -1 or text.find('石川') > -1:
        city_id = '170010'
    elif text.find('愛知') > -1 or text.find('名古屋') > -1:
        city_id = '230010'
    elif text.find('京都') > -1:
        city_id = '260010'
    elif text.find('神戸') > -1 or text.find('兵庫') > -1:
        city_id = '280010'
    elif text.find('神奈川') > -1 or text.find('横浜') > -1:
        city_id = '140010'
    elif text.find('奈良') > -1:
        city_id = '290010'
    elif text.find('和歌山') > -1:
        city_id = '300010'
    elif text.find('熊本') > -1 or text.find('阿蘇') > -1:
        city_id = '430010'
    else:
        city_id = '270000'
        memo = '場所がよくわからないもんでとりあえず'
    return city_id, memo


def weather_info(text):
    weather_api_url = 'http://weather.livedoor.com/forecast/webservice/json/v1'
    response_string = ''
    city_id, memo = get_city_id(text)
    response_string += memo

    try:
        params = {'city':city_id}
        response = requests.get(weather_api_url,params=params)
        response_dict = json.loads(response.text)
        title = response_dict["title"]
        description = response_dict["description"]["text"]
        response_string += title + "です。\n\n"
        forecasts_array = response_dict["forecasts"]
        forcast_array = []
        for forcast in forecasts_array:
            telop = forcast["telop"]
            telop_icon = ''
            if telop.find('雪') > -1:
                telop_icon = ':showman:'
            elif telop.find('雷') > -1:
                telop_icon = ':thunder_cloud_and_rain:'
            elif telop.find('晴') > -1:
                if telop.find('曇') > -1:
                    telop_icon = ':partly_sunny:'
                elif telop.find('雨') > -1:
                    telop_icon = ':partly_sunny_rain:'
                else:
                    telop_icon = ':sunny:'
            elif telop.find('雨') > -1:
                telop_icon = ':umbrella:'
            elif telop.find('曇') > -1:
                telop_icon = ':cloud:'
            else:
                telop_icon = ':fire:'

            temperature = forcast["temperature"]
            min_temp = temperature["min"]
            max_temp = temperature["max"]
            temp_text = ''
            if min_temp is not None:
                if len(min_temp) > 0:
                    temp_text += '\n最低気温は' + min_temp["celsius"] + "度です。"
            if max_temp is not None:
                if len(max_temp) > 0:
                    temp_text += '\n最高気温は' + max_temp["celsius"] + "度です。"

            forcast_array.append(forcast["dateLabel"] + ' ' + telop + temp_text)
        if len(forcast_array) > 0:
            response_string += '\n\n'.join(forcast_array)
        response_string += '\n\n' + description

    except Exception as e:
        response_string = 'すいません。天気検索でエラーを起こしてしまいました。改善出来るように頑張ります。:cold_sweat:\n' + e.message + '\n' + str(e)
    return response_string
