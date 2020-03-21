# autochaoxing

无界面超星刷课脚本，通过selenium库+bs4库+正则处理，实现看视频+章节测试全自动，无需打开浏览器即可刷课



## 使用

- 安装chrome浏览器以及相对应的chromedriver，并**将chromedriver复制到该目录下**
  - [chrome浏览器下载地址](https://www.google.cn/chrome/)
  - [chromedriver下载地址](http://npm.taobao.org/mirrors/chromedriver/)或者[这里](http://chromedriver.storage.googleapis.com/index.html)
  - 一定要版本对应，chromedriverV2.9之前的版本可以进notes.txt查看对应chrome版本，之后的70及以上到80都是直接和chrome对应的，版本号前三个数要对应，第四个可以更换着尝试
- 安装python3和pip，[python官网](https://www.python.org)
- 命令行执行`pip install selenium pillow requests beautifulsoup4`
- 在logindata.txt中填写登录信息——[其实就是这里的登录信息](https://passport2.chaoxing.com/login?refer=http://i.mooc.chaoxing.com)
  - 第一行填写机构全称
  - 第二行填写手机号或学号
  - 第三行填写登录密码
  - logindata.txt需要是utf-8编码，若不是，可另存为->选择编码->覆盖原文件
- `python autochaoxing.py`开始刷课
- [**懒人通道**](https://github.com/Luoofan/autochaoxing/releases)：发布了win10x64下的打包程序，直接下载运行即可刷课
- PS：**Linux用户**可以配环境运行py，也可以使用**docker⬇⬇⬇**(特别是无图形界面的用户)



## 关于autocx(Docker)

autocx是autochaoxing的**Docker**版本，主要由[KimJungWha](https://github.com/KimJungWha)制作了这个开箱即用的镜像

### 当您pull镜像后，只需进行以下几步：

- 以特权模式运行容器  
  `docker run -it --name autocx --privileged kimjungwha/autocx bash`
- 按照提示修改logindata.txt里的信息   
  `vim logindata.txt`
- 运行脚本  
  `python3 autocx_docker.py`

详细信息请见README_docker.md 或者[移步项目地址](https://hub.docker.com/r/kimjungwha/autocx)



## 功能支持

- [x] 几乎支持所有机构用户登录运行
- [x] 自动刷视频(包括页面内多视频)，静音播放，解决视频弹出的试题
- [x] 自动答章节测试题（单选、多选、判断）
- [x] **无浏览器界面**，只有控制台执行界面
- [x] 充分的**输出和日志记录**
- [x] *单一账号多开、多账号多开（需谨慎）*



## 写给愿意学习交流、开发以及遇到问题的小伙伴

- 程序在运行一次后，会在当前目录下生成以下几个文件：
  1. login_vercode.png：登录时需要输入的验证码图片，会自动弹出，记住验证码后关闭，在执行窗口填写即可(docker下直接显示在终端)
  2. chaoxing.txt：日志记录（暂时先用写文件的方式记录日志）
  3. record.txt：题库文件，里面包含题目，选项，答案
  4. ans_vercode.png：答章节测试题时需要确认提交的验证码（这个图片只有在短时间内多次答章节测试题的情况下才会弹出）
- 如果程序运行中出现bug，异常退出，可以截图报错信息、查看chaoxing.txt记录，来与我们交流解决




## 暂不支持&ToDo

 - [ ] 非视频、章节测试的任务点
 - [ ] 自动考试
 - [ ] chrome外其他浏览器的适配
 - [ ] 自动填写登录验证码
 - [ ] ~~多账号多开~~（初步完成）



## 关于题库与考试

 - 题库是直接访问的前辈维护的题库服务器；考试因为考虑到直接无界面完成会不放心，所以暂未提供支持，考试时可参考record.txt或者使用**查题程序**，当然你也可以来[这里get查题软件](https://github.com/yanyongyu/CXmoocSearchTool)或者直接使用以下的脚本
 - 题库服务器来源：[js脚本刷课项目](https://github.com/CodFrm/cxmooc-tools),[greasyfork](https://greasyfork.org/zh-CN/scripts/369625-%E8%B6%85%E6%98%9F%E7%BD%91%E8%AF%BE%E5%8A%A9%E6%89%8B),十分感谢！



## 更新

- 2020-3-21：

- 添加了分支**multi_autocx**，可以方便地**多开**刷课（同ip）
  - 在`logindata.txt`中每三行填写一份账户信息
  - 运行`python multi_autocx.py`按提示操作即可

  - 更改了登录和获取课程的模式，**减少了等待时间**，原来的模式保留作为备用方案
  - 修复了其他任务点影响视频任务点无法执行的bug，修复了部分视频无法获取的bug

- 2020-3-16:

- 由[KimJungWha](https://github.com/KimJungWha)制作了**Docker版本**，并发布到了[DockerHub](https://hub.docker.com/r/kimjungwha/autocx)

- 2020-3-15：
  - 增加了短时间内多次答题的时间限制，**减少答题验证码的弹出**
  - 修复了部分未完成任务点无法获取的bug
  - 新增了在**无图形界面的linux终端**下运行的脚本，需要工作目录下有`viu`，[viu:终端显示图片](https://github.com/atanunq/viu)
  - 发布了win10x64下的打包程序1.2

- 2020-3-13：

- 新增了**查题程序**，使用的服务器与脚本自动答题所使用的不同，可以在题目输入不完整时搜索答案，但不能保证服务器始终有效

- 2020-3-11：
  - **规范了查题接口的使用**
  - 删去了查题程序，如果有查题需要可以移步*题库与考试下的链接*
  - 修复了程序在linux编码错误和执行路径错误的bug
  - 发布了win10x64下的打包程序1.1

- 2020-3-10：

  - 修复了部分页面无法获取课程的bug、修复了普通章节下的子章节无法获取的bug

- 2020-3-9：

  - 修复了部分视频检测错误的bug、修复了有些页面无法打开视频页面和章节测试的bug
  - 新增了查题程序，分命令行执行和窗口执行两种，配套刷课脚本用来考试查询
  - 发布了win10x64下的打包程序1.0，可直接运行exe开始刷课



## 写在最后

本脚本主要用来学习，欢迎大家一起前来交流（*QQ群:1075080181*）

