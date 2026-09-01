from scr.scraping.extracao_SAR import extrair_dados, salvar_source_raw
from scr.analise.transformacao_SAR import (transformar_dados, salvar_raw)
from scr.analise.analise_SAR import gerar_modelo


URL = "https://www.ana.gov.br/sar0/Medicao?dropDownListEstados=14&dropDownListReservatorios=12054&dataInicial=01%2F01%2F2024&dataFinal=01%2F01%2F2026&button=Buscar"

SOURCE_RAW = "data/source_raw/dados_SAR/dados_completos.csv"
RAW = "data/raw/reservatorios_modelo.csv"
GRAFICO_REGRESSAO = "data/raw/regressao_cota_volume.png"


def main():

    print("Iniciando extração...")

    df = extrair_dados(URL)

    salvar_source_raw(df, SOURCE_RAW)

    print("Extração concluída.")

    print("Iniciando transformação...")

    df = transformar_dados(SOURCE_RAW)

    salvar_raw(df, RAW)

    print("Transformação concluída.")

    print("Iniciando modelagem...")

    resultado = gerar_modelo(df, GRAFICO_REGRESSAO)

    print(f"A = {resultado['A']}")
    print(f"B = {resultado['B']}")
    print(f"R² = {resultado['R2']}")
    print(f"MAE = {resultado['MAE']}")
    print(f"RMSE = {resultado['RMSE']}")
    print(f"Gráfico salvo em: {GRAFICO_REGRESSAO}")

    print("Pipeline concluída.")


if __name__ == "__main__":
    main()