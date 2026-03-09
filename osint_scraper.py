import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

sources = {
    "BOE": "https://www.boe.es/buscar/boe.php",
    "DatosGob": "https://datos.gob.es/es/catalogo"
}

all_data = []

for name, url in sources.items():
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        items = soup.find_all('a')
        for item in items[:5]:
            all_data.append({
                "source": name,
                "title": item.get_text(strip=True),
                "url": item.get('href'),
                "date": datetime.date.today()
            })
    except Exception as e:
        print(f"Error capturando {name}: {e}")

# Guardar CSV diario
df = pd.DataFrame(all_data)
csv_file = os.path.join(DATA_DIR, f"osint_{datetime.date.today()}.csv")
df.to_csv(csv_file, index=False)
print(f"Datos guardados en {csv_file}")
