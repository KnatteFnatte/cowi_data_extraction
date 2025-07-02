import numpy as np
import pandas as pd
import argparse
import os
import csv
import shutil
import matplotlib.pyplot as plt
from io import StringIO





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
        self.Co2 = False
        self.recompression = False
        self.new_wc = None
        self.avg_max_displacement = None
        self.avg_max_force = None
        self.lime_content = None
        self.diameter = 0.06 #meter

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

        #Add here any optional flags in naming convention (landerslev for example has Calcium which Egernsund does not)
        if len(name_parts) > 4:
            for i in name_parts[4:]:
                if i == "Co2":
                    self.Co2 = True

                if "Reco" in i:
                    self.recompression = True
                    self.new_wc = i[6:]

                if "Wet" in i:
                    self.testtype = "WetCompression"

            

        

        return
    def __str__(self):
        """Return a string representation of the Datafile object. It is named __str__ so that if the class instance is printed, the relevant data will be supplied"""
        return f"Clay Type: {self.clay_type}, Sand Content: {self.sand_content}, Water Content: {self.water_content}, Lime Content: {self.lime_content}, Curing: {self.curing}, Drying: {self.drying}, Temperature: {self.temperature}, CO2: {self.Co2}, Recompression: {self.recompression}, New WC: {self.new_wc}. avg_max_force: {self.avg_max_force}, avg_max_displacement: {self.avg_max_displacement}, Pressure: {self.mean_pressure}, Pressure Std: {self.pressure_std}, Force Std: {self.force_std}"
    
    def extract_data(self):
        """Extract the max force value and corresponding displacements from the CSV file. each file will have columnnumbers/3 values, as they should be concatenated laterally from the Instrom machine."""
        if not os.path.isfile(self.filename):
            raise ValueError(f"The file {self.filename} does not exist.")
        # Read the CSV file using pandas
        # We assume the CSV file has a header row, so we skip the first row
        df = pd.read_csv(self.filename, sep=",", header=1)
        
        # Create a list to hold the extracted data
        extracted_data = []
        for columns in df:
            # Extract the relevant columns for this set of data

            StringData = StringIO(df[columns].to_string(index = False, header = False))
            # Read the CSV data from the string
            new_df = pd.read_csv(StringData, header = 1, sep=";")
            # Rename the columns for clarity
            if len(new_df.columns) == 4:
                new_df.columns = ["Time (s)", "Displacement (mm)", "Force (kN)", "Unused"]
            elif len(new_df.columns) == 3:
                new_df.columns = ["Time (s)","Displacement (mm)", "Force (kN)"]
            # Get the maximum force value and its corresponding displacement
            max_force = new_df["Force (kN)"].max()
            max_displacement = new_df.loc[new_df["Force (kN)"] == max_force, "Displacement (mm)"].values[0]
            # Append the extracted data to the list
            extracted_data.append((max_force, max_displacement))

        # If we have multiple sets of data, we can average the max forces and displacements
        self.max_forces = [data[0] for data in extracted_data]
        self.max_displacements = [data[1] for data in extracted_data]
        self.avg_max_force = np.mean(self.max_forces)
        self.avg_max_displacement = np.mean(self.max_displacements)
        nparray_max_forces = np.array(self.max_forces)
        #Calculate the pressure on the sample
        self.pressure = nparray_max_forces / (np.pi * (self.diameter/2)**2)/10**3  # Pressure in kN/m^2 which is equivalent to kPa
        self.mean_pressure = np.mean(self.pressure)
        self.pressure_std = np.std(self.pressure)
        
        self.force_std = np.std(self.max_forces)
        # Return the values of the class as a string
        output = str(f"{self.clay_type}, {self.sand_content}, {self.water_content}, {self.lime_content}, {self.curing}, {self.drying}, {self.temperature}, {self.Co2}, {self.recompression}, {self.new_wc}, {self.avg_max_force}, {self.force_std}, {self.mean_pressure}, {self.pressure_std}")
        return output.split(", ")
    
    def plot_data(self):
        """Plot the data from the CSV file."""
        # Read the CSV file using pandas
        df = pd.read_csv(self.filename, sep=",", header=1)
        dfarray = []
        # Create a list to hold the extracted data
        for columns in df:
            # Extract the relevant columns for this set of data
            StringData = StringIO(df[columns].to_string(index = False, header = False))
            # Read the CSV data from the string
            new_df = pd.read_csv(StringData, header = 1, sep=";")
            # Rename the columns for clarity
            if len(new_df.columns) == 4:
                new_df.columns = ["Time (s)", "Displacement (mm)", "Force (kN)", "Unused"]
                
            elif len(new_df.columns) == 3:
                new_df.columns = ["Time (s)","Displacement (mm)", "Force (kN)"]
            dfarray.append(new_df)
            # Plot the data
        return dfarray

def get_filenames(directory):
    """Get all filenames in the specified directory."""
    if not os.path.isdir(directory):
        raise ValueError(f"The directory {directory} does not exist.")
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and (f.endswith('.csv') or f.endswith('.txt'))]

def get_directories(directory):
    """Get all directories in the specified directory. Use only in directory with data directories."""
    if not os.path.isdir(directory):
        raise ValueError(f"The directory {directory} does not exist.")
    return [directory+"/"+d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

#Function for collecting data outputs from single test (Instrom creates multiple CSV files - we only want one)

def collect_csv(directory):
    """Take a folder of csv files and concatenate them laterally (designed for csv files with 3 columns)"""
    olddir = os.getcwd()
    os.chdir(directory)
    #First access all the filenames
    if not os.path.isdir(directory):
        raise ValueError(f"The directory {directory} does not exist.")
    filearr = [f for f in os.listdir(directory) if (os.path.isfile(os.path.join(directory, f)) and f.endswith('.csv') or os.path.isfile(os.path.join(directory, f)) and f.endswith('.txt'))]
    #Remove file extension and give name to output file
    final_filename = filearr[0][:-4].split("_")
    print(final_filename)
    final_filename = [i for i in final_filename if not i.isdigit()]
    final_filename = "_".join(final_filename)
    final_filename = final_filename + ".csv"
    #We want to concatenate all the data laterally, which is lengthy without pandas.
    print(final_filename)
    masterdf = pd.read_csv(filearr[0], delimiter=",")
    for i in filearr[1:]:
        tempdf = pd.read_csv(i, delimiter=",")
        masterdf = pd.concat([masterdf, tempdf], axis=1)
    
    os.chdir(olddir)
    print(os.getcwd())
    masterdf.to_csv(final_filename, index=False, sep=",", header=True)
    print(os.getcwd())



def merge_output_files(output_file, input_files):
    """Merge multiple output files into a single output file."""
    dataframes = []
    for file in input_files:
        df = pd.read_csv(file, sep=",", header=0, names=["Clay type", "Sand content", "Water content", "Lime content", "Curing", "Drying", "Temperature", "CO2", "Recompression", "New WC"])
        dataframes.append(df)
    merged_df = pd.concat(dataframes, ignore_index=True)
    merged_df.to_csv(output_file, index=False, sep=",", header=True)
    return merged_df

def main2(directory,subplotsax1, subplotsax2):
    """This function is run manually through jupyter notebook to generate plots"""
    os.chdir(directory)
    cwd = directory
    
    # Get the if the target directory contains any csv files
    file_list = get_filenames(cwd)

    if file_list == []:
        print("No csv files found in the current working directory.")
        return
    #Extract the data from the files
    print(f"Found {len(file_list)} files in the target directory. Processing...")

    fig, ax = plt.subplots(subplotsax1,subplotsax2, figsize=(20, 20))
    ax = ax.flatten()
    index = 0
    for file in file_list:
        if file == "output.csv":
            print("WARNING: output.csv is in the target directory. The file will be overwritten.")
            input("Press Enter to continue or Ctrl+C to exit.")
            continue
        try:
            datafile = Datafile(file)
            #print(datafile)
            df = datafile.plot_data()
            for i in df:
                 ax[index].plot(i["Displacement (mm)"], i["Force (kN)"])
            ax[index].set_xlabel("Displacement (mm)")
            ax[index].set_ylabel("Force (kN)")

        except ValueError as e:
            print(f"Error processing file {file}: {e}")
        index += 1

    fig.tight_layout()
    plt.show()
    




def main():
    """Test the Datafile class."""
    #Change cwd to the argument passed from the command line
    os.chdir(args.target_directory)
    
    # Get the if the target directory contains any csv files
    file_list = get_filenames(os.getcwd())
    csv_file = csv.writer(open(args.output_file, "w", newline=""))
    csv_file2 = csv.writer(open("max_forces"+args.output_file, "w", newline=""))
    csv_file.writerow("Clay type, Sand content, Water content, Lime content, Curing, Drying, Temperature, CO2, Recompression, New WC, Mean_Max_Force [kN], Std force [kN], Pressure [MPa], Std Pressure [MPa]".split(", "))  


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
            output = datafile.extract_data()
            csv_file.writerow(output)
            csvfile2output = [datafile.filename]
            for i in datafile.max_forces:
                csvfile2output.append(i)
            if pressure:
                csvfile2output.append("Pressure")
                for i in datafile.pressure:
                    csvfile2output.append(i)
            csv_file2.writerow(csvfile2output)
        except ValueError as e:
            print(f"Error processing file {file}: {e}")
        print(f"Processed file: {file} with avg max force: {datafile.avg_max_force:.3f} kN and avg max displacement: {datafile.avg_max_displacement:.3f} mm")

    print("Data extraction complete. Output written to" + args.output_file + " and max_forces_" + args.output_file)
    return

if __name__ == "__main__":
    # Run the main function if this script is executed directly
    # This allows the script to be imported without executing main()
    # This is useful if we want to check specific files in a notebook or another script
    pressure = False   #Set to true if you want the calculated pressures in max_forces_output.csv

    # Add argument flags from the command line to add the possibility of changing directory
    # This allows the user to specify the current working directory where the data files are located
    parser = argparse.ArgumentParser(description="Process some data files.")
    parser.add_argument("-cwd", "--current_working_directory", type=str, default=os.getcwd(),
                        help="The directory where the final output file should be placed.")
    parser.add_argument("-td", "--target_directory", type=str, default=os.getcwd(), help="The directory where the data files are located. If not specified, the current working directory will be used.")
    parser.add_argument("-out", "--output_file", type=str, default="output.csv", help="The name of the output file. Default is 'output.csv'.")
    args = parser.parse_args()
    if args.output_file.endswith(".csv") is False:
        args.output_file = args.output_file + ".csv"


    main()

    shutil.move(args.target_directory+"/"+args.output_file, args.current_working_directory + "/" + args.output_file)
    print("Succesfully moved "+args.output_file+" to "+ args.current_working_directory)
    shutil.move( args.target_directory+"/"+"max_forces" +args.output_file, args.current_working_directory + "/max_forces_" + args.output_file)
    print("Succesfully moved max_forces_" + args.output_file + " to " + args.current_working_directory)
    input("Program successfully completed. Press Enter to exit.")
    
    
