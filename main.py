# Навык для определения предрасположенности к диабету 2-го типа


from flask import Flask, request, jsonify
import logging
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# Текст при запуске навыка
START_TEXT = 'Приветсвую тебя дорогой пользователь! Я - диаботик, я помогу ' \
             'тебе определить, есть ли у тебя предрасположенность ' \
             'к диабету. Желаете начать?'

# Текст при вызове кнопки помощи
HELP_TEXT = 'Я помогу тебе определить, есть ли у тебя предрасположенность ' \
            'к диабету'

# Текст, когда пользователь сказал чепуху в начале
HELLO_FAIL_ANS_TEXT = 'Что-то я не могу понять, что именно ты имеешь ' \
                      'ввиду. Повтори пожалуйста, желаешь начать?'

# Кнопки при старте
START_BUTTONS = [
    {
        'title': 'Помощь',
        'hide': True
    },
    {
        'title': 'Да',
        'hide': True
    },
    {
        'title': 'Нет',
        'hide': True
    }
]

# Всякое служебное
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    """ Основная функция навыка """

    # Логгирование
    logging.info('Request: %r', request.json)
    # Формируем ответ
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    # Запускаем цепочку диалогов
    handle_dialog(response, request.json)
    # Выводим текущее состояние навыка
    logging.info('Response: %r', response)
    return jsonify(response)


def handle_dialog(res, req):
    """ Цепочка диалогов """
    # ID пользователя
    user_id = req['session']['user_id']
    # Если сессия новая
    if req['session']['new']:
        # Размещаем стартовый текст
        res['response']['text'] = START_TEXT
        # Кнопочки
        res['response']['buttons'] = START_BUTTONS

        # Стартанули ли сессию
        sessionStorage[user_id] = {
            'session_started': False
        }
        return

    if sessionStorage[user_id]['session_started'] is False:
        if get_help(req):
            res['response']['text'] = HELP_TEXT
            res['response']['buttons'] = [
                {
                    'title': 'Помощь',
                    'hide': True
                },
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                }
            ]
        # Проверяем согласие
        elif get_approval(req):
            res['end_session'] = True
        # Проверяем отказ
        elif get_rejection(req):
            # Пользователь ушел
            res['response']['text'] = 'До встречи!'
            # Останавливаем сессию
            res['end_session'] = True
        else:
            # Если че-то инородное
            res['response']['text'] = HELLO_FAIL_ANS_TEXT
            res['response']['buttons'] = [
                {
                    'title': 'Помощь',
                    'hide': True
                }
            ]


def get_approval(req):
    """ Проверяем соглашается ли пользователь на какое-то действие """
    return 'да' in req['request']['nlu']['tokens']


def get_rejection(req):
    """ Проверяем, отказался ли пользователь от действия """
    return 'нет' in req['request']['nlu']['tokens']


def get_help(req):
    """ Проверяем, нужна ли пользователю помощь """
    return 'помощь' in req['request']['nlu']['tokens']


if __name__ == '__main__':
    app.run()
