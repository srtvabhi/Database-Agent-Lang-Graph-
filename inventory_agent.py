import json
import sqlite3
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph


load_dotenv()

DB_PATH = "inventory.db"

SCHEMA = """
Table: inventory
Columns:
- id (INTEGER)
- item_name (TEXT)
- category (TEXT)
- quantity (INTEGER)
- price (REAL)
- supplier (TEXT)
"""


class AgentState(TypedDict, total=False):
    question: str
    sql_query: str
    sql_result: str
    answer: str
    error: str


llm = ChatOpenAI(temperature=0)


def generate_sql(state: AgentState) -> AgentState:
    prompt = f"""
You convert natural language questions into SQLite SQL queries.

Database schema:
{SCHEMA}

Rules:
- Return only a single SQLite SELECT query.
- Do not write INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or PRAGMA.
- Use only the inventory table.
- If the user asks for all rows, limit to 20 rows.
- If totals or counts are requested, use SQL aggregation.
- Return plain SQL only. No markdown. No explanation.
"""

    response = llm.invoke(
        [
            SystemMessage(content=prompt),
            HumanMessage(content=state["question"]),
        ]
    )
    sql_query = response.content.strip().strip("`")
    return {"sql_query": sql_query}


def run_sql(state: AgentState) -> AgentState:
    sql_query = state["sql_query"].strip()
    normalized = sql_query.lower().lstrip()

    if not normalized.startswith("select"):
        return {"error": f"Blocked non-SELECT query: {sql_query}"}

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"sql_result": json.dumps(rows, indent=2)}
    except Exception as exc:
        return {"error": str(exc)}


def write_answer(state: AgentState) -> AgentState:
    if state.get("error"):
        return {"answer": f"Error: {state['error']}"}

    prompt = f"""
You are an inventory assistant.
Answer the user's question in simple language based only on the SQL result.

User question:
{state["question"]}

SQL query:
{state["sql_query"]}

SQL result:
{state["sql_result"]}
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"answer": response.content}


graph_builder = StateGraph(AgentState)
graph_builder.add_node("generate_sql", generate_sql)
graph_builder.add_node("run_sql", run_sql)
graph_builder.add_node("write_answer", write_answer)

graph_builder.set_entry_point("generate_sql")
graph_builder.add_edge("generate_sql", "run_sql")
graph_builder.add_edge("run_sql", "write_answer")
graph_builder.add_edge("write_answer", END)

graph = graph_builder.compile()


def ask_inventory_agent(question: str) -> None:
    result = graph.invoke({"question": question})
    print("\nQuestion:")
    print(question)
    print("\nGenerated SQL:")
    print(result.get("sql_query", "No SQL generated"))
    print("\nAnswer:")
    print(result.get("answer", "No answer generated"))


if __name__ == "__main__":
    print("Inventory agent is ready.")
    print("Type your question, or type 'exit' to quit.\n")

    while True:
        user_question = input("Ask inventory question: ").strip()
        if user_question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        ask_inventory_agent(user_question)
        print("\n" + "-" * 60 + "\n")


"""
Questions to try:
- What items are in the inventory?
- How many units of each item do we have?
- What is the total value of the inventory?
- How many Laptop do we have?
- Show all Furniture items
- Which item has the highest price?
- List items supplied by TechSupply

"""
