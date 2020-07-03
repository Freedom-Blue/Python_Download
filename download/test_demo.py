# -*- coding: utf-8 -*-
# @Time  : 2020/5/5 22:18
# @Author: 哦嚯嚯哦
# @File  : test_demo.py
# @tool  : PyCharm

"""
使用python实现百行代码高速下载，同IDM
"""

import os
import time
import sys
from requests import get,head
from concurrent.futures import ThreadPoolExecutor,wait


class Dowmloader:
    def __init__(self, url, nums, file):
        self.url = url      # url链接
        self.num = nums     # 线程数
        self.name = file    # 文件名字
        self.getSize = 0    # 大小
        self.info = {
            'main': {
                'progress': 0,
                'speed': ''
            },
            'sub': {
                'progress': [0 for i in range(nums)],    # 子线程状态
                'stat': [1 for i in range(nums)]         # 下载状态
            }
        }
        r = head(self.url)
        # 状态码显示302则迭代寻找文件
        while r.status_code == 302:
            self.url = r.headers['Location']
            print("此url已重定向至{}".format(self.url))
            r = head(self.url)
        self.size = int(r.headers['Content-Length'])
        print('该文件大小为: {} bytes'.format(self.size))

    def down(self, start, end, thread_id, chunk_size = 10240):
        raw_start = start
        for _ in range(10):
            try:
                headers = {'Range': 'bytes={}-{}'.format(start, end)}
                r = get(self.url, headers=headers, timeout=10, stream=True)
                print(f"线程{thread_id}连接成功")
                size = 0
                with open(self.name, "rb+") as fp:
                    fp.seek(start)
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            self.getSize += chunk_size
                            fp.write(chunk)
                            start += chunk_size
                            size += chunk_size
                            progress = round(size / (end - raw_start) * 100, 2)
                            self.info['sub']['progress'][thread_id - 1] = progress
                            self.info['sub']['stat'][thread_id - 1] = 1
                return
            except Exception as error:
                print(error)
                self.down(start, end, thread_id)
        print(f"{start}-{end}, 下载失败")
        self.info['sub']['start'][thread_id - 1] = 0

    def show(self):
        while True:
            speed = self.getSize
            time.sleep(0.5)
            speed = int((self.getSize - speed) * 2 / 1024)
            if speed > 1024:
                speed = f"{round(speed / 1024, 2)} M/s"
            else:
                speed = f"{speed} KB/s"
            progress = round(self.getSize / self.size * 100, 2)
            self.info['main']['progress'] = progress
            self.info['main']['speed'] = speed
            print(self.info)
            if progress >= 100:
                break

    def run(self):
        # 创建一个要下载的文件
        fp = open(self.name, 'wb')
        print(f"正在初始化下载文件: {self.name}")
        fp.truncate(self.size)
        print(f"文件初始化完成")
        start_time = time.time()
        fp.close()
        part = self.size // self.num
        pool = ThreadPoolExecutor(max_workers=self.num + 1)
        futures = []
        for i in range(self.num):
            start = part * i
            if i == self.num - 1:
                end = self.size
            else:
                end = start + part - 1
            futures.append(pool.submit(self.down, start, end, i + 1))
        futures.append(pool.submit(self.show))
        print(f"正在使用{self.num}个线程进行下载...")
        wait(futures)
        end_time = time.time()
        speed = int(self.size / 1024 / (end_time - start_time))
        if speed > 1024:
            speed = f"{round(speed / 1024, 2)} M/s"
        else:
            speed = f"{speed} KB/s"
        print(f"{self.name}下载完成，平均速度: {speed}")

if __name__ == '__main__':
    debug = 1           # 测试情况
    if debug:
        # url = 'http://119.6.237.80:8899/w10.xitongxz.net/202005/DNGS_GHOST_WIN10_X64_V2020_05.iso'        # 传入下载链接
        url = 'http://119.6.237.61:8899/w10.xitongxz.net/202007/DEEP_GHOST_WIN10_X64_V2020_07.iso'
        down = Dowmloader(url, 8, os.path.basename(url))
    else:
        # 命令行执行方式
        url = sys.argv[1]       # 下载链接
        file = sys.argv[2]      # 默认保存在项目路径下,文件的名字以文件格式结尾
        thread_num = int(sys.argv[3])  # 使用的线程数量
        down = Dowmloader(url, thread_num, file)
    down.run()





