# -*- coding: utf-8 -*-
"""
测试客户端：通过 stdio 连接 smart_home_server.py，验证 MCP 三大原语全部可用。
运行：python test_client.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).parent / "smart_home_server.py"


def show(title: str, payload: str) -> None:
    print(f"\n=== {title} ===")
    try:
        data = json.loads(payload)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception:
        print(payload)


async def main() -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER)],
        cwd=str(SERVER.parent),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("[ok] 会话初始化完成")

            # 1. 工具注册情况
            tools = await session.list_tools()
            print("\n=== 注册的工具 ({} 个) ===".format(len(tools.tools)))
            for t in tools.tools:
                print(f"- {t.name}: {t.description.splitlines()[0]}")
            assert len(tools.tools) >= 10, "工具数量不足"

            # 2. 设备控制链路
            result = await session.call_tool("list_devices", {})
            show("list_devices（全屋设备）", result.content[0].text)
            assert "客厅灯" in result.content[0].text

            result = await session.call_tool("control_light", {"device": "客厅灯", "power": True, "brightness": 60})
            show("control_light（打开客厅灯，亮度 60）", result.content[0].text)
            assert '"power": true' in result.content[0].text

            result = await session.call_tool("control_ac", {"device": "客厅空调", "power": True, "temperature": 24.0})
            show("control_ac（开空调，24°C）", result.content[0].text)

            # 3. 一键场景（任务执行）
            result = await session.call_tool("run_scene", {"scene_name": "晚安"})
            show("run_scene（执行「晚安」场景）", result.content[0].text)
            assert '"status": "ok"' in result.content[0].text

            result = await session.call_tool("get_device_status", {"device": "客厅灯"})
            show("get_device_status（执行场景后客厅灯状态）", result.content[0].text)
            assert '"power": false' in result.content[0].text

            # 4. 任务管理
            result = await session.call_tool("add_task", {"title": "面试前完成 MCP demo 讲解", "priority": "high"})
            show("add_task（新增任务）", result.content[0].text)
            task_id = json.loads(result.content[0].text)["id"]

            result = await session.call_tool("list_tasks", {"status": "todo"})
            show("list_tasks（待办任务）", result.content[0].text)

            result = await session.call_tool("complete_task", {"task_id": task_id})
            show("complete_task（完成任务）", result.content[0].text)

            # 5. Resources
            res = await session.read_resource("home://devices")
            show("resource home://devices（全屋设备资源）", res.contents[0].text)
            assert "客厅灯" in res.contents[0].text

            res = await session.read_resource("home://scenes")
            show("resource home://scenes（场景配置资源）", res.contents[0].text)

            # 6. Prompts（角色提示词模板）
            prompt = await session.get_prompt("smart_home_manager", {"user_name": "小明"})
            text = prompt.messages[0].content.text
            print("\n=== prompt smart_home_manager（前 120 字） ===")
            print(text[:120].replace("\n", " ") + " ...")
            assert "小住" in text

            prompt = await session.get_prompt("voice_assistant", {"assistant_name": "小智", "user_name": "小明"})
            text = prompt.messages[0].content.text
            print("\n=== prompt voice_assistant（前 120 字） ===")
            print(text[:120].replace("\n", " ") + " ...")
            assert "打断" in text

    print("\n✅ 全部验证通过：tools / resources / prompts 均可用，Server 可正常运行。")


if __name__ == "__main__":
    asyncio.run(main())
