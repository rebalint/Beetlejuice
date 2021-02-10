import discord, re, datetime
from discord.ext import commands
from sql.poll import SqlClass
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Poll(commands.Cog, name='poll'):
    """
    Poll commands
    """
    def __init__(self, client):
        self.client = client
        self.sql = SqlClass()

        self.pollsigns = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴",
                          "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]
        self.reg = re.compile(r'({.+})\ *(\[[^\n\r\[\]]+\] *)+')

        # starts up the schedular and all the tasks for all commands on timer
        self.sched = AsyncIOScheduler()
        self.sched.start()

        client.loop.create_task(self._async_init())

    async def _async_init(self):
        """Queues up all in progress polls
        :return:
        """
        await self.client.wait_until_ready()

    @staticmethod
    def date_convert(arg: str) -> datetime:
        """Converts ddhhmmss into datetime
        :param arg: ddhhmmss string
        :return:
        """
        time_letters = ['d', 'h', 'm', 's']
        time_dict = {}
        check = False
        for time_letter in time_letters:
            found = arg.find(time_letter)
            if found != -1:
                check = True
                split_arg = arg.split(time_letter)
                time_dict[time_letter] = float(split_arg[0])
                arg = split_arg[1]
            else:
                time_dict[time_letter] = 0

        if not check:
            raise discord.errors.DiscordException
        else:
            return datetime.datetime.now() + datetime.timedelta(days=time_dict['d'], hours=time_dict['h'],
                                                                minutes=time_dict['m'], seconds=time_dict['s'])

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def poll2(self, ctx, *, args):
        """Creates anonymous poll with optional timed ending. limit of 20 options
        :param ctx:
        :param args: ddhhmmss {title}[arg][arg]
        :return: Creates a poll with timed output
        """
        time = None
        # checks message against regex to see if it matches
        if not self.reg.match(args):
            # check if it has time at start of command
            # splits arguments and datetime
            index = args.find(' ')
            time = args[:index]
            args = args[index:].lstrip()

            # converts to datetime
            time = self.date_convert(time)

            # checks if the args are formatted correctly
            if not self.reg.match(args):
                raise discord.errors.DiscordException

        # have args and possible datetime
        # formatting of arguments in message
        args = args.split('[')
        name = args.pop(0)[1:]
        name = name[:name.find('}')]
        args = [arg[:arg.find(']')] for arg in args]  # thanks ritz for this line

        # filtering out
        if len(args) > 20:
            return await ctx.send(f"bad {ctx.author.name}! thats too much polling >:(")
        elif len(args) == 0:
            return await ctx.send(f"bad {ctx.author.name}! thats too little polling >:(")
        elif name == '' or '' in args:
            return await ctx.send(f"bad {ctx.author.name}! thats too simplistic polling >:(")

        # creating embed for poll
        # main body
        description = ''
        for count in range(len(args)):
            description += f'{self.pollsigns[count]} {args[count]}\n\n'

        # footer
        footer = ''
        if time:
            strtime = time.strftime("%m/%d/%Y, %H:%M:%S")
            footer += f'time: {strtime}\n'

        embed = discord.Embed(title=name, color=discord.Color.gold(), description=description)
        embed.set_footer(text=footer)
        msg = await ctx.send(embed=embed)
        msg2 = await ctx.send('`please wait until all reactions are added before reacting`')
        # adds a message id to the end of the poll
        footer += f'id: {msg.id}'
        embed.set_footer(text=footer)
        await msg.edit(embed=embed)

        # SQL Setup
        self.sql.add_poll(msg.id, msg.channel.id, msg.author.guild.id, name, time)
        self.sql.add_options(msg.id, msg.channel.id, msg.author.guild.id, self.pollsigns, args)

        # adding reactions
        for count in range(len(args)):
            await msg.add_reaction(self.pollsigns[count])
        await msg2.delete()

    @poll2.error
    async def poll2_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error,
                                                                                    discord.errors.DiscordException):
            await ctx.send('`ERROR Missing Required Argument: make sure it is .poll2 <time ddhhmmss> {title} [args]`')
        else:
            print(error)

    @commands.command(aliases=['checkvote'])
    async def checkvotes(self, ctx):
        """Checks what polls you have voted on in this server
        :param ctx:
        :return: embed of votes sent to user's dms
        """
        polls = self.sql.check_votes(ctx.author.id)
        # removes duplicate polls from data
        polls = list(dict.fromkeys(polls))
        await ctx.message.delete()

        if len(polls) == 0:
            msg = await ctx.send('You havent voted on any active polls')
            await sleep(10)
            await msg.delete()
        else:
            for poll in polls:
                votes = self.sql.check_votes(str(ctx.author.id), poll[0])

                description = 'You have voted: \n\n'
                for vote in votes:
                    description += vote[0] + '\n'
                embed = discord.Embed(title=f'on poll: {votes[0][1]}', color=discord.Color.green(),
                                      description=description)
                await ctx.author.send(embed=embed)


def setup(client):
    client.add_cog(Poll(client))
