from subprocess import Popen
from time import sleep
from colorama import Fore
from colorama import init as colorinit

colorinit()

print(Fore.BLUE+'Welcome To Multi-Autocx!'+Fore.RESET)
lt_phone=open(r'./logindata_phone.txt','r',encoding='utf-8').readlines()
for i in range(len(lt_phone)//2):
    logindata = ""
    try:
        for j in range(i*2, (i+1)*2):
            logindata += (lt_phone[j].strip('\n'))+','
    except IndexError:
        print(' Sorry,no info')
        break
    #print(logindata)
    logindata=logindata[0:-1]
    Popen('start cmd /k python login_getcourses.py '+logindata, shell=True)
    sleep(2)

lt = open(r'./logindata.txt', 'r', encoding='utf-8').readlines()
for i in range(len(lt)//3):
    logindata=""
    try:
        for j in range(i*3,(i+1)*3):
            logindata+=(lt[j].strip('\n'))+','
    except IndexError:
        print(' Sorry,no info')
        break
    #print(logindata)
    Popen('start cmd /k python login_getcourses.py '+logindata[0:-1],shell=True)
    input(Fore.GREEN+' please press any key to continue'+Fore.RESET)

print(Fore.BLUE+'Now you can exit this program! Good luck!'+Fore.RESET)
