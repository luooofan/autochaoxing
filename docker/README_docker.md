## 关于autocx

autocx是autochaoxing的Docker版本，是在作者[@Luoofan](https://github.com/Luoofan)老哥耐心的指导和帮助下，我们成功制作了这个开箱即用的镜像。[项目地址](https://hub.docker.com/r/kimjungwha/autocx)

### 当您pull镜像后，只需进行以下几步：

- 以特权模式运行容器  
  `docker run -it --name autocx --privileged kimjungwha/autocx bash`
- 按照提示修改logindata.txt里的信息   
  `vim logindata.txt`
- 运行脚本  
  `python3 autocx_docker.py`

### 关于镜像的详细说明：

&emsp;autocx镜像基于`debian:buster-slim` 只替换了网易源、添加了脚本运行所需的环境，其余均与官方保持一致。其中内置了sudo、vim，默认用户/密码均为autocx，默认workdir为/home/autocx/  
&emsp;因为内置了py3、chromium，还有我本人水平限制，目前的镜像足足700+M，随着脚本的更新，我会尽量使它变得更加完美小巧，同时也欢迎各位大佬来群里指导，吹水啊！

### 如果遇到问题：

1. 请检查容器是否以特权模式运行。
2. 检查容器内使用账户是否为autocx ( chromium默认禁止root用户运行)
3. 如果以上步骤均无法解决问题，请把workdir下chaoxing.txt反馈给[@Luoofan](https://github.com/Luoofan)老哥，帮助他排除bug



​																										**By:[KimJungWha](https://github.com/KimJungWha)**
