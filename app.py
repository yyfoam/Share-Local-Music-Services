import generate_config
from PIL import Image
from io import BytesIO
from mutagen import File
from mutagen.id3 import APIC
from mutagen.flac import FLAC
from datetime import timedelta
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggopus import OggOpus
from mutagen.oggvorbis import OggVorbis
from mutagen.apev2 import APEBinaryValue
from urllib.parse import urlparse, parse_qs
from mutagen.monkeysaudio import MonkeysAudio
from mutagen.asf import ASF, ASFByteArrayAttribute
from LOG.logger import set_log_level, log_info, log_warning, log_error
from LOG import logger
import hashlib, pytz, json, os, base64, mimetypes, subprocess, re, ffmpeg
from flask import Flask, request, send_file, send_from_directory, Response

generate_config.generate_config_file('CONF/config.py')
import CONF.config as config

set_log_level(config.log_level)

app = Flask(__name__)


logger.china_tz = pytz.timezone(config.china_tz)

@app.route('/music_share_local', defaults={'path': ''})
@app.route('/music_share_local/<path:path>')
def music_share_local(path):
    file_path_hx = request.args.get('path')
    if file_path_hx:
        if not os.path.isfile(file_path_hx):
            return "共享的链接已失效或不存在！", 504
    if path.startswith('static'):
        return send_from_directory('build/static', path)
    elif path.startswith('favicon.ico'):
        return send_from_directory('build', "favicon.ico")
    return send_from_directory('build', 'index.html')

@app.route('/music_share_local/static/<path:path>')
def music_share_local_serve_static_files(path):
    return send_from_directory('build/static', path)

@app.route('/music_local_api/')
def music_local_api():
    current_url = request.args.get('current_url')
    parsed_url = urlparse(current_url)
    query_params = parse_qs(parsed_url.query)
    file_path_hx = query_params.get('path', [None])[0]
    if not os.path.isfile(file_path_hx):
        return "共享的链接已失效或不存在！", 504
    file_types = os.path.splitext(file_path_hx)[1].lower()
    if file_types in config.ff_exclude_metadata:
        data = extract_metadata(file_path_hx)
    else:
        data = ffmpeg_get_audio_metadata(file_path_hx)
    if data.get('error'):
        return json.dumps(data, ensure_ascii=False), 504
    return json.dumps(data, ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/music_local_image/<string:path_base64>')
def music_local_image(path_base64):
    file_path = decode_hex_to_string(path_base64)
    file_types = os.path.splitext(file_path)[1].lower()
    try:
        if file_types in config.ff_exclude_img:
            image_data = get_cover_image(file_path)
        else:
            image_data = ffmpeg_extract_cover_image_binary(file_path)
        if image_data:
            with open("debug_image.jpg", "wb") as img_file:
                img_file.write(image_data)
            img_io = BytesIO(image_data)
            img_io.seek(0)
            try:
                with Image.open(img_io) as img:
                    mime_type = f"image/{img.format.lower()}"
                    img_io.seek(0)
                    return send_file(img_io, mimetype=mime_type)
            except Exception as e:
                log_error(f"Error opening image: {file_path} - {e}")
                return send_file(config.folder, mimetype='image/jpeg')
        else:
            log_warning(f"No cover image found: {file_path}")
            return send_file(config.folder, mimetype='image/jpeg')
    except Exception as e:
        log_error(f"Failed to process the audio file: {file_path} - {e}")
        return send_file(config.folder, mimetype='image/jpeg')

@app.route('/music_local', methods=['GET'])
def music_local():
    file_path = request.args.get('path')
    if not file_path or not os.path.isfile(file_path):
        return "文件不存在", 404
    file_extension = os.path.splitext(file_path)[1].lower()
    supported_formats = config.decoding_format
    if file_extension in supported_formats:
        return stream_transcoded_audio(file_path)
    return send_audio_with_range_support(file_path)

def send_audio_with_range_support(file_path):
    file_size = os.path.getsize(file_path)
    range_header = request.headers.get('Range')
    if range_header:
        byte_range = range_header.replace('bytes=', '').split('-')
        start = int(byte_range[0])
        end = int(byte_range[1]) if byte_range[1] else file_size - 1
        length = end - start + 1
        with open(file_path, 'rb') as f:
            f.seek(start)
            data = f.read(length)
        response = Response(data, 206, mimetype=mimetypes.guess_type(file_path)[0])
        response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
    else:
        with open(file_path, 'rb') as f:
            data = f.read()
        response = Response(data, 200, mimetype=mimetypes.guess_type(file_path)[0])
    response.headers.add('Accept-Ranges', 'bytes')
    return response

def stream_transcoded_audio(file_path):
    temp_file = get_cache_filename(file_path)
    if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
        cache_file = temp_file
        log_info(f'使用缓存播放：{file_path} --> /{cache_file}')
        return send_file(cache_file, as_attachment=False)
    log_info(f'开始转码：{file_path}')
    command = [
        'ffmpeg',
        '-i', file_path,
        '-f', 'mp3',
        '-vn',
        '-acodec', 'libmp3lame',
        '-b:a', '320k',
        '-threads', '0',
        '-preset', 'ultrafast',
        '-y',
        temp_file
    ]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        log_error(f"ffmpeg error: {e.stderr.decode()}")
        return "转码失败", 500
    if not os.path.exists(temp_file):
        log_error(f"临时文件 {temp_file} 未生成！")
        return "转码失败", 500

    return send_file(temp_file, as_attachment=False)

def extract_metadata(file_path):
    file_type = os.path.splitext(file_path)[1].upper()[1::]
    if not os.path.isfile(file_path):
        return {"error": "文件路径无效"}
    try:
        audio_file = File(file_path)
    except Exception:
        title = '未识别到'
        album = ''
        artist = ''
        lyrics = '[00:00.00]没有找到歌词信息'
        return create_playlist(file_type, title, album, artist, lyrics, get_audio_duration(file_path), file_path)
    if not audio_file:
        title = '未识别到'
        album = ''
        artist = ''
        lyrics = '[00:00.00]没有找到歌词信息'
        return create_playlist(file_type, title, album, artist, lyrics, get_audio_duration(file_path), file_path)

    metadata = audio_file.tags
    if isinstance(audio_file, FLAC):
        title = metadata.get('title')[0] if metadata.get('title') else ''
        album = metadata.get('album')[0] if metadata.get('album') else ''
        artist = metadata.get('artist')[0] if metadata.get('artist') else ''
        lyrics = metadata.get('lyrics')[0] if metadata.get('lyrics') else ''
    elif isinstance(audio_file, MonkeysAudio):
        title = metadata.get('TITLE')
        album = metadata.get('ALBUM')
        artist = metadata.get('ARTIST')
        lyrics = metadata.get('UNSYNCEDLYRICS')
    elif isinstance(audio_file, MP4):
        title = ''.join(metadata.get('©nam'))
        album = ''.join(metadata.get('©alb'))
        artist = ''.join(metadata.get('©ART'))
        lyrics = ''.join(metadata.get('©lyr'))
    elif isinstance(audio_file, (OggVorbis, OggOpus)):
        title = ''.join(metadata.get('title'))
        album = ''.join(metadata.get('album'))
        artist = ''.join(metadata.get('artist'))
        lyrics = ''.join(metadata.get('lyrics'))
    elif isinstance(audio_file, ASF):
        title = metadata.get('title')[-1] if metadata.get('title') else ''
        album = metadata.get('WM/AlbumTitle')[-1] if metadata.get('WM/AlbumTitle') else ''
        artist = metadata.get('Author')[-1] if metadata.get('Author') else ''
        lyrics = metadata.get('WM/Lyrics')[-1] if metadata.get('WM/Lyrics') else ''
    else:
        try:
            title = metadata.get('TIT2')
            album = metadata.get('TALB')
            artist = metadata.get('TPE1')
            lyrics = next((value for key, value in metadata.items() if key.startswith('USLT::')), "[00:00.00]没有找到歌词信息")
        except Exception as e:
            log_error(f'未知错误，需要更新代码：{e}')
            return {"error": "需要更新代码"}

    if os.path.splitext(file_path)[1].lower() in config.decoding_format:
        file_type = f"{file_type}->🅳"
    return create_playlist(file_type, title, album, artist, lyrics, get_audio_duration(file_path), file_path)

def get_cover_image(file_path):
    audio = File(file_path)
    if isinstance(audio, FLAC):
        for picture in audio.pictures:
            if picture.type == 3:
                return picture.data
    elif isinstance(audio, (OggVorbis, OggOpus)):
        img = audio.get("metadata_block_picture")
        try:
            img = base64.b64decode(img[0])
            img = img[42::]
        except Exception:
            img = None
        return img
    elif isinstance(audio, MP4):
        for tag in audio.tags.values():
            if isinstance(tag[0], MP4Cover):
                return tag[0]
    elif isinstance(audio, MonkeysAudio):
        for tag in audio.tags.values():
            if isinstance(tag, APEBinaryValue):
                text_bytes = b"Cover Art (Front).jpg"
                start_pos = tag.value.find(text_bytes)
                if start_pos != -1:
                    image_data = tag.value[:start_pos] + tag.value[start_pos + len(text_bytes) + 1:]
                else:
                    image_data = tag.value
                return image_data
    elif isinstance(audio, ASF):
        for tag in audio.tags.values():
            if isinstance(tag[0], ASFByteArrayAttribute):
                img = tag[0].value
                if img:
                    img = img[29::]
                    return img
    else:
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                return tag.data
    return None

def get_audio_duration(file_path):
    try:
        audio = File(file_path)
        if audio is not None and hasattr(audio, 'info'):
            duration = audio.info.length - 1
            return duration
    except Exception as e:
        log_warning(f"Error reading audio file: {e}")
    return 0

def create_playlist(_type, _title, _album, _artist, _lyrics, _duration, file_path):
    file_path_base64 = encode_string_to_hex(file_path)
    return {
        "Playlist": {
            "MusicShare": [{
                "url": f"/music_local?path={file_path}",
                "type": _type,
                "artist": str(_artist),
                "title": str(_title),
                "lyrics": str(_lyrics),
                "cover": f"/music_local_image/{file_path_base64}",
                "album": str(_album),
                "id": 1,
                "duration": _duration
            }]
        }
    }

def ffmpeg_get_audio_metadata(file_path):
    file_type = os.path.splitext(file_path)[1].upper()[1::]
    probe = ffmpeg.probe(file_path)
    audio_streams = probe.get('streams', {})
    format_info = probe.get('format', {})
    tags = format_info.get("tags")
    title, album, artist, lyrics, duration = os.path.splitext(os.path.basename(file_path))[0], '', '', '', 0
    if len(audio_streams) > 0:
        audio_stream_ = audio_streams[0]
        time_base = audio_stream_.get('time_base')
        duration_ts = audio_stream_.get('duration_ts')
        if tags:
            items = tags
        else:
            items = audio_stream_.get('tags')
        numerator, denominator = map(int, time_base.split('/'))
        try:
            duration = int(duration_ts * (numerator / denominator))
        except TypeError:
            duration = ''
            tags = audio_stream_.get('tags')
            if tags:
                for k, v in tags.items():
                    if k.lower().startswith('duration'):
                        duration = v
            if duration:
                hours, minutes, seconds_with_nanos = duration.split(':')
                seconds, nanoseconds = map(int, seconds_with_nanos.split('.'))
                time_obj = timedelta(hours=int(hours), minutes=int(minutes), seconds=seconds,
                                     microseconds=nanoseconds // 1000)
                duration = time_obj.total_seconds()
        if items:
            for key, value in items.items():
                if key.lower().startswith('title'):
                    title = value
                elif key.lower().startswith('album'):
                    album = value
                elif key.lower().startswith('artist'):
                    artist = value
                elif key.lower().startswith('lyrics') or key.lower().startswith('unsyncedlyrics'):
                    lyrics = value

    if os.path.splitext(file_path)[1].lower() in config.decoding_format:
        file_type = f"{file_type}->🅳"
    return create_playlist(file_type, title, album, artist, lyrics, duration, file_path)

def ffmpeg_extract_cover_image_binary(file_path):
    probe = ffmpeg.probe(file_path)
    for stream in probe['streams']:
        if stream['codec_type'] == 'video' and stream.get('disposition', {}).get('attached_pic') == 1:
            out, _ = (
                ffmpeg
                    .input(file_path)
                    .output('pipe:', format='mjpeg', vframes=1)
                    .run(capture_stdout=True, capture_stderr=True)
            )
            return out
    return None

def encode_string_to_hex(str_ing):
    bytes_object = str_ing.encode('utf-8')
    base64_encoded = base64.b64encode(bytes_object)
    return base64_encoded.hex()

def decode_hex_to_string(hex_string):
    base64_bytes = bytes.fromhex(hex_string)
    original_bytes = base64.b64decode(base64_bytes)
    return original_bytes.decode('utf-8')

def string_to_md5(input_string):
    return hashlib.md5(input_string.encode('utf-8')).hexdigest()

def get_cache_filename(file_path):
    file_hash = string_to_md5(file_path)
    return os.path.join(config.CACHE_DIR, f"{file_hash}.mp3")

def extract_base_url(url):
    pattern = r'^(https?://[^/]+)'
    match = re.match(pattern, url)
    if match:
        return match.group(1)
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7890, debug=False)
