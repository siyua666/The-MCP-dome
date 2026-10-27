# The-MCP-dome · AI 智能体面试实战作品集

面向 AI 智能体方向求职的实战作品集：一个**能跑的 MCP Server demo** + 一套**可直接使用的角色提示词案例**。
设计贴合智能家居 / IoT 智能体 / 对话智能体 / 任务执行智能体的招聘方向（对应小智、涂鸦等生态）。

## 仓库内容

| 路径 | 说明 |
| --- | --- |
| `mcp-demo/` | 智能家居助手 MCP Server（Python），覆盖 MCP 三大原语 tools / resources / prompts，含自动验证脚本 |
| `角色提示词案例集.md` | 3 个高质量角色提示词案例：智能家居管家、语音口语陪练、任务执行助手，含设计拆解与调参建议 |

## 作品一：智能家居助手 MCP Server

一个基于 [MCP（Model Context Protocol）](https://modelcontextprotocol.io) 的可运行 Server，演示模型如何通过标准协议调用外部能力。

- **技术栈**：Python 3.10+ · MCP Python SDK（mcp 1.x，FastMCP 经典 API）
- **覆盖三大原语**：
  - **tools（10 个）**：设备控制（灯光/空调/窗帘）、一键场景执行（晚安/回家/离家，多设备编排）、任务管理（增/查/完成）
  - **resources（2 个）**：`home://devices` 全屋设备清单、`home://scenes` 场景配置
  - **prompts（2 个）**：智能家居管家、语音助手角色模板
- **快速开始**：

  ```bash
  cd mcp-demo
  pip install "mcp>=1.0,<2"     # 需 Python 3.10+
  python test_client.py          # 自动验证三大原语（输出：全部验证通过）
  python smart_home_server.py    # 以 stdio 启动 Server，可接入任意 MCP 客户端
  ```

- 详细说明见 [`mcp-demo/README.md`](mcp-demo/README.md)。

## 作品二：角色提示词案例集

三个可直接复制使用的完整角色提示词，每个都包含 System Prompt 全文、设计拆解表和面试讲解点：

1. **智能家居管家「小住」** —— 意图理解 + 安全执行 + 语音友好输出（贴合 IoT 智能家居方向）
2. **语音口语陪练「Mia」** —— 纠错节奏、打断、总结等交互协议（贴合语音对话方向）
3. **任务执行助手「阿成」** —— 拆解 → 确认 → 汇报的执行闭环（贴合任务执行智能体方向）

详细内容见 [`角色提示词案例集.md`](角色提示词案例集.md)。

## 设计思路（面试 3 分钟版）

1. **讲清 MCP**：Anthropic 2024 年发布的开源标准，统一大模型与外部工具/数据/上下文的连接，被称为"AI 的 USB-C"。
2. **讲清三大原语**：tools（能力）、resources（上下文）、prompts（可复用模板）——本项目各实现了一套。
3. **讲一个完整场景**：用户说"我准备睡了" → 模型调用 `run_scene("晚安")` → 一次编排灯、窗帘多个动作 → 返回执行结果，体现"任务执行智能体"的规划与执行。
4. **讲角色提示词**：提示词里写的是"先查询、再执行、后确认"的行为规则，而不只是人设描写——这是与普通聊天 prompt 的本质区别。

## 目录

```
.
├── mcp-demo/
│   ├── smart_home_server.py   # MCP Server 主代码
│   ├── test_client.py         # 验证客户端（stdio 连接，逐项验证）
│   ├── requirements.txt
│   └── README.md
├── 角色提示词案例集.md
├── README.md                  # 本文件
└── .gitignore
```

## 说明

- demo 数据为内存模拟（重启重置），用于演示与面试讲解；可在此基础上扩展真实设备 API、语音链路（ASR → LLM → TTS）、SSE/HTTP 传输。
