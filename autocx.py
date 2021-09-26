# coding=utf-8
 
from subprocess import Popen
from time import sleep
from sys import path as sys_path
import argparse

from setting import ACCOUNTS, MODE, RATE, NUM

sys_path.append('./src/')
from publicfunc import Color
COLOR=Color()


def main():
    #处理账号信息
    print(COLOR.DISPLAY+'Welcome To Multi-Autocx!'+COLOR.END)

    for account in ACCOUNTS:
        Popen('start cmd /k python ./src/login_courses.py '+str(account['phone'])+' '+str(account['passwd'])+' '+str(MODE)+' '+str(RATE)+' '+str(NUM), shell=True)
        sleep(2)

    print(COLOR.DISPLAY+'Now will exit this program! Good luck!'+COLOR.END)
    sleep(1.5)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Multi-Autocx", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-m","--mode", type=str,default="single", choices=['single', 'fullauto', 'control','debug'], help=
    '''single     单课程自动模式: 选择课程,自动完成该课程
fullauto   全自动模式:     自动遍历全部课程,无需输入
control    单课程控制模式: 选择课程并选择控制章节,自动完成[该课程第一个未完成章节,选定章节)范围内章节''')
    parser.add_argument("-r","--rate",type=float,default=1.0,help="视频倍速")
    parser.add_argument("-n", "--num", type=int, default=5,help="自动答题时,如果未找到答案的题目数量达到num,则暂时保存答案,不提交")

    args = parser.parse_args()

    if args.rate>16 or args.rate<0.625:
        print(COLOR.ERR+'Invalid rate range, Try -h or --help for more information'+COLOR.END)

    # 当脚本参数与setting.py中的配置不一致时 以执行时指定的参数为准
    MODE = args.mode if args.mode != MODE else MODE
    RATE = args.rate if args.rate != RATE else RATE
    NUM = args.num if args.num != NUM else NUM

    print(COLOR.DISPLAY+'Set mode: %s\trate: %.2f\tnoans_num:%d'%(MODE,RATE,NUM)+COLOR.END) 

    main()