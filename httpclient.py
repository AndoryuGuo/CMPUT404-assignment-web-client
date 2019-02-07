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
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def urlParser(self,url):
        print(url)
        result = urlparse(url)
        hostName = result.hostname
        port = result.port if result.port else 80
        path = result.path if result.path else '/'

        print(hostName, port, path)
        return (hostName, port, path)

    def urlencoder(self, args):
        if args:
            queryStr = urlencode(args)
        else:
            queryStr = ''
        
        print(queryStr)
        return queryStr

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = re.search(r'^\S+\s(\d+)', data)[1]
        return int(code)

    def get_headers(self,data):
        return None

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body
    
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

    def set_request_header(self, method, length=0, body=''):
        if method == "GET":
            header_addition = ''
        else:
            header_addition = "Content-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n".format(length)

        header = "{0} {1} HTTP/1.1\r\nHost: {2}\r\n{3}Connection: close\r\n\r\n{4}".format(method, self.path, self.hostname, header_addition, body)
        return header

    def GET(self, url, args=None):
        try:
            self.hostname, self.port, self.path = self.urlParser(url)
            self.connect(self.hostname, self.port)
            req_data = self.set_request_header("GET")
            self.sendall(req_data)
            res_data = self.recvall(self.socket)
            code = self.get_code(res_data)
            body = self.get_body(res_data)
            self.close()
        except Exception as e:
            return HTTPResponse(404, e)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        try:
            self.hostname, self.port, self.path = self.urlParser(url)
            self.connect(self.hostname, self.port)
            queryStr = self.urlencoder(args)
            req_data = self.set_request_header("POST", length=len(queryStr), body=queryStr)
            self.sendall(req_data)
            res_data = self.recvall(self.socket)
            code = self.get_code(res_data)
            body = self.get_body(res_data)
            self.close()
        except Exception as e:
            return HTTPResponse(404, e)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)
    
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
