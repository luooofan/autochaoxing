from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from PIL import Image
from requests import post
import urllib.parse
from ast import literal_eval
import re
from time import sleep
import time


class color:
    END = '\033[0m'
    OK = '\033[1;32m'
    NOTE = '\033[1;33m'
    WARN = '\033[1;35m'
    ERR = '\033[1;31m'
    DISPLAY = '\033[1;34m'


class FLAG:
    pattern = 0
    flag = 0
    end = 0
    chapter = 0
    section = 0

    def getvalue(self, _chapter, _section, _flag, _end, _pattern):
        self.chapter = _chapter
        self.section = _section
        self.flag = _flag
        self.end = _end
        self.pattern = _pattern


def getlogindata():
    with open(r'./logindata.txt', 'r', encoding='utf-8') as f:
        return f.readlines()


def init():
    # 初始化
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('log-level=3')
    chrome_options.add_argument('–incognito')  # 启动无痕/隐私模式
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    ##  INFO = 0,
    ##  WARNING = 1,
    ##  LOG_ERROR = 2,
    ##  LOG_FATAL = 3
    ##  default is 0
    return webdriver.Chrome(chrome_options=chrome_options,executable_path=r".\chromedriver")


def login(driver):
    wait = WebDriverWait(driver, 20)
    action_chains = ActionChains(driver)
    logindata = getlogindata()
    log_fp.write('\n' +time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '\n')
    log_fp.write('登录信息:' + logindata[0].strip(' \t\n') +logindata[1].strip(' \t\n') + '\n')

    # 访问登陆界面并选择机构
    url = "https://passport2.chaoxing.com/login?refer=http://i.mooc.chaoxing.com"
    driver.get(url)

    wait.until( EC.presence_of_element_located((By.XPATH, '//a[@id="selectSchoolA"]')))
    school_select = driver.find_element_by_xpath('//a[@id="selectSchoolA"]')
    action_chains.move_to_element(school_select)
    school_select.click()

    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="searchSchool1"]')))
    school_input = driver.find_element_by_xpath('//input[@id="searchSchool1"]')
    school_input.send_keys(logindata[0].strip(' \t\n'))

    search = driver.find_element_by_xpath('//div[@id="dialog1"]/div/div[1]/ul/li[2]/input[2]')
    action_chains.move_to_element(search)
    search.click()

    wait.until( EC.presence_of_element_located((By.XPATH, '//div[@id="dialog2"]/div/div[2]/div/ul/li[1]/span/a')))
    school_bn = driver.find_element_by_xpath('//div[@id="dialog2"]/div/div[2]/div/ul/li[1]/span/a')
    action_chains.move_to_element(school_bn)
    school_bn.click()

    wait.until(EC.presence_of_element_located((By.XPATH, '//span[@id="schoolName2"]')))
    school_name = driver.find_element_by_xpath('//span[@id="schoolName2"]').get_attribute('textContent')
    print(COLOR.DISPLAY, 'check your school name:', school_name, COLOR.END)
    log_fp.write('now url:' + driver.current_url + '\n')

    driver.find_element_by_xpath('//input[@class="zl_input"]').send_keys( logindata[1].strip(' \t\n'))
    driver.find_element_by_xpath('//input[@class="zl_input2"]').send_keys(logindata[2].strip(' \t\n'))
    # 获取验证码，填写并点击登录
    while 1:
        img = driver.find_element_by_id('numVerCode')
        img.screenshot('login_vercode.png')
        img = Image.open('login_vercode.png')
        img.show()
        numVerCode = input(COLOR.NOTE + "please input the vercode:" +COLOR.END)
        driver.find_element_by_id('numcode').send_keys(numVerCode)
        driver.find_element_by_xpath('//input[@class="zl_btn_right"]').click()
        log_fp.write("now url:" + driver.current_url + '\n')
        if 'http://i.mooc.chaoxing.com/space/index' not in driver.current_url:
            print(COLOR.ERR, 'wrong vercode, login failed, please retry',
                  COLOR.END)
        else:
            break


def choose_course(driver):
    sleep(10)

    # 从当前页面读取课程名字，经选择后点击
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.XPATH, '//iframe')))
    iframe = driver.find_element_by_xpath('//iframe')
    driver.switch_to_frame(iframe)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ulDiv')))
    courses_num = len(
        driver.find_elements_by_xpath('//div[@class="ulDiv"]/ul/li'))
    courses_lt = []
    for i in range(1, courses_num):
        name = driver.find_element_by_xpath('//div[@class="ulDiv"]/ul/li[' + str(i) +']/div[2]/h3/a').get_attribute('title')
        href = driver.find_element_by_xpath('//div[@class="ulDiv"]/ul/li[' +str(i) +']/div[1]/a').get_attribute('href')
        courses_lt.append((name, href))
        print(COLOR.DISPLAY + '\t', i, '、', name + COLOR.END)
    while 1:
        course_id = eval( input(COLOR.NOTE + 'please select which course by order:' +COLOR.END))
        if course_id > 0 and course_id <= len(courses_lt):
            break
        else:
            print(COLOR.ERR, ' invalid course order, please reinput!',COLOR.END)
    menu_url = courses_lt[course_id - 1][1]
    course_name = courses_lt[course_id - 1][0]

    # cousre_name_lt =
    log_fp.write("course:" + str([x[0] for x in courses_lt]) + '\n')
    log_fp.write("choose:" + course_name + '\n')

    return [menu_url, course_name]


def get_chapter_section(driver, menu_url):
    driver.get(menu_url)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@class="timeline"]')))
    lt = driver.find_element_by_xpath('//div[@class="timeline"]')
    sleep(3)

    ch_se_lt = []
    end = 0
    for i in range(1, 50):
        if end == 2:
            break
        try:
            for j in range(1, 50):
                # print(i,j)
                icon = lt.find_element_by_xpath('//div[' + str(i) + ']/div[' +str(j) + ']' + '/h3/span[@class="icon"]')
                end = 0
                name = lt.find_element_by_xpath('//div[' + str(i) + ']/div[' + str(j) + ']' +'/h3/span[@class="articlename"]/a').get_attribute('title')
                if name in ["问卷调查", "阅读"]:
                    continue
                if 'openlock' not in icon.get_attribute('innerHTML'):
                    ch_se_lt.append([i, j])
        except:
            end += 1

    return ch_se_lt


# 返回road_lt[]列表
def get_video_road(text, video_num):
    # print(text)
    soup = BeautifulSoup('<html><body>' + text + '</body></html>','html.parser')
    # 'lxml'和'html5lib'会解析错误，把</p>提前
    # print(soup.prettify())
    video_lt = soup.find_all('iframe')
    road_lt = []
    for i in range(0, video_num):
        road = ''
        for parent in video_lt[i].parents:
            if parent.name == 'body':
                break
            index = '[' + str(len([x for x in parent.previous_siblings if x.name == parent.name]) + 1) + ']'
            road = '/' + parent.name + index + road
        road_lt.append(road)
    log_fp.write(' video road:' + str(road_lt) + '\n')
    return road_lt


def play_video(driver, menu_url):
    wait = WebDriverWait(driver, 30)
    action_chains = ActionChains(driver)

    # 进入课程主页进行选节播放
    driver.get(menu_url)
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="timeline"]')))
        lt = driver.find_element_by_xpath('//div[@class="timeline"]')
        sleep(1)
        lt.find_element_by_xpath('//div[' + str(flags.chapter) + ']/div[' +
                                 str(flags.section) + ']' + '/h3/span[@class="articlename"]/a').click()
    except:  # 正常情况下：是到了阅读模块和调查问卷模块 或者是遇到无效章节
        if flags.pattern == 1:
            flags.chapter += 1
            flags.section = 1
            flags.end += 1
        return
    print(COLOR.DISPLAY + 'now turns to ' + COLOR.END, str(flags.chapter) + '-' + str(flags.section))
    log_fp.write('now turns to ' + str(flags.chapter) + '-' + str(flags.section) + '\n')

    # 点击视频确保进入视频界面
    wait.until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]')))  # /span[@title="视频"]')))
    #print('1',end=" ")
    try:
        bt = driver.find_element_by_xpath(
            '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]/span[@title="视频"]')
    except:
        bt = driver.find_element_by_xpath(
            '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]/span[@title="视频 "]')
    #print('2',end=" ")
    sleep(7)
    action_chains.move_to_element(bt)
    bt.click()
    #print(3, end=" ")
    # action_chains.click_and_hold(bt)
    # action_chains.release(bt)

    wait.until(EC.presence_of_element_located((By.XPATH, '//iframe')))
    iframe = driver.find_element_by_xpath('//iframe')
    driver.switch_to.frame(iframe)
    sleep(1)

    # 多视频处理
    video_num = driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight);return document.getElementsByClassName('ans-job-icon').length")
    ans_cc = driver.find_element_by_xpath('//div[@class="ans-cc"]')
    h5_text = ans_cc.get_attribute('innerHTML')
    video_road = get_video_road(h5_text, video_num)  # bs4处理

    print(COLOR.DISPLAY, ' there are ' + str(video_num) + ' video in this section:', COLOR.END)
    log_fp.write(' there are ' + str(video_num) + ' videos in this section:\n')
    '''正则处理模式
    #处理得到每个video所在p标签index
    h5_text=re.sub(r'[ \t\n]','',h5_text)
    p_lt=re.findall(r'<p([\w\W]*?)</p>',h5_text)
    p_index=[]
    for index in range(1,len(p_lt)+1):
        #print(p_lt[index-1])
        if '<divclass="ans-attach-ct' in p_lt[index-1] :
            num=(len(p_lt[index-1])-len((p_lt[index-1]).replace('<divclass="ans-attach-ct','')))//len('<divclass="ans-attach-ct')
            #p_index.append(index)
            p_index.extend([index]*num)
            if len(p_index) ==video_num:
                break
    log_fp.write(' p_index:'+str(p_index))
    #print(p_index)
    '''

    # 开始播放所有视频
    first_road = '//div[@class="ans-cc"]'
    for v_num in range(1, video_num + 1):
        #print(4,end=" ")
        print(COLOR.DISPLAY, ' go ' + str(v_num) + ':', COLOR.END)
        log_fp.write(' go ' + str(v_num) + ':\n')
        driver.execute_script("window.scrollTo(0,arguments[0])", 400 + 700 * (v_num - 1))
        sleep(2)
        try:
            #flag = driver.find_element_by_xpath('//div[@class="ans-cc"]/p['+str(p_index[v_num-1])+']/div')
            # print(first_road+video_road[v_num-1])
            flag = driver.find_element_by_xpath(first_road + video_road[v_num - 1])
            icon_flag = 1
            nowflag = flag.get_attribute('class')
            #print(nowflag, end=" ")
            if 'finished' in nowflag:
                print(COLOR.OK + ' Well! the video is already finished! continue~' + COLOR.END)
                log_fp.write(' Well! the video is already finished! continue~' + '\n')
                flags.end = 0
                # 如果视频任务已完成,访问下一个视频
                continue
        except:
            icon_flag = 0

        # 点击播放并静音
        # print(driver.page_source)
        #wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="ans-cc"]/p['+str(p_index[v_num-1])+']/div/iframe')))
        #iframe = driver.find_element_by_xpath('//div[@class="ans-cc"]/p['+str(p_index[v_num-1])+']/div/iframe')
        wait.until(EC.presence_of_element_located((By.XPATH, first_road + video_road[v_num - 1] + '/iframe')))
        iframe = driver.find_element_by_xpath(first_road + video_road[v_num - 1] + '/iframe')
        driver.switch_to.frame(iframe)

        wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@id="reader"]/div/button[@class="vjs-big-play-button"]')))
        bt = driver.find_element_by_xpath('//div[@id="reader"]/div/button[@class="vjs-big-play-button"]')
        action_chains.move_to_element_with_offset(bt, 0, 0)
        # action_chains.click(bt)
        sleep(5)
        bt.click()  # 点击播放
        print('\033[92m start play \033[0m')
        log_fp.write(' start play \n')

        wait.until(EC.presence_of_element_located((By.XPATH,'//button[@class="vjs-mute-control vjs-control vjs-button vjs-vol-3"]')))
        volumn = driver.find_element_by_xpath('//button[@class="vjs-mute-control vjs-control vjs-button vjs-vol-3"]')
        action_chains.move_to_element(volumn)
        try:
            volumn.click()  # 点击静音
        except:
            sleep(1)

        # 获取时间信息
        if flags.flag > 0:  # 延迟获取video总时间
            sleep(flags.flag)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.vjs-duration-display')))
        total_tm = driver.find_element_by_css_selector('.vjs-duration-display')
        total_tm = total_tm.get_attribute('textContent')
        now_tme = driver.find_element_by_css_selector('.vjs-current-time-display')
        now_tm = now_tme.get_attribute('textContent')
        ttt_index = str(total_tm).find(':')
        total_tm = int(total_tm[:ttt_index], 10) * 60 + int(total_tm[ttt_index + 1:], 10)

        # 检测时间获取异常
        if total_tm == 0:
            log_fp.write(' failed to get total_tm ,will retry this section \n')
            print('\033[95m failed to get total_tm \033[0m,will retry this section ')
            flags.flag += 1
            return
        else:
            flags.flag = 0

        # 输出时间信息
        nt_index = str(now_tm).find(':')
        now_tm = int(now_tm[:nt_index], 10) * 60 + int(now_tm[nt_index + 1:], 10)
        need_tm = total_tm - now_tm
        print("   now_tm:", now_tm, '\t', "total_tm:", total_tm, '\t', "needtm:", need_tm)
        log_fp.write("   now_tm:" + str(now_tm) + '\t' + "total_tm:" + str(total_tm) + '\t' + "needtm:" + str(need_tm) + '\n')

        # 间隔性检验 剩余时间 和 视频内题目
        restime_lt = [x for i in range(1, 8) for x in range(300 * i - 5, 300 * i + 5)]
        for k in range((need_tm // 10) + 2):  # 适当延长，保证程序检测到‘任务点已完成’
            # 获取粗略剩余时间信息，10s误差
            if need_tm in restime_lt:
                print("   time rest: ", ((need_tm + 5) // 300) * 5, "min")
                log_fp.write("   time rest: " +str(((need_tm + 5) // 300) * 5) + "min\n")

            # 剩余时间<5min则间隔性检验任务是否已完成
            if icon_flag == 1 and need_tm <= 300:
                driver.switch_to.parent_frame()
                #flag = driver.find_element_by_xpath('//div[@class="ans-cc"]/p['+str(p_index[v_num-1])+']/div')
                flag = driver.find_element_by_xpath(first_road +
                                                    video_road[v_num - 1])
                nowflag = flag.get_attribute('class')
                # driver.switch_to_frame(driver.find_element_by_xpath('//div[@class="ans-cc"]/p['+str(p_index[v_num-1])+']/div/iframe'))
                driver.switch_to_frame(driver.find_element_by_xpath(first_road +video_road[v_num - 1] +'/iframe'))
                if 'finished' in nowflag:
                    print(COLOR.OK,' Well！the video is finished ahead of time! continue~',COLOR.END)
                    log_fp.write(' Well！the video is finished ahead of time! continue~'+ '\n')
                    sleep(10)
                    break

            # 自动检测答题
            pre = 1  # 选项默认值
            try:
                uls = driver.find_element_by_xpath('//div[@class="x-container ans-timelineobjects x-container-default"]/span/div/div/ul'
                )
                que_type = driver.find_element_by_xpath('//div[@class="ans-videoquiz-title"]').get_attribute( 'textContent')
                log_fp.write('que_type:' + que_type + '\n')
                que_type = re.search(r'[[]([\w\W]+?)[]]', que_type).group(1)
                print('      monitor question')
                log_fp.write('      monitor question,' + que_type + '\n')
                if "多选题" in que_type:
                    # print(uls.find_elements_by_xpath('//li[@class="ans-videoquiz-opt"]'))
                    opt_num = len(uls.find_elements_by_xpath('//li[@class="ans-videoquiz-opt"]'))
                    # print(opt_num)
                    for opt_i in range(2, opt_num + 1):  # 选择个数2，3，4
                        fin_que = 1
                        for opt_j in range(1, opt_num - opt_i + 2):  # 起始位置
                            print('      select:', end=" ")
                            log_fp.write('      select:')
                            for opt_k in range(0, opt_i):  # 个数
                                option = uls.find_element_by_xpath('//li[' + str(opt_j + opt_k) +']/label/input')
                                action_chains.move_to_element(option)
                                option.click()
                                print(chr(opt_j + opt_k + 64), end=" ")
                                log_fp.write(chr(pre + 64) + ' ')
                            print('\n', end="")
                            log_fp.write('\n')
                            bn = driver.find_element_by_xpath('//div[@class="x-container ans-timelineobjects x-container-default"]/span/div/div/div[2]')
                            action_chains.move_to_element(bn)
                            bn.click()
                            # action_chains.click(bn)
                            try:
                                driver.switch_to_alert().accept()
                            except:
                                fin_que = 0
                                break
                            # 到这里说明答题错误
                            try:
                                while 1:  # 多选题答错会弹出不止一个alert
                                    driver.switch_to_alert().accept()
                            except:
                                sleep(0.3)
                        if fin_que == 0:
                            break
                    print('      solve the question')
                    log_fp.write('      solve the question\n')
                    sleep(10)
                else:
                    while 1:
                        try:
                            option = uls.find_element_by_xpath('//li[' +str(pre) + ']/label/input')
                            action_chains.move_to_element(option)
                            option.click()
                            print('      select ' + chr(pre + 64))
                            log_fp.write('      select ' + chr(pre + 64) +'\n')
                            bn = driver.find_element_by_xpath('//div[@class="x-container ans-timelineobjects x-container-default"]/span/div/div/div[2]')
                            action_chains.move_to_element(bn)
                            bn.click()
                            # action_chains.click(bn)
                            try:
                                while 1:
                                    driver.switch_to_alert().accept()
                            except:
                                sleep(0.3)
                                pre += 1
                        except:
                            print('      solve the question')
                            log_fp.write('      solve the question\n')
                            sleep(10)
                            break
            except:  # 10s延时
                sleep(10)
                need_tm -= 10

        print('\033[92m finish the video: \033[0m',str(flags.chapter) + '-' + str(flags.section) + '-' + str(v_num))
        log_fp.write(' finish the video: ' + str(flags.chapter) + '-' +str(flags.section) + '-' + str(v_num) + '\n')

    flags.end = 0


def quiry_ans(question, course_name):
    lt = [x for x in range(0, 10)]
    # lt.append('(')
    lt.extend(['(', ')', '?'])
    goal = 'http://mooc.forestpolice.org/cx/0/'
    for c in question:
        if c in lt:
            goal += c
        else:
            goal += urllib.parse.quote(c)
    # print(goal)
    course = urllib.parse.quote(course_name)
    data = {'course': course, 'type': '0', 'option': ''}
    headers = {
        'Host': 'mooc.forestpolice.org',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
        'Content-type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive'
    }
    timeout = 10
    r = post(goal, data, headers=headers, timeout=timeout)
    status = r.status_code  # int
    # 200 且 code=1 响应成功
    # 200 且 code！=1 服务器繁忙
    # 403 请求过于频繁
    # 其他 服务器异常
    # 处理返回数据的三种方法
    # res=json.loads(r.text)
    # eval()
    if status == 200:
        res = literal_eval(r.text)
        if res['code'] == 1:
            log_fp.write('   响应成功\n')
            # print(res['data'])

            return res['data']
        else:
            log_fp.write('   服务器繁忙\n')
    elif status == 403:
        log_fp.write('   操作过于频繁\n')
    else:
        log_fp.write('   服务器异常\n')

    return 0


def re_process(text, course_name):
    regex = re.compile(r'[ \t\n]')
    text = regex.sub('', text)
    # print(text)
    regex = re.compile(r'\u3010[\u4e00-\u9fa5]+?\u3011([\w\W]+?)[ \t\n]*</div>')
    que_lt = regex.findall(text)  # 问题列表
    for i in range(0, len(que_lt)):
        que_lt[i] = re.sub(r'<.+?>', '', que_lt[i])
        que_lt[i] = re.sub(r'[(](.*?)[)]', '', que_lt[i])

    # print(que_lt)  # 问题
    pd_opt = ['正确', '错误', '√', '×', '对', '错', '是', '否', 'T', 'F', 'ri', 'wr']
    with open(r'./record.txt', 'a+', encoding="utf-8") as f:
        ans_order = []  # 答案序号列表
        ans_ul = re.findall(r'<ulclass="[\w\W]+?</ul>', text)  # 答案列表
        # for item in ans_ul:
        for i in range(1, len(ans_ul) + 1):
            f.write(que_lt[i - 1])
            ans = quiry_ans(que_lt[i - 1], course_name)
            # ans为0，未获取到答案
            log_fp.write('      go to ' + str(que_lt[i - 1]) + ' get ' + str(ans) + '\n')
            if ans == 0:
                ans_order.append([1])  # 服务器异常，默认选1
                continue

            f.write(ans)
            ansopt = re.findall(r'<a.+?><?p?>?([\w\W]+?)<?/?p?>?</a>', ans_ul[i - 1])  # 当前题目 选项列表
            for ansopt_index in range(0, len(ansopt)):
                ansopt[ansopt_index] = re.sub(r'<.+?>', '', ansopt[ansopt_index])
            f.write(str(ansopt))
            if ans in pd_opt:  # 判断题
                ans_order.append([(pd_opt.index(ans)) % 2 + 1])
                # print(ans_order)
            elif ans in ['A', 'B', 'C', 'D', 'E', 'F']:  # 直接返回选项的单选题
                ans_order.append([ord(ans) - ord('A') + 1])
            else:
                now_que_order = []
                for opt in ansopt:
                    if opt in ans:
                        now_que_order.append(ansopt.index(opt) + 1)
                if len(now_que_order) == 0:
                    now_que_order.append(1)  # 无匹配答案默认选A
                ans_order.append(now_que_order)
                # if ansopt.count(ans) == 1:
                #    ans_order.append(ansopt.index(ans)+1)
                # else:
                #    ans_order.append(1)
            f.write(str(ans_order[i - 1]) + '\n')
    return ans_order  # 返回一个列表,列表内的每一项是每个题目的答案列表


def ans_question(driver, course_name):
    # 点击章节测验
    print('\033[93m now go to question \033[0m')
    log_fp.write(' now go to question \n')
    action_chains = ActionChains(driver)
    driver.switch_to.default_content()
    try:
        bt = driver.find_element_by_xpath(
            '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]/span[@title="章节测验"]')
    except:
        print(COLOR.NOTE, ' no questions,continue~', COLOR.END)
        log_fp.write(' no questions,continue~\n')
        flags.section += 1
        return 0
    sleep(3)
    action_chains.move_to_element(bt)
    bt.click()
    #print(6, end=" ")

    # 进入答题界面
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[1]')))
    iframe = driver.find_element_by_xpath('//iframe[1]')
    driver.switch_to.frame(iframe)
    #print(7, end=" ")

    # 检测是否已完成
    flag = driver.find_element_by_xpath('//div[@class="ans-job-icon"]/..')
    nowflag = flag.get_attribute('class')
    # print(nowflag)
    if 'finished' in nowflag:
        print(COLOR.OK, 'questions of the section is already finished! continue~', COLOR.END)
        log_fp.write(' questions of the section is already finished! continue~' + '\n')
        flags.section += 1
        return 0

    for i in range(2):
        wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[1]')))
        iframe = driver.find_element_by_xpath('//iframe[1]')
        driver.switch_to.frame(iframe)
    # print(driver.page_source)
    sleep(3)

    ans_lt = re_process(driver.page_source, course_name)
    # print(ans_lt)
    # 开始答题
    # //*[@id="ZyBottom"]/div/div[1]/div
    # //*[@id="ZyBottom"]/div/div[2]/ul/li[1]/label/input
    # //*[@id="ZyBottom"]/div/div[2]/ul/li[2]/label/input
    # //*[@id="ZyBottom"]/div/div[4]/div[2]/ul/li[1]/label/input
    # //*[@id="ZyBottom"]/div/div[4]/div[4]/div[2]/ul/li[1]/label/input
    # //*[@id="ZyBottom"]/div/div[4]/div[4]/div[4]/div[2]/div/ul/li[1]/label/input
    try:
        for i in range(0, len(ans_lt)):
            for j in range(0, len(ans_lt[i])):
                try:
                    # print(i,j,ans_lt[i][j])
                    radio = driver.find_element_by_xpath(
                        '//*[@id="ZyBottom"]/div' + '/div[4]' * i + '/div[2]/ul/li[' + str(ans_lt[i][j]) + ']/label/input')
                except:
                    radio = driver.find_element_by_xpath(
                        '//*[@id="ZyBottom"]/div' + '/div[4]' * i + '/div[2]/div/ul/li[' + str(ans_lt[i][j]) + ']/label/input')
                action_chains.move_to_element(radio)
                radio.click()
    except:
        print(COLOR.ERR, "  答题失败！", COLOR.END)
        log_fp.write("  答题失败！" + '\n')
        if flags.pattern == 1:
            flags.section += 1
        return str(flags.chapter) + '-' + str(flags.section)

    # sleep(60)
    # 点击提交并确定，检测验证码
    # //*[@id="tempsave"]
    # //*[@id="ZyBottom"]/div/div[4]/div[4]/div[4]/div[5]/a[1]
    # //*[@id="ZyBottom"]/div/div[4]/div[4]/div[4]/div[5]/a[2]
    # //*[@id="ZyBottom"]/div/div[4]/div[4]/div[4]/div[4]/div[5]/a[2]
    # //*[@id="ZyBottom"]/div[2]/a[2]/span
    try:
        bn = driver.find_element_by_xpath('//*[@id="ZyBottom"]/div' + '/div[4]' *
                                          (len(ans_lt) - 2) + '/div[5]/a[2]')  # 多个题目
    except:
        bn = driver.find_element_by_xpath('//*[@id="ZyBottom"]/div[2]/a[2]')  # 只有一个题
    action_chains.move_to_element(bn)
    bn.click()
    sleep(0.5)

    try:  # 提交验证码
        driver.switch_to.default_content()
        while 1:
            img = driver.find_element_by_id('imgVerCode')
            img.screenshot('ans_vercode.png')
            img = Image.open('ans_vercode.png')
            img.show()
            numVerCode = input(COLOR.NOTE + "  please input the ans_vercode:" + COLOR.END)
            log_fp.write('  input the ans_vercode\n')
            # driver.find_element_by_id('code').send_keys(numVerCode)
            driver.find_element_by_xpath('//input[@id="code"]').send_keys(numVerCode)
            driver.find_element_by_xpath('//a[@id="sub"]').click()
            sleep(1)
    except:
        for i in range(3):
            wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[1]')))
            iframe = driver.find_element_by_xpath('//iframe[1]')
            driver.switch_to.frame(iframe)

    # //*[@id="confirmSubWin"]/div/div/a[1]
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="confirmSubWin"]/div/div/a[1]')))
    bn = driver.find_element_by_xpath('//*[@id="confirmSubWin"]/div/div/a[1]')
    action_chains.move_to_element(bn)
    try:
        bn.click()
        print(COLOR.OK, 'questions of the section is already finished! continue~', COLOR.END)
        log_fp.write(' finish the questions ' + '\n')
    except:
        print(COLOR.ERR, "  提交失败！", COLOR.END)
        log_fp.write("  提交失败！" + '\n')
        if flags.pattern == 1:
            flags.section += 1
        return str(flags.chapter) + '-' + str(flags.section)
    # sleep(1)
    # driver.switch_to_alert().accept()
    if flags.pattern == 1:
        flags.section += 1

    return 0


def perform(driver, menu_url, course_name):
    while 1:
        pattern = eval(input(COLOR.NOTE + "please select the pattern(0 is auto,1 is manual):" + COLOR.END))
        if pattern in [0, 1]:
            break
    ch_se_lt = get_chapter_section(driver, menu_url)
    print(COLOR.WARN, '未完成任务章节：', COLOR.END, str(ch_se_lt))
    log_fp.write('未完成任务章节：' + str(ch_se_lt) + '\n')
    error_lt = []
    if pattern == 1:
        chapter = eval(input(COLOR.NOTE + "please select which chapter:" + COLOR.END))
        section = eval(input(COLOR.NOTE + "please select which section:" + COLOR.END))
        flags.getvalue(chapter, section, 0, 0, pattern)
        while 1:
            play_video(driver, menu_url)
            if flags.flag > 0:
                print(COLOR.ERR, 'unfinished! Retry…', COLOR.END)
                continue
            elif flags.end > 0:
                continue
            if flags.end == 2:
                print(COLOR.OK, 'finish the lesson! quit! ', COLOR.END)
            err_section = ans_question(driver, course_name)
            if err_section != 0:
                print(COLOR.ERR, 'unfinished!', COLOR.END)
                error_lt.append(err_section)  # 记录答题提交失败的章节
            print(COLOR.OK, 'finished!', COLOR.END)
    else:
        flags.getvalue(0, 0, 0, 0, pattern)
        for ch_se in ch_se_lt:
            flags.chapter = ch_se[0]
            flags.section = ch_se[1]
            while 1:
                play_video(driver, menu_url)
                if flags.flag > 0:
                    print(COLOR.ERR, 'unfinished! Retry…', COLOR.END)
                else:
                    break
            err_section = ans_question(driver, course_name)
            if err_section != 0:
                print(COLOR.ERR, 'unfinished!', COLOR.END)
                error_lt.append(err_section)  # 记录答题提交失败的章节
            print(COLOR.OK, 'finished!', COLOR.END)
        print(COLOR.OK, 'finish the lesson! quit! ', COLOR.END)

    log_fp.write("err_lt:" + str(error_lt) + '\n')
    driver.quit()


def main():
    driver = init()
    print(COLOR.DISPLAY, 'Lauching…', COLOR.END)
    login(driver)
    # print(driver.current_url)
    ret = choose_course(driver)
    perform(driver, ret[0], ret[1])


if __name__ == "__main__":
    COLOR = color()
    flags = FLAG()
    log_fp = open(r'./chaoxing.txt', 'a+', encoding='utf-8')
    main()
    log_fp.close()
