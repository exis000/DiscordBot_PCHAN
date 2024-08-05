import discord
from discord.ext import commands
import asyncio
import datetime
import requests
from pprint import pprint
import json
import random
from bs4 import BeautifulSoup as bs
import urllib.parse

from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("TOKEN") #discord BOT token

TENOR_KEY = os.getenv("TENOR_API_KEY") #TENOR API KEY
print(BOT_TOKEN)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

MMK_TORAM_ROLE = os.getenv("TORAM_ROLE")# TORAM ROLE CHANNEL IN MISCHIEF MAKERS SERVER


guild_list = {}
scheduler = AsyncIOScheduler()

async def aes_scheduler(ctx, schedule, hours, minutes, start_time):
    async def job(ctx = ctx):
        '''this function gets called '''
        Time_before_raid = schedule - datetime.datetime.now()
        print(Time_before_raid)
        raid_hours = Time_before_raid.seconds // 3600 #converts time to hours
        raid_minutes = (Time_before_raid.seconds % 3600) // 60 # converts time to minutes
        if datetime.datetime.now() >= schedule:
             await ctx.send(f'Guild Raid starting now! everyone gather at int 2 Guild Bar!!!')
             await ctx.send(f'{MMK_TORAM_ROLE}\n' * 3)
             guild_list.update({ctx.guild.id:False})
             scheduler.remove_all_jobs()
             
        else:
            if raid_hours <= 1 and raid_minutes == 0:
                await ctx.send(f'Raid starts in {raid_hours} hour and {raid_minutes} minute!! \n{MMK_TORAM_ROLE}\n{MMK_TORAM_ROLE}\n{MMK_TORAM_ROLE}')
            if raid_hours <= 1 and raid_minutes > 0:
                await ctx.send(f'Raid starts in {raid_hours} hour and {raid_minutes} minutes!! \n{MMK_TORAM_ROLE}\n{MMK_TORAM_ROLE}\n{MMK_TORAM_ROLE}')

            if raid_hours > 1 and raid_minutes == 0:
                await ctx.send(f'Raid starts in {raid_hours} hours and {raid_minutes} minute!! \n{MMK_TORAM_ROLE}\n{MMK_TORAM_ROLE}\n{MMK_TORAM_ROLE}')
                
            if raid_hours > 1 and raid_minutes > 0:
                await ctx.send(f'Raid starts in {raid_hours} hours and {raid_minutes} minutes!! \n{MMK_TORAM_ROLE}\n{MMK_TORAM_ROLE}\n{MMK_TORAM_ROLE}')

    time_list = []
    
    for hour in range(0, hours, 3):
        time_list.append(start_time + datetime.timedelta(hours=hour, seconds=-3))
        print(hour)

    for i in time_list:
        taskB = scheduler.add_job(job, next_run_time=i) #create job
    print(time_list)

    # Add a job that runs every 15 minutes during the last hour
    last_hour_schedule = schedule - datetime.timedelta(hours=1,seconds=1)
    
    for i in range(15, 60, 15):
        scheduler.add_job(job, next_run_time=last_hour_schedule + datetime.timedelta(minutes=i,seconds=-2))
        
        
    taskC = scheduler.add_job(job, next_run_time=last_hour_schedule)    
    taskA = scheduler.add_job(job, next_run_time=schedule)
    scheduler.start()  

@bot.command()
@commands.has_permissions(administrator=True)
async def raid(ctx, hours:int, minutes: int ):

    if ctx.guild.id in guild_list and guild_list[ctx.guild.id]:
        await ctx.send('Command is currently in use')
       
        return
    
    guild_list[ctx.guild.id] = True
    start_time = datetime.datetime.now()
    schedule = start_time + datetime.timedelta(hours=hours, minutes=minutes)
    if hours <= 1:
        await ctx.send(f'Raid starts in {hours} hour and {minutes} minutes!! \n{MMK_TORAM_ROLE}\n{MMK_TORAM_ROLE}\n{MMK_TORAM_ROLE}')
    else:
        await ctx.send(f"Raid starts in {hours} hours and {minutes} minutes!! \n{MMK_TORAM_ROLE}\n{MMK_TORAM_ROLE}\n{MMK_TORAM_ROLE}")
    
    await aes_scheduler(ctx, schedule, hours, minutes, start_time)

@bot.command()
@commands.has_permissions(administrator=True)
async def stopraid(ctx):
    try:
        scheduler.remove_all_jobs()
        scheduler.shutdown()
    except KeyError as SchedulerAlreadyRunningError:
        print(f"error {SchedulerAlreadyRunningError} catched")
        print(guild_list)
    finally:
        guild_list.update({ctx.guild.id:False})
        await ctx.send('Raid stopped')
        print(f"{guild_list}")

@bot.command()
async def rawr(ctx):
    # print(*(user_mentioned.id for user_mentioned in ctx.message.mentions), sep='\n')
    for user_mentioned in ctx.message.mentions:
    # Now we can use the .id attribute.
        print(f"{user_mentioned}'s ID is {user_mentioned.id}")
    
    await ctx.send(f'<@{user_mentioned.id}>'* 3)

@bot.command()
async def test(ctx):
    role = discord.utils.get(ctx.author.roles, name="toram") # Get the role
    if role in ctx.author.roles: # Check if the author has the role
        await ctx.send("you have the permission")
        await ctx.send(f"")
    else:
        await ctx.send("You do not have the permission.")



@bot.command()
async def love(ctx):

    
    await ctx.send(f"I LOVE SOPING SO MUSH")


@bot.command() 
async def gif(ctx, *message)->str : #type !gif (ur message) sends a gif 

    lmt = 8

    data = requests.get(
        f"https://g.tenor.com/v2/search?q={message}&key={TENOR_KEY}&limit={lmt}"
        )

    if data.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        top_8gifs = json.loads(data.content)
        gif = (top_8gifs["results"][random.randint(0,3)]["itemurl"])
        await ctx.send(gif)
        
    else:
        top_8gifs = None
        print("none")


@bot.command() 
async def leveling(ctx, lvl: int):
    # Fetch the leveling data
    req = requests.get(f"https://coryn.club/leveling.php?lv={lvl}")
    soup = bs(req.text, "html.parser")
    result = []

    # Parse the HTML to extract leveling data
    ror = soup.find("div", class_='table-grid item-leveling')

    for data in ror.find_all("div", class_="level-row"):
        level = data.find("div", class_="level-col-1").text.strip()
        boss_name = data.find("div", class_="level-col-2").text.strip()
        exp = data.find("div", class_="level-col-3").text.strip()

        result.append({"level": level, "boss": boss_name, "exp": exp})
    
    # Create an embed object
    embed = discord.Embed(title=f"Leveling Information for Level {lvl}", color=discord.Color.blue())
    
    # Add each result to the embed
    for item in result[0:6]:  # Limiting to the first 6 results
        embed.add_field(
            name=f"Level: {item['level']}",
            value=f"**Boss Name:** {item['boss']}\n**EXP:** {item['exp']}",
            inline=False
        )

    # Send the embed in the channel
    await ctx.send(embed=embed)



@bot.command()
async def item(ctx, *item) ->str:
    try:
        search = f"{' '.join(item)}"
        
        coryn_item = requests.get(f"https://coryn.club/item.php?name={search}")
        coryn_item.raise_for_status()  # Raise an exception for HTTP errors

        soup = bs(coryn_item.text, "html.parser")
        search_item = soup.find("div", id='content')

        if not search_item:
            await ctx.send(f"No results found for '{item}'.")
            return

        item_result = []
        card_containers = search_item.find_all("div", class_='card-container')

        for i, card in enumerate(card_containers):
            item_name = card.find("div", class_='card-title').text.strip()
            img = card.find("img")['src'] if card.find("img") else None
            basic_stats = card.find("div", class_='table-grid item-basestat')

            if basic_stats:
                # Clean up the basic stats text
                clean_basic_stats = ' '.join(basic_stats.text.split()).strip()
            else:
                clean_basic_stats = None

            item_result.append({
                'name': item_name,
                'image': img,
                'basic_stats': clean_basic_stats
            })

        if not item_result:
            await ctx.send(f"No items found for '{item}'.")
            return

        
        for it in item_result:
            embed = discord.Embed(title=it['name'], description=it['basic_stats'], color=discord.Color.blue())
            embed.set_thumbnail(url=it['image'])  # Set the image as the embed's thumbnail

            await ctx.send(embed=embed)
            
    except requests.exceptions.RequestException as e:
        await ctx.send("An error occurred while trying to retrieve the item. Please try again later.")
        print(e)





@bot.command()
async def test2(ctx):
    await ctx.send("TEST SUCCESS!")







if __name__ == "__main__":
    bot.run(BOT_TOKEN)
        
    