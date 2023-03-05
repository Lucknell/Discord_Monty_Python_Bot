from quart import Quart, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session
from discord.ext import ipc
from pymongo import MongoClient
from cogs.lucknell.insta_vid import insta_vid, InstaDownloadFailedError
from cogs.lucknell.reddit_vid import reddit_vid, RedditDownloadFailedError
from cogs.lucknell.tik_vid import tik_vid, TikTokDownloadFailedError
from cogs.lucknell.tweet_vid2 import tweet_vid2, Tweet2DownloadFailedError
import selenium.common.exceptions
import os
import glob
import ffmpeg
import requests
import threading
import yt_dlp

app = Quart(__name__)
ipc_client = ipc.Client(secret_key = "theholygrail",)

app.secret_key = b"thisisatestofwill"
app.config["DISCORD_CLIENT_ID"] = os.getenv("CLIENT_ID")   # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("SECRET")   # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = "http://192.168.1.107:5101/callback"

discord = DiscordOAuth2Session(app)

@app.route("/")
async def home():
    return await render_template("index.html", authorized = await discord.authorized)

@app.route("/login")
async def login():
    return await discord.create_session()

@app.route("/callback")
async def callback():
    try:
        await discord.callback()
    except Exception:
        pass

    return redirect(url_for("dashboard"))

@app.route("/dashboard")
async def dashboard():
    if not await discord.authorized:
        return redirect(url_for("login"))

    guild_count = await ipc_client.request("get_guild_count")
    guild_ids = await ipc_client.request("get_guild_ids")

    user_guilds = await discord.fetch_guilds()

    guilds = []

    for guild in user_guilds:
        if guild.permissions.administrator:
            guild.class_color = "green-border" if guild.id in guild_ids else "red-border"
            guilds.append(guild)

    guilds.sort(key = lambda x: x.class_color == "red-border")
    name = (await discord.fetch_user()).name
    return await render_template("dashboard.html", guild_count = guild_count, guilds = guilds, username=name)

@app.route("/dashboard/<int:guild_id>")
async def dashboard_server(guild_id):
    if not await discord.authorized:
        return redirect(url_for("login"))

    guild = await ipc_client.request("get_guild", guild_id = guild_id)
    if guild is None:
        return redirect(f'https://discord.com/oauth2/authorize?&client_id={app.config["DISCORD_CLIENT_ID"]}&scope=bot&permissions=8&guild_id={guild_id}&response_type=code&redirect_uri={app.config["DISCORD_REDIRECT_URI"]}')
    client = MongoClient("mongodb://192.168.1.107:27017/")
    result =""
    for i in client.Monty.downloader.find({"server":guild_id}):
        result += str(i) +"\n"
    return guild["name"] +" Jobs:\n" + result

@app.route("/checkjobs/<int:guild_id>")
async def check_for_jobs(guild_id):
    threading.Thread(target=update_jobs, args=(guild_id,)).start()
    return f"Checks started for{guild_id} jobs "

@app.route("/donejobs/<int:guild_id>")
async def post_done_jobs(guild_id):
    results = await ipc_client.request("post_jobs")
    print (results)
    return results

def compress_video(video_full_path, output_file_name, target_size):
    # Reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    probe = ffmpeg.probe(video_full_path)
    # Video duration, in s.
    duration = float(probe['format']['duration'])
    # Audio bitrate, in bps.
    audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
    # Target total bitrate, in bps.
    target_total_bitrate = (target_size * 1024 * 8) / (1.073741824 * duration)

    # Target audio bitrate, in bps
    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate
    # Target video bitrate, in bps.
    video_bitrate = target_total_bitrate - audio_bitrate

    i = ffmpeg.input(video_full_path)
    ffmpeg.output(i, os.devnull,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run()
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                  ).overwrite_output().run()


def update_jobs(guild_id: int):
    path = "/src/bot/down/"
    client = MongoClient("mongodb://192.168.1.107:27017/")
    new_jobs = False
    tweet = None
    if not os.path.exists(path):
        os.mkdir(path)
    for i in client.Monty.downloader.find({"server":guild_id, "state":"new"}):
        URL = i["URL"]
        new_jobs = True
        has_photo = False
        print(f"starting thread for {URL}")
        if "v.redd.it" in URL or "reddit.com" in URL:
            try:
                reddit = reddit_vid(URL)
            except RedditDownloadFailedError:
                update = {"$set": {"state":"Failed to download"}}
                client.Monty.downloader.update_one(i, update)
                x = requests.get("http://192.168.1.107:5101/donejobs/"+str(guild_id))
                continue
        elif "tiktok.com" in URL:
            try:
                tiktok = tik_vid(URL)
            except TikTokDownloadFailedError:
                update = {"$set": {"state":"Failed to download"}}
                client.Monty.downloader.update_one(i, update)
                x = requests.get("http://192.168.1.107:5101/donejobs/"+str(guild_id))
                continue
        elif "instagram.com" in URL:
            try:
                ig = insta_vid()
                ig.insta_getvid(URL)
            except InstaDownloadFailedError:
                update = {"$set": {"state":"Failed to download"}}
                client.Monty.downloader.update_one(i, update)
                x = requests.get("http://192.168.1.107:5101/donejobs/"+str(guild_id))
                continue
        elif "twitter.com" in URL:
            is_video = True
            ydl_opts = {
                'outtmpl' : path + '%(id)s.%(ext)s',
                'format' : 'best[ext=mp4]'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    error = ydl.download([URL])
                except yt_dlp.utils.DownloadError:
                    is_video = False
            if not is_video:
                try:
                    tweet = tweet_vid2(URL)
                except (Tweet2DownloadFailedError, selenium.common.exceptions.WebDriverException):
                    update = {"$set": {"state":"Failed to download"}}
                    client.Monty.downloader.update_one(i, update)
                    x = requests.get("http://192.168.1.107:5101/donejobs/"+str(guild_id))
                    continue
        elif "youtube.com" in URL or "youtu.be" in URL:
            ydl_opts = {
                'outtmpl' : path + '%(id)s.%(ext)s',
                'format' : 'best[ext=mp4]'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(URL, download=False)
                    length = info_dict['duration_string']
                    error = 0
                    if len(length.split(":")) > 2:
                        print ("Video was too long")
                        error = 1
                    if error == 0:
                        error = ydl.download([URL])
                    if not error == 0:
                        update = {"$set": {"state":"Failed to download"}}
                        client.Monty.downloader.update_one(i, update)
                        x = requests.get("http://192.168.1.107:5101/donejobs/"+str(guild_id))
                        continue
        the_file = max(glob.iglob(path+'*'), key=os.path.getctime)
        while ".part" in the_file:
            os.remove(the_file)
            the_file = max(glob.iglob(path+'*'), key=os.path.getctime)
        print((os.path.getsize(the_file)/(1024*1024)))
        if ((os.path.getsize(the_file)/(1024*1024)) > 8):
            cfile = the_file.replace(path,"")
            compress_video(the_file, path+"compressed_"+cfile, 7800)
            if os.path.exists(the_file):
                os.remove(the_file)
            the_file =  path+"compressed_"+cfile
        if tweet and tweet.has_photo:
            has_photo = True
            the_file = os.listdir(path)
        update = {"$set": {"state":"Ready!","file": the_file, "pictures": has_photo}}
        client.Monty.downloader.update_one(i, update)
        print(f"ending thread for {URL}")
    x = requests.get("http://192.168.1.107:5101/donejobs/"+str(guild_id))
    print (x)

if __name__ == "__main__":
    app.run(debug=True)
