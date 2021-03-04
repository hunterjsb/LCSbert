import discord
from discord.ext import commands
import json
from lolseries import LCS, lcs_week
from datetime import datetime

with open('./secrets.json') as s:
    BOT_TOKEN = json.load(s)['BOT_TOKEN']
bot = commands.Bot(command_prefix='$')


@bot.command()
async def servers(ctx):
    c_servers = list(bot.guilds)
    await ctx.send(f"Connected on {str(len(c_servers))} servers:")
    await ctx.send('\n'.join(guild.name for guild in c_servers))


@bot.event  # readyuup
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f'Welcome to {lcs_week} of the LCS!'))
    print('- R E A D Y -')


@bot.command()
async def check(ctx, week=lcs_week):
    league = LCS()

    # GET AUTHOR
    author_name = ctx.author.name
    author_id = str(ctx.author.id)

    # INIT EMBED
    pasta = discord.Embed(title=f'LCS {week}',
                          description=f'*{author_name} predictions as of {datetime.now().strftime("%m/%d/%y")}*',
                          color=discord.Colour.gold())
    pasta.set_thumbnail(url="https://cdn.pandascore.co/images/league/image/4198/image.png")

    # GET SCHEDULE AND PREDICTIONS OR PRINT ERR
    p = league.get_predictions(author_id)
    if (type(p) != dict) or (week not in p):  # ERROR CATCHING
        await ctx.send('`ERROR 69:`    `NO PREDICTIONS`')
        return
    else:
        p = p[week]
    matches = league.get_matches('upcoming', week)

    # CONSTRUCT EMBED
    for i, match in enumerate(matches):
        guess = p[i].upper()
        pasta.add_field(name=match, value=guess)

    await ctx.send(embed=pasta)


@bot.command()
async def sched(ctx, week=lcs_week):
    league = LCS()

    # INIT EMBED
    pasta = discord.Embed(title=f'LCS {week}',
                          description=f'*schedule as of {datetime.now().strftime("%m/%d/%y")}*',
                          color=discord.Colour.gold())
    pasta.set_thumbnail(url="https://cdn.pandascore.co/images/league/image/4198/image.png")

    # CONSTRUCT EMBED - LABEL MATCHES BY DAY
    matches = league.get_matches('upcoming', week)
    for i, match in enumerate(matches):
        if i < 5:  # first five games are fri
            day = 'friday'
        elif i < 10:  # next five are sat
            day = 'saturday'
        else:  # the last five are sun
            day = 'sunday'
        pasta.add_field(name=match, value=f"{day}, game {i+1}")

    await ctx.send(embed=pasta)


@bot.command()
async def lcs(ctx, *args):
    league = LCS()
    # JUST SAVE THE STRING IN A FILE (VALIDATION IS DONE BY LCS OBJECT)

    author_id = str(ctx.author.id)
    league.predict(args, author_id)
    await ctx.send(lcs_week + ' predictions saved! Use $check to see them.')


@bot.command()
async def record(ctx):
    league = LCS()

    # GET AUTHOR AND LOOK UP PREDICTIONS
    author_id = str(ctx.author.id)
    user_record = league.get_record(author_id)

    # CONSTRUCT EMBED FOR EACH WEEK
    pasta = discord.Embed()
    pasta.set_thumbnail(url=ctx.author.avatar_url)
    total_correct = 0  # counter variable
    for oc_week in user_record:  # ocs = outcomes
        ocs = user_record[oc_week]
        pasta.title = f'{ctx.author.name} Predictions for LCS {oc_week}'

        # oc[0] = GAME as STR 't1 vs t2'
        # oc[1] = WINNER as STR 't1' or 't2'
        # oc[3] = PREDICTION BOOL
        for oc in ocs:
            total_correct += oc[2]
            pasta.add_field(name=oc[0], value=f'winner: **{oc[1]}**\ncorrect? {oc[2]}')

        # CALCULATE THE WR AND SEND A MESSAGE
        weekly_percent = round(100*total_correct/len(ocs), 2)
        pasta.description = f'{weekly_percent}% CORRECT ({total_correct}/{len(ocs)})'
        await ctx.send(embed=pasta)

        # CLEAR THE EMBED & COUNTER
        pasta = discord.Embed()
        pasta.set_thumbnail(url=ctx.author.avatar_url)
        total_correct = 0


def run():
    bot.run(BOT_TOKEN)


if __name__ == "__main__":
    run()
