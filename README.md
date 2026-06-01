# AI Assistant Chatbot Hub 🤖

An open-source AI Assistant built for the Elite Coders Open Source Hackathon 2026.

## Features

* Smart AI Chatbot
* Currency Converter
* Weather Information
* Motivational Quotes
* Joke Generator
* Chat History
* Dark Mode UI
* Mobile Responsive Design

## Tech Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* Flask

## Project Structure

```text
ai-assistant-chatbot-hub/
│
├── app.py
├── chatbot.py
├── requirements.txt
├── README.md
│
├── static/
│   ├── style.css
│   └── script.js
│
├── templates/
│   └── index.html
│
└── data/
    └── responses.json
```


## Screenshots
<img width="1920" height="1128" alt="AI Chatbot" src="https://github.com/user-attachments/assets/fe1abcd3-28fc-4027-bdda-4e726edc8ced" />

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
   
## Author

Heena Perween

Built during Open Source Hackathon 2026.


Please keep code beginner-friendly, documented, and maintainable.

## License
MIT License

