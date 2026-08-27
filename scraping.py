import requests
from bs4 import BeautifulSoup
from pathlib import Path

link = ("https://portal.inmet.gov.br/dadoshistoricos") #texto com o link do site que será raspado
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"}
#por onde estou fazendo a requisição, para não ser bloqueado pelo site

pasta = Path("dados_inmet") #criando uma pasta para armazenar os dados raspados
pasta.mkdir(exist_ok=True) #comando para criar a pasta, caso ela não exista

requisicao = requests.get(link, headers=headers) #requisitando o site com o link e o cabeçalho
site = BeautifulSoup(requisicao.text, "html.parser") #"abrindo" o site com BS e transformando em um objeto manipulável
doc = site.find_all("article", class_="post-preview") #variavel que armazena o conteudo que quero raspar, no caso, todos os artigos com a classe post-preview
print(doc)

for artigo in doc:
    link = artigo.find("a") #busca pelos artigos

    if link:
        url_arquivo = link.get("href") #acesso a url do arquivo
        nome = url_arquivo.split("/")[-1] 

        print(f"Baixando: {nome}")

        arquivo = requests.get(url_arquivo, headers=headers)

        caminho = pasta / nome

        with open(caminho, "wb") as f:
            f.write(arquivo.content)

        print(f"Salvo em: {caminho}")