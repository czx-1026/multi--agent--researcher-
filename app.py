import streamlit as st
from graph import app_graph

st.set_page_config(page_title="多Agent深度研究系统", page_icon="🧠", layout="wide")
st.title("🧠 多 Agent 协作深度研究系统")
st.caption("规划者 -> 资料员 -> 撰稿人 -> 审稿人，全流程自主协作与自我修正")

topic = st.text_input("请输入你要研究的主题：", placeholder="例如：人工智能在医疗领域的应用现状与挑战")

if st.button("🚀 开始研究", type="primary"):
    if not topic:
        st.warning("请先输入主题！")
    else:
        # 初始化全局状态
        initial_state = {
            "topic": topic,
            "queries": [],
            "research_data": "",
            "draft": "",
            "critique": "",
            "revision_count": 0
        }
        
        with st.spinner("Agent 团队正在开会研究中，请稍候..."):
            # 使用 stream 模式，实时捕获每个节点的执行结果
            for event in app_graph.stream(initial_state):
                for node_name, state_update in event.items():
                    # 根据节点名字展示对应的过程
                    if node_name == "planner":
                        queries = state_update.get("queries", [])
                        st.info(f"📝 **规划者 (Planner)**：将任务拆解为搜索词 `{queries}`")
                        
                    elif node_name == "researcher":
                        data_length = len(state_update.get("research_data", ""))
                        st.success(f"🔍 **资料员 (Researcher)**：完成联网搜索，整理出 {data_length} 字的参考资料。")
                        
                    elif node_name == "writer":
                        st.warning("✍️ **撰稿人 (Writer)**：正在奋笔疾书，提交了一版稿件...")
                        with st.expander("查看当前草稿"):
                            st.write(state_update.get("draft", ""))
                            
                    elif node_name == "critic":
                        critique = state_update.get("critique")
                        count = state_update.get("revision_count", 0)
                        if not critique:
                            st.success("🧐 **审稿人 (Critic)**：审查通过！稿件非常完美。")
                        else:
                            st.error(f"🧐 **审稿人 (Critic)** 提出了批评（第 {count} 次打回）：\n\n{critique}")
        
        # 获取最终的结果
        final_state = app_graph.invoke(initial_state)
        st.markdown("---")
        st.markdown("### 📄 最终研究报告")
        st.markdown(final_state["draft"])