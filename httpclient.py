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

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        #Version, code, message 
        code = data.splitlines()[0].split(' ')[1]
        return int(code) 

    def get_headers(self,data):
        headers = data.split('\r\n\r\n')[0]
        return headers 

    def get_body(self, data):
        content = data.splitlines()
        index_of_new_line = 0 
        for element in content:
            index_of_new_line += 1
            if not element:
                break
        # content will be everything comming after the new line 
        return ''.join(content[index_of_new_line:])


    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def request_builder(self, method, path, headers):
        payload = '{} {} HTTP/1.1\r\n'.format(method, path)

        for key, value in headers.items():
            payload += '{}: {}\r\n'.format(key, value)

        payload += '\r\n'

        
        return payload

    def GET(self, url, args=None):
        port, host, path = self.url_split(url)
        headers = {
            'Host': '{}'.format(host),
            'User-Agent': 'curl/7.54.0',
            'Accept': '*/*'
        }

        request = self.request_builder('GET', path, headers)
        self.connect(host, port)
        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()
        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
    def url_split(self, url):
        # URL looks like this: <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
        #https://github.com/python/cpython/blob/3.8/Lib/http/client.py#L1115     
        parsed_url = urlparse(url)
        path = parsed_url.path
        host = parsed_url.hostname
        port = parsed_url.port

        if not path:
            path = '/'
        return port, host, path

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
