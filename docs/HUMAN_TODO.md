# What You Need To Do (Step by Step)

## Prerequisites
1. Install Python 3.11+ (Download at [python.org](https://www.python.org/downloads/), check 'Add to PATH' during install)
2. Install Git (Optional for drag-and-drop, available at [git-scm.com](https://git-scm.com/))

## Setup
3. Get a free Groq API key:
   - Go to [console.groq.com](https://console.groq.com)
   - Sign in with Google/GitHub
   - Click 'API Keys' -> 'Create API Key'
   - Copy the key
4. Create .env file:
   - Copy .env.example to .env
   - Replace 'your_groq_api_key_here' with your actual key
## Running Locally
5. Install dependencies and run:
   - Backend:
     - `pip install -r requirements.txt`
     - `uvicorn server:app --reload --port 8000`
   - Frontend:
     - `cd frontend`
     - `npm install`
     - `npm run dev` (opens http://localhost:5173)

## Deployment (Render + Vercel)
6. **Backend on Render (Free Web Service)**:
   - Push your repo to GitHub
   - On render.com, click 'New' -> 'Web Service' -> Connect your repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - Environment Variables: add `GROQ_API_KEY`
7. **Frontend on Vercel (Free Frontend)**:
   - On vercel.com, click 'Add New' -> 'Project' -> Import your repo
   - Set Root Directory to: `frontend`
   - Environment Variables: add `VITE_API_BASE_URL` with your Render backend URL
   - Click Deploy

## What Link to Submit
- Your Vercel frontend URL (e.g. https://studypilot.vercel.app)
- Your GitHub repo link: https://github.com/YOUR_USERNAME/studypilot

## Troubleshooting (8 most common errors)
1. 'python not found' -> Install Python, check PATH
2. 'pip not found' -> Use `python -m pip` instead
3. 'ModuleNotFoundError' -> Activate venv and run pip install
4. 'GROQ_API_KEY missing' -> Check .env file exists with correct key
5. 'Rate limit error' -> Wait 60 seconds, the app auto-retries
6. 'streamlit not found' -> pip install streamlit
7. 'Port already in use' -> Close other Streamlit instances or use --server.port 8502
8. 'Git push rejected' -> git pull first, then push
