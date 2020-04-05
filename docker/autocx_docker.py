# coding=utf-8
##
# brief   选择模式启动刷课
# details 先后读取logindata_phone.txt(2行一个账号)和logindata.txt(3行一个账号)的全部账号信息
#         Linux(docker)环境下：通过Popen启动多个后台子进程，通过管道实现与子进程通信，从而有序输出
#         PS:无界面linux环境下的代码文件 和win32相比：只有autocx.py不一样
# author  Luoofan
# date    2020-03-27 20:38:15
# FilePath\docker\autocx_docker.py
#
from subprocess import Popen, PIPE, STDOUT
import fcntl
from time import sleep
from colorama import Fore
from colorama import init as colorinit
from sys import argv
from os import O_NONBLOCK
from getopt import gnu_getopt
from requests import post
from platform import platform, architecture, system
from publicfunc import Color, getlogindata, getlogindata_phone, send_err
from login_courses import Login_courses_by_request, Login_courses_by_chrome  # ,Login_courses
COLOR = Color()


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
                    print(sp_out,end=" ")
                    if 'LOGIN_FINISHED' in sp_out:
                        q_flag = 1
                        break
                    if 'input' in sp_out or 'select' in sp_out:
                        break
                sleep(0.5)
            if q_flag == 1:
                break
            sp_in = bytes(input()+'\n',encoding="utf-8")
            self.process.stdin.write(sp_in)
            self.process.stdin.flush()


def perform(mode, rate):
    #处理账号信息
    print(COLOR.DISPLAY+'Welcome To Multi-Autocx!'+COLOR.END)

    # 读取 手机号+密码 弹出多个弹窗
    lt_phone = getlogindata_phone()
    for i in range(len(lt_phone)//2):
        logindata = ""
        try:
            for j in range(i*2, (i+1)*2):
                logindata += (lt_phone[j].strip(' \n'))+','
        except IndexError:
            print(' Sorry,no info')
            break
        # print(logindata)
        # args_lt = 'python3 ./login_courses.py '+logindata[0:-1]+' '+str(mode)+' '+str(rate)+' &'
        args_lt=['python3','login_courses.py',logindata[0:-1],str(mode),str(rate),'&']
        sub_ps = StartAutoCX(args_lt)
        sub_ps.work()
        sleep(2)

    # 读取 机构账号 需要输入验证码 每次处理一个 按任意键后处理下一个
    lt = getlogindata()
    for i in range(len(lt)//3):
        logindata = ""
        try:
            for j in range(i*3, (i+1)*3):
                logindata += (lt[j].strip(' \n'))+','
        except IndexError:
            print(' Sorry,no info')
            break
        # print(logindata)
        args_lt=['python3','login_courses.py',logindata[0:-1],str(mode),str(rate),'&']
        sub_ps = StartAutoCX(args_lt)
        sub_ps.work()
        sleep(2)
        #input(COLOR.OK+' please press any key to continue'+COLOR.END)

    print(COLOR.DISPLAY+'Now you can exit this program! Good luck!'+COLOR.END)


def main():
    #参数处理
    try:
        opts, args = gnu_getopt(argv[1:], '-m:-r:-v-h', ['mode=', 'rate=', 'version', 'help'])
    except:
        print(COLOR.ERR+'Invalid args, Try -h or --help for more information'+COLOR.END)
        exit()
    #print(opts)
    #print(args)
    rate = 1
    mode = "single"
    opt_mode = ['single', 'fullauto', 'control']
    for opt_name, opt_value in opts:
        if opt_name in ('-h', '--help'):
            print('''
-m(--mode) single     单课程自动模式: 选择课程,自动完成该课程(默认启动参数)
           fullauto   全自动模式:     自动遍历全部课程,无需输入(除了机构登录方式下需要输入验证码)
           control    单课程控制模式: 选择课程并选择控制章节,自动完成[该课程第一个未完成章节,选定章节)范围内章节
-r(--rate) [0.625,16] 全局倍速设置:   在选定模式的全局范围内开启该倍速
-h(--help)     usage
-v(--version)  version
            ''')
            exit()
        if opt_name in ('-v', '--version'):
            print('2.0docker')
            exit()
        if opt_name in ('-r', '--rate'):
            rate = eval(opt_value)
            if rate > 16 or rate < 0.625:
                print(COLOR.ERR+'Invalid rate range, Try -h or --help for more information'+COLOR.END)
                exit()
        if opt_name in ('-m', '--mode'):
            mode = opt_value
            if mode not in opt_mode:
                print(COLOR.ERR+'Invalid args, Try -h or --help for more information'+COLOR.END)
                exit()
    #调用 执行 mode & rate
    print(COLOR.DISPLAY+'Set the mode: %s and the rate: %.2f' % (mode, rate)+COLOR.END)
    perform(opt_mode.index(mode), rate)


if __name__ == '__main__':
    main()
