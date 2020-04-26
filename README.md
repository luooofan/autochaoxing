# autochaoxing

超星学习通无界面刷课脚本，通过selenium库+bs4库+正则处理，实现看视频+章节测试全自动，无需打开浏览器即可刷课（还有docker版本哦:smile:）
<hr/>

## 使用

**Windows**：

- 安装chrome浏览器以及相对应的chromedriver，并**将chromedriver复制到source_code目录下**
  
    - [chrome浏览器下载地址](https://www.google.cn/chrome/)，[chromedriver下载地址](http://npm.taobao.org/mirrors/chromedriver/)或者[这里](http://chromedriver.storage.googleapis.com/index.html)，注意版本对应
    
- 安装python3和pip，[python官网](https://www.python.org)

- 安装依赖：命令行执行<br/>
`pip install -r requirements.txt`
    
- 在**logindata_phone.txt**或**logindata.txt**中按提示填写登录信息，并把提示信息删除（推荐使用前者）

- 查看帮助信息 ，选择合适的参数开始刷课<br/>
  `python autocx.py -h`     
    
- 示例：以16倍速(-r)全自动模式(-m)运行脚本，并指定自动提交限制(-n)为2<br/>
`python autocx.py -m fullauto -r 16 -n 2`

- ~~[懒人通道](https://github.com/Luoofan/autochaoxing/releases):win10x64环境下可直接使用打包的exe~~（暂未更新到最新版）

**Linux**：可以配环境运行py，也可以使用**docker**:point_down:

**如果有帮到你的话请赏颗:star:吧**

<br/>

## 关于autocx(Docker)

autocx是autochaoxing的**Docker**版本，主要由[KimJungWha](https://github.com/KimJungWha)制作了这个开箱即用的镜像
详细信息和说明请[移步项目地址](https://hub.docker.com/r/kimjungwha/autocx)

<br/>

## 功能支持

- [x] **无浏览器界面**，只有控制台执行界面
- [x] 充分的**交互**
- [x] **多账号多开**
- [x] 支持所有机构用户登录运行
- [x] 自动刷视频(包括页面内**多视频**)，静音播放
- [x] 解决视频内弹出的试题（单选、多选）
- [x] 自动答章节测试题（**单选、多选、判断**）
- [x] **多种模式：全自动，单课程自动，控制模式**
- [x] **倍速**
- [x] 自定义查题API优先级
- [x] 自动提交限制

<br/>

## 暂不支持&ToDo

 - [ ] 非视频、章节测试的任务点
 - [ ] 自动考试
 - [ ] ~~自动填写登录验证码~~（手机登录不需要填写）
   之后会尝试写图像识别接口解决该问题

<br/>

## 如果想亲手写刷课脚本 或者遇到问题 可以先来[FAQ](https://github.com/Luoofan/autochaoxing/blob/master/FAQ.md)看看哦:blush:

遇到问题**请先查看FAQ是否有对应问题**，提issue时请附：**工作目录，运行情况，报错信息截图**，并尽可能描述准确、详细

<br/>

## 关于题库与考试

 - 考试因为考虑到直接无界面完成不放心，所以暂未提供支持，考试时可使用**查题程序**辅助

 - 原先的题库服务器来源于GreasyFork上**wyn大佬**，非常感谢！

 - 现在的题库接口源于多方，仍在增加中，在此也表示十分感谢！

<br/>


## 更新（**如果有帮到你的话请赏颗:star:吧**）

- 2020-4-24：

  - 新增**全局答题设置**选项`-n(--num)`  默认值为5
    - 可选值：0，1，2 ......
    - 自动答题时,如果 未找到答案的题目数量 达到num值,则暂时保存答案,不进行自动提交
  - 查题接口+1
  - 支持**自定义查题API优先级** more information please go to  [FAQ](https://github.com/Luoofan/autochaoxing/blob/master/FAQ.md)
  - 修复了遇到【非选择判断类】题目空提交的bug，改为跳过这类题目继续执行
  
- 2020-4-23：

  - 脚本答题功能恢复，请使用最新脚本（exe暂时仍无法使用）
  - **封装答题功能**，原来**单题库变为多题库**，答题正确率依赖于题库。
  
- 2020-4-18：

  - 题库服务器停止维护并暂时关闭，脚本目前将不再进行自动答题

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
  - **主执行文件更改为`autocx.py`** (以后只会增加参数，不会变更主执行文件)

  -------------------------------------------------------------------------------------------------------------------------------------

- 2020-3-22:

  - 整理了项目文件结构，工作目录调整到**source_codes**

- 2020-3-21：

  - 更改了登录和获取课程的模式，**减少了等待时间**，原来的模式保留作为备用方案

- 2020-3-16:
  
  - 由[KimJungWha](https://github.com/KimJungWha)制作了**Docker版本**，并发布到了[DockerHub](https://hub.docker.com/r/kimjungwha/autocx)
  
- 2020-3-15：
  - 增加了短时间内多次答题的时间限制，**减少答题验证码的弹出**
  - 新增了在**无图形界面的linux终端**下运行的脚本，需要工作目录下有`viu`，[viu:终端显示图片](https://github.com/atanunq/viu)
  
- 2020-3-5：

  - 发布1.0版本

<br/>

## 免责声明

autochaoxing为本人python学习交流的开源非营利项目，仅作为程序员之间相互学习交流之用，使用需严格遵守开源许可协议，严禁用于商业用途。个人或者组织，机构如果使用本项目产生的各类纠纷，法律问题，均由其本人承担。对一切非法使用所产生的后果，本人概不负责。
