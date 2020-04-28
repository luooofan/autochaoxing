# coding=utf-8
##
# brief   选择模式启动刷课
# details 先后读取logindata_phone.txt(2行一个账号)和logindata.txt(3行一个账号)的全部账号信息
#         windows环境下：对于每一份账号信息启动一个cmd命令行来执行刷课操作
#         Linux(docker)环境下：通过Popen启动多个后台子进程，通过管道实现与子进程通信，从而有序输出
# author  Luoofan
# date    2020-03-27 20:38:15
# 
from subprocess import Popen, PIPE, STDOUT
from time import sleep
from colorama import Fore
from colorama import init as colorinit
from sys import argv,path as sys_path
from getopt import gnu_getopt
from requests import post
from platform import platform,architecture,system
#from os import getcwd

#cur_path=getcwd()
sys_path.append('./src/')#(cur_path+'/src/')
from publicfunc import Color, getlogindata, getlogindata_phone, send_err, SYSTEM
COLOR=Color()

if SYSTEM == 1:  # not windows
    from docker import StartAutoCX
    from os import O_NONBLOCK
    import fcntl

def perform(mode,rate,noans_num):
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
        if SYSTEM==0:
            Popen('start cmd /k python ./src/login_courses.py '+logindata[0:-1]+' '+str(mode)+' '+str(rate)+' '+str(noans_num), shell=True)
        else:
            args_lt = ['python3', './src/login_courses.py', logindata[0:-1], str(mode), str(rate), str(noans_num), '&']
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
        if SYSTEM==0:
            Popen('start cmd /k python ./src/login_courses.py '+logindata[0:-1]+' '+str(mode)+' '+str(rate)+' '+str(noans_num), shell=True)
            input(COLOR.OK+' please press any key to continue'+COLOR.END)
        else:
            args_lt = ['python3', './src/login_courses.py', logindata[0:-1], str(mode), str(rate), str(noans_num), '&']
            sub_ps = StartAutoCX(args_lt)
            sub_ps.work()
            sleep(2)

    print(COLOR.DISPLAY+'Now you can exit this program! Good luck!'+COLOR.END)
    sleep(1.5)

def main():
    #参数处理
    try:
        opts,args=gnu_getopt(argv[1:],'-m:-r:-n:-v-h',['mode=','rate=','num=','version','help'])
    except:
        print(COLOR.ERR+'Invalid args, Try -h or --help for more information'+COLOR.END)
        exit()
    #print(opts)
    #print(args)
    rate=1
    mode="single"
    noans_num=5
    opt_mode = ['single', 'fullauto', 'control']
    for opt_name,opt_value in opts:
        if opt_name in ('-h','--help'):
            print('''
-m(--mode) single     单课程自动模式: 选择课程,自动完成该课程(默认启动参数)
           fullauto   全自动模式:     自动遍历全部课程,无需输入(除了机构登录方式下需要输入验证码)
           control    单课程控制模式: 选择课程并选择控制章节,自动完成[该课程第一个未完成章节,选定章节)范围内章节
-r(--rate) [0.625,16] 全局倍速设置:   在选定模式的全局范围内开启该倍速   默认值:1
-n(--num)  0,1,2,3... 全局答题设置:   自动答题时,如果未找到答案的题目数量达到num,则暂时保存答案,不进行自动提交   默认值:5
-h(--help)     usage
-v(--version)  version
            ''')
            exit()
        if opt_name in ('-v','--version'):
            print('2.0')
            exit()
        if opt_name in ('-r','--rate'):
            rate=eval(opt_value)
            if rate>16 or rate<0.625:
                print(COLOR.ERR+'Invalid rate range, Try -h or --help for more information'+COLOR.END)
                exit()
        if opt_name in ('-m','--mode'):
            mode=opt_value
            if mode not in opt_mode:
                print(COLOR.ERR+'Invalid args, Try -h or --help for more information'+COLOR.END)
                exit()
        if opt_name in ('-n','--num'):
            try:
                noans_num=int(eval(opt_value))
                if noans_num<0:
                    raise Exception
            except:
                print(COLOR.ERR+'Invalid args, Try -h or --help for more information'+COLOR.END)
                exit()
    #调用 执行 mode & rate
    print(COLOR.DISPLAY+'Set mode: %s\trate: %.2f\tnoans_num:%d'%(mode,rate,noans_num)+COLOR.END)
    perform(opt_mode.index(mode),rate,noans_num)
        
if __name__=='__main__':
    main()
