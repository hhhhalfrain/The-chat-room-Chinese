import socket
import threading
import json
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText
import requests

IP = ''
PORT = ''
user = ''
listbox1 = ''
ii = 0
users = []
chat = '-------开始群聊---------'

root1 = tkinter.Tk()
root1.title('登录窗口')
root1['height'] = 110
root1['width'] = 270
root1.resizable(0, 0)

IP1 = tkinter.StringVar()
IP1.set('127.0.0.1:50007')
User = tkinter.StringVar()
User.set('')

labelIP = tkinter.Label(root1, text='服务器地址：')
labelIP.place(x=20, y=10, width=100, height=20)

entryIP = tkinter.Entry(root1, width=80, textvariable=IP1)
entryIP.place(x=120, y=10, width=130, height=20)

labelUser = tkinter.Label(root1, text='用户名：')
labelUser.place(x=30, y=40, width=80, height=20)

entryUser = tkinter.Entry(root1, width=80, textvariable=User)
entryUser.place(x=120, y=40, width=130, height=20)


def login(*args):
    global IP, PORT, user
    IP, PORT = entryIP.get().split(':')
    PORT = int(PORT)
    user = entryUser.get()
    if not user:
        tkinter.messagebox.showerror('啊哦', message='请告诉我你是谁')
    else:
        root1.destroy()


root1.bind('<Return>', login)
but = tkinter.Button(root1, text='上线', command=login)
but.place(x=100, y=70, width=70, height=30)

root1.mainloop()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
if user:
    s.send(user.encode())
else:
    s.send('匿名用户'.encode())

addr = s.getsockname()
addr = addr[0] + ':' + str(addr[1])
if user == '':
    user = addr

root = tkinter.Tk()
root.title(user)
root['height'] = 400
root['width'] = 580
root.resizable(0, 0)

listbox = ScrolledText(root)
listbox.place(x=5, y=0, width=570, height=320)

listbox.tag_config('red', foreground='red')
listbox.tag_config('blue', foreground='blue')
listbox.tag_config('green', foreground='green')
listbox.tag_config('pink', foreground='pink')
listbox.insert(tkinter.END, '您已上线', 'blue')

b1 = ''
b2 = ''
b3 = ''
b4 = ''

p1 = tkinter.PhotoImage(file='./emoji/facepalm.png')
p2 = tkinter.PhotoImage(file='./emoji/smirk.png')
p3 = tkinter.PhotoImage(file='./emoji/concerned.png')
p4 = tkinter.PhotoImage(file='./emoji/smart.png')

dic = {'aa**': p1, 'bb**': p2, 'cc**': p3, 'dd**': p4}
ee = 0


def mark(exp):
    global ee
    mes = exp + ':;' + user + ':;' + chat
    s.send(mes.encode())
    b1.destroy()
    b2.destroy()
    b3.destroy()
    b4.destroy()
    ee = 0


def bb1():
    mark('aa**')


def bb2():
    mark('bb**')


def bb3():
    mark('cc**')


def bb4():
    mark('dd**')


def express():
    global b1, b2, b3, b4, ee
    if ee == 0:
        ee = 1
        b1 = tkinter.Button(root, command=bb1, image=p1,
                            relief=tkinter.FLAT, bd=0)
        b2 = tkinter.Button(root, command=bb2, image=p2,
                            relief=tkinter.FLAT, bd=0)
        b3 = tkinter.Button(root, command=bb3, image=p3,
                            relief=tkinter.FLAT, bd=0)
        b4 = tkinter.Button(root, command=bb4, image=p4,
                            relief=tkinter.FLAT, bd=0)

        b1.place(x=5, y=248)
        b2.place(x=75, y=248)
        b3.place(x=145, y=248)
        b4.place(x=215, y=248)
    else:
        ee = 0
        b1.destroy()
        b2.destroy()
        b3.destroy()
        b4.destroy()


eBut = tkinter.Button(root, text='表情', command=express)
eBut.place(x=5, y=320, width=60, height=30)

listbox1 = tkinter.Listbox(root)
listbox1.place(x=445, y=0, width=130, height=320)


def users():
    global listbox1, ii
    if ii == 1:
        listbox1.place(x=445, y=0, width=130, height=320)
        ii = 0
    else:
        listbox1.place_forget()
        ii = 1


button1 = tkinter.Button(root, text='在线用户列表', command=users)
button1.place(x=485, y=320, width=90, height=30)

a = tkinter.StringVar()
a.set('')
entry = tkinter.Entry(root, width=120, textvariable=a)
entry.place(x=5, y=350, width=570, height=40)


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


def send(*args):
    users.append(chat)
    users.append('机器人')
    print(chat)
    if chat not in users:
        tkinter.messagebox.showerror('Send error', message='There is nobody to talk to!')
        return
    if chat == '机器人':
        print('机器人')
    if chat == user:
        tkinter.messagebox.showerror('Send error', message='Cannot talk with yourself in private!')
        return
    mes = entry.get() + ':;' + user + ':;' + chat
    s.send(mes.encode())
    a.set('')


button = tkinter.Button(root, text='发送', command=send)
button.place(x=515, y=353, width=60, height=30)
root.bind('<Return>', send)


def private(*args):
    global chat

    indexs = listbox1.curselection()
    index = indexs[0]
    if index > 0:
        chat = listbox1.get(index)

        if chat == '-------开始群聊---------':
            root.title(user)
            return
        ti = user + '  -->  ' + chat
        root.title(ti)


listbox1.bind('<ButtonRelease-1>', private)


def recv():
    global users
    while True:
        data = s.recv(1024)
        data = data.decode()

        try:
            data = json.loads(data)
            users = data
            listbox1.delete(0, tkinter.END)
            number = ('在线用户个数：' + str(len(data) + 1))
            listbox1.insert(tkinter.END, number)
            listbox1.itemconfig(tkinter.END, fg='green', bg="#f0f0ff")
            listbox1.insert(tkinter.END, '-------开始群聊---------')
            listbox1.insert(tkinter.END, '机器人')
            listbox1.itemconfig(tkinter.END, fg='green')
            for i in range(len(data)):
                listbox1.insert(tkinter.END, (data[i]))
                listbox1.itemconfig(tkinter.END, fg='green')
        except:
            data = data.split(':;')
            data1 = data[0].strip()
            data2 = data[1]
            data3 = data[2]
            if 'INVITE' in data1:
                if data3 == '机器人':
                    tkinter.messagebox.showerror('Connect error', message='Unable to make video chat with 机器人!')
                elif data3 == '-------开始群聊---------':
                    tkinter.messagebox.showerror('Connect error', message='Group video chat is not supported!')
                continue
            markk = data1.split('：')[1]

            pic = markk.split('#')

            if (markk in dic) or pic[0] == '``':
                data4 = '\n' + data2 + '：'
                if data3 == '-------开始群聊---------':
                    if data2 == user:
                        listbox.insert(tkinter.END, data4, 'blue')
                    else:
                        listbox.insert(tkinter.END, data4, 'green')
                elif data2 == user or data3 == user:
                    listbox.insert(tkinter.END, data4, 'red')
                if pic[0] == '``':
                    pass
                else:
                    listbox.image_create(tkinter.END, image=dic[markk])
            else:
                data1 = '\n' + data1
                if data3 == '-------开始群聊---------':
                    if data2 == user:
                        listbox.insert(tkinter.END, data1, 'blue')
                    else:
                        listbox.insert(tkinter.END, data1, 'green')
                    if len(data) == 4:
                        listbox.insert(tkinter.END, '\n' + data[3], 'pink')
                elif data3 == '机器人' and data2 == user:
                    print('Here:机器人')
                    apikey = 'ee19328107fa41e987a42a064a68d0da'
                    url = 'http://openapi.tuling123.com/openapi/api/v2'
                    print('msg = ', data1)
                    listbox.insert(tkinter.END, data1, 'blue')
                    reply = call_robot(url, apikey, data1.split('：')[1])
                    reply_txt = '\n机器人:' + reply['results'][0]['values']['text']
                    listbox.insert(tkinter.END, reply_txt, 'pink')
                elif data2 == user or data3 == user:
                    listbox.insert(tkinter.END, data1, 'red')
            listbox.see(tkinter.END)


r = threading.Thread(target=recv)
r.start()
#
root.mainloop()
s.close()
