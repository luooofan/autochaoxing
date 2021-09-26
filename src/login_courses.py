# coding=utf-8
##
# brief    执行单一账号的刷课前准备工作
# details  通过账号信息登录、获取课程信息并输出、用户选择课程信息 并 实例化SC类执行刷课

from requests import  Session, utils
from json import loads
from re import sub, findall
from selenium.webdriver.support import expected_conditions as EC
from sys import argv,exit
from os import popen as os_popen
from singlecourse import SingleCourse as SC
from publicfunc import Color
from queryans import QueryAns
from playmedia import PlayMedia
from signal import signal, SIGINT, SIGTERM
from startdriver import StartDriver

COLOR = Color()


class Login_courses(object):
    # 登录基类,账户信息,刷课选项
    def __init__(self, phone, passwd, pattern=0):
        self.account = phone
        self.password = passwd
        self.pattern = pattern

class Login_courses_by_request(Login_courses):

    #driver=None

    def __init__(self, phone, passwd, pattern=0):
        super().__init__(phone, passwd, pattern)
        self.mysession = Session()

    # 登录成功后返回该账号对应的课程信息
    def _login_by_phone(self):
        #headers = {
        #    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        #    'Referer': 'https://passport2.chaoxing.com/wlogin',
        #    'Host': 'passport2.chaoxing.com',
        #    'Connection': 'keep-alive',
        #    'Accept': 'application/json, text/javascript, */*; q=0.01',
        #    'Origin': 'https://passport2.chaoxing.com'
        #}
        print(COLOR.DISPLAY, 'check your phonenum:', self.account, COLOR.END)
        print(COLOR.DISPLAY, 'check your password:', self.password, COLOR.END)
        url = "https://passport2.chaoxing.com/mylogin"
        data = {
            'msg': self.account,
            'vercode': self.password
        }
        res = self.mysession.post(url, data=data).text  # str
        # print(res)
        try:
            msg = loads(res)
        except:
            print(' login failed,', COLOR.END, 'please check your login_info')
            exit(1)
        if(msg['status'] == 'false'):
            print(COLOR.ERR, msg['mes'], end="")
            print(' login failed,', COLOR.END, 'please check your login_info')
            exit(1)
        else:
            return self._getcourses()

    def _getcourses(self):
        # print(msg)
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
                   # 'X-Forwarded-For': ip,
                   'Host': 'mooc1-2.chaoxing.com',
                   'Connection': 'keep-alive',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'Referer': 'https://i.mooc.chaoxing.com',
                   }
        self.mysession.get(url="https://i.mooc.chaoxing.com/space/index").text
        courses = self.mysession.get(url='https://mooc1-2.chaoxing.com/visit/courses', headers=headers).text
        # print(courses)
        # 正则处理
        courses = sub(r'[ \t\n]', '', courses)
        # info = findall(r'<ahref=[\'\"](/mycourse.+?)[\'\"]target="_blank"title="(.+?)">(.+?)</p>', courses)
        info = findall(
            r'<ahref=[\'\"](/visit.+?)[\'\"]target="_blank"title="(.+?)">(.+?)</p>', courses)
        del_lt = []
        for i in range(len(info)):
            info[i] = list(info[i])
            info[i][1] = sub(r'&nbsp;', '', info[i][1])
            if "结课模式" in info[i][2]:  # 去掉有结课模式的课程
                del_lt.append(i)
            info[i][0] = info[i][0][0:info[i][0].find('\'')]  # 获取课程主页url
            del info[i][2]
        for i in range(len(del_lt)):  # 去掉有结课模式的课程
            del info[del_lt[i]-i]
        # print("info:"+str(info))
        return info

    @staticmethod  # 传入课程列表 输出课程 进行选课（1门） 选择0直接exit退出 选择范围外课程会陷入循环
    def _choose_course(courses_lt):
        # 选择课程，返回课程相对应的url和课程名称
        num = len(courses_lt)
        for i in range(num):
            print(COLOR.DISPLAY + '\t', i+1, '、', courses_lt[i][1] + COLOR.END)
        while 1:
            try:
                course_id = int(input('please select which course by order(0 is exit):'))
                if course_id > 0 and course_id <= len(courses_lt):
                    return courses_lt[course_id-1]
                elif course_id == 0:
                    return 0
                else:
                    print(COLOR.ERR, ' invalid course order, please reinput!', COLOR.END)
            except:
                print(COLOR.ERR, ' invalid course order, please reinput!', COLOR.END)

    def work(self):
        courses_lt = self._login_by_phone()
        cookies = utils.dict_from_cookiejar(self.mysession.cookies)
        # utils.dict_from_cookiejar(cookies)把cookiejar对象转换为字典对象

        global chrome_pid
        with StartDriver() as chrome_driver:
            driver = chrome_driver.driver
            chrome_pid = chrome_driver.chrome_pid
            base_url = 'https://mooc1-1.chaoxing.com'
            driver.get(base_url)
            driver.delete_all_cookies()
            for k, v in cookies.items():
                driver.add_cookie({'name': k, 'value': v})
                # print(str(k),str(v))
            # print(driver.get_cookies())
            # driver.get(base_url+goal_url)
            if self.pattern == 1:
                print(COLOR.OK+' LOGIN_FINISHED'+COLOR.END)
                for url, name in courses_lt:
                    print(COLOR.NOTE+' Course:'+name+COLOR.END)
                    singlecourse = SC(driver, base_url+url, name, 0)
                    singlecourse.work()
            else:
                while(1):
                    goal = self._choose_course(courses_lt)
                    if goal==0:
                        exit(0)
                    print(COLOR.OK+' LOGIN_FINISHED'+COLOR.END)
                    singlecourse = SC(driver, base_url+goal[0], goal[1], self.pattern)
                    singlecourse.work()

chrome_pid=0

def check_exit(signalnum,frame):
    global chrome_pid
    #if SYSTEM==0 and chrome_pid!=0:
    #    if signalnum==CTRL_CLOSE_EVENT:
    #        os_popen('taskkill /F /T /PID '+str(chrome_pid))
    chrome_pid=0
    raise KeyboardInterrupt

if __name__ == "__main__":

    signal(SIGINT,check_exit)
    signal(SIGTERM,check_exit)
    # print(argv)
    phone = argv[1]
    passwd = argv[2]
    pattern = {
        'single': 0,
        'fullauto': 1,
        'control': 2,
        'debug': 3
    }
    pattern = pattern[argv[3]]
    rate = eval(argv[4])
    noans_num = eval(argv[5])
        
    QueryAns.noans_num=noans_num
    PlayMedia.rate=rate

    try:
        process = Login_courses_by_request(phone, passwd, pattern)
        process.work()
    finally:
        if chrome_pid!=0:
            os_popen('taskkill /F /T /PID '+str(chrome_pid))