import discord
from discord.ext import commands


class ErrorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        is_error = False
        if isinstance(error, commands.BotMissingPermissions):
            message = "⚠️このBOTには次の権限が必要です。 : "\
                      "- メンバーをミュート\n" \
                      "- メンバーをキック\n" \
                      "- メンバーをBAN\n" \
                      "- メッセージの管理\n" \
                      "- その他メッセージの表示・送信、リアクションの追加、チャンネルの表示などの基本的な権限"
        elif isinstance(error, commands.NoPrivateMessage):
            message = "⚠️このコマンドはサーバーで使用して下さい。"
        elif isinstance(error, commands.MissingPermissions):
            message = "⚠️あなたはこのコマンドを使用する権限がありません。"
        elif isinstance(error, commands.BadArgument):
            message = "⚠️コマンドの引数が間違っています。"
        elif isinstance(error, commands.MissingRequiredArgument):
            message = "⚠️コマンドの引数が足りません。"
        elif isinstance(error, commands.CommandOnCooldown):
            target = "あなたは"
            if error.cooldown.type == commands.BucketType.guild:
                target = "このサーバーは"
            message = "⚠️{} レートリミットの影響を受けています。 **{}** 秒後にもう一度お試しください。".format(target, round(error.retry_after))
        else:
            message = "⚠️不明なエラー"
            is_error = True
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)
        if is_error:
            raise error
