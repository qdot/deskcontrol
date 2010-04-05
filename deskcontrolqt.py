#!/usr/bin/python
import sys
from PyQt4 import QtCore, QtGui
from ravespider import *
from ambx import *
from TrettioLight import *
from ui_SingleLightControlWidget import *
from ui_RGBLightControlWidget import *
from ui_DeskControlWidget import *
from ui_ambxControlWidget import *
import time

#########################################################################

class SingleLightControlWidget(QtGui.QWidget, Ui_SingleLightControlWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self) 
        self.setupUi(self)
        self.index = -1
        self.indexSpeed = QtCore.pyqtSignal(int, int)
        self.connect(self.lightLevel, QtCore.SIGNAL("valueChanged(int)"),
                     self, QtCore.SLOT("emitIndexedSpeedSignal(int)"))

    @QtCore.pyqtSlot(int)
    def emitIndexedSpeedSignal(self, val):
        self.emit(QtCore.SIGNAL("indexSpeed(int, int)"), self.index, val)

#########################################################################

class RGBLightControlWidget(QtGui.QWidget, Ui_RGBLightControlWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self) 
        self.setupUi(self)
        self.index = -1
        self.indexRGBSpeed = QtCore.pyqtSignal(int, int, int, int)
        self.connect(self.redLightLevel, QtCore.SIGNAL("valueChanged(int)"),
                     self, QtCore.SLOT("emitIndexedRGBSpeedSignal(int)"))
        self.connect(self.greenLightLevel, QtCore.SIGNAL("valueChanged(int)"),
                     self, QtCore.SLOT("emitIndexedRGBSpeedSignal(int)"))
        self.connect(self.blueLightLevel, QtCore.SIGNAL("valueChanged(int)"),
                     self, QtCore.SLOT("emitIndexedRGBSpeedSignal(int)"))

    @QtCore.pyqtSlot(int)
    def emitIndexedRGBSpeedSignal(self, val):
        self.emit(QtCore.SIGNAL("indexRGBSpeed(int, int, int, int)"), self.index, self.redLightLevel.value(), self.greenLightLevel.value(), self.blueLightLevel.value())

#########################################################################

class RaveSpiderControlWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self) 
        self.setupUi()
        self.spiderDevice = RaveSpider()
        self.spiderDevice.open()
    
    def setupUi(self):
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)        
        self.controlWidget = SingleLightControlWidget()
        self.controlWidget.lightGroupBox.setTitle("Rave Spider")
        self.layout.addWidget(self.controlWidget)
        self.connect(self.controlWidget.lightLevel, QtCore.SIGNAL("valueChanged(int)"),
                     self, QtCore.SLOT("setSpeed(int)"))

    @QtCore.pyqtSlot(int)
    def setSpeed(self, val):
        self.spiderDevice.setSpeed(val)

class DeskLightControlWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self) 
        self.setupUi()
        self.desktopDevice = FTDIDeskLight()
        self.desktopDevice.open()

    def setupUi(self):
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.controlWidget = []
        for i in range(0, 6):
            wid = SingleLightControlWidget()
            wid.index = i
            wid.lightGroupBox.setTitle("Light %d" % (i))
            self.controlWidget.append(wid)
            self.layout.addWidget(wid)
            self.connect(wid, QtCore.SIGNAL("indexSpeed(int, int)"),
                         self, QtCore.SLOT("setSpeed(int, int)"))


    @QtCore.pyqtSlot(int, int)
    def setSpeed(self, index, val):
        self.desktopDevice.setSpeed(index,val)


class amBXControlWidget(QtGui.QWidget, Ui_ambxControlWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self) 
        self.deviceNames = ["Left Speaker Light", "Right Speaker Light", "Left WW Light", "Middle WW Light", "Right WW Light", "Left Fan", "Right Fan", "Rumble Bar"]
        self.setupUi(self)
        self.rgbControlWidgets = []
        self.fanControlWidgets = []
        for i in range(0, 2):
            self.addRGBLight(i, self.speakerLayout)
        for i in range(2, 5):
            self.addRGBLight(i, self.wwLayout)
        for i in range(5, 8):
            fanControlWidget = SingleLightControlWidget()
            fanControlWidget.index = i
            fanControlWidget.lightGroupBox.setTitle(self.deviceNames[i])
            self.fanControlWidgets.append(fanControlWidget)
            self.fanLayout.addWidget(fanControlWidget)
            if i is not 7:
                self.connect(fanControlWidget, QtCore.SIGNAL("indexSpeed(int, int)"),
                             self, QtCore.SLOT("setFanSpeed(int, int)"))
            else:
                self.connect(fanControlWidget, QtCore.SIGNAL("indexSpeed(int, int)"),
                             self, QtCore.SLOT("setRumbleSpeed(int, int)"))
        self.ambxDevice = ambx()
        if self.ambxDevice.open() is False:
            print "No ambx device connected"
            return

    def addRGBLight(self, index, layout):
        rgbControlWidget = RGBLightControlWidget()
        rgbControlWidget.index = index
        rgbControlWidget.lightGroupBox.setTitle(self.deviceNames[index])
        self.rgbControlWidgets.append(rgbControlWidget)
        layout.addWidget(rgbControlWidget)
        self.connect(rgbControlWidget, QtCore.SIGNAL("indexRGBSpeed(int, int, int, int)"),
                     self, QtCore.SLOT("setRGBSpeed(int, int, int, int)"))        

    @QtCore.pyqtSlot(int, int)
    def setRumbleSpeed(self, index, val):
        self.ambxDevice.setFanSpeed((index << 4 | 0x0B), val)

    @QtCore.pyqtSlot(int, int)
    def setFanSpeed(self, index, val):
        self.ambxDevice.setFanSpeed((index << 4 | 0x0B), val)

    @QtCore.pyqtSlot(int, int, int, int)
    def setRGBSpeed(self, index, r, g, b):
        self.ambxDevice.setLightColor((index << 4 | 0x0B), [r, g, b])


class DeskControlDialog(QtGui.QDialog, Ui_DeskControlWidget):
    def __init__(self):
        QtGui.QDialog.__init__(self) 
        self.setupUi(self)
        # self.spiderWidget = RaveSpiderControlWidget()
        #self.deskTabLayout.addWidget(self.spiderWidget)
        self.deskWidget = DeskLightControlWidget()
        self.deskTabLayout.addWidget(self.deskWidget)
        self.ambxWidget = amBXControlWidget()
        self.ambxTabLayout.addWidget(self.ambxWidget)

def main(argv=None):
    app = QtGui.QApplication(sys.argv)

    control = DeskControlDialog()
    control.show()
    control.activateWindow()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
