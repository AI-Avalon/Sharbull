import discord
from discord.ext import commands
from sharbull__db.main import *
from sharbull__utility.main import get_prefix


class SetupCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def setup(self, ctx):
        add_guild(ctx.guild.id)
        prefix = get_prefix(self, ctx.message)
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        log_emoji = "✅ " if log_channel_id is not None else "❌ "
        verified_emoji = "✅ " if verified_role_id is not None else "❌ "
        captcha_emoji = "✅ " if captcha_level is not None else "❌ "
        activated_emoji = "✅ " if security_activated is not None else "❌ "
        embed = discord.Embed(title="Sharbull Security Botへようこそ！",
                              description="Sharbullを最初にセットアップするには、いくつかの手順を実行する必要があります。\n\n" +
                                          "**1.** " + log_emoji + "``"+prefix+"set_log_channel`` ログを投稿するテキストチャネルでコマンドを実行してください。\n\n" +
                                          "**2.** " + verified_emoji + "``"+prefix+"set_verified_role @a_role`` ユーザーがボットによって承認されたときに取得するロールを @a_role に置き換えて実行してください。\n\n" +
                                          "**3.** チャネルのアクセス許可を編集して、確認済みユーザーのみにアクセスを制限します。\n\n" +
                                          "**4.** " + captcha_emoji + "``"+prefix+"set_captcha_level <level (1, 2, or 3)>`` キャプチャポリシーを設定するには（詳細については、 ``"+prefix+"help security``\n" +
                                          " > Level ``1`` : キャプチャ検証なし\n" +
                                          " > Level ``2`` : 疑わしいユーザーのみの検証（推奨）\n" +
                                          " > Level ``3`` : すべての人のための検証\n" +
                                          "⚠️ 注意 : ユーザーはサーバーからのダイレクトメッセージを承認する必要があります。そうしないと、検証が不可能になります。\n\n"+
                                          "**5.** " + activated_emoji + "``"+prefix+"activate`` セキュリティサービスを開始するにはこのコマンドを実行してください。"
                              )
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def set_log_channel(self, ctx):
        add_guild(ctx.guild.id)
        set_guild_setting(ctx.guild.id, new_log_channel_id=ctx.channel.id)
        message = "✅ {.mention} がログチャンネルに設定されました。".format(ctx.channel)
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def set_verified_role(self, ctx, role: discord.Role):
        add_guild(ctx.guild.id)
        set_guild_setting(ctx.guild.id, new_verified_role_id=role.id)
        message = "✅ {.mention} が確認済みのロールになります。".format(role)
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def set_captcha_level(self, ctx, level: int):
        add_guild(ctx.guild.id)
        if level < 1:
            level = 1
        if level > 3:
            level = 3
        set_guild_setting(ctx.guild.id, new_captcha_level=level)
        message = "✅ キャプチャレベルは**{}**に設定されています".format(level)
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def activate(self, ctx):
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        prefix = get_prefix(self, ctx.message)
        if log_channel_id is None or verified_role_id is None or captcha_level is None:
            message = "⚠️保護を設定するための最初の手順を実行してください"
            embed = discord.Embed(description=message)
            await ctx.send(embed=embed)
        else:
            set_guild_setting(ctx.guild.id, new_security_activated=True)
            message = "✅ 保護が有効になりました, 無効にするには ``"+prefix+"deactivate``と実行してください。"
            embed = discord.Embed(description=message)
            await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def deactivate(self, ctx):
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        prefix = get_prefix(self, ctx.message)
        if log_channel_id is None or verified_role_id is None or captcha_level is None:
            message = "⚠️保護を設定するための最初の手順を実行してください"
            embed = discord.Embed(description=message)
            await ctx.send(embed=embed)
        else:
            set_guild_setting(ctx.guild.id, new_security_activated=None)
            message = "✅ 保護が無効になりました。, 有効化するには ``"+prefix+"activate`` と実行してください。"
            embed = discord.Embed(description=message)
            await ctx.send(embed=embed)
