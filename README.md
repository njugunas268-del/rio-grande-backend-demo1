# Rio Grande Due Diligence — Backend Demo

This is a minimal backend prototype showing:

- /health endpoint
- /generate-report endpoint
- Mock flood and wildfire risk scoring using Shapely
- Dockerfile ready for deployment to Railway, Render, or DigitalOcean App Platform

## How to run locally (basic idea)

1. Install dependencies from requirements.txt
2. Run the app with: uvicorn main:app --reload
3. Open your browser at: http://127.0.0.1:8000/docs

You can share this repository link and deploy it to a PaaS to demonstrate your backend skills for the Rio Grande Due Diligence project.
