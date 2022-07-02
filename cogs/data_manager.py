from td_helper import *
from datetime import datetime
import lightbulb
import hikari
import json

plugin = lightbulb.Plugin("Helper")
monitor_data = json.load(open("data/data.json", "r"))


def load(bot):
    bot.add_plugin(plugin)


def update_data():
    remove_key = []
    for ticker in monitor_data:
        if not monitor_data[ticker]:
            remove_key.append(ticker)

    for key in remove_key:
        del monitor_data[key]

    json.dump(monitor_data, open("data/data.json", "w"), indent=4)


def check_date(date: str) -> bool:
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


@plugin.command
@lightbulb.command("check_monitoring", "Get all data that are currently been monitored by the bot")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_check_monitoring(ctx: lightbulb.Context):
    embed = hikari.Embed(title="All Monitoring Data", color=0x42f584)
    for ticker in monitor_data:
        ticker_str = ""
        for ticker_data in monitor_data[ticker]:
            if ticker_data["type"] == "STOCK":
                ticker_str += f"> **Type**: Stock\n" \
                              f"> **Trigger**: {ticker_data['over_under'].title()} {ticker_data['price_target']}\n\n"

            if ticker_data["type"] == "OPTION":
                ticker_str += f"> **Type**: Option\n" \
                              f"> **Contract**: {ticker_data['strike']} {ticker_data['con_type']} {ticker_data['date']}\n" \
                              f"> **Trigger**: {ticker_data['over_under'].title()} {ticker_data['price_target']}\n\n"

        embed.add_field(ticker, ticker_str, inline=False)

    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.option("price_target", "The price target to check", type=float)
@lightbulb.option("over_under", "Do you want to notify when it goes over/under a price target", type=str)
@lightbulb.option("symbol", "The symbol of the stock", type=str)
@lightbulb.command("add_stock_task", "Add a stock price task for a symbol")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_add_stock_task(ctx: lightbulb.Context):
    symbol = ctx.options.symbol.upper()
    over_under = ctx.options.over_under.upper()
    price_target = str(ctx.options.price_target)

    if over_under != "OVER" and over_under != "UNDER":
        await ctx.respond("Only **OVER** and **UNDER** are accept for the over_under field")
        return

    if not get_stock_price(symbol):
        await ctx.respond(f"Symbol **{symbol}** was not found")
        return

    new_stock = {
        "type": "STOCK",
        "over_under": over_under,
        "price_target": price_target,
        "con_type": "",
        "strike": "",
        "date": ""
    }

    if symbol in monitor_data:
        monitor_data[symbol].append(new_stock)
    else:
        monitor_data[symbol] = [new_stock]

    update_data()

    await ctx.respond(f"Successfully added {symbol} to the monitor list, it will notify when the price goes "
                      f"{over_under} {price_target}\n"
                      f"(You still need to start the task)")


@plugin.command
@lightbulb.option("date", "The date of the option expire, must be in YYYY-MM-DD format", type=str)
@lightbulb.option("strike", "The strike of the contract", type=float)
@lightbulb.option("con_type", "The contract type, CALL/PUT", type=str)
@lightbulb.option("price_target", "The price target to check", type=float)
@lightbulb.option("over_under", "Do you want to notify when it goes over/under a price target", type=str)
@lightbulb.option("symbol", "The symbol of the stock", type=str)
@lightbulb.command("add_option_task", "Add an option price task for a symbol")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_add_option_task(ctx: lightbulb.Context):
    symbol = ctx.options.symbol.upper()
    over_under = ctx.options.over_under.upper()
    price_target = str(ctx.options.price_target)
    con_type = ctx.options.con_type.upper()
    strike = str(ctx.options.strike)
    date = ctx.options.date

    if over_under != "OVER" and over_under != "UNDER":
        await ctx.respond("Only **OVER** and **UNDER** are accept for the over_under field")
        return

    if not get_stock_price(symbol):
        await ctx.respond(f"Symbol **{symbol}** was not found")
        return

    if con_type != "CALL" and con_type != "PUT":
        await ctx.respond("Only **CALL** and **PUT** are allowed for the con_type field")
        return

    if not check_date(date):
        await ctx.respond(f"Please make sure that the date is in the format of YYYY-MM-DD")
        return

    if not get_option_price(symbol, strike, con_type, date):
        await ctx.respond(
            f"Error pulling the option data for the contract **{date} {symbol} {strike} {con_type}**, please make "
            f"sure the date and the strike is correct!")
        return

    new_option = {
        "type": "OPTION",
        "over_under": over_under,
        "price_target": price_target,
        "con_type": con_type,
        "strike": strike,
        "date": date
    }

    if symbol in monitor_data:
        monitor_data[symbol].append(new_option)
    else:
        monitor_data[symbol] = [new_option]

    update_data()

    await ctx.respond(
        f"Successfully added the contract **{date} {symbol} {strike} {con_type}** to the monitor list, "
        f"it will notify when the price goes {over_under} {price_target}\n"
        f"(You still need to start the task)")


@plugin.command
@lightbulb.command("remove_all_task", "remove ALL MONITORING DATA")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_remove_all_task(ctx: lightbulb.Context):
    monitor_data.clear()
    update_data()
    await ctx.respond("All monitor data has been cleared")


@plugin.command
@lightbulb.option("symbol", "The symbol that you want to remove")
@lightbulb.command("remove_symbol_monitor", "Remove ALL MONITORING data for a symbol")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_remove_symbol_monitor(ctx: lightbulb.Context):
    symbol = ctx.options.symbol.upper()

    if symbol not in monitor_data:
        await ctx.respond(f"The symbol {symbol} was not been monitored")
        return

    del monitor_data[symbol]
    update_data()
    await ctx.respond(f"The symbol {symbol} has been removed!")


@plugin.command
@lightbulb.option("price_target", "The price target of the task that you want to remove", type=float)
@lightbulb.option("over_under", "The over/under of the task you want to remove", type=str)
@lightbulb.option("symbol", "The symbol of the task that you want to remove", type=str)
@lightbulb.command("remove_stock_task", "Remove a specific stock monitoring task from the monitoring data")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_remove_stock_task(ctx: lightbulb.Context):
    symbol = ctx.options.symbol.upper()
    over_under = ctx.options.over_under.upper()
    price_target = str(ctx.options.price_target)

    if over_under != "OVER" and over_under != "UNDER":
        await ctx.respond("Only **OVER** and **UNDER** are accept for the over_under field")
        return

    if symbol not in monitor_data:
        await ctx.respond(f"The symbol {symbol} was not been monitored")
        return

    remove_task = {
        "type": "STOCK",
        "over_under": over_under,
        "price_target": price_target,
        "con_type": "",
        "strike": "",
        "date": ""
    }

    symbol_list = monitor_data[symbol]
    if remove_task not in symbol_list:
        await ctx.respond("There is no matching task to be removed")
        return

    monitor_data[symbol].remove(remove_task)
    update_data()

    await ctx.respond("The task has been removed!")


@plugin.command
@lightbulb.option("date", "The date of the option expire, must be in YYYY-MM-DD format", type=str)
@lightbulb.option("strike", "The strike of the task that you want to remove", type=float)
@lightbulb.option("con_type", "The contract type of the task you want to remove, CALL/PUT", type=str)
@lightbulb.option("price_target", "The price target of the task that you want to remove", type=float)
@lightbulb.option("over_under", "The over/under of the task you want to remove", type=str)
@lightbulb.option("symbol", "The symbol of the task that you want to remove", type=str)
@lightbulb.command("remove_option_task", "Remove a specific option monitoring task from the monitoring data")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_remove_option_task(ctx: lightbulb.Context):
    symbol = ctx.options.symbol.upper()
    over_under = ctx.options.over_under.upper()
    price_target = str(ctx.options.price_target)
    con_type = ctx.options.con_type.upper()
    strike = str(ctx.options.strike)
    date = ctx.options.date

    if over_under != "OVER" and over_under != "UNDER":
        await ctx.respond("Only **OVER** and **UNDER** are accept for the over_under field")
        return

    if con_type != "CALL" and con_type != "PUT":
        await ctx.respond("Only **CALL** and **PUT** are allowed for the con_type field")
        return

    if symbol not in monitor_data:
        await ctx.respond(f"The symbol {symbol} was not been monitored")
        return

    if not check_date(date):
        await ctx.respond(f"Please make sure that the date is in the format of YYYY-MM-DD")
        return

    remove_task = {
        "type": "OPTION",
        "over_under": over_under,
        "price_target": price_target,
        "con_type": con_type,
        "strike": strike,
        "date": date
    }

    symbol_list = monitor_data[symbol]
    if remove_task not in symbol_list:
        await ctx.respond("There is no matching task to be removed")
        return

    monitor_data[symbol].remove(remove_task)
    update_data()

    await ctx.respond("The task has been removed!")
