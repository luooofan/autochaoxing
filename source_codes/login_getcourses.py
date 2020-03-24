import autochaoxing as autocx
from requests import post, Session, get
from urllib.parse import quote
from json import loads
from PIL import Image
import base64
from re import sub, findall
from requests import utils
from selenium import webdriver
from time import sleep
from sys import argv
# utils.dict_from_cookiejar(cookies)把cookiejar对象转换为字典对象


def getlogindata():
    return open(r'./logindata.txt', 'r', encoding='utf-8').readlines()


def getschool(name):
    data = {
        "filter": quote(name),
        "pid": -1,
        "allowjoin": 0
    }
    # searchUnis?filter='+quote(name)).text  # type:str
    text = post(url='http://passport2.chaoxing.com/org/searchforms?filter='+quote(name)+'&allowjoin=0&pid=-1').text
    #print(text)
    dic = loads(text)  # 把字符串转化为字典
    try:
        return dic['froms'][0]['id'], dic['froms'][0]['name']  # 取第一个匹配的信息作为登录选项
    except:
        print(COLOR.ERR, ' get school_id failed', COLOR.END)
        exit(1)


def getcourses(mysession):
    # print(msg)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
               # 'X-Forwarded-For': ip,
               'Host': 'mooc1-2.chaoxing.com',
               'Connection': 'keep-alive',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Referer': 'http://i.mooc.chaoxing.com',
               }
    mysession.get(url="http://i.mooc.chaoxing.com/space/index").text
    courses = mysession.get(url='http://mooc1-2.chaoxing.com/visit/courses', headers=headers).text
    # print(courses)
    # 正则处理
    courses = sub(r'[ \t\n]', '', courses)
    info = findall(r'<ahref=[\'\"](/mycourse.+?)[\'\"]target="_blank"title="(.+?)">', courses)
    for i in range(len(info)):
        info[i] = list(info[i])
        info[i][0] = info[i][0][0:info[i][0].find('\'')]
    return info, utils.dict_from_cookiejar(mysession.cookies)


def login(school, username, password):
    # 返回值第一个：二重列表，内列表中第一项是课程url，第二项是课程名称
    # 返回值第二个：cookies字典
    mysession = Session()
    school_fid, school_name = getschool(school)  # 得到学校标号
    print(COLOR.DISPLAY, 'check your school name:', school_name, COLOR.END)
    print(COLOR.DISPLAY, 'check your username:', username, COLOR.END)
    print(COLOR.DISPLAY, 'check your password:', password, COLOR.END)
    url = 'https://passport2.chaoxing.com/num/code'
    while(1):
        login_vercode = mysession.get(url, timeout=60)  # get验证码
        # 验证码获取成功
        if login_vercode.status_code == 200:
            # 写图像，显示图像，读入验证码
            open(r'testvercode.png', 'wb').write(login_vercode.content)
            img = Image.open('testvercode.png')
            img.show()
            ver_code = int(input(" please input the vercode:"))
            psw = base64.b64encode(password.encode('utf-8'))
            data = {
                'fid': school_fid,
                'numcode': ver_code,
                'password': psw,
                'uname': username,
                't': 'true'
            }
            w = mysession.post(url='https://passport2.chaoxing.com/unitlogin', data=data).text
            msg = loads(w)
            if (msg['type'] == 1):  # 验证码错误 用户名或密码错误
                print(COLOR.ERR, msg['mes'], end="")
                print(' login failed,', COLOR.END, 'please check your login_info and retry')
                continue
            else:
                return getcourses(mysession)
        # 验证码获取失败
        else:
            continue


def login_by_phone(phonenum, password):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Referer': 'https://passport2.chaoxing.com/wlogin',
        'Host': 'passport2.chaoxing.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'https://passport2.chaoxing.com'
    }
    print(COLOR.DISPLAY, 'check your phonenum:', phonenum, COLOR.END)
    print(COLOR.DISPLAY, 'check your password:', password, COLOR.END)
    mysession = Session()
    url = "https://passport2.chaoxing.com/mylogin"
    data = {
        'msg': phonenum,
        'vercode': password
    }
    res = mysession.post(url, data=data).text  # str
    # print(res)
    msg = loads(res)
    if(msg['status'] == 'false'):
        print(COLOR.ERR, msg['mes'], end="")
        print(' login failed,', COLOR.END, 'please check your login_info')
        exit(1)
    else:
        return getcourses(mysession)


def choose_course(courses_lt):
    # 选择课程，返回课程相对应的url和课程名称
    num = len(courses_lt)
    for i in range(num):
        print(COLOR.DISPLAY + '\t', i+1, '、', courses_lt[i][1] + COLOR.END)
    while 1:
        course_id = int(input('please select which course by order(0 is exit):'))
        if course_id > 0 and course_id <= len(courses_lt):
            return courses_lt[course_id-1]
        elif course_id == 0:
            sleep(2)
            exit(0)
        else:
            print(COLOR.ERR, ' invalid course order, please reinput!', COLOR.END)


def call_autocx(driver, goal_url, course_name):
    autocx.perform_model0(driver, goal_url, course_name)


def perform(logindata):
    if(len(logindata) == 2):
        courses_lt, cookies = login_by_phone(logindata[0].strip(' \t\n'), logindata[1].strip(' \t\n'))
    else:
        courses_lt, cookies = login(logindata[0].strip(
            ' \t\n'), logindata[1].strip(' \t\n'), logindata[2].strip(' \t\n'))
    driver = autocx.init()  # 配置chrome启动参数并启动
    base_url = 'https://mooc1-1.chaoxing.com'
    driver.get(base_url)
    driver.delete_all_cookies()
    for k, v in cookies.items():
        driver.add_cookie({'name': k, 'value': v})
        # print(str(k),str(v))
    # print(driver.get_cookies())
    # driver.get(base_url+goal_url)
    while(1):
        goal = choose_course(courses_lt)  # 获得目标课程主页的url
        call_autocx(driver, base_url+goal[0], goal[1])
        autocx.log_fp.flush()
    autocx.log_fp.close()


COLOR = autocx.color()
if __name__ == "__main__":
    if len(argv) == 1:
        logindata = getlogindata()
    else:
        logindata = (argv[1]).split(',')
        # print(logindata)
    perform(logindata)
