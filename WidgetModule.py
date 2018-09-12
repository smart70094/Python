import sys
from PyQt5.QtWidgets import QApplication, QWidget,QLabel
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QImage,QFont

import numpy as np
import cv2
import time

class Thread(QThread):
    label_image_signal = pyqtSignal(dict)
    cammer = cv2.VideoCapture(0)

    dict_info = {}
    def run(self):
        count = 0
        while True:
            ret, image_np = self.cammer.read()
            if ret:
                self.dict_info['frame'] = image_np
                self.dict_info['name'] = '賴'
                self.dict_info['sex'] = '男'
                self.dict_info['age'] = str(count)
                count += 1

                self.label_image_signal.emit(self.dict_info)

class MainWidget(QWidget):

    # image_label => frame of camera

    def __init__(self,app, th):
        super(self.__class__, self).__init__()
        screen = app.primaryScreen().size()
        self.width_screen = screen.width()
        self.height_screen = screen.height()

        self.image_label = QLabel(self)
        # image_label size
        self.image_label_width = self.width_screen * 0.5
        self.image_label_height = self.height_screen * 0.5
        self.image_label.resize(self.image_label_width, self.image_label_height)
        # ===>image_label location
        self.image_label_x = (self.width_screen - self.image_label_width) * 0.1
        self.image_label_y = (self.height_screen - self.image_label_height) * 0.1
        self.image_label.move(self.image_label_x, self.image_label_y)

        # share paramater
        self.user_info_label_x = (self.image_label_x + self.image_label_width) * 1.1
        user_info_font_format = QFont("Times", 72, QFont.Bold)

        self.name_label = QLabel(self)
        # ===>name_label location
        self.name_label_x = self.user_info_label_x
        self.name_label_y = self.image_label_y
        self.name_label.move(self.name_label_x, self.name_label_y)
        # ===>name_label font
        self.name_label.setText("Jim")
        self.name_label.setFont(user_info_font_format)

        self.sex_label = QLabel(self)
        # ===>sex_label location
        self.sex_label_x = self.user_info_label_x
        print("name_label_y:%s, name_label height:%s" % (self.name_label_y, self.name_label.height()))
        self.sex_label_y = (self.name_label_y + self.name_label.height()) * 2
        self.sex_label.move(self.sex_label_x, self.sex_label_y)
        # ===>sex_label font
        self.sex_label.setText(" 男")
        self.sex_label.setFont(user_info_font_format)

        self.age_label = QLabel(self)
        # ===>age_label location
        self.age_label_x = self.user_info_label_x
        self.age_label_y = (self.sex_label_y + self.name_label.height()) * 1.5
        self.age_label.move(self.age_label_x, self.age_label_y)
        # ===>age_label font
        self.age_label.setText("20")
        self.age_label.setFont(user_info_font_format)



        th.label_image_signal.connect(self.updateMainWidgetSlot)
        th.start()

        self.showFullScreen()


    @pyqtSlot(dict)
    def updateMainWidgetSlot(self, info_dict):

        label_image_np = info_dict['frame']
        print(label_image_np)
        rgbImage = cv2.cvtColor(label_image_np, cv2.COLOR_BGR2RGB)
        qimage = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
        qimage = qimage.scaled(self.image_label_width, self.image_label_height)
        qpixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(qpixmap)

        name_str = info_dict.get('name',None)
        sex_str = info_dict.get('sex',None)
        age_str = info_dict.get('age', None)

        if name_str is not None:
            self.name_label.setText(name_str)

        if sex_str is not None:
            self.sex_label.setText(sex_str)

        if age_str is not None:
            self.age_label.setText(age_str)


    # exit event
    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Q:
            self.close()


def main():
    app = QApplication(sys.argv)
    th = Thread()
    mainWidget = MainWidget(app, th)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()