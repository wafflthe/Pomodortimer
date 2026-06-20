import sys
import json
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSpinBox, QPushButton, QLCDNumber,
    QTabWidget, QCheckBox, QMessageBox, QInputDialog
)

class PomodoroTimer(QWidget): # this tells Qt that this is a widget
    def __init__(self): # runs whenever its created
        super().__init__() # calls the QWidget's init to initialize everything Qt expects
        self.setWindowTitle("Pomodoro Timer")
        self.resize(360, 350)

        #Qt stylesheet
        self.setStyleSheet("""
QWidget {
    background-color: #2a1b3d;
    color: #f2e9ff;
    font-size: 16px;
}

QPushButton {
    background-color: #4b2e83;
    border: 2px solid #7a4fcf;
    padding: 6px;
    border-radius: 6px;
    color: #f2e9ff;
}

QPushButton:hover {
    background-color: #5c3aa3;
}

QSpinBox {
    background-color: #3a2558;
    border: 1px solid #7a4fcf;
    padding: 4px;
    border-radius: 4px;
    color: #f2e9ff;
}

QCheckBox {
    spacing: 8px;
}

QTabWidget::pane {
    border: 1px solid #7a4fcf;
}

QTabBar::tab {
    background: #4b2e83;
    padding: 6px;
    border: 1px solid #7a4fcf;
    border-bottom: none;
    color: #f2e9ff;
}

QTabBar::tab:selected {
    background: #7a4fcf;
}

QLCDNumber {
    background-color: #000000;
    color: #7db7ff;
    border: 2px solid #7a4fcf;
}

#statusLabel {
    font-size: 50px;
    font-weight: bold;
    color: #caa0ff;
}
""")


        #Mode setup switching
        with open("time.json", "r") as f:
            self.modes = json.load(f)

        for mode in self.modes:
            mode["time"] *= 60
        
        self.current_mode = 0
        self.remaining = self.modes[self.current_mode]["time"]

        #Widget config


        self.sot_button = QCheckBox("Stay on top")
        self.sot_button.stateChanged.connect(self.stay_on_top)
        #Checkbox setup

        self.display = QLCDNumber()
        self.display.setDigitCount(5)
        minutes = self.remaining // 60
        seconds = self.remaining % 60
        self.display.display(f"{minutes:02d}:{seconds:02d}")

        self.seconds = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        #timer config

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start)
        self.stop_button = QPushButton("Pause")
        self.stop_button.clicked.connect(self.pause)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)
        self.submit_button = QPushButton("Update")
        self.submit_button.clicked.connect(self.update_json)
        #Button creation and config

        work_label = QLabel("Work:")
        self.work_input = QSpinBox()
        self.work_input.setRange(1, 60)
        self.work_input.setValue(self.modes[0]["time"] // 60)
        work_suffix = QLabel("Minutes")

        break_label = QLabel("Break:")
        self.break_input = QSpinBox()
        self.break_input.setRange(1, 25)
        self.break_input.setValue(self.modes[1]["time"] // 60)
        break_suffix = QLabel("Minutes")
        #setup for both work and minute field for time update

        self.status = QLabel("Work!")
        self.status.setObjectName("statusLabel")
        #Thingy that stats pomodoro status

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tabs.addTab(self.tab1, "Timer")
        self.tabs.addTab(self.tab2, "Settings")
        #Tab setup for timer and settings setup



        #Layout and Widget setup
        #Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)

        #tab1 layout (timer)
        tab1_layout = QVBoxLayout(self.tab1)
        tab1_layout.addWidget(self.status, alignment=Qt.AlignHCenter)
        tab1_layout.addWidget(self.display)

        button_row = QHBoxLayout()
        button_row.addWidget(self.start_button)
        button_row.addWidget(self.stop_button)
        button_row.addWidget(self.reset_button)

        tab1_layout.addLayout(button_row)

        #tab2 layout (settings)
        tab2_layout = QVBoxLayout(self.tab2)

        work_row = QHBoxLayout()
        work_row.addWidget(work_label)
        work_row.addWidget(self.work_input)
        work_row.addWidget(work_suffix)
        tab2_layout.addLayout(work_row)

        break_row = QHBoxLayout()
        break_row.addWidget(break_label)
        break_row.addWidget(self.break_input)
        break_row.addWidget(break_suffix)
        tab2_layout.addLayout(break_row)

        final_row = QHBoxLayout()
        final_row.addWidget(self.sot_button)
        final_row.addWidget(self.submit_button)
        tab2_layout.addLayout(final_row)

        



    #Method setup
    def update_time(self):
        self.remaining -=1

        if self.remaining <= 0:
            self.switch_mode()
            return

        minutes = self.remaining // 60
        seconds = self.remaining % 60
        self.display.display(f"{minutes:02d}:{seconds:02d}")
    
    def switch_mode(self):
        self.current_mode = (self.current_mode + 1) % len(self.modes)
        self.remaining = self.modes[self.current_mode]["time"]
        if self.current_mode == 0:
            self.status.setText("Work!")
        else:
            self.status.setText("Break!")

        minutes = self.remaining // 60
        seconds = self.remaining % 60
        self.display.display(f"{minutes:02d}:{seconds:02d}")

    def reset(self):
        choice, ok = QInputDialog.getItem(
            self,
            "Reset Timer",
            "Reset to:",
            ["Work", "Break"],
            0,
            False
        )

        if not ok:
            return  # user cancelled

        if choice == "Work":
            self.current_mode = 0
        else:
            self.current_mode = 1

        self.remaining = self.modes[self.current_mode]["time"]

        if self.current_mode == 0:
            self.status.setText("Work!")
        else:
            self.status.setText("Break!")

        minutes = self.remaining // 60
        seconds = self.remaining % 60
        self.display.display(f"{minutes:02d}:{seconds:02d}")

    def start(self):
        self.timer.start(1000)

    def pause(self):
        self.timer.stop()

    def update_json(self):
        work_min = self.work_input.value()
        break_min = self.break_input.value()

        self.modes[0]["time"] = work_min * 60
        self.modes[1]["time"] = break_min * 60

        with open("time.json", "w") as f:
            json.dump([
                {"name": "Work", "time": work_min},
                {"name": "Break", "time": break_min}
            ], f, indent=4)

        QMessageBox.information(self, "Updated", "Timer settings saved!")
        self.current_mode = 0
        self.remaining = self.modes[0]["time"]
        minutes = self.remaining // 60
        seconds = self.remaining % 60
        self.display.display(f"{minutes:02d}:{seconds:02d}")

    def stay_on_top(self, state):
        if state == Qt.Checked:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        
        self.show()
    

app = QApplication(sys.argv)
window = PomodoroTimer() # make an instance of our widget
window.show()
app.exec()