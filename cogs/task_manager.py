from ticker import Stock, Option
from cogs.setting_manger import setting_data
from threading import Thread
import lightbulb
import hikari
import json

plugin = lightbulb.Plugin("task_manager")


def load(bot):
    bot.add_plugin(plugin)


class TaskManager:
    def __init__(self):
        self.target_obj: dict[str, Stock] = {}
        self.task_list: dict[str, Thread] = {}
        self.running_task: dict[str, Thread] = {}

        self.load_task()

    def load_task(self):
        monitor_data = json.load(open("data/data.json", "r"))
        self.task_list = {}
        check_interval = setting_data["RUNTIME"]["check_interval"]
        for ticker in monitor_data:
            for ticker_data in monitor_data[ticker]:
                over_under = ticker_data["over_under"]
                price_target = ticker_data["price_target"]
                if ticker_data["type"] == "STOCK":
                    new_stock = Stock(ticker, over_under, price_target, check_interval)
                    task_proc = Thread(target=new_stock.start)
                    self.task_list[f"STOCK_{ticker}_{over_under}_{price_target}"] = task_proc
                    self.target_obj[f"STOCK_{ticker}_{over_under}_{price_target}"] = new_stock

                elif ticker_data["type"] == "OPTION":
                    con_type = ticker_data["con_type"]
                    strike = ticker_data["strike"]
                    date = ticker_data["date"]
                    new_option = Option(ticker, over_under, price_target, check_interval, con_type, strike, date)
                    task_proc = Thread(target=new_option.start)
                    self.task_list[
                        f"OPTION_{ticker}_{over_under}_{price_target}_{con_type}_{strike}_{date}"] = task_proc
                    self.target_obj[
                        f"OPTION_{ticker}_{over_under}_{price_target}_{con_type}_{strike}_{date}"] = new_option

    def restart_task(self):
        self.load_task()

        prev_running_task = []
        for task_id in self.running_task:
            if self.target_obj[task_id].get_running():
                self.target_obj[task_id].running = False
                prev_running_task.append(task_id)

        self.running_task = {}
        for task_id in prev_running_task:
            if task_id in self.task_list:
                self.start_task(task_id)

    def get_task_list(self):
        return self.task_list

    def get_target_obj(self):
        return self.target_obj

    def get_running_task(self):
        return self.running_task

    def check_task_running(self, task_id):
        return self.target_obj[task_id].get_running()

    def start_task(self, task_id):
        self.task_list[task_id].start()
        self.running_task[task_id] = self.task_list[task_id]

    def stop_task(self, task_id):
        if self.target_obj[task_id].get_running():
            self.target_obj[task_id].running = False

        del self.running_task[task_id]


task_manger = TaskManager()


@plugin.command
@lightbulb.command("show_loaded_task", "Show all loaded monitor task that can be started")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_show_loaded_task(ctx: lightbulb.Context):
    task_manger.load_task()
    embed = hikari.Embed(title="Loaded task", color=0x42f584)
    load_task = task_manger.get_task_list()
    if not load_task:
        await ctx.respond("There is no loaded task currently")
        return

    for task_num, task_id in enumerate(load_task, start=1):
        task_info = task_id.split("_")
        embed_msg = f"Stock/Option: {task_info[0].title()}\n" \
                    f"Ticker: {task_info[1]}\n" \
                    f"Trigger: {task_info[2].title()} {task_info[3]}"
        if len(task_info) == 7:
            embed_msg += f"\nContract: {task_info[6]} {task_info[5]} {task_info[4]}"

        embed.add_field(f"Task {task_num}", embed_msg)

    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.command("show_running_task", "Show all current running task")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_show_running_task(ctx: lightbulb.Context):
    running_task = task_manger.get_running_task()
    embed = hikari.Embed(title="Loaded task", color=0x42f584)
    if not running_task:
        await ctx.respond("There is no task running currently")
        return

    for task_num, task_id in enumerate(running_task, start=1):
        task_info = task_id.split("_")
        embed_msg = f"Stock/Option: {task_info[0].title()}\n" \
                    f"Ticker: {task_info[1]}\n" \
                    f"Trigger: {task_info[2].title()} {task_info[3]}"
        if len(task_info) == 7:
            embed_msg += f"\nContract: {task_info[6]} {task_info[5]} {task_info[4]}"

        embed.add_field(f"Task {task_num}", embed_msg)

    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.command("reload_task", "Reload current task list, will also restart existing task to the updated info")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_reload_task(ctx: lightbulb.Context):
    task_manger.load_task()
    await ctx.respond("Task reloaded")


@plugin.command
@lightbulb.command("restart_all_task", "Restart all running task with updated info")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_restart_task(ctx: lightbulb.Context):
    task_manger.restart_task()
    await ctx.respond("All task restarted")


@plugin.command
@lightbulb.command("start_all_task", "Start all loaded task")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_start_all_task(ctx: lightbulb.Context):
    task_obj = task_manger.get_target_obj()
    task_list = task_manger.get_task_list()

    num = 0
    for task_id in task_list:
        if not task_obj[task_id].get_running():
            task_manger.start_task(task_id)
            num += 1

    await ctx.respond(f"All {num} idle task(s) has been started")


@plugin.command
@lightbulb.option("task_num", "The task # of the task you want to start")
@lightbulb.command("start_task", "Start a specific loaded task")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_start_task(ctx: lightbulb.Context):
    task_list = task_manger.get_task_list()
    task_id_dict = {str(task_id): key for task_id, key in enumerate(task_list, start=1)}
    task_id = task_id_dict[ctx.options.task_num]

    if task_manger.check_task_running(task_id):
        await ctx.respond("You cannot start a task that has already been started!")
        return

    task_manger.start_task(task_id)
    await ctx.respond(f"Successfully started the task!\n")


@plugin.command
@lightbulb.command("stop_all_task", "Stop all running task")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_stop_all_task(ctx: lightbulb.Context):
    running_task_id = [task_id for task_id in task_manger.get_running_task()]
    for task_id in running_task_id:
        task_manger.stop_task(task_id)

    await ctx.respond("All task has been stopped")


@plugin.command
@lightbulb.option("task_num", "The task # of the task you want to stop")
@lightbulb.command("stop_task", "Stop a specific task")
@lightbulb.implements(lightbulb.SlashCommand)
async def command_stop_task(ctx: lightbulb.Context):
    task_list = task_manger.get_task_list()
    task_id_dict = {str(task_id): key for task_id, key in enumerate(task_list, start=1)}
    task_id = task_id_dict[ctx.options.task_num]
    running_list = task_manger.get_running_task()

    if task_id not in running_list:
        await ctx.respond("This task has not been started yet")
        return

    task_manger.stop_task(task_id)
    await ctx.respond("Task has been stopped!")
