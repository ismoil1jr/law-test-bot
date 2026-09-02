import sqlite3

# app.py va database.py faylingizda qaysi nom bo'lsa, O'SHANI yozing (masalan, database.db)
DB_NAME = "database.db"

def init_and_seed():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Bloklar jadvalini yaratish
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT
        )
    ''')

    # 2. Savollar jadvalini yaratish
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_id INTEGER,
            question_text TEXT NOT NULL,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_option TEXT,
            q_type TEXT DEFAULT 'close',
            FOREIGN KEY (block_id) REFERENCES blocks (id) ON DELETE CASCADE
        )
    ''')

    # 3. Agarda bloklar bo'sh bo'lsa, avtomatik ma'lumot joylash
    cursor.execute("SELECT COUNT(*) FROM blocks")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO blocks (title, description) VALUES (?, ?)", 
                       ("1-Blok: Huquq asoslari", "Konstitutsiya va umumiy huquq testlari"))
        block_id = cursor.lastrowid

        questions_data = [
            (block_id, "O'zbekiston Respublikasi Konstitutsiyasi qachon qabul qilingan?", "1992-yil 8-dekabr", "1991-yil 1-sentyabr", "1993-yil 10-dekabr", "1990-yil 20-iyun", "A", "close"),
            (block_id, "Inson huquqlari umumjahon deklaratsiyasi nechanchi yilda qabul qilingan?", "1948-yil", "1945-yil", "1950-yil", "1991-yil", "A", "close")
        ]

        cursor.executemany('''
            INSERT INTO questions (block_id, question_text, option_a, option_b, option_c, option_d, correct_option, q_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', questions_data)

        conn.commit()
        print("✅ 1-Blok va savollar bazaga muvaffaqiyatli qo'shildi!")
    else:
        print("⚠️ Bazada bloklar allaqachon mavjud.")

    conn.close()

if __name__ == "__main__":
    init_and_seed()