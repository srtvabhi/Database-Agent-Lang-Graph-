import sqlite3
from pathlib import Path


DB_PATH = Path("inventory.db")


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS inventory")
    cursor.execute(
        """
        CREATE TABLE inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            supplier TEXT NOT NULL
        )
        """
    )

    sample_rows = [
        ("Laptop", "Electronics", 15, 65000, "TechSupply"),
        ("Mouse", "Electronics", 120, 700, "TechSupply"),
        ("Keyboard", "Electronics", 80, 1500, "KeyMakers"),
        ("Office Chair", "Furniture", 20, 5500, "ComfortWorks"),
        ("Desk", "Furniture", 12, 9000, "ComfortWorks"),
        ("Notebook", "Stationery", 200, 50, "PaperWorld"),
        ("Pen", "Stationery", 500, 10, "PaperWorld"),
    ]

    cursor.executemany(
        """
        INSERT INTO inventory (item_name, category, quantity, price, supplier)
        VALUES (?, ?, ?, ?, ?)
        """,
        sample_rows,
    )

    conn.commit()
    conn.close()
    print(f"Database created at: {DB_PATH.resolve()}")


if __name__ == "__main__":
    main()
