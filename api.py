from typing import Optional
from fastapi import FastAPI
import requests

from cacheout import Cache

cache = Cache(maxsize=2048, ttl=0)


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@cache.memoize(ttl=35, typed=True)
def get_from_api_call(min_age_limit, district_id, date):
    # store centres for a district and date
    covaxin_centers = []
    covishield_centers = []
    generic_centers = []
    # make actual API call
    print(f'HITTING URL THIS TIME...')
    url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={date}"    
    payload={}
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}
    results = []
    response = requests.request("GET", url, headers=headers, data=payload)    
    # logic
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
        return {'covaxin_centers':covaxin_centers, 'covishield_centers':covishield_centers, 'generic_centers':generic_centers}
    else:
        print(f'API call failed...')
        print(f'response status code : {response.status_code}')
        print(f'response text : {response.text}')
        print(f'Slept for 30 seconds')
        raise Exception('could not load data')




@app.get("/check/{min_age_limit}/{district_id}/{date}")
def read_item(min_age_limit: int, district_id: int, date: str, q: Optional[str] = None):
    print(f'min_age_limit: {min_age_limit}, district_id:{district_id}, date:{date}')
    centres_dict = get_from_api_call(min_age_limit, district_id, date)
    return centres_dict

