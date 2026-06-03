# HackAI — Full Stack AI Chatbot (Flask)

A modern, beginner-friendly, hackathon-ready full stack chatbot app.

## Features
- Chat UI with dark/light themes, smooth animations, avatars, typing indicator
- Context-aware responses using local intent knowledge base (`data/responses.json`)
- Fuzzy matching with `difflib`
- **Currency Converter**: e.g. `Convert 100 USD to INR`
- **Weather**: e.g. `Weather in London` (requires `WEATHER_API_KEY`)
- **Time & Date**: e.g. `What time is it?`
- **Jokes** and **Motivational quotes**
- Basic assistant commands:
  - `Who are you?`
  - `Help`
  - `What can you do?`
- Chat history saved in browser `localStorage`
- Export chat to JSON (bonus)
- Emoji quick insert (bonus)

## Screenshots
Add screenshots here when presenting at the hackathon.

> Tip for hackathon judging: record a short screen video showing **currency conversion**, **weather**, **jokes**, **motivation**, and **typing indicator**.


## Tech Stack
- Frontend: HTML5, CSS3, JavaScript
- Backend: Python Flask

## Setup
### 1) Prerequisites
- Python 3.10+

### 2) Install dependencies
```bash
cd ai-chatbot
python -m venv .venv
.[0m.venv\Scripts\activate
pip install -r requirements.txt
```

### 3) (Optional) Weather API key
Set `WEATHER_API_KEY` for live weather:

**Windows (PowerShell):**
```powershell
$env:WEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"
```

## Run the project
```bash
cd ai-chatbot
python app.py
```
Open in browser: `http://localhost:5000`

## Deployment

(See `DEPLOYMENT.md` for the full guide.)

### Render

1) Create a new Render Web Service

2) Set build command:
   - `pip install -r requirements.txt`
3) Set start command:
   - `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
4) Add environment variable `WEATHER_API_KEY` (optional)

### Vercel
Flask is not built-in for Vercel (it’s a Python server), but this can still work via an adapter/service.
- Recommendation: deploy primarily on Render.
- Optional hackathon approach: use Render for backend and keep Vercel for a separate frontend build.


## Future Improvements
- Add real LLM integration (OpenAI/local) while keeping fast fallback mode
- Server-side conversation persistence (DB)
- Add file upload + document Q&A
- Add multiple bot personalities
- Add suggestions based on conversation context
- Improve NLP (spaCy / embeddings)

## Contributing
See `open-source.md` for a beginner-friendly contribution guide.

1) Fork the repo
2) Create a branch: `blackboxai/<your-feature>`
3) Commit changes
4) Open a Pull Request


Please keep code beginner-friendly, documented, and maintainable.

## License
MIT License

