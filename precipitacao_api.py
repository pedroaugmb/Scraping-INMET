import base64
import requests
from pathlib import Path


API = "https://apiclima.inmet.gov.br"

def baixar_imagem(produto, metodo, ano, mes, pasta="data/dados_inmet_clima_api"):
    url = f"{API}/{produto}/{ano}/{metodo}/{mes:02d}"

    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()
    dados = resposta.json()

    print("Resposta da API:")
    print(dados)

    imagem = dados[0]["base64"]
    dados_base64 = imagem.split(",", 1)[1]
    png = base64.b64decode(dados_base64)

    pasta = Path(pasta)
    pasta.mkdir(exist_ok=True)

    caminho = pasta / f"{produto}_{metodo}_{ano}_{mes:02d}.png"
    caminho.write_bytes(png)

    print(f"Imagem salva em: {caminho}")
    return caminho


baixar_imagem(
    produto="prec",
    metodo="desvio",
    ano=2026,
    mes=5,
)