from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

caminho_source_raw = Path("data") / "source_raw" / "dados_SAR" / "medicoes.csv"
caminho_saida = Path("data") / "raw" / "dispersao_cota_volume.png"
caminho_destino = Path("data") / "raw" / "dados_SAR_tratado.csv"

def transformar_dados(caminho_source_raw: Path) -> pd.DataFrame:
    """Lê, filtra, limpa os tipos de dados e remove inconsistências."""
    df = pd.read_csv(caminho_source_raw)

    #seleciona apenas as colunas necessárias
    df = df[["Cota (m)", "Volume (hm³)"]].copy()

    #mudando formato "," para "."
    df["Cota (m)"] = (df["Cota (m)"].str.replace(",", ".", regex=False).astype(float))
    df["Volume (hm³)"] = (df["Volume (hm³)"].str.replace(",", ".", regex=False).astype(float))

    #limpeza de nulos e duplicatas
    df = df.dropna()
    df = df.drop_duplicates()
    return df


def gerar_grafico_dispersao(df: pd.DataFrame, caminho_saida: Path) -> None:
    """Gera e salva o gráfico de dispersão."""
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.scatter(df["Cota (m)"], df["Volume (hm³)"], alpha=0.7)
    plt.xlabel("Cota (m)")
    plt.ylabel("Volume (hm³)")
    plt.title("Relação entre Cota e Volume")

    plt.savefig(caminho_saida, bbox_inches="tight", dpi=300)
    plt.close()  # Libera a memória da figura gerada


def treinar_modelo_regressao(df: pd.DataFrame):
    """Realiza o split dos dados e treina o modelo de Regressão Linear."""
    X = df[["Cota (m)"]]
    y = df["Volume (hm³)"]

    #modelo treinado com 80% dos dados deixando 20% para teste:
    X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo = LinearRegression()
    modelo.fit(X_treino, y_treino)

    return modelo, X_teste, y_teste


def salvar_raw(df: pd.DataFrame, caminho_destino: Path) -> None:
    """Salva o DataFrame limpo em disco."""
    caminho_destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho_destino, index=False)