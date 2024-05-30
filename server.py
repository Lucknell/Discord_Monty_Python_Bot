import os
import glob
import ffmpeg
import yt_dlp
import requests
import threading
import selenium.common.exceptions

from quart import Quart, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session
from discord.ext import ipc
from pymongo import MongoClient
from gpt4all import GPT4All

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
    return f'{guild["name"]} Jobs:\n{result}'

@app.route("/checkjobs/<int:guild_id>")
async def check_for_jobs(guild_id):
    threading.Thread(target=update_jobs, args=(guild_id,)).start()
    return f"Checks started for{guild_id} jobs "

@app.route("/donejobs/<int:guild_id>")
async def post_done_jobs(guild_id):
    response = await ipc_client.request("post_jobs")
    return response.response

@app.route("/checkaijobs/<int:guild_id>")
async def check_for_ai_jobs(guild_id):
    threading.Thread(target=update_ai_jobs, args=(guild_id,)).start()
    return f"Checks started for{guild_id} ai jobs"

@app.route("/doneaijobs/<int:guild_id>")
async def post_done_ai_jobs(guild_id):
    response = await ipc_client.request("post_ai_jobs")
    return response.response



def update_ai_jobs(guild_id: int):
    client = MongoClient("mongodb://192.168.1.107:27017/")
    for job in client.Monty.gen_text.find({"server": guild_id, "state":"new"}):
        prompt = job["question"]
        model = job["model"]
        temperature = job["temperature"]
        models = {"mistral":"mistral-7b-instruct-v0.1.Q4_0.gguf","wizardlm":"wizardlm-13b-v1.2.Q4_0.gguf","falcon":"gpt4all-falcon-newbpe-q4_0.gguf","mpt":"mpt-7b-chat-newbpe-q4_0.gguf"}
        file_path = os.path.join("/src/bot/models/", models[model])
        chat_model = GPT4All(file_path)
        with chat_model.chat_session():
            response = chat_model.generate(prompt=prompt, temp=temperature, n_predict=2048)
            update = {"$set": {"answer": response, "state":"Ready!"}}
            client.Monty.gen_text.update_one(job, update)
            x = requests.get(f"http://192.168.1.107:5101/doneaijobs/{guild_id}")
            print(x)


#https://stackoverflow.com/questions/70825704/getting-error-message-using-ffmpeg-python-null-000002486ae7b180-unable-to-f
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
    # https://trac.ffmpeg.org/wiki/Encode/H.264#twopass
    ffmpeg.output(i, os.devnull,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run()
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                  ).overwrite_output().run()

def fail_this_job(client, guild_id, job, reason):
    print (reason)
    update = {"$set": {"state":"Failed", "reason":reason}}
    client.Monty.downloader.update_one(job, update)

def update_jobs(guild_id: int):
    path = "/src/bot/down/"
    client = MongoClient("mongodb://192.168.1.107:27017/")
    new_jobs = False
    tweet = None
    if not os.path.exists(path):
        os.mkdir(path)
    for job in client.Monty.downloader.find({"server":guild_id, "state":"new"}):
        URL = job["URL"]
        new_jobs = True
        has_photo = False
        print(f"starting thread for {URL}")
        file_path = os.path.join(path, str(id(URL)))
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        ydl_opts = {
            'outtmpl' : file_path + '/%(id)s.%(ext)s',
            'format' : 'best[ext=mp4]'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                if "x.com"in URL:
                    URL = URL.replace("x.com", "twitter.com")
                info_dict = ydl.extract_info(URL, download=False)
                length = info_dict.get('duration_string', None)
                if length is None:
                    raise yt_dlp.utils.DownloadError("This is not a video")
                if len(length.split(":")) > 2:
                    reason = "Video was too long"
                    fail_this_job(client, guild_id, job, reason)
                    continue
                ydl.download([URL])
            except yt_dlp.utils.DownloadError as e:
                reason = f"Error in download:{e}"
                fail_this_job(client, guild_id, job, reason)
                x = requests.get(f"http://192.168.1.107:5101/donejobs/{guild_id}")
                print(x)
                continue
        for file in os.listdir(file_path):
            the_file = os.path.join(file_path, file)
            if ((os.path.getsize(the_file)/(1024*1024)) > 8):
                try:
                    compressed_file = os.path.join(file_path, f"compressed_{file}")
                    compress_video(the_file, compressed_file, 7800)
                except ffmpeg._run.Error:
                    reason = f"Could not compress file{file}"
                    fail_this_job(client, guild_id, job, reason)
                    continue
                if os.path.exists(the_file):
                    os.remove(the_file)
        the_file = os.listdir(file_path)
        update = {"$set": {"state":"Ready!","file": the_file, "path": file_path}}
        client.Monty.downloader.update_one(job, update)
        print(f"ending thread for {URL}")
        x = requests.get(f"http://192.168.1.107:5101/donejobs/{guild_id}")
        print(x)


if __name__ == "__main__":
    app.run(debug=True)
