#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

from ast import arguments
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

DEFAULT_PORT = 80
BUFFER_SIZE = 1024

def help():
    print("httpclient.py [GET/POST] [URL]\n")

def split_url(url):
    match = re.match(r'https?:\/\/([\w\.]+)(?::(\d+))?(\/.+)?', url)
    host = match.group(1)
    port = int(match.group(2) or DEFAULT_PORT)
    path = (match.group(3) or '/').split('?')[0]
    return host, port, path

def get_arguments(url):
    match = re.search(r'\?(.+)', url)
    return match.group(1) if match else ''

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        match = re.match(r'HTTP\/\d\.\d (\d+)', data)
        return int(match.group(1))

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(BUFFER_SIZE)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        get_request = "GET %s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n%s"
        if args:
            arguments = urllib.parse.urlencode(args)
        else:
            arguments = ''
        host, port, path = split_url(url)
        self.connect(host, port)
        self.sendall(get_request % (path, host, len(arguments), arguments))
        data = str(self.recvall(self.socket))
        code = self.get_code(data)
        body = self.get_body(data)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        post_request = "POST %s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n%s"
        host, port, path = split_url(url)
        arguments = get_arguments(url)
        if args:
            if len(arguments) > 0:
                arguments += '&'
            arguments += urllib.parse.urlencode(args)
        self.connect(host, port)
        self.sendall(post_request % (path, host, len(arguments), arguments))
        data = str(self.recvall(self.socket))
        code = self.get_code(data)
        body = self.get_body(data)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
