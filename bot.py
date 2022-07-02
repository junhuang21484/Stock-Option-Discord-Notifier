import hikari
import lightbulb
import json

discord_setting = json.load(open("data/setting.json", "r"))["DISCORD_SETTING"]
default_guilds = discord_setting["default_guilds"]

bot = lightbulb.BotApp(
    token=discord_setting["token"],
    default_enabled_guilds=(default_guilds),
    intents=hikari.Intents.ALL
)

bot.load_extensions_from("./cogs")

bot.run()
