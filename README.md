# Share-Local-Music-Services

**Share-Local-Music-Services** 是一款 Web 服务，旨在分享本地音乐文件。开发这个项目的主要原因是目前音流（音频服务）不支持分享功能，而我们希望能提供一个简单易用的方式来分享本地音乐。

## 特性

- **显示歌曲信息：** 可以显示歌曲的标题、专辑、艺术家、歌词和封面。
- **支持的播放格式：** 支持多种音频格式的在线播放，包括：
  - `.flac`, `.wav`, `.mp3`, `.ape`, `.m4a`, `.dsf`, `.ogg`, `.aiff`, `.opus`, `.aac`, `.aif`, `.aifc`, `.wma`, `.adx`, `.au`, `.mp2`, `.rm`, `.oga`, `.tta`, `.voc`, `.mka` 等。
- **转码支持：** 对于不支持的格式，提供转码播放功能。
- **简单的共享功能：** 如果你已经有音流支持的音乐库，可以直接通过音流的界面点击按钮，将你的音乐共享给朋友。

## 动机

音流是一个流行的音乐服务，但它缺乏本地音乐分享的功能。为了弥补这一点，**Share-Local-Music-Services** 提供了一个简单的方式，让用户可以分享和在线播放他们的本地音乐文件。

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
- **```-v /opt/Music:/app/Music```**：将宿主机的音乐文件目录 /opt/Music 映射到容器的 /app/Music 目录。
- **```yyfoam/share-local-music-services:latest```**：使用最新的镜像部署该服务。
## 手动部署
### 克隆本仓库：

```bash
git clone https://github.com/yourusername/Share-Local-Music-Services.git
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
```bash
cd Share-Local-Music-Services
pip install -r requirements.txt
```
### 启动服务：
```bash
python app.py
```
### 在浏览器中访问 ```http://localhost:7890/music_share_local?path=/app/Music/xxx.mp3``` 来使用该服务。

## 使用方法
### 启动服务后，您可以：

- **上传您的本地音乐文件。**
- **查看歌曲信息，包括封面、标题、艺术家、专辑和歌词。**
- **友好界面播放支持的格式的音乐。**
- **通过url与其他人共享您的音乐。**

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
# 界面截图
