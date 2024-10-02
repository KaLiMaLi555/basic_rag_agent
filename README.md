# AI Chat Playground

## Features

- Ncert database Search
- Arxiv database Search
- Google Search

You can ask questions like 
- `What is sound?`
- `Tell me more about the paper "Attention is all you need"`
- `What is 1 + 1?`

---
## How to install

- Clone the repository

- Install dependencies

1. Frontend
```bash
# Uses react and next.js frontend
cd rag-assignment
pnpm install
```
2. Backend
```bash
# Uses fastapi backend

cd rag-assignment
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```
- Setup env variables

```bash
cd rag-assignment
cp .env.sample .env
```
Then fill in the API Key variables for `GOOGLE_API_KEY` and `SARWAM_API_KEY`.
These are *required* for having gemini access for the google gemini api and text to speech api from sarwam.ai 

- Setup vector store

```bash
cd rag-assignment
source .venv/bin/activate
python3 api/setup_dbs.py
```
This may take time depending on the specs of the host machine. But after completion, you can find two folders `data/ncert_persist` and `data/arxiv_persist`.<br><br>
Alternatively, you can download the two folders from this [Link](https://drive.google.com/drive/folders/1lBvwbpuWS2LbLzY18ndD4VAOTCekSNY1?usp=sharing)

----
## Run app
```bash
pnpm run dev
```
This might take a while when running for the first time, as it will install python dependencies for backend
### Only run frontend
```bash
pnpm run next-dev
```
### Only run backend
```bash
pnpm run fastapi-dev
```
---
## Langraph Agent Vizualization

![Agent Flow Viz](Assets/rag_assignment_graph_viz.png)
