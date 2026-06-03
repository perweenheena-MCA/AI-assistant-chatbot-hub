# Deployment Guide (Render + Vercel)

## 1) Render (Recommended)
### Steps
1. Go to https://render.com and create **New Web Service**.
2. Connect the repo (GitHub).
3. Set **Environment**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
4. (Optional) Add environment variable:
   - `WEATHER_API_KEY` (for live weather)
5. Click **Create Web Service**.

### Notes
- This app serves frontend from Flask templates/static.
- Backend is lightweight (rule-based + fuzzy matching), so it’s fast for hackathon demos.

## 2) Vercel
Vercel is primarily for Node/Next.js. Flask typically works only via adapters.
- If you must use Vercel, keep it hackathon-friendly:
  - Deploy Flask backend on Render.
  - Use Vercel for any additional frontend (optional).

## Health check
The app exposes `GET /api/health`.

