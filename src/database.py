import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'jobsearch.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS offers (
            france_travail_id TEXT PRIMARY KEY,
            position TEXT,
            entreprise TEXT,
            localisation TEXT,
            job_input TEXT,
            link TEXT,
            date_recorded DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS letters (
            id_letter INTEGER PRIMARY KEY AUTOINCREMENT,
            entreprise TEXT,
            path TEXT,
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            note INTEGER DEFAULT NULL,
            nb_words INTEGER DEFAULT 0,
            entreprise_is_present BOOLEAN DEFAULT 0
        )      
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id_session INTEGER PRIMARY KEY AUTOINCREMENT,
            date_start DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_end DATETIME DEFAULT CURRENT_TIMESTAMP,
            inputs_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            cost_usd REAL DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id_application INTEGER PRIMARY KEY AUTOINCREMENT,
            france_travail_id TEXT,
            id_letter INTEGER,
            date_application DATETIME DEFAULT CURRENT_TIMESTAMP,
            to_follow_up BOOLEAN DEFAULT 0,
            date_follow_up DATETIME,
            statut TEXT DEFAULT 'waiting'
        )
    ''')
    
    conn.commit()
    conn.close()

def save_offer(france_travail_id, position, entreprise, localisation, job_input, link):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO offers (france_travail_id, position, entreprise, localisation, job_input, link)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (france_travail_id, position, entreprise, localisation, job_input, link))
    conn.commit()
    conn.close()

def save_letter(entreprise, path, nb_words=0, entreprise_is_present=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO letters (entreprise, path, nb_words, entreprise_is_present)
        VALUES (?, ?, ?, ?)
    ''', (entreprise, path, nb_words, entreprise_is_present))
    conn.commit()
    conn.close()

def get_last_letter_id():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id_letter FROM letters ORDER BY date_creation DESC LIMIT 1')
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def rate_letter(id_letter, note):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE letters
        SET note = ?
        WHERE id_letter = ?
    ''', (note, id_letter))
    conn.commit()
    conn.close()

def save_session(inputs_tokens, output_tokens, cost_usd):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO sessions (inputs_tokens, output_tokens, cost_usd)
        VALUES (?, ?, ?)
    ''', (inputs_tokens, output_tokens, cost_usd))
    conn.commit()
    conn.close()

def save_application(france_travail_id, id_letter):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO applications (france_travail_id, id_letter)
        VALUES (?, ?)
    ''', (france_travail_id, id_letter))
    conn.commit()
    conn.close()

