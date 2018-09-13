from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QImage, QFont
import cv2


class AppConfig:

    # frame of camera area
    # rate with screen
    frame_width_rate = 0.5
    frame_height_rate = 0.5
    frame_x_rate = 0.1
    frame_y_reate = 0.1

    # user information area
    user_info_title_sex = '性別: '
    user_info_title_age = '年齡: '
    user_info_top_boundary = 50
    user_info_left_boundary_rate = 1.1
    user_info_label_width = 600
    user_info_label_height = 100
    user_info_font_format = QFont("Times", 72, QFont.Bold)

    # goods information area
    goods_info_font_format = QFont("Times", 30, QFont.Bold)
    goods_image_width = 200
    goods_image_height = 200
    goods_name_width = 200
    goods_name_height = 40
    goods_y_top_boundary = 1.1
    goods_boundary = 250


class MainWidget(QWidget):

    def __init__(self,app, th):
        super(self.__class__, self).__init__()
        screen = app.primaryScreen().size()
        self.width_screen = screen.width()
        self.height_screen = screen.height()
        self.user_id = None

        self.image_label = QLabel(self)
        # image_label size
        self.image_label_width = self.width_screen * AppConfig.frame_width_rate
        self.image_label_height = self.height_screen * AppConfig.frame_height_rate
        self.image_label.resize(self.image_label_width, self.image_label_height)
        # ===>image_label location
        self.image_label_x = (self.width_screen - self.image_label_width) * AppConfig.frame_x_rate
        self.image_label_y = (self.height_screen - self.image_label_height) * AppConfig.frame_y_reate
        self.image_label.move(self.image_label_x, self.image_label_y)

        # share parameter
        self.user_info_label_x = (self.image_label_x + self.image_label_width) * AppConfig.user_info_left_boundary_rate

        self.sex_label = QLabel(self)
        # ===>sex_label location
        self.sex_label_x = self.user_info_label_x
        self.sex_label_y = self.image_label_y
        self.sex_label.move(self.sex_label_x, self.sex_label_y)
        # ===>sex_label size
        self.sex_label.resize(AppConfig.user_info_label_width, AppConfig.user_info_label_height)
        # ===>sex_label font
        self.sex_label.setText(AppConfig.user_info_title_sex)
        self.sex_label.setFont(AppConfig.user_info_font_format)

        self.age_label = QLabel(self)
        # ===>age_label location
        self.age_label_x = self.user_info_label_x
        self.age_label_y = (self.sex_label_y + AppConfig.user_info_label_height) + AppConfig.user_info_top_boundary
        self.age_label.move(self.age_label_x, self.age_label_y)
        # ===>age_label size
        self.age_label.resize(AppConfig.user_info_label_width, AppConfig.user_info_label_height)
        # ===>age_label font
        self.age_label.setText(AppConfig.user_info_title_age)
        self.age_label.setFont(AppConfig.user_info_font_format)

        # goods
        self.goods_label_list = []
        for i in range(7):
            goods_dict = {}

            # parameter
            image_x = self.image_label_x + i * AppConfig.goods_boundary
            image_y = (self.image_label_y + self.image_label_height) * AppConfig.goods_y_top_boundary

            image_label = QLabel(self)
            image_label.setScaledContents(True)
            image_label.resize(AppConfig.goods_image_width, AppConfig.goods_image_height)
            image_label.move(image_x, image_y)

            name_label = QLabel(self)
            name_x = image_x + (AppConfig.goods_image_width - AppConfig.goods_name_width) / 2
            name_y = (image_y + AppConfig.goods_image_height)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.move(name_x, name_y)
            name_label.resize(AppConfig.goods_name_width, AppConfig.goods_name_height)
            name_label.setFont(AppConfig.goods_info_font_format)

            goods_dict['image_label'] = image_label
            goods_dict['name_label'] = name_label
            self.goods_label_list.append(goods_dict)

        th.label_image_signal.connect(self.updateMainWidgetSlot)
        th.start()
        self.showFullScreen()

    def convertNp2Qpixmap(self, image_np):
        rgbImage = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        qimage = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
        qimage = qimage.scaled(self.image_label_width, self.image_label_height)
        qpixmap = QPixmap.fromImage(qimage)
        return qpixmap

    @pyqtSlot(dict)
    def updateMainWidgetSlot(self, info_dict):
        label_image_np = info_dict.get('frame')
        # update frame of camera
        qpixmap = self.convertNp2Qpixmap(label_image_np)
        self.image_label.setPixmap(qpixmap)

        user_id = info_dict.get("id", None)
        if user_id is None:
            self.sex_label.setText(AppConfig.user_info_title_sex)
            self.age_label.setText(AppConfig.user_info_title_age)
            for goods  in self.goods_label_list:
                image_label = goods['image_label']
                name_label = goods['name_label']
                image_label.clear()
                name_label.setText("")
            self.user_id = None
        elif self.user_id != user_id:
            sex_str = info_dict.get('sex', None)
            age_str = info_dict.get('age', None)
            goods = info_dict.get('goods', None)
            # update sex text
            if sex_str is not None:
                self.sex_label.setText(AppConfig.user_info_title_sex + sex_str)
            # update age text
            if age_str is not None:
                self.age_label.setText(AppConfig.user_info_title_age + age_str)
            # update goods
            if goods is not None:
                for index, good in enumerate(goods):
                    name = good['name']
                    name_label = self.goods_label_list[index]['name_label']
                    name_label.setText(name)

                    image = good['image']
                    image_label = self.goods_label_list[index]['image_label']
                    qpixmap = self.convertNp2Qpixmap(image)
                    image_label.setPixmap(qpixmap)

            self.user_id = user_id

    # exit event
    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Q:
            self.close()

