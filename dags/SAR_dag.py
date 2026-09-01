from airflow.sdk import dag, task
import pendulum

from scr.scraping.extracao_SAR import extrair_dados, salvar_source_raw
from scr.analise.transformacao_SAR import (transformar_dados, salvar_raw)
from scr.analise.analise_SAR import gerar_modelo


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
        salvar_source_raw(df, "data/source_raw/dados_SAR/dados_completos.csv")

    @task
    def transformacao():

        df = transformar_dados("data/source_raw/dados_SAR/dados_completos.csv")
        salvar_raw(df, "data/raw/reservatorios_modelo.csv")

    @task
    def modelagem():

        df = transformar_dados("data/raw/reservatorios_modelo.csv")
        resultado = gerar_modelo(df)

        print(f"A = {resultado['A']}")
        print(f"B = {resultado['B']}")

        return resultado

    extracao() >> transformacao() >> modelagem()


pipeline_reservatorios()