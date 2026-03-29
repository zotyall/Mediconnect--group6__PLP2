# MediConnect

MediConnect is a terminal-based healthcare platform built for Rwanda that connects patients to nearby pharmacies based on their insurance and condition. Here's how it works:

**Step 1** — Run the app with `python mediconnect.py`. No installs needed, the database sets itself up automatically with 12 pre-seeded medicines ready to go.

**Step 2** — Pick your role from the main menu: Patient, Pharmacist, or Admin.

**Step 3 (Patient)** — Register a new account with a username and password, or log in with your existing credentials. Once in, select your insurance provider from RSSB, MMI, SORAS, or BRITAM.

**Step 4** — Pick what you're sick from. The app supports Malaria, Flu, Diabetes, Hypertension, Typhoid, and Stomach pain. It then finds matching pharmacies across Kigali that accept your insurance and treat your condition, sorted by rating so the best option shows first.

**Step 5** — The app shows you the distance to the pharmacy and the medicines you'll receive. Confirm you got them and an e-prescription gets saved to your account history automatically. You can also view it on the spot.

**Step 6 (Pharmacist)** — Log in by name using `alice` or `bob`. From here you can view current stock levels, add new medicines, restock existing ones, dispense medicines directly to a patient, and view the full stock log with before and after quantities for every action.

**Step 7 (Admin)** — Log in with the password `admin123`. Admins can view all registered patients, check any patient's prescription history, add or remove pharmacists, and monitor inventory across the platform.

**Step 8** — Every action across all roles — dispensing, restocking, prescriptions — is logged with a timestamp automatically so nothing goes untracked.
