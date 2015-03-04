#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socket
import string
from time import strftime

def pong(line):
    splitted = line.split()
    if(splitted[0] == "PING"):
        pong = "PONG " + splitted[1] + "\r\n"
        print(pong)
        filesocket.write(pong.encode())
        filesocket.flush()
        return True
    return False

def sayHi(line):
    splitted = line.split()
    if(len(splitted) == 4):
        if(splitted[1] == "PRIVMSG" and splitted[3] == ":!hi"):
            replyTo = splitted[0].split("!")[0][1:]
            replyChan = splitted[2]
            msg = "PRIVMSG " + replyChan + " :Hi " + replyTo + "!\r\n"
            filesocket.write(msg.encode())
            filesocket.flush()
def decodeData(line):
    try:
        line = line.decode('utf-8')
    except UnicodeDecodeError:
        line = line.decode('latin1')
    return line


print("Initialize KawayBOT - Alpha Version")

nickname = ""
if(len(sys.argv) >= 2):
    nickname = sys.argv[1]
if nickname == "":
    nickname = "Poulpinou"

s = socket.socket();
host = "euroserv.fr.quakenet.org"
#host = "barjavel.freenode.net"
port = 6667
readbuffer = ""
authed = False
joined = False
nick = str("NICK " + nickname + "\r\n").encode()
user = b"USER KawayBOT KawayBOT KawayBOT :KawayBOT\r\n"
join = b"JOIN #ladose,#ladose2\r\n"

s.connect((host,port))

s.send(nick)
s.send(user)
filesocket = s.makefile("rwb")
filesocket.flush()

connected = False
for line in filesocket:
    line = decodeData(line)
    print(strftime("%H:%M:%S") + " > "  + line)
    sys.stdout.flush()
    pinged = pong(line)
    sayHi(line)
    if not pinged and line.find("001") != -1 and not connected:
            s.send(join)
            connected = True


#while 1:
#    for line in filesocket:
#        line = line.decode()
#        print(line)
#        pong(line)


        #if line.find("PING") != -1:
        #    pong = "PONG " + line.split()[1] + "\r\n"
        #    s.send(pong.encode())
        #    print(pong)
        #    authed = True

