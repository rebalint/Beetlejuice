from discord.errors import DiscordException
from discord.ext import commands
from discord.utils import get
import discord
from sql.role import SqlClass # BITCH STOP COMPLAING YOU LITEREALYL WORK. DUMB ASS PROGRAMM


class Role(commands.Cog, name='role'):
    """
    Persistent roles
    """
    def __init__(self, client):
        self.client = client
        self.sql = SqlClass()

    def _update_roles(self, guild):
        """
        Updates Roles in the database
        :param guild: The guild class of the discord server that it is working on
        :return:
        """
        guild_roles = guild.roles
        guild_id = guild.id

        db_roles = self.sql.get_roles(guild_id)
        db_roles = [db_role[0] for db_role in db_roles]  # Removes tuples from list

        lst = []
        for role in guild_roles:
            role_id = role.id
            role_name = role.name

            if role_id not in db_roles and role_name != "@everyone":
                lst.append(role_id)

        self.sql.add_roles(guild_id, lst)

        lst = []
        for db_role in db_roles:
            if not any(guild_role.id == db_role for guild_role in guild_roles):
                lst.append(db_role)

        self.sql.remove_roles(guild_id, lst)

    def _update_guild(self):
        """
        Updates Guilds in the database
        :return:
        """
        guilds = self.client.guilds
        guilds = [guild.id for guild in guilds]

        db_guilds = self.sql.get_guilds()
        db_guilds = [db_guilds[0] for db_guilds in db_guilds]

        lst = []
        for guild in guilds:
            if guild not in db_guilds:
                lst.append(guild)

        self.sql.add_guilds(lst)

        lst = []
        for db_guild in db_guilds:
            if db_guild not in guilds:
                lst.append(db_guild)

        self.sql.remove_guilds(lst)

    @commands.command(aliases=['clearroles','purgeroles'])
    @commands.has_permissions(administrator=True)
    async def removeroles(self, ctx, member: discord.Member = None):
        """Removes a users roles
        :param ctx:
        :param member: The users whos roles are getting removed
        :return: Removes the users role from the database
        """
        guild_id = ctx.guild.id
        if member is None:
            username = ctx.author.name
            user_id = ctx.author.id
        else:
            username = member.name
            user_id = member.id

        message = await ctx.send(f"`purging {username}'s roles from datatables...`")
        self.sql.remove_user_roles(user_id, guild_id)
        await message.edit(content=f"`purged {username}'s roles from datatables!`")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addroles(self, ctx, member: discord.Member):
        """
        Adds user roles to server
        :param ctx:
        :param member: The users whos roles are getting added
        :return: Adds the users roles and removes their roles from the database
        """
        self._update_guild()
        self._update_roles(ctx.guild)

        user_id = member.id
        guild = member.guild.id
        user_roles = self.sql.get_user_roles(user_id, guild)
        user_roles = [user_role[0] for user_role in user_roles]

        if len(user_roles) < 1:
            await ctx.send(f'`{member.name} has no roles in my datatable`')
        else:
            message = await ctx.send(f"`adding {member.name}'s roles...`")

            # gets a list of role classes
            db_roles = []
            for user_role in user_roles:
                role = get(member.guild.roles, id=user_role)
                db_roles.append(role)

            # adds roles
            try:
                await member.add_roles(*db_roles, reason="Automatically added roles")
            except DiscordException as e:
                print(e)

            self.sql.remove_user_roles(user_id, guild)
            await message.edit(content=f"`updated {member.name}'s roles!`")

    @staticmethod
    @addroles.error
    async def addroles_error(ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('`MISSING ARGUMENTS: please specify a user`')
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('`MISSING PERMS: you need to be an administrator to run this command`')
        else:
            print(error)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        adds member's roles to database when they leave
        """
        self._update_guild()
        self._update_roles(member.guild)

        user_id = member.id
        user_guild_id = member.guild.id

        self.sql.add_user(user_id, user_guild_id)

        self.sql.remove_user_roles(user_id, user_guild_id)
        user_roles = member.roles
        lst = []
        for user_role in user_roles:
            if user_role.name != "@everyone":
                lst.append(user_role.id)
        self.sql.add_user_roles(user_id, lst, user_guild_id)


def setup(client):
    client.add_cog(Role(client))
