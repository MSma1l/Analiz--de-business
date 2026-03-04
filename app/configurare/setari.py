import os  # Importa modulul os pentru lucrul cu variabilele de mediu
from dotenv import load_dotenv  # Importa functia load_dotenv pentru incarcarea variabilelor din fisierul .env

load_dotenv()  # Incarca variabilele de mediu din fisierul .env in aplicatie

TOKEN = os.getenv("TOKEN")  # Obtine valoarea token-ului botului Telegram din variabilele de mediu
