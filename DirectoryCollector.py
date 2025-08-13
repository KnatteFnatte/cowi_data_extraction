import PyQt6
from PyQt6 import QtCore
from DataExtraction import collect_csv
from PyQt6.QtWidgets import QLabel, QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QComboBox, QHBoxLayout, QCheckBox
import subprocess
import os
from time import sleep
from app import DirectoryBrowser



class MainWindow(QMainWindow):
    def __init__(self):
        self.running_process = False
        super().__init__()
        self.setWindowTitle("INSTRON Datafil samler")
        self.setGeometry(100, 100, 600, 400)  # Set window size and position
        
        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.target_directory = None
        self.output_directory = None
        # Create a layout which should contain two directory selectors, a button to run the program, and an error handler.
        layout_InputDirectoryHandler = QVBoxLayout()
        layout_OutputDirectoryHandler = QVBoxLayout()
        layout_RunProgramButton = QHBoxLayout()
        layout_ErrorHandler = QVBoxLayout()

        # Create a button which lets you select a target directory, and save it to self.target_directory for later use.
        button_output = QPushButton("Select Output Directory")
        button_output.setFixedHeight(30)
        button_output.setMaximumWidth(500)
        button_output.clicked.connect(self.on_button_output_click)
        self.label_output = QLabel("Output Directory:")
        self.label_output.setStyleSheet("font-weight: bold;")

        button_input = QPushButton("Select Input Directory")
        button_input.setFixedHeight(30)
        button_input.setMaximumWidth(500)
        button_input.clicked.connect(self.on_button_input_click)
        self.label_input = QLabel("Data Directory:")
        self.label_input.setStyleSheet("font-weight: bold;")

        # Create a button to run the program
        button_run_program = QPushButton("Run Program")
        button_run_program.setFixedHeight(30)
        button_run_program.setMaximumWidth(300)
        button_run_program.clicked.connect(self.on_button_run_program_click)

        # Create an error handler layout
        self.Errormessage = QLabel("")
        layout_ErrorHandler.addWidget(self.Errormessage)

        # Add widgets to the layouts
        layout_InputDirectoryHandler.addWidget(self.label_input)
        layout_InputDirectoryHandler.addWidget(button_input)
        layout_OutputDirectoryHandler.addWidget(self.label_output)
        layout_OutputDirectoryHandler.addWidget(button_output)
        layout_RunProgramButton.addWidget(button_run_program)
        layout_ErrorHandler.addWidget(self.Errormessage)
        # Add the layouts to the central widget
        main_layout = QVBoxLayout(central_widget)
        main_layout.addLayout(layout_InputDirectoryHandler)
        main_layout.addLayout(layout_OutputDirectoryHandler)
        main_layout.addStretch()  # Add stretch to push the button to the bottom
        main_layout.addLayout(layout_RunProgramButton)
        main_layout.addLayout(layout_ErrorHandler)

    def on_button_input_click(self):
        window1 = DirectoryBrowser(title="Select Datafile Directory")
        directory = window1.select_directory()
        print(f"Selected Datafile Directory: {directory}")
        self.label_input.setText(f"Data Directory: {directory}")
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
        
        if should_return:
            self.Errormessage.setText(errormessage)
            self.running_process = False
            return
        
        # Run the main function with the selected directories
        run(self.target_directory, self.output_directory)
        
        self.Errormessage.setText("Process completed successfully!")
        self.running_process = False

def run(data_directory, output_directory):
    #Nu vil vi gerne lave et forloop i data directory, som går ind i hver undermappe og laver en datafil for hver undermappe.
    os.chdir(data_directory)

    #Vi laver en liste over alle undermapperne i data directory.
    subdirectories = [d for d in os.listdir(data_directory) if os.path.isdir(os.path.join(data_directory, d))]

    #Vi går nu tilbage til output_directory så csv filerne placeres der.
    os.chdir(output_directory)

    #Nu laver vi et forloop der går ind i hver undermappe og laver en datafil for hver undermappe.
    for subdirectory in subdirectories:
        #Vi laver en sti til undermappen og går ind i den.
        subdirectory_path = os.path.join(data_directory, subdirectory)
        
        #Nu bruges collect_csv funktionen, bemærk at siden vi lige nu er i data_directory, så vil collect_csv funktionen tage alle csv-filerne i undermappen og samle dem i en datafil.
        collect_csv(subdirectory_path)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()