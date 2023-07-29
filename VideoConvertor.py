import subprocess, time, sys, os, tool, json, configparser
from threading import Thread, Lock
from PyQt6 import QtWidgets, QtCore, QtGui, uic
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QApplication
from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool


def LoadCfg():
    global Config, THREADS, HOME_FOLDER, SAVE_FOLDER, LANGUAGE, Speed, Tune, Codec, Langs, config
    Config = configparser.ConfigParser()
    Config.read("Settings.ini")

    THREADS = Config["PERFORMANCE"].getint("THREADS", os.cpu_count())
    HOME_FOLDER = Config["OTHER"].get("HOME_FOLDER", os.path.dirname(os.path.realpath(__file__)))
    SAVE_FOLDER = Config["OTHER"].get("SAVE_FOLDER", os.path.dirname(os.path.realpath(__file__)))
    LANGUAGE = Config["OTHER"].get("LANGUAGE", "EN")

    with open("config.json") as f:
        config = json.load(f)
    Speed = config["Presets"]
    Tune = config["Tune"]
    Codec = config["Codecs"]
    Langs = config["Langs"]

LoadCfg()

# monkey-patch/replace Popen
subprocess.Popen = tool.new_Popen

#Delay which not freezing program
def Delay(sec : int):
    for i in range(0, sec*10, 1):
        QApplication.processEvents()
        time.sleep(0.1)

#Main Conversion Function
def ConvertPrep():
    global args, done
    LoadCfg()
    args = [                             #Command line formation
        "ffmpeg\\bin\\ffmpeg.exe",
        "-i", "", 
        "-c:v", "",
        "-tune", "",
        "-preset", "",
        "-crf", "",
        "-threads", "",
        ""
    ]
    try:args[2] = Screen.CurrentVideo[0].replace("/","\\") # Get path of selected input video
    except AttributeError: # If user not selected input video
        Screen.ErrorNoFileSelected()
        return
    if Screen.ui.radioButton.isChecked(): args[4] = Codec[0]  # If user choose "Default" codec
    else: args[4] = Codec[1]                                  # If user choose HEVC
    args[6] = Tune[Screen.comboBox_2.currentIndex()]       # Insert tune in command line
    args[8] = Speed[Screen.comboBox.currentIndex()]        # Insert speed preset in command line
    args[10] = str(Screen.spinBox.value())                 # Insert quality level in command line
    args[12] = str(24)
    args[13] = Screen.Save_File()[0].replace("/","\\")        # Open Save As window
    if args[11].replace(" ", "") == "":                       # If user didn't choose destination
        Screen.ErrorNoSave()
        return

    #Start conversion process
    Screen.setDisabled(True)    # Disable all widgets on main window
    done = False
    thread = Converter(args)
    Screen.threadpool.start(thread) # Start ffmpeg thread
    TimePass = 0
    while True: # Loop checking 
        if not done: Screen.ui.statusbar.showMessage(f"Converting {Screen.CurrentVideo[0]}. Passed seconds: {str(TimePass)}")  # If conversion proceeding
        else:                                                                                                                  # If conversion ended
            Screen.statusbar.showMessage(f"Converted {Screen.CurrentVideo[0]}. Conversion took: {str(TimePass)} seconds")
            Screen.EndConversionDialog(TimePass)
            break
        Delay(1)
        TimePass +=1

class Converter(QRunnable): # FFMpeg Thread
    def __init__(self, args):
        super(Converter, self).__init__()
        self.args = args

    @pyqtSlot()
    def run(self):
        global done
        p = subprocess.Popen(args=args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) # Start FFMpeg
        p.wait()
        done = True

class Settings(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()        
        uic.loadUi("design\\Settings.ui", self)
        self.UpdateValues()
        self.pushButton_2.clicked.connect(self.Apply)
        self.pushButton.clicked.connect(self.close)
        self.pushButton_3.clicked.connect(self.close)
        self.trans = QtCore.QTranslator(self)
        self.ChangeLanguage(LANGUAGE)
        self.retranslateUi(self)
        self.toolButton.clicked.connect(lambda e: self.ui.lineEdit.setText(self.choose1()))
        self.toolButton_2.clicked.connect(lambda e: self.ui.lineEdit_2.setText(self.choose2()))

    def Apply(self):
        if LANGUAGE != Langs[self.comboBox.currentIndex()]:
            MainWindow.ChangeLanguage(Screen, Langs[self.comboBox.currentIndex()])
            self.ChangeLanguage(Langs[self.comboBox.currentIndex()])

        Config["PERFORMANCE"]["THREADS"] = str(self.horizontalSlider.value())
        Config["OTHER"]["HOME_FOLDER"] = self.lineEdit.text()
        Config["OTHER"]["SAVE_FOLDER"] = self.lineEdit_2.text()
        Config["OTHER"]["LANGUAGE"] = Langs[self.comboBox.currentIndex()]
        with open("Settings.ini", "w") as configfile:
            Config.write(configfile)
        self.close()
    
    def UpdateValues(self):
        Config = configparser.ConfigParser()
        Config.read(".\\Settings.ini")

        THREADS = Config["PERFORMANCE"].getint("THREADS", os.cpu_count())
        HOME_FOLDER = Config["OTHER"].get("HOME_FOLDER", os.path.dirname(os.path.realpath(__file__)).replace("\\", "/"))
        SAVE_FOLDER = Config["OTHER"].get("SAVE_FOLDER", os.path.dirname(os.path.realpath(__file__)).replace("\\", "/"))
        LANGUAGE = Config["OTHER"].get("LANGUAGE", "EN")
        if LANGUAGE == "EN":
            LANGUAGE = 0
        elif LANGUAGE == "UA":
            LANGUAGE = 1

        self.horizontalSlider.setValue(int(THREADS))
        self.lineEdit.setText(HOME_FOLDER)
        self.lineEdit_2.setText(SAVE_FOLDER)
        self.comboBox.setCurrentIndex(LANGUAGE)

    def ChangeLanguage(self, lang):
        if lang == "UA":
            self.trans.load(config["Localization"]["UA"])
            QtWidgets.QApplication.instance().installTranslator(self.trans)
        else: QtWidgets.QApplication.instance().removeTranslator(self.trans)
        self.retranslateUi(self)
    
    def choose1(self): return QFileDialog.getExistingDirectory(self, "Open Default Video Directory",HOME_FOLDER)
    def choose2(self): return QFileDialog.getExistingDirectory(self, "Open Default Save Directory",SAVE_FOLDER)
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "Performance"))
        self.label.setToolTip(_translate("Form", "<html><head/><body><p>Count of CPUs used for conversion</p></body></html>"))
        self.label.setText(_translate("Form", "CPU count"))
        self.groupBox_2.setTitle(_translate("Form", "Other"))
        self.label_2.setToolTip(_translate("Form", "<html><head/><body><p>Language of programm </p></body></html>"))
        self.label_2.setText(_translate("Form", "Language"))
        self.comboBox.setItemText(0, _translate("Form", "English"))
        self.comboBox.setItemText(1, _translate("Form", "Ukrainian"))
        self.toolButton.setToolTip(_translate("Form", "<html><head/><body><p>Browse</p></body></html>"))
        self.toolButton.setText(_translate("Form", "..."))
        self.label_3.setToolTip(_translate("Form", "<html><head/><body><p>Default path of videos </p></body></html>"))
        self.label_3.setText(_translate("Form", "Input Video Folder"))
        self.label_4.setToolTip(_translate("Form", "<html><head/><body><p>Default path to save converted video</p></body></html>"))
        self.label_4.setText(_translate("Form", "Output Video Folder"))
        self.toolButton_2.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:12pt;\">Browse</span></p></body></html>"))
        self.toolButton_2.setText(_translate("Form", "..."))
        self.pushButton.setText(_translate("Form", "Cancel"))
        self.pushButton_2.setToolTip(_translate("Form", "<html><head/><body><p>Apply changes</p></body></html>"))
        self.pushButton_2.setText(_translate("Form", "Apply"))
        self.pushButton_3.setText(_translate("Form", "Ok"))

    

class MainWindow(QtWidgets.QMainWindow): #Main Window
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi("design\\MainWindow.ui", self)
        self.pushButton.clicked.connect(ConvertPrep) # "Convert" button clicked
        self.actionOpen.triggered.connect(self.OpenFile) # "Open" menu button clicked
        self.threadpool = QThreadPool() #Create Thread pool
        self.actionSettings.triggered.connect(self.ShowSettings)        
        self.trans = QtCore.QTranslator(self)
        self.ChangeLanguage(LANGUAGE)
        self.retranslateUi(self)
    def ShowSettings(self):
        LoadCfg()
        self.settings = Settings()
        self.settings.show()

    def EndConversionDialog(self, t): #End Conversion Dialog
        LoadCfg()
        Screen.setDisabled(False)
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Icon.Information)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Vid.ico"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        msgBox.setWindowIcon(icon)
        msgBox.setText(f"File {self.CurrentVideo[0]} was converted successfully!\nThe conversion took {t} seconds\nDo you want to open output folder?")
        msgBox.setWindowTitle("Conversion ended")
        msgBox.setStandardButtons(QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Open)
        button = hex(msgBox.exec())
        f = self.SaveFile[0].replace("/", "\\").split("\\")
        f.pop()
        if button == "0x2000":
            os.system('explorer "{0}"'.format('\\'.join(f))) #Open Explorer where video saved
    def Save_File(self):
        LoadCfg() 
        self.SaveFile = QFileDialog.getSaveFileName(self, "Save File As",SAVE_FOLDER, "Video Files (*.mp4 *.mov *.mkv)")
        return self.SaveFile
    def OpenFile(self):
        LoadCfg()  
        self.CurrentVideo = QFileDialog.getOpenFileName(self, "Open File",HOME_FOLDER, "Video Files (*.mp4 *.mov *.mkv)")

    def ChangeLanguage(self, lang):
        self.retranslateUi(self)
        print(lang)
        if lang == "UA":
            self.trans.load(config["Localization"]["UA"])
            QtWidgets.QApplication.instance().installTranslator(self.trans)
        else: QtWidgets.QApplication.instance().removeTranslator(self.trans)  
        self.retranslateUi(self)

    def ErrorNoFileSelected(self):
        LoadCfg() 
        msgBox = QMessageBox()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Vid.ico"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        msgBox.setWindowIcon(icon)
        msgBox.setIcon(QMessageBox.Icon.Critical)
        msgBox.setText("Error! You don't selected any video to convert!")
        msgBox.setWindowTitle("Error! No Video Selected!")
        msgBox.setStandardButtons(QMessageBox.StandardButton.Cancel)
        msgBox.exec()

    def ErrorNoSave(self):
        LoadCfg() 
        msgBox = QMessageBox()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Vid.ico"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        msgBox.setWindowIcon(icon)
        msgBox.setIcon(QMessageBox.Icon.Critical)
        msgBox.setText("Dialog","Error! You must select destination and name of output video to conversion!")
        msgBox.setWindowTitle("Error! No Save Destination Selected!")
        msgBox.setStandardButtons(QMessageBox.StandardButton.Cancel)
        msgBox.exec()
    
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtCore.QCoreApplication.translate("MainWindow", "Ultimate Video Converter"))
        self.groupBox_2.setTitle(QtCore.QCoreApplication.translate("MainWindow", "Video Quality"))
        self.spinBox.setToolTip(QtCore.QCoreApplication.translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">From 0 to 51. </span></p><p><span style=\" font-size:10pt;\">(0 - best quality, 51 - the worst quality)</span></p></body></html>"))
        self.label.setText(QtCore.QCoreApplication.translate("MainWindow", "Ultimate Video Converter"))
        self.pushButton.setToolTip(QtCore.QCoreApplication.translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">Start Video Conversion</span></p></body></html>"))
        self.pushButton.setText(QtCore.QCoreApplication.translate("MainWindow", "Convert"))
        self.groupBox_4.setTitle(QtCore.QCoreApplication.translate("MainWindow", "Conversion Speed"))
        self.comboBox.setToolTip(QtCore.QCoreApplication.translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">The slower the conversion </span></p><p><span style=\" font-size:10pt;\">the better the quality</span></p></body></html>"))
        self.comboBox.setPlaceholderText(QtCore.QCoreApplication.translate("MainWindow", "None"))
        self.comboBox.setItemText(0, QtCore.QCoreApplication.translate("MainWindow", "Ultra Fast"))
        self.comboBox.setItemText(1, QtCore.QCoreApplication.translate("MainWindow", "Super Fast"))
        self.comboBox.setItemText(2, QtCore.QCoreApplication.translate("MainWindow", "Very Fast"))
        self.comboBox.setItemText(3, QtCore.QCoreApplication.translate("MainWindow", "Faster"))
        self.comboBox.setItemText(4, QtCore.QCoreApplication.translate("MainWindow", "Fast"))
        self.comboBox.setItemText(5, QtCore.QCoreApplication.translate("MainWindow", "Medium"))
        self.comboBox.setItemText(6, QtCore.QCoreApplication.translate("MainWindow", "Slow"))
        self.comboBox.setItemText(7, QtCore.QCoreApplication.translate("MainWindow", "Slower"))
        self.comboBox.setItemText(8, QtCore.QCoreApplication.translate("MainWindow", "Very Slow"))
        self.groupBox_3.setTitle(QtCore.QCoreApplication.translate("MainWindow", "Video Tune"))
        self.comboBox_2.setToolTip(QtCore.QCoreApplication.translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">Choose Video Tune</span></p></body></html>"))
        self.comboBox_2.setPlaceholderText(QtCore.QCoreApplication.translate("MainWindow", "None"))
        self.comboBox_2.setItemText(0, QtCore.QCoreApplication.translate("MainWindow", "Film"))
        self.comboBox_2.setItemText(1, QtCore.QCoreApplication.translate("MainWindow", "Animation"))
        self.comboBox_2.setItemText(2, QtCore.QCoreApplication.translate("MainWindow", "Grain"))
        self.comboBox_2.setItemText(3, QtCore.QCoreApplication.translate("MainWindow", "Still image"))
        self.comboBox_2.setItemText(4, QtCore.QCoreApplication.translate("MainWindow", "Fast decode"))
        self.comboBox_2.setItemText(5, QtCore.QCoreApplication.translate("MainWindow", "Zero Latency"))
        self.groupBox.setTitle(QtCore.QCoreApplication.translate("MainWindow", "Encoding Codec"))
        self.radioButton.setToolTip(QtCore.QCoreApplication.translate("MainWindow", "<html><head/><body><p>H264</p></body></html>"))
        self.radioButton.setText(QtCore.QCoreApplication.translate("MainWindow", "Default"))
        self.radioButton_2.setToolTip(QtCore.QCoreApplication.translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">H265</span></p></body></html>"))
        self.radioButton_2.setText(QtCore.QCoreApplication.translate("MainWindow", "HEVC"))
        self.menuChoose_file.setTitle(QtCore.QCoreApplication.translate("MainWindow", "File"))
        self.menuSettings.setTitle(QtCore.QCoreApplication.translate("MainWindow", "Settings"))
        self.menuHelp.setTitle(QtCore.QCoreApplication.translate("MainWindow", "Help"))
        self.actionOpen.setText(QtCore.QCoreApplication.translate("MainWindow", "Open"))
        self.actionOpen.setToolTip(QtCore.QCoreApplication.translate("MainWindow", "Load new file "))
        self.actionHelp.setText(QtCore.QCoreApplication.translate("MainWindow", "Help"))
        self.actionSettings.setText(QtCore.QCoreApplication.translate("MainWindow", "Settings"))

    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Screen = MainWindow()
    Screen.show()
    sys.exit(app.exec())
    