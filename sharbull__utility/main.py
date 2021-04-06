import discord
from sharbull__db.main import *
from datetime import datetime, timedelta


def get_prefix(client, message):
    with open('config/customprefixes.json', 'r') as f:
        prefixes = json.load(f)
    try:
        return prefixes[str(message.guild.id)]
    except:
        return "!!"



def seconds_to_text(secs):
    days, hours, minutes, seconds = seconds_to_dhms(secs)
    result = ("{0} 日{1}, ".format(days, "s" if days!=1 else "") if days else "") + \
    ("{0} 時間{1}, ".format(hours, "s" if hours!=1 else "") if hours else "") + \
    ("{0} 分{1}, ".format(minutes, "s" if minutes!=1 else "") if minutes else "") + \
    ("{0:.2f} 秒{1} 前".format(seconds, "s" if seconds!=1 else "") if seconds else "")
    return result


def seconds_to_dhms(secs):
    days = secs//86400
    hours = (secs - days*86400)//3600
    minutes = (secs - days*86400 - hours*3600)//60
    seconds = secs - days*86400 - hours*3600 - minutes*60
    return days, hours, minutes, seconds


async def log(channel: discord.TextChannel, message: str):
    if channel is not None:
        embed = discord.Embed(title="新しいログ", description=message, timestamp=datetime.utcnow())
        embed.set_footer(text="Sharbull Security Bot - Timezone : GMT",
                         icon_url="https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png")
        await channel.send(embed=embed)
    else:
        print("ログの設定なし")


def return_info(member: discord.Member, message = ""):
    captcha_fails, mutes, reports, kicks, bans = check_user_flags(member.id)
    trust_score = 14
    now = datetime.now()
    created_at = member.created_at
    time_since_creation = now - created_at
    time_since_creation = time_since_creation.total_seconds()
    time_since_creation_fmt = seconds_to_text(time_since_creation)

    message += "アカウントの作成： " + time_since_creation_fmt + "\n\n ** 目立つフラグ **:\n"
    # trust
    days, hours, minutes, seconds = seconds_to_dhms(time_since_creation)
    if days < 1:
        message += " 	🚩 アカウントは1日以内に作成されました\n"
        trust_score -= 3
    if member.avatar_url == member.default_avatar_url:
        message += " 	🚩 アカウントにはカスタムアバターがありません\n"
        trust_score -= 2
    if member.public_flags.hypesquad is False:
        message += "⚠️ アカウントにはHypeSquadチームがありません\n"
        trust_score -= 1
    if member.premium_since is None:
        message += "⚠️ アカウントにNitroアクティブサブがありません\n"
        trust_score -= 1
    if member.public_flags.partner is False:
        message += "⚠️ アカウントにパートナーバッジがありません\n"
        trust_score -= 1
    if member.public_flags.early_supporter is False:
        message += "⚠️ アカウントに早期サポーターバッジがありません\n"
        trust_score -= 1
    if captcha_fails > 5:
        message += "⚠️ アカウントがキャプチャ** {} **回失敗しました\n".format(captcha_fails)
        trust_score -= 1
    if mutes > 6:
        message += " 	🚩 アカウントが** {} **回ミュートされました\n".format(mutes)
        trust_score -= 1
    if reports > 5:
        message += " 	🚩 アカウントは** {} **回報告されています\n".format(reports)
        trust_score -= 1
    if kicks > 3:
        message += " 	🚩 アカウントが** {} **回キックされました\n".format(kicks)
        trust_score -= 1
    if bans > 2:
        message += " 	🚩 アカウントは** {} **回BANされました\n".format(bans)
        trust_score -= 1

    message += ("🔍 信頼スコアは ``" + str(trust_score)+"``")

    return message, trust_score



