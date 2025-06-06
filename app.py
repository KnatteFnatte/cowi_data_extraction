import PyQt6
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit
import subprocess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("COWI ler Data Extraction")
        
        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.target_directory = None
        self.output_directory = None
        # Create a layout
        layout = QVBoxLayout()
        layout1 = QVBoxLayout()
        

        # Create a button
        button_input = QPushButton("Select Datafile Directory")
        button_input.clicked.connect(self.on_button_input_click)
        
        # Create blank field for output directory
        from PyQt6.QtWidgets import QLabel

        #save the labels in class for later use
        self.label_data = QLabel("Data Directory:")
        self.label_data.setStyleSheet("font-weight: bold;")
        self.label_data.frameRect = True

        self.label_output = QLabel("Output Directory:")
        self.label_output.setStyleSheet("font-weight: bold;")

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter your text here...")

        button_output = QPushButton("Select Output Directory")
        button_output.clicked.connect(self.on_button_output_click)

        button_run_program = QPushButton("Run Program")
        button_run_program.clicked.connect(self.on_button_run_program_click)

        # Add the button to the layout
        layout.addWidget(button_input)
        layout.addWidget(self.label_data)
        layout.addWidget(button_output)
        layout.addWidget(self.label_output)
        layout.addWidget(self.text_input)
        layout.addWidget(button_run_program)

        layout.addLayout(layout1)

        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-weight: bold;")

        # Set the layout on the central widget
        central_widget.setLayout(layout)

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
        if not self.target_directory or not self.output_directory:
            print("Please select both input and output directories.")
            return
        
        output_filename = self.text_input.text() or "output.csv"
        if not output_filename.endswith(".csv"):
            output_filename += ".csv"
        p = subprocess.Popen(["python", "DataExtraction.py","-td", self.target_directory,"-cwd", self.output_directory, "-out", output_filename],)
        
        
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
