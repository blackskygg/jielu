
import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QLabel
from PyQt5.QtCore import QPropertyAnimation, QRect, QByteArray, QTimer, QTimerEvent
from PyQt5.QtGui import QPixmap, QMovie, QIcon
import sys, time, os
import json

import blueMainUi
import porn_detector_final
import threading

PATH_TO_SETTINGS = "jielu.conf"
PATH_TO_STATISTICS = "jielu.stat"

slide_bt_down = "background-color: rgb(254,190,0); color: #2a313b"
slide_bt_up = "background-color: rgb(42,49,59); color: #757575"
slide_bt_mid = "background-color: rgb(236,106,0); color: #757575"

porn_detected = False
image = True
text = False
develop = False

def call_zqz():
    pass

class BlueApp:
    def __init__(self, argv):
        self.app = QApplication(argv)

        self.mainWindow = QtWidgets.QMainWindow()
        self.mainWindow.closeEvent = self.onClose
        self.ui = blueMainUi.Ui_MainWindow()
        self.ui.setupUi(self.mainWindow)


        #settings and statistics
        self.defaultSettings = dict(image_detect=True, text_detect=True,
                                    game_type=0, pipeRank=0,
                                    goal = 10, startDate = time.time(),
                                    avata = "res/icon.png", name = "窜天猴")
        self.defaultStat = dict(stat = [ [0, 0, 0, 0] for i in range(7)],
                                achivement = 0, lastWater = 0, lastFertilize = 0,
                                cleanHours = 0, cleanMinutes = 0)
        self.achivementsList = ["大淫魔", "从头开始", "欲火渐盛",
                                "钢筋铁骨", "渐入佳境","心无杂念"]
        self.achivementsStd = [0, 24, 24 * 3, 24 * 7, 24 * 31, 27 * 365]
        self.loadSettings()
        self.validateSettings()
        self.loadStatistics()

        #setup the visibles
        self.setupUi2()
        self.setupWidget1()
        self.setupWidget2()
        self.setupWidget3()
        self.setupWidget4()
        self.refreshStatistics()


        #setup porn_detector
        self.devMode = False
        self.timeToExit = False
        self.pornDectector = porn_detector_final.PornDetector()
        self.pornDetected = False
        self.detectThread = threading.Thread(target = self.detectPorn)
        self.detectThread.start()
        self.alarm = False  #first alarm, then take action

        #setup timer
        self.cleanMinute = 0
        self.MinuteTimer = QTimer()
        self.MinuteTimer.setInterval(1000 * 60)
        self.MinuteTimer.timeout.connect(self.addCleanMinute)
        self.MinuteTimer.start()


        #lauch
        self.mainWindow.show()

        self.connections()

    def addCleanMinute(self):
        self.stat["cleanMinutes"] += 1
        if self.stat["cleanMinutes"] == 60:
            self.self.stat["cleanMinutes"] = 0
            self.stat["cleanHours"] += 1
            self.saveStatistics()
            self.refreshStatistics()
            self.checkLevel()

    def call_zqz(self):
        if self.settings["game_type"] == 0:
            os.system("python2 easy_maze/PyMaze.py")
        else :
            os.system("python2 esay_game/play.py")
        QtWidgets.QMessageBox.information(None, "bluer", "你有10s的时间关掉黄黄的东西。")
        time.sleep(10)



    def detectPorn(self):
        while(True):
            if "PORN_DETECTED" == self.pornDectector.porn_detector(self.settings["image_detect"], self.settings["text_detect"], self.devMode):
                if self.alarm:
                    self.call_zqz()
                    self.stat["cleanHours"] -= 24
                    if self.stat["cleanHours"] < 0:
                        self.stat["cleanHours"] = 0

                    l = self.stat["stat"][time.localtime(time.time())[6]]
                    h = time.localtime(time.time())[3]
                    if h >= 0 and h < 6:
                        l[0] = 1
                    elif h >= 6 and h < 12:
                        l[1] = 1
                    elif h >= 12 and h < 18:
                        l[2] = 1;
                    else:
                        l[3] = 1;
                else:
                    self.alarm = True
            else:
                self.alarm = True

                self.saveStatistics()
                self.refreshStatistics()

            time.sleep(10)

    def onClose(self, event):
        self.mainWindow.hide()
        event.ignore()

    def onTrayClicked(self, event):
        if event == QSystemTrayIcon.Trigger or event == QSystemTrayIcon.DoubleClick:
            self.mainWindow.show()

    def saveSettings(self, event):
        QtWidgets.QMessageBox.Question = QIcon("res/logo-tray.png")
        if self.settings["goal"] != self.ui.spin_goal.value():
            ret = QtWidgets.QMessageBox.question(self.mainWindow, "Blue", "确定要将目标改为" + str(self.ui.spin_goal.value()) + "天吗？\n"
                                                 "此操作会重置当前任务的进度。")

            if ret != QtWidgets.QMessageBox.No:
                self.settings["goal"] = self.ui.spin_goal.value()
                self.saveStatistics()
                self.refreshStatistics()
                QtWidgets.QMessageBox.information(None, "Blue", "新目标设置为" + str(self.settings["goal"]) + "天")
            else:
                QtWidgets.QMessageBox.information(None, "Blue", "目标没有被重置")

        try:
            sfile = open(PATH_TO_SETTINGS, "w")
            json.dump(self.settings, sfile)
            sfile.close()
        except Exception:
            return

        QtWidgets.QMessageBox.information(None, "Blue", "设置已保存:D")

        self.refreshStatistics()

    def checkLevel(self):
        for i in range(5, -1, -1):
            if self.stat["cleanHours"] >= self.achivementsStd[i] and self.stat["achivement"] < i:
                QtWidgets.QMessageBox.information(None, "Blue", "等级提升为Lv. " + str(i) + " :" + self.achivementsList[i])
                self.stat["achivement"] = i
                self.saveStatistics()
                break

    def saveStatistics(self):
        json.dump(self.stat, open(PATH_TO_STATISTICS, "w"))

    def refreshStatistics(self):
        days = time.localtime(time.time())

        delta = self.settings["goal"] - self.stat["cleanHours"]

        if delta == 0:
            QtWidgets.QMessageBox.information(None, "Blue", "目标达成！！！\n请设置新的目标！！！")
            self.slideClicked3(None)

        self.ui.lb_days.setText(str(delta))
        self.ui.lb_goal.setText(str(self.settings["goal"]))
        self.ui.lb_achv.setText(self.achivementsList[self.stat["achivement"]])
        self.ui.lb_lv.setText("Lv. " + str(self.stat["achivement"]))
        self.ui.lb_growth.setText(str(self.stat["cleanHours"] // 24))

        #setup the water and ferilization
        if days[7] == time.localtime(self.stat["lastWater"])[7]:
            self.ui.lb_jiaoshui.setPixmap(QPixmap("res/ack.png"))
            self.watered = True
        else:
            self.watered = False

        if days[7] == time.localtime(self.stat["lastFertilize"])[7]:
            self.ui.lb_shifei.setPixmap(QPixmap("res/ack.png"))
            self.fertilized = True
        else:
            self.fertilized = False



        #setup the calendar
        pixmapA = QPixmap("res/lu.png")
        pixmapB = QPixmap("res/blue.png")

        h = days[3]
        if h >= 0 and h < 6:
            r = 0
        elif h >= 6 and h < 12:
            r = 1
        elif h >= 12 and h < 18:
            r = 2
        else:
            r = 3

        for i in range(days[6]):
            for j in range(4):
                if self.stat["stat"][i][j] == 0:
                    self.statLabels[i][j].setPixmap(pixmapA)
                else:
                    self.statLabels[i][j].setPixmap(pixmapB)

        day = days[6]
        for j in range(r):
            if self.stat["stat"][day][j] == 0:
                self.statLabels[day][j].setPixmap(pixmapA)
            else:
                self.statLabels[day][j].setPixmap(pixmapB)

        #setup the wall
        for i in range(6):
            self.achivIcons[i].setPixmap(QPixmap("res/" + str(i) * 2))

        for i in range(self.stat["achivement"] + 1):
            self.achivIcons[i].setPixmap(QPixmap("res/" + str(i)))


    def loadSettings(self):
        try:
            sfile = open(PATH_TO_SETTINGS, "r")
            self.settings = json.load(sfile)
            sfile.close()
        except:
            self.settings = self.defaultSettings
            self.saveSettings(None)

    def validateSettings(self):
        for keys in self.defaultSettings:
            try:
                self.settings[keys]
            except:
                self.settings[keys] = self.defaultSettings[keys]

    def loadStatistics(self):
        try:
            sfile = open(PATH_TO_STATISTICS, "r")
            self.stat = json.load(sfile)
        except:
            self.stat = self.defaultStat

        for keys in self.defaultStat:
            try:
                self.stat[keys]
            except:
                self.stat[keys] = self.defaultStat[keys]
        self.saveStatistics()

    def refreshInfo(self):
        #setup avata
        pixmap = QPixmap()
        pixmap.load("res/avata_mask")
        pixmap.scaled(115, 115)
        self.ui.lb_avata.setMask(pixmap.mask())
        pixmap.load(self.settings["avata"])
        self.ui.lb_avata.setPixmap(pixmap)

#        self.ui.lb_avata2.setMask(pixmap.mask())
#        pixmap.load(self.settings["avata"])
#        self.ui.lb_avata2.setPixmap(pixmap)


        #setup the name
        self.ui.lb_welcomname.setText(self.settings["name"])
        self.ui.lb_nick.setText(self.settings["name"])



    def appExit(self, event):
        if self.devMode == False:
            QtWidgets.QMessageBox.information(None, "bluer", "开发者模式开启")
            self.devMode = True
        else:
            QtWidgets.QMessageBox.information(None, "bluer", "开发者模式关闭")
            self.devMode = False

    def avataEdit(self, event):
        openDlg = QtWidgets.QFontDialog()
        openDlg.open()

    def setupUi2(self):
        #setup event handling
        self.sideButtons = [self.ui.lb1, self.ui.lb2, self.ui.lb3, self.ui.lb4]
        self.ui.lb_exit.mousePressEvent = self.appExit
        self.setupAnimes()
        self.setupSideButtons()
        self.refreshInfo()

        #setup tray
        self.icon = QIcon("res/logo-tray.png")
        self.trayIcon = QSystemTrayIcon()
        self.trayIcon.setIcon(self.icon)
        self.trayIcon.activated.connect(self.onTrayClicked)
        self.trayIcon.show()

        #setup the info edit
        self.ui.lb_avata.mousePressEvent = self.avataEdit

    def setupAnimes(self):
        self.shiftAnime1 = QPropertyAnimation()
        self.shiftAnime1.setTargetObject(self.ui.widget1)
        self.shiftAnime1.setPropertyName("geometry".encode())
        self.shiftAnime1.setDuration(400)
        self.shiftAnime1.setStartValue(QRect(177, 29, 0, 571))
        self.shiftAnime1.setEndValue(QRect(177, 29, 623, 571))

        self.shiftAnime2 = QPropertyAnimation()
        self.shiftAnime2.setTargetObject(self.ui.widget2)
        self.shiftAnime2.setPropertyName("geometry".encode())
        self.shiftAnime2.setDuration(400)
        self.shiftAnime2.setStartValue(QRect(800, 29, 0, 571))
        self.shiftAnime2.setEndValue(QRect(177, 29, 623, 571))

        self.shiftAnime3 = QPropertyAnimation()
        self.shiftAnime3.setTargetObject(self.ui.widget3)
        self.shiftAnime3.setPropertyName("geometry".encode())
        self.shiftAnime3.setDuration(400)
        self.shiftAnime3.setStartValue(QRect(800, 29, 623, 571))
        self.shiftAnime3.setEndValue(QRect(177, 29, 623, 571))

        self.shiftAnime4 = QPropertyAnimation()
        self.shiftAnime4.setTargetObject(self.ui.widget4)
        self.shiftAnime4.setPropertyName("geometry".encode())
        self.shiftAnime4.setDuration(400)
        self.shiftAnime4.setStartValue(QRect(800, 29, 623, 571))
        self.shiftAnime4.setEndValue(QRect(177, 29, 623, 571))

        self.selectedWidget = self.ui.widget1


    def setSlideMid(self, bt):
        if self.selectedSideButton != bt:
            bt.setStyleSheet(slide_bt_mid)

    def setSlideUp(self, bt):
        if self.selectedSideButton != bt:
            bt.setStyleSheet(slide_bt_up)

    def setSlideDown(self, bt):
        self.selectedSideButton.setStyleSheet(slide_bt_up)
        self.selectedSideButton = bt
        bt.setStyleSheet(slide_bt_down)


    def slideEnter1(self, event):
        self.setSlideMid(self.ui.lb1)

    def slideEnter2(self, event):
        self.setSlideMid(self.ui.lb2)

    def slideEnter3(self, event):
        self.setSlideMid(self.ui.lb3)

    def slideEnter4(self, event):
        self.setSlideMid(self.ui.lb4)

    def slideLeave1(self, event):
        self.setSlideUp(self.ui.lb1)

    def slideLeave2(self, event):
        self.setSlideUp(self.ui.lb2)

    def slideLeave3(self, event):
        self.setSlideUp(self.ui.lb3)

    def slideLeave4(self, event):
        self.setSlideUp(self.ui.lb4)

    def slideBack(self, event):
        self.setSlideDown(self.ui.lb1)
        self.ui.widget1.raise_()
        self.shiftAnime1.start()
        self.selectedWidget = self.ui.widget1

    def slideClicked1(self, event):
        self.setSlideDown(self.ui.lb1)
        if self.selectedWidget != self.ui.widget1:
            self.ui.widget1.raise_()
            self.shiftAnime1.start()
            self.selectedWidget = self.ui.widget1

    def slideClicked2(self, event):
        self.setSlideDown(self.ui.lb2)
        if self.selectedWidget != self.ui.widget2:
            self.ui.widget2.raise_()
            self.shiftAnime2.start()
            self.selectedWidget = self.ui.widget2

    def slideClicked3(self, event):
        self.setSlideDown(self.ui.lb3)
        if self.selectedWidget != self.ui.widget3:
            self.ui.widget3.raise_()
            self.shiftAnime3.start()
            self.selectedWidget = self.ui.widget3

    def jiaoshuiCheck(self, event):
        pixmap = QPixmap()
        pixmap.load("res/ack.png")
        self.ui.lb_jiaoshui.setPixmap(pixmap)
        self.stat["lastWater"] = time.time()
        self.saveStatistics()

    def shifeiCheck(self, event):
        pixmap = QPixmap()
        pixmap.load("res/ack.png")
        self.ui.lb_shifei.setPixmap(pixmap)
        self.stat["lastFertilize"] = time.time()
        self.saveStatistics()


    def slideClicked4(self, event):
        self.setSlideDown(self.ui.lb4)
        if self.selectedWidget != self.ui.widget4:
            self.ui.widget4.raise_()
            self.shiftAnime4.start()
            self.selectedWidget = self.ui.widget4

    def setupWidget1(self):
        #setup the tree
        movie = QMovie()
        movie.setFileName("res/tree.gif")
        self.ui.lb_tree.setMovie(movie)
        self.ui.lb_tree_big.setMovie(movie)
        movie.start()

        #setup the statistics
        self.ui.gridLayout.setHorizontalSpacing(60)
        self.ui.gridLayout.setVerticalSpacing(10)
        self.ui.gridLayout.setGeometry(QRect(0, 51, 291, 224))
        self.ui.gridLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.statLabels = []
        for i in range(7):
            self.statLabels.append([])
            for j in range(4):
                self.statLabels[i].append(QLabel())
                self.statLabels[i][j].setScaledContents(True)
                self.statLabels[i][j].setAutoFillBackground(False)
                self.statLabels[i][j].setAlignment(QtCore.Qt.AlignCenter)
                self.ui.gridLayout.addWidget(self.statLabels[i][j], i, j, 1, 1)

    def setupWidget2(self):
        self.ui.lb_jiaoshui.mousePressEvent = self.jiaoshuiCheck
        self.ui.lb_shifei.mousePressEvent = self.shifeiCheck

    def setupWidget3(self):
        self.ui.check_maze.mousePressEvent = self.mazeCliked
        self.ui.check_paper.mousePressEvent = self.paperCliked
        self.ui.check_pic.mousePressEvent = self.picCliked
        self.ui.check_text.mousePressEvent = self.textClicked
        self.ui.lb_save.mousePressEvent = self.saveSettings

        self.ui.spin_goal.setValue(self.settings["goal"])

        if self.settings["game_type"] == 0:
            self.mazeCliked(None)
        else:
            self.paperCliked(None)

        self.picCliked(None)
        self.picCliked(None)

        self.textClicked(None)
        self.textClicked(None)

    def setupWidget4(self):
        self.achivIcons = [self.ui.lb_a0, self.ui.lb_a1, self.ui.lb_a2,
                           self.ui.lb_a3, self.ui.lb_a4, self.ui.lb_a5]

        for i in range(6):
            self.achivIcons[i].setPixmap(QPixmap("res/" + str(i) * 2))

    def mazeCliked(self, event):
        pixmap = QPixmap()
        pixmap.load("res/checked.png")
        self.ui.check_maze.setPixmap(pixmap)

        pixmap.load("res/unchecked.png")
        self.ui.check_paper.setPixmap(pixmap)

        self.settings["game_type"] = 0

    def paperCliked(self, event):
        pixmap = QPixmap()
        pixmap.load("res/checked.png")
        self.ui.check_paper.setPixmap(pixmap)

        pixmap.load("res/unchecked.png")
        self.ui.check_maze.setPixmap(pixmap)

        self.settings["game_type"] = 1

    def picCliked(self, event):
        pixmap = QPixmap()
        pixmap.load("res/checked.png")
        self.ui.check_pic.setPixmap(pixmap)

        pixmap.load("res/unchecked.png")
        self.ui.check_text.setPixmap(pixmap)

        self.settings["pic_detect"] = 1
        self.settings["text_detect"] = 0


    def textClicked(self, event):
        pixmap = QPixmap()
        pixmap.load("res/checked.png")
        self.ui.check_text.setPixmap(pixmap)

        pixmap.load("res/unchecked.png")
        self.ui.check_pic.setPixmap(pixmap)

        self.settings["pic_detect"] = 1
        self.settings["text_detect"] = 1

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
        self.ui.lb4.enterEvent = self.slideEnter4
        self.ui.lb4.leaveEvent = self.slideLeave4
        self.ui.lb4.mousePressEvent = self.slideClicked4


        self.ui.lb_back2.mousePressEvent = self.slideBack
        self.ui.lb_back3.mousePressEvent = self.slideBack
        self.ui.lb_back4.mousePressEvent = self.slideBack


        for lb in self.sideButtons:
            lb.setStyleSheet(slide_bt_up)
        self.selectedSideButton = self.ui.lb1
        self.slideClicked1(None)

    def connections(self):
        pass

class blueSettings():
    def __init__(self):
        self.data = json.load()

    def reset(self):
        pass

blueapp = BlueApp(sys.argv)
blueapp.app.exec()
