import subprocess, time, sys, os, tool
from threading import Thread, Lock
import design.Design as Design
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QApplication
from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool

Speed = ["ultrafast","superfast","veryfast","faster","fast","medium","slow","slower","veryslow"]
Tune = ["film","animation","grain","stillimage","fastdecode","zerolatency"]

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
    
    args = [                             #Command line formation
        "ffmpeg\\bin\\ffmpeg.exe",
        "-i", "", 
        "-c:v", "",
        "-tune", "",
        "-preset", "",
        "-crf", "",
        ""
    ]
    try:args[2] = Screen.CurrentVideo[0].replace("/","\\") # Get path of selected input video
    except AttributeError: # If user not selected input video
        Screen.ErrorNoFileSelected()
        return
    if Screen.ui.radioButton.isChecked(): args[4] = "libx264" # If user choose "Default" codec
    else: args[4] = "libx265"                                 # If user choose HEVC
    args[6] = Tune[Screen.ui.comboBox_2.currentIndex()]       # Insert tune in command line
    args[8] = Speed[Screen.ui.comboBox.currentIndex()]        # Insert speed preset in command line
    args[10] = str(Screen.ui.spinBox.value())                 # Insert quality level in command line
    args[11] = Screen.Save_File()[0].replace("/","\\")        # Open Save As window
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
            Screen.ui.statusbar.showMessage(f"Converted {Screen.CurrentVideo[0]}. Conversion took: {str(TimePass)} seconds")
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
        

class MainWindow(QtWidgets.QMainWindow): #Main Window
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Design.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(ConvertPrep) # "Convert" button clicked
        self.ui.actionNew.triggered.connect(self.OpenFile) # "Open" menu button clicked
        self.threadpool = QThreadPool() #Create Thread pool
    def EndConversionDialog(self, t): #End Conversion Dialog
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
        self.SaveFile = QFileDialog.getSaveFileName(self, "Save File As",os.path.dirname(os.path.realpath(__file__)), "Video Files (*.mp4 *.mov *.mkv)")
        return self.SaveFile
    def OpenFile(self):  self.CurrentVideo = QFileDialog.getOpenFileName(self, "Open File",os.path.dirname(os.path.realpath(__file__)), "Video Files (*.mp4 *.mov *.mkv)")
       
    def ErrorNoFileSelected(self): 
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
        msgBox = QMessageBox()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Vid.ico"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        msgBox.setWindowIcon(icon)
        msgBox.setIcon(QMessageBox.Icon.Critical)
        msgBox.setText("Error! You must select destination and name of output video to conversion!")
        msgBox.setWindowTitle("Error! No Save Destination Selected!")
        msgBox.setStandardButtons(QMessageBox.StandardButton.Cancel)
        msgBox.exec()

    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Screen = MainWindow()
    Screen.show()
    sys.exit(app.exec())