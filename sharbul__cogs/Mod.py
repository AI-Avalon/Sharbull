import discord
from discord.ext import commands
from sharbull__db.main import *
from sharbull__utility.main import log


class ModCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(mute_members=True)
    @commands.has_permissions(mute_members=True)
    @commands.guild_only()
    @commands.command()
    async def mute(self, ctx, member: discord.Member):
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        # noinspection PyBroadException
        try:
            await member.remove_roles(ctx.guild.get_role(verified_role_id))
            message = "✅ {.mention} はミュートされました（{.mention} が剥奪されました。)".format(member,
                                                                             ctx.guild.get_role(
                                                                                 verified_role_id))
        except Exception:
            message = "✅ {.mention} は既にミュートされています（{.mention} が剥奪されました。)".format(member,
                                                                                ctx.guild.get_role(
                                                                                    verified_role_id))

        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)
        increase_user_flag(user_id=member.id, mutes_to_add=1)
        if ctx.guild.get_channel(log_channel_id) is not None:
            await log(ctx.guild.get_channel(log_channel_id), message)

    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    @commands.command()
    async def kick(self, ctx, member: discord.Member):
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        message = "✅ {.mention} はキックされました。".format(member)
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)
        await member.kick()
        increase_user_flag(user_id=member.id, kicks_to_add=1)
        if ctx.guild.get_channel(log_channel_id) is not None:
            await log(ctx.guild.get_channel(log_channel_id), message)

    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command()
    async def ban(self, ctx, member: discord.Member):
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        message = "✅ {.mention} はBANされました。".format(member)
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)
        await member.ban()
        increase_user_flag(user_id=member.id, bans_to_add=1)
        if ctx.guild.get_channel(log_channel_id) is not None:
            await log(ctx.guild.get_channel(log_channel_id), message)

    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command()
    async def alert(self, ctx):
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        if security_activated is True:
            message = ""
            with open('config/alerts.json', 'r') as f:
                alerts = json.load(f)
            # noinspection PyBroadException
            try:
                alert_activated = alerts[str(ctx.guild.id)]
                if alert_activated is False:
                    alerts[str(ctx.guild.id)] = True
                    message = "✅ 警戒モードが有効になりました。スパムを行ったユーザーは警告なしにBANされます"
                else:
                    alerts[str(ctx.guild.id)] = False
                    message = "✅ 警戒モードが無効になりました。"

            except KeyError:
                alerts[str(ctx.guild.id)] = True
                message = "✅ 警戒モードが有効になりました。スパムを行ったユーザーは警告なしにBANされます"
            except Exception:
                print("エラーはありません")

            with open('config/alerts.json', 'w') as f:
                json.dump(alerts, f, indent=4)

            embed = discord.Embed(description=message)
            await ctx.send(embed=embed)
            if ctx.guild.get_channel(log_channel_id) is not None:
                await log(ctx.guild.get_channel(log_channel_id), message)
        else:
            message = "⚠️セキュリティが有効になっておらず、警告モードを切り替えることができません。"
            embed = discord.Embed(description=message)
            await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix):
        with open('config/customprefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix

        with open('config/customprefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

        message = "✅ Prefixは現在 `{}` です。".format(prefix)
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)
