import discord
from discord.ext import commands
from sharbull__db.main import *
from sharbull__utility.main import log


class UserCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, page: str = None):
        footer = "Sharbull Security - Developed by 647"
        icon_url = "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png"
        if page == "commands":
            title = "About the commands",
            description = "``!!setup`` : Open minimum configuration menu\n - Permission required : administrator\n\n"
            "``!!mute <Member>`` : Mute a member and report their account to the Sharbull database\n - Permission required : mute members\n\n"
            "``!!kick <Member>`` : Kick a member and report their account to the Sharbull database\n - Permission required : kick members\n\n"
            "``!!ban <Member>`` : Ban a member and report their account to the Sharbull database\n - Permission required : ban members\n\n" \
            "``!!report <Member> <reason>`` : Report an account to the server and to the Sharbull database\n - Permission required : None\n\n"

        elif page == "security":
            title = "About the security"
            description = "Sharbull automatically detects if an account is fake or likely to be a " \
                          "selfbot by checking their avatar, creation date, user flags and reports. " \
                          "With this data, a trust score is calculated and further actions may be taken." \
                          "An antispam is also included, which automatically flags the user. Depending on their trust " \
                          "score, they may get muted, kicked or even banned. "
        else:
            title = "Welcome to Sharbull Security Bot!"
            description = "Sharbull is a ready to use bot deployable in minutes, aimed to filter out " \
                          "selfbot accounts by detecting fake accounts and using a captcha system. " \
                          "With its built-in anti-spam filter this bot will also rate limit humans who flood the chat, as " \
                          "Sharbull has a strict policy on spammers and raiders, zero tolerance is not an option, it's mandatory.\n" \
                          "Our bot is using a shared database across all servers in order to detect toxic people before they even " \
                          "join your server.\n\n" \
                          "If you are a server administrator, you can start by using the command ``!!setup``\n" \
                          "Take a look at other commands by sending ``!!help commands`` or ``!!help security``"

        embed = discord.Embed(title=title, description=description)
        embed.set_footer(text=footer, icon_url=icon_url)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def report(self, ctx, member: discord.User, *, reason):
        await ctx.message.delete()
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        message = "✅ Member {.mention} has been reported : ``{}``\nReporter : {.mention}".format(member, reason,
                                                                                                 ctx.author)
        embed = discord.Embed(description=message)
        await ctx.author.send(embed=embed)
        increase_user_flag(user_id=member.id, reports_to_add=1)
        add_report(member.id, ctx.author.id, str(reason))
        await log(ctx.guild.get_channel(log_channel_id), message)

    @commands.command()
    async def support(self, ctx):
        message = "✉️ Get support here : https://discord.gg/RKURYUeX6t"
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        message = ""
        if isinstance(error, commands.BotMissingPermissions):
            message = "⚠️The bot must be an administrator in order to protect the guild."
        elif isinstance(error, commands.NoPrivateMessage):
            message = "⚠️Please use this command in a guild channel."
        elif isinstance(error, commands.BadArgument):
            message = "⚠️Wrong command argument."
        elif isinstance(error, commands.MissingRequiredArgument):
            message = "⚠️Missing command argument."
        else:
            message = "⚠️Unknown error"
            raise error

        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)
