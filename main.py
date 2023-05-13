import mechanicalsoup
import re
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import blue
import tempfile
import json
from reportlab.platypus import PageBreak
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import matplotlib.pyplot as plt
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.firefox.options import Options

agentes_usuario = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1; rv:9.0.1) Gecko/20100101 Firefox/9.0.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3"
]

def escribirArchivo(texto):
    with open('salida.txt', 'a') as f:
        f.write(texto + '\n')

def crear_grafica(productos):
    if len(productos)==0:
        return
    tiendas = [producto['tienda'] for producto in productos]
    precios = [producto['precio'] for producto in productos]
    promedio = sum(precios) / len(precios)
    promedio_tienda = [promedio] * len(tiendas)

    # Gráfica de promedio de precios
    plt.figure(figsize=(10,5))
    plt.bar(tiendas, precios, label='Precio')
    plt.plot(tiendas, promedio_tienda, color='red', label='Promedio')
    plt.xlabel('Tienda')
    plt.ylabel('Precio')
    plt.title('Comparativa de precios y promedio')
    plt.legend()
    plt.savefig('grafica_promedio.png')

    # Gráfica de comparativa de precio más alto vs precio más bajo
    plt.figure(figsize=(10,5))
    plt.bar(['Precio más bajo', 'Precio más alto'], [min(precios), max(precios)])
    plt.ylabel('Precio')
    plt.title('Comparativa de precio más alto vs precio más bajo')
    plt.savefig('grafica_comparativa.png')

    # Gráfica de distribución de precios
    plt.figure(figsize=(10,5))
    plt.hist(precios, bins=10, edgecolor='black')
    plt.xlabel('Precio')
    plt.ylabel('Número de productos')
    plt.title('Distribución de precios')
    plt.savefig('grafica_distribucion.png')

def enviar_alerta(producto):
    msg = MIMEMultipart()
    msg['From'] = 'correotemporal2202861@gmail.com'
    msg['To'] = 'rafael.leon2861@alumnos.udg.mx'
    msg['Subject'] = f"El precio del producto {producto['titulo'][0:15]} ha bajado!"
    rebaja = float(producto['precioAnterior'])-float(producto['precio'])
    body = f"El precio del producto {producto['titulo']} en la tienda {producto['tienda']} ha bajado de {producto['precioAnterior']} a {producto['precio']} (descuento de {rebaja}). Puedes ver el producto aquí: {producto['url']}"
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(msg['From'], 'zkvoezgyfaddjynp')
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
        
def obtenerNavegador(pagina, form, barraBusqueda, nombreProducto, contieneForm, tipo):
    agente_usuario = random.choice(agentes_usuario)
    print("Agente usuario: ",agente_usuario)
    navegador = mechanicalsoup.StatefulBrowser(user_agent=agente_usuario)
    navegador.open(pagina)
    if tipo in ["cyberpuerta"]:
        time.sleep(20)
    if not contieneForm:
        return navegador
    navegador.select_form(form)
    navegador[barraBusqueda] = nombreProducto
    navegador.submit_selected()
    return navegador

def guardar_precios_json(productos):
    with open("precios.json", "w") as f:
        json.dump(productos, f, ensure_ascii=False, indent=4)

def cargar_precios_json():
    try:
        with open("precios.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
def comparar_precios(productos):
    productosAnteriores = cargar_precios_json()
    productos_bajaron_precio = []
    for producto in productos:
        for producto_anterior in productosAnteriores:
            if (
                producto["titulo"] == producto_anterior["titulo"]
                and producto["tienda"] == producto_anterior["tienda"]
                and producto["precio"] < producto_anterior["precio"]
            ):  
                producto["precioAnterior"] = producto_anterior["precio"]
                productos_bajaron_precio.append(producto)
                break
    return productos_bajaron_precio

def getProductosDDTECH(nombreProducto, palabrasExcluidas):
    navegador = obtenerNavegador("https://ddtech.mx/", 'form[action="https://ddtech.mx/productos/buscar"]',"search", nombreProducto, True, "ddtech")
    productos = []
    for item in navegador.page.select(".product"):
        en_stock = item.select_one(".label.with-stock")
        if not en_stock:
            continue
        titulo = item.select_one("h3.name a").text.strip()
        if any(substring.lower() in titulo.lower() for substring in palabrasExcluidas):
            continue
        url = item.select_one("h3.name a")['href']
        precio_texto = item.select_one(".price").text.strip()
        precio = float(re.sub(r"[^\d.]", "", precio_texto))
        url_imagen = item.select_one(".product-image img")["data-echo"]
        productos.append({
            "titulo": titulo,
            "precio": precio,
            "tienda": "DD Tech",
            "url_imagen": url_imagen,
            "url": url
        })
    return productos

def getProductosCyberpuerta(nombreProducto, palabrasExcluidas):
    navegador = obtenerNavegador("https://www.cyberpuerta.mx/", 'form[name="search"]',"searchparam", nombreProducto, True, "cyberpuerta")
    productos = []
    for item in navegador.page.select(".emproduct"):
        en_stock = item.select_one(".emstock")
        if not en_stock or "Disponibles" not in en_stock.text:
            continue
        titulo = item.select_one(".emproduct_right_title").text.strip()
        if any(substring.lower() in titulo.lower() for substring in palabrasExcluidas):
            continue
        url = item.find('a', class_='emproduct_right_title').get('href')
        precio_texto = item.select_one(".emproduct_right_price_left .price").text.strip()
        precio = float(re.sub(r"[^\d.]", "", precio_texto))
        
        datos_deslizador = item.select_one(".catSlider")["data-cp-prod-slider"]
        urls_imagenes = json.loads(datos_deslizador)
        primera_url_imagen = urls_imagenes[0] if urls_imagenes else None
        productos.append({
            "titulo": titulo, 
            "precio": precio, 
            "tienda": "Cyberpuerta",
            "url_imagen": primera_url_imagen,
            "url": url
        })
    return productos

def getProductosIntercompras(nombreProducto, palabrasExcluidas):
    agente_usuario = random.choice(agentes_usuario)
    print("Agente usuario: ",agente_usuario)
    options = Options()
    options.add_argument('-headless')
    options.add_argument(f'user-agent={agente_usuario}')
    navegador = webdriver.Firefox(options=options)
    url = "https://intercompras.com/ss?keywords="+nombreProducto.replace(" ", "+")
    navegador.get(url)

    if "intercompras" in url:
        WebDriverWait(navegador, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".divContentProductInfo")))

    productos = []
    elementos_productos = navegador.find_elements(By.CSS_SELECTOR,".divContentProductInfo")
    for item in elementos_productos:
        item_text = item.text
        if "Piezas Disponibles: 0" in item_text:
            continue
        titulo = item_text.split('\n')[1] if item_text.startswith('Ahorras') else item_text.split('\n')[0]
        if any(substring.lower() in titulo.lower() for substring in palabrasExcluidas):
            continue
        url = item.find_elements(By.TAG_NAME, 'a')[1].get_attribute('href')
        try:
            precio_texto = re.findall('\$(.*?)\n', item_text)[-2]
        except:
            precio_texto = re.findall('\$(.*?)\n', item_text)[-1]

        precio = float(re.sub(r"[^\d.]", "", precio_texto))
        url_imagen = item.find_elements(By.TAG_NAME, 'img')[1].get_attribute("src")
        
        productos.append({
            "titulo": titulo, 
            "precio": precio, 
            "tienda": "Intercompras",
            "url_imagen": url_imagen,
            "url": url
        })
    
    navegador.quit()
    return productos

def main():
    nombre_producto = "ryzen 5 5600x" 
    palabras_excluidas = ["computadora"]
    precios_ddtech = getProductosDDTECH(nombre_producto, palabras_excluidas)
    precios_cyberpuerta = getProductosCyberpuerta(nombre_producto, palabras_excluidas)
    precios_intercompras = getProductosIntercompras(nombre_producto, palabras_excluidas)
    productos = precios_intercompras + precios_ddtech + precios_cyberpuerta
    productos = sorted(productos, key=lambda k: k["precio"])
    productos_bajaron_precio = comparar_precios(productos)
    guardar_precios_json(productos)
    print("Cantidad de productos: ",len(productos))
    doc = SimpleDocTemplate("reporte.pdf", pagesize=letter)
    contenido = []
    estilos = getSampleStyleSheet()
    estilo_url = ParagraphStyle("EstiloURL", parent=estilos["Normal"], textColor=blue, underline=True)
    for producto in productos:
        contenido.append(Paragraph(f"Producto: {producto['titulo']}", estilos["Title"]))
        contenido.append(Paragraph(f"Precio: {producto['precio']}", estilos["Normal"]))
        contenido.append(Paragraph(f"Tienda: {producto['tienda']}", estilos["Normal"]))
        contenido.append(Paragraph("URL:"))
        contenido.append(Paragraph(f"<a href='{producto['url']}'><u><font color='blue'>{producto['url']}</font></u></a>", estilo_url))
        if producto['url_imagen']:
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
            }
            respuesta = requests.get(producto['url_imagen'], headers=headers, stream=True)  
            if respuesta.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False) as archivo_imagen:
                    for fragmento in respuesta.iter_content(1024):
                        archivo_imagen.write(fragmento)
                    imagen = Image(archivo_imagen.name)
                    imagen.drawWidth = 200  
                    imagen.drawHeight = 200  
                    contenido.append(imagen)
        contenido.append(PageBreak())
    
    try:
        crear_grafica(productos)
        for grafica in ['grafica_promedio.png', 'grafica_comparativa.png', 'grafica_distribucion.png']:
            imagen_grafica = Image(grafica)
            imagen_grafica.drawWidth = 450  
            imagen_grafica.drawHeight = 300
            contenido.append(imagen_grafica)
        for producto in productos_bajaron_precio:
            print("Se envio una alerta de bajada de precio")
            enviar_alerta(producto)
        doc.build(contenido)
        for grafica in ['grafica_promedio.png', 'grafica_comparativa.png', 'grafica_distribucion.png']:
            if os.path.exists(grafica):
                os.remove(grafica)
    except Exception as e:
        print(str(e))    

if __name__ == "__main__":
    main()
