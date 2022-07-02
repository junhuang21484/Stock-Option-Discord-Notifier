import requests
import json

api_key = json.load(open("data/setting.json", "r", encoding="UTF-8"))["TD_SETTING"]["api_key"]


def check_api_key(check_key: str) -> bool:
    req_url = f"https://api.tdameritrade.com/v1/marketdata/SPY/quotes?apikey={check_key}"
    req = requests.get(req_url)
    return req.status_code == 200


def get_stock_price(ticker: str):
    req_url = f"https://api.tdameritrade.com/v1/marketdata/{ticker}/quotes?apikey={api_key}"
    req = requests.get(req_url)
    if req.status_code == 200 and req.json():
        stock_data = req.json()[ticker]
        return stock_data["lastPrice"]

    return


def get_option_price(ticker: str, strike: str, con_type: str, date: str):
    req_url = f"https://api.tdameritrade.com/v1/marketdata/chains?apikey={api_key}" \
              f"&symbol={ticker}&contractType={con_type}&strike={strike}&fromDate={date}&toDate={date}"

    req = requests.get(req_url)
    if req.status_code == 200:
        try:
            option_data = req.json()["callExpDateMap"] if con_type == "CALL" else req.json()["putExpDateMap"]
            opt_date = list(option_data.keys())[0]
            return option_data[opt_date][strike][0]['last']
        except IndexError:
            return
    return
