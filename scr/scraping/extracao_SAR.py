import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

link = "https://www.ana.gov.br/sar0/Medicao?dropDownListEstados=14&dropDownListReservatorios=12054&dataInicial=01%2F01%2F2024&dataFinal=01%2F01%2F2026&button=Buscar"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"}

def extrair_dados(link: str) -> pd.DataFrame:

    requisicao = requests.get(link, headers=headers, timeout = 30) #requisitando o site com o link, cabeçalho e timeout
    requisicao.raise_for_status()
    site = BeautifulSoup(requisicao.text, "html.parser") #"abrindo" o site com BS e transformando em um objeto manipulável

    tabela = site.find("table")
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

    return df

def salvar_source_raw(df: pd.DataFrame, caminho: str):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False)
    print(f"Dados salvos em: {caminho}")


if __name__ == "__main__":
    df = extrair_dados(link)
    salvar_source_raw(df, Path("data") / "source_raw" / "dados_SAR" / "medicoes.csv")