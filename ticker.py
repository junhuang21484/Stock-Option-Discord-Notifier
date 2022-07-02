from dhooks import Webhook, Embed
import td_helper as td_api
import time
import json

discord_setting = json.load(open("data/setting.json", "r", encoding="UTF-8"))["DISCORD_SETTING"]


class Stock:
    def __init__(self, symbol: str, over_under: str, price_target: str, check_interval: int):
        self.symbol = symbol
        self.over_under = over_under.upper()
        self.price_target = price_target
        self.check_interval = check_interval

        self.running = False

    def get_running(self):
        return self.running

    def check_price_hit(self):
        stock_price = td_api.get_stock_price(self.symbol)
        if stock_price:
            return stock_price < float(self.price_target) if self.over_under == "UNDER" else stock_price > float(
                self.price_target), stock_price

        return False, None

    def notify(self, price):
        webhook = Webhook(discord_setting["webhook"])
        noti_embed = Embed(title="Stock/Option Discord Notifier",
                           description=f"The notification setting has been set to notify when the stock price "
                                       f"is **{self.over_under} {self.price_target}**",
                           color=0x0388fc)

        noti_embed.add_field("Ticker", self.symbol)
        noti_embed.add_field("Current Price", str(price) + " (when alerting)")
        noti_embed.add_field("Over/Under", self.over_under)
        noti_embed.add_field("Links",
                             f"[[TD Ameritrade]](https://research.tdameritrade.com/grid/public/research/stocks/summary?symbol={self.symbol}) "
                             f"[[Developer Github]](https://github.com/junhuang21484)")

        mention_msg = ""
        if discord_setting["mention"]["user"]:
            for user_id in discord_setting["mention"]["user"]:
                mention_msg += f"<@{user_id}>"

        if discord_setting["mention"]["role"]:
            for role_id in discord_setting["mention"]["role"]:
                mention_msg += f"<@&{role_id}>"

        webhook.send(mention_msg, embed=noti_embed)

    def start(self):
        self.running = True
        while self.running:
            target_hit, price = self.check_price_hit()
            if target_hit:
                self.notify(price)
                self.running = False
                break

            time.sleep(self.check_interval)


class Option(Stock):
    def __init__(self, symbol: str, over_under: str, price_target: str, check_interval: int, con_type: str, strike: str,
                 date: str):
        super().__init__(symbol, over_under, price_target, check_interval)

        self.con_type = con_type
        self.strike = strike
        self.date = date

    def check_price_hit(self):
        stock_price = td_api.get_option_price(self.symbol, self.strike, self.con_type, self.date)
        if stock_price:
            return stock_price < float(self.price_target) if self.over_under == "UNDER" else stock_price > float(
                self.price_target), stock_price

        return False, None
