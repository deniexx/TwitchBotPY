import re
from twitchio.ext import commands
import asyncio
import random

CHANNELS = ["#YourChannel"]  # channels that the bot will connect [must be list or tuple]
NICK = "NickOfBot"  # your bot channel username

bot = commands.Bot(
    irc_token="oauth:YourAuthToken",  # your oauth code
    client_id="YourClientId",  # your app id
    nick=NICK,
    prefix="!",  # command prefix
    initial_channels=CHANNELS
)

trustedUsers = []


async def intervalMessage(ws):
    for channel in CHANNELS:
        await ws.send_privmsg(channel, "You can grab your own MetcheBot source code from: https://github.com/deniexx/TwitchBotPY")
        await ws.send_privmsg(channel, "These messages can be customized")

    await asyncio.sleep(300)
    await intervalMessage(ws)


@bot.event
async def event_ready():
    print("Bot is ready")
    ws = bot._ws
    for channel in CHANNELS:
        await ws.send_privmsg(channel, "/me is coming to save the day")
        # message to send when he comes online

    await intervalMessage(ws)


@bot.event
async def event_message(ctx):
    if ctx.author.name.lower() == NICK:
        return

    await bot.handle_commands(ctx)

    # check if there is a link in the message
    match = re.search(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]"
                      r"+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>"
                      r"]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<"
                      r">]+|(\([^\s()<>]+\)))*\)|[^\s`!()"
                      r"\[\]{};:'\".,<>?«»“”‘’]))", ctx.content)

    if match and ctx.author.name\
            not in trustedUsers and not ctx.author.is_mod:

        await ctx.channel.timeout(ctx.author.name, 60, "link post")
        await ctx.channel.send(f"Don't post links @{ctx.author.name}")
        # times out people who post links


@bot.command(name="clear")
async def clear(ctx):
    if ctx.author.is_mod:
        await ctx.channel.clear()
        # clears the entire chat if the command is used by a moderator


@bot.command(name="ban")
async def ban(ctx, user=None, *args):
    if ctx.author.is_mod:
        if user and args:
            await ctx.channel.ban(user, " ".join(args))
            await ctx.send(f"@{user} has been banned for {' '.join(args)}")

        else:
            await ctx.send(f'@{ctx.author.name} -> !ban "user" "reason"')
            # bans a user if command is used by mod


@bot.command(name="unban")
async def unban(ctx, user):
    if ctx.author.is_mod:
        await ctx.channel.unban(user)
        # unbans user if command is used by mod


@bot.command(name="trust")
async def trust(ctx, user):
    if ctx.author.is_mod:
        trustedUsers.append(user)
        await ctx.send(f"@{user} is permitted to post links")
        # you can permit a user to post links if command is used by mod


@bot.command(name="untrust")
async def untrust(ctx, user):
    if ctx.author.is_mod:
        trustedUsers.remove(user)
        await ctx.send(f"@{user} is no longer permitted to post links")
        # you can remove the permission from the user if command is used by mod


@bot.command(name="winner")
async def getwinner(ctx):
    if ctx.author.is_mod:
        users = await bot.get_chatters(str(ctx.channel))
        await ctx.send(f"@{random.choice(users[1])} is the winner")
        # gets a list of all members and chooses 1 on random

bot.run()
