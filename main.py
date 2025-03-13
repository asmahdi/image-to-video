import os
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QFileDialog)
from PyQt5.QtCore import QtCore
from PyQt5 import uic 
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from gui import Ui_gui

VERSION = "0.1.0-alpha"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
qapp = QApplication(sys.argv)
qapp.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)


class GifCreator(QWidget, Ui_gui):

    image_types = ["png", "jpg"]


    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setupUi(self)
        #uic.loadUi("gui.ui", self)
        self.browse_outputPath_btn.clicked.connect(self.set_outputFile)
        self.browse_inputPath_btn.clicked.connect(self.browse_folder)
        self.export_btn.clicked.connect(self.start_gif_creation)
        self.type_ComboBox.addItems(self.image_types)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.inputPath_lineEdit.setText(folder)

    def set_outputFile(self):
        file = QFileDialog.getSaveFileName(self, "Save GIF", "", "GIF Files (*.gif)")
        if file[0]:
            self.outputPath_lineEdit.setText(file[0])

    def resize_image_by_percentage(self,file_path, scale_percent):
        img = Image.open(file_path)
        img = img.convert("RGB")
        new_width = int(img.width * (scale_percent / 100))
        new_height = int(img.height * (scale_percent / 100))
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img = img.convert("P")
        return img

    def create_gif(self, input_folder, output_gif, duration=1000, scale_percent=50):
        files = []
        png_files = sorted([f for f in os.listdir(input_folder) if f.lower().endswith('.png')])
        jpeg_files = sorted([f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg','.jpeg'))])
        if self.type_ComboBox.currentText() == "png":
            files = png_files
        elif self.type_ComboBox.currentText() == "jpg":
            files = jpeg_files

        if not files:
            print("No files found in the specified folder.")
            self.status_label.setText("No files found in the specified folder.")
            return
        
        image_paths = [os.path.join(input_folder, f) for f in jpeg_files]
        with ThreadPoolExecutor() as executor:
            images = list(executor.map(lambda path: self.resize_image_by_percentage(path, scale_percent), image_paths))
        
        self.status_label.setText("Creating GIF...")
        images[0].save(output_gif, save_all=True, append_images=images[1:], duration=duration, loop=0)
        print(f"GIF saved in {output_gif}")
        self.status_label.setText(f"GIF saved in {output_gif}")
        

    def start_gif_creation(self):
        input_folder = self.inputPath_lineEdit.text()
        output_gif = self.outputPath_lineEdit.text()
        duration = self.duration_spinBox.value()
        scale_percent = self.scale_spinBox.value()

        if not input_folder or not output_gif:
            print("Please select a folder and specify an output GIF file.")
            return

        self.create_gif(input_folder, output_gif, duration, scale_percent)

def main():
    app = QApplication([])
    window = GifCreator()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()