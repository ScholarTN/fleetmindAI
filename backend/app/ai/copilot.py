from sqlalchemy.ext.asyncio import AsyncSession
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.ai.prompts import SYSTEM_PROMPT
from app.ai.tools import DatabaseTools

from app.core.config import settings


class FleetCopilot:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.tools = DatabaseTools(db)

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0,
        )

    async def chat(self, question: str) -> str:

        # ----------------------------
        # Database Context
        # ----------------------------

        available_drivers = await self.tools.get_available_drivers()
        pending_loads = await self.tools.get_pending_loads()
        recent_incidents = await self.tools.get_recent_incidents()

        database_context = f"""
Available Drivers: {len(available_drivers)}

Pending Loads: {len(pending_loads)}

Recent Incidents: {len(recent_incidents)}
"""

        # ----------------------------
        # Knowledge Base Context
        # ----------------------------

       # rag = similarity_search(question, n_results=5)

       # documents = rag["documents"][0] if rag["documents"] else []

        knowledge_context = ""

        # ----------------------------
        # Final Prompt
        # ----------------------------

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=f"""
Database Context

{database_context}


Knowledge Base

{knowledge_context}


User Question

{question}
"""
            ),
        ]

        response = await self.llm.ainvoke(messages)

        return response.content