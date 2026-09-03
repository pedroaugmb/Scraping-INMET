import os
import sys
import pendulum
from pathlib import Path

# Força o Python a enxergar a pasta raiz 'Scraping-INMET' (precisa vir antes dos imports de 'scr')
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from airflow.sdk import dag, task

from scr.scraping.extracao_SAR import extrair_dados, salvar_source_raw
from scr.analise.transformacao_SAR import (transformar_dados, salvar_raw)
from scr.analise.analise_SAR import gerar_modelo

URL_ANA = "https://www.ana.gov.br/sar0/Medicao?dropDownListEstados=14&dropDownListReservatorios=12054&dataInicial=01%2F01%2F2024&dataFinal=01%2F01%2F2026&button=Buscar"

PATH_SOURCE_RAW = os.path.join(RAIZ_PROJETO, "data/source_raw/dados_SAR/dados_completos.csv")
PATH_RAW = os.path.join(RAIZ_PROJETO, "data/raw/reservatorios_modelo.csv")

@dag(
    dag_id="pipeline_reservatorios",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["ANA", "reservatorios", "ML"]
)
def pipeline_reservatorios():

    @task
    def extracao():

        df = extrair_dados(URL_ANA)
        salvar_source_raw(df, PATH_SOURCE_RAW)

    @task
    def transformacao():

        df = transformar_dados(PATH_SOURCE_RAW)
        salvar_raw(df, PATH_RAW)

    @task
    def modelagem():

        import pandas as pd
        df = pd.read_csv(PATH_RAW)
        resultado = gerar_modelo(df)

        print(f"A = {resultado['A']}")
        print(f"B = {resultado['B']}")

        return resultado

    extracao() >> transformacao() >> modelagem()


pipeline_reservatorios()