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