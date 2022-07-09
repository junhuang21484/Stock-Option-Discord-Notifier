import requests

from td_helper import check_api_key, reload_key
import lightbulb
import hikari
import json

plugin = lightbulb.Plugin("Helper")
setting_data = json.load(open("data/setting.json", "r"))


def load(bot):
    bot.add_plugin(plugin)


def update_data():
    json.dump(setting_data, open("data/setting.json", "w"), indent=4)


@plugin.command
@lightbulb.command("check_setting", "Check the current setting of the bot")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_check_setting(ctx):
    td_setting = setting_data['TD_SETTING']
    dc_setting = setting_data['DISCORD_SETTING']
    rt_setting = setting_data['RUNTIME']
    embed = hikari.Embed(title="Stock/Option Discord Notifier Setting", color=0x42f584)
    embed.add_field("TD Ameritrade API", f"> ||{td_setting['api_key']}||", inline=False)
    embed.add_field("Discord Setting",
                    f"> Default Guilds: {','.join([str(guild_id) for guild_id in dc_setting['default_guilds']])}\n"
                    f"> Notify Channels: {' '.join([f'<#{channel_id}>' for channel_id in dc_setting['notify_channels']])}\n"
                    f"> Mention Users: {' '.join([f'<@{user_id}>' for user_id in dc_setting['mention']['user']])}\n"
                    f"> Mention role: {' '.join([f'<@&{role_id}>' for role_id in dc_setting['mention']['role']])}\n"
                    f"> Webhook: {dc_setting['webhook']}",
                    inline=False)
    embed.add_field("Runtime Setting",
                    f"> Check Interval: {rt_setting['check_interval']}s")

    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.option("new_key", "The new api key")
@lightbulb.command("change_api_key", "Change the api key that you want to use for TD Ameritrade")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_change_api_key(ctx: lightbulb.Context):
    new_key = ctx.options.new_key
    if not check_api_key(new_key):
        await ctx.respond("Failed to change the api key, the key cannot be validated")
        return

    setting_data["TD_SETTING"]["api_key"] = new_key
    update_data()
    reload_key()
    await ctx.respond(f"The api key has now been changed to ||{new_key}||")


@plugin.command
@lightbulb.option("new_webhook", "The new webhook that you want the webhook to be sent")
@lightbulb.command("change_noti_webhook", "Change the notification webhook to a new webhook")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_change_noti_webhook(ctx: lightbulb.Context):
    new_webhook = ctx.options.new_webhook
    req = requests.get(new_webhook)

    if req.status_code != 200:
        await ctx.respond("Failed to change the webhook, please make sure correct link is provided")
        return

    setting_data["DISCORD_SETTING"]["webhook"] = new_webhook
    update_data()

    await ctx.respond("A new webhook has now be set!")


@plugin.command
@lightbulb.option("channel_id", "The channel id that you want to add")
@lightbulb.command("add_notify_channel", "Add another channel to the notify channel list")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_add_notify_channel(ctx: lightbulb.Context):
    channel_id = ctx.options.channel_id

    if not channel_id.isnumeric():
        await ctx.respond("Make sure the channel is valid! (Should be all numbers)")
        return

    if channel_id in setting_data["DISCORD_SETTING"]["notify_channels"]:
        await ctx.respond("Channel id already in notify channel list")
        return

    if not ctx.bot.cache.get_guild_channel(channel_id):
        await ctx.respond("Channel cannot be fetch, please check correct channel id is been provided")
        return

    setting_data["DISCORD_SETTING"]["notify_channels"].append(channel_id)
    update_data()
    await ctx.respond(f"Successfully added <#{channel_id}> to the notify channel list!")


@plugin.command
@lightbulb.option("channel_id", "The channel id that you want to remove")
@lightbulb.command("remove_noti_channel", "Remove a channel from notification channel list")
@lightbulb.implements(lightbulb.SlashCommand)
async def remove_noti_channel(ctx: lightbulb.Context):
    channel_id = ctx.options.channel_id

    if channel_id not in setting_data["DISCORD_SETTING"]["notify_channels"]:
        await ctx.respond(f"Channel Id: {channel_id} is not in the notify channel list")
        return

    setting_data["DISCORD_SETTING"]["notify_channels"].remove(channel_id)
    update_data()
    await ctx.respond(f"Channel id {channel_id} has successfully been removed")


@plugin.command
@lightbulb.option("user_id", "The user id that you want to add to the mention list")
@lightbulb.command("add_mention_user", "Add a user to the mention list")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_add_mention_user(ctx: lightbulb.Context):
    user_id = ctx.options.user_id

    if not user_id.isnumeric():
        await ctx.respond("Please make sure a valid user id is been provided! (Should be all numbers)")
        return

    if user_id in setting_data["DISCORD_SETTING"]["mention"]["user"]:
        await ctx.respond("This user is already been added to the mention list")
        return

    if not ctx.bot.cache.get_user(user_id):
        await ctx.respond("User cannot be fetch, please check correct user id is been provided")
        return

    setting_data["DISCORD_SETTING"]["mention"]["user"].append(user_id)
    update_data()
    await ctx.respond(f"Successfully added user <@{user_id}> to the mention list!")


@plugin.command
@lightbulb.option("user_id", "The user id that you want to remove from mention list")
@lightbulb.command("remove_mention_user", "Remove a user from the mention list")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_remove_mention_user(ctx: lightbulb.Context):
    user_id = ctx.options.user_id
    if user_id not in setting_data["DISCORD_SETTING"]["mention"]["user"]:
        await ctx.respond(f"User id **{user_id}** is not in the mention list")
        return

    setting_data["DISCORD_SETTING"]["mention"]["user"].remove(user_id)
    update_data()

    await ctx.respond(f"User id {user_id} has been removed from mention list")


@plugin.command
@lightbulb.option("role_id", "The user id that you want to add to the mention list")
@lightbulb.command("add_mention_role", "Add a role to the mention list")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_add_mention_role(ctx: lightbulb.Context):
    role_id = ctx.options.role_id

    if not role_id.isnumeric():
        await ctx.respond("Please make sure a valid role id is been provided! (Should be all numbers)")
        return

    if role_id in setting_data["DISCORD_SETTING"]["mention"]["role"]:
        await ctx.respond("This role is already been added to the mention list")
        return

    if not ctx.bot.cache.get_role(role_id):
        await ctx.respond("Role cannot be fetch, please check correct role id is been provided")
        return

    setting_data["DISCORD_SETTING"]["mention"]["role"].append(role_id)
    update_data()
    await ctx.respond(f"Successfully added role <@&{role_id}> to the mention list!")


@plugin.command
@lightbulb.option("role_id", "The role id that you want to remove from mention list")
@lightbulb.command("remove_mention_role", "Remove a role from the mention list")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_remove_mention_role(ctx: lightbulb.Context):
    role_id = ctx.options.role_id
    if role_id not in setting_data["DISCORD_SETTING"]["mention"]["role"]:
        await ctx.respond(f"Role id **{role_id}** is not in the mention list")
        return

    setting_data["DISCORD_SETTING"]["mention"]["role"].remove(role_id)
    update_data()

    await ctx.respond(f"Role id {role_id} has been removed from mention list")


@plugin.command
@lightbulb.option("check_interval", "The new check interval that you want (in second)", type=int)
@lightbulb.command("change_check_interval", "Change the sleep time between each check for the running tasks")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_change_check_interval(ctx: lightbulb.Context):
    new_check_interval = ctx.options.check_interval
    setting_data["RUNTIME"]["check_interval"] = new_check_interval
    update_data()

    await ctx.respond(f"The new check interval has now been changed to {new_check_interval}s\n"
                      f"(Running task will not be updated unless reload task)")
