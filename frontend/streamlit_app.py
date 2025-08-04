import streamlit as st
import openai
import os
import json
import uuid
from typing import Dict, List, Optional
import asyncio
import requests
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    st.warning("python-dotenv not installed. Install with: pip install python-dotenv")

# Streamlit page config
st.set_page_config(
    page_title="🤖 AI Language Learning Assistant",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .language-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin-bottom: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .language-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .language-card h4 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .language-card p {
        color: #495057;
        margin-bottom: 0;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    .status-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 2rem;
    }
    .bot-message {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        margin-right: 2rem;
        color: #2c3e50;
    }
    .suggestions-message {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        text-align: center;
        font-weight: bold;
    }
    
    /* Welcome section styling */
    .welcome-section h3 {
        color: #2c3e50;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Language mappings
LANGUAGE_CODES = {
    "turkish": "tr",
    "english": "en", 
    "german": "de",
    "french": "fr",
    "italian": "it"
}

LANGUAGE_NAMES = {
    'turkish': 'Türkçe 🇹🇷',
    'english': 'English 🇬🇧', 
    'german': 'Deutsch 🇩🇪',
    'french': 'Français 🇫🇷',
    'italian': 'Italiano 🇮🇹'
}

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.detected_language = None
    st.session_state.user_level = None
    st.session_state.message_count = 0
    st.session_state.conversation_active = False

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
        return f"Sorry, I'm having trouble responding right now. Please try again."

async def generate_natural_response(user_message: str) -> str:
    """Generate natural response before level detection"""
    
    simple_prompt = f"""
    Respond naturally and encouragingly to this message: "{user_message}"
    
    Be friendly and ask a follow-up question to continue the conversation.
    Respond in the same language as the user's message.
    Keep it conversational and engaging.
    """
    
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": simple_prompt}],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Thank you for your message! Please continue writing so I can better understand your language level."

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

# Main App
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Language Learning Assistant</h1>
        <p>Learn Turkish, English, German, French, Italian with AI</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Session Status")
        
        # Status boxes
        if st.session_state.detected_language:
            language_display = LANGUAGE_NAMES.get(st.session_state.detected_language, st.session_state.detected_language)
            st.markdown(f"""
            <div class="status-box">
                <strong>Language:</strong><br>
                {language_display}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-box">
                <strong>Language:</strong><br>
                Detecting...
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.session_state.user_level:
            st.markdown(f"""
            <div class="status-box">
                <strong>Level:</strong><br>
                {st.session_state.user_level}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-box">
                <strong>Level:</strong><br>
                Assessing...
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**Messages:** {st.session_state.message_count}")
        st.markdown(f"**Session ID:** {st.session_state.session_id[:8]}...")
        
        st.markdown("---")
        
        # End conversation button
        if st.button("🔚 End Conversation", type="secondary", use_container_width=True):
            if st.session_state.conversation_active and len(st.session_state.messages) > 0:
                # Generate suggestions
                suggestions = asyncio.run(generate_level_suggestions(
                    st.session_state.detected_language,
                    st.session_state.user_level,
                    st.session_state.messages
                ))
                
                # Add suggestions message
                st.session_state.messages.append({
                    "role": "suggestions", 
                    "content": f"Konuşma tamamlandı! 🎉\n\n{suggestions}\n\nYeni bir konuşma başlatmak için mesaj yazabilirsiniz."
                })
                
                # Reset session
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.detected_language = None
                st.session_state.user_level = None
                st.session_state.message_count = 0
                st.session_state.conversation_active = False
                
                st.rerun()
            else:
                st.warning("Henüz aktif bir konuşma yok!")
        
        # Reset button
        if st.button("🔄 New Session", type="primary", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.detected_language = None
            st.session_state.user_level = None
            st.session_state.message_count = 0
            st.session_state.conversation_active = False
            st.rerun()

    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Welcome message for new sessions
        if not st.session_state.messages:
            st.markdown('<div class="welcome-section">', unsafe_allow_html=True)
            st.markdown("### 🌍 Welcome! Choose your language and start practicing:")
            
            # Language cards
            languages = [
                ("🇹🇷 Türkçe", "Merhaba! Hangi dilde konuşmak istiyorsun? Sadece yazmaya başla, 3 mesaj sonra seviyeni tespit edeceğim."),
                ("🇬🇧 English", "Hello! Which language would you like to practice? Just start writing, I'll detect your level after 3 messages."),
                ("🇩🇪 Deutsch", "Hallo! In welcher Sprache möchtest du üben? Fang einfach an zu schreiben, ich erkenne dein Niveau nach 3 Nachrichten."),
                ("🇫🇷 Français", "Salut ! Dans quelle langue veux-tu pratiquer ? Commence à écrire, je détecterai ton niveau après 3 messages."),
                ("🇮🇹 Italiano", "Ciao! In che lingua vuoi praticare? Inizia a scrivere, rileverò il tuo livello dopo 3 messaggi.")
            ]
            
            for lang_name, message in languages:
                st.markdown(f"""
                <div class="language-card">
                    <h4>{lang_name}</h4>
                    <p>{message}</p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat messages
        if st.session_state.messages:
            st.markdown("### 💬 Conversation")
            
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong> {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                elif msg["role"] == "assistant":
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>AI Assistant:</strong> {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                elif msg["role"] == "suggestions":
                    st.markdown(f"""
                    <div class="chat-message suggestions-message">
                        {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Message input
        st.markdown("---")
        user_input = st.text_area(
            "✍️ Write your message in any language:",
            height=100,
            placeholder="Start typing to begin your language learning journey..."
        )
        
        col_send, col_clear = st.columns([1, 1])
        with col_send:
            send_button = st.button("📤 Send Message", type="primary", use_container_width=True)
        with col_clear:
            clear_button = st.button("🗑️ Clear Input", use_container_width=True)
        
        if clear_button:
            st.rerun()
        
        if send_button and user_input.strip():
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input.strip()})
            st.session_state.message_count += 1
            
            # Process message
            with st.spinner("🤔 Thinking..."):
                # Detect language and level after exactly 3 messages
                if st.session_state.message_count == 3 and not st.session_state.detected_language:
                    all_user_messages = " ".join([msg["content"] for msg in st.session_state.messages if msg["role"] == "user"])
                    detection_result = asyncio.run(detect_language_and_level(all_user_messages))
                    
                    st.session_state.detected_language = detection_result["language"]
                    st.session_state.user_level = detection_result["level"]
                    st.session_state.conversation_active = True
                
                # Generate response
                if st.session_state.detected_language and st.session_state.user_level:
                    bot_response = asyncio.run(generate_response(
                        user_input.strip(),
                        st.session_state.detected_language,
                        st.session_state.user_level,
                        st.session_state.messages
                    ))
                else:
                    # Before detection is complete
                    if st.session_state.message_count < 3:
                        bot_response = asyncio.run(generate_natural_response(user_input.strip()))
                    else:
                        bot_response = "I'm analyzing your language level... Please continue writing!"
                
                # Add bot response
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
            st.rerun()
    
    with col2:
        st.markdown("### 📚 Learning Tips")
        
        tips = [
            "💡 **Tip 1:** Write naturally - don't worry about making mistakes!",
            "🎯 **Tip 2:** The system analyzes your level after 3 messages",
            "🔄 **Tip 3:** Practice regularly for best results",
            "📈 **Tip 4:** Challenge yourself with complex topics",
            "🗣️ **Tip 5:** Use the language you want to practice"
        ]
        
        for tip in tips:
            st.markdown(tip)
        
        st.markdown("---")
        st.markdown("### 🌟 Supported Languages")
        for lang_code, lang_name in LANGUAGE_NAMES.items():
            st.markdown(f"• {lang_name}")
        
        st.markdown("---")
        st.markdown("### 📊 CEFR Levels")
        level_descriptions = {
            "A1": "Beginner",
            "A2": "Elementary", 
            "B1": "Intermediate",
            "B2": "Upper Intermediate",
            "C1": "Advanced",
            "C2": "Proficient"
        }
        
        for level, desc in level_descriptions.items():
            st.markdown(f"• **{level}**: {desc}")

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("🚨 OpenAI API key not found! Please set the OPENAI_API_KEY environment variable.")
        st.info("💡 Create a .env file in your project directory with: OPENAI_API_KEY=your_api_key_here")
        st.stop()
    
    main()