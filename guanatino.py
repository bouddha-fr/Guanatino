import discord, os
from discord.ext import commands, tasks
import yt_dlp as youtube_dl

TOKEN = os.getenv('')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='radio!', intents=intents)

ffmpeg_options = {
    'options': '-vn',
}

playlist = [
    "",
]

@bot.event
async def on_ready():
    print(f'{bot.user.name} est connecté.')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="radio!join"))
    play_next_song.start()

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Tu n'es pas dans un salon !")

def play_song(vc, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            vc.play(discord.FFmpegPCMAudio(url2, **ffmpeg_options), after=lambda e: print('done', e))
    except Exception as e:
        print(f"An error occurred while playing {url}: {e}")

@tasks.loop(seconds=5.0)
async def play_next_song():
    for guild in bot.guilds:
        vc = discord.utils.get(bot.voice_clients, guild=guild)
        if vc and not vc.is_playing():
            if len(playlist) > 0:
                url = playlist.pop(0)
                play_song(vc, url)
                playlist.append(url)

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)
