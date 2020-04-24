# coding=utf-8
##
# brief   单账号下单课程任务类
#          DOCKER:不用PIL显示图像，采用viu在终端显示
#                 输出到文件,不输出到终端(保证ssh情况下的可行性)
# author Luoofan
# date   2020-04-03 10:11:02
# FilePath\source_code\singlecourse.py
# 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException as SERException
from bs4 import BeautifulSoup
from PIL import Image
from requests import post,get as requestget
import urllib.parse
from ast import literal_eval
import re
from time import sleep
import time
from colorama import Fore
from colorama import init as colorinit
import traceback
from subprocess import Popen
from publicfunc import Color,send_err,SYSTEM
from queryans import QueryAns
from sys import stdout

COLOR = Color()

# 单账号单课程自动化
class SingleCourse(object):
    # 实例化该类需传入3-5个参数：已经登录的driver，章节名称及对应的url，运行模式以及视频速率
    def __init__(self, driver, menu_url, course_name, pattern=0, rate=1, out_fp=stdout):
        self.driver = driver
        self.menu_url = menu_url
        self.course_name = course_name
        self.courseID=''
        self.pattern = pattern
        self.rate=rate
        self.retry_dic={}
        self._setflag()
        self._out_fp= out_fp if out_fp!=None else stdout
        #self._out_fp=open(course_name+'.txt', 'w+', encoding="utf-8") if SYSTEM==1 else stdout

    def _setflag(self):
        self._err_lt=[]   # 错误章节列表
        self._chapter = 0
        self._section = 0
        self._subsection = 0
        self._end = 0
        self._que_server_flag=1 #1正常 0异常

    def work(self):
        if self.pattern == 0:
            self._perform_model0()  # auto模式
        elif self.pattern == 2:
            self._perform_model2()  # control模式
        else:
            self._perform_model1()  # debug模式
        self._out_fp.flush()

    ##
    # brief  处理单个章节下的三级标题
    # details   通过bs4处理h5文本得到三级标题
    # param  str：text
    # return list：titles
    def _bs4_3rd_titles(self, text):
        soup = BeautifulSoup(text, 'html.parser')
        titles = []
        icons = soup.find_all(class_='icon')
        # print(icons)
        for i in range(1, len(icons)+1):
            flag = icons[i-1].find('em')
            if 'orange' in flag['class']:  # or 'blank' in flag['class']:
                titles.append(i)
        return titles

    ##
    # brief  get&print unfinished chapter list
    # details 获取并输出 未完成章节列表
    # return ch_se_lt 未完成任务章节列表
    # todo:把selenium寻找元素改为正则处理或者js处理
    def _g2p_chapter_section(self):
        self.driver.get(self.menu_url)
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="timeline"]')))
        lt = self.driver.find_element_by_xpath('//div[@class="timeline"]')
        sleep(3)

        ch_se_lt = []
        end = 0
        for i in range(1, 50):
            if end == 2:
                break
            try:
                for j in range(1, 50):
                    icon = lt.find_element_by_xpath(
                        '//div[' + str(i) + ']/div[' + str(j) + ']' + '/h3/span[@class="icon"]')
                    end = 0
                    #print(str(i)+' '+str(j)+' '+re.sub(r'[ \t\n]+','',icon.get_attribute('innerHTML')))

                    try:
                        name = lt.find_element_by_xpath(
                            '//div[' + str(i) + ']/div[' + str(j) + ']' + '/h3/span[@class="articlename"]/a').get_attribute('title')
                        if name in ["问卷调查", "阅读"] or "直播" in name:
                            continue
                    except:
                        pass
                    try:
                        # 寻找三级标题
                        three_levels = lt.find_element_by_xpath(
                            '//div[' + str(i) + ']/div[' + str(j) + ']' + '/div[@class="levelthree"]')
                        #
                        ch_se_lt.extend(
                            [*map(lambda x:[i, j, x], self._bs4_3rd_titles(three_levels.get_attribute('innerHTML')))])
                    except:
                        pass
                    icon_html = icon.get_attribute('innerHTML')
                    if 'orange' in icon_html or "display:inline-block;" in icon_html:
                        ch_se_lt.append([i, j])
            except:
                end += 1

        print(COLOR.WARN, '未完成任务章节：', COLOR.END, str(ch_se_lt), file=self._out_fp)
        for item in ch_se_lt:
            if str(item) not in self.retry_dic:
                self.retry_dic[str(item)]=0
        #log_fp.write('未完成任务章节：' + str(ch_se_lt) + '\n')
        return ch_se_lt

    ##
    # brief 获取任务点xpath路径
    # details  通过bs4处理h5文本获取xpath
    def _get_road(self, text, num):
        # print(text)
        soup = BeautifulSoup('<html><body>' + text + '</body></html>', 'html.parser')
        # 'lxml'和'html5lib'会解析错误，把</p>提前
        # print(soup.prettify())
        # video_lt = soup.find_all('iframe')#视频不一定全部有效
        video_lt = soup.find_all(class_='ans-job-icon')
        road_lt = []
        if len(video_lt)<num:
            num=len(video_lt)
        for i in range(0, num):
            road = ''
            for parent in video_lt[i].parents:
                if parent.name == 'body':
                    break
                index = '[' + str(len([x for x in parent.previous_siblings if x.name == parent.name]) + 1) + ']'
                road = '/' + parent.name + index + road
            road_lt.append(road)
        #log_fp.write(' video road:' + str(road_lt) + '\n')
        return road_lt

    def _play_video(self):

        wait = WebDriverWait(self.driver, 30)
        action_chains = ActionChains(self.driver)

        # 进入课程主页进行选节播放
        self.driver.get(self.menu_url)

        # 未读消息通知框
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="weedialog bradius"]')))
            sleep(2)
            dialog = self.driver.find_element_by_xpath('//div[@class="weedialog bradius"]/div/a')
            sleep(2)
            action_chains.move_to_element(dialog)
            dialog.click()
        except:
            pass

        for i in range(10):
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="timeline"]')))
                lt = self.driver.find_element_by_xpath('//div[@class="timeline"]')
                sleep(1)
                break
            except:
                i = i+1
                sleep(i)
        if i == 10:
            print(COLOR.ERR+" no menus list,continue"+COLOR.END, file=self._out_fp)
            return

        try:
            if self._subsection == 0:  # 2
                lt.find_element_by_xpath('//div[' + str(self._chapter) + ']/div[' +
                                         str(self._section) + ']' + '/h3/span[@class="articlename"]/a').click()
            else:  # 3
                lt.find_element_by_xpath('//div[' + str(self._chapter) + ']/div[' + str(self._section) + ']' +
                                         '/div[@class="levelthree"]/h3['+str(self._subsection)+']/span[@class="articlename"]/a').click()
        except:
            # 正常情况下：是到了阅读模块和调查问卷模块 或者是遇到无效章节
            if self.pattern == 1:
                self._chapter += 1
                self._section = 1
                self._end += 1
            return

        print(COLOR.DISPLAY + 'now turns to ' + COLOR.END, str(self._chapter) + '-' + str(self._section), end="", file=self._out_fp)
        if self._subsection == 0:
            print(file=self._out_fp)
        else:
            print('-'+str(self._subsection), file=self._out_fp)
        #log_fp.write('now turns to ' + str(self._chapter) + '-' + str(self._section) + '-'+str(self._subsection) + '\n')

        # 点击视频确保进入视频界面（若出现问题增多可以改换bs4或者re分析）
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]')))
            try:
                bt = self.driver.find_element_by_xpath(
                    '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]/span[@title="视频"]')
            except:
                try:
                    bt = self.driver.find_element_by_xpath(
                        '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]/span[@title="视频 "]')
                except:
                    try:  # 无标题视频
                        bt = self.driver.find_element_by_xpath(
                            '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]/span[@title="微课"]')
                    except:
                        bt = self.driver.find_element_by_xpath(
                            '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]/span[last()-1]')
            sleep(7)
            self.driver.execute_script("arguments[0].scrollIntoView();arguments[0].click();", bt)
        except:
            pass

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//iframe')))
            iframe = self.driver.find_element_by_xpath('//iframe')
            self.driver.switch_to.frame(iframe)
            sleep(1)
        except:
            print(COLOR.NOTE, ' no videos,continue~', COLOR.END, file=self._out_fp)
            #log_fp.write(' no videos,continue~\n')
            return

        # 多视频处理
        try:
            video_num = self.driver.execute_script(
                "window.scrollTo(0,document.body.scrollHeight);return document.getElementsByClassName('ans-job-icon').length")
        except:
            video_num = self.driver.execute_script(
                "return document.getElementsByClassName('ans-job-icon').length")
        try:
            self.driver.execute_script("window.scrollTo(0,0)")
        except:
            pass

        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="ans-cc"]')))
        ans_cc = self.driver.find_element_by_xpath('//div[@class="ans-cc"]')
        for i in range(3):
            try:
                h5_text = ans_cc.get_attribute('innerHTML')
            except SERException:
                sleep(1)
                pass
        video_road = self._get_road(h5_text, video_num)  # bs4处理得到各个视频路径

        print(COLOR.DISPLAY, ' there are ' + str(video_num) + ' video in this section:', COLOR.END, file=self._out_fp)
        #log_fp.write(' there are ' + str(video_num) + ' videos in this section:\n')

        # 开始播放所有视频
        first_road = '//div[@class="ans-cc"]'

        for v_num in range(1, video_num + 1):
            # log
            #self.driver.refresh()
            self.driver.switch_to.default_content()
            for i in range(5):
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//iframe')))
                    iframe = self.driver.find_element_by_xpath('//iframe')
                    self.driver.switch_to.frame(iframe)
                    break
                except:
                    sleep(i+0.5)
            
            print(COLOR.DISPLAY, ' go ' + str(v_num) + ':', COLOR.END, file=self._out_fp)
            #log_fp.write(' go ' + str(v_num) + ':\n')
            # 拖动滚动条
            #self.driver.execute_script("window.scrollTo(0,arguments[0])", 400 + 700 * (v_num - 1))
            sleep(2)

            goal_road = first_road + video_road[v_num - 1]
            # 查看是否有任务点标识并查看是或否已经完成该任务点
            try:
                flag = self.driver.find_element_by_xpath(goal_road)
                self.driver.execute_script(
                        '''var goal=document.evaluate(arguments[0],document).iterateNext();goal.scrollIntoView();''', goal_road)
                sleep(5)
                icon_flag = 1
                nowflag = flag.get_attribute('class')
                if 'finished' in nowflag:
                    print(COLOR.OK + ' Well! the video is already finished! continue~' + COLOR.END, file=self._out_fp)
                    #log_fp.write(' Well! the video is already finished! continue~' + '\n')
                    self._end = 0
                    # 如果视频任务已完成,访问下一个视频
                    continue
            except:
                #print(traceback.format_exc())
                icon_flag = 0

            # try:
            iframe_flag = 0
            for i in range(10):
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, goal_road + '/iframe')))
                    iframe = self.driver.find_element_by_xpath(goal_road + '/iframe')
                    self.driver.switch_to.frame(iframe)
                    iframe_flag = 1
                    sleep(2)
                    break
                except:
                    #print(traceback.format_exc())
                    # log
                    sleep(i+1)
            if iframe_flag == 0:
                print(COLOR.ERR+"  can't into the video,continue"+COLOR.END, file=self._out_fp)
                continue

            # 通过js代码开始视频播放
            play_ok = 0
            for i in range(4):
                try:
                    self.driver.execute_script(
                            "var video=document.querySelector('video');video.scrollIntoView();video.play();video.onmouseout=function(){return false;}")
                    play_ok = 1
                    self.driver.execute_script("document.querySelector('video').autoplay=true;")
                    self.driver.execute_script("document.querySelector('video').playbackRate=arguments[0];document.querySelector('video').defaultPlaybackRate=arguments[0]",self.rate)
                    self.driver.execute_script("document.querySelector('video').load();")
                    break
                except:
                    sleep(i+1)
            if play_ok == 0:
                # 未播放成功
                self.driver.switch_to.parent_frame()
                print(COLOR.DISPLAY+' this is not a video, go ahead!'+COLOR.END, file=self._out_fp)
                #log_fp.write(" this is not a video, go ahead!\n")
                continue
            else:
                # 开倍速 & 获取时间信息
                sleep(2)
                for i in range(5):
                    total_tm = self.driver.execute_script("return document.querySelector('video').duration")
                    #print(total_tm)
                    now_tm = self.driver.execute_script("return document.querySelector('video').currentTime")
                    #print(now_tm)
                    sleep(2)
                    self.driver.execute_script("document.querySelector('video').play();")
                    if total_tm != None and now_tm != None:
                        break
                    else:
                        sleep(i+1)
                total_tm = int(total_tm)
                now_tm = int(now_tm)
                need_tm = total_tm-now_tm
                print("   now_tm:", now_tm, '\t', "total_tm:", total_tm, '\t', "need_tm:", need_tm, file=self._out_fp)

            real_time=0
            while 1:
                real_time+=10
                try:
                    now_tm = self.driver.execute_script("return document.querySelector('video').currentTime")
                    need_tm=total_tm-int(now_tm)
                except:
                    pass
                # 交互
                progress = (total_tm-need_tm)*100/total_tm
                print(COLOR.OK+"   progress:{0:.2f}%\trest:{1}         ".format(progress, need_tm)+COLOR.END, file=self._out_fp, end="\r")
                self._out_fp.flush()

                # 剩余时间<5min则间隔性检验任务是否已完成
                if (icon_flag == 1 and need_tm <= 300):
                    self.driver.switch_to.parent_frame()
                    flag = self.driver.find_element_by_xpath(goal_road)
                    nowflag = flag.get_attribute('class')
                    self.driver.switch_to.frame(self.driver.find_element_by_xpath(goal_road + '/iframe'))
                    if 'finished' in nowflag:
                        print(COLOR.OK, ' Well！the video is finished ahead of time! continue~', COLOR.END, file=self._out_fp)
                        #log_fp.write(' Well！the video is finished ahead of time! continue~' + '\n')
                        sleep(10)
                        break
                
                if need_tm<=2 or real_time>(total_tm+100) :
                    print(COLOR.OK, ' Well！the video is finished! continue~', COLOR.END, file=self._out_fp)
                    #log_fp.write(' Well！the video is finished! continue~' + '\n')
                    sleep(10)
                    break

                # 自动检测答题
                pre = 1  # 选项默认值
                try:
                    uls = self.driver.find_element_by_xpath(
                        '//div[@class="x-container ans-timelineobjects x-container-default"]/span/div/div/ul')
                    que_type = self.driver.find_element_by_xpath(
                        '//div[@class="ans-videoquiz-title"]').get_attribute('textContent')
                    #log_fp.write('que_type:' + que_type + '\n')
                    que_type = re.search(r'[[]([\w\W]+?)[]]', que_type).group(1)
                    #log_fp.write('      monitor question,' + que_type + '\n')
                    if "多选题" in que_type:
                        # print(uls.find_elements_by_xpath('//li[@class="ans-videoquiz-opt"]'))
                        opt_num = len(uls.find_elements_by_xpath('//li[@class="ans-videoquiz-opt"]'))  # 选项个数
                        #print(opt_num,file=self._out_fp)
                        for opt_i in range(2, opt_num + 1):  # 选择个数2，3，4,……
                            fin_que = 1
                            for opt_j in range(1, opt_num - opt_i + 2):  # 起始位置
                                #print('      select:',file=self._out_fp)
                                for opt_k in range(0, opt_i):  # 个数
                                    option = uls.find_element_by_xpath('//li[' + str(opt_j + opt_k) + ']/label/input')
                                    self.driver.execute_script("arguments[0].click();", option)
                                sleep(5)
                                bn = self.driver.find_element_by_xpath(
                                    '//div[@class="x-container ans-timelineobjects x-container-default"]/span/div/div/div[2]')
                                self.driver.execute_script("arguments[0].click();", bn)
                                try:
                                    self.driver.switch_to_alert().accept()
                                except:
                                    fin_que = 0
                                    break
                                try:
                                    while 1:  # 多选题答错会弹出不止一个alert
                                        self.driver.switch_to_alert().accept()
                                except:
                                    sleep(0.5)
                                
                                for opt_k in range(0, opt_i):  # 个数
                                    option = uls.find_element_by_xpath('//li[' + str(opt_j + opt_k) + ']/label/input')
                                    self.driver.execute_script("arguments[0].click();", option)
                                sleep(5)
                                bn = self.driver.find_element_by_xpath(
                                    '//div[@class="x-container ans-timelineobjects x-container-default"]/span/div/div/div[2]')
                                self.driver.execute_script("arguments[0].click();", bn)
                                try:
                                    while 1:  # 多选题答错会弹出不止一个alert
                                        self.driver.switch_to_alert().accept()
                                except:
                                    sleep(0.5)
                                sleep(0.5)
                                
                            if fin_que == 0:
                                break
                        #log_fp.write('      solve the question\n')
                        sleep(10)
                    else:
                        while 1:
                            try:
                                option = uls.find_element_by_xpath('//li[' + str(pre) + ']/label/input')
                                self.driver.execute_script("arguments[0].click();", option)
                                # action_chains.move_to_element(option)
                                # option.click()
                                #log_fp.write('      select ' + chr(pre + 64) + '\n')
                                bn = self.driver.find_element_by_xpath(
                                    '//div[@class="x-container ans-timelineobjects x-container-default"]/span/div/div/div[2]')
                                self.driver.execute_script("arguments[0].click();", bn)
                                # action_chains.move_to_element(bn)
                                # bn.click()
                                # action_chains.click(bn)
                                try:
                                    while 1:
                                        self.driver.switch_to_alert().accept()
                                except:
                                    sleep(0.3)
                                    pre += 1
                            except:
                                #log_fp.write('      solve the question\n')
                                sleep(10)
                                break
                except:  # 10s延时
                    sleep(10)

            print(COLOR.OK+' finish the video                     '+COLOR.END, file=self._out_fp)
            #log_fp.write(' finish the video: ' + str(self._chapter) +
                         #'-' + str(self._section) + '-' + str(v_num) + '\n')

        self._end = 0  # 只要成功执行到这里就置end为0

    def _ans_question(self):
        # 点击章节测验
        #action_chains = ActionChains(self.driver)
        self.driver.switch_to.default_content()
        sleep(2)
        try:
            bt = self.driver.find_element_by_xpath(
                '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]/span[@title="章节测验"]')
        except:
            try:
                bt = self.driver.find_element_by_xpath(
                    '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]/span[last()]')
            except:  # 还可能没有标签页
                pass

        try:
            sleep(3)
            self.driver.execute_script("arguments[0].click();", bt)
            # action_chains.move_to_element(bt)
            # bt.click()
        except:
            pass

            #print(6, end=" ")
        wait = WebDriverWait(self.driver, 30)
        try:
            # 进入答题界面
            wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[1]')))
            iframe = self.driver.find_element_by_xpath('//iframe[1]')
            self.driver.switch_to.frame(iframe)
            print(COLOR.NOTE+' now go to question '+COLOR.END, file=self._out_fp)
            #log_fp.write(' now go to question \n')
            #print(7, end=" ")
        except:
            print(COLOR.NOTE, ' no questions,continue~', COLOR.END, file=self._out_fp)  # 未找到章节测验
            #log_fp.write(' no questions,continue~\n')
            return 0

        # 多任务点处理
        for i in range(3):
            try:
                task_num = self.driver.execute_script(
                    "window.scrollTo(0,document.body.scrollHeight);return document.getElementsByClassName('ans-job-icon').length")
            except:
                sleep(1)
                # task_num = self.driver.execute_script(
                #    "return document.getElementsByClassName('ans-job-icon').length")
        try:
            self.driver.execute_script("window.scrollTo(0,0)")
        except:
            pass
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="ans-cc"]')))
        for i in range(3):
            try:
                ans_cc = self.driver.find_element_by_xpath('//div[@class="ans-cc"]')
                h5_text = ans_cc.get_attribute('innerHTML')
            except:
                sleep(1)
        task_road = self._get_road(h5_text, task_num)  # bs4处理得到各个任务点路径

        print(COLOR.DISPLAY, ' there are ' + str(task_num) + ' task in this section:', COLOR.END, file=self._out_fp)
        #log_fp.write(' there are ' + str(task_num) + ' task in this section:\n')

        first_road = '//div[@class="ans-cc"]'
        for v_num in range(1, task_num + 1):
            print(COLOR.DISPLAY, ' go ' + str(v_num) + ':', COLOR.END, file=self._out_fp)
            #log_fp.write(' go ' + str(v_num) + ':\n')
            sleep(2)
            try:  # 查看是否有任务点标识并查看是或否已经完成该任务点
                #flag = self.driver.find_element_by_xpath('//div[@class="ans-cc"]/p['+str(p_index[v_num-1])+']/div')
                # print(first_road+video_road[v_num-1])
                flag = self.driver.find_element_by_xpath(first_road + task_road[v_num - 1])
                self.driver.execute_script("arguments[0].scrollIntoView();", flag)

                icon_flag = 1
                nowflag = flag.get_attribute('class')
                #print(nowflag, end=" ")
                if 'finished' in nowflag:
                    print(COLOR.OK + ' Well! the task is already finished! continue~' + COLOR.END, file=self._out_fp)
                    #log_fp.write(' Well! the task is already finished! continue~' + '\n')
                    continue
            except:
                icon_flag = 0  # 有的无任务点标识

            # 检测是否已完成
            # sleep(10)
            #wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="ans-cc"]')))
            #ans_cc = self.driver.find_element_by_xpath('//div[@class="ans-cc"]')
            # action_chains.move_to_element(ans_cc)
            # try:
            #    flag = ans_cc.find_element_by_xpath('//div[@class="ans-job-icon"]/..')
            #    nowflag = flag.get_attribute('class')
            #    # print(nowflag)
            #    if 'finished' in nowflag:
            #        print(COLOR.OK, 'questions of the section is already finished! continue~', COLOR.END, file=self._out_fp)
            #        #log_fp.write(' questions of the section is already finished! continue~' + '\n')
            #        return 0
            # except:
            #    # 定位到题目页元素但无法查看完成状态
            #    print(COLOR.ERR, "  答题失败！", COLOR.END, file=self._out_fp)
            #    #log_fp.write("  答题失败！" + '\n')
            #    return str(self._chapter) + '-' + str(self._section)

            try:
                wait.until(EC.presence_of_element_located((By.XPATH, first_road+task_road[v_num-1]+'/iframe[1]')))
                iframe = self.driver.find_element_by_xpath(first_road+task_road[v_num-1]+'/iframe[1]')
                self.driver.switch_to.frame(iframe)
                wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[1]')))
                iframe = self.driver.find_element_by_xpath('//iframe[1]')
                self.driver.switch_to.frame(iframe)
            except:
                print(COLOR.NOTE, ' no questions,continue~', COLOR.END, file=self._out_fp)  # 未找到章节测验
                #log_fp.write(' no questions,continue~\n')
                self.driver.switch_to.default_content()
                wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[1]')))
                iframe = self.driver.find_element_by_xpath('//iframe[1]')
                self.driver.switch_to.frame(iframe)
                continue
                # print(self.driver.page_source)
            sleep(3)

            #查询并获取答案
            data = {
                'courseId': '',
                'classId': '',
                #'oldWorkId': '',
                #'workRelationId': ''
            }
            try:
                for key in data.keys():
                    data[key] = self.driver.execute_script('return document.getElementById(arguments[0]).value', key)
                    sleep(0.1)
                self.courseID=data['courseId']+' '+data['classId'] 
            except:
                self.courseID=""
            QA=QueryAns(self.driver.page_source,course=self.course_name,courseID=self.courseID)
            ans_flag,ans_lt=QA.work()

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
                        if ans_lt[i][j]==0:
                            continue
                        try:
                            # print(i,j,ans_lt[i][j])
                            radio = self.driver.find_element_by_xpath(
                                '//*[@id="ZyBottom"]/div' + '/div[4]' * i + '/div[2]/ul/li[' + str(ans_lt[i][j]) + ']/label/input')
                        except:
                            radio = self.driver.find_element_by_xpath(
                                '//*[@id="ZyBottom"]/div' + '/div[4]' * i + '/div[2]/div/ul/li[' + str(ans_lt[i][j]) + ']/label/input')
                        self.driver.execute_script("arguments[0].scrollIntoView();arguments[0].click();", radio)
                        # action_chains.move_to_element(radio)
                        # radio.click()
                        sleep(1)
            except:
                #print('==========', file=self._out_fp)
                #print(traceback.format_exc(), file=self._out_fp)
                print(COLOR.ERR, "  答题失败！", COLOR.END, file=self._out_fp)
                #log_fp.write("  答题失败！" + '\n')
                sleep(5)
                return str(self._chapter) + '-' + str(self._section)
                
            # 点击提交并确定，检测验证码
            # //*[@id="tempsave"]
            # //*[@id="ZyBottom"]/div/div[4]/div[4]/div[4]/div[5]/a[1]
            # //*[@id="ZyBottom"]/div/div[4]/div[4]/div[4]/div[5]/a[2]
            # //*[@id="ZyBottom"]/div/div[4]/div[4]/div[4]/div[4]/div[5]/a[2]
            # //*[@id="ZyBottom"]/div[2]/a[2]/span
            try:
                bn = self.driver.find_element_by_xpath('//*[@id="ZyBottom"]/div' + '/div[4]' *
                                                       (len(ans_lt) - 2) + '/div[5]/a['+str(ans_flag)+']')  # 多个题目
            except:
                bn = self.driver.find_element_by_xpath('//*[@id="ZyBottom"]/div[2]/a['+str(ans_flag)+']')  # 只有一个题
            # action_chains.move_to_element(bn)
            # bn.click()
            self.driver.execute_script("arguments[0].scrollIntoView();arguments[0].click();", bn)
            sleep(1)

            try:  # 提交验证码
                self.driver.switch_to.default_content()
                while 1:
                    img = self.driver.find_element_by_id('imgVerCode')
                    img.screenshot('ans_vercode.png')
                    if SYSTEM==0:
                        img = Image.open('ans_vercode.png')
                        img.show()
                    else:
                        p=Popen(['./viu', 'ans_vercode.png'])
                        p.communicate()
                        sleep(1.5)
                    numVerCode = input(COLOR.NOTE + "  please input the ans_vercode:" + COLOR.END, file=self._out_fp)
                    #log_fp.write('  input the ans_vercode\n')
                    # self.driver.find_element_by_id('code').send_keys(numVerCode)
                    self.driver.find_element_by_xpath('//input[@id="code"]').send_keys(numVerCode)
                    self.driver.find_element_by_xpath('//a[@id="sub"]').click()
                    sleep(1)
            except:
                wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[1]')))
                iframe = self.driver.find_element_by_xpath('//iframe[1]')
                self.driver.switch_to.frame(iframe)
                wait.until(EC.presence_of_element_located((By.XPATH, first_road+task_road[v_num-1]+'/iframe[1]')))
                iframe = self.driver.find_element_by_xpath(first_road+task_road[v_num-1]+'/iframe[1]')
                self.driver.switch_to.frame(iframe)
                wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[1]')))
                iframe = self.driver.find_element_by_xpath('//iframe[1]')
                self.driver.switch_to.frame(iframe)

            # //*[@id="confirmSubWin"]/div/div/a[1]
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="confirmSubWin"]/div/div/a[1]')))
            bn = self.driver.find_element_by_xpath('//*[@id="confirmSubWin"]/div/div/a[1]')
            # action_chains.move_to_element(bn)
            try:
                # bn.click()
                self.driver.execute_script("arguments[0].click();", bn)
                print(COLOR.OK, 'questions of the section is finished! continue~', COLOR.END, file=self._out_fp)
                #log_fp.write(' finish the questions ' + '\n')
            except:
                print('=======', file=self._out_fp)
                print(traceback.format_exc(), file=self._out_fp)
                print(COLOR.ERR, "  提交失败！", COLOR.END, file=self._out_fp)
                #log_fp.write("  提交失败！" + '\n')
                return str(self._chapter) + '-' + str(self._section)
            self.driver.switch_to.parent_frame()
            self.driver.switch_to.parent_frame()
            sleep(5)
        # self.driver.switch_to_alert().accept()
        # if(len(err_lt)==0):
        return 0

    def _go_que_task(self):
        try:
            err_section = self._ans_question()

            if err_section != 0:
                print(COLOR.ERR, 'unfinished!', COLOR.END, file=self._out_fp)
                self._err_lt.append(err_section)  # 记录答题提交失败的章节
            else:
                print(COLOR.OK, 'finished!', COLOR.END, file=self._out_fp)
        except:
            try:
                send_err(traceback.format_exc())
            except:
                pass
            
    ##
    # brief    单课程自动模式
    # details  自动完成单课程下的任务(过程不需要输入)，递归调用自身，未完成任务点为空时退出
    #          (todo：单章节设定重试次数，超过次数则退出，避免死循环)
    def _perform_model0(self):
        # 获取未完成章节列表并输出
        ch_se_lt = self._g2p_chapter_section()

        if len(ch_se_lt) == 0:
            print(COLOR.OK, 'finish the lesson! quit! ', COLOR.END, file=self._out_fp)
            return
        self._out_fp.flush()

        last_time = time.time()-120  # 答题间隔控制,减少答题验证码的弹出

        # 遍历每个未完成章节
        end_flag=1
        for ch_se in ch_se_lt:
            if self.retry_dic[str(ch_se)]>2:
                continue
            end_flag=0
            self.retry_dic[str(ch_se)]+=1
            self._chapter = ch_se[0]
            self._section = ch_se[1]
            self._subsection = ch_se[2] if len(ch_se) == 3 else 0

            try:
                self._play_video()
            except:
                try:
                    send_err(traceback.format_exc())
                except:
                    pass
            # 答题间隔控制
            now_time = time.time()
            if now_time-last_time < 120:
                sleep(120-(now_time-last_time))
            last_time = time.time()

            if self._que_server_flag==1:
                self._go_que_task()

        if end_flag==1:
            print(COLOR.OK, 'finish the lesson! quit! ', COLOR.END, file=self._out_fp)
            return
        #log_fp.write("err_lt:" + str(error_lt) + '\n')
        # 递归调用
        return self._perform_model0()

    ##
    # brief    单课程手动模式
    # details  需要输入 开始章节信息 ，用于debug(未设定递归)
    def _perform_model1(self):
        self._g2p_chapter_section()

        last_time = time.time()-300
        self._chapter = eval(input(COLOR.NOTE + "please select which chapter:" + COLOR.END, file=self._out_fp))
        self._section = eval(input(COLOR.NOTE + "please select which section:" + COLOR.END, file=self._out_fp))
        self._subsection = eval(input(COLOR.NOTE + "please select which subsection(if not input 0):" + COLOR.END, file=self._out_fp))
        while 1:
            self._play_video()
            if self._end > 0:
                self._section += 1
                continue
            now_time = time.time()
            # print(now_time-last_time)
            if now_time-last_time < 300:
                sleep(300-(now_time-last_time))
            last_time = time.time()
            if self._end == 2:
                print(COLOR.OK, 'finish the lesson! quit! ', COLOR.END, file=self._out_fp)
            if self._que_server_flag==1:
                self._go_que_task()
            self._section += 1
        #log_fp.write("err_lt:" + str(error_lt) + '\n')

    ##
    # brief    单课程控制模式
    # details  需要输入 终止章节信息
    def _perform_model2(self):
        # 获取未完成章节列表并输出
        ch_se_lt = self._g2p_chapter_section()

        chapter = eval(input("please select the end chapter(from unfinished list):"))
        section = eval(input("please select which section:"))
        subsection = eval(input("please select which subsection(if not input 0):"))
        
        self._out_fp.flush()
        last_time = time.time()-150  # 答题间隔控制,减少答题验证码的弹出

        # 遍历每个未完成章节
        for ch_se in ch_se_lt:

            self._chapter = ch_se[0]
            self._section = ch_se[1]
            self._subsection = ch_se[2] if len(ch_se) == 3 else 0

            if self._chapter == chapter and self._section == section and self._subsection == subsection:
                print(COLOR.OK, "OK! finish your task!", COLOR.END, file=self._out_fp)
                print(COLOR.DISPLAY, "now check your unfinished tasks:", COLOR.END, file=self._out_fp)
                self._g2p_chapter_section()
                break

            try:
                self._play_video()
            except:
                try:
                    send_err(traceback.format_exc())
                except:
                    pass
            # 答题间隔控制
            now_time = time.time()
            if now_time-last_time < 150:
                sleep(150-(now_time-last_time))
            last_time = time.time()

            if self._que_server_flag==1:
                self._go_que_task()
        #log_fp.write("err_lt:" + str(error_lt) + '\n')
