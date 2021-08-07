import discord
from discord.ext import commands, tasks
import auth
import datetime

# allow bot to access member list
intents = discord.Intents.default()
intents.members = True

# CONSTANTS
TOKEN = auth.token
bot = commands.Bot(command_prefix='!', intents=intents)
server_ids = ["697957942325936149"]
# after api v1.0 all IDs are int not str
god = 282973496559009792
team = [god]
test_channel = 868199419022041119

async def check_in(user):
    
    await user.send("Good morning! Time for check-in :sunny:")
    
    def check(message):
        return message.author in team
    
    msg = await bot.wait_for('message', check=check)
    await user.send(f"How do you feel today, {msg.author}?")
    # await user.send("What have you accomplished since yesterday?")
    # await user.send("What will you do today?")
    # await user.send("Anything blocking your progress?")

@bot.event
async def on_ready():
    for guild in bot.guilds:
        for member in guild.members:
            if member.id == god:
                await check_in(member)

    # user = await bot.fetch_user(god)
    # await user.send("hello")

@bot.command()
async def members(ctx):
    channel = bot.get_channel(test_channel)
    async for member in ctx.guild.fetch_members(limit=None):
        await channel.send(f"{member} --- {member.id}")


bot.run(TOKEN)