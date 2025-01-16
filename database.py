import aiosqlite

async def init_db():
    async with aiosqlite.connect("users.db") as conn:
        cursor = await conn.cursor()
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            chat_enabled INTEGER DEFAULT 0
        )
        """)
        await conn.commit()

        await cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in await cursor.fetchall()]
        if "chat_enabled" not in columns:
            await cursor.execute("ALTER TABLE users ADD COLUMN chat_enabled INTEGER DEFAULT 0")
            await conn.commit()

        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            feedback_text TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        """)
        await conn.commit()

        await cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in await cursor.fetchall()]
        if "chat_enabled" not in columns:
            await cursor.execute("ALTER TABLE users ADD COLUMN chat_enabled INTEGER DEFAULT 0")
            await conn.commit()

async def get_user(user_id):
    async with aiosqlite.connect("users.db") as conn:
        cursor = await conn.cursor()
        await cursor.execute("SELECT username, chat_enabled FROM users WHERE user_id = ?", (user_id,))
        result = await cursor.fetchone()
        return result if result else None

async def insert_user(user_id, user_data):
    if not await get_user(user_id):
        async with aiosqlite.connect("users.db") as conn:
            cursor = await conn.cursor()
            await cursor.execute("INSERT INTO users (user_id, username, chat_enabled) VALUES (?, ?, ?)",
                                 (user_id, user_data.get("name", ""), user_data.get("chat_enabled", 0)))
            await conn.commit()

async def update_user(user_id, updates):
    user = await get_user(user_id)
    if user:
        async with aiosqlite.connect("users.db") as conn:
            cursor = await conn.cursor()

            username = updates.get('name')
            if username:
                await cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))

            chat_enabled = updates.get('chat_enabled')
            if chat_enabled is not None:
                await cursor.execute("UPDATE users SET chat_enabled = ? WHERE user_id = ?", (chat_enabled, user_id))

            await conn.commit()

async def save_feedback(user_id: int, feedback: str):
    async with aiosqlite.connect("users.db") as conn:
        cursor = await conn.cursor()
        await cursor.execute("INSERT INTO feedback (user_id, feedback_text) VALUES (?, ?)", (user_id, feedback))
        await conn.commit()
