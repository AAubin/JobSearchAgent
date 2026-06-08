import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent.parent / 'jobsearch.db'

def _connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_id TEXT UNIQUE,
            source TEXT,
            position TEXT,
            entreprise TEXT,
            localisation TEXT,
            description TEXT,
            link TEXT,
            interested INTEGER DEFAULT 0,
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
            offer_id TEXT,
            id_letter INTEGER,
            date_application DATETIME DEFAULT CURRENT_TIMESTAMP,
            to_follow_up BOOLEAN DEFAULT 1,
            date_follow_up DATETIME,
            statut TEXT DEFAULT 'En cours',
            UNIQUE (offer_id, id_letter)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_offer(offer_id, source, position, entreprise, localisation, link, description=None, interested=0):
    ts = datetime.now().isoformat()
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO offers (offer_id, source, position, entreprise, localisation, link, description, interested, date_recorded)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (offer_id, source, position, entreprise, localisation, link, description, interested, ts))
    conn.commit()
    conn.close()

def update_offers(offer_id, entreprise=None, intitule=None, lieu=None, interested=1):
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        UPDATE offers
        SET position = ?, entreprise = ?, localisation = ?,  interested = ?
        WHERE offer_id = ?
    ''', (intitule, entreprise, lieu, interested, offer_id))
    conn.commit()
    conn.close()

def get_all_offers():
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        SELECT  offer_id, position, entreprise, localisation, interested, link, date_recorded
        FROM offers
    ''')
    results = c.fetchall()
    conn.close()
    if results:
        keys = ["offer_id", "Intitulé", "Entreprise", "Lieu", "Intéressé", "Lien", "Recherché le"]
        offers = [dict(zip(keys, r)) for r in results]
        for offer in offers:
            offer['Intéressé'] = bool(offer['Intéressé']) if offer['Intéressé'] is not None else None
        return offers
    return []

def get_offer_by_id(offer_id):
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        SELECT offer_id, source, position, entreprise, localisation, link, description, interested, date_recorded
        FROM offers
        WHERE offer_id = ?
    ''', (offer_id,))
    result = c.fetchone()
    conn.close()
    if result:
        keys = ["offer_id", "source", "position", "entreprise", "localisation", "link", "description", "interested", "date_recorded"]
        return dict(zip(keys, result))
    return None

def get_offer_interest(offer_id):
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        SELECT interested
        FROM offers
        WHERE offer_id = ?
    ''', (offer_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_existing_offer_ids(offer_ids: list) -> set:
    conn = _connect()
    c = conn.cursor()
    placeholders = ",".join(["?" for _ in offer_ids])
    c.execute(f"SELECT offer_id FROM offers WHERE offer_id IN ({placeholders})", offer_ids)
    result = {row[0] for row in c.fetchall()}
    conn.close()
    return result


def save_letter(entreprise, path, nb_words=0, entreprise_is_present=False):
    ts = datetime.now().isoformat()
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        INSERT INTO letters (entreprise, path, nb_words, entreprise_is_present, date_creation)
        VALUES (?, ?, ?, ?, ?)
    ''', (entreprise, path, nb_words, entreprise_is_present, ts))
    conn.commit()
    conn.close()

def get_last_letter_id():
    conn = _connect()
    c = conn.cursor()
    c.execute('SELECT id_letter FROM letters ORDER BY date_creation DESC LIMIT 1')
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def update_letter_rating(id_letter, note):
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        UPDATE letters
        SET note = ?
        WHERE id_letter = ?
    ''', (note, id_letter))
    conn.commit()
    conn.close()


def save_session(date_start, date_end, token_count, cost_usd):
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        INSERT INTO sessions (date_start, date_end, inputs_tokens, output_tokens, cost_usd)
        VALUES (?, ?, ?, ?, ?)
    ''', (date_start, date_end, token_count['input_tokens'], token_count['output_tokens'], cost_usd))
    conn.commit()
    session_id = c.lastrowid
    conn.close()
    return session_id

def update_session(session_id, date_end, token_count, cost_usd):
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        UPDATE sessions
        SET date_end = ?, inputs_tokens = ?, output_tokens = ?, cost_usd = ?
        WHERE id_session = ?
    ''', (date_end, token_count['input_tokens'], token_count['output_tokens'], cost_usd, session_id))
    conn.commit()
    conn.close()

def get_all_sessions():
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        SELECT id_session, date_start, date_end, inputs_tokens, output_tokens, cost_usd
        FROM sessions
        ORDER BY date_start DESC
    ''')
    results = c.fetchall()
    conn.close()
    if results:
        keys = ["id_session", "date_start", "date_end", "input_tokens", "output_tokens", "cost_usd"]
        return [dict(zip(keys, r)) for r in results]
    return []

def save_application(offerDB_id, id_letter):
    ts = datetime.now().isoformat()
    ts_relance = (datetime.now() + timedelta(days=7)).isoformat()
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO applications (offer_id, id_letter, date_application, date_follow_up)
        VALUES (?, ?, ?, ?)
    ''', (offerDB_id, id_letter, ts, ts_relance))
    conn.commit()
    conn.close()

def get_all_applications():
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        SELECT o.offer_id, o.position, o.entreprise, o.localisation, o.link, o.source, l.id_letter, l.path, 
               a.id_application, a.date_application, a.to_follow_up, a.date_follow_up, a.statut
        FROM applications a
        LEFT JOIN offers o ON a.offer_id = o.offer_id
        LEFT JOIN letters l ON a.id_letter = l.id_letter
    ''')
    results = c.fetchall()
    conn.close()
    if results:
        keys = ["offer_id", "Poste", "Entreprise", "Lieu", "Lien", "Source", "id_letter", "path",
                "id_application", "Postulé le", "A relancer", "Date de relance", "Statut"]
        return [dict(zip(keys, r)) for r in results]

def update_application(id_application, to_follow_up, statut):
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        UPDATE applications
        SET to_follow_up = ?, statut = ?
        WHERE id_application = ?
    ''', (to_follow_up, statut, id_application))
    conn.commit()
    conn.close()