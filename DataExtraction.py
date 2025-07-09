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
        """Tager navnet på en fil og genererer et objekt der indeholder informationen om serien ud fra navnet.\n
        Filnavnet skal have formatet: lertype_sandindhold_vandindhold_evtlimeindhold_curing/drying-temperature[Co2]_[Reco-new_wc]\n
        Eksempel: ERS_S15_W15.8_L5_Cu28-C23_Reco-17.4\n
        Filnavnet skal have et '_' i sig, som adskiller navnet og filendelsen. Filendelsen skal være .csv eller .txt.\n
        Classen har 2 hovedfunktioner: extract_data() og plot_data().\n
        extract_data() udtrækker de relevante data såsom max_force fra filen og gemmer dem i classens attributter.\n
        plot_data() tager rådataet fra de dataframes der kan dannes fra csv'en og returnerer det i et array så det kan plottes.\n
        """
        self.filename = filename
        if "_" not in filename:
            raise ValueError("Filename must contain an underscore '_' to separate the name and the extension.")
        filename = filename[:-4]  # Remove the file extension
        name_parts = filename.split("_")

        #Gem karakteristika for testen i attributter for classen
        self.clay_type = name_parts[0]
        self.sand_content = name_parts[1]
        self.water_content = name_parts[2]
        self.Co2 = False
        self.recompression = False
        self.new_wc = None
        self.avg_max_displacement = None
        self.avg_max_force = None
        self.lime_content = None
        self.diameter = 0.06 #meter - DETTE BETYDER AT LIGE NU BENYTTES MÅLINGEN PÅ DIAMETER IKKE

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

        #Add here any optional flags in naming convention (landerslev for example has Calcium which Egernsund does not, this if statement could be added easily, and so this is where we should add stuff like that)
        if len(name_parts) > 4:
            for i in name_parts[4:]:
                if i == "Co2":
                    self.Co2 = True

                if "Reco" in i:
                    self.recompression = True
                    self.new_wc = i[6:]

                if "Wet" in i:
                    self.testtype = "WetCompression"
        
        #Nameing convention benyttes lige nu ikke da værdierne var gemt som booleans og ikke som strenge i classen, men jeg lader den være her hvis det skal bruges på et tidspunkt.
        naming_convention = {'Cu':'S', 'Dr':'D', 'L5':'L5', 'Co2':'C1', 'Reco':'Reco', 'Wet':'W'}

        # gem navnet på serien i classen, så det kan bruges senere til at plotte og sætte rækkefølgen af dataet.
        if self.curing:
            self.name = 'S'
        else:
            self.name = 'D'
        
        self.name += str(self.temperature[1:])

        if self.lime_content == None:
            pass
        else:
            self.name += self.lime_content
        
        if self.Co2:
            self.name += "C1"

        if self.recompression:
            self.name += "_Reco"

        #Returner intet, da classen er bygget til at blive brugt som et objekt der indeholder data om en serie, og ikke som en funktion der returnerer noget.
        return
    
    def __str__(self):
        """Return a string representation of the Datafile object. It is named __str__ so that if the class instance is printed, the relevant data will be supplied"""
        return f"Clay Type: {self.clay_type}, Sand Content: {self.sand_content}, Water Content: {self.water_content}, Lime Content: {self.lime_content}, Curing: {self.curing}, Drying: {self.drying}, Temperature: {self.temperature}, CO2: {self.Co2}, Recompression: {self.recompression}, New WC: {self.new_wc}. avg_max_force: {self.avg_max_force}, avg_max_displacement: {self.avg_max_displacement}, Pressure: {self.mean_pressure}, Pressure Std: {self.pressure_std}, Force Std: {self.force_std}"
    
    def extract_data(self):
        """Trækker maxværdierne for datasættene ud. Funktionen er bygget med antagelsen om at csv-filen består af datasæt af 3-4 kolonner, hvor hver kolonne er adskilt af ; og hvert datasæt er adskilt af komma. \n
        eksempelvis 0;0;0;0, 1;1;1;1, 2;2;2;2 \n
        Returnerer alt værdien fra Classen i en liste, og max forces, displacements, gennemsnittet af max forces og standardafvigelsen gemmes i classens attributter.\n
        Også trykket bliver gemt, det er antaget at alle prøver har en diameter på 60 mm. \n
        !!!\n
        Der mangler at implementere for splitting at vi i stedet skal bruge længdetrykket i stedet for arealttrykket på toppen.\n
        !!!"""
        # Check if the file exists
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

        # If we have multiple sets of data, we can average the max forces and displacements - det virker stadig selv hvis der kun er et datasæt, så er gennemsnittet bare trivielt. standardafvigelsen er dog ikke veldefineret i det tilfælde.
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
        """Trækker dataet ud af CSV filen men returnerer en liste af de adskilte dataframes.\n
        Altså gør den det samme som starten af extract_data() men laver intet behandling på dataet.\n
        Dataet plottes uden for funktionens scope, så det kan bruges til at plotte dataet i et subplot.\n"""
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
            
            # Make sure displacement starts at 0
            new_df["Displacement (mm)"] = new_df["Displacement (mm)"] - new_df["Displacement (mm)"].iloc[0]
            dfarray.append(new_df)

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
    """Take a folder of csv files and concatenate them laterally (designed for csv files that are semicolon separated, as they will be concatenated laterally with comma seperation)\n
    The outputfile is saved in the argument directory, and it is assumed all the files have the same name but then _1, _2, etc. appended to the end of the filename.\n
    The output file is named after the first file in the directory, with the file extension .csv\n
    Output file is saved in the current working directory, so make sure to change the directory before calling this function.\n"""
    olddir = os.getcwd()
    os.chdir(directory)
    #First access all the filenames
    if not os.path.isdir(directory):
        raise ValueError(f"The directory {directory} does not exist.")
    filearr = [f for f in os.listdir(directory) if (os.path.isfile(os.path.join(directory, f)) and f.endswith('.csv') or os.path.isfile(os.path.join(directory, f)) and f.endswith('.txt'))]
    #Remove file extension and give name to output file
    final_filename = filearr[0][:-4].split("_")
    
    #The instron machine appends _1, _2, etc. to the end of the filename, so we need to remove those. As there is no entries that are purely numbers in the naming convention, we can remove all entries that are purely a number
    final_filename = [i for i in final_filename if not i.isdigit()]
    final_filename = "_".join(final_filename)
    final_filename = final_filename + ".csv"

    #We want to concatenate all the data laterally.
    print(final_filename)
    masterdf = pd.read_csv(filearr[0], delimiter=",")
    for i in filearr[1:]:
        tempdf = pd.read_csv(i, delimiter=",")
        masterdf = pd.concat([masterdf, tempdf], axis=1)
    
    os.chdir(olddir)
    masterdf.to_csv(final_filename, index=False, sep=",", header=True)




def merge_output_files(output_file, input_files):
    """Merge multiple output files into a single output file.\n
    Jeg er lidt usikker på om den her funktion nogensinde bruges? Det kan være den bruges i notebook uden jeg lige kan huske hvordan."""
    dataframes = []
    for file in input_files:
        df = pd.read_csv(file, sep=",", header=0, names=["Clay type", "Sand content", "Water content", "Lime content", "Curing", "Drying", "Temperature", "CO2", "Recompression", "New WC"])
        dataframes.append(df)
    merged_df = pd.concat(dataframes, ignore_index=True)
    merged_df.to_csv(output_file, index=False, sep=",", header=True)
    return merged_df

def main2(directory,subplotsaxes=(9,2), figsize=(20,20), stress_strain=False, savefig=False, figname="COWI Test Plots", naming_convention=1, show_plot=True):
    """This function is run manually through jupyter notebook to generate plots.\n
    It takes a directory as an argument, with the collected csv files in it. It can only plot the data if the csv files are in the correct format, either being raw data or being the concatenated data from the collect_csv function.\n
    The function will plot the data in subplots, with the subplot axes specified by the subplotsaxes argument. The default is set to (9,2) as we have 18 series in Egernsund, so all the series can be plotted in a 2x9 grid.\n
    The function takes arguments: figsize [tuple/default=(20,20)], subplotsaxes [tuple/default=(9,2)], stress_strain [bool/default=False], savefig [bool/default=False], figname [str/default=COWI Test Plots], naming_convention [int/default=1].\n
    figsize is the size of the figure, subplotsaxes is the number of subplots in the x and y direction, stress_strain is a boolean that determines if the data should be plotted as stress-strain or force-displacement, savefig is a boolean that determines if the figure should be saved as a png file, and figname is the name of the figure.
    Naming convention should be either 0 or 1, where 0 will make the names as S1L5C1 and 1 will make the names as S23L5C1.\n
    """
    
    # Change the current working directory to the specified directory
    os.chdir(directory)
    #This line is technically redundant as the argument could be passed directly to the function, but it is kept for clarity.
    cwd = directory
    
    # Get the if the target directory contains any csv files
    file_list = get_filenames(cwd)

    if file_list == []:
        print("No csv files found in the current working directory.")
        return
    
    #Extract the data from the files
    print(f"Found {len(file_list)} files in the target directory. Processing...")

    # Create dictionary for subplot orientation. The naming convention is the one used for Egernsund, the sseries names are doubled because 
    subplot_index = {
        "S1": 0,
        "S23": 0,
        "S2": 1,
        "S40": 1,
        "D1": 2,
        "D23": 2,
        "S1L5": 3,
        "S23L5": 3,
        "S2L5": 4,
        "S40L5": 4,
        "D1L5": 5,
        "D23L5": 5,
        "S1L5C1": 6,
        "S23L5C1": 6,
        "S2L5C1": 7,
        "S40L5C1": 7,
        "D1L5C1": 8,
        "D23L5C1": 8,
        "S1_Reco": 9,
        "S23_Reco": 9,
        "S2_Reco": 10,
        "S40_Reco": 10,
        "D1_Reco": 11,
        "D23_Reco": 11,
        "S1L5_Reco": 12,
        "S23L5_Reco": 12,
        "S2L5_Reco": 13,
        "S40L5_Reco": 13,
        "D1L5_Reco": 14,
        "D23L5_Reco": 14,
        "S1L5C1_Reco": 15,
        "S23L5C1_Reco": 15,
        "S2L5C1_Reco": 16,
        "S40L5C1_Reco": 16,
        "D1L5C1_Reco": 17,
        "D23L5C1_Reco": 17,
    }

    fig, ax = plt.subplots(subplotsaxes[0],subplotsaxes[1], figsize=figsize)
    ax = ax.flatten()
    max_force_val = 0
    for file in file_list:
        if file == "output.csv":
            print("WARNING: output.csv is in the target directory. The file will be overwritten.")
            input("Press Enter to continue or Ctrl+C to exit.")
            continue
        try:
            datafile = Datafile(file)
            #print(datafile)
            df = datafile.plot_data()

            # Determine the subplot index based on the naming convention
            if datafile.name in subplot_index:
                index = subplot_index[datafile.name]
            else:
                print(f"Warning: No subplot index found for {datafile.name}. Skipping this file.")
                continue

            for j,i in enumerate(df):
                if max(i["Force (kN)"]) > max_force_val:
                    max_force_val = max(i["Force (kN)"])
                if stress_strain:
                    column_height = 60 #mm
                    column_diameter = 60 #mm
                    surface_area = np.pi * (column_diameter/2*10**(-3))**2
                    stress = i["Force (kN)"] / surface_area*10**(-3)  # Convert to MPa
                    strain = i["Displacement (mm)"] / (column_height)*100  # Convert to strain in %
                    ax[index].plot(strain, stress, label = j)
                    ax[index].set_xlabel("Strain [%]")
                    ax[index].set_ylabel("Stress [MPa]")

                    if index%2 != 0:
                        ax[index].yaxis.tick_right()
                        ax[index].yaxis.set_label_position("right")
                    
                else:
                    ax[index].plot(i["Displacement (mm)"], i["Force (kN)"])
                    ax[index].set_xlabel("Displacement (mm)")
                    ax[index].set_ylabel("Force (kN)")
                    
                    if index%2 != 0:
                        ax[index].yaxis.tick_right()
                        ax[index].yaxis.set_label_position("right")
        except ValueError as e:
            print(f"Error processing file {file}: {e}")

    if stress_strain:
        max_force_val = max_force_val / surface_area*10**(-3)  # Convert to MPa
    keylist = [key for key in subplot_index]
    for j,i in enumerate(ax):
        if naming_convention == 0:
            i.set_title(keylist[j*2], fontsize=10)
        elif naming_convention == 1:
            i.set_title(keylist[j*2+1], fontsize=10)
        else:
            print("Invalid naming convention. Please use 0 or 1.")
        i.legend(loc='upper right', fontsize='small')
        i.grid(True)
        if max_force_val > 0:
            i.set_ylim(0, max_force_val*1.1)

        

    
    fig.suptitle(figname, fontsize=16, y=1.0)
    fig.tight_layout()
    if savefig:
        fig.savefig(figname, dpi='figure', bbox_inches='tight')
        print("Saved figure as compression_test_plots.png")
    if show_plot:
        plt.show()
    




def main():
    """The function that is run from the run.bat script.\n
    It takes the current working directory and the target directory as arguments, and then processes all the csv files in the target directory.\n
    The output is written to a csv file in the current working directory, with the name specified by the user. If no name is specified, the default is output.csv.\n
    The output file contains the following columns: Clay type, Sand content, Water content, Lime content, Curing, Drying, Temperature, CO2, Recompression, New WC, Mean_Max_Force [kN], Std force [kN], Pressure [MPa], Std Pressure [MPa].\n
    The function also creates a second csv file with the max forces for each test, with the name max_forces_output.csv.\n
    The second csv file only has full name of the test (maybe this should be changed to the naming convention?) and then the max forces for each test, and if pressure is set to True, it will also include the pressure values for each test.\n"""
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
    
    
