import streamlit as st
import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt
import datetime
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


# 1/1 Interactive table
# 1/2 Chart elements (Latest listing)
# 1/1 Map
# 1/1 Button (Submit Contact)
# 1/1 Checkbox (Contact agreement)
# 2/2 Message box (Error message for search and success and error of email sent)
# 6/5 Input widgets (Slider, date input, text input, selectbox, text area, file uploader)


# Coin Market Cal API constants
COIN_MARKET_CAL_BASE_URL = "https://developers.coinmarketcal.com/v1"
CRYPTO_EVENTS_CATEGORIES_URL = f"{COIN_MARKET_CAL_BASE_URL}/categories"
CRYPTO_EVENTS_URL = f"{COIN_MARKET_CAL_BASE_URL}/events"
CRYPTO_EVENTS_REQUEST_HEADERS = {
    "x-api-key": "4usto4BDYv9eS6kS494KU480aVrzxqRV1BsG4Kyc", # st.secrets["coin_market_cal_api_key"],
    "Accept-Encoding": "deflate, gzip",
    "Accept": "application/json"
}


st.title("Crypto App")

st.title("Latest Listing")
slider_range = st.slider("Price Range (USD)", value=5, max_value=10)


def create_bar(limit):
    latest_list = [""]
    data_dict = {'Name': [], 'Current Price (USD)': []}
    print(limit)
    latest_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit={0}&CMC_PRO_API_KEY=7913ed85-ea99-4e89-843c-d8e81ec4ac66".format(int(limit))
    latest_dict = requests.get(latest_url).json()
    name_list = []
    price_list = []

    for i in latest_dict["data"]:
        name_list.append(i["name"])
        price_list.append(i["quote"]["USD"]["price"])

    data_dict["Name"] += name_list
    data_dict["Current Price (USD)"] += price_list

    x = np.arange(len(name_list))  # the label locations
    fig, ax = plt.subplots()
    fig.set_size_inches(15, 15)
    ax.set_xlabel('Names')
    ax.set_xticks(x, labels=name_list)
    rects1 = ax.bar(x, price_list, 0.05)
    ax.set_ylabel('Current Price (USD)')
    ax.bar_label(rects1, padding=1)
    st.pyplot(fig)

def create_linegraph(id):
    latest_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id={0}&CMC_PRO_API_KEY=7913ed85-ea99-4e89-843c-d8e81ec4ac66".format(id)
    latest_dict = requests.get(latest_url).json()
    intervals = ["1 hour", "24 hours", "7 days", "30 days"]
    percent_change_list = []
    percent_change_list.append(latest_dict["data"][str(id)]["quote"]["USD"]["percent_change_1h"])
    percent_change_list.append(latest_dict["data"][str(id)]["quote"]["USD"]["percent_change_24h"])
    percent_change_list.append(latest_dict["data"][str(id)]["quote"]["USD"]["percent_change_7d"])
    percent_change_list.append(latest_dict["data"][str(id)]["quote"]["USD"]["percent_change_30d"])

    st.title("Percentage Change of USD Value")
    fig, ax = plt.subplots()
    ax.set_xlabel('Intervals')
    ax.set_ylabel('Percent Change(%)')
    ax.plot(intervals, percent_change_list)
    st.pyplot(fig)


def fetch_event_categories():
    crypto_events_categories = requests.get(
        CRYPTO_EVENTS_CATEGORIES_URL,
        headers=CRYPTO_EVENTS_REQUEST_HEADERS
    )
    return crypto_events_categories.json().get("body", [])


def fetch_events(start_date, end_date, category):
    crypto_events_response = requests.get(
        CRYPTO_EVENTS_URL,
        params={
            "dateRangeStart": start_date,
            "dateRangeEnd": end_date,
            "categories": [category.get("id")]
        },
        headers=CRYPTO_EVENTS_REQUEST_HEADERS
    )
    crypto_events_response = crypto_events_response.json()
    return [
        {
            "title": ce.get("title", {}).get("en"),
            "coins": ", ".join([c.get("fullname") for c in ce.get("coins", [])]),
            "date": datetime.datetime.strptime(ce.get("date_event"), "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b, %Y"),
            "categories": ", ".join([c.get("name") for c in ce.get("categories", [])]),
            "description": ce.get("description", {}).get("en")
        }
        for ce in crypto_events_response.get("body", [])
    ]


"""
    Crypto currencies list Section
"""
create_bar(slider_range)


"""
    Search Crypto currencies Section
"""
st.title("Search Cryptocurrencies")

symbol = st.text_input('Search Crypto (Use symbol)', 'BTC')
st.write("For list of all crypto symbols [click here](https://www.finder.com.au/cryptocurrency-list-all)")
research_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/info?symbol={0}&CMC_PRO_API_KEY=7913ed85-ea99-4e89-843c-d8e81ec4ac66".format(symbol)
research_dict = requests.get(research_url).json()
if(research_dict["status"]["error_message"] != None):
    st.error("Either symbol is written wrong or desired cryptocurrency doesn't exist. Please retry with another.")
searched = list(research_dict["data"].keys())[0]
tag_list = research_dict["data"][searched]["tags"]
tag_name_list = research_dict["data"][searched]["tag-names"]
tag_group_list = research_dict["data"][searched]["tag-groups"]
result_dict = {"Tags": tag_list, "Names": tag_name_list, "Groups": tag_group_list}
st.write("Description: " + research_dict["data"][searched]["description"])
st.dataframe(data=result_dict)
create_linegraph(research_dict["data"][searched]["id"])
# st.write(research_dict["data"][searched])


"""
    Crypto Events Section
"""
st.title("Crypto Events")

categories = fetch_event_categories()
current_date = datetime.datetime.now()
max_date = current_date + datetime.timedelta(days=7)

start_date = st.date_input("Start Date:", value=current_date, min_value=current_date, max_value=(current_date + datetime.timedelta(days=6)))
end_date = st.date_input("End Date:", value=(current_date + datetime.timedelta(days=1)), max_value=max_date)
category = st.selectbox(
    "Category:", categories, 3, format_func=lambda c: c.get("name")
)

crypto_events = fetch_events(start_date, end_date, category)
st.table(data=crypto_events)


"""
    Locations of Top Crypto Miners section
"""
st.title("Locations of Top Crypto Miners")

location_dict = {
    "lat": [38.9295209, 64.146557, 55.6447941, 47.1947866, 46.8653046, 51.4544323],
    "lon": [121.330581, -21.8985398, 37.2384401, -119.29729, 8.8595681, 5.5136456]
}
location_data = pd.DataFrame(data=location_dict)
st.map(data=location_data)


"""
    Contact Us Section
"""
st.title("Contact Us")

email = st.text_input("Email:")
name = st.text_input("Name:")
body = st.text_area("Message:")
attachment = st.file_uploader("Attachments")
agree = st.checkbox("I agree to be contact at the provided email")

submitted = st.button("Submit")
if submitted:
    if email == "" or name == "" or body == "":
        st.error("Make sure to fill out all fields")
    elif not(re.fullmatch(regex,email)):
        st.error("Enter valid email")
    elif agree == False:
        st.error("Make sure to agree")
    else:
        st.success("Email was sent")
