from PyQt6.QtWidgets import QApplication, QFileDialog, QLabel, QMainWindow, QScrollArea
from PyQt6.QtGui import QAction, QPixmap, QWheelEvent
from PyQt6.QtCore import Qt
from pathlib import Path
import webbrowser
import zipfile
import shutil
import sys
import os

class MainWindow(QMainWindow): 
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ComicFLUX")
        self.setGeometry(100, 100, 800, 600)

        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        open_action = QAction("&Open", self)
        open_action.triggered.connect(self.locate_file)
        file_menu.addAction(open_action)

        help_menu = menubar.addMenu("&Help")
        help_action = QAction("&Docs", self)
        help_action.triggered.connect(self.open_docs)
        help_menu.addAction(help_action)

        # Image container
        self.image_container = QLabel()
        self.image_container.setPixmap(QPixmap())
        self.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a QScrollArea and set the image label as its widget
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_container)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.setCentralWidget(self.scroll_area)

        self.filename = None
        self.filename_path = None
        self.counter = 0  # Counter keeps track of index for paths list
        self.image_count = 0  # Total image count
        self.is_loading_image = False # Prevent multiple counter updates during scroll wheel change
        # Ensure inputs go to main window object
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.show()

    # Override mouse wheel event. For webtoon format, it checks the scrollbar position to determine if it should load next or previous image. 
    # Otherwise, it checks how many degrees the mouse wheel has changed, and chooses the next image based on sign.  
    def wheelEvent(self, event):
        # Non webtoon format
        if self.image_container.height() < self.frameSize().height():  
            # QWheelEvent.angleDelta returns QPoint object (a point in the plane), so we need to get it's y value, an int, for the comparison
            deltaY = QWheelEvent.angleDelta(event).y()
            # Scroll up since angleDelta is positive ( positive is away from user; negative is towards user )
            if deltaY > 0 and self.counter >= 1:
                self.counter -= 1
                self.query_image()
            elif deltaY < 0 and self.counter < self.image_count-1:
                self.counter += 1
                self.query_image()
            
            # Do normal mousewheel event after custom one 
            super().wheelEvent(event)
            return
        
        # Webtoon format
        else:
            # Guard against multiple counter updates
            if self.is_loading_image:
                return
            
            current_position = self.scroll_area.verticalScrollBar().value()
            min_position = self.scroll_area.verticalScrollBar().minimum()
            max_position = self.scroll_area.verticalScrollBar().maximum()

            if current_position == max_position and self.counter < self.image_count-1:
                self.is_loading_image = True
                self.counter += 1 
                self.query_image()
                self.last_scrollbar_position = current_position 
                self.is_loading_image = False

            elif current_position == min_position and self.counter >= 1:  
                self.counter -= 1
                self.query_image()
                self.scroll_area.verticalScrollBar().setValue(self.last_scrollbar_position)  

            super().wheelEvent(event)

    # Binds left and right arrow keys to flip between images
    def keyPressEvent(self, event): 
        if event.key() == Qt.Key.Key_Left and self.counter >= 1: 
            self.counter -= 1
            self.query_image()
        elif event.key() == Qt.Key.Key_Right and self.counter < self.image_count-1: 
            self.counter += 1
            self.query_image()
        else:
            super().keyPressEvent(event)

    # Allows user to choose file to open, queries first image to display
    def locate_file(self): 
        if self.counter > 0:
            self.cleanup()

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select a File", 
            "C:", 
            "CBZ, RAR, and ZIP Files (*.cbz *.rar *.zip)"
        )
        if filename:
            filepath = Path(filename).resolve()
            self.filename_path = str(filepath)
            self.filename = filename

            # Unzip file and begin queries
            self.foldername = self.remove_extension(filename) 
            self.folderpath = self.remove_extension(str(filepath))
            self.unzip(filename)
            self.image_paths = self.get_image_paths()
            self.image_count = len(self.image_paths)
            self.counter = 0
            self.query_image()
            self.setWindowState(Qt.WindowState.WindowMaximized)

    # Loads image from extracted folder based on counter
    def return_image(self, pos):
        return self.load_image(self.image_paths[pos])

    # Creates list comprehension of image files in extracted folder
    def get_image_paths(self): 
        folderpath = self.folderpath
        return [file for file in os.listdir(folderpath) if os.path.isfile(os.path.join(folderpath, file))] 
        

    # Load image into QPixmap format for drawing
    def load_image(self, image):
        filepath = f"{self.folderpath}/{image}"
        return QPixmap(filepath) 

    # Unzip comic archive
    def unzip(self, input):
        with zipfile.ZipFile(f"{input}", "r") as file:
            if os.path.exists(self.foldername):
                self.cleanup()

            os.mkdir(self.foldername)
            file.extractall(self.foldername)

    # Delete extracted folder
    def cleanup(self):
        shutil.rmtree(self.foldername) 

    # Remove extensions
    def remove_extension(self, string):
        string = string.replace(".cbz", "")
        string = string.replace(".rar", "")
        string = string.replace(".zip", "")
        return string

    # Get image and display it 
    def query_image(self): 
        pixmap = self.return_image(self.counter)

        self.image_container.clear() 
        self.image_container.resize(pixmap.size())
        self.image_container.setPixmap(pixmap)
        self.image_container.adjustSize()

    # Docs
    def open_docs(self):
        webbrowser.open("https://github.com/lgtipton4/ComicFlux")

    # Deletes folder before exiting
    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)


def start():
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    start()