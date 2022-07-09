import json
import lightbulb
import miru
import hikari

plugin = lightbulb.Plugin("Util")
command_data = json.load(open("data/command.json", "r"))


def load(bot):
    bot.add_plugin(plugin)


class HelpMenu(miru.View):
    @miru.select(
        placeholder="Select a command",
        options=[
            miru.SelectOption(label="Setting Commands"),
            miru.SelectOption(label="Data Management Commands"),
            miru.SelectOption(label="Task Commands"),
        ]
    )
    async def slm_help(self, select: miru.Select, ctx: miru.Context):
        cmd_section = select.values[0]
        embed = hikari.Embed(title=cmd_section,
                             description=f"Below is the lis of all commands related to {cmd_section.lower()}",
                             color=0x3486eb)

        for cmd_name in command_data[cmd_section]:
            cmd_data = command_data[cmd_section][cmd_name]
            embed.add_field(f"Command: {cmd_name}",
                            f"{cmd_data['desc']}\n\n__Parameters__\n{cmd_data['para']}")

        await ctx.respond(embed=embed)


@plugin.command
@lightbulb.command("help", "Get the helper menu for commands")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_help(ctx: lightbulb.Context):
    view = HelpMenu(timeout=3)
    msg = await ctx.respond("Choose a command that you have a question about", components=view.build())
    view.start(await msg.message())
    await view.wait()


@plugin.command
@lightbulb.command("ping", "Get the latency of the bot")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context):
    await ctx.respond(f"Bot Latency: {ctx.bot.heartbeat_latency * 1000:,.0f}ms")
