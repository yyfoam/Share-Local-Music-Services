"""
目前测试可以播放的格式
'.flac', '.wav', '.mp3', '.ape', '.m4a', '.dsf', '.ogg', '.aiff', '.opus', '.aac',
'.aif','.aifc', '.wma', '.adx', '.au' ,'.caf', '.mp2', '.rm', '.oga', '.tta',
'.voc', '.mka'
"""

# 时区设置
china_tz = 'Asia/Shanghai'

# 设置缓存文件的目录
CACHE_DIR = "cache_dir"

ff_exclude_metadata = ['.wav', ]

ff_exclude_img = ['.wma', '.wav']

# 需要转码的格式
decoding_format = ['.ape', '.m4a', '.dsf', '.aiff', '.aif','.aifc', '.wma', '.adx', '.au' ,'.caf', '.mp2', '.rm', '.oga', '.tta', '.voc']


# 日志级别: DEBUG > INFO > WARNING > ERROR
log_level = 'INFO'

# 默认封面图像
folder = "folder.jpg"