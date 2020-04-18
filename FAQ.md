# FAQ

## How to run (v2.0)

- 新增**模式选择**：`-m(--mode)`   默认single模式

  - `single`:      单课程自动模式——选择课程,自动完成该课程(默认启动参数，可不填写)
  - `fullauto`:  全自动模式——自动遍历全部课程,无需输入
  - `control`:    单课程控制模式——选择课程并选择控制章节,自动完成选定章节前的任务点

- 新增**视频倍速**：`-r(--rate)`   默认1倍速

  - [0.625,16]​   全局倍速设置——在选定模式的全局范围内开启该倍速

- 实例：

  ![image-20200403014324816](D:\文档\音视频图片\照片图片\typoraphoto\FAQ\image-20200403014324816.png)



## About chrome&chromedriver

- 要把`chromedriver.exe`放在**source_code目录**下

- 需要注意的是版本要对应：chromedriverV2.9之前的版本可以进notes.txt查看对应chrome版本，之后的70及以上到80都是直接和chrome对应的

- **版本号前三个数应一致，第四个可以更换着尝试**

- 附：已经测试过的可以正常运行的版本对应关系：

| chrome | chromedriver |
| ------ | ------------ |
| 80.0.3987.132/149 | 80.0.3987.106 |
| 76.0.3809.132 | 76.0.3809.126 |



## About login info

- 在`logindata_phone.txt或logindata.txt`中按提示填写登录信息，并把提示信息删除

  - `logindata.txt:`——[其实就是这里的登录信息](https://passport2.chaoxing.com/login?refer=http://i.mooc.chaoxing.com)
    - 第一行填写机构**全称**
    - 第二行填写手机号或学号
    - 第三行填写登录密码
  - `logindata_phone.txt:`——[这个的登录信息在这里](https://passport2.chaoxing.com/wlogin)
    - 第一行填写手机号
    - 第二行填写登录密码
  - 可填写多个账号，也可一个账号写多个（自己注意）

- **编码问题**：

  - 怎样判断是编码的问题？

    - 程序运行时会输出`check XXXXinfo: `，这个时候检查输出的信息是否带有特殊符号

  - txt需要是**utf-8编码**，若不是，可另存为->选择编码->覆盖原文件

  - 有的windows默认的utf-8编码其实是`utf-8 BOM`编码，如果是这种情况，可按如下方式修改`autocx.py`:

    ![image-20200403015518283](D:\文档\音视频图片\照片图片\typoraphoto\FAQ\image-20200403015518283.png)

    **怎样判断是带BOM的编码**：如果你的第一个check的信息最前面是个小方块，那很有可能是utf-8 BOM



## About Files after run

程序在运行一次后，可能会在当前目录下生成以下文件：

1. login_vercode.png：登录时需要输入的验证码图片，会自动弹出，记住验证码后关闭，在执行窗口填写即可(docker下直接显示在终端)**(手机登录方式不需要验证码)**
2. record.txt：题库文件，里面包含题目，选项，答案
3. ans_vercode.png：答章节测试题时需要确认提交的验证码**(几乎不会弹出)**



## About Docker

- 具体使用教程请[移步项目地址](https://hub.docker.com/r/kimjungwha/autocx)
- docker版的源码只有autocx.py与普通版不同，通过**进程之间的通信**实现了在**无界面单终端**下的**多开刷课**，用户需按序填写每个账号的信息 (fullauto模式不必输入) ，然后每个账号的sk将在后台进行
- 这样的模式导致的**交互性**远远不如有界面下的执行，用户需要在当前目录的`AccountInfo`目录下找到相应的账号文件查看sk过程及结果
- 当然，选用这种模式不仅成功实现了单终端无界面下的多开，更棒的是**不必担心ssh不稳定断开所带来的程序中断**，换句话说，只要您的服务器(or your pc)没有出现异常，sk将持续进行下去直到完成它的任务。



## About requests

- 在完成章节的测试的时候，会发送课程和题目信息到题库服务器
- 如果程序运行出现异常，会发送报错(traceback……error……)到我的服务器，以便更快地debug，来给大家提供更好的体验~~
- 可以检查`query_ans(type, question)`和`send_err(err_info)`函数来调整您发送的信息



## How to develop？

- 如果想知道代码做了些什么，可以在`source_code\login_courses.py`中第38行（查找`headless`所在行）前加`#`注释，再次运行会展示浏览器窗口

- 代码经过简单重构后已经 将功能封装，可以参照注释直接使用or开发

