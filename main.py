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

is_test = False
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
            
            # assume the middle 2 flights are fixed
            {
                "id": "2",
                "originLocationCode": "TPE",
                "destinationLocationCode": "YVR",
                "departureDateTimeRange": {"date": "2025-07-04"},
            },
            {
                "id": "3",
                "originLocationCode": "YVR",
                "destinationLocationCode": "TPE",
                "departureDateTimeRange": {"date": "2025-07-19"},
            },
            
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
    res.raise_for_status()
    data = res.json()
    return data

# Update the locations & dates you are interested 
ALL_locations = ["CNX", "NGO", "HKG", "OKA", "DAD", "BKK", "PEN", "CTS", "HAN", "SDJ", "HKD", "SGN"]
for start_loc in ALL_locations:
    for start_date in ["2025-04-05", "2025-04-06"]:
        for end_loc in ALL_locations:
            for end_date in ["2025-10-02", "2025-10-03", "2025-10-08", "2025-10-09"]:
                file_prefix = f"{folder}/{start_loc}_{start_date}_{end_loc}_{end_date}"
                if Path(f"{file_prefix}_raw.json").exists():
                    print(f"Skip {start_loc}_{start_date}_{end_loc}_{end_date} because cached")
                    continue
                data = search(start_loc, start_date, end_loc, end_date)
                print(f"Search {file_prefix}")
                with open(f"{file_prefix}_raw.json", "w") as f:
                    f.write(json.dumps(data, indent=4, ensure_ascii=False))
                
                