import discord
from discord.ext import commands
import random

class Fun(commands.Cog, name='Fun'):
    """
    F is for friends and uh U is for I forgot and N is for now? Idk this song
    """
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['hugs'])
    async def hug(self, ctx, target: discord.Member = None):
        hug_urls = ["https://imgur.com/gvC4K6u", "https://imgur.com/9RGBOLa", "https://imgur.com/ZRGpg8P",
                    "https://imgur.com/7APfwfg", "https://imgur.com/xTJdcbg", "https://imgur.com/D1bJQWL",
                    "https://imgur.com/3AB9LXN", "https://imgur.com/xwogdA8", "https://imgur.com/3aSRyez",
                    "https://imgur.com/OMtbHom", "https://imgur.com/XALtUs4", "https://imgur.com/EIfimk8",
                    "https://imgur.com/BEG77iA", "https://imgur.com/qxeXsRr", "https://imgur.com/osZF2GM",
                    "https://imgur.com/PqotrGa", "https://imgur.com/sYCVhZ1", "https://imgur.com/ItZk2E7",
                    "https://imgur.com/ng81k8S", "https://imgur.com/4bGa09O"]

        if target is None:
            await ctx.send(f"*hugs back*")

        elif target == ctx.author:
            await ctx.send("https://imgur.com/xTJdcbg")
            return

        else:
            hug_result = random.shuffle(hug_urls)
            await ctx.send(f"{hug_result}")
            return


def setup(client):
    client.add_cog(Fun(client))


cars = ["Ford", "Volvo", "BMW"]

cars[0] = "Toyota"