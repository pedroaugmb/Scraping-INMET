import pandas as pd
from sklearn.linear_model import LinearRegression

def treinar_modelo(df):

    X = df[["Cota (m)"]]
    y = df["Volume (hm³)"]
    modelo = LinearRegression()
    modelo.fit(X, y)

    return modelo

def obter_parametros(modelo):

    a = modelo.coef_[0]
    b = modelo.intercept_
    return a, b

def gerar_modelo(df):

    modelo = treinar_modelo(df)
    a, b = obter_parametros(modelo)

    return {"A": a,"B": b}