from urllib.parse import quote
from requests import post
from ast import literal_eval
from re import sub
lt = [x for x in range(0, 10)]
# lt.append('(')
lt.extend(['(', ')', '?'])
course_name = input("请输入课程名字:")
course = quote(course_name)
data = {'course': course, 'type': '0', 'option': ''}
headers = {
    'Host': 'mooc.forestpolice.org',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
    'Content-type': 'application/x-www-form-urlencoded',
    'Connection': 'keep-alive'
}
while 1:
    question = input("请输入问题:")
    question = sub(r'[\u3010\u4e00-\u9fa5]+?\u3011', '', question)
    question = sub(r'<.+?>', '', question)
    # question=re.sub(r'[(](.*?)[)]','',question)
    question = sub(r'\uff08(.*?)\uff09', '', question)
    # print(question)
    goal = 'http://mooc.forestpolice.org/cx/0/'
    for c in question:
        if c in lt:
            goal += c
        else:
            goal += quote(c)
    # print(goal)
    timeout = 10
    r = post(goal, data, headers=headers, timeout=timeout)
    status = r.status_code  # int
    # 200 且 code=1 响应成功
    # 200 且 code！=1 服务器繁忙
    # 403 请求过于频繁
    # 其他 服务器异常
    if status == 200:
        res = literal_eval(r.text)
        if res['code'] == 1:
            #print('响应成功')
            print(res['data'])
        else:
            print('未找到答案')
    elif status == 403:
        print('操作过于频繁')
    else:
        print('服务器异常')
