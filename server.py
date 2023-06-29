import socket
import threading
import queue
import json
import time
import os
import os.path
import requests
import sys

IP = ''
PORT = 50007
apikey = 'ee19328107fa41e987a42a064a68d0da'
url = 'http://openapi.tuling123.com/openapi/api/v2'
que = queue.Queue()
users = []
lock = threading.Lock()


def call_robot(url, apikey, msg):
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": msg
            },

            "inputImage": {
                "url": "https://cn.bing.com/images/"
            },

            "inputMedia": {
                "url": "https://www.1ting.com/"
            },

            "selfInfo": {
                "location": {
                    "city": "佛山",
                    "province": "广东省",
                    "street": "ABCDEF"
                }
            },
        },
        "userInfo": {
            "apiKey": "ee19328107fa41e987a42a064a68d0da",
            "userId": "Brandon"
        }
    }
    headers = {'content-type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(data))
    return r.json()


#####################################################################################


def onlines():
    online = []
    for i in range(len(users)):
        online.append(users[i][1])
    return online


class ChatServer(threading.Thread):
    global users, que, lock

    def __init__(self, port):
        threading.Thread.__init__(self)

        self.ADDR = ('', port)

        os.chdir(sys.path[0])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def tcp_connect(self, conn, addr):

        user = conn.recv(1024)
        user = user.decode()

        for i in range(len(users)):
            if user == users[i][1]:
                print('User already exist')
                user = '' + user + '_2'

        if user == 'no':
            user = addr[0] + ':' + str(addr[1])
        users.append((conn, user, addr))
        print(' New connection:', addr, ':', user, end='')
        d = onlines()
        self.recv(d, addr)
        try:
            while True:
                data = conn.recv(1024)
                data = data.decode()
                self.recv(data, addr)
            conn.close()
        except:
            print(user + ' Connection lose')
            self.delUsers(conn, addr)
            conn.close()

    def delUsers(self, conn, addr):
        a = 0
        for i in users:
            if i[0] == conn:
                users.pop(a)
                print(' Remaining online users: ', end='')
                d = onlines()
                self.recv(d, addr)
                print(d)
                break
            a += 1

    def recv(self, data, addr):
        lock.acquire()
        try:
            que.put((addr, data))
        finally:
            lock.release()

    def sendData(self):
        while True:
            if not que.empty():
                data = ''
                reply_text = ''
                message = que.get()
                if isinstance(message[1], str):
                    for i in range(len(users)):

                        for j in range(len(users)):
                            if message[0] == users[j][2]:
                                print(' this: message is from user[{}]'.format(j))
                                if '@Robot' in message[1] and reply_text == '':

                                    msg = message[1].split(':;')[0]
                                    reply = call_robot(url, apikey, msg)
                                    reply_text = reply['results'][0]['values']['text']
                                    data = ' ' + users[j][1] + '：' + message[1] + ':;' + 'Robot：' + '@' + \
                                           users[j][1] + ',' + reply_text
                                    break
                                elif '@Robot' in message[1] and (not reply_text == ''):
                                    data = ' ' + users[j][1] + '：' + message[1] + ':;' + 'Robot：' + '@' + \
                                           users[j][1] + ',' + reply_text
                                else:
                                    data = ' ' + users[j][1] + '：' + message[1]
                                    break
                        users[i][0].send(data.encode())

                if isinstance(message[1], list):

                    data = json.dumps(message[1])
                    for i in range(len(users)):
                        try:
                            users[i][0].send(data.encode())
                        except:
                            pass

    def run(self):

        self.s.bind(self.ADDR)
        self.s.listen(5)
        print('Chat server starts running...')
        q = threading.Thread(target=self.sendData)
        q.start()
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()


################################################################


class FileServer(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)

        self.ADDR = ('', port)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.first = r'.\resources'
        os.chdir(self.first)

    def tcp_connect(self, conn, addr):
        print(' Connected by: ', addr)

        while True:
            data = conn.recv(1024)
            data = data.decode()
            if data == 'quit':
                print('Disconnected from {0}'.format(addr))
                break
            order = data.split(' ')[0]
            self.recv_func(order, data, conn)

        conn.close()

    def sendList(self, conn):
        listdir = os.listdir(os.getcwd())
        listdir = json.dumps(listdir)
        conn.sendall(listdir.encode())

    def sendFile(self, message, conn):
        name = message.split()[1]
        fileName = r'./' + name
        with open(fileName, 'rb') as f:
            while True:
                a = f.read(1024)
                if not a:
                    break
                conn.send(a)
        time.sleep(0.1)
        conn.send('EOF'.encode())

    def recvFile(self, message, conn):
        name = message.split()[1]
        fileName = r'./' + name
        with open(fileName, 'wb') as f:
            while True:
                data = conn.recv(1024)
                if data == 'EOF'.encode():
                    break
                f.write(data)

    def cd(self, message, conn):
        message = message.split()[1]

        if message != 'same':
            f = r'./' + message
            os.chdir(f)

        path = os.getcwd().split('\\')
        for i in range(len(path)):
            if path[i] == 'resources':
                break
        pat = ''
        for j in range(i, len(path)):
            pat = pat + path[j] + ' '
        pat = '\\'.join(pat.split())

        if 'resources' not in path:
            f = r'./resources'
            os.chdir(f)
            pat = 'resources'
        conn.send(pat.encode())

    def recv_func(self, order, message, conn):
        if order == 'get':
            return self.sendFile(message, conn)
        elif order == 'put':
            return self.recvFile(message, conn)
        elif order == 'dir':
            return self.sendList(conn)
        elif order == 'cd':
            return self.cd(message, conn)

    def run(self):
        print('File server starts running...')
        self.s.bind(self.ADDR)
        self.s.listen(3)
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()


#############################################################################


class PictureServer(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)

        self.ADDR = ('', port)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        os.chdir(sys.path[0])
        self.folder = '.\\Server_image_cache\\'

    def tcp_connect(self, conn, addr):
        while True:
            data = conn.recv(1024)
            data = data.decode()
            print('Received message from {0}: {1}'.format(addr, data))
            if data == 'quit':
                break
            order = data.split()[0]
            self.recv_func(order, data, conn)
        conn.close()
        print('---')

    def sendFile(self, message, conn):
        print(message)
        name = message.split()[1]
        fileName = self.folder + name
        f = open(fileName, 'rb')
        while True:
            a = f.read(1024)
            if not a:
                break
            conn.send(a)
        time.sleep(0.1)
        conn.send('EOF'.encode())
        print('Image sent!')

    def recvFile(self, message, conn):
        print(message)
        name = message.split(' ')[1]
        fileName = self.folder + name
        print(fileName)
        print('Start saving!')
        f = open(fileName, 'wb+')
        while True:
            data = conn.recv(1024)
            if data == 'EOF'.encode():
                print('Saving completed!')
                break
            f.write(data)

    def recv_func(self, order, message, conn):
        if order == 'get':
            return self.sendFile(message, conn)
        elif order == 'put':
            return self.recvFile(message, conn)

    def run(self):
        self.s.bind(self.ADDR)
        self.s.listen(5)
        print('Picture server starts running...')
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()


####################################################################################


if __name__ == '__main__':
    cserver = ChatServer(PORT)
    fserver = FileServer(PORT + 1)
    pserver = PictureServer(PORT + 2)
    cserver.start()
    fserver.start()
    pserver.start()
    while True:
        time.sleep(1)
        if not cserver.isAlive():
            print("Chat connection lost...")
            sys.exit(0)
        if not fserver.isAlive():
            print("File connection lost...")
            sys.exit(0)
        if not pserver.isAlive():
            print("Picture connection lost...")
            sys.exit(0)
