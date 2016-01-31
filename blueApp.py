from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtGui import QPixmap
import blueMainUi
import sys


class BlueApp:
    def __init__(self, argv):
        self.app = QApplication(argv)

        self.mainWindow = QtWidgets.QMainWindow()
        self.ui = blueMainUi.Ui_MainWindow()
        self.ui.setupUi(self.mainWindow)

        #some adjusts
        pixmap = QPixmap()
        pixmap.load("circle.png")
        pixmap.scaled(115, 115)
        self.ui.lb_avata.setMask(pixmap.mask())
        pixmap.load("flower.png")
        self.ui.lb_avata.setPixmap(pixmap)

        self.mainWindow.show()


        #setup event handling
        self.sideButtons = [self.ui.lb1, self.ui.lb2, self.ui.lb3, self.ui.lb4]
        self.selectedSideButton = self.ui.lb1
        self.setupSideButtons()

        self.connections()

    def slideEnter1(self, event):
        if self.selectedSideButton != self.ui.lb1:
            self.ui.lb1.setStyleSheet("background-color: rgb(236,106,0);")

    def slideEnter2(self, event):
        if self.selectedSideButton != self.ui.lb2:
            self.ui.lb2.setStyleSheet("background-color: rgb(236,106,0);")

    def slideEnter3(self, event):
        if self.selectedSideButton != self.ui.lb3:
            self.ui.lb3.setStyleSheet("background-color: rgb(236,106,0);")

    def slideEnter4(self, event):
        if self.selectedSideButton != self.ui.lb4:
            self.ui.lb4.setStyleSheet("background-color: rgb(236,106,0);")

    def slideLeave1(self, event):
        if self.selectedSideButton != self.ui.lb1:
            self.ui.lb1.setStyleSheet("background-color: rgb(42,49,59);")

    def slideLeave2(self, event):
        if self.selectedSideButton != self.ui.lb2:
            self.ui.lb2.setStyleSheet("background-color: rgb(42,49,59);")

    def slideLeave3(self, event):
        if self.selectedSideButton != self.ui.lb3:
            self.ui.lb3.setStyleSheet("background-color: rgb(42,49,59);")

    def slideLeave4(self, event):
        if self.selectedSideButton != self.ui.lb4:
            self.ui.lb4.setStyleSheet("background-color: rgb(42,49,59);")

    def slideClicked1(self, event):
        self.selectedSideButton.setStyleSheet("background-color: rgb(42,49,59);")
        self.selectedSideButton = self.ui.lb1
        self.ui.lb1.setStyleSheet("background-color: rgb(254,190,0);")


    def slideClicked2(self, event):
        self.selectedSideButton.setStyleSheet("background-color: rgb(42,49,59);")
        self.selectedSideButton = self.ui.lb2
        self.ui.lb2.setStyleSheet("background-color: rgb(254,190,0);")

    def slideClicked3(self, event):
        self.selectedSideButton.setStyleSheet("background-color: rgb(42,49,59);")
        self.selectedSideButton = self.ui.lb3
        self.ui.lb3.setStyleSheet("background-color: rgb(254,190,0);")

    def slideClicked4(self, event):
        self.selectedSideButton.setStyleSheet("background-color: rgb(42,49,59);")
        self.selectedSideButton = self.ui.lb4
        self.ui.lb4.setStyleSheet("background-color: rgb(254,190,0);")

    def setupSideButtons(self):
        self.ui.lb1.enterEvent = self.slideEnter1
        self.ui.lb1.leaveEvent = self.slideLeave1
        self.ui.lb1.mousePressEvent = self.slideClicked1
        self.ui.lb2.enterEvent = self.slideEnter2
        self.ui.lb2.leaveEvent = self.slideLeave2
        self.ui.lb2.mousePressEvent = self.slideClicked2
        self.ui.lb3.enterEvent = self.slideEnter3
        self.ui.lb3.leaveEvent = self.slideLeave3
        self.ui.lb3.mousePressEvent = self.slideClicked3
        self.ui.lb4.enterEvent = self.slideEnter4
        self.ui.lb4.leaveEvent = self.slideLeave4
        self.ui.lb4.mousePressEvent = self.slideClicked4

        self.ui.lb1.setStyleSheet("background-color: rgb(254,190,0);")

    def connections(self):
        pass

    def aa(self, event):
        print(self)
        print(event.type)


blueapp = BlueApp(sys.argv)
input()
