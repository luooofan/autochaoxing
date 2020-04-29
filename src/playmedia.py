from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
from sys import stdout
from publicfunc import Color
from re import search as re_search
from traceback import format_exc

COLOR=Color()


class PlayMedia(object):

    rate=1
    instance=None

    def __new__(cls,*args,**kwargs):
        if cls.instance is None:
            cls.instance=super().__new__(cls)
        return cls.instance

    def __init__(self,driver,out_fp=stdout):
        self.driver=driver
        self._out_fp=out_fp

    def play_media(self,url):
        wait = WebDriverWait(self.driver, 30)
        action_chains = ActionChains(self.driver)

        self.driver.get(url)
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
            sleep(5)
            self.driver.execute_script("arguments[0].scrollIntoView();arguments[0].click();", bt)
        except:
            pass
        
        try:
            wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="switchbtn"]')))
            switch_btn=self.driver.find_element_by_xpath('//div[@class="switchbtn"]')
            action_chains.move_to_element(switch_btn)
            switch_btn.click()
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
            except:
                sleep(1)
                pass
        video_road = PlayMedia.get_road(h5_text, video_num)  # bs4处理得到各个视频路径

        print(COLOR.DISPLAY, ' there are ' + str(video_num) + ' media in this section:', COLOR.END, file=self._out_fp)
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

            #print(1)
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

            #print(2)

            try:
                ppt_num = eval(self.driver.execute_script("return document.getElementsByClassName('all')[0].innerText"))
                for i in range(0, ppt_num):
                    self.driver.execute_script("document.getElementsByClassName('mkeRbtn')[0].click()")
                    sleep(1)
                continue
            except:
                pass

            #print(2.5)

            # 通过js代码开始视频播放
            play_ok = 0
            for i in range(3):
                try:
                    self.driver.execute_script(
                        """
                        var video=document.querySelector('video');video.scrollIntoView();video.play();
                        video.onmouseout=function(){return false;}
                        """)
                    play_ok = 1
                    sleep(2)
                    self.driver.execute_script("document.querySelector('video').autoplay=true;")
                    self.driver.execute_script("document.querySelector('video').play();")
                    self.driver.execute_script(
                        "document.querySelector('video').playbackRate=arguments[0];document.querySelector('video').defaultPlaybackRate=arguments[0]", PlayMedia.rate)
                    sleep(1)
                    #self.driver.execute_script("document.querySelector('video').load();")
                    break
                except:
                    print(format_exc())
                    sleep(i+1)
            #print(3)

            audio = 0
            if play_ok == 0:
                for i in range(3):
                    try:
                        self.driver.execute_script(
                            "var audio=document.querySelector('audio');audio.scrollIntoView();audio.play();audio.onmouseout=function(){return false;}")
                        play_ok = 1
                        audio = 1
                        self.driver.execute_script("document.querySelector('audio').autoplay=true;")
                        self.driver.execute_script(
                            "document.querySelector('audio').playbackRate=arguments[0];document.querySelector('audio').defaultPlaybackRate=arguments[0]", PlayMedia.rate)
                        #self.driver.execute_script("document.querySelector('audio').load();")
                        break
                    except:
                        sleep(i+1)
            if audio == 1:
                media_type = 'audio'
            else:
                media_type = 'video'

            #print(media_type)

            if play_ok == 0:
                # 未播放成功
                self.driver.switch_to.parent_frame()
                print(COLOR.DISPLAY+' this is not a media, go ahead!'+COLOR.END, file=self._out_fp)
                #log_fp.write(" this is not a video, go ahead!\n")
                continue
            else:
                # 开倍速 & 获取时间信息
                sleep(2)
                for i in range(5):
                    total_tm = self.driver.execute_script(
                        "return document.querySelector(arguments[0]).duration", media_type)
                    #print(total_tm)
                    now_tm = self.driver.execute_script(
                        "return document.querySelector(arguments[0]).currentTime", media_type)
                    #print(now_tm)
                    self.driver.execute_script("document.querySelector(arguments[0]).play();", media_type)
                    if total_tm != None and now_tm != None:
                        break
                    else:
                        sleep(i+1)
                total_tm = int(total_tm)
                now_tm = int(now_tm)
                need_tm = total_tm-now_tm
                print("   now_tm:", now_tm, '\t', "total_tm:", total_tm, '\t', "need_tm:", need_tm, file=self._out_fp)

            #print(4)

            real_time = 0
            while 1:
                real_time += 10
                try:
                    now_tm = self.driver.execute_script(
                        "return document.querySelector(arguments[0]).currentTime", media_type)
                    need_tm = total_tm-int(now_tm)
                    self.driver.execute_script("document.querySelector(arguments[0]).play();", media_type)

                except:
                    pass
                # 交互
                progress = (total_tm-need_tm)*100/total_tm
                print(COLOR.OK+"   progress:{0:.2f}%\trest:{1}         ".format(progress,
                                                                                need_tm)+COLOR.END, file=self._out_fp, end="\r")
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

                if need_tm <= 2 or real_time > (total_tm+100):
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
                    que_type = re_search(r'[[]([\w\W]+?)[]]', que_type).group(1)
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
        #return 0  # 只要成功执行到这里就置end为0

    ##
    # brief 获取任务点xpath路径
    # details  通过bs4处理h5文本获取xpath
    @staticmethod
    def get_road(text, num):
        # print(text)
        soup = BeautifulSoup('<html><body>' + text + '</body></html>', 'html.parser')
        # 'lxml'和'html5lib'会解析错误，把</p>提前
        # print(soup.prettify())
        # video_lt = soup.find_all('iframe')#视频不一定全部有效
        video_lt = soup.find_all(class_='ans-job-icon')
        road_lt = []
        if len(video_lt) < num:
            num = len(video_lt)
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
