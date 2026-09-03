# Scraping-INMET

Scripts de raspagem (scraping) e um pipeline de ETL + modelagem que juntos coletam dados climáticos e hidrológicos de fontes públicas — [INMET](https://portal.inmet.gov.br/) e [ANA](https://www.ana.gov.br/) — e, no caso dos dados de reservatórios, treinam um modelo de regressão linear sobre eles. A orquestração é feita com Apache Airflow.

## Estrutura de pastas

```
Scraping-INMET/
├── main.py                          # roda o pipeline de reservatórios (ANA/SAR) fora do Airflow
├── requirements.txt
├── scr/
│   ├── scraping/
│   │   ├── navegador.py             # boletins do INMET (PDF) — Selenium
│   │   ├── scraping.py              # dados históricos do INMET (zip) — requests + BeautifulSoup
│   │   ├── precipitacao_api.py      # imagens da API de clima do INMET — requests
│   │   └── extracao_SAR.py          # medições de reservatórios da ANA (SAR) — requests + BeautifulSoup
│   └── analise/
│       ├── transformacao_SAR.py     # limpeza dos dados do SAR + treino da regressão linear
│       └── analise_SAR.py           # métricas do modelo (R², MAE, RMSE) + gráfico da regressão
├── dags/                            # pasta de DAGs do Airflow (AIRFLOW__CORE__DAGS_FOLDER)
│   ├── teste_hello_world.py         # DAG mínima, só para validar a instalação do Airflow
│   └── SAR_dag.py                   # orquestra extração → transformação → modelagem do SAR
├── airflow/                         # AIRFLOW_HOME (airflow.cfg, banco de metadados, logs)
└── data/                            # criada automaticamente pelos scripts, não versionada
    ├── source_raw/
    │   ├── downloads/                    # PDFs baixados por navegador.py
    │   ├── dados_inmet/                  # arquivos baixados por scraping.py
    │   ├── dados_inmet_clima_api/        # imagens baixadas por precipitacao_api.py
    │   └── dados_SAR/dados_completos.csv # tabela bruta extraída por extracao_SAR.py
    └── raw/
        ├── reservatorios_modelo.csv      # dados do SAR já limpos (Cota x Volume)
        └── regressao_cota_volume.png     # gráfico da reta ajustada
```

`scr/` é um pacote Python normal (tem `__init__.py` em cada nível), então os módulos são importados como `scr.scraping.extracao_SAR`, `scr.analise.transformacao_SAR` etc. `data/` e `airflow/` não são versionadas (veja [.gitignore](.gitignore)).

## Dois grupos de scripts

### 1. Raspagem avulsa do INMET (`scr/scraping/`)

Três scripts independentes, cada um baixando um tipo de dado do INMET. Não fazem parte do pipeline orquestrado — são executados manualmente:

| Script | O que faz | Técnica |
|---|---|---|
| [navegador.py](scr/scraping/navegador.py) | Acessa o portal do INMET, navega até *Publicações → Boletins → Prognóstico Climático* e baixa os PDFs da aba do **ano corrente** | Selenium (Chrome headless) |
| [scraping.py](scr/scraping/scraping.py) | Raspa a página de dados históricos e baixa os arquivos `.zip` anexados aos artigos publicados | Requests + BeautifulSoup |
| [precipitacao_api.py](scr/scraping/precipitacao_api.py) | Consulta a API pública de clima do INMET e salva como PNG a imagem (base64) retornada para um produto/método/ano/mês | Requests (consumo de API) |

```bash
python3 scr/scraping/navegador.py
python3 scr/scraping/scraping.py
python3 scr/scraping/precipitacao_api.py
```

Em `precipitacao_api.py`, os parâmetros (`produto`, `metodo`, `ano`, `mes`) são definidos na chamada de `baixar_imagem` no final do arquivo.

### 2. Pipeline de reservatórios ANA/SAR — extração → transformação → modelagem

Coleta o histórico de medições (cota e volume) de um reservatório monitorado pelo [Sistema de Acompanhamento de Reservatórios (SAR)](https://www.ana.gov.br/sar0/Home) da ANA, limpa os dados e treina uma regressão linear de **Volume em função da Cota**. Esse é o único fluxo orquestrado pelo Airflow.

```
extrair_dados()          transformar_dados()         gerar_modelo()
  (extracao_SAR.py)   →    (transformacao_SAR.py)  →   (analise_SAR.py)
  raspa a tabela            filtra Cota/Volume,          treina regressão linear
  do SAR (ANA)              troca "," por ".",           (80/20 treino/teste),
                            remove nulos/duplicatas       calcula R², MAE, RMSE
       ↓                          ↓                            ↓
data/source_raw/dados_SAR/  data/raw/                    data/raw/
  dados_completos.csv         reservatorios_modelo.csv     regressao_cota_volume.png
```

- **[extracao_SAR.py](scr/scraping/extracao_SAR.py)** — `extrair_dados(link)` faz o request à URL de consulta do SAR (com estado, reservatório e período fixados na query string), lê a tabela HTML de medições diárias e devolve um DataFrame; `salvar_source_raw(df, caminho)` grava o CSV bruto.
- **[transformacao_SAR.py](scr/analise/transformacao_SAR.py)** — `transformar_dados(caminho)` lê o CSV bruto, mantém só as colunas `Cota (m)` e `Volume (hm³)`, converte o separador decimal de `,` para `.` e remove nulos/duplicatas; `treinar_modelo_regressao(df)` faz o split treino/teste (80/20) e treina a `LinearRegression`; `salvar_raw(df, caminho)` grava o CSV limpo; `gerar_grafico_dispersao(df, caminho)` plota um scatter simples dos dados (função utilitária, não usada no pipeline principal).
- **[analise_SAR.py](scr/analise/analise_SAR.py)** — `gerar_modelo(df, caminho_grafico=None)` chama `treinar_modelo_regressao`, extrai os coeficientes (`A`, `B`), calcula R², MAE e RMSE sobre o conjunto de teste e, se `caminho_grafico` for informado, salva o gráfico de dispersão com a reta ajustada sobreposta via `gerar_grafico_regressao`.

**Rodar sem o Airflow:**

```bash
python3 main.py
```

[main.py](main.py) executa as três etapas em sequência e imprime os coeficientes (`A`, `B`), as métricas (`R²`, `MAE`, `RMSE`) e o caminho do gráfico gerado.

## Orquestração com Airflow

O projeto usa Apache Airflow 3.x (Task SDK, decorators `@dag`/`@task`). A pasta de DAGs é a `dags/` na raiz do projeto — configurada via variável de ambiente `AIRFLOW__CORE__DAGS_FOLDER` (tem prioridade sobre o `dags_folder` do `airflow/airflow.cfg`), e `AIRFLOW_HOME=./airflow`.

| DAG | Arquivo | O que faz |
|---|---|---|
| `teste_hello_world` | [dags/teste_hello_world.py](dags/teste_hello_world.py) | DAG mínima com duas tasks encadeadas, só para validar que o Airflow está funcionando |
| `pipeline_reservatorios` | [dags/SAR_dag.py](dags/SAR_dag.py) | `extracao() >> transformacao() >> modelagem()` — mesmas funções de `scr/scraping/extracao_SAR.py` e `scr/analise/*`, chamadas como tasks |

Como o DAG file fica fora do pacote `scr`, ele insere a raiz do projeto no `sys.path` manualmente **antes** de importar `scr.*` — isso precisa ser feito assim porque o Airflow processa os DAGs sem depender de o processo estar rodando com o diretório de trabalho na raiz do projeto.

```bash
export AIRFLOW_HOME="$(pwd)/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$(pwd)/dags"

airflow standalone          # sobe scheduler + webserver em http://localhost:8080
# ou, para rodar uma DAG pontualmente sem subir o servidor:
airflow dags test pipeline_reservatorios
```

## Requisitos

- Python 3.12+
- Google Chrome instalado (necessário para o Selenium em [navegador.py](scr/scraping/navegador.py))
- Apache Airflow 3.x, se for usar a orquestração (instalação separada — não está no `requirements.txt` por exigir arquivo de constraints próprio; veja a [documentação oficial](https://airflow.apache.org/docs/apache-airflow/stable/installation/index.html))

## Instalação

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> O Selenium 4 já gerencia o chromedriver automaticamente (Selenium Manager), não sendo necessário instalar o driver manualmente.

## Observações

- `scraping.py` e `navegador.py` verificam se o arquivo já existe na pasta de destino antes de baixar novamente, evitando downloads duplicados.
- Os scripts fazem requisições reais aos portais do INMET e da ANA; use com moderação para não sobrecarregar os servidores (`scraping.py` aguarda 3 segundos entre downloads).
- `data/` é criada automaticamente pelos scripts na primeira execução e não é versionada.
