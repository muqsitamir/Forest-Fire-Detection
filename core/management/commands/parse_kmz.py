import geopandas as gpd
from shapely.geometry import Point, Polygon, shape
from django.core.management import BaseCommand
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from datetime import datetime
import os
from backend import settings
from core.models import Event
from core.models import Camera
import geopy.distance


class Command(BaseCommand):
    help = 'parse kmz'

    def handle(self, *args, **options):
        try:
            events = Event.objects.all()
            cameras = Camera.objects.all()
            current_date = datetime.now().strftime('%Y%m%d')

            output_filename = f'{current_date}.kmz'
            kmz_file_path = os.path.join(settings.MEDIA_ROOT, 'kmz')
            output_path = os.path.join(kmz_file_path, output_filename)

            points_within_radius = []
            with ZipFile(output_path, 'r') as zip_file:
                kml_file_name = [name for name in zip_file.namelist() if name.lower().endswith('.kml')][0]
                kml_data = zip_file.read(kml_file_name).decode('utf-8')

            root = ET.fromstring(kml_data)

            gdf = gpd.GeoDataFrame(columns=['geometry', 'properties'])

            ns = {"kml": "http://earth.google.com/kml/2.1"}

            for placemark in root.findall(".//kml:Placemark", namespaces=ns):
                polygon = placemark.find(".//kml:Polygon", namespaces=ns)
                point = placemark.find(".//kml:Point", namespaces=ns)

                description = placemark.find(".//kml:description", namespaces=ns)
                description_text = description.text.strip() if description is not None else ""

                properties = {'description': description_text}

                if polygon is not None:
                    coords_element = polygon.find(".//kml:coordinates", namespaces=ns)
                    if coords_element is not None:
                        coordinates = [tuple(map(float, coord.split(','))) for coord in
                                       coords_element.text.strip().split()]
                        if len(coordinates) >= 4:
                            coordinates.append(coordinates[0])

                            linear_ring = Polygon(coordinates)
                            for camera in cameras:
                                camera_latitude = camera.latitude
                                camera_longitude = camera.longitude

                                distance = geopy.distance.distance(
                                    (linear_ring.centroid.y, linear_ring.centroid.x),  # Latitude, Longitude
                                    (camera_latitude, camera_longitude)
                                ).km

                                if distance <= 10.0:
                                    points_within_radius.append(
                                        {'geometry': linear_ring, 'properties': properties, 'camera_id': camera.id})
                            gdf.loc[len(gdf)] = [linear_ring, properties]
                        else:
                            print("Error parsing KMZ: A LinearRing requires at least 4 coordinates.")

                elif point is not None:
                    coords_element = point.find(".//kml:coordinates", namespaces=ns)
                    if coords_element is not None:
                        coordinates = tuple(map(float, coords_element.text.strip().split(',')))

                        point_geom = Point(coordinates)
                        for camera in cameras:
                            camera_latitude = camera.latitude
                            camera_longitude = camera.longitude
                            # Calculate distance between point_geom and camera location
                            distance = geopy.distance.distance(
                                (point_geom.y, point_geom.x),  # Latitude, Longitude
                                (camera_latitude, camera_longitude)
                            ).km

                            if distance <= 10.0:
                                points_within_radius.append(
                                    {'geometry': point_geom, 'properties': properties, 'camera_id': camera.id})
                        gdf.loc[len(gdf)] = [point_geom, properties]

            geojson_data = gdf.to_json()
            print(points_within_radius)

            self.stdout.write(self.style.SUCCESS('KMZ file parsed successfully.'))
            for point_data in points_within_radius:
                filtered_events = [
                    event for event in events
                    if event.created_at.strftime('%Y%m%d') == current_date and event.camera.id == point_data['camera_id']
                ]

                for event in filtered_events:
                    event.nasa_tag = True
                    event.save()
            # print(filtered_events)
        except Exception as error:
            print('Error parsing KMZ:', error)
            self.stderr.write(self.style.ERROR('Error parsing KMZ: ' + str(error)))
