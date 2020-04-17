# coding=utf-8
##
# brief    执行单一账号的刷课前准备工作
# details  通过账号信息登录、获取课程信息并输出、用户选择课程信息 并 实例化SC类执行刷课
#          执行文件时可带参数:fistarg:  [机构名,学号,密码] or [手机号,密码]   type:字符串列表
#                            secondarg:模式   in  [0,1,2]
#                            thirdarg: 倍速   from 0.625 to 16
#                   不带参数:获取logindata.txt或logindata_phone.txt中的第一个账号信息以默认模式和倍速开始刷课
#          docker exchange:如果产生img，img通过调用viu显示在终端上
#                          在调用SC类之前 输出“LOGIN_FINISHED” 实现与父进程的通信
# author   Luoofan
# date     2020-03-27 21:01:12
# FilePath\source_code\login_courses.py
#
from requests import post, Session, get
from urllib.parse import quote
from json import loads
from PIL import Image
import base64
from re import sub, findall
from requests import utils, post
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from traceback import format_exc
from subprocess import Popen
from time import sleep
from sys import argv,exit
from os import system as os_system,path as os_path,mkdir
from singlecourse import SingleCourse as SC
from publicfunc import Color, getlogindata, getlogindata_phone, send_err, SYSTEM
COLOR = Color()

# 启动chrome
# debugarg:拓展启动选项


def startchrome(debugarg=''):
    # 初始化
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('log-level=3')
    chrome_options.add_argument('–incognito')  # 启动无痕/隐私模式
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('blink-settings=imagesEnabled=false') #不加载图片, 提升速度
    chrome_options.add_argument('--disable-gpu')
    if debugarg != '':
        chrome_options.add_argument(debugarg)
    ##  INFO = 0,
    ##  WARNING = 1,
    ##  LOG_ERROR = 2,
    ##  LOG_FATAL = 3
    ##  default is 0
    return webdriver.Chrome(options=chrome_options, executable_path=r"./chromedriver")


class Login_courses(object):
    # 登录基类,账户信息,刷课选项
    def __init__(self, logindata, pattern=0, rate=1):
        self.mode = 1 if len(logindata) == 2 else 2  # 1:phone 2:school
        self.school = logindata[0].strip(' \t\n') if self.mode == 2 else ''
        self.account = logindata[self.mode-1].strip(' \t\n')
        self.password = logindata[self.mode].strip(' \t\n')
        self.pattern = pattern
        self.rate = rate
        if SYSTEM==1:
            if os_path.exists('./AccountInfo')==False:
                mkdir('./AccountInfo')
            self._sc_out_fp=open(r'./AccountInfo/'+self.account+r'.txt','a+',encoding="utf-8")  
        else:
            self._sc_out_fp=None


class Login_courses_by_request(Login_courses):
    def __init__(self, logindata, pattern=0, rate=1):
        super().__init__(logindata, pattern, rate)
        self.mysession = Session()

    def _getschool(self):
        #data = {
        #    "filter": quote(self.school),
        #    "pid": -1,
        #    "allowjoin": 0
        #}
        # searchUnis?filter='+quote(name)).text  # type:str
        text = post(url='http://passport2.chaoxing.com/org/searchforms?filter=' +
                    quote(self.school)+'&allowjoin=0&pid=-1').text
        try:
            dic = loads(text)  # 把字符串转化为字典
            return dic['froms'][0]['id'], dic['froms'][0]['name']  # 取第一个匹配的信息作为登录选项
        except:
            print(COLOR.ERR, ' get school_id failed', COLOR.END)
            exit(1)

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
                   'Referer': 'http://i.mooc.chaoxing.com',
                   }
        self.mysession.get(url="http://i.mooc.chaoxing.com/space/index").text
        courses = self.mysession.get(url='http://mooc1-2.chaoxing.com/visit/courses', headers=headers).text
        # print(courses)
        # 正则处理
        courses = sub(r'[ \t\n]', '', courses)
        info = findall(r'<ahref=[\'\"](/mycourse.+?)[\'\"]target="_blank"title="(.+?)">(.+?)</p>', courses)
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
                    sleep(2)
                    exit(0)
                else:
                    print(COLOR.ERR, ' invalid course order, please reinput!', COLOR.END)
            except SystemExit:
                exit(0)
            except:
                print(COLOR.ERR, ' invalid course order, please reinput!', COLOR.END)

    def _login(self):
        # 返回值第一个：二重列表，内列表中第一项是课程url，第二项是课程名称
        # 返回值第二个：cookies字典
        school_fid, school_name = self._getschool()  # 得到学校标号
        print(COLOR.DISPLAY, 'check your school name:', school_name, COLOR.END)
        print(COLOR.DISPLAY, 'check your username:', self.account, COLOR.END)
        print(COLOR.DISPLAY, 'check your password:', self.password, COLOR.END)
        url = 'https://passport2.chaoxing.com/num/code'
        while(1):
            login_vercode = self.mysession.get(url, timeout=60)  # get验证码
            # 验证码获取成功
            if login_vercode.status_code == 200:
                # 写图像，显示图像，读入验证码
                open(r'login_vercode.png', 'wb').write(login_vercode.content)

                if SYSTEM == 0:  # Win
                    img = Image.open('login_vercode.png')
                    img.show()
                else:
                    p=Popen(['./viu', 'login_vercode.png'])
                    p.communicate()
                    sleep(1.5)

                while 1:
                    try:
                        ver_code =input(" please input the vercode:")
                        break
                    except:
                        pass

                psw = base64.b64encode(self.password.encode('utf-8'))
                data = {
                    'fid': school_fid,
                    'numcode': ver_code,
                    'password': psw,
                    'uname': self.account,
                    't': 'true'
                }
                # print(data)
                w = self.mysession.post(url='https://passport2.chaoxing.com/unitlogin', data=data).text
                try:
                    msg = loads(w)
                    # print(w)
                    if (msg['type'] == 0):
                        return self._getcourses()
                    elif (msg['type'] == 1):  # 验证码错误 用户名或密码错误
                        print(COLOR.ERR, msg['mes'], end=",")
                        print(' login failed,', COLOR.END, 'please check your login_info and retry')
                        continue
                    else:  # 采用备用方案登录
                        work_bak = Login_courses_by_chrome([self.school, self.account, self.password], self.pattern, self.rate)
                        work_bak.work()  # 会重新输入验证码

                except:
                    work_bak = Login_courses_by_chrome(
                        [self.school, self.account, self.password], self.pattern, self.rate)
                    work_bak.work()  # 会重新输入验证码
            # 验证码获取失败
            else:
                continue

    def work(self):
        if self.mode == 1:
            courses_lt = self._login_by_phone()
        else:
            courses_lt = self._login()
        cookies = utils.dict_from_cookiejar(self.mysession.cookies)
        # utils.dict_from_cookiejar(cookies)把cookiejar对象转换为字典对象
        driver = startchrome()
        # '--remote-debugging-port=9222') # 配置chrome启动参数并启动
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
                singlecourse = SC(driver, base_url+url, name, 0, self.rate,self._sc_out_fp)
                singlecourse.work()
        else:
            while(1):
                goal = self._choose_course(courses_lt)
                print(COLOR.OK+' LOGIN_FINISHED'+COLOR.END)
                singlecourse = SC(driver, base_url+goal[0], goal[1], self.pattern, self.rate, self._sc_out_fp)
                singlecourse.work()
        if self._sc_out_fp !=None:
            self._sc_out_fp.flush()
            self._sc_out_fp.close()


class Login_courses_by_chrome(Login_courses):
    # 传入logindata列表参数：账号信息
    # pattern和rate可选参数
    # 调用实例化对象的work方法：login->choose_course->select_model->call SC开始单课程的刷课
    # 只能 以机构方式登录 ，在内部手动确定

    def __init__(self, logindata ,pattern=0, rate=1):
        super().__init__(logindata, pattern, rate)
        self.driver = None
        self.__wait = None

    def work(self):
        self.driver = startchrome()
        self.__wait = WebDriverWait(self.driver, 20)
        print(COLOR.DISPLAY, 'Lauching…', COLOR.END)
        self._login()
        # print(self.driver.current_url)
        courses_lt = self._choose_course()
        self._call_SC(courses_lt)
        self.driver.quit()
        if self._sc_out_fp !=None:
            self._sc_out_fp.flush()
            self._sc_out_fp.close()

    def _login(self):
        action_chains = ActionChains(self.driver)
        logindata = getlogindata()
        #log_fp.write('\n' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '\n')
        #log_fp.write('登录信息:' + logindata[0].strip(' \t\n') + logindata[1].strip(' \t\n') + '\n')

        # 访问登陆界面并选择机构
        url = "https://passport2.chaoxing.com/login?refer=http://i.mooc.chaoxing.com"
        self.driver.get(url)

        self.__wait.until(EC.presence_of_element_located((By.XPATH, '//a[@id="selectSchoolA"]')))
        school_select = self.driver.find_element_by_xpath('//a[@id="selectSchoolA"]')
        action_chains.move_to_element(school_select)
        school_select.click()

        self.__wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="searchSchool1"]')))
        school_input = self.driver.find_element_by_xpath('//input[@id="searchSchool1"]')
        school_input.send_keys(logindata[0].strip(' \t\n'))

        search = self.driver.find_element_by_xpath('//div[@id="dialog1"]/div/div[1]/ul/li[2]/input[2]')
        action_chains.move_to_element(search)
        search.click()

        self.__wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@id="dialog2"]/div/div[2]/div/ul/li[1]/span/a')))
        school_bn = self.driver.find_element_by_xpath('//div[@id="dialog2"]/div/div[2]/div/ul/li[1]/span/a')
        action_chains.move_to_element(school_bn)
        school_bn.click()

        self.__wait.until(EC.presence_of_element_located((By.XPATH, '//span[@id="schoolName2"]')))
        school_name = self.driver.find_element_by_xpath('//span[@id="schoolName2"]').get_attribute('textContent')
        print(COLOR.DISPLAY, 'check your school name:', school_name, COLOR.END)
        #log_fp.write('now url:' + self.driver.current_url)
        self.driver.find_element_by_xpath('//input[@class="zl_input"]').send_keys(logindata[1].strip(' \t\n'))
        self.driver.find_element_by_xpath('//input[@class="zl_input2"]').send_keys(logindata[2].strip(' \t\n'))
        # 获取验证码，填写并点击登录
        while 1:
            img = self.driver.find_element_by_id('numVerCode')
            img.screenshot('login_vercode.png')

            if SYSTEM == 0:  # Win
                img = Image.open('login_vercode.png')
                img.show()
            else:
                p=Popen(['./viu', 'login_vercode.png'])
                p.communicate()
                sleep(1.5)

            numVerCode = input(COLOR.NOTE + "please input the vercode:" + COLOR.END)
            self.driver.find_element_by_id('numcode').send_keys(numVerCode)
            self.driver.find_element_by_xpath('//input[@class="zl_btn_right"]').click()
            #log_fp.write("now url:" + self.driver.current_url + '\n')
            if 'http://i.mooc.chaoxing.com/space/index' not in self.driver.current_url:
                print(COLOR.ERR, 'wrong vercode, login failed, please retry', COLOR.END)
            else:
                break

    def _choose_course(self):
        sleep(10)
        # 从当前页面读取课程名字，经选择后点击
        self.__wait = WebDriverWait(self.driver, 30)
        self.__wait.until(EC.presence_of_element_located((By.XPATH, '//iframe')))
        iframe = self.driver.find_element_by_xpath('//iframe')
        self.driver.switch_to.frame(iframe)
        self.__wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ulDiv')))
        courses_num = len(self.driver.find_elements_by_xpath('//div[@class="ulDiv"]/ul/li'))
        courses_lt = []
        valid_i = 1
        for i in range(1, courses_num):
            try:
                name = self.driver.find_element_by_xpath(
                    '//div[@class="ulDiv"]/ul/li[' + str(i) + ']/div[2]/h3/a').get_attribute('title')
                href = self.driver.find_element_by_xpath(
                    '//div[@class="ulDiv"]/ul/li[' + str(i) + ']/div[1]/a').get_attribute('href')
                courses_lt.append((name, href))
                print(COLOR.DISPLAY + '\t', valid_i, '、', name + COLOR.END)
                valid_i += 1
            except:
                print('=======')
                print(format_exc())
                pass
        return courses_lt
        #log_fp.write("course:" + str([x[0] for x in courses_lt]) + '\n')
        #log_fp.write("choose:" + course_name + '\n')

    def _call_SC(self, courses_lt):
        if self.pattern == 1:
            print(COLOR.OK+' LOGIN_FINISHED'+COLOR.END)

            for name, url in courses_lt:
                print(COLOR.NOTE+' Course:'+name+COLOR.END)
                singlecourse = SC(self.driver, url, name, 0, self.rate, self._sc_out_fp)
                singlecourse.work()
        else:
            while 1:
                try:
                    course_id = eval(input(COLOR.NOTE + 'please select which course by order:' + COLOR.END))
                    if course_id > 0 and course_id <= len(courses_lt):
                        break
                    else:
                        print(COLOR.ERR, ' invalid course order, please reinput!', COLOR.END)
                except:
                    pass

            print(COLOR.OK+' LOGIN_FINISHED'+COLOR.END)

            menu_url = courses_lt[course_id - 1][1]
            course_name = courses_lt[course_id - 1][0]
            singlecourse = SC(self.driver, menu_url, course_name, self.pattern, self.rate, self._sc_out_fp)
            singlecourse.work()


if __name__ == "__main__":
    if len(argv) == 1:
        #logindata = getlogindata()
        logindata = getlogindata_phone()[0:2]
        mode = 0
        rate = 1
    else:
        logindata = (argv[1]).split(',')
        mode = int(argv[2])
        rate = eval(argv[3])
    try:
        process = Login_courses_by_request(logindata, mode, rate)
        # process = Login_courses_by_chrome(logindata,mode,rate)  #备用登录选项
        process.work()
    except SystemExit:
        print(COLOR.NOTE, "QUIT!", COLOR.END)
    except:
        try:
            print(format_exc())
            send_err(format_exc())
        except:
            print(COLOR.ERR, "ERROR! QUIT!", COLOR.END)
    
