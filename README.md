# autochaoxing
无界面超星刷课脚本，通过selenium库+bs4库+正则处理，实现看视频+章节测试全自动，无需打开浏览器即可刷课

## 使用
- 安装chrome浏览器以及相对应的chromedriver，并**将chromedriver复制到该目录下**
    - [chrome浏览器下载地址](https://www.google.cn/chrome/)
    - [chromedriver下载地址](http://npm.taobao.org/mirrors/chromedriver/)或者[这里](http://chromedriver.storage.googleapis.com/index.html)
    - 一定要版本对应，chromedriverV2.9之前的版本可以进notes.txt查看对应chrome版本，之后的70及以上到80都是直接和chrome对应的，版本号前三个数要对应，第四个可以更换着尝试
    
- 附：已经测试过的可以正常运行的版本对应关系：

     |chrome | chromedriver |
     :-:|:-:
     |80.0.3987.132 | 80.0.3987.106|
     |76.0.3809.132 | 76.0.3809.126|
     
- 安装python3和pip，[python官网](https://www.python.org)

- 命令行执行`pip install selenium pillow requests beautifulsoup4`

- 在logindata.txt中填写登录信息
    - 第一行填写机构全称
    - 第二行填写手机号或学号
    - 第三行填写登录密码
    - [其实就是这里的登录信息](https://passport2.chaoxing.com/login?refer=http://i.mooc.chaoxing.com)
    - logindata.txt需要是utf-8编码，若不是，可另存为->选择编码->覆盖原文件
    
- `python autochaoxing.py`开始刷课

- *注意*：必须让autochaoxing.exe、logindata.txt和chromedriver.exe在**同一目录下**才可执行

- [**懒人通道**](https://github.com/Luoofan/autochaoxing/releases)：发布了win10x64下的打包程序，直接下载运行即可刷课+查题

## 功能支持

- [x] 几乎支持所有机构用户登录运行
- [x] 自动刷视频(包括页面内多视频)，静音播放，解决视频弹出的试题
- [x] 自动答章节测试题（单选、多选、判断）
- [x] **无浏览器界面**，只有控制台执行界面
- [x] 充分的**输出和日志记录**
- [x] *单一账号多开（需谨慎）*

## 写给愿意学习交流、开发以及遇到问题的小伙伴
- 如果想知道代码都做了些什么，可以在`autochaoxing.py`中第49行（查找`headless`所在行）前加`#`注释，再次运行会展示浏览器窗口
- 程序在运行一次后，会在当前目录下生成以下几个文件：
  1. login_vercode.png：登录时需要输入的验证码图片，会自动弹出，记住验证码后关闭，在执行窗口填写即可
  2. chaoxing.txt：日志记录（暂时先用写文件的方式记录日志）
  3. record.txt：题库文件，里面包含题目，选项，答案
  4. ans_vercode.png：答章节测试题时需要确认提交的验证码（这个图片只有在短时间内多次答章节测试题的情况下才会弹出）
- 如果程序运行中出现bug，异常退出，可以截图报错信息、查看chaoxing.txt记录，来与我们交流解决


## 暂不支持&ToDo
 - [ ] 非视频、章节测试的任务点
 - [ ] 自动考试
 - [ ] chrome外其他浏览器的适配

## 关于题库与考试
 - 题库是直接访问的前辈们维护的题库服务器；考试因为考虑到直接无界面完成会不放心，所以暂未提供支持，考试时可使用查题程序查题
 - 题库服务器来源：[js脚本刷课项目](https://github.com/CodFrm/cxmooc-tools),[greasyfork](https://greasyfork.org/zh-CN/scripts/369625-%E8%B6%85%E6%98%9F%E7%BD%91%E8%AF%BE%E5%8A%A9%E6%89%8B),十分感谢！

## 更新
 - 2020-3-9：
   - 修复了部分视频检测错误的bug、修复了有些页面无法打开视频页面和章节测试的bug
   - 新增了查题程序，分命令行执行和窗口执行两种，配套刷课脚本用来考试查询
   - 发布了win10x64下的打包程序(刷课+查题)，可直接运行exe开始刷课
- 2020-3-10：
  - 修复了部分页面无法获取课程的bug、修复了普通章节下的子章节无法获取的bug

## 写在最后

本脚本主要用来学习，之后会在博客里写一份详细的使用文档和编程过程中的记录总结，欢迎大家一起前来交流
（*QQ群:1075080181*）

