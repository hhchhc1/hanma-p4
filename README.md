# 悍马 P4 — 智能家居边缘控制终端 🏠

基于乐鑫 ESP32-P4 的智能家居边缘控制终端，集成 AI 语音交互、传感器监控、家居设备控制、安防告警等功能。

## 硬件架构

```
┌─────────────────────────────┐
│   ESP32-P4 (主控)           │
│   • MIPI DSI 触控屏         │
│   • MIPI CSI 摄像头         │
│   • ES8311 音频编解码器      │
│   • DHT22 温湿度传感器       │
│   • BH1750 光照传感器        │
│   • EC11 旋转编码器          │
└────────────┬────────────────┘
             │ WiFi / LAN
    ┌────────┴────────┐
    │                 │
┌───┴──────────┐  ┌──┴───────────┐
│ ESP32-C3     │  │ 云端 AI 服务  │
│ 传感器节点    │  │ (WebSocket /  │
│ • DHT22      │  │  MQTT+UDP)   │
│ • BH1750     │  │              │
└──────────────┘  └──────────────┘
```

## 功能特性

### 🤖 AI 语音交互
- WebSocket / MQTT+UDP 双协议对接云端大模型
- 流式 ASR + LLM + TTS 全双工语音交互
- 离线语音唤醒（ESP-SR）
- MCP（Model Context Protocol）标准化调用接口，AI 可控硬件
- OPUS 音频编解码

### 🏠 智能家居控制
- LVGL 9.3 多页面触控 UI（聊天、家居控制、传感曲线、天气）
- SoftAP 网页服务器 — 手机浏览器即可控制设备
- GPIO 控制风扇、灯光等家居设备
- MCP 协议支持 AI 自动控制

### 📊 环境监测
- 本地 DHT22 + BH1750 传感器采集
- 远端 ESP32-C3 节点通过 HTTP 上报异地数据
- 温湿度、光照历史曲线展示
- 定时语音播报当前环境数据

### 📷 安防监控
- MIPI CSI 摄像头支持
- 帧差法移动侦测 + 肤色检测
- 异常移动声光告警
- 本地 PCM 语音警示

### 🔧 系统功能
- OTA 远程固件升级
- 本地 PCM 语音播报（温度、湿度、提醒等）
- 定时提醒功能
- 多语言支持

## 开发环境

- **框架**: ESP-IDF 5.5+
- **UI 库**: LVGL 9.3
- **芯片**: ESP32-P4（主控）+ ESP32-C3（传感器节点）
- **编译器**: GCC (xtensa-esp / riscv32-esp)
- **推荐 IDE**: VSCode + ESP-IDF 插件

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/hhchhc1/hanma-p4.git
cd hanma-p4
```

### 2. 设置 ESP-IDF 环境

```bash
# 安装 ESP-IDF v5.5 或更高版本
# 参考: https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/
```

### 3. 编译 P4 主控固件

```bash
idf.py set-target esp32p4
idf.py build
idf.py flash
```

### 4. 编译 C3 传感器节点

```bash
cd c3_sensor_node
idf.py set-target esp32c3
idf.py build
idf.py flash
```

## 项目结构

```
hanma-p4/
├── main/                     # P4 主控代码
│   ├── application.cc/.h     # 核心应用逻辑
│   ├── boards/wks-p4-cb/     # 自定义 P4 开发板
│   ├── display/              # 显示子系统 (LVGL)
│   │   └── extra_screens.cc  # 智能家居自定义页面
│   ├── audio/                # 音频子系统
│   ├── protocols/            # 通信协议 (WebSocket/MQTT)
│   ├── camera/               # 摄像头驱动
│   ├── sensors/              # 传感器驱动 (DHT22/BH1750)
│   ├── input/ec11.cc         # 旋转编码器驱动
│   ├── mcp_server.cc         # MCP 服务
│   ├── smart_home_web_server.cc  # 智能家居 Web 服务
│   └── assets/               # 音频资源
├── c3_sensor_node/           # C3 传感器节点
├── partitions/               # 分区表
├── scripts/                  # 构建/工具脚本
└── docs/                     # 文档
```

## 基于项目

本项目基于 [小智 AI 聊天机器人](https://github.com/78/xiaozhi-esp32) 开发，在其优秀的 AI 语音交互框架基础上，扩展了智能家居边缘控制、环境传感、安防监控等功能。

## 许可证

本项目基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。
