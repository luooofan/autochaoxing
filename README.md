# autochaoxing

无界面超星刷课脚本，通过selenium库+bs4库+正则处理，实现看视频+章节测试全自动，无需打开浏览器即可刷课（还支持多开哦:smile:）
<hr/><br/>

## 使用

- 安装chrome浏览器以及相对应的chromedriver，并**将chromedriver复制到source_code目录下**
    - [chrome浏览器下载地址](https://www.google.cn/chrome/)，[chromedriver下载地址](http://npm.taobao.org/mirrors/chromedriver/)或者[这里](http://chromedriver.storage.googleapis.com/index.html)，注意版本对应
- 安装python3和pip，[python官网](https://www.python.org)
- 安装依赖：命令行执行
    `pip install -r requirements.txt`
- 在**logindata_phone.txt**或**logindata.txt**中按提示填写登录信息，并把提示信息删除（推荐使用前者）
- 查看帮助信息 ，选择合适的参数开始刷课
    `python autocx.py -h`     
- 示例：以16倍速全自动模式运行脚本
    `python autocx.py -m fullauto -r 16`

- [懒人通道](https://github.com/Luoofan/autochaoxing/releases):win10x64环境下可直接使用打包的exe
- **Linux用户**可以配环境运行py，也可以使用**docker**:point_down:
- 如果有帮到你的话请赏颗:star:吧

<br/>

## 关于autocx(Docker)

autocx是autochaoxing的**Docker**版本，主要由[KimJungWha](https://github.com/KimJungWha)制作了这个开箱即用的镜像

#### 当您pull镜像后，只需进行以下几步：

- 以守护模式创建容器
  `docker run -id --name autocx kimjungwha/autocx bash`

- 进入容器
  `docker exec -it autocx bash`

- 按照提示修改logindata.txt或logindata_phone.txt里的信息 (并清空提示信息)
  `vim logindata_phone.txt`

- 运行脚本
  `python3 autocx.py`


详细信息和说明请[移步项目地址](https://hub.docker.com/r/kimjungwha/autocx)

<br/>

## 功能支持

- [x] **无浏览器界面**，只有控制台执行界面
- [x] 充分的**交互**
- [x] 支持所有机构用户登录运行
- [x] 自动刷视频(包括页面内多视频)，静音播放
- [x] 解决视频内弹出的试题
- [x] 自动答章节测试题（单选、多选、判断）
- [x] **多种模式：全自动，单课程自动，控制模式**
- [x] 支持倍速
- [x] ***多开***


<br/>

## 暂不支持&ToDo
 - [ ] 非视频、章节测试的任务点
 - [ ] 自动考试
 - [ ] chrome外其他浏览器的适配
 - [ ] ~~自动填写登录验证码~~（手机登录不需要填写）
 - [ ] ~~多账号多开~~（初步完成）

<br/>

## 如果想亲手写刷课脚本 或者遇到问题 可以先来[FAQ](https://github.com/Luoofan/autochaoxing/blob/master/FAQ.md)看看哦:blush:

<br/>

## 关于题库与考试

 - 题库是直接访问的前辈维护的题库服务器；考试因为考虑到直接无界面完成会不放心，所以暂未提供支持，考试时可参考record.txt或者使用**查题程序**，当然你也可以来[这里get查题软件](https://github.com/yanyongyu/CXmoocSearchTool)或者直接使用以下的脚本
 - 题库服务器来源：[js脚本刷课项目](https://github.com/CodFrm/cxmooc-tools),[greasyfork](https://greasyfork.org/zh-CN/scripts/369625-%E8%B6%85%E6%98%9F%E7%BD%91%E8%AF%BE%E5%8A%A9%E6%89%8B),十分感谢！

<br/>

## 更新

- 2020-4-7：

  - 上传2.0版win10x64打包程序,[通道](https://github.com/Luoofan/autochaoxing/releases)

- 2020-4-6：

  - **发布了Docker2.0版本**（有docker的小伙伴可以直接在docker里多开sk啦）

- **2020-4-2**：:star:

  - **发布了2.0版本**
  - 新增**模式选择**：`-m(--mode)`
    - `single`:      单课程自动模式——选择课程,自动完成该课程(默认启动参数，可不填写)
    - `fullauto`:  全自动模式——自动遍历全部课程,无需输入
    - `control`:    单课程控制模式——选择课程并选择控制章节,自动完成选定章节前的任务点
  - 新增**视频倍速**：`-r(--rate)`  默认1倍速
    - [0.625,16]   全局倍速设置——在选定模式的全局范围内开启该倍速
  - 代码简单**重构**，执行**优化**：将原有功能封装，想*亲自写脚本*的童鞋可以关注这点哦 :point_left:
  - 提高**容错率**(遇到未完成的任务点会暂时跳过,登录异常采用备用登录方案)
  - 更改原播放视频部分的模拟操作为js操作，提高程序运行稳定性
  - 可以通过 `-h(--help)`选项查看帮助信息，`-v(--version)`选项查看版本信息
  - 运行异常提交服务器—以便尽快debug
  - 分支合并到`master`，**执行文件更改为`autocx.py`** (以后只会增加参数，不会变更主执行文件)

  -------------------------------------------------------------------------------------------------------------------------------------

- 2020-3-22:
  - **multi_autocx**分支下新增了**手机号登录**模式，无需输入验证码即可登录，推荐使用该方式
  - 整理了项目文件结构，工作目录调整到**source_codes**
  - 修复了同页面内多项章节测试无法完成的bug、修复了输出信息颜色显示不稳定的bug
  
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

<br/>

## 写在最后

本脚本主要用来学习，欢迎大家前来一起交流:grinning:（*QQ群:1075080181*）

如果有帮到你的话请赏颗:star:吧