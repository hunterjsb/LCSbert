import discord
from discord.ext import commands
import json
from lolseries import LCS, lcs_week
from datetime import datetime

with open('./secrets.json') as s:
    BOT_TOKEN = json.load(s)['BOT_TOKEN']
bot = commands.Bot(command_prefix='$')


@bot.event  # readyuup
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f'Welcome to week 420 of the LCS!'))
    print('- R E A D Y -')


@bot.command()
async def logos(ctx):  # TODO MAKE FUNC UN LCSI INDEX BY SLUG
    with open('./assets/runningseries.json', 'r') as f:
        resp = json.load(f)

    for r in resp:
        await ctx.send(r['league']['image_url'])


@bot.command()
async def lcs(ctx, *args):
    league = LCS()
    author_id = str(ctx.author.id)
    league.predict(args, author_id)
    await ctx.send(lcs_week + ' predictions saved! Use $check to see them.')


@bot.command()
async def check(ctx):
    league = LCS()
    author_name = ctx.author.name
    author_id = str(ctx.author.id)

    # INIT EMBED
    pasta = discord.Embed(title=f'LCS {lcs_week}',
                          description=f'*{author_name} predictions as of {datetime.now().strftime("%m/%d/%y")}*',
                          color=discord.Colour.gold())
    pasta.set_thumbnail(url="https://cdn.pandascore.co/images/league/image/4198/image.png")

    # GET SCHEDULE AND PREDICTIONS
    p = league.get_predictions(author_id)[lcs_week]
    matches = league.next_week_matches()

    # CONSTRUCT EMBED
    for i, match in enumerate(matches):
        guess = p[i].upper()
        pasta.add_field(name=match, value=guess)

    await ctx.send(embed=pasta)


@bot.command()
async def sched(ctx):
    league = LCS()
    author_id = str(ctx.author.id)

    # INIT EMBED
    pasta = discord.Embed(title=f'LCS {lcs_week}',
                          description=f'*schedule, {datetime.now().strftime("%m/%d/%y")}*',
                          color=discord.Colour.gold())
    pasta.set_thumbnail(url="https://cdn.pandascore.co/images/league/image/4198/image.png")

    # GET SCHEDULE AND PREDICTIONS
    matches = league.next_week_matches()

    # CONSTRUCT EMBED
    for i, match in enumerate(matches):
        if i < 5:
            day = 'friday'
        elif i < 10:
            day = 'saturday'
        else:
            day = 'sunday'
        pasta.add_field(name=match, value=f"{day}, game {i+1}")

    await ctx.send(embed=pasta)


def run():
    bot.run(BOT_TOKEN)


if __name__ == "__main__":
    run()
