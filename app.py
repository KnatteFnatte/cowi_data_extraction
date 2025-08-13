import PyQt6
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QComboBox, QHBoxLayout, QCheckBox
import subprocess
from time import sleep
class MainWindow(QMainWindow):
    def __init__(self):
        self.running_process = False
        super().__init__()
        self.setWindowTitle("COWI ler Data Extraction")
        self.setGeometry(100, 100, 600, 400)  # Set window size and position
        
        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.target_directory = None
        self.output_directory = None
        # Create a layout and sublayouts
        parentlayout = QVBoxLayout()
        RunDirectoryCollectorLayout = QHBoxLayout()
        DatafileDirectoryLayout = QVBoxLayout()
        OutputDirectoryLayout = QVBoxLayout()
        TestTypeLayout = QHBoxLayout()
        MainLayout = QHBoxLayout()
        PlotLayout = QHBoxLayout()
        OutputFilenameLayout = QVBoxLayout()
        ErrorHandler = QVBoxLayout()
        
        #Create a button which starts the directory collector program
        button_run_directory_collector = QPushButton("Run Directory Collector")
        button_run_directory_collector.setFixedHeight(30)
        button_run_directory_collector.setMaximumWidth(500)
        button_run_directory_collector.clicked.connect(self.on_button_run_directory_collector_click)

        #Deisgnate the sizes of the sublayouts
        DatafileDirectoryLayout.setContentsMargins(10, 10, 10, 10)
        DatafileDirectoryLayout.setSpacing(2)
        #DatafileDirectoryLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

        OutputDirectoryLayout.setContentsMargins(10, 10, 10, 10)
        OutputDirectoryLayout.setSpacing(2)
        #OutputDirectoryLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

        PlotLayout.setContentsMargins(10, 10, 10, 10)
        PlotLayout.setSpacing(2)

        TestTypeLayout.setContentsMargins(10, 10, 10, 10)
        TestTypeLayout.setSpacing(2)
        #TestTypeLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

        OutputFilenameLayout.setContentsMargins(10, 10, 10, 0)
        OutputFilenameLayout.setSpacing(2)
        #OutputFilenameLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

        ErrorHandler.setContentsMargins(10, 0, 10, 10)
        ErrorHandler.setSpacing(0)

        # Create a button
        button_input = QPushButton("Select Datafile Directory")
        button_input.setFixedHeight(30)
        button_input.setMaximumWidth(500)
        button_input.clicked.connect(self.on_button_input_click)
        
        # Create blank field for output directory
        from PyQt6.QtWidgets import QLabel

        #save the labels in class for later use
        self.label_data = QLabel("Selected Data Directory:")
        self.label_data.setStyleSheet("font-weight: bold;")
        self.label_data.frameRect = True

        # Create a button for output directory
        button_output = QPushButton("Select Output Directory")
        button_output.setFixedHeight(30)
        button_output.setMaximumWidth(500)
        button_output.clicked.connect(self.on_button_output_click)
        self.label_output = QLabel("Selected Output Directory:")
        self.label_output.setStyleSheet("font-weight: bold;")

        # Create a dropdown menu for test type
        self.TestTypeDropdownMenu = QComboBox()
        self.TestTypeDropdownMenu.setFixedHeight(30)
        self.TestTypeDropdownMenu.setMaximumWidth(200)
        self.TestTypeDropdownMenu.addItems(["None", "Compression", "Wet Compression", "Splitting", "Production"])

        #Create a tickbox for whether you wish to get pressure values
        self.pressure_checkbox = QCheckBox("Get Pressure Values")
        self.pressure_checkbox.setChecked(False)

        # Choose whether main should be run
        self.main_checkbox = QCheckBox("Run Main Function")

        #Create a tick box for whether you want plots and whether you want linear regression
        self.plot_checkbox = QCheckBox("Generate Plots")
        self.plot_checkbox.setChecked(False)
        self.linear_regression_checkbox = QCheckBox("Perform Linear Regression")
        self.linear_regression_checkbox.setChecked(False)


        # Create a text input field for output filename
        self.text_input = QLineEdit()
        self.text_input.setFixedHeight(30)
        self.text_input.setMaximumWidth(500)
        self.text_input.setPlaceholderText("Enter your text here...")

        # Create a button to run the program
        button_run_program = QPushButton("Run Program")
        button_run_program.setFixedHeight(30)
        button_run_program.setMaximumWidth(500)
        button_run_program.clicked.connect(self.on_button_run_program_click)

        # Create an error handler layout
        self.Errormessage = QLabel("")
        ErrorHandler.addWidget(self.Errormessage)

        # Add the button to the layout
        DatafileDirectoryLayout.addWidget(button_input)
        DatafileDirectoryLayout.addWidget(self.label_data)

        OutputDirectoryLayout.addWidget(button_output)
        OutputDirectoryLayout.addWidget(self.label_output)

        TestTypeLayout.addWidget(QLabel("Select Test Type:"))
        TestTypeLayout.addWidget(self.TestTypeDropdownMenu)
        TestTypeLayout.addStretch()  # This creates a bit of space
        TestTypeLayout.addWidget(self.pressure_checkbox)
        TestTypeLayout.addStretch()  # This pushes everything to the left

        PlotLayout.addWidget(self.main_checkbox)
        PlotLayout.addStretch()  # This creates a bit of space

        PlotLayout.addWidget(self.plot_checkbox)
        PlotLayout.addStretch()  # This pushes everything to the left
        PlotLayout.addWidget(self.linear_regression_checkbox)
        PlotLayout.addStretch()  # This pushes everything to the left

        OutputFilenameLayout.addWidget(QLabel("Output Filename:"))
        OutputFilenameLayout.addWidget(self.text_input)
        OutputFilenameLayout.addWidget(button_run_program)

        parentlayout.addWidget(button_run_directory_collector)
        parentlayout.addStretch()
        parentlayout.addLayout(DatafileDirectoryLayout)
        parentlayout.addStretch()
        parentlayout.addLayout(OutputDirectoryLayout)
        parentlayout.addStretch()
        parentlayout.addLayout(TestTypeLayout)
        parentlayout.addStretch()
        parentlayout.addLayout(PlotLayout)
        parentlayout.addStretch()
        parentlayout.addLayout(OutputFilenameLayout)
        parentlayout.addLayout(ErrorHandler)
        parentlayout.addStretch()
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-weight: bold;")

        # Set the layout on the central widget
        central_widget.setLayout(parentlayout)

    def check_process(self):
        if self.process.poll() is not None:
            self.Errormessage.setText("Process completed successfully!")
            self.timer.stop()
            self.running_process = False
            # Optionally, you can update the UI or perform other actions here

    def get_test_type(self):
        self.testtypeDictionary = {
            "None": -1,
            "Compression": "compression",
            "Wet Compression": "wet_compression",
            "Splitting": "splitting",
            "Production": "production"
        }
        if self.TestTypeDropdownMenu.currentText() == "None":
            return -1
        return self.TestTypeDropdownMenu.currentText()
    
    def on_button_run_directory_collector_click(self):
        if self.running_process:
            return
        self.running_process = True
        
        errormessage = "Running Directory Collector..."

        self.Errormessage.setText(errormessage)
        p = subprocess.Popen(["python", "DirectoryCollector.py"])
        self.process = p
        # Run the main function with the selected directories
        self.timer = QtCore.QTimer()

        self.timer.timeout.connect(self.check_process)
        self.timer.start(500)


    def on_button_input_click(self):
        window1 = DirectoryBrowser(title="Select Datafile Directory")
        directory = window1.select_directory()
        print(f"Selected Datafile Directory: {directory}")
        self.label_data.setText(f"Data Directory: {directory}")
        self.target_directory = directory
        return 

    def on_button_output_click(self):
        window1 = DirectoryBrowser(title="Select Output Directory")
        directory = window1.select_directory()
        print(f"Selected Output Directory: {directory}")
        self.label_output.setText(f"Output Directory: {directory}")
        self.output_directory = directory
        return
    
    def on_button_run_program_click(self):
        if self.running_process:
            return
        self.running_process = True
        errormessage = None
        should_return = False
        if not self.target_directory or not self.output_directory:
            errormessage = "Please select both input and output directories."
            should_return = True
        
        if not self.main_checkbox.isChecked() and not self.plot_checkbox.isChecked():
            if errormessage == None:
                errormessage = "Please select either 'Run Main Function' or 'Generate Plots'."
            else:
                errormessage += "\nPlease select either 'Run Main Function' or 'Generate Plots'."
            should_return = True

        testtype = self.get_test_type()
        if testtype == -1:
            if errormessage == None:
                errormessage = "Please select a test type."
            else:
                errormessage += "\nPlease select a test type."
            should_return = True
        
        if not self.plot_checkbox.isChecked() and self.linear_regression_checkbox.isChecked():
            if errormessage == None:
                errormessage = "Please select 'Generate Plots' to perform linear regression."
            else:
                errormessage += "\nPlease select 'Generate Plots' to perform linear regression."
            should_return = True

        self.Errormessage.setText(errormessage)
        if should_return:
            
            return
        else:
            self.Errormessage.setText("Running program...")

        if self.pressure_checkbox.isChecked():
            pressure = "-p"
        else:
            pressure = ""
        
        output_filename = self.text_input.text() or "output.csv"
        if not output_filename.endswith(".csv"):
            output_filename += ".csv"
        argarray = ["python", "DataExtraction.py","-td", self.target_directory,"-cwd", self.output_directory, "-out", output_filename]
        if self.pressure_checkbox.isChecked():
            argarray.append(pressure)
        argarray.append("-tt")
        argarray.append(self.testtypeDictionary[testtype])
        if self.main_checkbox.isChecked():
            argarray.append("-m")
        if self.plot_checkbox.isChecked():
            argarray.append("-sp")
            if self.linear_regression_checkbox.isChecked():
                argarray.append("-lr")
        p = subprocess.Popen(argarray,)
        self.process = p
        self.timer = QtCore.QTimer()

        self.timer.timeout.connect(self.check_process)
        self.timer.start(500)

        


        
        # Here you would call the main function from DataExtraction.py
        # For example:
        # main(self.target_directory, self.output_directory)
        print(f"Running program with input directory: {self.target_directory} and output directory: {self.output_directory}")
        # Add your data extraction logic here

class DirectoryBrowser:
    def __init__(self, title="Select Directory"):
        self.title = title

    def select_directory(self):
        from PyQt6.QtWidgets import QFileDialog
        options = QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        directory = QFileDialog.getExistingDirectory(None, self.title, options=options)
        return directory if directory else None

def __main__():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    __main__()
