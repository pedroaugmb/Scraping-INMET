import re
import os
import requests
from datetime import date
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
 #não precisar abrir o navegador na tela
url = 'https://portal.inmet.gov.br/dadoshistoricos'
navegador = webdriver.Chrome(options = options)

try:
    navegador.get(url) #acessando o site

    #publicações
    publicacoes = WebDriverWait(navegador, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Publicações']")))

    publicacoes.click()

    #boletins
    navegador.find_element(By.XPATH, "//a[normalize-space()='Boletins']").click()
    sleep(1)

    #prognóstico climático
    navegador.find_element(By.CSS_SELECTOR, 'a[href="/boletinsprog"]').click()

    #aba do ano corrente
    ano_atual = date.today().year
    elementos = navegador.find_elements(
        By.XPATH,
        f"//div[@id='d{ano_atual}']//a[contains(@onclick, 'pdfcall')]"
    )

    pasta = os.path.join("data", "source_raw", "downloads")
    os.makedirs(pasta, exist_ok=True)

    print(f"PDFs encontrados: {len(elementos)}")

    for elemento in elementos:
        onclick = elemento.get_attribute("onclick")

        resultado = re.search(r"pdfcall\('([^']+)'", onclick)

        if resultado:
            url_pdf = resultado.group(1)
            nome = url_pdf.split("/")[-1]
            caminho = os.path.join(pasta, nome)

            if os.path.exists(caminho):
                print(f"O arquivo {nome} já existe. Pulando...")
                continue

            resposta = requests.get(url_pdf, timeout=30)
            resposta.raise_for_status()

            with open(caminho, "wb") as arquivo:
                arquivo.write(resposta.content)

            print(f"Baixado: {caminho}")
finally:
    navegador.quit()