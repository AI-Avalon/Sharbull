import discord
from discord.ext import commands


class ErrorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        message = ""
        if isinstance(error, commands.BotMissingPermissions):
            message = "⚠️このBOTには次の権限が必要です。 : "\
                      "- メンバーをミュート\n" \
                      "- キックメンバー\n" \
                      "- メンバーの禁止\n" \
                      "- メッセージの管理\n" \
                      "- メッセージの表示と送信、リアクションの追加、チャンネルの表示などの基本的な権限..."
        elif isinstance(error, commands.NoPrivateMessage):
            message = "⚠️ギルドチャンネルでこのコマンドを使用してください。"
        elif isinstance(error, commands.MissingPermissions):
            message = "⚠️その動作を行うのに十分な権限がありません。"
        elif isinstance(error, commands.BadArgument):
            message = "⚠️コマンド引数が間違っています。"
        elif isinstance(error, commands.MissingRequiredArgument):
            message = "⚠️コマンド引数がありません。"
        elif isinstance(error, commands.CommandOnCooldown):
            target = "あなたは"
            if error.cooldown.type == commands.BucketType.guild:
                target = "ギルドは"
            message = "⚠️{} レート制限がありますので **{}** 秒後にもう一度お試しください。".format(target, round(error.retry_after))
        else:
            message = "⚠️未知のエラー"
            raise error
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)