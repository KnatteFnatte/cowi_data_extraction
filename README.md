# cowi_data_extraction
Code for extracting relevant data from cowi clay experiments

The run.bat can be run on windows computers, which allows specification of target directory, output directory and filename.

if running through linux/mac use following commmand from terminal: 

        python DataExtraction.py -td [path to target directory - default current working directory] -cwd [place to put output file - default current working directory] -out [output file name - default "output.csv"]

All the files the data extraction runs on needs to be of the format

(Project name)\_(Sand content)\_(Water Content)\_(optional Lime)\_(Curing/Drying-temperature)\_(optional flags)

An example of this:

ERS_S15_W15.8_L5_Cu28-C23_Reco-W17.2

If you have data from the Instrom machine, you can run the collect_csv function from the notebook specifying the path to the folder with the output csv or txt files from the instrom machines. This will concatenate the csv laterally, which the dataextraction script is prepared to handle.

So for example for the ERS tests, we run the collect_csv function on the folder from each test. The output files are then collected in a single folder, which the dataextraction script is then run on. This gives a csv file which can then be further used with excel.
