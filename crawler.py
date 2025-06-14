# Usaremos las librerías que ya tienes: requests y beautifulsoup4
# También añadiremos 'csv' y 'time', que vienen por defecto con Python
import requests
from bs4 import BeautifulSoup
import csv
import time # Importante para ser amables con el servidor que visitamos

# --- CONFIGURACIÓN ---
# La URL donde están listadas las categorías de artículos
START_URL = "https://help.gohighlevel.com/support/home"
# El nombre del archivo que vamos a crear con toda la información
OUTPUT_FILE = "ghl_knowledge_base.csv"

print("Iniciando el proceso de scraping de la base de conocimiento de GHL...")

# --- PASO 1: ENCONTRAR TODOS LOS ENLACES A LOS ARTÍCULOS ---

# Hacemos una petición a la página principal de ayuda
try:
    page = requests.get(START_URL)
    page.raise_for_status() # Esto generará un error si la página no responde correctamente
    soup = BeautifulSoup(page.content, "html.parser")

    article_links = []
    # Buscamos todas las listas de artículos en la página de inicio
    # (Inspeccionando la página, vi que los links están en una estructura <ul> con la clase 'article-list')
    for article_list in soup.find_all("ul", class_="article-list"):
        # Dentro de cada lista, encontramos cada elemento de enlace <a>
        for link in article_list.find_all("a"):
            href = link.get("href")
            # Nos aseguramos de que sea un enlace a un artículo y construimos la URL completa
            if href and href.startswith("/support/solutions/articles/"):
                full_url = "https://help.gohighlevel.com" + href
                if full_url not in article_links:
                    article_links.append(full_url)
    
    print(f"Se encontraron {len(article_links)} artículos de ayuda únicos. Empezando extracción...")

except requests.exceptions.RequestException as e:
    print(f"Error al acceder a la página principal de ayuda: {e}")
    exit() # Si no podemos acceder a la página principal, detenemos el script


# --- PASO 2: EXTRAER TÍTULO Y CONTENIDO DE CADA ARTÍCULO Y GUARDAR EN CSV ---

# Abrimos (o creamos) nuestro archivo CSV en modo escritura
with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
    # Definimos los nombres de las columnas
    fieldnames = ['titulo', 'contenido']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Escribimos la primera fila con los nombres de las columnas
    writer.writeheader()

    # Iteramos sobre cada URL de artículo que encontramos
    for url in article_links:
        try:
            print(f"Procesando: {url}")
            article_page = requests.get(url)
            article_page.raise_for_status()
            article_soup = BeautifulSoup(article_page.content, "html.parser")

            # Extraemos el título (El título está en una etiqueta <h1> con la clase 'article-title')
            title_element = article_soup.find("h1", class_="article-title")
            title = title_element.get_text(strip=True) if title_element else "Título no encontrado"

            # Extraemos el contenido (El contenido está en una etiqueta <div> con la clase 'article-body')
            content_element = article_soup.find("div", class_="article-body")
            
            if content_element:
                # Usamos tu excelente lógica para limpiar el HTML de scripts y estilos
                [s.decompose() for s in content_element(["script", "style", "noscript"])]
                content = content_element.get_text(separator=' ', strip=True)
            else:
                content = "Contenido no encontrado"

            # Escribimos la fila con el título y el contenido en nuestro CSV
            writer.writerow({'titulo': title, 'contenido': content})

            # Esperamos 1 segundo entre cada petición para no sobrecargar el servidor de GHL
            time.sleep(1) 
            
        except Exception as e:
            print(f"-------> Error procesando la URL {url}: {e}")
            # Continuamos con el siguiente link aunque uno falle
            continue

print(f"¡Proceso completado! Los datos se han guardado en el archivo '{OUTPUT_FILE}'.")