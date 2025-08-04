from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import openai
import os
import json
from typing import Dict, List, Optional
import asyncio

app = FastAPI(title="AI Dil Öğrenme Asistanı")

# OpenAI setup - Yeni API yapısı
openai.api_key = os.getenv("OPENAI_API_KEY")

# Templates setup
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory session storage (cleared on server restart)
sessions: Dict[str, Dict] = {}

class ChatMessage(BaseModel):
    message: str
    session_id: str

class SessionData(BaseModel):
    messages: List[Dict] = []
    detected_language: Optional[str] = None
    user_level: Optional[str] = None
    message_count: int = 0
    conversation_active: bool = False

# Language detection and level assessment
LANGUAGE_CODES = {
    "turkish": "tr",
    "english": "en", 
    "german": "de",
    "french": "fr",
    "italian": "it"
}

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

async def detect_language_and_level(text: str) -> Dict:
    """Detect language and assess level from user text"""
    
    prompt = f"""
    Analyze this combined text from multiple messages and provide:
    1. Language detection (turkish, english, german, french, italian)
    2. CEFR level assessment (A1, A2, B1, B2, C1, C2)

    Combined text from user messages: "{text}"

    Please assess the ACTUAL level based on:
    - Grammar complexity and accuracy
    - Vocabulary range and sophistication
    - Sentence structure complexity
    - Language fluency indicators

    Do NOT default to A1. Assess the real level based on the text complexity.

    Respond in JSON format:
    {{
        "language": "detected_language",
        "level": "assessed_level",
        "confidence": "high/medium/low"
    }}
    """
    
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        # Fallback - but don't assume A1
        return {"language": "english", "level": "B1", "confidence": "low"}

async def generate_response(user_message: str, language: str, level: str, conversation_history: List[Dict]) -> str:
    """Generate appropriate response based on user's language and level"""
    
    level_descriptions = {
        "A1": "very basic, simple sentences, present tense, common vocabulary",
        "A2": "basic, simple past/future, everyday topics, familiar vocabulary", 
        "B1": "intermediate, various tenses, personal experiences, some complex vocabulary",
        "B2": "upper-intermediate, complex grammar, abstract topics, advanced vocabulary",
        "C1": "advanced, sophisticated language, nuanced expressions, professional vocabulary",
        "C2": "proficient, native-like fluency, complex discourse, specialized vocabulary"
    }
    
    history_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-6:]])
    
    prompt = f"""
    You are a language learning assistant. The user is learning {language} at {level} level.
    
    Level characteristics: {level_descriptions[level]}
    
    Recent conversation:
    {history_context}
    
    User's new message: "{user_message}"
    
    Respond in {language} at exactly {level} level. Be engaging, encouraging, and continue the conversation naturally. 
    Ask follow-up questions to keep the user practicing. Gently correct major errors by modeling correct usage.
    
    Keep responses conversational and appropriate for {level} level learners.
    """
    
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I'm having trouble responding right now. Please try again. (Error: {str(e)})"

async def generate_level_suggestions(language: str, current_level: str, conversation_history: List[Dict]) -> str:
    """Generate suggestions for progressing to next level"""
    
    current_index = LEVELS.index(current_level)
    if current_index >= len(LEVELS) - 1:
        next_level = "C2+ (Advanced proficiency)"
    else:
        next_level = LEVELS[current_index + 1]
    
    history_text = "\n".join([msg['content'] for msg in conversation_history if msg['role'] == 'user'])
    
    prompt = f"""
    Based on this {language} conversation at {current_level} level, provide specific suggestions for progressing to {next_level} level.

    User's messages in this conversation:
    {history_text}

    Provide 3-4 specific, actionable suggestions in Turkish for improving from {current_level} to {next_level} level in {language}.
    Focus on grammar, vocabulary, and practice activities.
    
    Format as a friendly, encouraging message in Turkish.
    """
    
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Bir sonraki seviyeye geçmek için daha fazla pratik yapmanızı öneririm. ({current_level} → {next_level})"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(message_data: ChatMessage):
    session_id = message_data.session_id
    user_message = message_data.message.strip()
    
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Initialize session if not exists
    if session_id not in sessions:
        sessions[session_id] = SessionData().dict()
    
    session = sessions[session_id]
    
    # Handle end conversation command
    if user_message.lower() in ["konuşmayı bitir", "end conversation", "finish", "bitir"]:
        if session["conversation_active"] and len(session["messages"]) > 0:
            suggestions = await generate_level_suggestions(
                session["detected_language"], 
                session["user_level"], 
                session["messages"]
            )
            
            # Reset session for new conversation
            sessions[session_id] = SessionData().dict()
            
            return {
                "response": f"Konuşma tamamlandı! 🎉\n\n{suggestions}\n\nYeni bir konuşma başlatmak için mesaj yazabilirsiniz.",
                "suggestions": True,
                "detected_language": None,
                "user_level": None
            }
        else:
            return {"response": "Henüz aktif bir konuşma yok. Bir şeyler yazarak başlayabilirsiniz!", "suggestions": False}
    
    # Add user message to history
    session["messages"].append({"role": "user", "content": user_message})
    session["message_count"] += 1
    
    # Detect language and level after exactly 3 messages
    if session["message_count"] == 3 and not session["detected_language"]:
        all_user_messages = " ".join([msg["content"] for msg in session["messages"] if msg["role"] == "user"])
        detection_result = await detect_language_and_level(all_user_messages)
        
        session["detected_language"] = detection_result["language"]
        session["user_level"] = detection_result["level"]
        session["conversation_active"] = True
    
    # Generate response
    if session["detected_language"] and session["user_level"]:
        bot_response = await generate_response(
            user_message,
            session["detected_language"],
            session["user_level"], 
            session["messages"]
        )
        
        # Add bot response to history
        session["messages"].append({"role": "assistant", "content": bot_response})
        
        # Update session
        sessions[session_id] = session
        
        return {
            "response": bot_response,
            "detected_language": session["detected_language"],
            "user_level": session["user_level"],
            "message_count": session["message_count"],
            "suggestions": False
        }
    else:
        # Before detection is complete - respond naturally without level assessment
        if session["message_count"] < 3:
            # Generate a natural response in detected language or universally
            try:
                simple_prompt = f"""
                Respond naturally and encouragingly to this message: "{user_message}"
                
                Be friendly and ask a follow-up question to continue the conversation.
                Respond in the same language as the user's message.
                Keep it conversational and engaging.
                """
                
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[{"role": "user", "content": simple_prompt}],
                    temperature=0.7,
                    max_tokens=150
                )
                
                bot_response = response.choices[0].message.content.strip()
                session["messages"].append({"role": "assistant", "content": bot_response})
                sessions[session_id] = session
                
                return {
                    "response": bot_response,
                    "detected_language": None,
                    "user_level": None,
                    "message_count": session["message_count"],
                    "suggestions": False
                }
            except Exception as e:
                bot_response = "Thank you for your message! Please continue writing so I can better understand your language level."
                
        else:
            # After 3 messages, still detecting
            bot_response = "I'm analyzing your language level... Please continue writing!"
            
        session["messages"].append({"role": "assistant", "content": bot_response})
        sessions[session_id] = session
        return {
            "response": bot_response,
            "detected_language": None,
            "user_level": None,
            "message_count": session["message_count"],
            "suggestions": False
        }

@app.get("/new-session")
async def new_session():
    """Create a new session ID"""
    import uuid
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)