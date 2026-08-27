import time 
import requests
from pathlib import Path
from bs4 import BeautifulSoup

link = ("https://portal.inmet.gov.br/dadoshistoricos") #texto com o link do site que será raspado
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"}
#por onde estou fazendo a requisição, para não ser bloqueado pelo site

pasta = Path("data") / "dados_inmet" #criando uma pasta para armazenar os dados raspados
pasta.mkdir(parents=True, exist_ok=True) #comando para criar a pasta, caso ela não exista

requisicao = requests.get(link, headers=headers) #requisitando o site com o link e o cabeçalho
site = BeautifulSoup(requisicao.text, "html.parser") #"abrindo" o site com BS e transformando em um objeto manipulável
doc = site.find_all("article", class_="post-preview") #variavel que armazena o conteudo que quero raspar, no caso, todos os artigos com a classe post-preview
print(doc)

for artigo in doc:
    link_tag = artigo.find("a") 

    if link_tag:
        url_arquivo = link_tag.get("href")
        nome = url_arquivo.split("/")[-1]
        caminho = pasta / nome

        # verifica se o arquivo já existe na pasta para não baixar de novo
        if caminho.exists():
            print(f"O arquivo {nome} já existe. Pulando...")
            continue
        print(f"Baixando: {nome}")
        try:
            # faz o request com stream=True e um timeout para evitar travamentos
            resposta = requests.get(url_arquivo, headers=headers, stream=True, timeout=30)
            resposta.raise_for_status() # lança um erro se o status não for 200 (OK)

            # grava o arquivo no disco em pequenos blocos (chunks de 8KB)
            with open(caminho, "wb") as f:
                for chunk in resposta.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"Salvo com sucesso em: {caminho}")

        except Exception as e:
            print(f"Erro ao tentar baixar {nome}. Detalhe: {e}")
        
        # pausa de 3 segundos antes da próxima iteração
        print("Aguardando 3 segundos...")
        time.sleep(3)