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
    result = ("{0} 日{1}, ".format(days, "" if days!=1 else "") if days else "") + \
    ("{0} 時間{1}, ".format(hours, "" if hours!=1 else "") if hours else "") + \
    ("{0} 分{1}, ".format(minutes, "" if minutes!=1 else "") if minutes else "") + \
    ("{0:.2f} 秒{1} 前に作成".format(seconds, "" if seconds!=1 else "") if seconds else "")
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
        embed.set_footer(text="Sharbull Security Bot - Timezone : UTC",
                         icon_url="https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png")
        await channel.send(embed=embed)
    else:
        print("ログは設定されていません")


def return_info(member: discord.Member, message = ""):
    captcha_fails, mutes, reports, kicks, bans = check_user_flags(member.id)
    trust_score = 14
    now = datetime.now()
    created_at = member.created_at
    time_since_creation = now - created_at
    time_since_creation = time_since_creation.total_seconds()
    time_since_creation_fmt = seconds_to_text(time_since_creation)

    message += "アカウント作成日時： " + time_since_creation_fmt + "\n\n ** 所有しているバッジ **:\n"
    # trust
    days, hours, minutes, seconds = seconds_to_dhms(time_since_creation)
    if days < 1:
        message += " 	🚩 アカウントは1日以内に作成されました。\n"
        trust_score -= 3
    if member.avatar_url == member.default_avatar_url:
        message += " 	🚩 アカウントのアバターがデフォルトです。\n"
        trust_score -= 2
    if member.public_flags.hypesquad is False:
        message += "⚠️ アカウントはどのHypeSquadチームにも属していません。\n"
        trust_score -= 1
    if member.premium_since is None:
        message += "⚠️ アカウントに有効なNitroサブスクがありません。\n"
        trust_score -= 1
    if member.public_flags.partner is False:
        message += "⚠️ アカウントにパートナーバッジがありません。\n"
        trust_score -= 1
    if member.public_flags.early_supporter is False:
        message += "⚠️ アカウントに早期サポーターバッジがありません。\n"
        trust_score -= 1
    if captcha_fails > 5:
        message += "⚠️ アカウントがCaptcha認証に** {} **回失敗しました。\n".format(captcha_fails)
        trust_score -= 1
    if mutes > 6:
        message += " 	🚩 アカウントが過去に** {} **回ミュートされます。\n".format(mutes)
        trust_score -= 1
    if reports > 5:
        message += " 	🚩 アカウントは過去に** {} **回報告されています。\n".format(reports)
        trust_score -= 1
    if kicks > 3:
        message += " 	🚩 アカウントは過去に** {} **回キックされています。\n".format(kicks)
        trust_score -= 1
    if bans > 2:
        message += " 	🚩 アカウントは過去に** {} **回BANされています。\n".format(bans)
        trust_score -= 1

    message += ("🔍 信頼スコアは `" + str(trust_score)+"`です。")

    return message, trust_score



