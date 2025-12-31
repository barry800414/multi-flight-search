import requests
import json
from pathlib import Path

"""
How to use it:
1. Get test app token from https://developers.amadeus.com/
2. After searching price, result will be stored in ./test or ./prod
3. Use view.py to view result
4. If you want to get real price, you need to activate prod token. 
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
# NRT: 東京成田機場
# KIX: 大阪關西機場
# AKL: 奧克蘭機場

# Flight configurations: [origins, destinations, dates]
FLIGHT_CONFIGS = [
    {
        "origins": ["KIX"],
        "destinations": ["TPE"], 
        "dates": ["2026-05-04"],
    },
    {
        "origins": ["TPE"], 
        "destinations": ["AKL"],
        "dates": ["2026-09-24"],
    },
    {
        "origins": ["AKL"], 
        "destinations": ["TPE"],
        "dates": ["2026-10-08"],
    },
    {
        "origins": ["TPE"],
        "destinations": ["NRT"],
        "dates": ["2026-10-22"],
    },
]

def search(flights):
    """
    flights: list of dicts with keys: origin, destination, date
    """
    payload = {
        "currencyCode": "TWD",
        "originDestinations": [
            {
                "id": str(i + 1),
                "originLocationCode": flight["origin"],
                "destinationLocationCode": flight["destination"],
                "departureDateTimeRange": {"date": flight["date"]},
            }
            for i, flight in enumerate(flights)
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
                        "originDestinationIds": [
                            str(i + 1) for i in range(len(flights))
                        ],
                    }
                ],
                "connectionRestriction": {"maxNumberOfConnections": 0},
                # CI: 中華航空
                # BR: 長榮航空
                # JX: 星宇航空
                # uncomment this line to limit airlines
                # "carrierRestrictions": {"includedCarrierCodes": ["BR", "CI", "JX"]},
            },
        },
    }

    res = requests.post(
        endpoint, headers={"Authorization": f"Bearer {token}"}, json=payload
    )
    res.raise_for_status()
    data = res.json()
    return data


def generate_combinations(flight_configs, current_flights=None, flight_index=0):
    """
    Recursively generate all combinations of flights and search for each.

    Args:
        flight_configs: List of flight configuration dictionaries
        current_flights: Current combination being built
        flight_index: Index of current flight being processed
    """
    if current_flights is None:
        current_flights = []

    # Base case: all flights configured, perform search
    if flight_index >= len(flight_configs):
        # Create file prefix from flight details
        flight_details = []
        for flight in current_flights:
            flight_details.extend(
                [flight["origin"], flight["destination"], flight["date"]]
            )
        file_prefix = f"{folder}/{'_'.join(flight_details)}"

        # Check if already cached
        if Path(f"{file_prefix}_raw.json").exists():
            print(f"Skip {file_prefix} because cached")
            return

        # Perform search
        try:
            data = search(current_flights)
            print(f"Search {file_prefix}")
            with open(f"{file_prefix}_raw.json", "w") as f:
                f.write(json.dumps(data, indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"Error searching {file_prefix}: {e}")
        return

    # Recursive case: try all combinations for current flight
    config = flight_configs[flight_index]

    for origin in config["origins"]:
        for destination in config["destinations"]:
            for date in config["dates"]:
                flight = {"origin": origin, "destination": destination, "date": date}
                generate_combinations(
                    flight_configs, current_flights + [flight], flight_index + 1
                )


# Start the recursive search
generate_combinations(FLIGHT_CONFIGS)
