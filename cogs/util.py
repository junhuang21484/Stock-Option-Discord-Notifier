import lightbulb
import hikari

plugin = lightbulb.Plugin("Util")


def load(bot):
    bot.add_plugin(plugin)


@plugin.command
@lightbulb.command("ping", "Get the latency of the bot")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context):
    await ctx.respond(f"Bot Latency: {ctx.bot.heartbeat_latency * 1000:,.0f}ms")