from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import logging
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

router = APIRouter()
logger = logging.getLogger(__name__)

class Message(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    messages: List[Message]
    
SYSTEM_PROMPT = """You are an expert Indian Campus Placement Advisor for tech roles. 
Your job is to answer student queries about resumes, interviews, ATS scoring, and skill gaps realistically and concisely.
Keep your answers brief, encouraging, and focused entirely on software engineering placements in India (both product-based like Amazon/Microsoft and service-based like TCS/Infosys).

CRITICAL FORMATTING RULES:
1. DO NOT use markdown bolding (**text**) or italics (*text*). Do not output a single asterisk anywhere.
2. If you need to provide a list, use standard numbers (1., 2.) or simple hyphens (-) with clean line breaks.
3. Keep the output as clean plain text that is easy to read.

If asked about something unrelated to careers, politely guide the conversation back to placements."""

@router.post("/chat/")
async def chat_endpoint(request: ChatRequest):
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="Empty message list")
            
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable not set")
            
        # Initialize Groq client
        llm = ChatGroq(temperature=0.7, model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key)
        
        # Convert history format
        langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        
        for msg in request.messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
                
        # Get response
        response = llm.invoke(langchain_messages)
        
        return {"response": response.content}
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
