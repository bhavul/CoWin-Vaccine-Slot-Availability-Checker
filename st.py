import asyncio
import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .time {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #ec5953 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def check():
    NUMPERIODS = 4  # check for next 9 days
    DELHI_DISTRICT_CODES = [141, 145, 140, 146, 147, 143, 144, 149, 150, 142, 148, 661, 265]
    all_centers = []
    covaxin_centers = []
    covishield_centers = []
    generic_centers = []
    today_date = datetime.today()
    date_list = [today_date + timedelta(days=3*x) for x in range(NUMPERIODS)]
    date_str_list = [x.strftime("%d-%m-%Y") for x in date_list]
    for district_id in DELHI_DISTRICT_CODES:
        for temp_date in date_str_list:
            url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={temp_date}"    
            payload={}
            headers = {}
            results = []
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.ok and 'centers' in response.json():
                json_response = response.json()
                centers = json_response['centers']
                for center in centers:
                    new_centre = {}
                    if 'sessions' not in center:
                        continue
                    name = center['name']
                    district_name = center['district_name']
                    pincode = center['pincode']
                    for session in center['sessions']:
                        vaccine = session['vaccine']
                        available_capacity = session['available_capacity']
                        min_age_limit = session['min_age_limit']
                        date = session['date']
                        if vaccine == 'COVAXIN' and available_capacity > 0 and min_age_limit == 18:
                            new_centre['name'] = name
                            new_centre['district_name'] = district_name
                            new_centre['pincode'] = pincode
                            new_centre['vaccine'] = vaccine
                            new_centre['available_capacity'] = available_capacity
                            new_centre['date'] = date
                            covaxin_centers.append(new_centre)
                            break
                        elif vaccine == 'COVISHIELD' and available_capacity > 0  and min_age_limit == 18:
                            new_centre['name'] = name
                            new_centre['district_name'] = district_name
                            new_centre['pincode'] = pincode
                            new_centre['vaccine'] = vaccine
                            new_centre['available_capacity'] = available_capacity
                            new_centre['date'] = date
                            covishield_centers.append(new_centre)
                            break
                        elif available_capacity > 0 and min_age_limit == 18:
                            new_centre['name'] = name
                            new_centre['district_name'] = district_name
                            new_centre['pincode'] = pincode
                            new_centre['vaccine'] = vaccine
                            new_centre['available_capacity'] = available_capacity
                            new_centre['date'] = date
                            generic_centers.append(new_centre)
                            break
            else:
                print(f'API call failed...')
                print(f'response status code : {response.status_code}')
                print(f'response text : {response.text}')
                time.sleep(15)
                print(f'Slept for 15 seconds')
                return None, None, None, False

    all_centers.extend(covaxin_centers)
    all_centers.extend(covishield_centers)
    all_centers.extend(generic_centers)

    covaxin_df = pd.DataFrame(covaxin_centers)
    covishield_df = pd.DataFrame(covishield_centers)
    generic_df = pd.DataFrame(generic_centers)

    covaxin_df.drop_duplicates(subset=['name', 'pincode', 'date', 'vaccine'])
    covishield_df.drop_duplicates(subset=['name', 'pincode', 'date', 'vaccine'])
    generic_df.drop_duplicates(subset=['name', 'pincode', 'date', 'vaccine'])    

    if covaxin_df.shape[0] > 0:
        covaxin_df.sort_values(by=['vaccine', 'available_capacity'], inplace=True, ascending=True)
    if covishield_df.shape[0] > 0:
        covishield_df.sort_values(by=['vaccine', 'available_capacity'], inplace=True, ascending=True)
    if generic_df.shape[0] > 0:
        generic_df.sort_values(by=['vaccine', 'available_capacity'], inplace=True, ascending=True)


    return covaxin_df, covishield_df, generic_df, True


async def watch(covaxin_df_container, covishield_df_container, generic_df_container, head1, head2, head3, test):
    while True:
        covaxin_df, covishield_df, generic_df, is_valid = check()
        test.markdown(
            f"""
            <p class="time">
                Updated at : {str(datetime.now())}
            </p>
            """, unsafe_allow_html=True)
        if not is_valid:
            error.write('Some API error...')    
        else:
            # covaxin
            head1.markdown(
                f"""
                ## Covaxin Centres
                """, unsafe_allow_html=True)
            if covaxin_df.shape[0] > 0:
                extra.write('# Go go go!! BOOK!!')
            covaxin_df_container.dataframe(covaxin_df)

            # covishield
            head2.markdown(
                f"""
                ## Covishield Centres
                """, unsafe_allow_html=True)
            covishield_df_container.dataframe(covishield_df)

            # covaxin
            head3.markdown(
                f"""
                ## Generic Centres
                """, unsafe_allow_html=True)
            generic_df_container.dataframe(generic_df)

        r = await asyncio.sleep(10)


st.markdown(f"""
    # Covid Vaccine Slots Availability Checker (18+)

    Written with love by Bhavul.
    """)
test = st.empty()
error = st.empty()

container1 = st.beta_container()
container2 = st.beta_container()
container3 = st.beta_container()

head1 = container1.empty()
extra = container1.empty()
covaxin_df_container = container1.empty()

head2 = container2.empty()
covishield_df_container = container2.empty()

head3 = container3.empty()
generic_df_container = container3.empty()


asyncio.run(watch(covaxin_df_container, covishield_df_container, generic_df_container, head1, head2, head3, test))
