import requests
import json
from pathlib import Path

# SGN: 胡志明市國際機場
# TPE: 台北桃園國際機場
# YVR: 溫哥華國際機場
# HAN: 河內國際機場

# CI: 中華航空
# BR: 長榮航空
# JX: 星宇航空

is_test = False
folder = "./test" if is_test else "./prod"

token = ""

endpoint = (
    "https://test.api.amadeus.com/v2/shopping/flight-offers"
    if is_test
    else "https://api.amadeus.com/v2/shopping/flight-offers"
)

def search(first_location, first_date, last_location, last_date):
    payload = {
        "currencyCode": "TWD",
        "originDestinations": [
            {
                "id": "1",
                "originLocationCode": first_location,
                "destinationLocationCode": "TPE",
                "departureDateTimeRange": {"date": first_date},
            },
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


# 長榮
EVA_locations = ["CNX", "HKG", "FUK", "OKA", "DAD", "BKK", "PEN", "CTS", "HAN", "SDJ", "KMQ", "AMS", "SGN"]
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
                
                
