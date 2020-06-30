import vk_api
from random import *
import requests
from vk_api.longpoll import VkLongPoll, VkEventType
import os

GROUP_ID = 196583514
IMAGES_PATH = "C:\\Users\\Алексей\\Desktop\\Универ\\2 курс\\Сети\\Bot\\Images"

def write_msg(user_id, message):
    vk.method('messages.send', {'user_id':user_id,'message':message,'random_id':randint(0,2048)})

def write_info(user_id):
    response = vk.method('users.get',{'user_id':user_id, 'fields':'sex,city'})
    user_data = response[0]
    reply = f"Вот что мне удалось о тебе узнать:\nТвое имя {user_data['first_name']}\n" + \
            f"Твоя фамилия {user_data['last_name']}\nТвой город {user_data['city']['title']}\n"
    if user_data['is_closed']:
        reply += "Твоя страница закрыта\n"
    else:
        reply += "Твоя страница открыта\n"
    if user_data['sex'] == 1:
        reply += "Твой пол - женский\n"
    else:
        reply += "Твой пол - мужской\n"
    write_msg(user_id, reply)

def write_info_about_user(sender_id, target_id):
    response = vk.method('users.get',{'user_id':target_id, 'fields':'sex,city'})
    user_data = response[0]
    reply = f"Вот что мне удалось узнать:\nИмя {user_data['first_name']}\n" + \
            f"Фамилия {user_data['last_name']}\nГород {user_data['city']['title']}\n"
    if user_data['is_closed']:
        reply += "Страница закрыта\n"
    else:
        reply += "Страница открыта\n"
    if user_data['sex'] == 1:
        reply += "Пол - женский\n"
    else:
        reply += "Пол - мужской\n"
    write_msg(sender_id, reply)

def write_members(sender_id):
    response = vk.method('groups.getMembers',{'group_id':GROUP_ID,'offset':0,'count':50})
    id_list = response['items']
    reply = "В моей группе состоят эти люди:\n"
    for user_id in id_list:
        reply += f"http://vk.com/id{user_id}\n"
    write_msg(sender_id, reply)

def write_command_list(user_id):
    command_list = "Список комманд:\n"+\
                   "Информация о пользователе (Что ты обо мне знаешь?)\n"+\
                   "Пользователи состоящие в группе (Кто состоит в твоей группе?)\n"+\
                   "Проверка наличия пользователя в группе бота (Этот человек состоит в твоей группе? + id)\n"+\
                   "Отправка рандомной картинки (Скинь картинку)\n"+\
                   "Информация о другом пользователе (Что ты знаешь об этом пользователе?) + id\n"
    write_msg(user_id,command_list)

#Получение id пользователя из ссылки
#Пример входных данных - https://vk.com/id....
def get_id(request):
    user_id = ""
    for symbol in request:
        if symbol.isdigit():
            user_id += symbol
    return int(user_id)

def write_is_member(user_id, target_id):
    if vk.method('groups.isMember',{'group_id':GROUP_ID,'user_id':target_id}):
        write_msg(user_id, "Этот человек состоит в моей группе")
    else:
        write_msg(user_id, "Этот человек не состоит в моей группе")

def send_random_photo(user_id):
    upload = vk.method("photos.getMessagesUploadServer")
    count_images = len(os.listdir(IMAGES_PATH))
    photo = requests.post(upload['upload_url'],files={'photo':open(f'Images\\{randint(1,count_images)}.jpg','rb')}).json()
    response = vk.method("photos.saveMessagesPhoto",{'photo':photo['photo'],'server':photo['server'],'hash':photo['hash']})[0]
    attachment = f"photo{response['owner_id']}_{response['id']}"
    vk.method("messages.send",{'peer_id':user_id,'message':'Скинул картинку','attachment':attachment,'random_id':randint(0,2048)})

#Основной скрипт

#Получение токена для работы с API
with open("token.txt") as token_file:
    token = token_file.read()

#Авторизация
vk = vk_api.VkApi(token=token)

#Получение достпупа к Long Poll серверу
longpoll = VkLongPoll(vk)

#Прослушивание Long Poll сервера на наличие новых событий
#и обработка полученных сообщений
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text
        if request == "привет" or request == "Привет":
            write_msg(event.user_id,"Привет, человек")
        elif request == "пока" or request == "Пока":
            write_msg(event.user_id,"До встречи")
        elif request == "Что ты обо мне знаешь?" or request == "что ты обо мне знаешь?":
            write_info(event.user_id)
        elif request == "кто состоит в твоей группе?" or request == "Кто состоит в твоей группе?":
            write_members(event.user_id)
        elif request.find("Этот человек состоит в твоей группе?") > -1 or request.find("этот человек состоит в твоей группе?") > -1:
            target_id = get_id(request)
            write_is_member(event.user_id, target_id)
        elif request == "скинь картинку" or request == "Скинь картинку":
            send_random_photo(event.user_id)
        elif request.find("Что ты знаешь об этом пользователе?") > -1 or request.find("что ты знаешь об этом пользователе?") > -1:
            target_id = get_id(request)
            write_info_about_user(event.user_id, target_id)
        else:
            write_command_list(event.user_id)

    
