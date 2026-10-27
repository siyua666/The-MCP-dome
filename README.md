# The-MCP-dome · AI 智能体面试实战作品集

面向 AI 智能体方向求职的实战作品集：一个**能跑的 MCP Server demo** + 一套**可直接使用的角色提示词案例**。
设计贴合智能家居 / IoT 智能体 / 对话智能体 / 任务执行智能体的招聘方向（对应小智、涂鸦等生态）。

## 仓库内容

| 路径 | 说明 |
| --- | --- |
| `mcp-demo/` | 智能家居助手 MCP Server（Python），覆盖 MCP 三大原语 tools / resources / prompts，含自动验证脚本 |
| `角色提示词案例集.md` | 3 个高质量角色提示词案例：智能家居管家、语音口语陪练、任务执行助手，含设计拆解与调参建议 |

## 作品一：智能家居助手 MCP Server

一个基于 [MCP（Model Context Protocol）](https://modelcontextprotocol.io) 的可运行 Server，演示模型如何通过标准协议调用外部能力。数据为内存模拟（重启重置），用于演示与面试讲解。

- **技术栈**：Python 3.10+ · MCP Python SDK（mcp 1.x，FastMCP 经典 API）
- **覆盖三大原语**：
  - **tools（10 个）**：设备控制（灯光/空调/窗帘）、一键场景执行（晚安/回家/离家，多设备编排）、任务管理（增/查/完成）
  - **resources（2 个）**：`home://devices` 全屋设备清单、`home://scenes` 场景配置
  - **prompts（2 个）**：智能家居管家、语音助手角色模板

### 环境要求与安装

- Python 3.10+
- 安装依赖：

```bash
pip install "mcp>=1.0,<2"
```

> 注意：请使用 mcp 1.x（FastMCP 经典 API，社区教程主流写法）；mcp 2.x 已改名 MCPServer，写法不同。

### 运行与验证

```bash
cd mcp-demo
python test_client.py          # 自动验证三大原语（输出：全部验证通过）
python smart_home_server.py    # 以 stdio 启动 Server，可接入任意 MCP 客户端
```

`test_client.py` 输出应包含：`✅ 全部验证通过：tools / resources / prompts 均可用`。

### 功能清单

| 类型 | 名称 | 说明 |
| --- | --- | --- |
| tool | `list_devices` | 列出设备（可按房间过滤） |
| tool | `get_device_status` | 查询单设备状态 |
| tool | `control_light` | 灯光：开关 / 亮度 0-100 / 色温 2700-6500K |
| tool | `control_ac` | 空调：开关 / 16-30°C / 模式 |
| tool | `control_curtain` | 窗帘开合 0-100 |
| tool | `list_scenes` | 列出可执行场景 |
| tool | `run_scene` | 一键场景（晚安 / 回家 / 离家），一次编排多设备动作 |
| tool | `add_task` | 新增任务（优先级 / 截止时间） |
| tool | `list_tasks` | 任务列表（按状态过滤） |
| tool | `complete_task` | 完成任务 |
| resource | `home://devices` | 全屋设备与状态（JSON） |
| resource | `home://scenes` | 场景配置（JSON） |
| prompt | `smart_home_manager` | 智能家居管家角色模板（可传用户名） |
| prompt | `voice_assistant` | 语音助手角色模板（唤醒 / 打断 / TTS 约束） |

### 接入任意 MCP 客户端

以 stdio 方式把本 Server 注册为外部工具即可（示例：Claude Desktop / Cursor / Dify / Cherry Studio 等支持 MCP 的客户端）：

```json
{
  "mcpServers": {
    "smart-home-assistant": {
      "command": "python",
      "args": ["<仓库根绝对路径>/mcp-demo/smart_home_server.py"]
    }
  }
}
```

接入后即可让对话模型调用设备控制、场景执行、任务管理工具，并在会话中调用两个角色提示词模板。

## 作品二：角色提示词案例集

三个可直接复制使用的完整角色提示词，每个都包含 System Prompt 全文、设计拆解表和面试讲解点：

1. **智能家居管家「小住」** —— 意图理解 + 安全执行 + 语音友好输出（贴合 IoT 智能家居方向）
2. **语音口语陪练「Mia」** —— 纠错节奏、打断、总结等交互协议（贴合语音对话方向）
3. **任务执行助手「阿成」** —— 拆解 → 确认 → 汇报的执行闭环（贴合任务执行智能体方向）

详细内容见 [`角色提示词案例集.md`](角色提示词案例集.md)。

## 面试讲解思路（3 分钟版）

1. **讲清 MCP 是什么**：Anthropic 2024 年发布的开源标准，统一大模型与外部工具 / 数据 / 上下文的连接方式，被称为 "AI 的 USB-C"。
2. **讲清三大原语**：tools（模型可调用的能力）、resources（模型可读取的上下文）、prompts（可复用的提示词模板）—— 本项目各实现了一套。
3. **讲一个完整场景**：用户说 "我准备睡了" → 模型调用 `run_scene("晚安")` → 一次编排灯、窗帘多个动作 → 返回执行结果，体现 "任务执行智能体" 的规划与执行。
4. **讲角色提示词**：`smart_home_manager` 模板里写了 "意图理解 + 安全确认 + 语音友好输出" 三层规则（详见《角色提示词案例集》）。
5. **讲后续可扩展**：接入真实设备 API（涂鸦云）、加流式语音链路（ASR→LLM→TTS，对应小智场景）、换 SSE/HTTP 传输。

## 目录

```
.
├── mcp-demo/
│   ├── smart_home_server.py   # MCP Server 主代码
│   ├── test_client.py         # 验证客户端（stdio 连接，逐项验证）
│   └── requirements.txt
├── 角色提示词案例集.md
├── README.md                  # 本文件
└── .gitignore
```

## 说明

- demo 数据为内存模拟（重启重置），用于演示与面试讲解；可在此基础上扩展真实设备 API、语音链路（ASR → LLM → TTS）、SSE/HTTP 传输。
