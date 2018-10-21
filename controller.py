import youtube_dl
import os
import sys
import json
import shutil
from config import tmp_file


def my_hook(d):
    downloadMB = (int(float(d['downloaded_bytes']))/1048576)
    if d['status'] == 'finished':
        print('\nDone downloading, now converting ...')
    elif d['status'] == 'downloading':
        sys.stdout.write('\rdownloading {0:.2f} MB'.format(downloadMB))
        sys.stdout.flush()


def readJSON(file=''):
    with open(file) as f:
        data = json.load(f)
    return data


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


class Controller:

    def __init__(self):
        if not os.path.exists(tmp_file):
            os.mkdir(tmp_file)

    def start(self, bot, update):
        update.message.reply_text("Send me a valid Youtube URL: ")

    def url_message(self, bot, update):
        chat_id = update.message.chat_id
        file_name = str(chat_id)
        tmp_out_file = tmp_file + file_name
        info_file = tmp_file + file_name + '.info.json'
        url = update.message.text
        ydl_opts = {
            'outtmpl': tmp_out_file + '.%(ext)s',
            'writeinfojson': info_file,
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        tmp_out_file += '.mp3'
        data = readJSON(info_file)
        title = data['track']
        performer = data['artist']
        if not data['track']:
            tmp = data['title'].split('-')
            if len(tmp) == 2:
                title = tmp[1].strip()
                performer = tmp[0].strip()
            else:
                title = data['title']
                performer = None

        bot.send_audio(chat_id=chat_id, audio=open(tmp_out_file, 'rb'),
                       title=title, performer=performer, 
                       caption="Via -> @Jutubot", timeout=1000)
        os.remove(tmp_out_file)
        os.remove(info_file)
