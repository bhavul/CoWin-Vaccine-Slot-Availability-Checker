import asyncio
import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import time
import pytz


IST = pytz.timezone('Asia/Kolkata')

##############
# ST CONFIGS
##############
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

##############
# FUNCTIONS
##############

@st.cache
def get_district_id_map():
    df = pd.read_csv('./district_mapping.csv')
    district_id_map = pd.Series(df['district id'].values, index=df['district name']).to_dict()
    return district_id_map



def check(list_of_district_ids, min_age_limit):
    NUMPERIODS = 2  # check for next 9 days
    all_centers = []
    covaxin_centers = []
    covishield_centers = []
    generic_centers = []
    today_date = datetime.today()
    date_list = [today_date + timedelta(days=6*x) for x in range(NUMPERIODS)]
    date_str_list = [x.strftime("%d-%m-%Y") for x in date_list]
    for district_id in list_of_district_ids:
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
                        min_age_limit_session = session['min_age_limit']
                        date = session['date']
                        if vaccine == 'COVAXIN' and available_capacity > 0 and min_age_limit_session == min_age_limit:
                            new_centre['name'] = name
                            new_centre['district_name'] = district_name
                            new_centre['pincode'] = pincode
                            new_centre['vaccine'] = vaccine
                            new_centre['available_capacity'] = available_capacity
                            new_centre['date'] = date
                            covaxin_centers.append(new_centre)
                            break
                        elif vaccine == 'COVISHIELD' and available_capacity > 0  and min_age_limit_session == min_age_limit:
                            new_centre['name'] = name
                            new_centre['district_name'] = district_name
                            new_centre['pincode'] = pincode
                            new_centre['vaccine'] = vaccine
                            new_centre['available_capacity'] = available_capacity
                            new_centre['date'] = date
                            covishield_centers.append(new_centre)
                            break
                        elif available_capacity > 0 and min_age_limit_session == min_age_limit:
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
                time.sleep(30)
                print(f'Slept for 30 seconds')
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


def write_output(list_of_district_ids, min_age_limit, covaxin_df_container, covishield_df_container, generic_df_container, head1, head2, head3, test):
    while True:
        with st.spinner('Loading new data...'):
            covaxin_df, covishield_df, generic_df, is_valid = check(list_of_district_ids, min_age_limit)
        test.markdown(
            f"""
            <p class="time">
                Last Updated at : {str(datetime.now(IST).strftime("%d-%m-%Y %H:%M:%S"))} (auto-refreshes)
            </p>
            """, unsafe_allow_html=True)
        if not is_valid:
            error.write('Some API error last time an API call was made...Should auto-fix in a minute or so.')
            time.sleep(5)    
        else:
            # covaxin
            head1.markdown(
                f"""
                ## Covaxin Centres
                """, unsafe_allow_html=True)
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
                ## Generic Centres (Vaccine type not mentioned)
                """, unsafe_allow_html=True)
            generic_df_container.dataframe(generic_df)

        time.sleep(15)


###########
# Layout
###########
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb


def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))


def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):
    style = """
    <style>      
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     .stApp { bottom: 70px; }
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        text_align="center",
        height="auto",
        opacity=1
    )

    style_hr = styles(
        display="none"
    )

    style_p = styles(
        font_size="12px"
    )

    body = p(
        style=style_p
    )
    foot = div(
        style=style_div
    )(
        hr(
            style=style_hr
        ),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    myargs = [
        "Made with ❤️ by ",
        image("https://mk0hootsuiteblof6bud.kinstacdn.com/wp-content/uploads/2018/09/Twitter_Logo_Blue-310x310.png", width=px(25), height=px(25)),
        link("https://twitter.com/BhavulGauri", "@BhavulGauri"),
        " (worth a follow?)",
        br(),
        "These are tough times. Get yourself and your family vaccinated soon. If this tool helps you, kindly donate whatever you can afford to ",
        link("https://donate.indiacovidresources.in/", "one of the NGOs for covid relief here."),
    ]
    layout(*myargs)

########
## JS
########

# """Add this in your streamlit app.py"""
# GA_JS = """Hello world!"""

# # Insert the script in the head tag of the static template inside your virtual environement
# index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
# soup = BeautifulSoup(index_path.read_text(), features="lxml")
# if not soup.find(id='custom-js'):
#     script_tag = soup.new_tag("script", id='custom-js')
#     script_tag.string = GA_JS
#     soup.head.append(script_tag)
#     index_path.write_text(str(soup))


############
## MAIN
###########


footer()

district_id_map = get_district_id_map()

st.markdown(f"""
    # CoWin Vaccine Slots Availability Checker

    Designed to help see (almost) realtime updating information about slots that are available.  

    - You can also select multiple districts and see for all of them at once.
    - The information updates every 30 seconds or so on its own, don't keep refreshing the page.
    - Results are shown categorised by vaccine types.
    - Slots for upto 9 days in future are only shown.

    But first, enter your choices in the sidebar on the left, and click "Submit".
    """)
test = st.empty()
error = st.empty()

container1 = st.beta_container()
container2 = st.beta_container()
container3 = st.beta_container()

head1 = container1.empty()
covaxin_df_container = container1.empty()

head2 = container2.empty()
covishield_df_container = container2.empty()

head3 = container3.empty()
generic_df_container = container3.empty()

st.sidebar.markdown(f"""
    # Select your choices
    """)
radio_age = st.sidebar.radio('Select age limit', ['18+', '45+'])
options = st.sidebar.multiselect('Select Districts', list(district_id_map.keys()))

if st.sidebar.button('Submit'):
    # actual call which does the job!
    list_of_district_ids = [district_id_map[district_name] for district_name in options]
    min_age_limit = 18 if radio_age == '18+' else 45    
    write_output(list_of_district_ids, min_age_limit, covaxin_df_container, covishield_df_container, generic_df_container, head1, head2, head3, test)