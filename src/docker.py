from subprocess import Popen, PIPE, STDOUT
from time import sleep
from os import O_NONBLOCK
import fcntl
class StartAutoCX(object):
    def __init__(self, args_lt):
        # 子进程 来完成操作
        # 不能加 shell=True，不能加/bin/bash or sh or dash -c
        self.process = Popen(args_lt, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        # 获取 子进程标准输出管道 的File Flag
        flags = fcntl.fcntl(self.process.stdout, fcntl.F_GETFL)
        # 为 子进程标准输出管道 添加 非阻塞 Flag
        flags |= O_NONBLOCK
        fcntl.fcntl(self.process.stdout, fcntl.F_SETFL, flags)

    def work(self):
        # 非阻塞地读取 子进程的输出 判断是否该输入
        q_flag = 0
        while 1:
            while 1:
                sp_out = self.process.stdout.read()
                if sp_out != None:
                    sp_out = (str(sp_out, encoding="utf-8"))
                    print(sp_out, end=" ")
                    if 'LOGIN_FINISHED' in sp_out:
                        q_flag = 1
                        break
                    if 'input' in sp_out or 'select' in sp_out:
                        break
                sleep(0.5)
            if q_flag == 1:
                break
            sp_in = bytes(input()+'\n', encoding="utf-8")
            self.process.stdin.write(sp_in)
            self.process.stdin.flush()
