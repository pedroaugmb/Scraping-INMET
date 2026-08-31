import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

link = "https://www.ana.gov.br/sar0/Medicao?dropDownListEstados=14&dropDownListReservatorios=12054&dataInicial=01%2F01%2F2024&dataFinal=01%2F01%2F2026&button=Buscar"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"}

pasta = Path("data") / "source_raw" / "dados_SAR"
pasta.mkdir(parents=True, exist_ok=True)

requisicao = requests.get(link, headers=headers, timeout = 30) #requisitando o site com o link, cabeçalho e timeout
site = BeautifulSoup(requisicao.text, "html.parser") #"abrindo" o site com BS e transformando em um objeto manipulável

# print(requisicao.status_code)
# print(site.title.text)

tabela = site.find("table")
# print(tabela)
# print(tabela.prettify()[:5000])
linhas = tabela.find_all("tr")
dados = []

for linha in linhas:
    colunas = linha.find_all(["th", "td"])
    dados.append([
        coluna.get_text(strip=True)
        for coluna in colunas
    ])

df = pd.DataFrame(dados[1:], columns=dados[0])
print(df.head())
print(df.info())

arquivo = pasta / "dados_SAR.csv"
df.to_csv(arquivo, index=False, encoding="utf-8-sig")
print(f"Arquivo salvo em: {arquivo}")