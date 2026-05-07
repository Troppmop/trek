import requests
from google.transit import gtfs_realtime_pb2

URL = "https://gtfs.mot.gov.il/gtfsrealtime/TripUpdates.pb"

def test_realtime_with_headers():
    # Mimic a real web browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/x-protobuf, */*',
    }

    try:
        print(f"Fetching feed with browser headers...")
        response = requests.get(URL, headers=headers, timeout=15)
        
        # Check if we got HTML (error) or Binary (success)
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type:
            print("❌ Still getting blocked! The server returned HTML instead of data.")
            return

        # Try to parse the binary content
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        print(f"✅ Success! Parsed {len(feed.entity)} updates.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_realtime_with_headers()