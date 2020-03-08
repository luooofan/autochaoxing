from urllib.parse import quote
from requests import post
from ast import literal_eval
from re import sub
import tkinter as tk
from time import sleep
lt = [x for x in range(0, 10)]
lt.extend(['(', ')', '?'])
headers = {
    'Host': 'mooc.forestpolice.org',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
    'Content-type': 'application/x-www-form-urlencoded',
    'Connection': 'keep-alive'
}
#实例化，创建窗口
window = tk.Tk()
window.title('SearchAns')
window.geometry('500x170')  # 设定窗口大小
l_course = tk.Label(window, text='课程:', font=('Arial', 12), width=5, height=1)
l_course.place(x=10, y=17)
e_course = tk.Entry(window, show=None, font=('Arial', 12), width=45)
e_course.place(x=70, y=20)
l_que = tk.Label(window, text='题目:', font=('Arial', 12), width=5, height=2)
l_que.place(x=10, y=47)
#e_question = tk.Entry(window, show=None, font=('Arial', 12),width=45)
#e_question.place(x=70,y=58)
t_que = tk.Text(window, font=('Arial', 12), width=35, height=2)
t_que.place(x=70, y=58)

l_ans = tk.Label(window, text='结果:', font=('Arial', 12), width=5, height=2)
l_ans.place(x=10, y=100)
var = tk.StringVar()
l_res = tk.Label(window, textvariable=var, font=('Arial', 12), width=45, height=2)
l_res.place(x=70, y=100)


def quiry_ans(ev=None):
    global var
    course_name = sub(r'[ \t\n]', '', e_course.get())
    course = quote(course_name)
    data = {'course': course, 'type': '0', 'option': ''}
    question = t_que.get('0.0', 'end')
    question = sub(r'[ \t\n]', '', question)
    question = sub(r'[\u3010\u4e00-\u9fa5]*?\u3011', '', question)
    question = sub(r'<.+?>', '', question)
    # question=re.sub(r'[(](.*?)[)]','',question)
    question = sub(r'\uff08(.*?)\uff09', '', question)
    goal = 'http://mooc.forestpolice.org/cx/0/'
    for c in question:
        if c in lt:
            goal += c
        else:
            goal += quote(c)
    # var.set(goal)
    timeout = 10
    r = post(goal, data, headers=headers, timeout=timeout)
    status = r.status_code  # int
    if status == 200:
        res = literal_eval(r.text)
        if res['code'] == 1:
            #var.set('响应成功')
            var.set(res['data'])
        else:
            var.set('未找到答案')
    elif status == 403:
        var.set('操作过于频繁')
    else:
        var.set('服务器异常')
    t_que.delete('1.0', 'end')


t_que.bind('<Return>', quiry_ans)
b = tk.Button(window, text='go', font=('Arial', 17), width=5, height=1, command=quiry_ans)
b.place(x=400, y=55)
window.mainloop()  # 主窗口循环展示
