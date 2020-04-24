import re
from time import sleep
from urllib import parse
from requests import post, get as requestget
from traceback import format_exc
from ast import literal_eval
from publicfunc import send_que


class QueryAns(object):
    que_type = ['单选题', '多选题', '填空题', '判断题', '简答题', '名词解释题', '论述题', '计算题', '其他',
                '分录题', '资料题', '连线题', '', '排序题', '完形填空', '阅读理解', '', '', '口语题', '听力题']
    pd_opt = ['正确', '错误', '√', '×', '对', '错', '是', '否', 'T', 'F', 'ri', 'wr', 'true', 'false']

    def __init__(self, h5page='', *, question='', type='',  course='', courseID=''):
        # 实例化方式:QueryAns(course,h5page)页面源码        操作:将处理源码内全部题目
        #           QueryAns(course,**info)课程-题目-类型       将处理单个题目
        self.course = course
        self.courseID=courseID
        self.que_lt = []
        self.ans_ul = []
        self.que = ""
        self.que_ori = ""
        self.que_type = ""
        if h5page == "":
            self.que_ori = question
            self.que_lt.append((type, question))  # 有可能为空
            self._re_que_lt()
        else:
            self._re_h5page(h5page)  # get que_lt,ans_ul

    def work(self):
        if len(self.ans_ul) == 0:
            return self.work4single()
        else:
            return self.work4page()

    def work4single(self):
        if QueryAns.que_type.count(self.que_lt[0][0]) == 0:
            self.que_type = 8
        else:
            self.que_type = QueryAns.que_type.index(self.que_lt[0][0])

        # 访问查题接口获取答案
        self.que = self.que_lt[0][1]
        return self._query_ans()

    def work4page(self):
        # 答案序号列表
        ans_order = []
        for i in range(1, len(self.ans_ul) + 1):

            # 问题类型
            if QueryAns.que_type.count(self.que_lt[i-1][0]) == 0:
                self.que_type = 8
            else:
                self.que_type = QueryAns.que_type.index(self.que_lt[i-1][0])

            # 访问查题接口获取答案
            self.que = self.que_lt[i - 1][1]
            ans = self._query_ans()
            sleep(3)
            # ans为0，未获取到答案
            if ans == 0:
                ans_order.append([1])  # 服务器异常，默认选1
                continue

            ansopt = re.findall(r'<a.+?><?p?>?([\w\W]+?)<?/?p?>?</a>', self.ans_ul[i - 1])  # 当前题目 选项列表
            for ansopt_index in range(0, len(ansopt)):
                ansopt[ansopt_index] = re.sub(r'<.+?>', '', ansopt[ansopt_index])

            if ans in QueryAns.pd_opt:  # 判断题
                ans_order.append([(QueryAns.pd_opt.index(ans)) % 2 + 1])
            elif ans in ['A', 'B', 'C', 'D', 'E', 'F']:  # 直接返回选项的单选题
                if (ord(ans) - ord('A') + 1) > len(ansopt):
                    ans_order.append([1])
                else:
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

            #f.write(str(ans_order[i - 1]) + '\n')
        #f.flush()
        #f.close()
        return ans_order  # 返回一个列表,列表内的每一项是每个题目的答案列表

    def _query_ans(self):
        res= self.GreasyFork_Group_API()
        if res==0 or res=='' or '暂未搜到' in res:
            res = self.WangKeTiKu_API()
            if res=='' or res==0:
                res=self.SearchAns_GUI_API()
                if res=='':
                    res=0
        if res!=0:
            send_que('courseID:'+self.courseID+' course:'+self.course + ' que:' + self.que + '  ans:' + str(res) + '\n')
        return res

    def SearchAns_GUI_API(self):
        #以原问题访问准确率更高___h5源码实例化的时候尽量不使用该方式
        url = 'http://api.xmlm8.com/tk.php?t='+parse.quote(self.que_ori)
        try:
            ret_da = literal_eval(requestget(url).text)
            #print("que:"+ret_da['tm']+'\n'+"ans:"+ret_da['da'])
            return ret_da['da']
        except:
            return 0

    def GreasyFork_Group_API(self):
        #url = 'http://mooc.forestpolice.org/cx/0/' #WYN
        url2 = 'http://voice.fafads.cn/xxt/api.php'
        url1 = 'http://129.204.175.209/cha_xin.php'

        #def _prepare_query(index):
        #    data = {
        #        'courseId': '',
        #        'classId': '',
        #        'oldWorkId': '',
        #        'workRelationId': ''
        #    }
        #    for key in data.keys():
        #        data[key] = self.driver.execute_script('return document.getElementById(arguments[0]).value', key)
        #        sleep(0.1)
        #    #print(data)
        #    url = 'http://mooc.forestpolice.org/report/cx/'
        #    requestget(url, data=data)
        #    sleep(1)
        # _prepare_query()

        # get goal
        '''lt = [x for x in range(0, 10)]
        lt.extend(['(', ')', '?'])
        goal = url1
        for c in self.que:
            if c in lt:
                goal += c
            else:
                goal += parse.quote(c)'''

        #course = urllib.parse.quote(self.course)
        data2 = {
            # 'course': course,
            'question': self.que,  # 不能用parse.quote()和goal
            'type': str(type)
        }
        data1 = {
            'content': self.que
        }

        def post_url(url,data):
            headers = {
                'Content-type': 'application/x-www-form-urlencoded',
            }
            timeout = 30
            r = post(url, data, headers=headers, timeout=timeout)
            #print(r.text)
            status = r.status_code  # int
            # 200 且 code=1 响应成功
            # 200 且 code！=1 服务器繁忙
            # 403 请求过于频繁
            # 其他 服务器异常
            if status == 200:
                try:
                    res = literal_eval(r.text.strip(' \n'))
                    #if res['code'] == 1:
                    #    print('   响应成功\n')
                    # print(res['data'])
                    try:
                        return res['data']
                    except:
                        return res['answer']
                except:
                    return 0
            #    except:
            #        print('=======')
            #        print(format_exc())
            #        return 0
            #    else:
            #        print('   服务器繁忙\n')
            #elif status == 403:
            #    print('   操作过于频繁\n')
            #else:
            #    print('   服务器异常\n')
            return 0
        
        res=post_url(url1,data1)
        if res==0:
            return post_url(url2,data2)
        else:
            return res

    def WangKeTiKu_API(self):
        #print(self.que)
        url='http://www.wangketiku.com/getquestion.php?question='+self.que_ori
        headers={
            'Host': 'www.wangketiku.com',
            'Referer':'http://www.wangketiku.com/?',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
        }
        try:
            ret = literal_eval(requestget(url,headers=headers).text)['answer']
            #print(ret)
            ret=re.sub('[ \t\n\：]','',ret)
            ret=re.sub(r'题目(.+?)答案','',ret) 
            index=ret.rfind('选项')
            if index!=-1:
                ret=ret[:index]
            ret_lt=ret.split('备选')
            del ret_lt[0]
            ans =""
            for item in ret_lt:
                if '李恒道不会做这道题' in item or '暂无答案' in item:
                    continue
                else:
                    ans+=item+'#'
            return ans
        except:
            return 0

    def _re_h5page(self, text):
            # 去空格、tab、换行
        regex = re.compile(r'[ \t\n]')
        text = regex.sub('', text)

        # 提取列表self.que_lt 并处理
        regex = re.compile(r'\u3010([\u4e00-\u9fa5]+?)\u3011([\w\W]+?)[ \t\n]*</div>')
        self.que_lt = regex.findall(text)
        self._re_que_lt()

        # 提取得到self.ans_ul
        self.ans_ul = re.findall(r'<ulclass="[\w\W]+?</ul>', text)  # 答案列表

    def _re_que_lt(self):
        # self.que_lt[i][0]是题型,self.que_lt[i][1]是问题
        for i in range(0, len(self.que_lt)):
            self.que_lt[i] = list(self.que_lt[i])
            self.que_lt[i][1] = re.sub(r'<.+?>', '', self.que_lt[i][1])
            self.que_lt[i][1] = re.sub(r'[(](.*?)[)]', '()', self.que_lt[i][1])
            self.que_lt[i][1] = re.sub(r'&nbsp;', '', self.que_lt[i][1])
            self.que_lt[i][1] = re.sub(r'\uff08(.*?)\uff09', '', self.que_lt[i][1])
            self.que_lt[i][0] = re.sub(r' \t\n', '', self.que_lt[i][0])


def test():
    infodic = {
        'question': 'question',
        'type': 'type'
    }
    QA = QueryAns('course_name', **infodic)
    print(QA.work())

if __name__ == "__main__":
    test()
