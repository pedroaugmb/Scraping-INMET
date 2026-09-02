from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from scr.analise.transformacao_SAR import treinar_modelo_regressao

def obter_parametros(modelo):
    a = modelo.coef_[0]
    b = modelo.intercept_

    return a, b

def gerar_grafico_regressao(X_teste, y_teste, previsoes, caminho_saida: Path) -> None:
    """Plota os dados de teste e a reta ajustada pelo modelo."""
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    #gera gráfico o gráfio de treino, com os dados de treino e reta gerada pelo modelo sobrepostos  
    x = X_teste["Cota (m)"]
    ordem = x.values.argsort()

    plt.figure(figsize=(8, 5))
    plt.scatter(x, y_teste, alpha=0.7, label="Dados reais (teste)")
    plt.plot(x.values[ordem], previsoes[ordem], color="red", linewidth=2, label="Regressão linear")
    plt.xlabel("Cota (m)")
    plt.ylabel("Volume (hm³)")
    plt.title("Regressão Linear: Cota x Volume")
    plt.legend()

    plt.savefig(caminho_saida, bbox_inches="tight", dpi=300)
    plt.close()

def gerar_modelo(df, caminho_grafico: Path = None):
    modelo, X_teste, y_teste = treinar_modelo_regressao(df)
    a, b = obter_parametros(modelo)
    #extraindo detalhes do modelo:
    previsoes = modelo.predict(X_teste)
    r2 = r2_score(y_teste, previsoes)
    mae = mean_absolute_error(y_teste, previsoes)
    rmse = mean_squared_error(y_teste, previsoes) ** 0.5
    #gera o gráfico de teste, com o resto dos dados e a reta gerada pelo modelo com eles 
    if caminho_grafico is not None:
        gerar_grafico_regressao(X_teste, y_teste, previsoes, caminho_grafico)

    return {"A": a, "B": b, "R2": r2, "MAE": mae, "RMSE": rmse}