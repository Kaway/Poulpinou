#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import socket
import sys
from time import strftime

from constants import *

host = "euroserv.fr.quakenet.org"
port = 6667
connected = False
names_request = {'asked': False}
nickname = ''


def say_hi(requester, chan):
    reply_to = requester.split("!")[0]
    msg = 'Hi ' + reply_to + "!"
    send_message_in_chat(chan, msg)


def send_message_in_chat(chan, message):
    msg_to_send = PRIVMSG + ' ' + chan + ' :' + message
    send_message_to_server(msg_to_send)


def decode_data(msg):
    try:
        msg = msg.decode('utf-8')
    except UnicodeDecodeError:
        msg = msg.decode('latin1')
    return msg


def send_names_command(chan):
    msg = SRV_CMD_NAMES + ' ' + chan
    send_message_to_server(msg)


def parse_notice_auth_or_ping(auth_or_ping):
    ping_or_auth_split = auth_or_ping.split()
    if ping_or_auth_split[0] == PING:
        reply_to_ping(ping_or_auth_split[1])


def reply_to_ping(ping_argument):
    pong_msg = str.join(" ", (PONG, ping_argument))
    send_message_to_server(pong_msg)


def parse_priv_msg(sender, subject):
    raw_message, reply_chan = parse_subject(subject)
    message = normalize_message(raw_message)

    striped_msg = message.strip()
    if striped_msg.lower() == '!hi':
        say_hi(sender, reply_chan)
    elif striped_msg[0:6] == '!names':
        global names_request
        names_request = {'asked': True, 'chan': reply_chan}
        send_names_command(reply_chan)


def parse_subject(subject):
    reply_chan, raw_message = subject.strip().split(' ', 1)
    return raw_message, reply_chan


def normalize_message(message):
    return message[1:]


def normalize_user_nickname(nickname):
    irc_user_statuses = ['%', '+', '@']
    if nickname[0] in irc_user_statuses:
        return nickname[1:]
    return nickname


def parse_names_msg(subject):
    global names_request

    raw_message, reply_chan = parse_subject(subject)
    names_in_chan = raw_message.split(':')[1].split(' ')

    normalized_nicknames = list(map(normalize_user_nickname, names_in_chan))

    mass_hl = "Hey " + ', '.join(normalized_nicknames)
    send_message_in_chat(names_request['chan'], mass_hl)
    names_request = {}


def process_message(sender, command, subject):
    if command == PRIVMSG:
        parse_priv_msg(sender, subject)
    elif command == RESPONSE_RPL_NAM_REPLY and names_request['asked']:
        parse_names_msg(subject)


def parse_message(message):
    global connected
    sender, command, subject = message.split(' ', 2)

    if command == RESPONSE_RPL_WELCOME:
        for chan in chans:
            join_command = SRV_CMD_JOIN + ' ' + chan
            send_message_to_server(join_command)
    elif command not in MESSAGES_TO_IGNORE:
        process_message(sender, command, subject)


def parse_server_message(raw_message):
    message = decode_data(raw_message)
    print_server_message(message)
    if message[0] != ':':
        parse_notice_auth_or_ping(message)
    else:
        parse_message(message[1:])


def send_message_to_server(msg):
    final_msg = format_msg_for_server(msg)
    file_socket.write(final_msg)
    file_socket.flush()


def format_msg_for_server(msg):
    return (msg + "\r\n").encode()


def print_server_message(msg):
    print(strftime("%H:%M:%S") + " > " + msg)


def arg_to_chan(chan_arg):
    return '#' + chan_arg


def main():
    print("Initialize Kaway BOT - Alpha Version")

    parser = argparse.ArgumentParser(description='Useless bot')
    parser.add_argument('nickname', type=str, nargs='?', default=['Poulpinou'])
    parser.add_argument('channel_args', type=str, nargs='*', default=['ladose2'])

    args = parser.parse_args()

    global chans, nickname, file_socket
    chans = list(map(arg_to_chan, args.channel_args))
    nickname = args.nickname[0]

    file_socket = socket.socket()
    file_socket.connect((host, port))
    file_socket = file_socket.makefile("rwb")

    nick_cmd = SRV_CMD_NICK + ' ' + nickname
    send_message_to_server(nick_cmd)
    usr_cmd = SRV_CMD_USER + ' KawayBOt KawayBot KawayBot :KawayBot'
    send_message_to_server(usr_cmd)

    for raw_line in file_socket:
        parse_server_message(raw_line)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
