import requests
import json
import pandas as pd
import datetime
import streamlit as st

def get_energy_prices(date):
    api_url = 'https://mgrey.se/espot?format=json&date='+date
    response = requests.get(api_url)
    if response.status_code == 200:
        # Parse the JSON data
        data = json.loads(response.text)
        df_energy_prices = pd.json_normalize(data['SE3'])
        df_energy_prices['date'] = date
        return df_energy_prices
    else:
        print(f"Error: API request failed with status code {response.status_code}")


def find_best_time(df, consecutive_hours_needed, max_end_date, max_end_hour):
    df = df[(df['date'] < max_end_date) | ((df['date'] == max_end_date)  &  (df['hour'] <= max_end_hour))]
    df['rolling_sum'] = df['price_sek'].rolling(consecutive_hours_needed).mean()
    df['start_time_rolling_sum'] = df['hour'].shift(consecutive_hours_needed)
    df['start_date_rolling_sum'] = df['date'].shift(consecutive_hours_needed)
    df_best_hour = df[df.rolling_sum.min() == df.rolling_sum]
    return df_best_hour
    

def plan_appliances(hours: int = 1, max_end_hour: int = 24 , max_end_date: str = 'NA'):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1) 
    today_string = today.strftime('%Y-%m-%d')
    tomorrow_string = tomorrow.strftime('%Y-%m-%d')
    current_hour = datetime.datetime.now().hour
    df_all_prices = pd.concat([get_energy_prices(today_string),(get_energy_prices(tomorrow_string))])
    df_all_prices = df_all_prices[(df_all_prices['date'] > today_string) | (df_all_prices['hour'] > current_hour)]
    df_return = find_best_time(df_all_prices, hours,tomorrow_string, max_end_hour) 
    return "Start at hour " + str(int(df_return.start_time_rolling_sum.values[0])) + " for optimal prices in the next " + str(hours) + " hours"
    


import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    body {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

def main():
    from PIL import Image

    image = Image.open('image.png')
    st.title("Plan Your Energy Consumption")
    st.image(image, caption='Image by wirestock on Freepik')


    # Input fields
    consecutive_hours = st.number_input("Consecutive Hours:", min_value=1,max_value = 24, step=1)
    max_end_time = st.number_input("Max End Time:", min_value=1,max_value= 24,value =24, step=1)

    # Output block
    if consecutive_hours and max_end_time:
        st.write(f"You have chosen the following input:")
        st.write(f"- Consecutive Hours: {consecutive_hours}")
        st.write(f"- Max End Time: {max_end_time}")
        st.write(plan_appliances(consecutive_hours, max_end_time))

if __name__ == "__main__":
    main()
