#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gpuRIR GUI Demo
A graphical user interface for demonstrating Room Impulse Response simulation
using the gpuRIR library with GPU acceleration.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import soundfile as sf
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QSlider, QTextEdit,
                             QGroupBox, QTabWidget, QFileDialog, QMessageBox,
                             QProgressBar, QCheckBox, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import gpuRIR

class RIRSimulationThread(QThread):
    finished = pyqtSignal(np.ndarray)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, params):
        super().__init__()
        self.params = params
        
    def run(self):
        try:
            self.progress.emit(10)
            
            # Extract parameters
            room_sz = self.params['room_sz']
            T60 = self.params['T60']
            pos_src = self.params['pos_src']
            pos_rcv = self.params['pos_rcv']
            fs = self.params['fs']
            att_diff = self.params['att_diff']
            att_max = self.params['att_max']
            mic_pattern = self.params['mic_pattern']
            abs_weights = self.params['abs_weights']
            
            self.progress.emit(30)
            
            # Calculate reflection coefficients
            beta = gpuRIR.beta_SabineEstimation(room_sz, T60, abs_weights=abs_weights)
            
            self.progress.emit(50)
            
            # Calculate timing parameters
            Tdiff = gpuRIR.att2t_SabineEstimator(att_diff, T60)
            Tmax = gpuRIR.att2t_SabineEstimator(att_max, T60)
            nb_img = gpuRIR.t2n(Tdiff, room_sz)
            
            self.progress.emit(70)
            
            # Simulate RIR
            if mic_pattern != "omni":
                orV_rcv = np.array([[0, 1, 0]] * len(pos_rcv))
                RIRs = gpuRIR.simulateRIR(room_sz, beta, pos_src, pos_rcv, nb_img, 
                                        Tmax, fs, Tdiff=Tdiff, orV_rcv=orV_rcv, 
                                        mic_pattern=mic_pattern)
            else:
                RIRs = gpuRIR.simulateRIR(room_sz, beta, pos_src, pos_rcv, nb_img, 
                                        Tmax, fs, Tdiff=Tdiff, mic_pattern=mic_pattern)
            
            self.progress.emit(100)
            self.finished.emit(RIRs)
            
        except Exception as e:
            self.error.emit(str(e))

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
    def plot_rir(self, RIRs, fs, pos_src, pos_rcv):
        self.fig.clear()
        
        nb_src, nb_rcv, _ = RIRs.shape
        t = np.arange(RIRs.shape[2]) / fs
        
        for src_idx in range(nb_src):
            for rcv_idx in range(nb_rcv):
                ax = self.fig.add_subplot(nb_src, nb_rcv, src_idx * nb_rcv + rcv_idx + 1)
                ax.plot(t, RIRs[src_idx, rcv_idx, :])
                ax.set_title(f'Src{src_idx+1} → Rcv{rcv_idx+1}')
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Amplitude')
                ax.grid(True)
        
        self.fig.tight_layout()
        self.draw()
        
    def plot_room_layout(self, room_sz, pos_src, pos_rcv):
        self.fig.clear()
        ax = self.fig.add_subplot(111, projection='3d')
        
        # Draw room boundaries
        x_room = [0, room_sz[0], room_sz[0], 0, 0]
        y_room = [0, 0, room_sz[1], room_sz[1], 0]
        z_room = [0, 0, 0, 0, 0]
        ax.plot(x_room, y_room, z_room, 'k-', linewidth=2)
        
        z_room = [room_sz[2], room_sz[2], room_sz[2], room_sz[2], room_sz[2]]
        ax.plot(x_room, y_room, z_room, 'k-', linewidth=2)
        
        for i in range(4):
            ax.plot([x_room[i], x_room[i]], [y_room[i], y_room[i]], 
                   [0, room_sz[2]], 'k-', linewidth=2)
        
        # Plot sources
        if len(pos_src) > 0:
            ax.scatter(pos_src[:, 0], pos_src[:, 1], pos_src[:, 2], 
                      c='red', s=100, marker='o', label='Sources')
        
        # Plot receivers
        if len(pos_rcv) > 0:
            ax.scatter(pos_rcv[:, 0], pos_rcv[:, 1], pos_rcv[:, 2], 
                      c='blue', s=100, marker='^', label='Receivers')
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('Room Layout')
        ax.legend()
        
        self.fig.tight_layout()
        self.draw()

class GPURIRDemoGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.RIRs = None
        self.current_fs = 16000
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('gpuRIR Demo - Room Impulse Response Simulation')
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Left panel for controls
        left_panel = QWidget()
        left_panel.setFixedWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Room parameters
        room_group = QGroupBox("Room Parameters")
        room_layout = QGridLayout()
        
        room_layout.addWidget(QLabel("Room Size (m):"), 0, 0)
        self.room_x = QDoubleSpinBox()
        self.room_x.setRange(0.1, 20.0)
        self.room_x.setValue(3.0)
        self.room_x.setSuffix(" m")
        room_layout.addWidget(QLabel("X:"), 0, 1)
        room_layout.addWidget(self.room_x, 0, 2)
        
        self.room_y = QDoubleSpinBox()
        self.room_y.setRange(0.1, 20.0)
        self.room_y.setValue(3.0)
        self.room_y.setSuffix(" m")
        room_layout.addWidget(QLabel("Y:"), 1, 1)
        room_layout.addWidget(self.room_y, 1, 2)
        
        self.room_z = QDoubleSpinBox()
        self.room_z.setRange(0.1, 10.0)
        self.room_z.setValue(2.5)
        self.room_z.setSuffix(" m")
        room_layout.addWidget(QLabel("Z:"), 2, 1)
        room_layout.addWidget(self.room_z, 2, 2)
        
        room_layout.addWidget(QLabel("T60 (s):"), 3, 0)
        self.t60_spin = QDoubleSpinBox()
        self.t60_spin.setRange(0.1, 5.0)
        self.t60_spin.setValue(1.0)
        self.t60_spin.setSuffix(" s")
        room_layout.addWidget(self.t60_spin, 3, 1, 1, 2)
        
        room_group.setLayout(room_layout)
        left_layout.addWidget(room_group)
        
        # Source positions
        src_group = QGroupBox("Source Positions")
        src_layout = QVBoxLayout()
        
        self.src_text = QTextEdit()
        self.src_text.setPlainText("1.0, 2.9, 0.5\n1.0, 2.0, 0.5")
        self.src_text.setMaximumHeight(80)
        src_layout.addWidget(QLabel("Format: x, y, z (one per line)"))
        src_layout.addWidget(self.src_text)
        
        src_group.setLayout(src_layout)
        left_layout.addWidget(src_group)
        
        # Receiver positions
        rcv_group = QGroupBox("Receiver Positions")
        rcv_layout = QVBoxLayout()
        
        self.rcv_text = QTextEdit()
        self.rcv_text.setPlainText("0.5, 1.0, 0.5\n1.0, 1.0, 0.5\n1.5, 1.0, 0.5")
        self.rcv_text.setMaximumHeight(80)
        rcv_layout.addWidget(QLabel("Format: x, y, z (one per line)"))
        rcv_layout.addWidget(self.rcv_text)
        
        rcv_group.setLayout(rcv_layout)
        left_layout.addWidget(rcv_group)
        
        # Simulation parameters
        sim_group = QGroupBox("Simulation Parameters")
        sim_layout = QGridLayout()
        
        sim_layout.addWidget(QLabel("Sampling Rate (Hz):"), 0, 0)
        self.fs_combo = QComboBox()
        self.fs_combo.addItems(["8000", "16000", "44100", "48000"])
        self.fs_combo.setCurrentText("16000")
        sim_layout.addWidget(self.fs_combo, 0, 1)
        
        sim_layout.addWidget(QLabel("Microphone Pattern:"), 1, 0)
        self.mic_pattern_combo = QComboBox()
        self.mic_pattern_combo.addItems(["omni", "card", "hypcard", "subcard", "bidir"])
        sim_layout.addWidget(self.mic_pattern_combo, 1, 1)
        
        sim_layout.addWidget(QLabel("Diffuse Attenuation (dB):"), 2, 0)
        self.att_diff_spin = QDoubleSpinBox()
        self.att_diff_spin.setRange(5.0, 60.0)
        self.att_diff_spin.setValue(15.0)
        sim_layout.addWidget(self.att_diff_spin, 2, 1)
        
        sim_layout.addWidget(QLabel("Max Attenuation (dB):"), 3, 0)
        self.att_max_spin = QDoubleSpinBox()
        self.att_max_spin.setRange(10.0, 100.0)
        self.att_max_spin.setValue(60.0)
        sim_layout.addWidget(self.att_max_spin, 3, 1)
        
        sim_group.setLayout(sim_layout)
        left_layout.addWidget(sim_group)
        
        # Control buttons
        button_layout = QVBoxLayout()
        
        self.simulate_btn = QPushButton("Simulate RIR")
        self.simulate_btn.clicked.connect(self.simulate_rir)
        button_layout.addWidget(self.simulate_btn)
        
        self.visualize_room_btn = QPushButton("Visualize Room Layout")
        self.visualize_room_btn.clicked.connect(self.visualize_room)
        button_layout.addWidget(self.visualize_room_btn)
        
        self.export_btn = QPushButton("Export RIR as WAV")
        self.export_btn.clicked.connect(self.export_rir)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        left_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        left_layout.addWidget(self.status_text)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # Right panel for plots
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Plot canvas
        self.plot_canvas = PlotCanvas(parent=right_panel, width=10, height=8)
        right_layout.addWidget(self.plot_canvas)
        
        layout.addWidget(right_panel)
        
        # Initialize
        self.log_message("gpuRIR Demo initialized. Ready to simulate Room Impulse Responses.")
        
    def log_message(self, message):
        self.status_text.append(message)
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )
        
    def parse_positions(self, text):
        positions = []
        lines = text.strip().split('\n')
        for line in lines:
            if line.strip():
                try:
                    coords = [float(x.strip()) for x in line.split(',')]
                    if len(coords) == 3:
                        positions.append(coords)
                except ValueError:
                    raise ValueError(f"Invalid position format: {line}")
        return np.array(positions)
    
    def simulate_rir(self):
        try:
            # Parse inputs
            room_sz = [self.room_x.value(), self.room_y.value(), self.room_z.value()]
            pos_src = self.parse_positions(self.src_text.toPlainText())
            pos_rcv = self.parse_positions(self.rcv_text.toPlainText())
            
            if len(pos_src) == 0:
                raise ValueError("At least one source position is required")
            if len(pos_rcv) == 0:
                raise ValueError("At least one receiver position is required")
            
            # Validate positions are inside room
            for pos in pos_src:
                if not (0 < pos[0] < room_sz[0] and 0 < pos[1] < room_sz[1] and 0 < pos[2] < room_sz[2]):
                    raise ValueError(f"Source position {pos} is outside room boundaries")
            
            for pos in pos_rcv:
                if not (0 < pos[0] < room_sz[0] and 0 < pos[1] < room_sz[1] and 0 < pos[2] < room_sz[2]):
                    raise ValueError(f"Receiver position {pos} is outside room boundaries")
            
            # Prepare simulation parameters
            params = {
                'room_sz': room_sz,
                'T60': self.t60_spin.value(),
                'pos_src': pos_src,
                'pos_rcv': pos_rcv,
                'fs': float(self.fs_combo.currentText()),
                'att_diff': self.att_diff_spin.value(),
                'att_max': self.att_max_spin.value(),
                'mic_pattern': self.mic_pattern_combo.currentText(),
                'abs_weights': [0.9]*5 + [0.5]  # Default absorption weights
            }
            
            self.current_fs = params['fs']
            
            # Start simulation in separate thread
            self.simulate_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.log_message("Starting RIR simulation...")
            
            self.sim_thread = RIRSimulationThread(params)
            self.sim_thread.finished.connect(self.on_simulation_finished)
            self.sim_thread.error.connect(self.on_simulation_error)
            self.sim_thread.progress.connect(self.progress_bar.setValue)
            self.sim_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.log_message(f"Error: {str(e)}")
    
    def on_simulation_finished(self, RIRs):
        self.RIRs = RIRs
        self.simulate_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Plot results
        pos_src = self.parse_positions(self.src_text.toPlainText())
        pos_rcv = self.parse_positions(self.rcv_text.toPlainText())
        self.plot_canvas.plot_rir(RIRs, self.current_fs, pos_src, pos_rcv)
        
        self.log_message(f"RIR simulation completed successfully!")
        self.log_message(f"RIR shape: {RIRs.shape} (sources × receivers × time)")
        self.log_message(f"RIR duration: {RIRs.shape[2] / self.current_fs:.3f} seconds")
        
    def on_simulation_error(self, error_msg):
        self.simulate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Simulation Error", error_msg)
        self.log_message(f"Simulation error: {error_msg}")
    
    def visualize_room(self):
        try:
            room_sz = [self.room_x.value(), self.room_y.value(), self.room_z.value()]
            pos_src = self.parse_positions(self.src_text.toPlainText())
            pos_rcv = self.parse_positions(self.rcv_text.toPlainText())
            
            self.plot_canvas.plot_room_layout(room_sz, pos_src, pos_rcv)
            self.log_message("Room layout visualization updated.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.log_message(f"Visualization error: {str(e)}")
    
    def export_rir(self):
        if self.RIRs is None:
            QMessageBox.warning(self, "Warning", "No RIR data to export. Please simulate first.")
            return
        
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export RIR", "rir_export.wav", "WAV files (*.wav)"
            )
            
            if filename:
                # Export first source-receiver pair
                rir_data = self.RIRs[0, 0, :]
                # Normalize to prevent clipping
                rir_data = rir_data / np.max(np.abs(rir_data))
                
                sf.write(filename, rir_data, int(self.current_fs))
                self.log_message(f"RIR exported to: {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
            self.log_message(f"Export error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Check if gpuRIR is available
    try:
        gpuRIR.activateMixedPrecision(False)
        gpuRIR.activateLUT(True)
        print("gpuRIR initialized successfully")
    except Exception as e:
        print(f"Warning: gpuRIR initialization issue: {e}")
    
    gui = GPURIRDemoGUI()
    gui.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()