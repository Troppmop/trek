🚀 Getting Started
1. Prerequisites
Docker and Docker Compose installed.

GTFS Data: Ensure you have a stops.txt file located at scripts/data/stops.txt.

2. Clone and Environment Setup
Bash
git clone https://github.com/your-username/trek.git
cd trek
cp .env.example .env
Edit the .env file with your desired database credentials.

3. Spin Up Infrastructure
Build and start the FastAPI application and the PostGIS database:

Bash
docker compose up -d --build
4. Initialize Database & Import Data
We use a custom script to create the tables, enable spatial extensions, and bulk-load the GTFS stops. This process handles the coordinate conversion to geographic points automatically.

Run the import script inside the running container:

Bash
docker exec -it trek-api-1 bash -c "cd /app && PYTHONPATH=. python scripts/static.py"
Note: This script will process ~35,000 stops in chunks. You should see "Successfully loaded stations" upon completion.

5. Verify the Spatial Index
To ensure the PostGIS index is active for high-speed "Nearby" queries, you can run a quick check:

Bash
docker exec -it trek-db-1 psql -U [YOUR_USER] -d [YOUR_DB] -c "\d stations"
Verify that idx_stations_geom appears under the Indexes section.

6. Access the API
The API will be available at http://localhost:8000.

Swagger UI Docs: http://localhost:8000/docs

Test Nearby Endpoint:
GET /api/v1/stations/nearby?lat=32.091940&lon=34.825525&limit=10

🛠 Project Structure
/app/dal: Data Access Layer (Postgres/SQLAlchemy logic).

/app/routes: FastAPI endpoint definitions.

/scripts: Python scripts for data ingestion and static processing.

/scripts/data: Directory for GTFS source files.