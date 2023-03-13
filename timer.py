import os, sys, pathlib

from PyQt5.QtCore import Qt, QTimer, QSize, QSettings, QRect
from PyQt5.QtGui import QFont, QFontDatabase, QPainter, QColor, QIcon, QFontDatabase
from PyQt5.QtWidgets import QSizeGrip, QInputDialog, QLineEdit, QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect, QGraphicsColorizeEffect

FIXED_FONT = "Chivo Mono"

# Logic for resizing transparent window obtained from: https://stackoverflow.com/a/62812752
# Licensed [CC BY-SA 4.0] - https://creativecommons.org/licenses/by-sa/4.0/
class SideGrip(QWidget):
	def __init__(self, parent, edge):
		QWidget.__init__(self, parent)
		if edge == Qt.LeftEdge:
			self.setCursor(Qt.SizeHorCursor)
			self.resizeFunc = self.resizeLeft
		elif edge == Qt.TopEdge:
			self.setCursor(Qt.SizeVerCursor)
			self.resizeFunc = self.resizeTop
		elif edge == Qt.RightEdge:
			self.setCursor(Qt.SizeHorCursor)
			self.resizeFunc = self.resizeRight
		else:
			self.setCursor(Qt.SizeVerCursor)
			self.resizeFunc = self.resizeBottom
		self.mousePos = None

	def resizeLeft(self, delta):
		window = self.window()
		width = max(window.minimumWidth(), window.width() - delta.x())
		geo = window.geometry()
		geo.setLeft(geo.right() - width)
		window.setGeometry(geo)

	def resizeTop(self, delta):
		window = self.window()
		height = max(window.minimumHeight(), window.height() - delta.y())
		geo = window.geometry()
		geo.setTop(geo.bottom() - height)
		window.setGeometry(geo)

	def resizeRight(self, delta):
		window = self.window()
		width = max(window.minimumWidth(), window.width() + delta.x())
		window.resize(width, window.height())

	def resizeBottom(self, delta):
		window = self.window()
		height = max(window.minimumHeight(), window.height() + delta.y())
		window.resize(window.width(), height)

	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.mousePos = event.pos()

	def mouseMoveEvent(self, event):
		if self.mousePos is not None:
			delta = event.pos() - self.mousePos
			self.resizeFunc(delta)

	def mouseReleaseEvent(self, event):
		self.mousePos = None

class closeBtn(QPushButton):
	def __init__(self, *args):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.setStyleSheet("""
			QPushButton {
				background: rgba(0, 0, 0, 0);
				color: rgba(255, 255, 255, .1);
			}
			QPushButton:hover {
				background: rgba(255, 0, 0, 0);
				color: rgba(255, 255, 255, .6);
			}
		""")
		self.setFont(QFont(FIXED_FONT, 12))
		self.setFixedHeight(16)
		self.setFixedWidth(14)
		self.setText("x")

	def mousePressEvent(self, QMouseEvent):
		if QMouseEvent.button() == Qt.LeftButton:
			app.exit()
		elif QMouseEvent.button() == Qt.RightButton:
			self.parent().move(-3, 60)

class RefreshLoop(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def strToSeconds(self, string):
		arr = []
		if ":" in string:
			tmpArr = string.split(":")
			for el in tmpArr:
				intEl = 0
				try:
					intEl = int(el)
				except:
					# print("Invalid string to convert to time: " + str(el))
					pass
				arr.append(intEl)
		else:
			intEl = 0
			try:
				intEl = int(string)
			except:
				# print("Invalid string to convert to time: " + str(string))
				pass
			arr.append(intEl)

		fullTime = 0

		arr.reverse()
		if len(arr) < 4:
			try:
				fullTime += arr[0]
				fullTime += arr[1] * 60
				fullTime += arr[2] * 60 * 60
			except:
				pass

		return fullTime

	def initUI(self):
		self.setFixedSize(0, 0)

		self.counter = 0
		self.active = False
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.timerExpired)
		self.timer.start(1000)

		self.count = 0

		self.settings = QSettings("timer_length")
		# print(self.settings.value("timer_length"))

		try:
			self.timer_length = int(self.strToSeconds(str(self.settings.value("timer_length"))))
		except Exception as e:
			# print(e)
			self.timer_length = 0

		# print("self.timer_length: " + str(self.timer_length))

	def setActive(self, toggle):
		self.active = toggle
		self.counter = 0

		global clicked
		clicked = False

	def setTimeLabel(self, timeLabel):
		self.timeLabel = timeLabel
		self.timeLabel.setTimeLabel(int(self.timer_length) * -1, 0, self.active)
		# self.timeLabel.setTimeLabel(int(self.timer_length), 0)

	def resetTimer(self):
		self.counter = 0
		self.timeLabel.setTimeLabel(self.timer_length, 0, self.active)

	def setTimerLength(self, newTime):
		try:
			self.settings.setValue("timer_length", str(newTime))
			print(str(self.settings.value("timer_length")))

			self.timer_length = int(self.strToSeconds(str(self.settings.value("timer_length"))))

			self.timeLabel.setTimeLabel(int(self.timer_length) * -1, 0, self.active)

			self.resetTimer()
		except Exception as e:
			# print(e)
			self.timer_length = 0
			# print("Invalid time entered.")

	def timerExpired(self):
		global clicked
		if self.timer_length:
			try:
				if self.active:
					self.counter = self.counter + 1
					if self.counter > int(self.timer_length):
						if clicked:
							self.counter = 0
							self.timeLabel.setTimeLabel(self.timer_length, 0, self.active)
							clicked = False
					else:
						clicked = False

					self.timeLabel.setTimeLabel(self.timer_length, self.counter, self.active)
			except:
				pass

class TimeLabel(QLabel):
	def __init__(self):
		super().__init__()
		self.initUI()

	def seconds_to_timestamp(self, seconds):
		def zeropad(string):
			string = str(string)
			if len(string) < 2:
				return "0" + string
			else:
				return string

		if seconds > 59:
			return "{}:{}".format(zeropad(int(seconds / 60)), zeropad(seconds % 60))
		elif seconds < 0:
			seconds = seconds * -1
			return "-{}:{}".format(zeropad(int(seconds / 60)), zeropad(seconds % 60))
		else:
			return "00:{}".format(zeropad(seconds))

	def initUI(self):
		self.setFont(QFont(FIXED_FONT, 35))
		self.setStyleSheet("color: white;")
		self.setAlignment(Qt.AlignCenter)
		self.setFixedHeight(40)

		self.expiredTimer = QTimer(self)
		self.expiredTimer.timeout.connect(self.setTimerExpiredTheme)

		self.currentThemeIndex = True

	def setTimeLabel(self, maxLength, newTime, isActive):
		currentTime = int(maxLength) - int(newTime)
		self.setText(self.seconds_to_timestamp(currentTime))

		if currentTime < 0 and isActive:
			if not self.expiredTimer.isActive():
				self.expiredTimer.start(500)
		else:
			self.clearTimerExpiredTheme()
			if self.expiredTimer.isActive():
				self.expiredTimer.stop()

	def setTimerExpiredTheme(self):
		self.currentThemeIndex = not self.currentThemeIndex
		if self.currentThemeIndex:
			self.setStyleSheet("color: white;")

			op = QGraphicsColorizeEffect()
			op.setColor(QColor(89, 6, 0))

			# try:
			self.parent().parent().setGraphicsEffect(op)
			# except Exception as e:
			# 	pass
		else:
			self.setStyleSheet("color: red;")

			op = QGraphicsColorizeEffect()
			# try:
			self.parent().parent().setGraphicsEffect(None)
			# except Exception as e:
			# 	pass

	def clearTimerExpiredTheme(self):
		self.setStyleSheet("color: white;")
		# try:
		self.parent().parent().setGraphicsEffect(None)
		# except Exception as e:
		# 	pass

class RefreshButton(QPushButton):
	def __init__(self, controller):
		super().__init__()
		self.initUI(controller)

	def initUI(self, controller):
		self.setStyleSheet("""
			QPushButton {
				background: rgba(0, 0, 0, 0);
				color: rgba(255, 255, 255, .8);
			}
			QPushButton:hover {
				background: rgba(0, 0, 0, 0.4);
				color: rgba(255, 255, 255, 1);
			}
		""")

		self.setIcon(QIcon(resource_path('refresh.png')))
		self.setIconSize(QSize(15, 15))
		self.setFixedSize(20, 20)
		op = QGraphicsColorizeEffect()
		op.setColor(QColor(89, 6, 0))
		self.setGraphicsEffect(op)
		self.setToolTip('Toggle timer.')

		self.refreshLoopController = controller
		self.refreshLoopbtnActive = False

	def mousePressEvent(self, QMouseEvent):
		if QMouseEvent.button() == Qt.LeftButton:
			if self.refreshLoopbtnActive:
				self.refreshLoopbtnActive = False
				op = QGraphicsColorizeEffect()
				op.setColor(QColor(89, 6, 0))
				self.setGraphicsEffect(op)
				self.refreshLoopController.setActive(False)
			else:
				self.refreshLoopbtnActive = True
				op = QGraphicsColorizeEffect()
				op.setColor(QColor(0, 105, 17))
				self.setGraphicsEffect(op)
				self.setGraphicsEffect(op)
				self.refreshLoopController.setActive(True)
		elif QMouseEvent.button() == Qt.RightButton:
			self.refreshLoopController.resetTimer()

class BgLayer(QWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self.initUI()

	def initUI(self):
		self.alwaysOnTopBtnActive = False

		timelabel = TimeLabel()
		timelabel.setParent(self)

		refreshLoopController = RefreshLoop()
		refreshLoopController.setTimeLabel(timelabel)
		self.refreshLoopController = refreshLoopController

		refreshLoopbtn = RefreshButton(refreshLoopController)
		self.refreshLoopbtn = refreshLoopbtn

		alwaysOnTopbtn = QPushButton()
		alwaysOnTopbtn.setIcon(QIcon(resource_path('eye.png')))
		self.alwaysOnTopbtn = alwaysOnTopbtn
		alwaysOnTopbtn.setStyleSheet("""
			QPushButton {
				background: rgba(0, 0, 0, 0);
				color: rgba(200, 200, 200, .2);
			}
			QPushButton:hover {
				background: rgba(0, 0, 0, 0.4);
				color: rgba(255, 255, 255, .6);
			}
		""")

		alwaysOnTopbtn.setIcon(QIcon(resource_path('eye.png')))
		op = QGraphicsOpacityEffect()
		op.setOpacity(0.4)
		alwaysOnTopbtn.setGraphicsEffect(op)
		alwaysOnTopbtn.setIconSize(QSize(20, 20))
		alwaysOnTopbtn.setFixedSize(20, 20)
		btnOverlay1 = QGraphicsColorizeEffect()
		btnOverlay1.setColor(QColor(120, 120, 120))
		alwaysOnTopbtn.setGraphicsEffect(btnOverlay1)
		alwaysOnTopbtn.setToolTip('Toggle Always on Top.')
		alwaysOnTopbtn.clicked.connect(self.alwaysOnTopButtonClicked)

		settingsbtn = QPushButton()
		settingsbtn.setStyleSheet("""
			QPushButton {
				background: rgba(0, 0, 0, 0);
				color: rgba(255, 255, 255, .9);
			}
			QPushButton:hover {
				background: rgba(0, 0, 0, 0.4);
				color: rgba(255, 255, 255, 1);
			}
		""")
		settingsbtn.setIcon(QIcon(resource_path('gear.png')))
		settingsbtn.setIconSize(QSize(18, 18))
		settingsbtn.setFixedSize(20, 20)
		settingsbtn.setToolTip('Set timer length.')
		btnOverlay2 = QGraphicsColorizeEffect()
		btnOverlay2.setColor(QColor(120, 120, 120))
		settingsbtn.setGraphicsEffect(btnOverlay2)
		settingsbtn.clicked.connect(self.settingsButtonClicked)

		buttonContainerLayout = QHBoxLayout()
		self.buttonContainerLayout = buttonContainerLayout
		buttonContainerLayout.addWidget(refreshLoopbtn)
		buttonContainerLayout.addWidget(alwaysOnTopbtn)
		buttonContainerLayout.addWidget(settingsbtn)
		buttonContainerLayout.setSpacing(0)
		buttonContainerLayout.setContentsMargins(0, 2, 0, 0)

		timeLayout = QHBoxLayout()
		timeLayout.addWidget(timelabel)

		layout = QVBoxLayout()
		layout.addLayout(buttonContainerLayout)

		timeLayout.setContentsMargins(0, 4, 0, 4)
		layout.addLayout(timeLayout)

		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)

		self.setLayout(layout)

	def alwaysOnTopButtonClicked(self):
		if self.alwaysOnTopBtnActive:
			self.alwaysOnTopBtnActive = False
			btnOverlay1 = QGraphicsColorizeEffect()
			btnOverlay1.setColor(QColor(120, 120, 120))
			self.alwaysOnTopbtn.setGraphicsEffect(btnOverlay1)
			self.parent().setWindowFlags(Qt.FramelessWindowHint)
			self.parent().show()
		else:
			self.alwaysOnTopBtnActive = True
			btnOverlay1 = QGraphicsColorizeEffect()
			btnOverlay1.setColor(QColor(200, 200, 200))
			self.alwaysOnTopbtn.setGraphicsEffect(btnOverlay1)
			self.parent().setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
			self.parent().show()

	def settingsButtonClicked(self):
		if self.refreshLoopController.settings.value("timer_length"):
			originalText = self.refreshLoopController.settings.value("timer_length")
		else:
			originalText = ""
		text, accept = QInputDialog.getText(self, 'Timer Length', 'Duration:', QLineEdit.Normal, originalText)
		if accept:
			self.refreshLoopController.setTimerLength(str(text).strip())

class ExLayer(QWidget):
	bgLayer = None
	_gripSize = 2

	def __init__(self):
		super().__init__()
		self.__press_pos = None
		self.initUI()

	def initUI(self):
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.setAttribute(Qt.WA_TranslucentBackground)

		bgLayer = BgLayer(self)
		self.bgLayer = bgLayer

		layout = QVBoxLayout()
		layout.addWidget(bgLayer)

		layout.setContentsMargins(2, 0, 2, 0)
		layout.setSpacing(0)

		self.setLayout(layout)

		self.sideGrips = [
			SideGrip(self, Qt.LeftEdge), 
			SideGrip(self, Qt.TopEdge), 
			SideGrip(self, Qt.RightEdge), 
			SideGrip(self, Qt.BottomEdge), 
		]
		self.cornerGrips = [QSizeGrip(self) for i in range(4)]

		btn = closeBtn()
		self.btn = btn
		btn.setParent(self)

	# Logic for resizing transparent window obtained from: https://stackoverflow.com/a/62812752
	# Licensed [CC BY-SA 4.0] - https://creativecommons.org/licenses/by-sa/4.0/
	@property
	def gripSize(self):
		return self._gripSize

	def setGripSize(self, size):
		if size == self._gripSize:
			return
		self._gripSize = max(2, size)
		self.updateGrips()

	def updateGrips(self):
		self.setContentsMargins(*[self.gripSize] * 4)

		outRect = self.rect()
		# An "inner" rect used for reference to set the geometries of size grips
		inRect = outRect.adjusted(self.gripSize, self.gripSize,
			-self.gripSize, -self.gripSize)

		# top left
		self.cornerGrips[0].setGeometry(
			QRect(outRect.topLeft(), inRect.topLeft()))
		# top right
		self.cornerGrips[1].setGeometry(
			QRect(outRect.topRight(), inRect.topRight()).normalized())
		# bottom right
		self.cornerGrips[2].setGeometry(
			QRect(inRect.bottomRight(), outRect.bottomRight()))
		# bottom left
		self.cornerGrips[3].setGeometry(
			QRect(outRect.bottomLeft(), inRect.bottomLeft()).normalized())

		# left edge
		self.sideGrips[0].setGeometry(
			0, inRect.top(), self.gripSize, inRect.height())
		# top edge
		self.sideGrips[1].setGeometry(
			inRect.left(), 0, inRect.width(), self.gripSize)
		# right edge
		self.sideGrips[2].setGeometry(
			inRect.left() + inRect.width(), 
			inRect.top(), self.gripSize, inRect.height())
		# bottom edge
		self.sideGrips[3].setGeometry(
			self.gripSize, inRect.top() + inRect.height(), 
			inRect.width(), self.gripSize)

	def resizeEvent(self, event):
		self.updateGrips()
		if self.btn:
			self.btn.move(self.width() - self.btn.width(), -3)

	def paintEvent(self, paintEvent):
		painter = QPainter(self)
		painter.setBrush(QColor(20, 20, 20, 127));
		painter.drawRect(-1, -1, self.width() + 1, self.height() + 1)

	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.__press_pos = event.pos()
			global clicked
			clicked = True

	def mouseReleaseEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.__press_pos = None

	def mouseMoveEvent(self, event):
		if self.__press_pos:
			self.move(self.pos() + (event.pos() - self.__press_pos))

def resource_path(filename):
	try:
		base_path = pathlib.Path(sys._MEIPASS).resolve()
	except Exception:
		base_path = pathlib.Path(__file__).parent.resolve() / "assets"

	return str((base_path / filename).resolve())

app = QApplication([])
app.setStyle("windows")
# app.setAttribute(Qt.AA_UseHighDpiPixmaps)
app.setStyleSheet("""
	QSizeGrip {
		color: rgba(0, 0, 0, 0);
		background: rgba(0, 0, 0, 0);
		border: none;
	}
	QPushButton:focus {
		outline: none;
	}
""")

QFontDatabase.addApplicationFont(resource_path("fonts/ChivoMono-VariableFont_wght.ttf"))

w = ExLayer()
w.setWindowTitle("Timer")
w.setWindowIcon(QIcon(resource_path("clock.png")))
w.show()

w.bgLayer.alwaysOnTopButtonClicked()

clicked = False

app.exec_()
