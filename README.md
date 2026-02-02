# Analiz--de-business
Problema de probă în cadrul companiei Crowe Ţurcan Mikhailenko

# Documentație proiect – Telegram Bot pentru analiza business

## 1. Introducere

Acest proiect reprezintă un Telegram Bot pentru analiza nivelului de conformitate și maturitate a unei afaceri**, prin intermediul unui set de întrebări structurate pe categorii. Utilizatorul răspunde la întrebări, iar aplicația generează un raport PDF cu rezultatele și recomandări.

Proiectul a fost realizat cu ajutorul limbajului Python, utilizând:

* Telegram Bot API
* SQLite pentru stocarea datelor
* Generare PDF pentru raport final


## 2. Scopul proiectului

Scopul proiectului este:

* evaluarea stării unei afaceri din punct de vedere juridic, financiar și organizațional;
* automatizarea procesului de chestionare;
* generarea unui raport final structurat;
* oferirea unui instrument digital simplu pentru antreprenori.


## 3. Funcționalități principale

* Selectarea limbii
* Pornirea testului de analiză
* Afișarea întrebărilor din baza de date (JSON)
* Salvarea răspunsurilor utilizatorului
* Calcularea scorului
* Generarea raportului PDF
* Vizualizarea rezultatului în Telegram


## 4. Structura proiectului

### 4.1 Structura generală


app/
 ├── bd_sqlite/
 ├── bot/
 ├── configurare/
 ├── logica/
 ├── data/
 ├── pdf/
 ├── scripts/
 ├── main.py



## 5. Descrierea modulelor

### 5.1 Modulul bd_sqlite

Conține logica pentru lucrul cu baza de date SQLite.

Fișiere:

* `conexiune.py` – gestionează conexiunea la baza de date
* `scheme_bd.py` – definește structura tabelelor
* `models.py` – modele pentru date
* `function_bd.py` – funcții CRUD (create, read, update, delete)

Rol: stocarea utilizatorilor, răspunsurilor și rezultatelor.


## 5.2 Modulul bot

Conține logica principală a botului Telegram.

Submodule:

## gestonari/

* `start.py` – comandă /start
* `meniu.py` – meniul principal
* `question.py` – afișarea întrebărilor
* `rezultate.py` – afișarea rezultatului
* `raportPdf.py` – trimiterea raportului PDF

## tastatura/

* `cabinet_keyboard.py` – tastatură pentru meniu
* `limba.py` – selectarea limbii
* `locatie_keyboard.py` – locație
* `meniuButton.py` – butoane
* `testButton.py` – butoane pentru test

## Users/

* `utilizator.py` – model utilizator

---

## 5.3 Modulul logica

* `scorul.py` – calcularea scorului final
* `State.py` – gestionarea stării conversației

## 5.4 Modulul pdf

* `generare_pdf.py` – generarea fișierului PDF
* `assets/background.jpg` – fundal pentru raport


## 5.5 Modulul scripts

* `load_intrebari.py` – încărcarea întrebărilor din JSON

## 5.6 Modulul data

* `intrebari.json` – lista întrebărilor
* `telegram_bot.db` – baza de date SQLite


## 6. Fluxul de funcționare

1. Utilizatorul pornește botul cu /start
2. Selectează limba
3. Apasă "Începe testul"
4. Primește întrebări una câte una
5. Răspunde (Da/Nu)
6. Se calculează scorul
7. Se generează raportul PDF
8. Raportul este trimis utilizatorului


## 7. Tehnologii utilizate

* Python 3.x
* python-telegram-bot / aiogram
* SQLite3
* JSON
* ReportLab / FPDF (pentru PDF)
* Docker (opțional)


## 8. Instalare și rulare

Aplicația poate fi rulată folosind **Docker**, fără a instala manual toate dependențele.

## 8.1 Instalare Docker

1. Descărcați și instalați Docker:

   * Windows / macOS: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
   * Linux: folosind managerul de pachete specific distribuției

2. Verificați instalarea:

```bash
docker --version
docker-compose --version
```


### 8.2 Rulare aplicație cu Docker

1. Deschideți terminalul în directorul proiectului (unde se află fișierul `docker-compose.yml`).

2. Rulați comanda:

```bash
docker compose up --build
```

3. Botul va porni automat și se va conecta la Telegram API.


### 8.3 Rulare fără Docker (opțional)

1. Instalare dependințe:

```bash
pip install -r requirements.txt
```

2. Rulare aplicație:

```bash
python main.py
```

## 9. Posibile îmbunătățiri

* Adăugare interfață web
* Sistem de autentificare
* Mai multe tipuri de rapoarte
* Export Excel
* Panou de administrare

---

## 10. Concluzie

Proiectul demonstrează utilizarea combinată a bazelor de date, botului Telegram și generării de rapoarte PDF într-o aplicație practică pentru analiză business.

Aplicația poate fi utilizată ca instrument de evaluare inițială pentru antreprenori și consultanți.
