# -*- coding: utf-8 -*-
"""
智能家居助手 MCP Server —— 面试实战作品 demo

覆盖 MCP（Model Context Protocol）三大原语：
- tools     : 设备控制（灯/空调/窗帘）、一键场景执行、任务管理（贴合"任务执行智能体"方向）
- resources : home://devices 全屋设备清单、home://scenes 场景配置
- prompts   : 角色提示词模板（智能家居管家 / 语音助手），与"角色提示词案例集"呼应

运行方式：
    python smart_home_server.py
（默认以 stdio 传输启动，可被任意 MCP 客户端连接）

数据为内存模拟，重启后重置，仅供演示。
"""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

# 压掉 SDK 的请求日志（默认打到 stderr），保持演示输出干净
logging.getLogger("mcp").setLevel(logging.ERROR)

mcp = FastMCP("smart-home-assistant")


# ---------------------------------------------------------------------------
# 模拟数据（内存态，重启重置）
# ---------------------------------------------------------------------------
DEVICES: dict[str, dict[str, Any]] = {
    "客厅灯":   {"type": "light",   "room": "客厅", "power": False, "brightness": 80, "color_temp": 4000},
    "卧室灯":   {"type": "light",   "room": "卧室", "power": False, "brightness": 60, "color_temp": 3500},
    "客厅空调": {"type": "ac",      "room": "客厅", "power": False, "temperature": 26.0, "mode": "cool"},
    "卧室空调": {"type": "ac",      "room": "卧室", "power": False, "temperature": 26.0, "mode": "cool"},
    "客厅窗帘": {"type": "curtain", "room": "客厅", "open_percent": 100},
    "卧室窗帘": {"type": "curtain", "room": "卧室", "open_percent": 0},
}

# 一键场景：一次编排多个设备动作，演示"任务执行智能体"的规划与执行
SCENES: dict[str, list[dict[str, Any]]] = {
    "晚安": [
        {"device": "客厅灯",   "action": {"power": False}},
        {"device": "卧室灯",   "action": {"power": False}},
        {"device": "客厅窗帘", "action": {"open_percent": 0}},
        {"device": "卧室窗帘", "action": {"open_percent": 0}},
    ],
    "回家": [
        {"device": "客厅灯",   "action": {"power": True, "brightness": 80}},
        {"device": "客厅空调", "action": {"power": True, "temperature": 25.0}},
    ],
    "离家": [
        {"device": "客厅灯",   "action": {"power": False}},
        {"device": "卧室灯",   "action": {"power": False}},
        {"device": "客厅空调", "action": {"power": False}},
        {"device": "卧室空调", "action": {"power": False}},
        {"device": "客厅窗帘", "action": {"open_percent": 100}},
    ],
}

TASKS: dict[str, dict[str, Any]] = {}
_TASK_SEQ: list[int] = [0]


def _next_task_id() -> str:
    _TASK_SEQ[0] += 1
    return f"T{_TASK_SEQ[0]:03d}"


def _apply_action(device: str, action: dict[str, Any]) -> dict[str, Any]:
    """把动作应用到设备，返回设备最新状态。"""
    dev = DEVICES.get(device)
    if not dev:
        raise ValueError(f"未知设备: {device}，可用设备请调用 list_devices")
    for k, v in action.items():
        if k not in dev:
            raise ValueError(f"设备 {device} 不支持属性 {k}")
        dev[k] = v
    return dict(dev)


# ---------------------------------------------------------------------------
# Tools：设备控制
# ---------------------------------------------------------------------------
@mcp.tool()
def list_devices(room: str | None = None) -> str:
    """列出全部设备（可按房间过滤），返回 JSON 字符串。"""
    items = [{"name": name, **dev} for name, dev in DEVICES.items()
             if room is None or dev["room"] == room]
    return json.dumps(items, ensure_ascii=False, indent=2)


@mcp.tool()
def get_device_status(device: str) -> str:
    """查询单个设备的当前状态。"""
    dev = DEVICES.get(device)
    if not dev:
        raise ValueError(f"未知设备: {device}")
    return json.dumps({"name": device, **dev}, ensure_ascii=False, indent=2)


@mcp.tool()
def control_light(device: str, power: bool | None = None,
                  brightness: int | None = None,
                  color_temp: int | None = None) -> str:
    """控制灯光设备：power 开关；brightness 亮度 0-100；color_temp 色温 2700-6500K。未传的属性保持不变。"""
    if device not in DEVICES or DEVICES[device]["type"] != "light":
        raise ValueError(f"设备 {device} 不是灯光设备")
    if brightness is not None and not (0 <= brightness <= 100):
        raise ValueError("亮度需在 0-100 之间")
    if color_temp is not None and not (2700 <= color_temp <= 6500):
        raise ValueError("色温需在 2700-6500K 之间")
    action = {k: v for k, v in {"power": power, "brightness": brightness,
                                "color_temp": color_temp}.items() if v is not None}
    dev = _apply_action(device, action)
    return json.dumps({"name": device, **dev}, ensure_ascii=False, indent=2)


@mcp.tool()
def control_ac(device: str, power: bool | None = None,
               temperature: float | None = None,
               mode: str | None = None) -> str:
    """控制空调设备：power 开关；temperature 目标温度 16-30°C；mode 模式(cool/heat/fan/auto)。未传的属性保持不变。"""
    if device not in DEVICES or DEVICES[device]["type"] != "ac":
        raise ValueError(f"设备 {device} 不是空调设备")
    if temperature is not None and not (16 <= temperature <= 30):
        raise ValueError("温度需在 16-30°C 之间")
    if mode is not None and mode not in ("cool", "heat", "fan", "auto"):
        raise ValueError("mode 需为 cool/heat/fan/auto")
    action = {k: v for k, v in {"power": power, "temperature": temperature,
                                "mode": mode}.items() if v is not None}
    dev = _apply_action(device, action)
    return json.dumps({"name": device, **dev}, ensure_ascii=False, indent=2)


@mcp.tool()
def control_curtain(device: str, open_percent: int) -> str:
    """控制窗帘开合度 0-100（0 全关，100 全开）。"""
    if device not in DEVICES or DEVICES[device]["type"] != "curtain":
        raise ValueError(f"设备 {device} 不是窗帘设备")
    if not (0 <= open_percent <= 100):
        raise ValueError("开合度需在 0-100 之间")
    dev = _apply_action(device, {"open_percent": open_percent})
    return json.dumps({"name": device, **dev}, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tools：场景执行与任务管理（任务执行智能体）
# ---------------------------------------------------------------------------
@mcp.tool()
def list_scenes() -> str:
    """列出所有可用的一键场景。"""
    return json.dumps(list(SCENES.keys()), ensure_ascii=False, indent=2)


@mcp.tool()
def run_scene(scene_name: str) -> str:
    """执行一键场景（如 晚安/回家/离家），一次编排多个设备动作，返回每个动作的执行结果。"""
    if scene_name not in SCENES:
        raise ValueError(f"未知场景: {scene_name}，可用场景请调用 list_scenes")
    results = []
    for step in SCENES[scene_name]:
        try:
            state = _apply_action(step["device"], step["action"])
            results.append({"device": step["device"], "status": "ok", "state": state})
        except ValueError as exc:
            results.append({"device": step["device"], "status": "failed", "error": str(exc)})
    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
def add_task(title: str, due_date: str | None = None, priority: str = "medium") -> str:
    """新增一条任务，返回任务信息与任务 ID。priority: high/medium/low。"""
    if priority not in ("high", "medium", "low"):
        raise ValueError("priority 需为 high/medium/low")
    task_id = _next_task_id()
    TASKS[task_id] = {"id": task_id, "title": title, "due_date": due_date,
                      "priority": priority, "status": "todo"}
    return json.dumps(TASKS[task_id], ensure_ascii=False, indent=2)


@mcp.tool()
def list_tasks(status: str | None = None) -> str:
    """列出任务，可按状态过滤（todo/done）。"""
    items = [t for t in TASKS.values() if status is None or t["status"] == status]
    return json.dumps(items, ensure_ascii=False, indent=2)


@mcp.tool()
def complete_task(task_id: str) -> str:
    """将指定任务标记为完成。"""
    if task_id not in TASKS:
        raise ValueError(f"未知任务: {task_id}")
    TASKS[task_id]["status"] = "done"
    return json.dumps(TASKS[task_id], ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Resources：可被客户端读取的上下文资源
# ---------------------------------------------------------------------------
@mcp.resource("home://devices")
def all_devices() -> str:
    """全屋设备清单与当前状态（JSON）。"""
    return json.dumps(DEVICES, ensure_ascii=False, indent=2)


@mcp.resource("home://scenes")
def all_scenes() -> str:
    """全部一键场景的配置（JSON）。"""
    return json.dumps(SCENES, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Prompts：角色提示词模板（与"角色提示词案例集"呼应，可在支持 MCP 的客户端里直接调用）
# ---------------------------------------------------------------------------
@mcp.prompt()
def smart_home_manager(user_name: str = "用户") -> str:
    """智能家居管家角色提示词模板：传入用户名，生成一位懂设备、会安排的家居管家人设。"""
    return f"""你叫"小住"，是{user_name}的专属智能家居管家，负责管理全屋灯光、空调、窗帘和日常家务任务。

【人设与语气】
- 温和、细致、行动力强，说话简洁口语化，一次只推进一件事。
- 把{user_name}当家人相处，主动记住 TA 的习惯，但不过度热情。

【能力与工具】
- 你拥有全屋设备控制、一键场景执行和任务管理能力，使用工具时遵循"先查询、再执行、后确认"。
- 用户只说意图时（如"有点冷"），先判断合理的设备动作，执行后简短说明做了什么、为什么。

【行为规则】
1. 每次动手前先确认设备存在且状态合理，执行后向用户复述结果。
2. 涉及安全或不确定的动作（如离家关闭所有设备）先向用户确认。
3. 不编造不存在的设备或功能，查询不到就如实说明。
4. 回答控制在 2 句以内，口语化，适合语音播报。"""


@mcp.prompt()
def voice_assistant(assistant_name: str = "小智", user_name: str = "用户") -> str:
    """语音助手角色提示词模板：面向语音交互场景（唤醒、打断、口语化输出）。"""
    return f"""你是{assistant_name}，一台正在与{user_name}进行语音对话的 AI 语音助手。

【交互约束】
- 输出必须简短口语化，适合 TTS 朗读，默认不超过 2 句话。
- 回答先直接给结论，再补一句必要信息；不输出 Markdown、列表或表情符号。
- 被"打断"时（用户中途插话）立刻停止当前内容，先回应新的请求。
- 唤醒词为"你好{assistant_name}"，被唤醒后进入待命状态。

【人设】
- 声音亲切但克制，像一位懂技术的家人，不卖萌、不啰嗦。
- 不知道的答案直说"这个我还不会，可以帮你记下来去查"，绝不编造。"""


if __name__ == "__main__":
    # 默认 stdio 传输，可被任意 MCP 客户端（Claude Desktop、Cursor、Dify 等）连接
    mcp.run(transport="stdio")
