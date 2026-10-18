import os
from dotenv import load_dotenv
load_dotenv()
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from duckduckgo_search import DDGS
from state import ResearchState

llm = ChatOpenAI(model="deepseek-chat", temperature=0)

# 1. 规划者：拆解课题，生成搜索词
def planner_node(state: ResearchState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个高级研究员。请根据用户的研究主题，生成3个用于搜索的简短关键词。只输出关键词，用逗号分隔。"),
        ("human", "研究主题：{topic}")
    ])
    chain = prompt | llm
    result = chain.invoke({"topic": state["topic"]})
    queries = [q.strip() for q in result.content.split(",")]
    print(f"📝 [Planner] 生成搜索词: {queries}")
    return {"queries": queries}

# 2. 研究员：联网搜索，整理资料
def researcher_node(state: ResearchState):
    print("🔍 [Researcher] 正在联网搜索...")
    search_tool = TavilySearch(max_results=2)
    all_results = []
    
    for query in state["queries"]:
        try:
            results = search_tool.invoke({"query": query})
            for r in results:
                all_results.append(f"标题: {r['title']}\n摘要: {r['content']}\n")
        except Exception as e:
            print(f"搜索 '{query}' 时出错: {e}")
    
    if not all_results:
        all_results.append("未搜索到相关资料，请直接基于自身知识作答。")
    
    return {"research_data": "\n---\n".join(all_results)}

# 3. 写作者：根据资料写初稿，或根据批评意见重写
def writer_node(state: ResearchState):
    if state.get("critique"):
        print("✍️ [Writer] 正在根据审稿人意见修改...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业撰稿人。请根据审稿人的意见，修改这篇报告。"),
            ("human", "报告主题：{topic}\n\n资料：{data}\n\n初稿：{draft}\n\n审稿意见：{critique}")
        ])
        result = (prompt | llm).invoke({
            "topic": state["topic"],
            "data": state["research_data"], 
            "draft": state["draft"], 
            "critique": state["critique"]
        })
        return {"draft": result.content, "critique": ""} 
    else:
        print("✍️ [Writer] 正在撰写初稿...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业撰稿人。请务必围绕【用户给定的主题】撰写一篇逻辑清晰的深度报告。\n\n【注意】：如果资料显示“未搜索到相关资料”，请直接基于你自身的庞大知识库，围绕【用户给定的主题】进行撰写，绝对不要偏离主题去探讨所谓的“信息缺失”问题！"),
            ("human", "用户给定的主题：{topic}\n\n资料：{data}")
        ])
        result = (prompt | llm).invoke({
            "topic": state["topic"],
            "data": state["research_data"]
        })
        return {"draft": result.content}

# 4. 审稿人：挑刺，决定是否打回重写
def critic_node(state: ResearchState):
    print("🧐 [Critic] 正在审稿...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个严苛的审稿人。请审查这份初稿。\n1. 检查它是否紧紧围绕用户给定的主题。如果它跑题了，请严厉指出并打回。\n2. 如果内容充实、逻辑通顺且紧扣主题，请回复'PASS'。\n如果存在问题，请详细指出修改意见（不要回复PASS）。"),
        ("human", "用户给定的主题：{topic}\n\n初稿：{draft}")
    ])
    result = (prompt | llm).invoke({
        "topic": state["topic"],
        "draft": state["draft"]
    })
    critique = result.content
    
    if "PASS" in critique:
        print("✅ [Critic] 质量合格，通过！")
        return {"critique": ""}
    else:
        print(f"❌ [Critic] 发现问题，打回重写: {critique[:50]}...")
        count = state.get("revision_count", 0) + 1
        return {"critique": critique, "revision_count": count}