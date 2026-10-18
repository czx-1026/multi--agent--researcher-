from langgraph.graph import StateGraph, END
from state import ResearchState
from nodes import planner_node, researcher_node, writer_node, critic_node

# 初始化状态图
workflow = StateGraph(ResearchState)

# 1. 添加节点
workflow.add_node("planner", planner_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.add_node("critic", critic_node)

# 2. 设置入口点
workflow.set_entry_point("planner")

# 3. 添加顺序边（单向箭头的流向）
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "critic")

# 4. 【核心】定义条件路由逻辑
def route_after_critic(state: ResearchState):
    """审稿后的路由判断：通过则结束，不通过且次数未满则打回重写"""
    # 如果重写次数达到 2 次，强制结束（防止死循环）
    if state.get("revision_count", 0) >= 2:
        print("⚠️ 达到最大修改次数，强制结案。")
        return "end"
    
    # 如果 critique 为空，说明上一步 critic 返回了 PASS
    if not state.get("critique"):
        return "end"
    
    # 否则打回重写
    return "rewrite"

# 5. 绑定条件边
workflow.add_conditional_edges(
    "critic",
    route_after_critic,
    {
        "end": END,          # 如果返回 "end"，走向结束
        "rewrite": "writer"  # 如果返回 "rewrite"，画一条线指回 writer 节点
    }
)

# 编译图，生成可执行的 App
app_graph = workflow.compile()