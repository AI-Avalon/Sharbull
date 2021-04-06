import discord
from discord.ext import commands
from sharbull__db.main import *
from sharbull__utility.main import log, get_prefix, return_info
import string


class UserCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, page: str = None):
        footer = "Sharbull Securityは647によって開発されました"
        icon_url = "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png"
        prefix = get_prefix(self, ctx.message)
        if page == "commands":
            title = "コマンド一覧"
            description = "".join(("``",prefix,"setup`` : 最小構成メニューを開く\n - 必要な権限 : 管理者\n\n",
            "``",prefix,"mute <Member>`` : メンバーをミュートし、そのアカウントをSharbullデータベースに報告します\n - 必要な権限 : メンバーをMUTEする\n\n",
            "``",prefix,"kick <Member>`` : メンバーをキックし、そのアカウントをSharbullデータベースに報告します\n - 必要な権限 : メンバーをKICKする\n\n",
            "``",prefix,"ban <Member>`` : メンバーを禁止し、Sharbullデータベースにアカウントを報告します\n - 必要な権限 : メンバーをBANする\n\n",
            "``",prefix,"alert`` : ALERTモードを切り替えます（スパムメンバーは警告なしに禁止されます）\n - 必要な権限 : メンバーをBANする\n\n",
            "``",prefix,"report <Member> <reason>`` : サーバーとSharbullデータベースにアカウントを報告します\n - 必要な権限 : なし\n\n",
            "``",prefix,"flags <Member (optional)>`` : ユーザーの公開フラグを取得します\n - 必要な権限 : なし\n\n",
            "``",prefix,"status`` : このサーバーで有効になっている保護機能を確認する\n - 必要な権限 : なし\n\n",
            "``",prefix,"set_prefix <prefix>`` : このボットに新しいPrefixを設定します\n - 必要な権限 : 管理者\n\n",
            "Prefixを使用する代わりに、私にタグを付けることもできます"))

        elif page == "security":
            title = "セキュリティについて"
            description = "".join(("**自動フラグ付け**\nSharbullは、アバター、作成日、ユーザーフラグ、レポートを確認してセルフボットや偽物である可能性が高いかを自動的に検出します。",
                          "このデータを使用して、信頼スコアが計算され、さらにアクションを実行できます。\n\n",
                          "**画像認証**\n画像認証はどこでも広く使用されており、セルフボットに対して効果的であることが証明されています。",
                          "そしてSharbullは、保護の3つのレベルを使用しています。\n",
                          "- Level One : ユーザーは、画像認証を完了することなくサーバーに参加できます。\n",
                          "- Level Two : Sharbullは、ユーザーのフラグを確認することで、疑わしいユーザーの画像認証を有効にするかどうかを決定します。\n",
                          "- Level Three : クリーンユーザーを含むすべての人が画像認証を完了する必要があります。\n\n",
                          "**スパム対策**\n","ユーザーに自動的にフラグを立てるスパム対策も含まれています。",
                          " 彼らの信頼に応じてスコアが管理され、彼らはミュート、キック、または禁止される可能性があります。\n\n",
                          "**アラートモード**\n", "アラートモードを有効にすると、スパムメンバーは警告なしに禁止されます。",
                          "(*Sharbull保護サービスを最初に有効にする必要があります*) ",
                          "メンバーがスパム禁止のしきい値に達すると、アラートモードが自動的に有効になります。",
                          "ボットに無視させたい場合は各チャネルで、Sharbullに対するこのチャネルのメッセージの読み取り権限をブロックします。"))
        else:
            title = "Sharbull Security Botへようこそ！"
            description = "".join(("**このボットは何ですか？**\nSharbullは、フィルターで除外することを目的とした、数分でデプロイ可能なすぐに使用できるボットです。 ",
                          "偽のアカウントを検出し、画像認証システムを使用してセルフボットアカウントを識別します。",
                          "組み込みのスパム対策フィルターを備えたこのボットは、チャットに殺到する人間のレート制限も行います。",
                          "Sharbullは、スパマーとレイダーに対して厳格なポリシーを持っています。ゼロトレランスはオプションではなく、必須です。\n",
                          "私たちのボットは、有毒な人を検出する前に、すべてのサーバーで共有データベースを使用しています。",
                          "サーバーに参加します。\n\n",
                          "**主な特徴** \n",
                          "- メンバーに参加するための切り替え可能な画像認証\n",
                          "- すべてのサーバー間で共有されるレピュテーションシステム\n",
                          "- ユーザーの担当者に従って動作するスパム対策\n",
                          "- セルフボット検出およびフラグシステム\n\n",
                          "**使用法**\n",
                          "サーバー管理者でこのボットを使用したい場合は、 ``",prefix,"setup``コマンドを使用して今すぐ開始してください\n",
                          "``",prefix,"help commands`` or ``",prefix,"help security``送信して他のコマンドを見てみましょう\n",
                          "質問？ 懸念？ 新しいアイデア？ ``",prefix,"support``送信してサポートサーバーのリンクを取得する\n\n",
                          "Prefixを使用する代わりに、私にタグを付けることもできます"))

        embed = discord.Embed(title=title, description=description)
        embed.set_footer(text=footer, icon_url=icon_url)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def report(self, ctx, member: discord.User, *args):
        await ctx.message.delete()
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        message = "✅ メンバー {.mention} 報告されている ： ``理由 : {}``\nレポーター : {.mention}".format(member, ' '.join(word[0] for word in args),
                                                                                                 ctx.author)
        embed = discord.Embed(description=message)
        await ctx.author.send(embed=embed)
        increase_user_flag(user_id=member.id, reports_to_add=1)
        add_report(member.id, ctx.author.id, str(' '.join(word[0] for word in args)))
        if ctx.guild.get_channel(log_channel_id) is not None:
            await log(ctx.guild.get_channel(log_channel_id), message)

    @commands.command()
    async def support(self, ctx):
        message = "✉️ここでサポートを受ける: https://discord.gg/MKMQzaBzFS"
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.command()
    async def flags(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author
        add_user(member.id)
        message, trust_score = return_info(member)
        embed = discord.Embed(title="ユーザーのフラグ情報 {.name}".format(member),
                              description=message)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.command()
    async def status(self, ctx):
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        is_alert = False
        if captcha_level is None:
            captcha_level = 0
        if security_activated is None:
            security_activated = False
        with open('config/alerts.json', 'r') as f:
            alerts = json.load(f)
        try:
            is_alert = alerts[str(ctx.guild.id)]
        except:
            pass

        verified_role = ctx.guild.get_role(verified_role_id)
        is_alert_emoji = "✅ " if is_alert is not False else "❌ "
        verified_emoji = "✅ " if verified_role is not None else "❌ "
        captcha_emoji = "✅ " if captcha_level != 0 else "❌ "
        activated_emoji = "✅ " if security_activated is True else "❌ "

        if verified_role is not None:
            verified_role_fmt = verified_role.mention
        else:
            verified_role_fmt = "ロールなし"
        message = "".join((verified_emoji, "確認済みのロール：", verified_role_fmt, "\n",
                           captcha_emoji, "画像認証レベル： ", str(captcha_level),"\n",
                           activated_emoji,"保護が有効: ", str(security_activated), "\n",
                           is_alert_emoji,"アラートモードが有効: ", str(is_alert)))
        embed = discord.Embed(title="{}'のステータス".format(ctx.guild.name),
                              description=message)
        await ctx.send(embed=embed)




