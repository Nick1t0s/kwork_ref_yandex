import sqlite3
import datetime

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dt
                 (user_id INTEGER, datetime TEXT)''')
    conn.commit()
    conn.close()


# Функция для записи нажатия в базу данных
def record_click(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Получаем текущее время в правильном формате для SQLite
    current_time = datetime.datetime.now().isoformat()

    c.execute("INSERT INTO dt (user_id, datetime) VALUES (?, ?)",
              (user_id, current_time))
    conn.commit()
    conn.close()


def get_total_clicks():
    """
    Возвращает общее количество всех кликов
    """
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM dt")
    total_clicks = c.fetchone()[0]

    conn.close()
    return total_clicks


def get_today_clicks():
    """
    Возвращает количество кликов за сегодня
    """
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Получаем сегодняшнюю дату в формате YYYY-MM-DD
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # Ищем записи, где дата начинается с сегодняшней даты
    c.execute("SELECT COUNT(*) FROM dt WHERE datetime LIKE ?", (f"{today}%",))
    today_clicks = c.fetchone()[0]

    conn.close()
    return today_clicks

def clear():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM dt;")
    conn.commit()

    conn.close()
init_db()
print(get_today_clicks())