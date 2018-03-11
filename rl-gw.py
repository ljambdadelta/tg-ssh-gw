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
            msg = '< forward from: @{0} >: {1}'.format(msg_buffer['message']['forward_from']['username'] , msg)
    if 'reply_to_message' in msg_buffer['message']:
            msg = '< answer for @{0} > {1}'.format(msg_buffer['message']['reply_to_message']['from']['username'], msg)
    return msg

def send_message(message_type, msg_buffer):
    log = open("./tg.log", "a")
    msg_chat_id =  msg_buffer[message_type]['chat']['id'] 
    msg_name = msg_buffer[message_type]['from']['username']
    msg_text = parse_type_of_message(msg_buffer) if message_type == 'message' else msg_buffer[message_type]['text']
    link_sentence = ' sent: ' if message_type == 'message' else ' changed his mmessage to '
    timestamp = time.ctime(time.time())
    output = '@{0}{1}"{2}" at {3}\n'.format(msg_name, link_sentence, msg_text, timestamp)
    telegram.send_text( msg_chat_id, output )
    log.write( output )
    log.flush()


def main():
    parsed_msg_id = None
    while True:
        telegram.get_updates(parsed_msg_id)
        msg_buffer = telegram.get_last_update()
        msg_upd_id = msg_buffer['update_id']
        parsed_msg_id = msg_upd_id + 1

        message_type = 'message' if 'message' in msg_buffer else 'edited_message'
        send_message(message_type, msg_buffer)
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
