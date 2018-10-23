import youtube_dl
import os
import sys
import json
import shutil
from config import db_file, TOKEN
import telegram
from model import DB
import datetime
from mutagen.easyid3 import EasyID3
import re
from urllib.parse import urlparse, parse_qs


def my_hook(d):
    downloadMB = (int(float(d['downloaded_bytes']))/1048576)
    if d['status'] == 'finished':
        print('\nDone downloading, now converting ...')
    elif d['status'] == 'downloading':
        sys.stdout.write('\rdownloading {0:.2f} MB'.format(downloadMB))
        sys.stdout.flush()


def readJSON(file):
    with open(file) as f:
        data = json.load(f)
    return data


def parseInfoFile(file):
    data = readJSON(file)
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
    return {'performer': performer,
            'title': title}


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def tag_file(file, file_record):
    audio = EasyID3(file)
    audio["artist"] = file_record['performer']
    audio.save(file)


def get_url(url):
    url = re.findall(r'(https?://\S+)', url)[0]
    print(url)
    if url:
        url_id = get_id(url)
        print(url_id)
        return url, url_id
    raise Exception("no url found")


def get_id(url):
    u_pars = urlparse(url)
    quer_v = parse_qs(u_pars.query).get('v')
    if quer_v:
        return quer_v[0]
    pth = u_pars.path.split('/')
    if pth:
        return pth[-1]


class Controller:

    def __init__(self):
        self.db = DB()
        if not os.path.exists(db_file):
            os.mkdir(db_file)

    def user_exists(self, user_id, user_name):
        user = self.db.get_user(user_id)
        if not user:
            self.db.insert_user(user_id, user_name)
            return False
        return True

    def start(self, bot, update):
        user_id = update.message.chat_id
        user_name = update.message.from_user.first_name
        if self.user_exists(user_id, user_name):
            update.message.reply_text("Send me a valid Youtube URL: ")
        else:
            update.message.reply_text(
                "Wellcome {}.\nSend me a valid Youtube URL: ".format(user_name))

    def url_message(self, bot, update):
        chat_id = update.message.chat_id
        user_name = update.message.from_user.first_name
        self.user_exists(chat_id, user_name)
        dt = datetime.datetime.now().strftime("%s")
        out_file = db_file + str(chat_id) + dt
        info_file = out_file + '.info.json'

        try:
            url, url_id = get_url(update.message.text)
        except:
            bot.send_message(chat_id=chat_id,
                             text="Ups!\nSeems something went wrong while downloading the song\nCheck you sent me a valid youtube link")

        audio_file = self.db.get_file(url_id)
        if audio_file:
            file_record = audio_file
            self.db.update_record(url_id)
        else:
            ydl_opts = {
                'outtmpl': out_file + '.%(ext)s',
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
            message_info = bot.send_message(chat_id=chat_id,
                                            text='Downloading...',
                                            disable_notification='True')

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([url])
                except Exception as e:
                    print(str(e))
                    bot.editMessageText(chat_id=chat_id,
                                        message_id=message_info['message_id'],
                                        text="Ups!\nSeems something went wrong while downloading the song\nCheck you sent me a valid youtube link")

            out_file += '.mp3'
            data = parseInfoFile(info_file)
            file_record = {'_id': url_id,
                           'url': url,
                           'file_path': out_file,
                           'last_download': dt,
                           'download_count': 1,
                           **data}

            bot.editMessageText(chat_id=chat_id,
                                message_id=message_info['message_id'],
                                text='Sending...',
                                disable_notification='True')

        bot.send_chat_action(chat_id=chat_id,
                             action='record_audio',
                             timeout=10)
        tmp_send_file = db_file+file_record['title']+'.mp3'
        shutil.copyfile(file_record['file_path'], tmp_send_file)
        tag_file(tmp_send_file, file_record)

        bot.send_audio(chat_id=chat_id,
                       audio=open(tmp_send_file, 'rb'),
                       title=file_record['title'],
                       performer=file_record['performer'],
                       caption="Via -> @Jutubot",
                       timeout=1000)
        os.remove(tmp_send_file)
        if audio_file == None:
            bot.delete_message(chat_id=chat_id,
                               message_id=message_info['message_id'])
            os.remove(info_file)
        self.db.add_to_history(chat_id, file_record)
        try:
            self.db.insert_file_record(file_record)
        except:
            pass