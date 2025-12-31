import requests
import json
from pathlib import Path

"""
How to use it:
1. Get test app token from https://developers.amadeus.com/
2. My assumption is 2nd & 3rd flights' location and date are fixed, we search for pontential 1st and 4th flight location and dates
3. After searching price, result will be stored in ./test or ./prod
4. Use view.py to view result
5. If you want to get real price, you need to activate prod token. 
   (need credict card & sign contract, but there is free quota)
"""

is_test = True
folder = "./test" if is_test else "./prod"

# Get access token from https://developers.amadeus.com/
# For production usage, you need to use credit card & sign contract to get token
# But there is free quota.
token = ""

# Use test for testing script correctness, use prod for correct price
endpoint = (
    "https://test.api.amadeus.com/v2/shopping/flight-offers"
    if is_test
    else "https://api.amadeus.com/v2/shopping/flight-offers"
)

# Update the locations & dates you are interested 
FIRST_AND_LAST_FLIGHT_LOCATIONS = ["KIX", "NRT"]
FISRT_FLIGHT_DATES = ["2026-05-04"]
LAST_FLIGH_DATES = ["2026-10-21"]
SECOND_FLIGHT = {
                "id": "2",
                "originLocationCode": "TPE",
                "destinationLocationCode": "AKL",
                "departureDateTimeRange": {"date": "2026-09-23"},
            }
THIRD_FLIGHT = {
                "id": "3",
                "originLocationCode": "AKL",
                "destinationLocationCode": "TPE",
                "departureDateTimeRange": {"date": "2026-10-08"},
            }

# SGN: 胡志明市國際機場
# TPE: 台北桃園國際機場
# YVR: 溫哥華國際機場
# HAN: 河內國際機場

# CI: 中華航空
# BR: 長榮航空
# JX: 星宇航空

def search(first_location, first_date, last_location, last_date):
    payload = {
        "currencyCode": "TWD",
        "originDestinations": [
            # 4 flights
            {
                "id": "1",
                "originLocationCode": first_location,
                "destinationLocationCode": "TPE",
                "departureDateTimeRange": {"date": first_date},
            },
            
            # assume 2nd & 3rd flights are fixed
            SECOND_FLIGHT,
            THIRD_FLIGHT,
            
            {
                "id": "4",
                "originLocationCode": "TPE",
                "destinationLocationCode": last_location,
                "departureDateTimeRange": {"date": last_date},
            },
        ],
        "travelers": [
            {"id": "1", "travelerType": "ADULT"},
            {"id": "2", "travelerType": "ADULT"},
        ],
        "sources": ["GDS"],
        "searchCriteria": {
            "maxFlightOffers": 250,
            "flightFilters": {
                "cabinRestrictions": [
                    {
                        "cabin": "ECONOMY",
                        "coverage": "MOST_SEGMENTS",
                        "originDestinationIds": ["1", "2", "3", "4"],
                    }
                ],
                "connectionRestriction": {"maxNumberOfConnections": 0},
                "carrierRestrictions": {"includedCarrierCodes": ["BR", "CI", "JX"]},
            },
        },
    }

    res = requests.post(
        endpoint, headers={"Authorization": f"Bearer {token}"}, json=payload
    )
    print(res.text)
    res.raise_for_status()
    data = res.json()
    return data

for start_loc in FIRST_AND_LAST_FLIGHT_LOCATIONS:
    for start_date in FISRT_FLIGHT_DATES:
        for end_loc in FIRST_AND_LAST_FLIGHT_LOCATIONS:
            for end_date in LAST_FLIGH_DATES:
                file_prefix = f"{folder}/{start_loc}_{start_date}_{end_loc}_{end_date}"
                if Path(f"{file_prefix}_raw.json").exists():
                    print(f"Skip {start_loc}_{start_date}_{end_loc}_{end_date} because cached")
                    continue
                data = search(start_loc, start_date, end_loc, end_date)
                print(f"Search {file_prefix}")
                with open(f"{file_prefix}_raw.json", "w") as f:
                    f.write(json.dumps(data, indent=4, ensure_ascii=False))
                
                