# Share-Local-Music-Services（本地音乐分享）

**Share-Local-Music-Services** 是一款 Web 服务，旨在分享本地音乐文件。开发这个项目的主要原因是目前音流（音频服务）不支持分享功能，而我们希望能提供一个简单易用的方式来分享本地音乐。

## 特性

- **显示歌曲信息：** 可以显示歌曲的标题、专辑、艺术家、歌词和封面。
- **支持的播放格式：** 蛮多。
- **转码支持：** 对于浏览器不支持的格式，支持转码 在`/CONF/config.py` 中 `decoding_format = ['.xxx']` **重启**服务或docker即可 。
- **简单的共享功能：** 如果你已经有音流支持的音乐库，可以直接通过音流的界面点击按钮，将你的私人音乐分享给朋友。

## 动机
目前的私人音乐服务大部分都不支持（瞎猜的！反正**音流**不支持）分享服务。为了弥补这一点，**Share-Local-Music-Services** 提供了一个简单的方式，让用户可以分享和在线播放他们的本地音乐文件。


## 安装
### 使用 Docker 部署（推荐）

推荐通过 Docker 部署该服务，确保环境的统一性和部署的简便性。使用以下命令启动容器：

```bash
docker run -d \
-p 7890:7890 \
--name slms \
-v /opt/Music:/app/Music \
yyfoam/share-local-music-services:latest
```
- **```-p 7890:7890```**：将容器的 7890 端口映射到宿主机的 7890 端口。
- **```--name slms```**：为容器指定一个名称 slms。
- **```-v /opt/Music:/app/Music```**：将宿主机的音乐文件目录如 `/opt/Music` 映射到容器的 `/app/Music` 目录（程序不会对该目录有任何写的操作）
- **```yyfoam/share-local-music-services:latest```**：使用最新的镜像部署该服务。
## 手动部署
### 克隆本仓库：

```bash
git clone https://github.com/yyfoam/Share-Local-Music-Services.git
```
### 安装ffmpeg 
#### 在 Ubuntu/Debian 上安装 
```bash
sudo apt update
sudo apt install ffmpeg
ffmpeg -version
```
看到版本号就成功了。

### 安装依赖：
**python环境：3.9.18**
```bash
cd Share-Local-Music-Services
pip install -r requirements.txt
```
### 启动服务：
```bash
python app.py
```

## 使用方法
推荐用音流，里面有个api入口，配置好以后直接点击就行了。


## 一. 使用音流：
- **1.登陆到你自己的资料库后，依次进入 `设置` --> `自定义API` --> `歌曲详情接口`**
- **2.在`地址`栏中输入```http://localhost:7890/music_share_local``` localhost:7890改为你自己的地址**
- **3.```路径替换```栏中输入要替换的字符串```/emby/Music,/app/Music```。举例：音乐文件实际目录为本机的```/opt/Music```；我的emby是docker部署的，容器内音乐文件路径为 ```/emby/Music```；本项目也是docker部署的，容器内音乐文件路径为```/app/Music```；因为音流接入的是emby 所以**路径替换**需要填入 ```/emby/Music,/app/Music``` 里面这个```,```很重要哦！**

![音流配置说明](https://github.com/user-attachments/assets/d9c3cb12-c378-49b2-a5e1-e0984d2ab2b0)
- **配置好后随便点开一首歌曲 点击歌曲详情就能访问了！**
![歌曲详情](https://github.com/user-attachments/assets/a5cbdb6d-7dee-495e-bb36-d2c0773e193e)

## 二、URL访问：
- **在浏览器中访问 ```http://localhost:7890/music_share_local?path=/app/Music/xxx.mp3``` 来使用该服务。**
- **注意** 如果是**本地部署** `http://localhost:7890/music_share_local?path=` 后面直接写绝对路径就行了 如果是**docker部署** `path=` 后面应该为 `/app/Music` 开头。
- **ps:容器能直接访问到的文件路径就行**



## 支持的格式
- `.flac`
- `.wav`
- `.mp3`
- `.ape`
- `.m4a`
- `.dsf`
- `.ogg`
- `.aiff`
- `.opus`
- `.aac`
- `.aif`
- `.aifc`
- `.wma`
- `.adx`
- `.au`
- `.mp2`
- `.rm`
- `.oga`
- `.tta`
- `.voc`
- `.mka`
## 效果图
### qq分享效果
![qq分享](https://github.com/user-attachments/assets/a79e7561-71e7-46a9-9646-d7f3ee393af7)

### 移动端效果
![移动端1](https://github.com/user-attachments/assets/ce1f4324-1496-431e-bf8e-4228649b3942)
![移动端2](https://github.com/user-attachments/assets/55113024-55a0-4c48-b611-37766ace329d)

### web界面
![1](https://github.com/user-attachments/assets/b40a368c-25f7-4e1c-832e-d45150633a01)
![2](https://github.com/user-attachments/assets/d48ce095-5aab-41a0-b3a5-5aedfd5bcd9b)

### 其他设备界面
![手表](https://github.com/user-attachments/assets/69e689aa-5955-4878-9e01-823e30f38263)


