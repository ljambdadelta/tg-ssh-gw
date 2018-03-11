#!/bin/python3

import requests
import time

class Telegram:
    def __init__(self, TOKEN):
        self.TOKEN = TOKEN
        self.api_url = "https://api.telegram.org/bot{}/".format(TOKEN)

    def get_updates(self, offset=None, timeout=3000):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        answer = requests.get(self.api_url + method, params)
        answer2json = answer.json()['result']
        return answer2json 
        
    def send_text(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        answer = requests.post(self.api_url + method, params)
        return answer    

    def get_last_update(self):
        get_answer = self.get_updates()
        if len(get_answer) > 0:
            last_update = get_answer[-1]
        else:
            try:
                last_update = get_answer[len(get_answer)]
            except:
                print(last_update)
                print(time.clock)
        return last_update

TOKEN = ""
telegram = Telegram(TOKEN)

def parse_type_of_message(msg_buffer):
    print(msg_buffer) 
    try:
        # Types:
        if 'text' in msg_buffer['message']:
            msg = msg_buffer['message']['text']
        elif 'sticker' in msg_buffer['message']:      
            msg = msg_buffer['message']['sticker']['emoji']
        elif 'document' in msg_buffer['message']:
            msg = 'document'
        elif 'audio' in msg_buffer['message']:
            msg = 'audiofile: {0} -- {1}'.format(msg_buffer['message']['audio']['performer'], msg_buffer['message']['audio']['title'])
        elif 'photo' in msg_buffer['message']:
            msg = 'photo'
        elif 'voice' in msg_buffer['message']:
            msg = 'voice mail'
        else:
            msg = 'unknown file'
    except KeyError:
            msg = 'unknown error' 
    # special messages 
    if 'forward_from_chat' in msg_buffer['message']:
            msg = '<forward from channel: {0}>: {1}'.format(msg_buffer['message']['forward_from_chat']['title'] , msg)
    if 'forward_from' in msg_buffer['message']:
            msg = '< forward from: {0} >: {1}'.format(msg_buffer['message']['forward_from']['username'] , msg)
    if 'reply_to_message' in msg_buffer['message']:
            msg = '< answer for @{0} > {1}'.format(msg_buffer['message']['reply_to_message']['from']['username'], msg)
    return msg

def main():
    parsed+msg_id = None
    log = open("./tg.log", "a")
    while True:
        log.write('\n')
        log.flush()
        #  1: offset, id of message to be parced; 2: get this msg 
        telegram.get_updates(parsed+msg_id)
        msg_buffer = telegram.get_last_update()
        # parcing
        msg_upd_id = msg_buffer['update_id']
        # prepared for nxt itteration
        parsed+msg_id = msg_upd_id + 1
        # edited text has own type
        if 'edited_message' in msg_buffer:
            emsg_chat_id = msg_buffer['edited_message']['chat']['id']
            emsg_name = msg_buffer['edited_message']['from']['username']
            emsg_text = msg_buffer['edited_message']['text']
            r = '@{0} changed his message to "{1}" '.format(emsg_name,emsg_text)
            telegram.send_text(emsg_chat_id, r)
            log.write(r)
            log.write(time.ctime(time.time()))
            continue

        msg_text = parse_type_of_message(msg_buffer)
        msg_chat_id = msg_buffer['message']['chat']['id']
        msg_name = msg_buffer['message']['from']['username']

        response = '@{0} sent: {1} '.format(msg_name, msg_text)
        telegram.send_text(msg_chat_id, response)
        log.write(response)
        log.write(time.ctime(time.time()))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
