# Comic Book Reader
# Open .cbz, .rar, .zip files. 
# Read images in
# Display them
# Have scroll function
# Image caching for long strip manhwa
# Maybe need a way to differentiate between long strip and regular. Can do this by 
#    image dimension. Need to calculate proper zoom level as well.

# need to remember where user last was. 

import zipfile 
import time
import os 
import shutil
import gui
from pathlib import Path
from PIL import Image
from PIL.ImageQt import ImageQt

class Main:
    def __init__(self, filename, filepath):
        self.filename = filename
        self.filepath = filepath

        self.foldername = self.remove_extension(filename)
        self.folderpath = self.remove_extension(filepath)

        self.unzip(filename)

        self.image_paths = self.get_image_paths()

    # Removes extensions
    def remove_extension(self, string):
        string = string.replace(".cbz", "")
        string = string.replace(".rar", "")
        string = string.replace(".zip", "")
        return string

    # Unzips archive
    def unzip(self, input):
        with zipfile.ZipFile(f"{input}", "r") as file:
            os.mkdir(self.foldername)
            file.extractall(self.foldername)

    def cleanup(self):
        shutil.rmtree(self.foldername) # delete folder

    # List comprehension to get files in the extracted folder
    def get_image_paths(self): 
        folderpath = self.folderpath
        image_list = [file for file in os.listdir(folderpath) if os.path.isfile(os.path.join(folderpath, file))] 
        # for file in image_list:
        #     print(file)

        return image_list
    
    # Loads image from file
    def load_image(self, image):
        filepath = f"{self.folderpath}/{image}"
        im = Image.open(filepath)
        # print(filepath)
        # print("past opening image")
        return ImageQt(im) 

    # Returns image. The GUI calls this a lot 
    def return_image(self, pos):
        return self.load_image(self.image_paths[pos])