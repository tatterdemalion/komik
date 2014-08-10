#!/usr/bin/python
import sys
import zipfile

from PySide import QtCore, QtGui

from mainwindow import Ui_MainWindow


class ThumbnailWorker(QtCore.QThread):
    thumbnailSignal = QtCore.Signal(dict)

    def __init__(self, cbr=None):
        QtCore.QThread.__init__(self)
        self.cbr = cbr

    def getImageByName(self, name):
        with self.cbr.open(name, 'r') as f:
            image = QtGui.QImage()
            image.loadFromData(f.read())
            return image

    def run(self):
        for row, page in enumerate(self.cbr.namelist()):
            self.thumbnailSignal.emit({'row': row,
                                       'image': self.getImageByName(page)})


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionOpen.triggered.connect(self.openComicFile)
        #self.ui.actionZoom_In.triggered.connect(self.zoomIn)
        #self.ui.actionZoom_Out.triggered.connect(self.zoomOut)
        #self.ui.actionFit_to_Window.triggered.connect(self.fitToWindow)
        self.ui.pagesList.currentItemChanged.connect(self.displayPage)

        self.openComicFile()

    def setThumbnail(self, image_dict):
        pixmap = QtGui.QPixmap.fromImage(image_dict['image'])
        item = self.ui.pagesList.item(image_dict['row'])
        item.setIcon(pixmap)
        item.setText('')

    def getPixmapByName(self, name):
        with self.cbr.open(name, 'r') as f:
            image = QtGui.QImage()
            image.loadFromData(f.read())
        if image.isNull():
            QtGui.QMessageBox.information(
                self, "Image Viewer", "Cannot load %s." % name)
            return
        return QtGui.QPixmap.fromImage(image)

    def openComicFile(self):
        filename = QtGui.QFileDialog.getOpenFileName(
            self, "Open File", QtCore.QDir.currentPath())
        if filename:
            filename = filename[0]
            self.cbr = zipfile.ZipFile(filename, 'r')
            self.worker = ThumbnailWorker(cbr=self.cbr)
            self.worker.thumbnailSignal.connect(self.setThumbnail)

            for page in self.cbr.namelist():
                #image = self.getPixmapByName(page)
                item = QtGui.QListWidgetItem()
                #item.setIcon(QtGui.QIcon(image))
                item.setText(page)
                item.setData(QtCore.Qt.UserRole, page)
                self.ui.pagesList.addItem(item)
        self.ui.pagesList.setCurrentRow(0)
        self.displayPage()
        self.worker.start()

    def displayPage(self):
        item = self.ui.pagesList.currentItem()
        filename = item.data(QtCore.Qt.UserRole)
        image = self.getPixmapByName(filename)
        self.ui.pageView.setPixmap(image)
        self.scaleFactor = 1.0
        self.ui.pageView.adjustSize()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
