from quart import Quart, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session
from discord.ext import ipc
from pymongo import MongoClient
from cogs.lucknell.insta_vid import insta_vid, InstaDownloadFailedError
from cogs.lucknell.reddit_vid import reddit_vid, RedditDownloadFailedError
from cogs.lucknell.tik_vid import tik_vid, TikTokDownloadFailedError
import os
import requests
import threading

app = Quart(__name__)
ipc_client = ipc.Client(secret_key = "theholygrail",)

app.secret_key = b"thisisatestofwill"
app.config["DISCORD_CLIENT_ID"] = 774527385843662858   # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = "futI50L3cASjvklzKyyxRv64qz1qqBDj"   # Discord client secret.
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
    return results

def update_jobs(guild_id: int):
    path = "/src/bot/down/"
    client = MongoClient("mongodb://192.168.1.107:27017/")
    new_jobs = False
    if not os.path.exists(path):
        os.mkdir(path)
    for i in client.Monty.downloader.find({"server":guild_id, "state":"new"}):
        URL = i["URL"]
        new_jobs = True
        print(f"starting thread for {URL}")
        if "v.redd.it" in URL or "reddit.com" in URL:
            try:
                reddit = reddit_vid(URL)
            except RedditDownloadFailedError:
                update = {"$set": {"state":"Failed to download"}}
                client.Monty.downloader.update_one(i, update)
                return
        elif "tiktok.com" in URL:
            try:
                tiktok = tik_vid(URL)
            except TikTokDownloadFailedError:
                update = {"$set": {"state":"Failed to download"}}
                client.Monty.downloader.update_one(i, update)
                return
        elif "instagram.com" in URL:
            try:
                ig = insta_vid()
                ig.insta_getvid(URL)
            except InstaDownloadFailedError:
                update = {"$set": {"state":"Failed to download"}}
                client.Monty.downloader.update_one(i, update)
                return
        files = os.listdir(path)
        update = {"$set": {"state":"Ready!","file": files[0]}}
        client.Monty.downloader.update_one(i, update)
        print(f"ending thread for {URL}")
    x = requests.get("http://192.168.1.107:5101/donejobs/"+str(guild_id))

if __name__ == "__main__":
    app.run(debug=True)
