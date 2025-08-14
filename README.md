# cowi_data_extraction

###### Important ######
Follow the installation guide.pdf for instructions on how to run the program.

The run.bat can be run on windows computers, which allows specification of target directory, output directory and filename.

if running through linux/mac use following commmand from terminal: 

        python app.py

All the files the data extraction runs on needs to be of the format

(Project name)\_(Sand content)\_(Water Content)\_(optional Lime)\_(Curing/Drying-temperature)\_(optional flags)

An example of this:

ERS_S15_W15.8_L5_Cu28-C23_Reco-W17.2

in Datafile.__init__() new flags can be added if there is add more naming convention for example if we wish to add algae with the naming convention "Al%" to the mix the lines of code should be added in the if statement on line 59:
if "Al".lower() in i.lower():
        self.algae = True
        self.alcontent = i[2:]

And perhaps intiate self.algae earlier as self.algae = False

When naming conventions change, the dictionary of main2() should be changed, since it is used for indexing and namechecking when plotting data.

The sizes of the tests are assumed to all be 60 mm diameter and 60 mm height since it was not easily extractable from the instron data, and the name checking with a different excel document would have caused more value than its worth. Just be aware that if the sizes change the code should be modified or the pressure values will be incorrect.
