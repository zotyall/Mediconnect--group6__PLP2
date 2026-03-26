#!/usr/bin/env python3
"""MediConnect — compact rewrite (~350 lines). Same features, same DB schema."""

import sqlite3
from datetime import datetime

DB = "mediconnect.db"
ADMIN_PW = "admin123"
PHARMACISTS = ["alice", "bob"]

# ── Static config ────────────────────────────────────────────────────────────

INSURANCES = {
    "RSSB": ["RSSB001","RSSB002","RSSB100"], 
    "MMI": ["MMI001","MMI002","MMI200"],
    "SORAS":["SOR001","SOR002","SOR300"],     
    "BRITAM":["BRI001","BRI002","BRI400"],
}

SICKNESS_MEDS = {
    "Malaria":      ["Artemether","Lumefantrine","Quinine"],
    "Flu":          ["Paracetamol","Vitamin C","Antihistamine"],
    "Diabetes":     ["Metformin","Insulin"],
    "Hypertension": ["Amlodipine"],
    "Typhoid":      ["Ciprofloxacin"],
    "Stomach pain": ["Omeprazole","Buscopan"],
}

PHARMACIES = {
    "PharmaCare Plus":   {"km":2.5,"rating":4.8,"ins":["RSSB","MMI"], "sick":["Malaria","Flu","Typhoid"]},
    "City MedShop":      {"km":3.1,"rating":4.5,"ins":["SORAS","BRITAM"], "sick":["Diabetes","Hypertension","Stomach pain"]},
    "HealthFirst":       {"km":4.0,"rating":4.2,"ins":["RSSB","SORAS"], "sick":["Flu","Hypertension","Malaria"]},
    "MediQuick":         {"km":1.8,"rating":4.6,"ins":["MMI","BRITAM"], "sick":["Typhoid","Diabetes","Stomach pain"]},
    "Kigali MedCenter":  {"km":2.1,"rating":4.7,"ins":["RSSB","SORAS"], "sick":["Malaria","Typhoid","Hypertension"]},
    "CurePoint":         {"km":1.2,"rating":4.9,"ins":["RSSB","MMI","BRITAM"], "sick":["Malaria","Flu","Typhoid","Stomach pain"]},
    "MediPlus Rwanda":   {"km":2.9,"rating":4.4,"ins":["BRITAM","SORAS","MMI"], "sick":["Typhoid","Flu","Stomach pain"]},
    "SafeHealth Clinic": {"km":3.5,"rating":4.6,"ins":["BRITAM","RSSB","SORAS"], "sick":["Flu","Malaria","Hypertension","Stomach pain"]},
    "People's Pharmacy": {"km":5.2,"rating":3.9,"ins":["RSSB","BRITAM","MMI","SORAS"],"sick":["Flu","Malaria","Stomach pain"]},
}

SEED_STOCK = {
    "Paracetamol":30,"Artemether":20,"Lumefantrine":20,"Quinine":15,
    "Vitamin C":25,"Antihistamine":18,"Metformin":20,"Insulin":10,
    "Ciprofloxacin":20,"Omeprazole":20,"Amlodipine":15,"Buscopan":22,
}

# ── DB ───────────────────────────────────────────────────────────────────────

def cx():
    return sqlite3.connect(DB)

def init_db():
    with cx() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS patients  (username TEXT PRIMARY KEY, password TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS history   (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT,
                date TEXT, sickness TEXT, medicines TEXT, insurance TEXT, pharmacy TEXT);
            CREATE TABLE IF NOT EXISTS stock     (medicine TEXT PRIMARY KEY, quantity INTEGER);
            CREATE TABLE IF NOT EXISTS stock_log (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT,
                action TEXT, medicine TEXT, qty INTEGER, before INTEGER, after INTEGER, by_whom TEXT, patient TEXT);
        """)
        if not c.execute("SELECT 1 FROM stock LIMIT 1").fetchone():
            c.executemany("INSERT INTO stock VALUES (?,?)", SEED_STOCK.items())

def q(sql, params=()):
    with cx() as c:
        return c.execute(sql, params).fetchall()

def run(sql, params=()):
    with cx() as c:
        c.execute(sql, params)

def get_stock():
    return dict(q("SELECT medicine, quantity FROM stock ORDER BY medicine"))

def dispense(med, by, patient):
    """Deduct 1 unit, log it, flag if out of stock. Returns False if unavailable."""
    stock = get_stock()
    if med not in stock or stock[med] <= 0:
        return False
    before, after = stock[med], stock[med] - 1
    run("UPDATE stock SET quantity=? WHERE medicine=?", (after, med))
    log("Dispensed", med, by, before=before, after=after, patient=patient)
    if after == 0:
        log("Out of stock", med, by, before=before, after=0)
    return True

def log(action, med, by, qty=None, before=None, after=None, patient=None):
    run("INSERT INTO stock_log (date,action,medicine,qty,before,after,by_whom,patient) VALUES (?,?,?,?,?,?,?,?)",
        (ts(), action, med, qty, before, after, by, patient))
    

def hr():   print("\n" + "-" * 40)
def go():   input("\nPress Enter to continue...")
def ts():   return datetime.now().strftime("%Y-%m-%d %H:%M")

def menu(title, options):
    """options = list of (label, callable). Returns when user picks 'Back/Logout'."""
    while True:
        hr(); print(title); hr()
        for i, (label, _) in enumerate(options, 1):
            print(f"  {i}. {label}")
        last = str(len(options))
        c = input("\nYour choice: ").strip()
        if c == last:
            break
        elif c.isdigit() and 1 <= int(c) < len(options):
            options[int(c)-1][1]()
        else:
            print("Invalid choice.")

def pick(items, prompt):
    for i, x in enumerate(items, 1): print(f"  {i}. {x}")
    while True:
        c = input(f"\n{prompt}: ").strip()
        if c.isdigit() and 1 <= int(c) <= len(items):
            return items[int(c)-1]
        print("  Invalid. Try again.")

def ask_int(prompt):
    try:    return int(input(prompt).strip())
    except: return None


# ── Shared views ─────────────────────────────────────────────────────────────

def show_stock():
    hr()
    for med, qty in get_stock().items():
        print(f"  {med:<20}: {qty}  {'LOW' if qty<=5 else ''}")
    go()

def show_history(username):
    hr(); print(f"HISTORY — {username}"); hr()
    rows = q("SELECT date,sickness,medicines,pharmacy FROM history WHERE username=? ORDER BY id", (username,))
    if not rows: print("No records yet.")
    else:
        for i,(date,sick,meds,pharm) in enumerate(rows,1):
            print(f"\n  {i}. {date} | {sick} | {meds} | {pharm}")
    go()

# ── Admin ────────────────────────────────────────────────────────────────────

def admin_menu():
    hr()
    if input("Admin password: ").strip() != ADMIN_PW:
        print(" Wrong password."); return

    def all_patients():
        rows = q("SELECT username FROM patients ORDER BY username")
        hr()
        [print(f"  {i}. {r[0]}") for i,r in enumerate(rows,1)] if rows else print("No patients.")
        go()

    def patient_history():
        u = input("Patient username: ").strip()
        if not q("SELECT 1 FROM patients WHERE username=?", (u,)): print(" Not found."); go(); return
        show_history(u)

    def list_pharmacists():
        hr()
        [print(f"  {i}. {p.capitalize()}") for i,p in enumerate(PHARMACISTS,1)]
        go()

    def add_pharmacist():
        n = input("Name: ").strip().lower()
        if n in PHARMACISTS: print("Already exists.")
        else: PHARMACISTS.append(n); print(f" {n.capitalize()} added.")
        go()

    def remove_pharmacist():
        n = input("Name to remove: ").strip().lower()
        if n not in PHARMACISTS: print(" Not found.")
        else: PHARMACISTS.remove(n); print(f" Removed.")
        go()

    menu("ADMIN MENU", [
        ("View all patients",    all_patients),
        ("View patient history", patient_history),
        ("View pharmacists",     list_pharmacists),
        ("Add pharmacist",       add_pharmacist),
        ("Remove pharmacist",    remove_pharmacist),
        ("View stock",           show_stock),
        ("Logout",               None),
    ])