# LangGraph + SQLite Inventory Agent

This is the simplest starter example for asking natural-language inventory questions through a LangGraph agent backed by a SQLite database.

## 1. Create virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 2. Install packages

```powershell
pip install -r requirements.txt
```

## 3. Add your OpenAI key

Copy `.env.example` to `.env`, then put your real key inside:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

## 4. Create the SQLite database

```powershell
python init_db.py
```

This creates `inventory.db` with sample inventory data.

## 5. Run the inventory agent

```powershell
python inventory_agent.py
```

## 6. Ask natural-language questions

Example questions:

- `How many laptops do we have?`
- `Which item has the highest price?`
- `Show all furniture items`
- `What is the total quantity of stationery items?`
- `List items supplied by TechSupply`

## Files

- `requirements.txt` : Python packages
- `.env.example` : environment variable template
- `init_db.py` : creates the SQLite database and sample data
- `inventory_agent.py` : LangGraph inventory agent
- `inventory.db` : created after running `python init_db.py`

## Notes

- This version allows only `SELECT` queries for safety.
- SQLite is built into Python, so no separate SQLite package is needed.
- You can later expand this to multiple tables, tool calling, or a Streamlit/FastAPI UI.
