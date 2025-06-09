import json
import os

from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow

from pixel import Pixel
from ui_pixel import Ui_Dialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建UI实例（组合而非继承）
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # 图像处理
        self.pixel = Pixel()

        self.ui.pushButton_1.clicked.connect(
            lambda:
            self.generate_preview(
                self.ui.lineEdit_path.text(),
                self.ui.lineEdit_interval.text(),
                self.ui.checkBox.isChecked()
            )
        )

        self.ui.pushButton_2.clicked.connect(
            lambda:
            self.save_image(
                self.ui.lineEdit_path.text(),
                self.ui.lineEdit_interval.text(),
                self.ui.checkBox.isChecked()
            )
        )

        self.ui.pushButton_3.clicked.connect(
            lambda:
            self.save_json(
                self.ui.lineEdit_path.text(),
                self.ui.lineEdit_interval.text(),
                self.ui.checkBox.isChecked()
            )
        )

    @staticmethod
    def pil_to_pixmap(pil_image):
        # 将PIL图像转换为字节数据
        bytes_img = pil_image.tobytes("raw", pil_image.mode)

        # 创建QImage
        qimg = QImage(bytes_img, pil_image.width, pil_image.height, QImage.Format_RGBA8888)

        # 创建QPixmap
        pixmap = QPixmap.fromImage(qimg)
        return pixmap

    def display(self, pil_image, background_color):
        json_display = self.pixel.get_json()
        self.ui.label_show.setPixmap(self.pil_to_pixmap(pil_image))
        self.ui.label_show.setScaledContents(False)
        if json_display["size"]["width"] > 600 or json_display["size"]["height"] > 600:
            self.ui.label_show.setGeometry(
                QtCore.QRect(0, 60, json_display["size"]["width"], json_display["size"]["height"]))
        if background_color:
            self.ui.label_show.setStyleSheet("background-color: #FFFFFF;")
        else:
            self.ui.label_show.setStyleSheet("background-color: #000000;")
        self.information(f"""
        宽/高:{str(json_display["size"]["width"]) + "/" + str(json_display["size"]["height"])}<br/>
        粒子数量:{json_display["count"] if json_display["count"] <= 9999 else str(json_display["count"]) +
                                                                              "<br/>(粒子数量过大可能显示不全)"}
        """, "信息" if json_display["count"] <= 9999 else "警告")

    def information(self, text, exception="信息"):
        match exception:
            case "警告":
                text = "<font color='orange'>警告:<br/><font/>" + text
            case "报错":
                text = "<font color='red'>报错:<br/><font/>" + text
            case _:
                text = "信息:<br/>" + text
        self.ui.label_Information.setText(text)

    def generate_preview(self, path, interval, background_color):
        if not interval.isdigit():
            self.information(f"间隔必须为正整数", "报错")
            return False
        try:
            self.pixel = Pixel()
            match os.path.splitext(path)[1].lower():
                case ".png" | ".jpg" | ".jpeg":  # 图片
                    self.pixel.image_to_json(path, int(interval))
                    self.pixel.json_to_pil()
                    self.display(self.pixel.get_pil_image(), background_color)
                    return True
                case ".json":  # json
                    self.pixel.json_to_pil(path)
                    self.display(self.pixel.get_pil_image(), background_color)
                    return True
                case _:  # 报错
                    self.information("文件类型错误", "报错")
        except json.JSONDecodeError:
            self.information("JSON 解码错误", "报错")
        except ValueError:
            self.information("JSON 解包错误", "报错")
        except FileNotFoundError:
            self.information("文件不存在", "报错")
        except Exception as e:
            # 捕获其他所有类型的异常
            print(e)
            self.information(str(e), "报错")
        return False

    def save_image(self, path, interval, background_color):
        if self.generate_preview(path, interval, background_color):
            filename_with_ext = os.path.basename(path)
            filename, ext = os.path.splitext(filename_with_ext)
            self.pixel.get_pil_image().save(filename + '_image.png')

    def save_json(self, path, interval, background_color):
        if self.generate_preview(path, interval, background_color):
            json_data = json.dumps(self.pixel.get_json())
            filename_with_ext = os.path.basename(path)
            filename, ext = os.path.splitext(filename_with_ext)
            with open(filename + '_json.json', 'w') as f:
                f.write(json_data)


# 添加主函数
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
