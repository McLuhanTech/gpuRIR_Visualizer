# gpuRIR_Visualizer Demo
Based on QT &amp; gpuRIR for Room Impulse Response Visualizer基于QT的gpuRIR可视化，可导出混响参数用于音频处理

A graphical user interface for demonstrating Room Impulse Response (RIR) simulation using the gpuRIR library.
一个用于演示如何使用 gpuRIR 库进行房间脉冲响应 (RIR) 模拟的图形界面。
## Features
- **交互式房间配置**：设置房间尺寸和混响时间 (T60)
- **声源/接收机定位**：定义多个声源和接收机位置
- **实时可视化**：
- 包含声源和接收机位置的 3D 房间布局
- 所有声源-接收机对的 RIR 波形图
- **模拟参数**：配置采样率、麦克风模式和衰减设置
- **导出功能**：将 RIR 数据保存为 WAV 文件以供进一步分析
- **进度跟踪**：通过实时状态更新监控模拟进度
  
- **Interactive Room Configuration**: Set room dimensions and reverberation time (T60)
- **Source/Receiver Positioning**: Define multiple source and receiver positions
- **Real-time Visualization**: 
  - 3D room layout with source and receiver positions
  - RIR waveform plots for all source-receiver pairs
- **Simulation Parameters**: Configure sampling rate, microphone patterns, and attenuation settings
- **Export Functionality**: Save RIR data as WAV files for further analysis
- **Progress Tracking**: Monitor simulation progress with real-time status updates

## Requirements

Before running the GUI demo, install the required dependencies:
需要安装以下依赖：
```bash
pip install -r requirements_gui.txt
```

Required packages:
- PyQt5 (>=5.15.0) - GUI framework
- matplotlib (>=3.5.0) - Plotting and visualization
- numpy (>=1.20.0) - Numerical computing
- soundfile (>=0.10.0) - Audio file I/O
- scipy (>=1.7.0) - Scientific computing

## Usage

1. **Install dependencies**:
   ```bash
   pip install -r requirements_gui.txt
   ```

2. **Run the GUI demo**:
   ```bash
   python gpurir_gui_demo.py
   ```

3. **Configure simulation parameters**:
   - 设置房间尺寸（X、Y、Z 轴，以米为单位）
   - 定义混响时间（T60，以秒为单位）
   - 输入声源位置（格式：x、y、z - 每行一个）
   - 输入接收器位置（格式：x、y、z - 每行一个）
   - 选择采样率和麦克风模式
   - Set room dimensions (X, Y, Z in meters)
   - Define reverberation time (T60 in seconds)
   - Enter source positions (format: x, y, z - one per line)
   - Enter receiver positions (format: x, y, z - one per line)
   - Choose sampling rate and microphone pattern

5. **Visualize and simulate**:
   - 点击“可视化房间布局”查看 3D 房间设置
   - 点击“模拟 RIR”运行模拟
   - 查看生成的 RIR 波形
   - 如有需要，可将结果导出为 WAV 文件
   - Click "Visualize Room Layout" to see the 3D room setup
   - Click "Simulate RIR" to run the simulation
   - View the resulting RIR waveforms
   - Export results as WAV files if needed

## Example Configuration

**Room Parameters:** **房间参数:**
- Size: 3.0 × 3.0 × 2.5 m米
- T60: 1.0 s秒

**Source Positions:** **声源位置 :**
```
1.0, 2.9, 0.5
1.0, 2.0, 0.5
```

**Receiver Positions:** **接收位置:**
```
0.5, 1.0, 0.5
1.0, 1.0, 0.5
1.5, 1.0, 0.5
```

## GUI Components

### Left Panel Controls:
- **房间参数**：房间尺寸和 T60 配置
- **声源/接收位置**：用于坐标定义的文本输入
- **模拟参数**：采样率、麦克风模式、衰减设置
- **控制按钮**：模拟、可视化和导出功能
- **进度条**：实时模拟进度
- **状态日志**：活动和错误消息
  
- **Room Parameters**: Room dimensions and T60 configuration
- **Source/Receiver Positions**: Text input for coordinate definition
- **Simulation Parameters**: Sampling rate, microphone patterns, attenuation settings
- **Control Buttons**: Simulate, visualize, and export functions
- **Progress Bar**: Real-time simulation progress
- **Status Log**: Activity and error messages

### Right Panel Visualization:
- **3D 房间布局**：房间几何形状的交互式 3D 可视化
- **RIR 图**：所有源-接收机 RIR 对的多子图显示
- **实时更新**：模拟后自动更新图
  
- **3D Room Layout**: Interactive 3D visualization of room geometry
- **RIR Plots**: Multi-subplot display of all source-receiver RIR pairs
- **Real-time Updates**: Automatic plot updates after simulation

## Features Explanation

### Room Impulse Response Simulation
GUI 利用 gpuRIR 的 GPU 加速图像源方法 (ISM) 来模拟真实的房间声学效果。模拟考虑了以下因素：
- 房间几何形状和边界条件
- 基于 T60 和吸收率的反射系数
- 多个声源和接收器位置
- 定向麦克风模式
  
The GUI leverages gpuRIR's GPU-accelerated Image Source Method (ISM) to simulate realistic room acoustics. The simulation accounts for:
- Room geometry and boundary conditions
- Reflection coefficients based on T60 and absorption
- Multiple source and receiver positions
- Directional microphone patterns

### Visualization
- **3D 房间布局**：显示房间边界、声源位置（红色圆圈）和接收器位置（蓝色三角形）
- **RIR 波形**：时域图显示从每个声源到每个接收器的脉冲响应
  
- **3D Room Layout**: Shows room boundaries, source positions (red circles), and receiver positions (blue triangles)
- **RIR Waveforms**: Time-domain plots showing the impulse response from each source to each receiver

### Export Options
- 将各个 RIR 通道导出为 WAV 文件
- 标准化输出以防止削波
- 与标准音频分析工具兼容
  
- Export individual RIR channels as WAV files
- Normalized output to prevent clipping
- Compatible with standard audio analysis tools

## Tips for Use
1. **位置验证**：确保所有声源和接收器都在房间边界内
2. **内存注意事项**：T60 时间较长的大房间可能需要大量的 GPU 内存
3. **采样率**：更高的采样率可提供更好的时间分辨率，但会增加计算时间
4. **麦克风模式**：
- “omni”：全向（所有方向灵敏度相同）
- “card”：心形指向（心形图案）
- "hypcard"：超心形指向（指向性比心形指向更强）
- "subcard"：亚心形指向（指向性比心形指向弱）
- "bidir"：双向指向（8字形图案）
  
1. **Position Validation**: Ensure all sources and receivers are within room boundaries
2. **Memory Considerations**: Large rooms with long T60 times may require significant GPU memory
3. **Sampling Rate**: Higher sampling rates provide better temporal resolution but increase computation time
4. **Microphone Patterns**: 
   - "omni": Omnidirectional (equal sensitivity in all directions)
   - "card": Cardioid (heart-shaped pattern)
   - "hypcard": Hypercardioid (more directional than cardioid)
   - "subcard": Subcardioid (less directional than cardioid)
   - "bidir": Bidirectional (figure-8 pattern)

## Troubleshooting

**Common Issues:**
- **GPU 内存错误**：减小房间大小、T60 或最大衰减
- **位置错误**：确认所有坐标均在房间边界内
- **导入错误**：确保所有必需的软件包均已安装
- **模拟卡顿**：检查 GPU 可用性和 CUDA 安装
  
- **GPU Memory Error**: Reduce room size, T60, or maximum attenuation
- **Position Errors**: Verify all coordinates are within room boundaries
- **Import Errors**: Ensure all required packages are installed
- **Simulation Hangs**: Check GPU availability and CUDA installation

**Performance Tips:**
- 对于兼容的 GPU（Pascal 或更高版本），请使用混合精度模式
- 启用 LUT（查找表）以加快 sinc 计算速度
- 从较小的房间和较短的 T60 时间开始测试
  
- Use mixed precision mode for compatible GPUs (Pascal or newer)
- Enable LUT (Look-Up Table) for faster sinc computations
- Start with smaller rooms and shorter T60 times for testing

## Technical Details
GUI 使用 PyQt5 作为界面，并使用 matplotlib 进行可视化。 RIR 仿真在单独线程中运行，以防止计算过程中 GUI 卡顿。该实现展示了 gpuRIR 的主要功能：
- GPU 加速 ISM 仿真
- 多源接收机配置
- 定向麦克风建模
- Sabine 混响时间估算
- 导出功能以供进一步分析

The GUI uses PyQt5 for the interface and matplotlib for visualization. RIR simulation runs in a separate thread to prevent GUI freezing during computation. The implementation demonstrates gpuRIR's key features:
- GPU-accelerated ISM simulation
- Multiple source-receiver configurations
- Directional microphone modeling
- Sabine reverberation time estimation
- Export capabilities for further analysis
## License
MIT
