#!/bin/python3
import time
import subprocess
import pexpect
import sys

host = 'yatl.cf'
user = 'waifu'
port =  1234
key_source =  './key'
tg_log =  './tg.log'
last_tg_source ='./last_tg_msg'
keypass = '12921'

def read_last_sent_from_tg():
    f = open( last_tg_source, 'r' )
    lst = f.read()
    f.close()
    return lst

def update_last_sent_from_tg():
    f = subprocess.check_output( ['tail', '-1', tg_log] )
    g = open( last_tg_source, 'w' )
    g.write( f.decode("utf-8") )
    g.close() 


def main():
    child = pexpect.spawn('ssh {0}@{1} -p {2} -v -i {3}'.format( user, host, port, key_source ), encoding = 'utf-8')
    child.logfile = sys.stdout
    child.expect('passphrase')
    child.sendline('{0}'.format(keypass))
    last = read_last_sent_from_tg()
    while 1:
        time.sleep(1)
        update_last_sent_from_tg()
        very_last = read_last_sent_from_tg()
        if last == very_last:
            continue
        last = very_last
        child.send( "{0}\n\r".format(last) )

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
