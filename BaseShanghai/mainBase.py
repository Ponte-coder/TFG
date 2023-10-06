from ShanghaiMap import ShanghaiMap

if __name__ == "__main__":
    # Create an instance of ShanghaiMap
    shanghai_map = ShanghaiMap()

    # Folder path containing the XLSX files
    folder_path = "dataset"

    # Load data from the XLSX files using parallel processing
    shanghai_map.load_data_from_excel(folder_path)

    # Plot the base stations on a map
    shanghai_map.plot_base_stations()
