import re
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from datetime import datetime

# Read the data from your text file
with open("travel_test2.txt", "r") as file:
    text = file.read()

# Create the GPX XML structure
gpx = Element("gpx", version="1.1", creator="Insta360 Studio", xmlns="http://www.topografix.com/GPX/1/1")

# Add metadata
metadata = SubElement(gpx, "metadata")

link = SubElement(metadata, "link", href="https://www.insta360.com")
link_text = SubElement(link, "text")
link_text.text = "Insta360 GPS Dashboard"

time = SubElement(metadata, "time")
time.text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

# Regular expressions to extract data in the specified format
datetime_pattern = re.compile(r"GPS Date/Time\s+:\s(.*?)Z")
coords_pattern = re.compile(r"GPS Latitude\s+:\s(.*?)\s([NS])\nGPS Longitude\s+:\s(.*?)\s([EW])")
speed_pattern = re.compile(r"GPS Speed\s+:\s(.*?)")
track_pattern = re.compile(r"GPS Track\s+:\s(.*?)")
altitude_pattern = re.compile(r"GPS Altitude\s+:\s(.*?) m")

# Create a list to track unique GPS points
gps_points = []

# Find and process GPS data
gps_data = re.finditer(
    r"GPS Date/Time\s+:\s(.*?)Z\nGPS Latitude\s+:\s(.*?)\s([NS])\nGPS Longitude\s+:\s(.*?)\s([EW])\nGPS Speed\s+:\s(.*?)\nGPS Track\s+:\s(.*?)\nGPS Altitude\s+:\s(.*?) m",
    text,
    re.DOTALL,
)

previous_time = None

for match in gps_data:
    date_time = match.group(1)
    latitude_str = match.group(2)
    latitude_dir = match.group(3)
    longitude_str = match.group(4)
    longitude_dir = match.group(5)
    speed = match.group(6)
    track = match.group(7)
    altitude = match.group(8)

    # Convert latitude and longitude from the specified format to decimal format
    lat_deg, lat_min, lat_sec = map(float, re.findall(r'(\d+\.\d+|\d+)', latitude_str))
    lon_deg, lon_min, lon_sec = map(float, re.findall(r'(\d+\.\d+|\d+)', longitude_str))

    latitude_decimal = lat_deg + lat_min / 60 + lat_sec / 3600
    if latitude_dir == 'S':
        latitude_decimal = -latitude_decimal

    longitude_decimal = lon_deg + lon_min / 60 + lon_sec / 3600
    if longitude_dir == 'W':
        longitude_decimal = -longitude_decimal

    # Check if the time is different by at least one second from the previous point
    if previous_time is None or (date_time != previous_time and (not gps_points or date_time != gps_points[-1][0])):
        gps_points.append((date_time, latitude_decimal, longitude_decimal, altitude, speed, track))
        previous_time = date_time

# Add unique GPS points to the GPX file
trk = SubElement(gpx, "trk")
name = SubElement(trk, "name")
name.text = "Insta360 GPS Data"
trkseg = SubElement(trk, "trkseg")

for point in gps_points:
    date_time, latitude_decimal, longitude_decimal, altitude, speed, track = point

    trkpt = SubElement(trkseg, "trkpt", lat=str(latitude_decimal), lon=str(longitude_decimal))
    ele = SubElement(trkpt, "ele")
    ele.text = altitude

    formatted_time = datetime.strptime(date_time, "%Y:%m:%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%SZ")
    time = SubElement(trkpt, "time")
    time.text = formatted_time

max_latitude = max(point[1] for point in gps_points)
min_latitude = min(point[1] for point in gps_points)
max_longitude = max(point[2] for point in gps_points)
min_longitude = min(point[2] for point in gps_points)

# Add the calculated bounding box to the GPX metadata
bounds = SubElement(metadata, "bounds", maxlat=str(max_latitude), minlat=str(min_latitude), maxlon=str(max_longitude), minlon=str(min_longitude))

# Convert the XML structure to a formatted string
gpx_str = parseString(tostring(gpx)).toprettyxml()
# gpx_str = re.sub(r'\<time\>(.*?)\<\/time\>', lambda match: f'<time>{match.group(1).replace("T", " ").replace("Z", "")}Z</time>', gpx_str)

# Save the GPX data to a file
with open("travel_test2.gpx", "w") as gpx_file:
    gpx_file.write(gpx_str)

print("GPX file created: output.gpx")