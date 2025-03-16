from PyQt6.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QLabel, QWidget, QMainWindow
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtCore import Qt
from pathlib import Path
import webbrowser
import main
import sys

class MainWindow(QMainWindow): 
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ComicFLUX")
        
        self.create_menu_bar()

        # widget and layout
        mainwidget = QWidget(self)
        layout = QVBoxLayout()
        mainwidget.setLayout(layout)

        # image container
        self.image_container = QLabel(self)
        self.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter) 

        self.filename = None
        self.filename_path = None
        self.main_instance = None
        # Counter keeps track of index for paths list
        self.counter = 0
        # total image count
        self.image_count = 0

        layout.addWidget(self.image_container)

        self.setCentralWidget(mainwidget)

        self.showMaximized()

    # Binds left and right arrow keys to flip between images
    def keyPressEvent(self, event): 
        # left arrow key pressed, prevent out of bounds indexing. 
        if event.key() == Qt.Key.Key_Left and self.counter >= 1: 
            # print(self.counter)
            self.counter -= 1
            self.query_image()
        elif event.key() == Qt.Key.Key_Right and self.counter < self.image_count-1: 
            # print(self.counter)
            self.counter += 1
            self.query_image()
        else:
            super().keyPressEvent(event) # do whatever it did before (the default)

    # Creates menu bar and its buttons
    def create_menu_bar(self): 
        # File button
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        open_action = QAction("&Open", self)
        open_action.triggered.connect(self.locate_file)
        file_menu.addAction(open_action)
        # Help button
        help_menu = menubar.addMenu("&Help")
        help_action = QAction("&Docs", self)
        help_action.triggered.connect(self.open_docs)
        help_menu.addAction(help_action)

    # Allows user to choose file to open, loads first image
    def locate_file(self): 
        filename, ok = QFileDialog.getOpenFileName(
            self,
            "Select a File", 
            "C:", 
            "CBZ, RAR, and ZIP Files (*.cbz *.rar *.zip)"
        )
        if filename:
            filepath = Path(filename).resolve()
            self.filename_path = str(filepath)
            self.filename = filename

            self.main_instance = main.Main(self.filename, self.filename_path) # initialize Main
            self.image_count = len(self.main_instance.image_paths)
            # print(self.image_count)
            # load first image
            image = self.main_instance.return_image(self.counter) 

            # convert to pixmap. We use pixmap instead of ImageQt because it's better for rendering images in a GUI 
            pixmap = QPixmap.fromImage(image)
            # Scale the image to fit 
            pixmap = self.scale_image(pixmap)
            # print(pixmap.size())

             # Ensure label is resized and set 
            self.image_container.resize(pixmap.width(), pixmap.height()) 
            self.image_container.setPixmap(pixmap) 

    # Gets an image to display.
    def query_image(self): 
        # print(self.counter)
        image = self.main_instance.return_image(self.counter) 
        pixmap = QPixmap.fromImage(image)

        pixmap = self.scale_image(pixmap)
        self.image_container.resize(pixmap.width(), pixmap.height())
        self.image_container.setPixmap(pixmap)
        # print(f"size hint: {self.image_container.sizeHint()}") 
        # print(f"current size: {self.image_container.size()}")

    # Scales image to fit within the window.
    def scale_image(self, pixmap): 
        # print(f"pixmap dimensions {pixmap.size()}")
        # print(f"window dimensions {self.size()}")
        # print(f"max container size: {self.image_container.maximumSize()}")
        # print(f"recommended container size: {self.image_container.sizeHint()}")
        available_width = self.width() - 100
        available_height = self.height() - 100

        if pixmap.width() <= available_width and pixmap.height() <= available_height:
            return pixmap
        else:
            return pixmap.scaled(available_width, available_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # return pixmap.scaled(self.width()-100, self.height()-100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    
    # Open documentation for help
    def open_docs(self):
        webbrowser.open("https://github.com/lgtipton4/ComicFlux")

    # Delete extracted folder to save disk space
    def closeEvent(self, event):
        self.main_instance.cleanup()
        super().closeEvent(event)


def start():
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()

if __name__ == "__main__":
    start()