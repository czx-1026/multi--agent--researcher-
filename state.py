from typing import TypedDict, List

class ResearchState(TypedDict):
    topic: str              # 研究主题
    queries: List[str]      # 搜索词列表
    research_data: str      # 搜到的资料
    draft: str              # 初稿
    critique: str           # 批评意见
    revision_count: int     # 修改次数（防止无限循环）