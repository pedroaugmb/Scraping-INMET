# Scraping-INMET

Scripts de raspagem (scraping) de dados climáticos e meteorológicos disponibilizados pelo [INMET](https://portal.inmet.gov.br/) (Instituto Nacional de Meteorologia), cobrindo três fontes diferentes: boletins em PDF, dados históricos e imagens da API de clima.

## Sobre o projeto

O repositório reúne três scripts independentes, cada um responsável por coletar um tipo de dado do INMET:

| Script | O que faz | Técnica |
|---|---|---|
| [navegador.py](navegador.py) | Acessa o portal do INMET, navega até *Publicações → Boletins → Prognóstico Climático* e baixa os PDFs disponíveis para o ano de 2025 | Selenium (Chrome headless) |
| [scraping.py](scraping.py) | Raspa a página de dados históricos e baixa os arquivos anexados aos artigos publicados | Requests + BeautifulSoup |
| [precipitacao_api.py](precipitacao_api.py) | Consulta a API pública de clima do INMET e salva como PNG a imagem (base64) retornada para um produto/método/ano/mês | Requests (consumo de API) |

## Estrutura de pastas

```
Scraping-INMET/
├── navegador.py
├── scraping.py
├── precipitacao_api.py
├── requirements.txt
└── data/
    ├── downloads/               # PDFs baixados por navegador.py
    ├── dados_inmet/              # Arquivos baixados por scraping.py
    └── dados_inmet_clima_api/    # Imagens baixadas por precipitacao_api.py
```

A pasta `data/` (e suas subpastas) é criada automaticamente pelos scripts na primeira execução e **não é versionada** (veja [.gitignore](.gitignore)).

## Requisitos

- Python 3.12+
- Google Chrome instalado (necessário para o Selenium em [navegador.py](navegador.py))

## Instalação

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> O Selenium 4 já gerencia o chromedriver automaticamente (Selenium Manager), não sendo necessário instalar o driver manualmente.

## Uso

Cada script é independente e pode ser executado separadamente:

```bash
# Baixa os PDFs de boletins de prognóstico climático (2025)
python3 navegador.py

# Raspa os dados históricos e baixa os arquivos anexados
python3 scraping.py

# Baixa uma imagem de precipitação da API de clima
python3 precipitacao_api.py
```

Em [precipitacao_api.py](precipitacao_api.py), os parâmetros de consulta (`produto`, `metodo`, `ano`, `mes`) são definidos na chamada da função `baixar_imagem` no final do arquivo e podem ser ajustados conforme necessário.

## Observações

- `scraping.py` verifica se o arquivo já existe na pasta de destino antes de baixar novamente, evitando downloads duplicados.
- Os scripts fazem requisições reais ao portal do INMET; use com moderação para não sobrecarregar o servidor (`scraping.py` já aguarda 3 segundos entre downloads).
