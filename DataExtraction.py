import numpy as np
import pandas as pd
import argparse
import os
import csv
import shutil

class Datafile:
    def __init__(self, filename):
        """Henter parametre for testserien ud fra filnavnet.
        Filnavnet skal have formatet: lertype_sandindhold_vandindhold_evtlimeindhold_curing/drying-temperature[Co2]_[Reco-new_wc]"""
        self.filename = filename
        if "_" not in filename:
            raise ValueError("Filename must contain an underscore '_' to separate the name and the extension.")
        filename = filename[:-4]  # Remove the file extension
        name_parts = filename.split("_")
        self.clay_type = name_parts[0]
        self.sand_content = name_parts[1]
        self.water_content = name_parts[2]
        if "L" in name_parts[3]:
            self.lime_content = name_parts[3]
            del name_parts[3]
        if "Cu" in name_parts[3]:
            self.curing = True
        else:
            self.curing = False
        if "Dr" in name_parts[3]:
            self.drying = True
        else:
            self.drying = False
        self.temperature = name_parts[3][5:]
        if len(name_parts) > 4:
            if name_parts[4] == "Co2":
                self.Co2 = True
                del name_parts[4]
            else:
                self.Co2 = False
        if len(name_parts) > 4:
            if "Reco" in name_parts[4]:
                self.recompression = True
                self.new_wc = name_parts[4][6:]
        else:
            self.recompression = False
            self.new_wc = None
        return
    def __str__(self):
        """Return a string representation of the Datafile object. It is named __str__ so that if the class instance is printed, the relevant data will be supplied"""
        return f"Clay Type: {self.clay_type}, Sand Content: {self.sand_content}, Water Content: {self.water_content}, Lime Content: {self.lime_content}, Curing: {self.curing}, Drying: {self.drying}, Temperature: {self.temperature}, CO2: {self.Co2}, Recompression: {self.recompression}, New WC: {self.new_wc}"
    
    def extract_data(self):
        #pd.read_csv(self.filename, sep="\t", header=None, names=["Time", "Stress", "Strain", "Temperature"])
        output = str(f"{self.clay_type}, {self.sand_content}, {self.water_content}, {self.lime_content}, {self.curing}, {self.drying}, {self.temperature}, {self.Co2}, {self.recompression}, {self.new_wc}")
        return output.split(", ")


def get_filenames(directory):
    """Get all filenames in the specified directory."""
    if not os.path.isdir(directory):
        raise ValueError(f"The directory {directory} does not exist.")
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.csv')]

def main():
    """Test the Datafile class."""
    #Change cwd to the argument passed from the command line
    os.chdir(args.target_directory)
    
    # Get the if the target directory contains any csv files
    file_list = get_filenames(os.getcwd())
    csv_file = csv.writer(open("output.csv", "w", newline=""))
    csv_file.writerow("Clay type, Sand content, Water content, Lime content, Curing, Drying, Temperature, CO2, Recompression, New WC".split(", "))  


    ############# TEST ###############
    datafile = Datafile("ERS_S15_W15.8_L5_Cu28-C40_Co2.csv")
    #print(datafile)
    output = datafile.extract_data()
    csv_file.writerow(output)
    csv_file.writerow(output)  
    ############# END TEST ###############


    if file_list == []:
        print("No csv files found in the current working directory.")
        return
    #Extract the data from the files
    print(f"Found {len(file_list)} files in the target directory. Processing...")
    for file in file_list:
        if file == "output.csv":
            print("WARNING: output.csv is in the target directory. The file will be overwritten.")
            input("Press Enter to continue or Ctrl+C to exit.")
            continue
        try:
            datafile = Datafile(file)
            #print(datafile)
            output = file.extract_data()
            csv_file.writerow(output)
        except ValueError as e:
            print(f"Error processing file {file}: {e}")

    print("Data extraction complete. Output written to output.csv")
    return

if __name__ == "__main__":
    # Run the main function if this script is executed directly
    # This allows the script to be imported without executing main()
    # This is useful if we want to check specific files in a notebook or another script

    # Add argument flags from the command line to add the possibility of changing directory
    # This allows the user to specify the current working directory where the data files are located
    parser = argparse.ArgumentParser(description="Process some data files.")
    parser.add_argument("-cwd", "--current_working_directory", type=str, default=os.getcwd(),
                        help="The directory where the final output file should be placed.")
    parser.add_argument("-td", "--target_directory", type=str, default=os.getcwd(), help="The directory where the data files are located. If not specified, the current working directory will be used.")
    args = parser.parse_args()

    main()
    shutil.move("output.csv", args.current_working_directory + "/output.csv")
    
