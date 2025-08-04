#!/usr/bin/env python3
"""
Streamlit Runner Script
Run this to start the Streamlit app
"""
import openai
import subprocess
import sys
import os


openai.api_key = os.getenv("OPENAI_API_KEY")
def main():
    # Set environment variables if needed
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set!")
        print("Please set it before running the app:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print()
    
    # Run streamlit
    try:
        print("🚀 Starting Streamlit Language Learning Assistant...")
        print("📱 The app will open in your browser automatically")
        print("🔗 Usually at: http://localhost:8501")
        print()
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down Streamlit app...")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")

if __name__ == "__main__":
    main()