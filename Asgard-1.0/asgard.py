import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from gui import Ui_MainWindow
from about import Ui_Dialog as About_Ui_Dialog


import serial_port_finder as spf

import serial, time
from sequence_recorder import MotionSequence, parse_status_report

s0 = serial.Serial()

class AboutDialog(About_Ui_Dialog):
    def __init__(self, dialog):
        About_Ui_Dialog.__init__(self)
        self.setupUi(dialog)

class AsgardGUI(Ui_MainWindow):
    def __init__(self, dialog):
        Ui_MainWindow.__init__(self)
        self.setupUi(dialog)

        self.getSerialPorts()

        self.SerialThreadClass = SerialThreadClass()
        self.SerialThreadClass.serialSignal.connect(self.updateConsole)
        self.sequence = MotionSequence()
        self.latest_status = ""
        self.latest_status_info = {}
        self.latest_status_received_at = 0
        self.status_generation = 0
        self.playback_active = False
        self.playback_events = []
        self.playback_index = 0
        self.playback_phase = ""
        self.playback_status_generation = 0
        self.playback_started_at = 0
        self.playbackTimer = QtCore.QTimer(dialog)
        self.playbackTimer.setSingleShot(True)
        self.playbackTimer.timeout.connect(self.sendPlaybackCommand)
        self.playbackTimeoutTimer = QtCore.QTimer(dialog)
        self.playbackTimeoutTimer.setSingleShot(True)
        self.playbackTimeoutTimer.timeout.connect(self.playbackTimedOut)

        self.actionAbout.triggered.connect(self.launchAboutWindow)
        self.actionExit.triggered.connect(self.close_application)

        self.HomeButton.pressed.connect(self.sendHomingCycleCommand)
        self.ZeroPositionButton.pressed.connect(self.sendZeroPositionCommand)
        self.KillAlarmLockButton.pressed.connect(self.sendKillAlarmCommand)

        self.G0MoveRadioButton.clicked.connect(self.FeedRateBoxHide)
        self.G1MoveRadioButton.clicked.connect(self.FeedRateBoxHide)

        self.FKGoButtonArt1.pressed.connect(self.FKMoveArt1)
        self.FKSliderArt1.valueChanged.connect(self.FKSliderUpdateArt1)
        self.SpinBoxArt1.valueChanged.connect(self.FKSpinBoxUpdateArt1)
        self.FKDec10ButtonArt1.pressed.connect(self.FKDec10Art1)
        self.FKDec1ButtonArt1.pressed.connect(self.FKDec1Art1)
        self.FKDec0_1ButtonArt1.pressed.connect(self.FKDec0_1Art1)
        self.FKInc0_1ButtonArt1.pressed.connect(self.FKInc0_1Art1)
        self.FKInc1ButtonArt1.pressed.connect(self.FKInc1Art1)
        self.FKInc10ButtonArt1.pressed.connect(self.FKInc10Art1)

        self.FKGoButtonArt2.pressed.connect(self.FKMoveArt2)
        self.FKSliderArt2.valueChanged.connect(self.FKSliderUpdateArt2)
        self.SpinBoxArt2.valueChanged.connect(self.FKSpinBoxUpdateArt2)
        self.FKDec10ButtonArt2.pressed.connect(self.FKDec10Art2)
        self.FKDec1ButtonArt2.pressed.connect(self.FKDec1Art2)
        self.FKDec0_1ButtonArt2.pressed.connect(self.FKDec0_1Art2)
        self.FKInc0_1ButtonArt2.pressed.connect(self.FKInc0_1Art2)
        self.FKInc1ButtonArt2.pressed.connect(self.FKInc1Art2)
        self.FKInc10ButtonArt2.pressed.connect(self.FKInc10Art2)

        self.FKGoButtonArt3.pressed.connect(self.FKMoveArt3)
        self.FKSliderArt3.valueChanged.connect(self.FKSliderUpdateArt3)
        self.SpinBoxArt3.valueChanged.connect(self.FKSpinBoxUpdateArt3)
        self.FKDec10ButtonArt3.pressed.connect(self.FKDec10Art3)
        self.FKDec1ButtonArt3.pressed.connect(self.FKDec1Art3)
        self.FKDec0_1ButtonArt3.pressed.connect(self.FKDec0_1Art3)
        self.FKInc0_1ButtonArt3.pressed.connect(self.FKInc0_1Art3)
        self.FKInc1ButtonArt3.pressed.connect(self.FKInc1Art3)
        self.FKInc10ButtonArt3.pressed.connect(self.FKInc10Art3)

        self.FKGoButtonArt4.pressed.connect(self.FKMoveArt4)
        self.FKSliderArt4.valueChanged.connect(self.FKSliderUpdateArt4)
        self.SpinBoxArt4.valueChanged.connect(self.FKSpinBoxUpdateArt4)
        self.FKDec10ButtonArt4.pressed.connect(self.FKDec10Art4)
        self.FKDec1ButtonArt4.pressed.connect(self.FKDec1Art4)
        self.FKDec0_1ButtonArt4.pressed.connect(self.FKDec0_1Art4)
        self.FKInc0_1ButtonArt4.pressed.connect(self.FKInc0_1Art4)
        self.FKInc1ButtonArt4.pressed.connect(self.FKInc1Art4)
        self.FKInc10ButtonArt4.pressed.connect(self.FKInc10Art4)

        self.FKGoButtonArt5.pressed.connect(self.FKMoveArt5)
        self.FKSliderArt5.valueChanged.connect(self.FKSliderUpdateArt5)
        self.SpinBoxArt5.valueChanged.connect(self.FKSpinBoxUpdateArt5)
        self.FKDec10ButtonArt5.pressed.connect(self.FKDec10Art5)
        self.FKDec1ButtonArt5.pressed.connect(self.FKDec1Art5)
        self.FKDec0_1ButtonArt5.pressed.connect(self.FKDec0_1Art5)
        self.FKInc0_1ButtonArt5.pressed.connect(self.FKInc0_1Art5)
        self.FKInc1ButtonArt5.pressed.connect(self.FKInc1Art5)
        self.FKInc10ButtonArt5.pressed.connect(self.FKInc10Art5)

        self.FKGoButtonArt6.pressed.connect(self.FKMoveArt6)
        self.FKSliderArt6.valueChanged.connect(self.FKSliderUpdateArt6)
        self.SpinBoxArt6.valueChanged.connect(self.FKSpinBoxUpdateArt6)
        self.FKDec10ButtonArt6.pressed.connect(self.FKDec10Art6)
        self.FKDec1ButtonArt6.pressed.connect(self.FKDec1Art6)
        self.FKDec0_1ButtonArt6.pressed.connect(self.FKDec0_1Art6)
        self.FKInc0_1ButtonArt6.pressed.connect(self.FKInc0_1Art6)
        self.FKInc1ButtonArt6.pressed.connect(self.FKInc1Art6)
        self.FKInc10ButtonArt6.pressed.connect(self.FKInc10Art6)

        self.FKGoAllButton.pressed.connect(self.FKMoveAll)

        self.GoButtonGripper.pressed.connect(self.MoveGripper)
        self.SliderGripper.valueChanged.connect(self.SliderUpdateGripper)
        self.SpinBoxGripper.valueChanged.connect(self.SpinBoxUpdateGripper)
        self.Dec10ButtonGripper.pressed.connect(self.Dec10Gripper)
        self.Dec1ButtonGripper.pressed.connect(self.Dec1Gripper)
        self.Inc1ButtonGripper.pressed.connect(self.Inc1Gripper)
        self.Inc10ButtonGripper.pressed.connect(self.Inc10Gripper)

        self.SerialPortRefreshButton.pressed.connect(self.getSerialPorts)
        self.ConnectButton.pressed.connect(self.connectSerial)

        self.ConsoleButtonSend.pressed.connect(self.sendSerialCommand)
        self.ConsoleInput.returnPressed.connect(self.sendSerialCommand)

        self.RecordButton.pressed.connect(self.startRecording)
        self.StopRecordingButton.pressed.connect(self.stopRecording)
        self.ResetSequenceButton.pressed.connect(self.resetSequence)
        self.LoadSequenceButton.pressed.connect(self.loadSequence)
        self.SaveSequenceButton.pressed.connect(self.saveSequence)
        self.RunSequenceButton.pressed.connect(self.runSequence)
        self.StopRunButton.pressed.connect(self.stopSequencePlayback)
        self.updateSequenceControls()

    def close_application(self):
        sys.exit()

    def launchAboutWindow(self):
        self.dialogAbout = QtWidgets.QDialog()
        self.ui = AboutDialog(self.dialogAbout)
        self.dialogAbout.exec_()

    def sendHomingCycleCommand(self):
        self.sendControllerCommand("$H")

    def sendZeroPositionCommand(self):
        self.sendControllerCommand("G0 A0 B0 C0 D0 X0 Y0 Z0", recordable=True)

    def sendKillAlarmCommand(self):
        self.sendControllerCommand("$X")

    def FeedRateBoxHide(self):
        if self.G1MoveRadioButton.isChecked():
            self.FeedRateLabel.setEnabled(True)
            self.FeedRateInput.setEnabled(True)
        else:
            self.FeedRateLabel.setEnabled(False)
            self.FeedRateInput.setEnabled(False)

    def sendControllerCommand(self, command, recordable=False, playback=False):
        command = command.strip()
        if not s0.isOpen():
            self.noSerialConnection()
            return False
        if self.playback_active and not playback:
            self.statusbar.showMessage("Stop the running sequence before sending another command.")
            return False
        sent_at = time.monotonic()
        try:
            s0.write((command + "\n").encode("UTF-8"))
        except Exception as error:
            self.ConsoleOutput.appendPlainText("Serial write failed: " + str(error))
            return False
        self.ConsoleOutput.appendPlainText(">>> " + command)
        if recordable and self.sequence.is_recording:
            self.sequence.record_command(command, self.latest_status, sent_at)
            self.updateSequenceControls()
        return True

    def startRecording(self):
        if not s0.isOpen():
            self.noSerialConnection()
            return
        if self.playback_active:
            return
        if self.sequence.events:
            answer = QtWidgets.QMessageBox.question(
                self.centralwidget,
                "Start new recording",
                "Replace the current in-memory sequence with a new recording?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )
            if answer != QtWidgets.QMessageBox.Yes:
                return
        self.sequence.start()
        self.statusbar.showMessage("Recording motion commands and controller status.")
        self.updateSequenceControls()

    def stopRecording(self):
        if self.sequence.is_recording:
            self.sequence.stop()
            self.statusbar.showMessage("Recording stopped. Save the sequence before closing Asgard.")
            self.updateSequenceControls()

    def resetSequence(self):
        if self.playback_active or self.sequence.is_recording:
            return
        if self.sequence.events:
            answer = QtWidgets.QMessageBox.question(
                self.centralwidget,
                "Reset sequence",
                "Discard the recorded sequence and all status samples?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )
            if answer != QtWidgets.QMessageBox.Yes:
                return
        self.sequence.clear()
        self.statusbar.showMessage("Sequence reset.")
        self.updateSequenceControls()

    def saveSequence(self):
        if self.sequence.is_recording:
            self.stopRecording()
        if not self.sequence.events:
            self.statusbar.showMessage("There is no recorded sequence to save.")
            return
        path, unused_filter = QtWidgets.QFileDialog.getSaveFileName(
            self.centralwidget,
            "Save Asgard sequence",
            "",
            "Asgard sequence (*.json)",
        )
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        try:
            self.sequence.save(path)
        except (IOError, OSError, ValueError) as error:
            QtWidgets.QMessageBox.warning(self.centralwidget, "Save failed", str(error))
            return
        self.statusbar.showMessage("Sequence saved: " + path)

    def loadSequence(self):
        if self.sequence.is_recording or self.playback_active:
            return
        path, unused_filter = QtWidgets.QFileDialog.getOpenFileName(
            self.centralwidget,
            "Load Asgard sequence",
            "",
            "Asgard sequence (*.json)",
        )
        if not path:
            return
        try:
            self.sequence.load(path)
        except (IOError, OSError, ValueError, TypeError) as error:
            QtWidgets.QMessageBox.warning(self.centralwidget, "Load failed", str(error))
            return
        self.statusbar.showMessage("Sequence loaded: {} commands".format(self.sequence.command_count))
        self.updateSequenceControls()

    def runSequence(self):
        if not s0.isOpen():
            self.noSerialConnection()
            return
        if self.sequence.is_recording or self.playback_active:
            return
        if self.sequence.command_count == 0:
            self.statusbar.showMessage("Record or load a sequence before running it.")
            return
        if (not self.latest_status_info
                or self.latest_status_info.get("state") != "Idle"
                or time.monotonic() - self.latest_status_received_at > 1.0):
            QtWidgets.QMessageBox.warning(
                self.centralwidget,
                "Controller not ready",
                "Playback requires a fresh GRBL Idle report. Home the arm and verify the workspace first.",
            )
            return
        answer = QtWidgets.QMessageBox.question(
            self.centralwidget,
            "Run sequence",
            "Run {} recorded commands? Confirm the arm is homed, the payload is secured, and the path is clear. "
            "Playback uses recorded feed commands; reported positions are controller estimates, not encoder readings.".format(
                self.sequence.command_count
            ),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )
        if answer != QtWidgets.QMessageBox.Yes:
            return
        self.playback_events = [
            event for event in self.sequence.events if event["type"] == "command"
        ]
        self.playback_index = 0
        self.playback_started_at = time.monotonic()
        self.playback_active = True
        self.statusbar.showMessage("Sequence running. Use the physical emergency stop if motion is unsafe.")
        self.updateSequenceControls()
        self.schedulePlaybackCommand()

    def schedulePlaybackCommand(self):
        if not self.playback_active or self.playback_index >= len(self.playback_events):
            return
        due_at = self.playback_started_at + self.playback_events[self.playback_index]["t_s"]
        delay_ms = max(0, int((due_at - time.monotonic()) * 1000))
        if delay_ms:
            self.playbackTimer.start(delay_ms)
        else:
            self.sendPlaybackCommand()

    def sendPlaybackCommand(self):
        if not self.playback_active or self.playback_index >= len(self.playback_events):
            return
        event = self.playback_events[self.playback_index]
        self.playback_phase = "command"
        if not self.sendControllerCommand(event["command"], playback=True):
            self.stopSequencePlayback()
            return
        self.playbackTimeoutTimer.start(120000)

    def handlePlaybackResponse(self, response):
        response = response.strip().lower()
        if response.startswith("error:") or response.startswith("alarm:"):
            self.stopSequencePlayback()
            self.statusbar.showMessage("Playback halted after controller response: " + response)
            return
        if not self.playback_active or response != "ok":
            return
        self.playbackTimeoutTimer.stop()
        if self.playback_phase == "command":
            self.playback_phase = "sync"
            if not self.sendControllerCommand("G4 P0", playback=True):
                self.stopSequencePlayback()
                return
            self.playbackTimeoutTimer.start(120000)
        elif self.playback_phase == "sync":
            self.playback_phase = "idle"
            self.playback_status_generation = self.status_generation
            self.playbackTimeoutTimer.start(120000)

    def handlePlaybackStatus(self, status):
        if self.playback_active and status.get("state") in ("Alarm", "Hold", "Door"):
            self.stopSequencePlayback()
            self.statusbar.showMessage(
                "Playback halted by controller state: {}".format(status.get("state"))
            )
            return
        if (not self.playback_active or self.playback_phase != "idle"
                or self.status_generation <= self.playback_status_generation
                or status.get("state") != "Idle"):
            return
        self.playbackTimeoutTimer.stop()
        self.playback_index += 1
        if self.playback_index >= len(self.playback_events):
            self.playback_active = False
            self.playback_phase = ""
            self.statusbar.showMessage("Sequence complete.")
            self.updateSequenceControls()
            return
        self.playback_phase = ""
        self.schedulePlaybackCommand()

    def playbackTimedOut(self):
        if self.playback_active:
            self.stopSequencePlayback()
            self.statusbar.showMessage("Playback halted: controller response or Idle report timed out.")

    def stopSequencePlayback(self):
        if not self.playback_active:
            return
        self.playback_active = False
        self.playback_phase = ""
        self.playbackTimer.stop()
        self.playbackTimeoutTimer.stop()
        if s0.isOpen():
            try:
                s0.write(b"!")
            except Exception:
                pass
        self.statusbar.showMessage("Playback stopped. The physical emergency stop is required for emergencies.")
        self.updateSequenceControls()

    def updateSequenceControls(self):
        recording = self.sequence.is_recording
        busy = recording or self.playback_active
        self.RecordButton.setEnabled(not busy and s0.isOpen())
        self.StopRecordingButton.setEnabled(recording)
        self.ResetSequenceButton.setEnabled(not busy and bool(self.sequence.events))
        self.LoadSequenceButton.setEnabled(not busy)
        self.SaveSequenceButton.setEnabled(not self.playback_active and bool(self.sequence.events))
        self.RunSequenceButton.setEnabled(
            not busy and self.sequence.command_count > 0 and s0.isOpen()
        )
        self.StopRunButton.setEnabled(self.playback_active)
        if recording:
            label = "REC {}".format(self.sequence.command_count)
        elif self.playback_active:
            label = "RUN {}/{}".format(self.playback_index + 1, len(self.playback_events))
        else:
            label = "{} moves".format(self.sequence.command_count)
        self.SequenceStatusLabel.setText(label)


#FK Art1 Functions
    def FKMoveArt1(self):
        if s0.isOpen():
            if self.G1MoveRadioButton.isChecked():
                typeOfMovement="G1 "
                feedRate=" F" + str(self.FeedRateInput.value())
            else:
                typeOfMovement="G0 "
                feedRate=""
            message=typeOfMovement + "A" + str(self.SpinBoxArt1.value()) + feedRate
            self.sendControllerCommand(message, recordable=True)
        else:
            self.noSerialConnection()
    def FKSliderUpdateArt1(self):
        val=self.FKSliderArt1.value()/10
        self.SpinBoxArt1.setValue(val)
    def FKSpinBoxUpdateArt1(self):
        val=int(self.SpinBoxArt1.value()*10)
        self.FKSliderArt1.setValue(val)
    def FKDec10Art1(self):
        val=self.SpinBoxArt1.value()-10
        self.SpinBoxArt1.setValue(val)
    def FKDec1Art1(self):
        val=self.SpinBoxArt1.value()-1
        self.SpinBoxArt1.setValue(val)
    def FKDec0_1Art1(self):
        val=self.SpinBoxArt1.value()-0.1
        self.SpinBoxArt1.setValue(val)
    def FKInc0_1Art1(self):
        val=self.SpinBoxArt1.value()+0.1
        self.SpinBoxArt1.setValue(val)
    def FKInc1Art1(self):
        val=self.SpinBoxArt1.value()+1
        self.SpinBoxArt1.setValue(val)
    def FKInc10Art1(self):
        val=self.SpinBoxArt1.value()+10
        self.SpinBoxArt1.setValue(val)

#FK Art2 Functions
    def FKMoveArt2(self):
        if s0.isOpen():
            if self.G1MoveRadioButton.isChecked():
                typeOfMovement="G1 "
                feedRate=" F" + str(self.FeedRateInput.value())
            else:
                typeOfMovement="G0 "
                feedRate=""
            message=typeOfMovement + "B" + str(self.SpinBoxArt2.value()) + " C" + str(self.SpinBoxArt2.value()) + feedRate
            self.sendControllerCommand(message, recordable=True)
        else:
            self.noSerialConnection()
    def FKSliderUpdateArt2(self):
        val=self.FKSliderArt2.value()/10
        self.SpinBoxArt2.setValue(val)
    def FKSpinBoxUpdateArt2(self):
        val=int(self.SpinBoxArt2.value()*10)
        self.FKSliderArt2.setValue(val)
    def FKDec10Art2(self):
        val=self.SpinBoxArt2.value()-10
        self.SpinBoxArt2.setValue(val)
    def FKDec1Art2(self):
        val=self.SpinBoxArt2.value()-1
        self.SpinBoxArt2.setValue(val)
    def FKDec0_1Art2(self):
        val=self.SpinBoxArt2.value()-0.1
        self.SpinBoxArt2.setValue(val)
    def FKInc0_1Art2(self):
        val=self.SpinBoxArt2.value()+0.1
        self.SpinBoxArt2.setValue(val)
    def FKInc1Art2(self):
        val=self.SpinBoxArt2.value()+1
        self.SpinBoxArt2.setValue(val)
    def FKInc10Art2(self):
        val=self.SpinBoxArt2.value()+10
        self.SpinBoxArt2.setValue(val)

#FK Art3 Functions
    def FKMoveArt3(self):
        if s0.isOpen():
            if self.G1MoveRadioButton.isChecked():
                typeOfMovement="G1 "
                feedRate=" F" + str(self.FeedRateInput.value())
            else:
                typeOfMovement="G0 "
                feedRate=""
            message=typeOfMovement + "D" + str(self.SpinBoxArt3.value()) + feedRate
            self.sendControllerCommand(message, recordable=True)
        else:
            self.noSerialConnection()
    def FKSliderUpdateArt3(self):
        val=self.FKSliderArt3.value()/10
        self.SpinBoxArt3.setValue(val)
    def FKSpinBoxUpdateArt3(self):
        val=int(self.SpinBoxArt3.value()*10)
        self.FKSliderArt3.setValue(val)
    def FKDec10Art3(self):
        val=self.SpinBoxArt3.value()-10
        self.SpinBoxArt3.setValue(val)
    def FKDec1Art3(self):
        val=self.SpinBoxArt3.value()-1
        self.SpinBoxArt3.setValue(val)
    def FKDec0_1Art3(self):
        val=self.SpinBoxArt3.value()-0.1
        self.SpinBoxArt3.setValue(val)
    def FKInc0_1Art3(self):
        val=self.SpinBoxArt3.value()+0.1
        self.SpinBoxArt3.setValue(val)
    def FKInc1Art3(self):
        val=self.SpinBoxArt3.value()+1
        self.SpinBoxArt3.setValue(val)
    def FKInc10Art3(self):
        val=self.SpinBoxArt3.value()+10
        self.SpinBoxArt3.setValue(val)

#FK Art4 Functions
    def FKMoveArt4(self):
        if s0.isOpen():
            if self.G1MoveRadioButton.isChecked():
                typeOfMovement="G1 "
                feedRate=" F" + str(self.FeedRateInput.value())
            else:
                typeOfMovement="G0 "
                feedRate=""
            message=typeOfMovement + "X" + str(self.SpinBoxArt4.value()) + feedRate
            self.sendControllerCommand(message, recordable=True)
        else:
            self.noSerialConnection()
    def FKSliderUpdateArt4(self):
        val=self.FKSliderArt4.value()/10
        self.SpinBoxArt4.setValue(val)
    def FKSpinBoxUpdateArt4(self):
        val=int(self.SpinBoxArt4.value()*10)
        self.FKSliderArt4.setValue(val)
    def FKDec10Art4(self):
        val=self.SpinBoxArt4.value()-10
        self.SpinBoxArt4.setValue(val)
    def FKDec1Art4(self):
        val=self.SpinBoxArt4.value()-1
        self.SpinBoxArt4.setValue(val)
    def FKDec0_1Art4(self):
        val=self.SpinBoxArt4.value()-0.1
        self.SpinBoxArt4.setValue(val)
    def FKInc0_1Art4(self):
        val=self.SpinBoxArt4.value()+0.1
        self.SpinBoxArt4.setValue(val)
    def FKInc1Art4(self):
        val=self.SpinBoxArt4.value()+1
        self.SpinBoxArt4.setValue(val)
    def FKInc10Art4(self):
        val=self.SpinBoxArt4.value()+10
        self.SpinBoxArt4.setValue(val)

#FK Art5 Functions
    def FKMoveArt5(self): # En realidad esto no va así, hay que calcular el movimiento acoplado. Proximamente.
        if s0.isOpen():
            if self.G1MoveRadioButton.isChecked():
                typeOfMovement="G1 "
                feedRate=" F" + str(self.FeedRateInput.value())
            else:
                typeOfMovement="G0 "
                feedRate=""
            message=typeOfMovement + "Y" + str(self.SpinBoxArt5.value()) + feedRate
            self.sendControllerCommand(message, recordable=True)
        else:
            self.noSerialConnection()
    def FKSliderUpdateArt5(self):
        val=self.FKSliderArt5.value()/10
        self.SpinBoxArt5.setValue(val)
    def FKSpinBoxUpdateArt5(self):
        val=int(self.SpinBoxArt5.value()*10)
        self.FKSliderArt5.setValue(val)
    def FKDec10Art5(self):
        val=self.SpinBoxArt5.value()-10
        self.SpinBoxArt5.setValue(val)
    def FKDec1Art5(self):
        val=self.SpinBoxArt5.value()-1
        self.SpinBoxArt5.setValue(val)
    def FKDec0_1Art5(self):
        val=self.SpinBoxArt5.value()-0.1
        self.SpinBoxArt5.setValue(val)
    def FKInc0_1Art5(self):
        val=self.SpinBoxArt5.value()+0.1
        self.SpinBoxArt5.setValue(val)
    def FKInc1Art5(self):
        val=self.SpinBoxArt5.value()+1
        self.SpinBoxArt5.setValue(val)
    def FKInc10Art5(self):
        val=self.SpinBoxArt5.value()+10
        self.SpinBoxArt5.setValue(val)

#FK Art6 Functions
    def FKMoveArt6(self): # En realidad esto no va así, hay que calcular el movimiento acoplado. Proximamente.
        if s0.isOpen():
            if self.G1MoveRadioButton.isChecked():
                typeOfMovement="G1 "
                feedRate=" F" + str(self.FeedRateInput.value())
            else:
                typeOfMovement="G0 "
                feedRate=""
            message=typeOfMovement + "Z" + str(self.SpinBoxArt6.value()) + feedRate
            self.sendControllerCommand(message, recordable=True)
        else:
            self.noSerialConnection()
    def FKSliderUpdateArt6(self):
        val=self.FKSliderArt6.value()/10
        self.SpinBoxArt6.setValue(val)
    def FKSpinBoxUpdateArt6(self):
        val=int(self.SpinBoxArt6.value()*10)
        self.FKSliderArt6.setValue(val)
    def FKDec10Art6(self):
        val=self.SpinBoxArt6.value()-10
        self.SpinBoxArt6.setValue(val)
    def FKDec1Art6(self):
        val=self.SpinBoxArt6.value()-1
        self.SpinBoxArt6.setValue(val)
    def FKDec0_1Art6(self):
        val=self.SpinBoxArt6.value()-0.1
        self.SpinBoxArt6.setValue(val)
    def FKInc0_1Art6(self):
        val=self.SpinBoxArt6.value()+0.1
        self.SpinBoxArt6.setValue(val)
    def FKInc1Art6(self):
        val=self.SpinBoxArt6.value()+1
        self.SpinBoxArt6.setValue(val)
    def FKInc10Art6(self):
        val=self.SpinBoxArt6.value()+10
        self.SpinBoxArt6.setValue(val)

#FK Every Articulation Functions
    def FKMoveAll(self): # En realidad esto no va así, hay que calcular el movimiento acoplado. Proximamente.
        if s0.isOpen():
            if self.G1MoveRadioButton.isChecked():
                typeOfMovement="G1 "
                feedRate=" F" + str(self.FeedRateInput.value())
            else:
                typeOfMovement="G0 "
                feedRate=""
            message=typeOfMovement + "A" + str(self.SpinBoxArt1.value()) + " B" + str(self.SpinBoxArt2.value()) + " C" + str(self.SpinBoxArt2.value()) + " D" + str(self.SpinBoxArt3.value()) + " X" + str(self.SpinBoxArt4.value()) + " Y" + str(self.SpinBoxArt5.value()) + " Z" + str(self.SpinBoxArt6.value()) + feedRate
            self.sendControllerCommand(message, recordable=True)
        else:
            self.noSerialConnection()

# Gripper Functions
    def MoveGripper(self): # En realidad esto no va así, hay que calcular el movimiento acoplado. Proximamente.
        if s0.isOpen():
            message="M3 S" + str((255/100)*self.SpinBoxGripper.value())
            self.sendControllerCommand(message, recordable=True)
        else:
            self.noSerialConnection()

    def SliderUpdateGripper(self):
        val=self.SliderGripper.value()
        self.SpinBoxGripper.setValue(val)
    def SpinBoxUpdateGripper(self):
        val=int(self.SpinBoxGripper.value())
        self.SliderGripper.setValue(val)
    def Dec10Gripper(self):
        val=self.SpinBoxGripper.value()-10
        self.SpinBoxGripper.setValue(val)
    def Dec1Gripper(self):
        val=self.SpinBoxGripper.value()-1
        self.SpinBoxGripper.setValue(val)
    def Inc1Gripper(self):
        val=self.SpinBoxGripper.value()+1
        self.SpinBoxGripper.setValue(val)
    def Inc10Gripper(self):
        val=self.SpinBoxGripper.value()+10
        self.SpinBoxGripper.setValue(val)

# Serial Connection functions
    def getSerialPorts(self):
        self.SerialPortComboBox.clear()
        self.SerialPortComboBox.addItems(spf.serial_ports())

    def connectSerial(self):
        serialPort = self.SerialPortComboBox.currentText()
        baudrate = self.BaudRateComboBox.currentText()
        if serialPort != "":
            if baudrate!="":
                s0.port = serialPort
                s0.baudrate = baudrate
                s0.timeout = 1
                try:
                    s0.close()
                    s0.open()
                    self.SerialThreadClass.start()
                    self.updateSequenceControls()
                except Exception as e:
                    print ("error opening serial port: " + str(e))
            else:
                self.blankBaudRate()
        else:
            self.blankSerialPort()

    def serialDisconnected(self):
        self.RobotStateDisplay.setStyleSheet('background-color: rgb(255, 0, 0)')
        self.RobotStateDisplay.setText("Disconnected")

    def updateConsole(self, dataRead, receivedAt=None):
        if receivedAt is None:
            receivedAt = time.monotonic()
        verboseShow=self.ConsoleShowVerbosecheckBox.isChecked()
        okShow=self.ConsoleShowOkRespcheckBox.isChecked()

        if dataRead=="SERIAL-DISCONNECTED":
            self.stopSequencePlayback()
            if s0.isOpen():
                s0.close()
            self.serialDisconnected()
            print ("Serial Connection Lost")
        else:
            status = parse_status_report(dataRead)
            if status:
                self.latest_status = dataRead
                self.latest_status_info = status
                self.latest_status_received_at = receivedAt
                self.status_generation += 1
                if self.sequence.is_recording:
                    self.sequence.record_status(dataRead, receivedAt)
                self.updateCurrentState(status["state"])
                self.updateFKPosDisplay(dataRead)
                self.handlePlaybackStatus(status)
                self.updateSequenceControls()
                if verboseShow:
                    self.ConsoleOutput.appendPlainText(dataRead)
            elif dataRead.strip().lower() == "ok":
                self.handlePlaybackResponse(dataRead)
                if okShow:
                    self.ConsoleOutput.appendPlainText(dataRead)
            elif dataRead.strip().lower().startswith(("error:", "alarm:")):
                self.handlePlaybackResponse(dataRead)
                self.ConsoleOutput.appendPlainText(dataRead)
            else:
                self.ConsoleOutput.appendPlainText(dataRead)

    def sendSerialCommand(self):
        message = self.ConsoleInput.text().strip()
        if message and self.sendControllerCommand(message, recordable=True):
            self.ConsoleInput.clear()

    def updateFKPosDisplay(self,dataRead):
        status = parse_status_report(dataRead)
        positions = status.get("mpos", {})
        widgets_by_axis = {
            "A": self.FKCurrentPosValueArt1,
            "B": self.FKCurrentPosValueArt2,
            "D": self.FKCurrentPosValueArt3,
            "X": self.FKCurrentPosValueArt4,
            "Y": self.FKCurrentPosValueArt5,
            "Z": self.FKCurrentPosValueArt6,
        }
        named_positions = False
        for axis, widget in widgets_by_axis.items():
            if axis in positions:
                widget.setText("{}º".format(positions[axis]))
                named_positions = True
        if named_positions or not positions:
            return
        try:
            data=dataRead[1:][:-1].split(",")
            self.FKCurrentPosValueArt1.setText(data[1][5:][:-2]+"º")
            self.FKCurrentPosValueArt2.setText(data[2][:-2]+"º")
            self.FKCurrentPosValueArt3.setText(data[4][:-2]+"º")
            self.FKCurrentPosValueArt4.setText(data[5][:-2]+"º")
            self.FKCurrentPosValueArt5.setText(data[6][:-2]+"º")
            self.FKCurrentPosValueArt6.setText(data[7][:-2]+"º")
        except (IndexError, ValueError):
            pass

    def updateCurrentState(self, state):
        self.RobotStateDisplay.setText(state)
        if state=="Idle" or state=="Run":
            self.RobotStateDisplay.setStyleSheet('background-color: rgb(0, 255, 0)')
        elif state=="Home":
            self.RobotStateDisplay.setStyleSheet('background-color: rgb(85, 255, 255)')
        elif state=="Alarm":
            self.RobotStateDisplay.setStyleSheet('background-color: rgb(255, 255, 0)')
        elif state=="Hold":
            self.RobotStateDisplay.setStyleSheet('background-color: rgb(255, 0, 0)')
        else:
            self.RobotStateDisplay.setStyleSheet('background-color: rgb(255, 255, 255)')


    def blankSerialPort(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText("There is not Serial Port value indicated to establish the connection.\nPlease check it and try to connect again.")
        msgBox.exec_()

    def blankBaudRate(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText("There is not Baud Rate value indicated to establish the connection.\nPlease check it and try to connect again.")
        msgBox.exec_()

    def noSerialConnection(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText("The connection has not been established yet. Please establish the connection before trying to control.")
        msgBox.exec_()

############### SERIAL READ THREAD CLASS ###############

class SerialThreadClass(QtCore.QThread):
    serialSignal = pyqtSignal(str, float)
    def __init__(self, parent=None):
         super(SerialThreadClass,self).__init__(parent)
         self.lastStatusRequest = 0
    def run(self):
        while True:
            if s0.isOpen():
                try:
                    if time.monotonic() - self.lastStatusRequest >= 0.1:
                        self.lastStatusRequest = time.monotonic()
                        s0.write(b"?")
                    rawData = s0.readline()
                    receivedAt = time.monotonic()
                    if rawData:
                        dataRead = rawData.decode("UTF-8", errors="replace").strip()
                        if dataRead:
                            self.serialSignal.emit(dataRead, receivedAt)
                except Exception:
                    self.serialSignal.emit("SERIAL-DISCONNECTED", time.monotonic())
                    print ("Lost Serial connection!")
            else:
                self.msleep(50)


###############  SERIAL READ THREAD CLASS ###############










if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mwindow = QtWidgets.QMainWindow()

    prog = AsgardGUI(mwindow)

    # make the fixed-size UI scrollable so it fits small screens
    designed = mwindow.size()                 # size set by gui.py's setupUi
    central = mwindow.takeCentralWidget()
    central.setMinimumSize(designed)
    scroll = QtWidgets.QScrollArea()
    scroll.setWidget(central)
    scroll.setWidgetResizable(False)
    mwindow.setCentralWidget(scroll)
    mwindow.resize(designed.width() + 20, 820)   # fits the Air's 900px

    mwindow.show()
    sys.exit(app.exec_())

