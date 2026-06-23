import discord
from discord.ext import commands
import requests
import urllib
import json
import math
from bs4 import BeautifulSoup
import asyncio


class PornHub(commands.Cog):
    """PornHub search cog for discord.py 2.x"""

    categories = [
        ["60fps", "video?c=105"],
        ["Amateur", "video?c=3"],
        ["Anal", "video?c=35"],
        ["Arab", "video?c=98"],
        ["Asian", "video?c=1"],
        ["Babe", "categories/babe"],
        ["Babysitter", "video?c=89"],
        ["BBW", "video?c=6"],
        ["Behind The Scenes", "video?c=141"],
        ["Big Ass", "video?c=4"],
        ["Big Dick", "video?c=7"],
        ["Big Tits", "video?c=8"],
        ["Bisexual", "video?c=76"],
        ["Blonde", "video?c=9"],
        ["Blowjob", "video?c=13"],
        ["Bondage", "video?c=10"],
        ["Brazilian", "video?c=102"],
        ["British", "video?c=96"],
        ["Brunette", "video?c=11"],
        ["Bukkake", "video?c=14"],
        ["Cartoon", "video?c=86"],
        ["Casting", "video?c=90"],
        ["Celebrity", "video?c=12"],
        ["College", "categories/college"],
        ["Compilation", "video?c=57"],
        ["Cosplay", "video?c=241"],
        ["Creampie", "video?c=15"],
        ["Cuckold", "video?c=242"],
        ["Cumshot", "video?c=16"],
        ["Czech", "video?c=100"],
        ["Described Video", "described-video"],
        ["Double Penetration", "video?c=72"],
        ["Ebony", "video?c=17"],
        ["Euro", "video?c=55"],
        ["Exclusive", "video?c=115"],
        ["Feet", "video?c=93"],
        ["Fetish", "video?c=18"],
        ["Fisting", "video?c=19"],
        ["For Women", "video?c=73"],
        ["French", "video?c=94"],
        ["Funny", "video?c=32"],
        ["Gangbang", "video?c=80"],
        ["Gay", "gayporn"],
        ["German", "video?c=95"],
        ["Handjob", "video?c=20"],
        ["Hardcore", "video?c=21"],
        ["HD Porn", "hd"],
        ["Henry", "video/search?search=henry"],
        ["Hentai", "categories/hentai"],
        ["Indian", "video?c=101"],
        ["Interracial", "video?c=25"],
        ["Italian", "video?c=97"],
        ["Japanese", "video?c=111"],
        ["Korean", "video?c=103"],
        ["Latina", "video?c=26"],
        ["Lesbian", "video?c=27"],
        ["Massage", "video?c=78"],
        ["Masturbation", "video?c=22"],
        ["Mature", "video?c=28"],
        ["MILF", "video?c=29"],
        ["Music", "video?c=121"],
        ["Old/Young", "video?c=181"],
        ["Orgy", "video?c=2"],
        ["Panda Style", "video?c=442"],
        ["Parody", "video?c=201"],
        ["Party", "video?c=53"],
        ["Pissing", "video?c=211"],
        ["Pornstar", "categories/pornstar"],
        ["POV", "video?c=41"],
        ["Public", "video?c=24"],
        ["Pussy Licking", "video?c=131"],
        ["Reality", "video?c=31"],
        ["Red Head", "video?c=42"],
        ["Rough Sex", "video?c=67"],
        ["Russian", "video?c=99"],
        ["School", "video?c=88"],
        ["SFW", "video?c=221"],
        ["Shemale", "shemale"],
        ["Small Tits", "video?c=59"],
        ["Smoking", "video?c=91"],
        ["Solo Male", "video?c=92"],
        ["Squirt", "video?c=69"],
        ["Striptease", "video?c=33"],
        ["Teen", "categories/teen"],
        ["Threesome", "video?c=65"],
        ["Toys", "video?c=23"],
        ["Uniforms", "video?c=81"],
        ["Verified Amateurs", "video?c=138"],
        ["Vintage", "video?c=43"],
        ["Virtual Reality", "vr"],
        ["Webcam", "video?c=61"]
    ]

    def __init__(self, bot):
        self.bot = bot
        self.tasks = []

    async def display_help(self, ctx):
        """Display help message"""
        help_embed = discord.Embed(
            title='__PornHub Command Help__',
            colour=discord.Colour(0xFF9900)
        )
        help_embed.add_field(
            name="Some Useful Tips",
            value="1. Arguments in < > are mandatory for the command to work\n"
                  "2. Arguments in [ ] are optional and usually have a default value\n"
                  "3. *<You must have a subscription to Pr0nBot Gold to view this Useful Tip!>*",
            inline=False
        )
        help_embed.add_field(name=".pornhub help", value="Displays this message.", inline=False)
        help_embed.add_field(
            name=".pornhub search <query> [page] [minRating]",
            value="Allows you to search PornHub for videos.",
            inline=False
        )
        await ctx.send(embed=help_embed)

    def get_vids_api(self, url, actual_page, skip, rating, still_need):
        """Get videos using the Hub Traffic API"""
        full_url = url + '&page=' + str(actual_page)
        print(full_url)

        try:
            r = requests.get(full_url, timeout=10)
            if r.status_code != 200:
                print(f'Error {r.status_code}: Cannot connect to PornHub.com')
                return []

            r_json = json.loads(r.text)

            if "videos" not in r_json:
                return []

            vid_json = r_json["videos"]
        except Exception as e:
            print(f"Error fetching videos: {e}")
            return []

        vids = []
        i = 0
        while i < len(vid_json) and still_need > 0:
            try:
                key = vid_json[i]["video_id"]
                title = vid_json[i]["title"]
                dur = vid_json[i]["duration"]
                views = "{:,}".format(int(vid_json[i]["views"]))
                rate = str(int(round(float(vid_json[i]["rating"]))))

                if int(rate) >= rating:
                    if skip > 0:
                        skip -= 1
                    else:
                        vids.append([key, title, dur, views, rate])
                        still_need -= 1
            except (KeyError, ValueError, TypeError):
                pass

            i += 1

        if still_need > 0:
            vids += self.get_vids_api(url, actual_page + 1, skip, rating, still_need)

        return vids

    @commands.group(invoke_without_command=True)
    async def pornhub(self, ctx):
        """PornHub search commands"""
        if ctx.invoked_subcommand is None:
            await self.display_help(ctx)

        # Clear out tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        self.tasks.clear()

    @pornhub.command(name="help")
    async def pornhub_help(self, ctx):
        """Display help message"""
        await self.display_help(ctx)

    @pornhub.command(name="search")
    async def pornhub_search(self, ctx, query: str = "help", page: int = 1, rating: int = 0):
        """Search PornHub for videos"""
        if query.lower() == "help":
            help_embed = discord.Embed(
                title="*.pornhub search <query> [page] [minRating]*",
                colour=discord.Colour(0xFF9900)
            )
            help_embed.set_author(name="PornHub Search Help")
            help_embed.add_field(
                name="Description",
                value="Allows you to search PornHub for videos.",
                inline=False
            )
            help_embed.add_field(
                name="Arguments",
                value="**query:** What you want to search for\n"
                      "**page:** What page of results you want (default=1)\n"
                      "**minRating:** Minimum rating 0-100 (default=0)",
                inline=False
            )
            await ctx.send(embed=help_embed)
            return

        if rating < 0 or rating > 100:
            rating = 0
        if page <= 0:
            page = 1

        try:
            actual_page = 1 if rating != 0 else math.ceil(page / 6)
            skip = 5 * ((page - 1) % 6)
            base_url = "http://www.pornhub.com/webmasters/search?thumbsize=medium&search="
            parsed_query = urllib.parse.quote_plus(query)
            partial_url = base_url + parsed_query
            vids = self.get_vids_api(partial_url, actual_page, skip, rating, 5)

            if len(vids) <= 0:
                await ctx.send("No videos found :cry:")
            else:
                res_embed = discord.Embed(
                    title='__Choose one by giving its number__',
                    colour=discord.Colour(0xFF9900)
                )
                res_embed.set_footer(text=f'{query} Results - Page {page}')
                for i in range(len(vids)):
                    good_bad = ':thumbsup:' if int(vids[i][4]) >= 50 else ':thumbsdown:'
                    porn_title = f"{i + page * 5 - 4}. {vids[i][1]}"
                    porn_stats = f':clock2: {vids[i][2]} :eyes: {vids[i][3]} {good_bad} {vids[i][4]}%'
                    res_embed.add_field(name=porn_title, value=porn_stats, inline=False)

                await ctx.send(embed=res_embed)
        except Exception as e:
            print(f"Error in search: {e}")
            await ctx.send(f"Error searching: {str(e)}")


async def setup(bot):
    """Setup function for loading the cog"""
    await bot.add_cog(PornHub(bot))

