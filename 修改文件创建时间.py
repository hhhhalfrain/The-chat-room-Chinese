
import os
import random
import time
def get_now_random_time():
    # 获取当前时间戳
    now_time = int(time.time())
    # 获取当前时间戳的随机数
    random_time = random.randint(-10*24*3600,0)
    # 返回当前时间戳的随机数
    return now_time+random_time,now_time+random_time

for file_path,j,filenames in os.walk(r"./"):
    # 打印当前目录
    print(file_path)
    os.utime(file_path,get_now_random_time())
    for filename in filenames:
        os.utime(file_path+'/'+filename,get_now_random_time())
