# coding=utf-8
##
# brief   单账号下单课程任务类
#          DOCKER:不用PIL显示图像，采用viu在终端显示
#                 输出到文件,不输出到终端(保证ssh情况下的可行性)
# author Luoofan
# date   2020-04-03 10:11:02
# FilePath\src\singlecourse.py
# 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
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
from playmedia import PlayMedia
from queryans import QueryAns
from sys import stdout

COLOR = Color()

if SYSTEM==0:
    from PIL import Image

# 单账号单课程自动化
class SingleCourse(object):

    # 实例化该类需传入3-5个参数：已经登录的driver，章节名称及对应的url，运行模式以及视频速率
    def __init__(self, driver, menu_url, course_name, pattern=0, out_fp=stdout):
        self.driver = driver
        self.menu_url = menu_url
        self.course_name = course_name
        self.courseID=''
        self.pattern = pattern
        #self.rate=rate
        self._setflag()
        self._out_fp= out_fp if out_fp!=None else stdout
        #self._out_fp=open(course_name+'.txt', 'w+', encoding="utf-8") if SYSTEM==1 else stdout

    def _setflag(self):
        self.ch_se_lt=[]
        self.retry_dic={}
        self._err_lt=[]   # 错误章节列表
        #self._chapter = 0
        #self._section = 0
        #self._subsection = 0
        #self._end = 0
        self._que_server_flag=1 #1正常 0异常

    def work(self):
        if self.pattern == 0:
            self._perform_model0()  # auto模式
        elif self.pattern == 2:
            self._perform_model2()  # control模式
        self._out_fp.flush()

    def _get_chapter_section(self):
        action_chains = ActionChains(self.driver)
        try:
            self.driver.get(self.menu_url)
            self._bs4_menu_page()
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            # 未读消息通知框
            self.driver.get(self.menu_url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="weedialog bradius"]')))
            sleep(2)
            dialog = self.driver.find_element_by_xpath('//div[@class="weedialog bradius"]/div/a')
            sleep(2)
            action_chains.move_to_element(dialog)
            dialog.click()
            self._bs4_menu_page()
        sleep(1)
        
        print(COLOR.WARN, '未完成任务章节：', COLOR.END, file=self._out_fp)
        #, str(ch_se_lt), file=self._out_fp)
        for item in self.ch_se_lt:
            print('\t'+str(item[0]),file=self._out_fp)
            if str(item[0]) not in self.retry_dic.keys():
                self.retry_dic[str(item[0])] = 0
    
    def _midprocess(self,input_lt,num):
        #课程目录分析的中间过程
        level = ['leveltwo', 'levelthree', 'levelfour', 'levelfive']
        #print('num:'+str(num))
        #print('str(len(input_lt)))
        output_lt=[]
        for item in input_lt:
            title=""
            if num==0:#units
                try:
                    title = item.h2.a.attrs['title']
                    #print('units:'+title)
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except:
                    continue
            else:
                try:
                    title = item.find(class_='chapterNumber').string+'|-|'
                    title += item.find(class_='articlename').a.attrs['title']
                    icon = item.find(class_='icon').em.attrs['class']
                    #print(title+'   '+str(icon))
                    #"display:inline-block;"
                    if 'orange' in icon or 'blank' in icon: #未完成
                        try:
                            self.ch_se_lt.append((title, item.find(class_='articlename').a.attrs['href']))
                        except KeyboardInterrupt:
                            raise KeyboardInterrupt
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except:
                    pass
            try:
                sub_lt=item.find_all(class_=level[num])
                if num==1: #第三级标题
                    sub_lt=sub_lt[0].find_all(class_='clearfix')
                if len(sub_lt)!=0:
                    output_lt.append((title,self._midprocess(sub_lt,num+1)))
                else:
                    raise Exception
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                if title!='':
                    output_lt.append((title,[]))
        return output_lt

    def _bs4_menu_page(self,page_source=''):
        #对课程目录页分析，得到课程目录信息 以及 未完成任务章节
        self.ch_se_lt=[] #(order,url)
        if page_source=="":
            page_source=self.driver.page_source
        soup=BeautifulSoup(page_source,'html.parser')

        timeline = soup.find(class_='timeline')
        units_lt=timeline.find_all(class_='units')

        #total_info = 
        self._midprocess(units_lt, 0)
        #print(str(total_info))
        #print(str(self.ch_se_lt))

    def _ans_question(self):
        # 点击章节测验
        #action_chains = ActionChains(self.driver)
        self.driver.switch_to.default_content()
        sleep(2)
        try:
            bt = self.driver.find_element_by_xpath(
                '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]/span[@title="章节测验"]')
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            try:
                bt = self.driver.find_element_by_xpath(
                    '//div[@class="left"]/div/div[@class="main"]/div[@class="tabtags"]/span[last()]')
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:  # 还可能没有标签页
                pass

        try:
            sleep(3)
            self.driver.execute_script("arguments[0].click();", bt)
            # action_chains.move_to_element(bt)
            # bt.click()
        except KeyboardInterrupt:
            raise KeyboardInterrupt
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
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            print(COLOR.NOTE, ' no questions,continue~', COLOR.END, file=self._out_fp)  # 未找到章节测验
            #log_fp.write(' no questions,continue~\n')
            return 0

        # 多任务点处理
        for i in range(3):
            try:
                task_num = self.driver.execute_script(
                    "window.scrollTo(0,document.body.scrollHeight);return document.getElementsByClassName('ans-job-icon').length")
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                sleep(1)
                # task_num = self.driver.execute_script(
                #    "return document.getElementsByClassName('ans-job-icon').length")
        try:
            self.driver.execute_script("window.scrollTo(0,0)")
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            pass
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="ans-cc"]')))
        for i in range(3):
            try:
                ans_cc = self.driver.find_element_by_xpath('//div[@class="ans-cc"]')
                h5_text = ans_cc.get_attribute('innerHTML')
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                sleep(1)
        task_road = PlayMedia.get_road(h5_text, task_num)  # bs4处理得到各个任务点路径

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

                #icon_flag = 1
                nowflag = flag.get_attribute('class')
                #print(nowflag, end=" ")
                if 'finished' in nowflag:
                    print(COLOR.OK + ' Well! the task is already finished! continue~' + COLOR.END, file=self._out_fp)
                    #log_fp.write(' Well! the task is already finished! continue~' + '\n')
                    continue
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                pass
                #icon_flag = 0  # 有的无任务点标识

            try:
                wait.until(EC.presence_of_element_located((By.XPATH, first_road+task_road[v_num-1]+'/iframe[1]')))
                iframe = self.driver.find_element_by_xpath(first_road+task_road[v_num-1]+'/iframe[1]')
                self.driver.switch_to.frame(iframe)
                wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[1]')))
                iframe = self.driver.find_element_by_xpath('//iframe[1]')
                self.driver.switch_to.frame(iframe)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
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
            except KeyboardInterrupt:
                raise KeyboardInterrupt
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
                        except KeyboardInterrupt:
                            raise KeyboardInterrupt
                        except:
                            radio = self.driver.find_element_by_xpath(
                                '//*[@id="ZyBottom"]/div' + '/div[4]' * i + '/div[2]/div/ul/li[' + str(ans_lt[i][j]) + ']/label/input')
                        self.driver.execute_script("arguments[0].scrollIntoView();arguments[0].click();", radio)
                        # action_chains.move_to_element(radio)
                        # radio.click()
                        sleep(1)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                #print('==========', file=self._out_fp)
                #print(traceback.format_exc(), file=self._out_fp)
                print(COLOR.ERR, "  答题失败！", COLOR.END, file=self._out_fp)
                #log_fp.write("  答题失败！" + '\n')
                sleep(5)
                return 1
                #str(self._chapter) + '-' + str(self._section)
                
            # 点击提交并确定，检测验证码
            # //*[@id="tempsave"]
            # //*[@id="ZyBottom"]/div/div[4]/div[4]/div[4]/div[5]/a[1]
            # //*[@id="ZyBottom"]/div/div[4]/div[4]/div[4]/div[5]/a[2]
            # //*[@id="ZyBottom"]/div/div[4]/div[4]/div[4]/div[4]/div[5]/a[2]
            # //*[@id="ZyBottom"]/div[2]/a[2]/span
            try:
                bn = self.driver.find_element_by_xpath('//*[@id="ZyBottom"]/div' + '/div[4]' *
                                                       (len(ans_lt) - 2) + '/div[5]/a['+str(ans_flag)+']')  # 多个题目
            except KeyboardInterrupt:
                raise KeyboardInterrupt
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
                        p=Popen(['./src/viu', 'ans_vercode.png'])
                        p.communicate()
                        sleep(1.5)
                    numVerCode = input(COLOR.NOTE + "  please input the ans_vercode:" + COLOR.END, file=self._out_fp)
                    #log_fp.write('  input the ans_vercode\n')
                    # self.driver.find_element_by_id('code').send_keys(numVerCode)
                    self.driver.find_element_by_xpath('//input[@id="code"]').send_keys(numVerCode)
                    self.driver.find_element_by_xpath('//a[@id="sub"]').click()
                    sleep(1)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
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
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                #print('=======', file=self._out_fp)
                #print(traceback.format_exc(), file=self._out_fp)
                send_err(traceback.format_exc())
                print(COLOR.ERR, "  提交失败！", COLOR.END, file=self._out_fp)
                #log_fp.write("  提交失败！" + '\n')
                return 1
            self.driver.switch_to.parent_frame()
            self.driver.switch_to.parent_frame()
            sleep(5)
        # self.driver.switch_to_alert().accept()
        # if(len(err_lt)==0):
        return 0

    def _go_que_task(self):
        try:
            err_flag = self._ans_question()

            if err_flag != 0:
                print(COLOR.ERR, 'unfinished!', COLOR.END, file=self._out_fp)
                #self._err_lt.append()  # 记录答题提交失败的章节
            else:
                print(COLOR.OK, 'finished!', COLOR.END, file=self._out_fp)
        except KeyboardInterrupt:
                raise KeyboardInterrupt
        except:
            send_err(traceback.format_exc())

            
    ##
    # brief    单课程自动模式
    # details  自动完成单课程下的任务(过程不需要输入)，递归调用自身，未完成任务点为空时退出
    #          (单章节设定重试次数，超过次数则退出，避免死循环)
    def _perform_model0(self):
        # 获取未完成章节列表并输出
        self._get_chapter_section()

        if len(self.ch_se_lt) == 0:
            print(COLOR.OK, 'finish the lesson! quit! ', COLOR.END, file=self._out_fp)
            return
        self._out_fp.flush()

        last_time = time.time()-120  # 答题间隔控制,减少答题验证码的弹出

        # 遍历每个未完成章节
        end_flag=1
        for ch_se in self.ch_se_lt:
            if self.retry_dic[str(ch_se[0])]>2:
                continue
            end_flag=0
            self.retry_dic[str(ch_se[0])]+=1
            
            print(COLOR.DISPLAY + 'now turns to '+str(ch_se[0]) + COLOR.END, file=self._out_fp)
            try:
                PM=PlayMedia(self.driver,self._out_fp)
                PM.play_media('https://mooc1-1.chaoxing.com'+ch_se[1])
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                send_err(traceback.format_exc())

            if self._que_server_flag==1:
                # 答题间隔控制
                now_time = time.time()
                if now_time-last_time < 120:
                    sleep(120-(now_time-last_time))
                last_time = time.time()
                self._go_que_task()

        if end_flag==1:
            print(COLOR.OK, 'finish the lesson! quit! ', COLOR.END, file=self._out_fp)
            return
        #log_fp.write("err_lt:" + str(error_lt) + '\n')
        # 递归调用
        return self._perform_model0()

    ##
    # brief    单课程控制模式
    # details  需要输入 终止章节信息
    def _perform_model2(self):
        # 获取未完成章节列表并输出
        self._get_chapter_section()

        #chapter = eval(input("please select the end chapter(from unfinished list):"))
        #section = eval(input("please select which section:"))
        #subsection = eval(input("please select which subsection(if not input 0):"))
        end_ch_se = input("please input the end chapter(from unfinished list):")

        self._out_fp.flush()
        last_time = time.time()-150  # 答题间隔控制,减少答题验证码的弹出

        # 遍历每个未完成章节
        for ch_se in self.ch_se_lt:
            
            if end_ch_se in ch_se[0]:
                print(COLOR.OK, "OK! finish your task!", COLOR.END, file=self._out_fp)
                print(COLOR.DISPLAY, "now check your unfinished tasks:", COLOR.END, file=self._out_fp)
                self._get_chapter_section()
                break

            print(COLOR.DISPLAY + 'now turns to '+str(ch_se[0]) + COLOR.END, file=self._out_fp)
            try:
                PM=PlayMedia(self.driver,self._out_fp)
                PM.play_media('https://mooc1-1.chaoxing.com'+ch_se[1])
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                send_err(traceback.format_exc())

            if self._que_server_flag == 1:
                # 答题间隔控制
                now_time = time.time()
                if now_time-last_time < 150:
                    sleep(150-(now_time-last_time))
                last_time = time.time()
                self._go_que_task()
