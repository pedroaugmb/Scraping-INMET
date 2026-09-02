import os
import pendulum
from airflow.decorators import dag, task

from scr.scraping.extracao_SAR import extrair_dados, salvar_source_raw
from scr.analise.transformacao_SAR import (transformar_dados, salvar_raw)
from scr.analise.analise_SAR import gerar_modelo

BASE_DIR = "/home/pedro/teste-etl/Scraping-INMET/airflow"
PATH_SOURCE_RAW = os.path.join(BASE_DIR, "data/source_raw/dados_SAR/dados_completos.csv")
PATH_RAW = os.path.join(BASE_DIR, "data/raw/reservatorios_modelo.csv")

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

        url = "URL_DA_ANA"
        df = extrair_dados(url)
        salvar_source_raw(df, PATH_SOURCE_RAW)

    @task
    def transformacao():

        df = transformar_dados(PATH_SOURCE_RAW)
        salvar_raw(df, PATH_RAW)

    @task
    def modelagem():

        df = transformar_dados(PATH_RAW)
        resultado = gerar_modelo(df)

        print(f"A = {resultado['A']}")
        print(f"B = {resultado['B']}")

        return resultado

    extracao() >> transformacao() >> modelagem()


pipeline_reservatorios()