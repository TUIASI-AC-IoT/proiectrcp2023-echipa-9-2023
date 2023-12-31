import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QTextEdit, QLabel

demo_topics = ["temperature", "house", "news"]

class MQTTServerGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.applyStyles()
    
    def initUI(self):
        layout = QVBoxLayout()

        self.topicComboBox = QComboBox()
        self.topicComboBox.addItem("Select a topic")

        self.topicComboBox.currentIndexChanged.connect(self.onTopicChanged)
        layout.addWidget(self.topicComboBox)

        # Last 10 messages
        self.lastMessagesBox = QTextEdit()
        self.lastMessagesBox.setReadOnly(True)
        layout.addWidget(QLabel("Last 10 Messages"))
        layout.addWidget(self.lastMessagesBox)

        # Connected Subscribers
        self.subscribersBox = QTextEdit()
        self.subscribersBox.setReadOnly(True)
        layout.addWidget(QLabel("Connected Subscribers"))
        layout.addWidget(self.subscribersBox)

        # QoS1 messages
        self.qos1Box = QTextEdit()
        self.qos1Box.setReadOnly(True)
        layout.addWidget(QLabel("QoS1 Messages"))
        layout.addWidget(self.qos1Box)

        # QoS2 messages
        self.qos2Box = QTextEdit()
        self.qos2Box.setReadOnly(True)
        layout.addWidget(QLabel("QoS2 Messages"))
        layout.addWidget(self.qos2Box)

        self.setLayout(layout)
        self.setWindowTitle('MQTT Server Stats')
        self.populateTopicDropdown(demo_topics)

    def onTopicChanged(self, index):
        # Logic to load messages
        pass

    def populateTopicDropdown(self, topics):
        for topic in topics:
            self.topicComboBox.addItem(str(topic))

    def applyStyles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #dcdcdc;
            }
            QLabel {
                font-size: 12pt;
            }
            QComboBox {
                border: 1px solid #767676;
                border-radius: 5px;
                padding: 5px;
                background-color: #1e1e1e;
                color: #dcdcdc;
                font-size: 11pt;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                border-radius: 5px;
                background: #1e1e1e;
                color: #dcdcdc;
            }
            QTextEdit {
                border: 2px solid #767676;
                border-radius: 10px;
                font-size: 10pt;
            }
        """)


def main():
    app = QApplication(sys.argv)
    gui = MQTTServerGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
