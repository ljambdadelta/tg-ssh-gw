#!/bin/python3

import requests
import time
import subprocess
import pexpect
import sys
import threading

TOKEN = ""

host = 'yatl.cf'
user = 'waifu'
port =  1234
key_source =  './key'
tg_log =  './tg.log'
last_tg_source ='./last_tg_msg'
last_ssh_source = './last_ssh_msg'
keypass = '12921'

class Ssh(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.kost =1
        self.daemon = True
        self.child = pexpect.spawn('ssh {0}@{1} -p {2} -i {3}'.format( user, host, port, key_source ), encoding = 'utf-8')
        #self.child.logfile = sys.stdout
        self.child.expect('passphrase')
        self.child.sendline('{0}'.format(keypass))
        self.last = self.read_last_sent_from_tg()
    def run(self):
        while True:
            time.sleep(0.1)
            self.update_last_sent_from_ssh(self.child)
            self.update_last_sent_from_tg()
            very_last = self.read_last_sent_from_tg()
            if self.last != very_last:
                self.last = very_last
                self.child.send( "{0}\n\r".format(self.last) )
    def read_last_sent_from_tg(self):
        f = open(last_tg_source, 'r')
        lst = f.read()
        f.close()
        return lst

    def update_last_sent_from_tg(self):
        f = subprocess.check_output(['tail', '-1', tg_log])
        g = open(last_tg_source, 'w')
        g.write(f.decode("utf-8"))
        g.close() 
    def update_last_sent_from_ssh(self, child):
        line ='s'
        try:
            line = child.read_nonblocking(10000,2)
            trimsize = line.rfind('\r\r\n')
            i#sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g"
#.format(user))
            print(line.encode().decode())
            line = line[0:trimsize]
            
            print('msg:{0}'.format(line))
            if line[0:len(user)] == user:
               # print(line)
                print("self")
                #raise Exception
            if len(line) > 0:
                if line[1] == '*':
                    if line.find('join') != -1:
                        #raise Exception
                        print('joined')
            fil = open(last_ssh_source, 'r')
            previous_last_message = fil.read()
            fil.close()
            if line == previous_last_message:
                print(line)
                print("equal")
                raise Exception
            fil = open(last_ssh_source, 'w')
            fil.write(line)
            fil.close()
        except pexpect.exceptions.TIMEOUT:
            print("timeout")
            a=1
        except:
            print('ex')
class Telegram(threading.Thread):
    def __init__(self, TOKEN, chatid):
        threading.Thread.__init__(self)
        self.chatid = chatid
        self.daemon = True
        self.parsed_msg_id = None
        self.msg_buffer = ''
        self.TOKEN = TOKEN
        self.api_url = "https://api.telegram.org/bot{}/".format(TOKEN)
        self.last_ssh_msg = ''
    def run(self):
        while True:
            self.next_message()
            self.send_message()
    def send_msg_from_ssh(self):
        source = open(last_ssh_source, 'r')
        last_in_file = source.read()
        source.close()
        if last_in_file != self.last_ssh_msg:
            self.last_ssh_msg = last_in_file
            print(self.send_text(self.chatid, self.last_ssh_msg))
        
            

    def get_updates(self, offset=None, timeout=3000):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        answer = requests.get(self.api_url + method, params)
        answer2json = answer.json()['result']
        return answer2json 
        
    def send_text(self, chat_id, text):
        text = text
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        print('text:')
        print(chat_id)
        print(text)
        answer = requests.post(self.api_url + method, params)
        return answer    

    def get_last_update(self):
        get_answer = self.get_updates()
        last_update = ''
        if len(get_answer) > 0:
            last_update = get_answer[-1]
        else:
            try:
                last_update = get_answer[len(get_answer)]
            except:
                print(last_update)
                print(time.clock)
        return last_update

    def next_message(self):
        self.get_updates(self.parsed_msg_id)
        self.msg_buffer = self.get_last_update()
        self.msg_upd_id = self.msg_buffer['update_id']
        self.parsed_msg_id = self.msg_upd_id + 1

    def parse_type_of_message(self):
        print(self.msg_buffer) 
        try:
        # Types:
            if 'text' in self.msg_buffer['message']:
                msg = self.msg_buffer['message']['text']
            elif 'sticker' in self.msg_buffer['message']:      
                msg = self.msg_buffer['message']['sticker']['emoji']
            elif 'document' in self.msg_buffer['message']:
                msg = 'document'
            elif 'audio' in self.msg_buffer['message']:
                msg = 'audiofile: {0} -- {1}'.format(self.msg_buffer['message']['audio']['performer'], self.msg_buffer['message']['audio']['title'])
            elif 'photo' in self.msg_buffer['message']:
                msg = 'photo'
            elif 'voice' in self.msg_buffer['message']:
                msg = 'voice mail'
            else:
                msg = 'unknown file'
        except KeyError:
            msg = 'unknown error' 
    # special messages 
        if 'forward_from_chat' in self.msg_buffer['message']:
                msg = '<forward from channel: {0}>: {1}'.format(self.msg_buffer['message']['forward_from_chat']['title'] , msg)
        if 'forward_from' in self.msg_buffer['message']:
                msg = '< forward from: @{0} >: {1}'.format(self.msg_buffer['message']['forward_from']['username'] , msg)
        if 'reply_to_message' in self.msg_buffer['message']:
                msg = '< answer for @{0} > {1}'.format(self.msg_buffer['message']['reply_to_message']['from']['username'], msg)
        return msg

    def send_message(self):
        message_type = 'message' if 'message' in self.msg_buffer else 'edited_messag    e'
        log = open("./tg.log", "a")
        msg_chat_id =  self.msg_buffer[message_type]['chat']['id'] 
        msg_name = self.msg_buffer[message_type]['from']['username']
        msg_text = self.parse_type_of_message() if message_type == 'message' else self.msg_buffer[message_type]['text']
        link_sentence = ' sent: ' if message_type == 'message' else ' changed his message to '
        timestamp = time.ctime(time.time())
        output = '@{0}{1}"{2}" at {3}\n'.format(msg_name, link_sentence, msg_text, timestamp)
        self.send_text( msg_chat_id, output )
        log.write( output )
        log.flush()
        log.close()


def main():
    telegram = Telegram(TOKEN,-314023830)
    index=0
    telegram.start()
    ssh = Ssh()   
    ssh.start() 
    while True:
        time.sleep(5)
        sender = Telegram(TOKEN,-314023830)
        sender.send_msg_from_ssh()
        if telegram.isAlive() != True:
            telegram.join()
            telegram = Telegram(TOKEN,-314023830)
            telegram.start()
        if ssh.isAlive() != True:
            ssh.join()    
            ssh = Ssh()
            ssh.start()
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
