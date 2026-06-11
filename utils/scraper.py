import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def capturar_json_directo(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    # Mantenemos tu configuración por si la necesitas más adelante
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"}) 
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        
        # Esperamos a que cargue. Si aparece el reto de Cloudflare de Sofascore,
        # este tiempo te da margen para que se resuelva (o lo resuelvas manualmente)
        time.sleep(1)
        
        # Al ser un JSON directo, Chrome lo renderiza dentro de un tag <pre> o <body>
        try:
            texto_api = driver.find_element(By.TAG_NAME, "pre").text
        except NoSuchElementException:
            texto_api = driver.find_element(By.TAG_NAME, "body").text
        driver.quit()
        # Convertimos la cadena de texto directamente a un diccionario de Python
        diccionario_json = json.loads(texto_api)
        return diccionario_json

    except json.JSONDecodeError:
        print("Error: El contenido no es un JSON válido. Posiblemente se quedó bloqueado en el control de Cloudflare.")
        driver.quit()
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        driver.quit()
        return None