# 🥗 AI Nutrition Assistant

An agentic AI app that tracks meals and weight, and gives personalized nutrition advice with cited sources. Type "I had 2 rotis and dal tadka for lunch" and it logs the food, calculates calories, and tells you how much is left for the day.

## Features
- Chat in plain language to log meals and weight
- Daily calorie target calculated with the Mifflin-St Jeor formula from your profile and goal
- Meal suggestions that respect diet type (veg/non-veg) and allergies
- Weight trend and daily calorie charts
- Food answers include numbered citations and their dataset source

## AI Concepts Used
| Concept | Where it is used |
|---|---|
| Transformer encoder | `all-MiniLM-L6-v2` turns foods and queries into embeddings |
| Vector DB + RAG | ChromaDB retrieval over Indian food data, passed to the LLM as context |
| Decoder LLM (GenAI) | LLM via Groq generates the answers |
| Prompt engineering | System prompts with grounding rules, citation format, diet/allergy guardrails, and user profile injected dynamically |
| Agentic AI | LangGraph agent that chooses tools, with conversation memory |
| Fine-tuning | DistilBERT token classifier that extracts foods and quantities from sentences |

## Architecture
```mermaid
flowchart TD
    U[User - Streamlit UI] --> A[LangGraph Agent]
    A -->|decides| T{Tools}
    T --> S[Food search - RAG]
    T --> L[Log meal / weight]
    T --> R[Calories and weekly summary]
    S --> V[(ChromaDB vectors)]
    S --> E[Encoder - sentence-transformers]
    L --> N[Fine-tuned DistilBERT]
    L --> M[(MySQL)]
    R --> M
    A --> G[LLM - Groq]
```

## Tech Stack
Python, Streamlit, LangChain, LangGraph, ChromaDB, sentence-transformers, Hugging Face Transformers, SQLAlchemy, MySQL, Groq API

## Project Structure
```
nutrition-assistant/
├── config.py          # settings and paths
├── core/              # embeddings, vector store, RAG, prompts, LLM, agent, tools
├── db/                # MySQL models and CRUD functions
├── ui/app.py          # Streamlit app
├── finetune/          # NER dataset generator (training done in Google Colab)
└── data/              # cleaned food data
```

## Fine-tuning
DistilBERT was fine-tuned on 3,000 synthetic sentences generated from food names, to tag FOOD and QTY. Because the training data is template-based, unusual phrasing may be missed.

## Run Locally
1. Download the project and open it in PyCharm.
2. Create a virtual environment and install packages:
```bash
pip install -r requirements.txt
```
3. Install MySQL and create a database named `nutrition_db`.
4. Create a `.env` file in the project root:
```
LLM_API_KEY=your_groq_api_key
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/nutrition_db
```
5. Download and clean the data: `python download_data.py`, then `python prepare_data.py`
6. Create the tables: `python create_tables.py`
7. Build the vector DB: `python ingest_data.py`
8. Train the extractor with the Colab steps, and place it in `finetune/food_ner_model/`
9. Start the app: `streamlit run ui/app.py`

## Limitations
- Nutrition values come from a Kaggle dataset and may be per serving, not per 100g
- The veg/non-veg tag is keyword-based, so some dishes may be wrong
- The food extractor was trained on synthetic data
- Not medical advice

## Data Source
Kaggle: Indian Food Nutrition Dataset (`batthulavinay/indian-food-nutrition`)