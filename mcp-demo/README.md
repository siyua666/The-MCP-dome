# 智能家居助手 MCP Server（面试实战作品）

一个**能跑的** MCP（Model Context Protocol）Server demo，覆盖协议三大原语：
**tools（设备控制 / 一键场景 / 任务管理）· resources（设备与场景清单）· prompts（角色提示词模板）**。

设计贴合目标公司方向：智能家居/IoT 智能体（对应涂鸦生态）+ 任务执行智能体 + 对话智能体（对应小智生态）。
数据为内存模拟（重启重置），用于演示与面试讲解。

## 目录结构

```
mcp-demo/
├── smart_home_server.py   # MCP Server 主代码（Python + MCP SDK）
├── test_client.py         # 验证客户端：stdio 连接并逐项验证三大原语
├── requirements.txt       # 依赖清单
└── README.md              # 本文件
```

## 环境要求与安装

- Python 3.10+
- 安装依赖：

```bash
pip install "mcp>=1.0,<2"
```

> 注意：请使用 mcp 1.x（FastMCP 经典 API，社区教程主流写法）；mcp 2.x 已改名 MCPServer，写法不同。

## 运行与验证

```bash
# 启动 Server（stdio 传输，等待 MCP 客户端连接）
python smart_home_server.py

# 运行自动验证（连接 Server，逐项调用工具/资源/提示词）
python test_client.py
```

`test_client.py` 输出应包含：`✅ 全部验证通过：tools / resources / prompts 均可用`。

## 功能清单

| 类型 | 名称 | 说明 |
| --- | --- | --- |
| tool | `list_devices` | 列出设备（可按房间过滤） |
| tool | `get_device_status` | 查询单设备状态 |
| tool | `control_light` | 灯光：开关 / 亮度 0-100 / 色温 2700-6500K |
| tool | `control_ac` | 空调：开关 / 16-30°C / 模式 |
| tool | `control_curtain` | 窗帘开合 0-100 |
| tool | `list_scenes` | 列出可执行场景 |
| tool | `run_scene` | 一键场景（晚安/回家/离家），一次编排多设备动作 |
| tool | `add_task` | 新增任务（优先级 / 截止时间） |
| tool | `list_tasks` | 任务列表（按状态过滤） |
| tool | `complete_task` | 完成任务 |
| resource | `home://devices` | 全屋设备与状态（JSON） |
| resource | `home://scenes` | 场景配置（JSON） |
| prompt | `smart_home_manager` | 智能家居管家角色模板（可传用户名） |
| prompt | `voice_assistant` | 语音助手角色模板（唤醒 / 打断 / TTS 约束） |

## 接入任意 MCP 客户端

以 stdio 方式把本 Server 注册为外部工具即可（示例：Claude Desktop / Cursor / Dify / Cherry Studio 等支持 MCP 的客户端）：

```json
{
  "mcpServers": {
    "smart-home-assistant": {
      "command": "python",
      "args": ["<本目录绝对路径>/smart_home_server.py"]
    }
  }
}
```

接入后即可让对话模型调用设备控制、场景执行、任务管理工具，并在会话中调用两个角色提示词模板。

## 面试讲解要点（3 分钟版）

1. **讲清 MCP 是什么**：Anthropic 2024 年发布的开源标准，统一大模型与外部工具/数据/上下文的连接方式，被称为"AI 的 USB-C"。
2. **讲清三大原语**：tools（模型可调用的能力）、resources（模型可读取的上下文）、prompts（可复用的提示词模板）——本项目各实现了一套。
3. **讲一个完整场景**：用户说"我准备睡了" → 模型调用 `run_scene("晚安")` → 一次编排灯、窗帘多个动作 → 返回执行结果。体现"任务执行智能体"的规划与执行。
4. **讲角色提示词**：`smart_home_manager` 模板里写了"意图理解 + 安全确认 + 语音友好输出"三层规则（详见《角色提示词案例集》）。
5. **讲后续可扩展**：接入真实设备 API（涂鸦云）、加流式语音链路（ASR→LLM→TTS，对应小智场景）、换 SSE/HTTP 传输。
