from flask import Flask, request
import requests
import os

###вместо ... вставить свой токен
TOKEN = '...'
TB_API_URL = f'https://api.telegram.org/bot{TOKEN}'

###вместо ... вставить url предоставленный heroku
WEBHOOK_URL = f'.../{TOKEN}'

#создание экземпляра сервера flask
app = Flask(__name__)


def send_message(chat_id, text):
    '''Отправка сообщения в чат'''
    requests.get(f'{TB_API_URL}/sendMessage?chat_id={chat_id}&text={text}')

def get_ip_info(ip):
    '''Получение информации об ip-адресе'''
    r = requests.get(f'http://ipwhois.app/json/{ip}').json()
    if not r['success']:
        return False
    return r
    

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook_response():
'''Правило маршрутизации POST запроса'''
    r = request.get_json()
    chat_id = r['message']['chat']['id']
    ip_info = get_ip_info(r['message']['text'])
    if ip_info:
        send_message(chat_id, 'Местонахождение(Страна): '+ip_info['country'])
        send_message(chat_id, 'Номер AS провайдера: '+ip_info['asn'])
        send_message(chat_id, 'Имя провайдера: '+ip_info['isp'])
    else:
        send_message(chat_id, 'К сожалению не удалось найти информацию об этом IP-адресе.')
    return ''

def webhook_restart(webhook_url):
    '''Перезагрузка вебхука с адресом webhook_url'''
    requests.get(f'{TB_API_URL}/deleteWebhook')
    requests.get(f'{TB_API_URL}/setWebhook?url={webhook_url}')


if __name__ == '__main__':
    webhook_restart(WEBHOOK_URL)
    #host='0.0.0.0' сделает сервер общедоступным, получение порта из переменной окружения PATH(требование heroku)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))