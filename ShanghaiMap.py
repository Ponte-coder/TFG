import matplotlib.pyplot as plt
import pandas as pd
import os
import concurrent.futures

from BaseStation import BaseStation


class ShanghaiMap:
    def __init__(self):
        # Initialize a ShanghaiMap object with an empty dictionary to store base stations
        self.base_stations = {}

    def add_base_station(self, longitude, latitude):
        # Create a unique key for the base station using the longitude and latitude
        key = (longitude, latitude)
        # Check if the base station already exists in the dictionary
        if key not in self.base_stations:
            # Create a new BaseStation object and add it to the base_stations dictionary
            base_station = BaseStation(longitude, latitude)
            self.base_stations[key] = base_station
            print("key:", str(key))

    def process_file(self, file_path):
        # Read Excel file using pandas
        data = pd.read_excel(file_path)

        # Print the name of the file being processed
        file_name = os.path.basename(file_path)
        print("Processing file:", file_name)

        for _, row in data.iterrows():
            # Get longitude value from the row
            longitude_str = str(row['longitude']).replace(',', '.')
            latitude_str = str(row['latitude']).replace(',', '.')

            if longitude_str and latitude_str:  # Check if both longitude and latitude are non-empty
                try:
                    longitude = float(longitude_str)
                    latitude = float(latitude_str)

                    if not pd.isnull(longitude) and not pd.isnull(
                            latitude):  # Check if both longitude and latitude are valid numbers
                        self.add_base_station(longitude, latitude)
                except ValueError:
                    pass

    def load_data_from_excel(self, folder_path):
        # Get list of XLSX file names in the folder
        file_names = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []

            for file_name in file_names:
                file_path = os.path.join(folder_path, file_name)  # Get the full file path

                # Submit the file processing task
                future = executor.submit(self.process_file, file_path)
                futures.append(future)

            # Wait for all tasks to complete
            for future in concurrent.futures.as_completed(futures):
                pass

    def plot_base_stations(self):
        # Get the longitudes and latitudes of all base stations
        longitudes = [station.longitude for station in self.base_stations.values()]
        latitudes = [station.latitude for station in self.base_stations.values()]

        # Plot the base stations on a scatter plot with longitude as Y and latitude as X
        plt.scatter(latitudes, longitudes, s=20, marker='o', alpha=0.6)
        plt.xlabel('Latitude')
        plt.ylabel('Longitude')
        plt.title('Shanghai Base Stations')
        plt.show()
