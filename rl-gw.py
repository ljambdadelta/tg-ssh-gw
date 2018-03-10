#!/bin/python3

import requests
import time

class tg:

#---Initialisation
    def __init__( self,
                  token ):
    
        self.token   = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
#---Request to tg server
    def get_updates( self,
                     offset  = None, 
                     timeout = 3000  ):

        method      = 'getUpdates'
        params      = { 'timeout': timeout ,
                        'offset' : offset  }
        answer      = requests.get( self.api_url + method, params )
        answer2json = answer.json()[ 'result' ]
        
        return answer2json 
        
#---
    def send_text( self,
                   chat_id,
                   text ):
    
        params = { 'chat_id' : chat_id ,
                   'text'    : text    }
        method = 'sendMessage'
        answer = requests.post( self.api_url + method, params )
        
        return answer    
#---
    def get_last_update( self ):
        get_answer = self.get_updates()
        if len( get_answer ) > 0:
            last_update = get_answer[ -1 ]
        else:
            try:
                last_update = get_answer[ len( get_answer ) ]
            except:
                print( last_update )
                print( time.clock )

        return last_update

#---
#---
#--- HARDCODED !!!
token = ""
telegram = tg( token )
#- parce the nature of send data
def parseTypeOfMessage( msgBuffer ):
    print ( msgBuffer ) 
    try:
#- Types:
        if 'text'      in msgBuffer[ 'message' ] :
            msg =           msgBuffer[ 'message' ][ 'text' ]
        elif 'sticker' in msgBuffer[ 'message' ] :      
            msg =           msgBuffer[ 'message' ]['sticker'][ 'emoji' ]
        elif 'document'   in msgBuffer[ 'message' ] :
            msg =           'document'
        elif 'audio'   in msgBuffer[ 'message' ] :
            msg = 'audiofile: {0} -- {1}'.format(  msgBuffer[ 'message' ][ 'audio' ][ 'performer' ], msgBuffer[ 'message' ][ 'audio' ][ 'title' ] )
        elif 'photo'   in msgBuffer[ 'message' ] :
            msg =           'photo'
        elif 'voice'   in msgBuffer[ 'message' ] :
            msg =           'voice mail'
        else :
            msg = 'unknown file'
    except KeyError:
            msg = 'unknown error' 
#- special messages 
    if 'forward_from_chat' in msgBuffer[ 'message' ] :
            msg = '<forward from channel: {0}>: {1}'.format( msgBuffer[ 'message' ][ 'forward_from_chat' ][ 'title' ] , msg )
    if 'forward_from' in msgBuffer[ 'message' ] :
            msg = '< forward from: {0} >: {1}'.format( msgBuffer[ 'message' ][ 'forward_from' ][ 'username' ] , msg )
    if 'reply_to_message' in msgBuffer[ 'message' ] :
            msg = '< answer for @{0} > {1}'.format( msgBuffer[ 'message' ][ 'reply_to_message' ][ 'from' ][ 'username' ], msg )
    return msg

def main():
     parcedMsgId = None
     log = open("./tg.log", "a")
     while True:
         log.write( '\n' )
         log.flush()
#-  1: offset, id of message to be parced; 2: get this msg 
         telegram.get_updates( parcedMsgId )
         msgBuffer  = telegram.get_last_update()
#- parcing
         msg_upd_id     = msgBuffer[ 'update_id' ]
#- prepared for nxt itteration
         parcedMsgId = msg_upd_id + 1
#- edited text has own type
         if 'edited_message' in msgBuffer :
           emsg_chat_id = msgBuffer[ 'edited_message'][ 'chat' ][ 'id']
           emsg_name    = msgBuffer[ 'edited_message' ][ 'from' ][ 'username' ]
           emsg_text    = msgBuffer[ 'edited_message' ][ 'text' ]
           r = '@{0} changed his message to "{1}" '.format( emsg_name,emsg_text)
           telegram.send_text( emsg_chat_id, r )
           log.write( r )
           log.write( time.ctime( time.time() ) )
           continue
#-
         msg_text       = parseTypeOfMessage( msgBuffer )
         msg_chat_id    = msgBuffer[ 'message' ][ 'chat' ][ 'id' ]
         msg_name       = msgBuffer[ 'message' ][ 'from' ][ 'username' ]
#-
         response   = '@{0} sent: {1} '.format( msg_name, msg_text )
         telegram.send_text( msg_chat_id, response )
         log.write( response )
         log.write( time.ctime( time.time() ) )
#---
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

