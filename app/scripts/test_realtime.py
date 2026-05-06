import requests
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import json

URL = "https://gtfs.mot.gov.il/gtfsrealtime/TripUpdates.pb"

def inspect_schema():
    print(f"Fetching {URL}...")
    response = requests.get(URL)
    
    print(response.content)


    # # Convert the first entity to a dictionary to see the full structure
    # if len(feed.entity) > 0:
    #     # We take just one entity to avoid a wall of text
    #     sample_entity = MessageToDict(feed.entity[0])
        
    #     print("\n--- ACTUAL DATA SCHEMA (JSON REPRESENTATION) ---")
    #     print(json.dumps(sample_entity, indent=2, ensure_ascii=False))
    # else:
    #     print("Feed was empty.")

if __name__ == "__main__":
    inspect_schema()