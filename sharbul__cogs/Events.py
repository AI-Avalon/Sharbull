import asyncio
import random
import string
from datetime import datetime

import discord
from captcha import image
from colorama import Fore, Style
from discord.ext import commands

from sharbul__cogs import Tasks
from sharbull__db.main import *
from sharbull__utility.main import log, return_info


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(Fore.GREEN + Style.BRIGHT +
              '接続に成功しました。 [{}]'.format(self.bot.user))
        ping_ms = round(self.bot.latency * 1000)
        print("レイテンシ : " + Fore.YELLOW +
              "{}".format(ping_ms) + Fore.GREEN + "ms\n" + Style.RESET_ALL)

        if len(self.bot.guilds) < 20:
            for server in self.bot.guilds:
                print(server.name, server.id)
        Tasks.BackgroundTasks.update_presence.start(self)

    @commands.Cog.listener()
    async def on_message(self, message):
        msg = message
        add_user(message.author.id)
        await self.bot.handler.propagate(message)
        if self.bot.tracker.is_spamming(message):
            log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(message.guild.id)
            points = calculate_reputation(message.author.id)
            increase_user_flag(user_id=msg.author.id, reports_to_add=1, bypass_cooldown=True)
            alert_activated = False
            with open('config/alerts.json', 'r') as f:
                alerts = json.load(f)
            # noinspection PyBroadException
            try:
                alert_activated = alerts[str(message.guild.id)]
                if alert_activated is False:
                    pass
                else:
                    points = 99
            except Exception:
                pass

            message_log = "ユーザー {.mention}".format(msg.author) + " - マイナス評価ポイント : " + str(points) + "\n"
            if points <= 3:
                message_log += "ユーザーが警告されました。"
                description = "{.mention} : スパムをやめて下さい。-ミュート前の警告 : {}".format(msg.author, 3 - points)
            elif points <= 6:
                message_log += "ユーザーがミュートされました（認証済みロールは剥奪済み）"
                description = "{.mention} スパムのためにミュートされています- キックの前の警告 : {} ".format(message.author, 6 - points)
                await msg.author.remove_roles(msg.guild.get_role(verified_role_id))
                increase_user_flag(user_id=msg.author.id, mutes_to_add=1)
            elif points <= 9:
                message_log += "ユーザーがキックされました"
                description = "{.mention} はスパムを行ったためキックされました。-BAN前の警告 : {}".format(msg.author, 12 - points)
                increase_user_flag(user_id=msg.author.id, kicks_to_add=1)
                await msg.author.kick(reason="スパム行為")
            else:
                alert_message = ""
                if alert_activated is True:
                    alert_message = "-警戒モードが有効になりました。"

                message_log += "ユーザーがBANされました"
                description = "{.mention} はスパムを行ったためBANされました。 {} - **警戒モードが有効になりました**。スパムを行ったユーザーは警告なしにBANされます".format(
                    msg.author, alert_message)
                alerts[str(message.guild.id)] = True
                with open('config/alerts.json', 'w') as f:
                    json.dump(alerts, f, indent=4)

                await msg.author.ban(reason="スパム", delete_message_days=1)
                increase_user_flag(user_id=msg.author.id, bans_to_add=1)
            embed = discord.Embed(description=description)
            if security_activated is not None:
                await msg.channel.send(embed=embed)
                if msg.guild.get_channel(log_channel_id) is not None:
                    await log(msg.guild.get_channel(log_channel_id), message_log)
            self.bot.tracker.remove_punishments(message)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        now = datetime.now().strftime("%Y %m %d - %H:%M:%S")
        print(now, "新しいCaptcha認証が開始されました。ユーザー：", member.id)
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(member.guild.id)
        if security_activated is None or member.bot is True:
            return False

        add_user(member.id)

        message = "**新しいメンバーが参加しました。** : " + member.mention + "\n"

        message, trust_score = return_info(member, message)

        await log(member.guild.get_channel(log_channel_id), message)

        if captcha_level == 2 and trust_score > 9:
            await log(member.guild.get_channel(log_channel_id),
                      "{.mention}の信頼スコアが基準に達しているためCaptcha認証をスキップしました。".format(member))
            if member.guild.get_role(verified_role_id) is not None:
                await member.add_roles(member.guild.get_role(verified_role_id))
            return True
        if captcha_level == 1:
            await log(member.guild.get_channel(log_channel_id), "Captcha認証が無効のため、認証をスキップしました。")
            if member.guild.get_role(verified_role_id) is not None:
                await member.add_roles(member.guild.get_role(verified_role_id))
            return True

        string_to_guess = ""
        for char in range(6):
            char = random.choice(string.ascii_lowercase)
            string_to_guess += char
        image_data = image.ImageCaptcha(width=280, height=90).generate_image(string_to_guess)
        image_data.save("captcha/" + str(member.id) + ".png")
        embed = discord.Embed(title="**{}** へようこそ！".format(member.guild.name),
                              description="続行するには、次のCaptcha認証を完了してください。\n" +
                                          "**60**秒以内に返信しなければアクセスが拒否されます。" +
                                          "\n文字は**小文字のみ**です。数字は含まれていません。"  # in bold because ppl cant read
                              )
        embed.set_thumbnail(url=member.guild.icon_url)
        embed.set_footer(
            text="Sharbull SecurityGuard-このサーバーでは高度なセキュリティ認証が実施されています。",
            icon_url="https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png"
        )
        file = discord.File("captcha/" + str(member.id) + ".png", filename="image.png")
        embed.set_image(url="attachment://image.png")
        # noinspection PyBroadException
        try:
            await member.send(
                embed=embed,
                file=file
            )
        except Exception:
            if log_channel_id is not None:
                message = ("⚠️ エラー！ Captcha認証を送信できませんでした。 {.mention} はDMを拒否しています。 ユーザーは手動の承認待ちです。".format(
                    member
                ))
                await log(member.guild.get_channel(log_channel_id), message)
                return False

        # await member.send(file=discord.File("captcha/" + str(member.id) + ".png"))

        def check(received_message):
            return received_message.content == string_to_guess and \
                   received_message.channel == received_message.author.dm_channel

        try:
            await self.bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="時間を超過しました。認証に失敗しました。",
                description="あなたは**{}**からキックされました。\n".format(member.guild.name) +
                            "サーバーに再度参加して再試行してください。"
            )
            embed.set_thumbnail(url=member.guild.icon_url)
            embed.set_footer(
                text="Sharbull Security Guard",
                icon_url="https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png"
            )
            await member.dm_channel.send(embed=embed)
            await member.kick(reason="ユーザーがCaptcha認証に失敗しました")
            increase_user_flag(user_id=member.id, captcha_fails_to_add=1)
        else:
            embed = discord.Embed(
                title="認証に成功しました。",
                description="**{}** へようこそ！".format(member.guild.name)
            )
            embed.set_thumbnail(url=member.guild.icon_url)
            embed.set_footer(
                text="Sharbull Security Guard",
                icon_url="https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png"
            )
            # noinspection PyBroadException
            try:
                await member.dm_channel.send(embed=embed)
            except Exception:
                if log_channel_id is not None:
                    message = ("⚠️ Captcha認証を送信できませんでした。 {.mention} はDMを拒否しています。".format(
                        member
                    ))
                    await log(member.guild.get_channel(log_channel_id), message)
            await member.add_roles(member.guild.get_role(verified_role_id))
        os.remove("captcha/" + str(member.id) + ".png")
