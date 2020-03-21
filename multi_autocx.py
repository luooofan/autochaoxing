from subprocess import Popen

print('\033[1;34m'+'Welcome To Multi-Autocx!'+'\033[0m')
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
    Popen('start cmd /k python login_getcourses.py '+logindata,shell=True)
    input('\033[1;32m'+' please press any key to continue'+'\033[0m')
print('\033[1;34m'+'Now you can exit this program! Good luck!'+'\033[0m')
