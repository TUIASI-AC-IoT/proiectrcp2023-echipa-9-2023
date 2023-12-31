import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QComboBox, QPushButton, QLabel, QLineEdit)
from PyQt5.QtCore import Qt

class MQTTClientUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('MQTT Client')
        self.setWindowTitle('MQTT Client')
        self.setGeometry(300, 250, 800, 600)  # Adjusted main window size
        self.setStyleSheet("""
            QWidget {
                background-color: #000;
                color: #fff;
            }
            QTextEdit {
                background-color: #121212;
                border-radius: 10px;
            }
            QLineEdit, QPushButton{
                font-size: 16px;
                padding-top: 8px;
                padding-bottom: 8px;
                background-color: #121212;
                border-radius: 5px;
            }
            QLineEdit {
                padding-left: 4px;
            }
            QPushButton {
                background-color: #3700B3;
            }
            QPushButton:hover {
                background-color: #6200EE;
            }
            QComboBox {
                font-size: 14px;
                padding-top: 8px;
                padding-bottom: 8px;
                padding-left: 4px;
                background-color: #121212;
                border-radius:5px;
            }
        """)

        # Layouts
        mainLayout = QVBoxLayout()
        topicLayout = QHBoxLayout()
        messageLayout = QHBoxLayout()
        sendLayout = QHBoxLayout()

        # Message History
        self.historyArea = QTextEdit()
        self.historyArea.setReadOnly(True)
        mainLayout.addWidget(self.historyArea)

        # Topic Input
        topicLayout.addWidget(QLabel("Topic:"))
        self.topicInput = QLineEdit()
        topicLayout.addWidget(self.topicInput)
        mainLayout.addLayout(topicLayout)

        # Message Input
        self.messageInput = QLineEdit()
        messageLayout.addWidget(QLabel("Message:"))
        messageLayout.addWidget(self.messageInput)
        mainLayout.addLayout(messageLayout)

        # QoS Selector
        self.qosSelector = QComboBox()
        self.qosSelector.addItems(['QoS 1', 'QoS 2', 'QoS 3'])
        sendLayout.addWidget(self.qosSelector)

        # Retain Flag Selector
        self.retainFlagButton = QPushButton('Retain: False')
        self.retainFlagButton.setCheckable(True)
        self.retainFlagButton.clicked.connect(self.toggleRetainFlag)
        sendLayout.addWidget(self.retainFlagButton)

        # Send Button
        sendButton = QPushButton('Send')
        sendButton.clicked.connect(self.sendMessage)
        sendLayout.addWidget(sendButton)

        mainLayout.addLayout(sendLayout)
        self.setLayout(mainLayout)

    def toggleRetainFlag(self):
        if self.retainFlagButton.isChecked():
            self.retainFlagButton.setText('Retain: True')
        else:
            self.retainFlagButton.setText('Retain: False')

    def sendMessage(self):
        message = self.messageInput.text()
        topic = self.topicInput.text()
        qos = self.qosSelector.currentText()
        retain = self.retainFlagButton.isChecked()

        #Aici trb sa adaugam logica

        self.updateHistory(f"Topic: {topic}, Message: {message}, QoS: {qos}, Retain: {retain}")

    def updateHistory(self, message):
        self.historyArea.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MQTTClientUI()
    ex.show()
    sys.exit(app.exec_())
