# 🤖 AI Language Learning Assistant

An intelligent language learning application powered by OpenAI GPT-4, available in both **Streamlit** and **FastAPI** versions with Docker support.

## 🌟 Features

- **Multi-language Support**: Turkish, English, German, French, Italian
- **Automatic Level Detection**: CEFR levels (A1-C2) detected after 3 messages
- **Personalized Responses**: AI adapts to your language level
- **Real-time Conversation**: Interactive chat interface
- **Progress Tracking**: Session management and conversation history
- **Level-appropriate Learning**: Responses tailored to your proficiency
- **Docker Support**: Easy deployment with containerization

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API Key
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-language-assistant.git
   cd ai-language-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## 🐳 Docker Deployment

### Option 1: Streamlit Version
```bash
# Build the image
docker build -t ai-language-assistant-streamlit .

# Run the container
docker run -p 8501:8501 --env-file .env ai-language-assistant-streamlit
```

### Option 2: FastAPI Version
```bash
# Build the FastAPI image
docker build -f Dockerfile.fastapi -t ai-language-assistant-fastapi .

# Run the container
docker run -p 8000:8000 --env-file .env ai-language-assistant-fastapi
```

### Option 3: Docker Compose (Both versions)
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down
```

Access the applications:
- **Streamlit**: http://localhost:8501
- **FastAPI**: http://localhost:8000

## 🖥️ Local Development

### Streamlit Version
```bash
streamlit run streamlit_app.py
```
Open: http://localhost:8501

### FastAPI Version
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Open: http://localhost:8000

## 🎯 How to Use

### Streamlit Interface
1. **Start the Application**: Open your browser and navigate to `http://localhost:8501`
2. **Choose Your Language**: Start writing in any supported language
3. **Automatic Detection**: After 3 messages, the system detects language and level
4. **Practice**: Continue conversations with tailored AI responses
5. **Track Progress**: Monitor your session in the sidebar

### FastAPI Interface
1. **Start the Application**: Open your browser and navigate to `http://localhost:8000`
2. **Interactive Chat**: Use the web interface for real-time conversations
3. **API Endpoints**: Access programmatically via REST API
4. **Session Management**: Each session maintains conversation history

## 🌍 Supported Languages

- 🇹🇷 **Turkish** (Türkçe)
- 🇬🇧 **English**
- 🇩🇪 **German** (Deutsch)
- 🇫🇷 **French** (Français)
- 🇮🇹 **Italian** (Italiano)

## 📊 CEFR Levels

- **A1**: Beginner
- **A2**: Elementary
- **B1**: Intermediate
- **B2**: Upper Intermediate
- **C1**: Advanced
- **C2**: Proficient

## 🏗️ Architecture

### Two Implementation Options

#### 1. Streamlit Version (`streamlit_app.py`)
- **Frontend**: Streamlit web interface
- **State Management**: Streamlit session state
- **Deployment**: Single file, easy to run
- **Best for**: Quick prototyping, simple deployment

#### 2. FastAPI Version (`main.py`)
- **Backend**: FastAPI REST API
- **Frontend**: HTML templates with JavaScript
- **State Management**: In-memory sessions
- **Deployment**: Production-ready web service
- **Best for**: Scalable applications, API integrations

## 🔧 Technical Details

### Tech Stack
- **Backend**: FastAPI / Streamlit
- **AI Model**: OpenAI GPT-4
- **Language**: Python 3.8+
- **Containerization**: Docker
- **Orchestration**: Docker Compose

### API Endpoints (FastAPI Version)
- `GET /` - Main chat interface
- `POST /chat` - Send message and get response
- `GET /new-session` - Create new session

## 📝 Project Structure

```
ai-language-assistant/
├── streamlit_app.py          # Streamlit version
├── main.py                   # FastAPI version
├── templates/                # HTML templates (FastAPI)
│   └── index.html
├── static/                   # Static files (FastAPI)
│   ├── style.css
│   └── script.js
├── requirements.txt          # Python dependencies
├── Dockerfile               # Streamlit Docker image
├── Dockerfile.fastapi       # FastAPI Docker image
├── docker-compose.yml       # Multi-container setup
├── .env                     # Environment variables
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## 📋 Requirements

Create `requirements.txt`:
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
streamlit>=1.28.0
openai>=0.28.0
python-dotenv>=0.19.0
jinja2>=3.1.0
python-multipart>=0.0.6
aiofiles>=23.0.0
requests>=2.28.0
```

## 🐳 Docker Configuration

### Dockerfile (Streamlit)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Dockerfile.fastapi
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - .:/app

  fastapi:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - .:/app
```

## 🚀 Deployment Options

### 1. Local Development
```bash
# Streamlit
streamlit run streamlit_app.py

# FastAPI
uvicorn main:app --reload
```

### 2. Docker Single Container
```bash
# Streamlit
docker run -p 8501:8501 --env-file .env ai-language-assistant

# FastAPI
docker run -p 8000:8000 --env-file .env ai-language-assistant-fastapi
```

### 3. Docker Compose
```bash
docker-compose up -d
```

### 4. Cloud Deployment
- **Heroku**: Use `Procfile` for deployment
- **AWS/GCP**: Use container services
- **Streamlit Cloud**: Direct GitHub integration for Streamlit version

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔐 Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
DEBUG=True
PORT=8000
HOST=0.0.0.0
```

## 🆘 Troubleshooting

### Common Issues

1. **OpenAI API Key not found**
   - Ensure `.env` file exists with correct API key
   - Check environment variable is loaded

2. **Docker build fails**
   - Ensure Docker is running
   - Check Dockerfile syntax
   - Verify requirements.txt exists

3. **Port already in use**
   - Change port in docker-compose.yml
   - Kill existing processes: `docker-compose down`

4. **Session not persisting**
   - FastAPI uses in-memory storage (resets on restart)
   - For production, consider Redis or database

## 📄 License

This project is licensed under the MIT License 

