import re
import os
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# options = Options()
# options.add_argument("--headless=new") #não precisar abrir o navegador na tela
url = 'https://portal.inmet.gov.br/dadoshistoricos'
navegador = webdriver.Chrome()
navegador.get(url) #acessando o site

#publicações
publicacoes = WebDriverWait(navegador, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Publicações']")))

publicacoes.click()

#boletins
navegador.find_element(By.XPATH, "//a[normalize-space()='Boletins']").click()
sleep(1)

#prognóstico climático
navegador.find_element(By.CSS_SELECTOR, 'a[href="/boletinsprog"]').click()

#aba do ano de 2025
elementos = navegador.find_elements(
    By.XPATH,
    "//div[@id='d2025']//a[contains(@onclick, 'pdfcall')]"
)

pasta = "downloads"
os.makedirs(pasta, exist_ok=True)

print(f"PDFs encontrados: {len(elementos)}")

for elemento in elementos:
    onclick = elemento.get_attribute("onclick")

    resultado = re.search(r"pdfcall\('([^']+)'", onclick)

    if resultado:
        url_pdf = resultado.group(1)
        nome = url_pdf.split("/")[-1]

        resposta = requests.get(url_pdf, timeout=30)
        resposta.raise_for_status()

        caminho = os.path.join(pasta, nome)

        with open(caminho, "wb") as arquivo:
            arquivo.write(resposta.content)

        print(f"Baixado: {caminho}")