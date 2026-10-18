# 🧠 多 Agent 协作深度研究系统 (Multi-Agent Researcher)

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-1.x-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.3-red.svg)

## 📖 项目简介
本项目是一个基于 **LangGraph** 构建的多智能体（Multi-Agent）协作系统。旨在解决单一 LLM 在面对复杂研究任务时容易“幻觉”且缺乏系统性规划的痛点。
系统模拟真实的学术/商业研究团队，通过有向图编排 **规划者 (Planner)**、**资料员 (Researcher)**、**撰稿人 (Writer)** 和 **审稿人 (Critic)** 四大角色，实现从任务拆解、全网搜索、内容撰写到自我反思与重构的完整闭环。

## ✨ 核心特性
- **多角色自主协作**：将复杂任务解耦，不同 Agent 拥有专属 System Prompt，各司其职。
- **反思与自修正循环 (Self-Reflection)**：利用 LangGraph 的条件边（Conditional Edge），审稿人若判定内容不达标，系统会自动打回撰稿人重写，直到满足质量要求或达到最大迭代次数。
- **真实联网搜索**：接入 **Tavily Search API**，确保研究基于真实的外部实时资讯。
- **强容错与防幻觉降级**：针对搜索 API 故障等异常情况，设计了强主题约束 Prompt 与降级机制，确保系统不会偏离研究主题。
- **全过程可视化**：基于 Streamlit 开发前端，实时动态展示各 Agent 的思考过程与协作流转日志。

## 🏗️ LangGraph 架构图

```mermaid
graph TD
    User((用户输入主题)) --> Planner[📝 规划者 Planner]
    Planner -->|"生成搜索词"| Researcher[🔍 资料员 Researcher]
    Researcher -->|"联网搜集真实资料"| Writer[✍️ 撰稿人 Writer]
    
    Writer -->|"提交初稿"| Critic[🧐 审稿人 Critic]
    
    Critic -->|"❌ 发现问题 (打回)"| Writer
    Critic -->|"✅ 审查通过 (PASS)"| End((输出最终报告))
    
    style Planner fill:#e1f5fe,stroke:#03a9f4
    style Researcher fill:#e8f5e9,stroke:#4caf50
    style Writer fill:#fff3e0,stroke:#ff9800
    style Critic fill:#ffebee,stroke:#f44336


📁 项目结构

```text
multi-agent-demo/
├── .env                # 密钥配置
├── app.py              # Streamlit 前端界面
├── graph.py            # LangGraph 有向图组装
├── nodes.py            # 四大 Agent 的具体实现
├── state.py            # 全局状态定义
├── requirements.txt    # 依赖清单
└── README.md
```

💡 开发心得与思考

1. 状态管理 (State) 是多 Agent 的核心：通过 TypedDict 定义全局状态，让所有 Agent 共享同一个“白板”，是让协作顺畅的关键。
2. 条件边 (Conditional Edge) 是灵魂：它打破了线性流程的限制，让系统具备了“打回重写”的动态路由能力。
3. 防范大模型“跑题”：在真实测试中，如果搜索失败返回空数据，撰稿人 Agent 极易将“信息缺失”写成哲学文章。通过在 Prompt 中加入强主题约束和降级指令，成功解决了这一工程痛点。

```
