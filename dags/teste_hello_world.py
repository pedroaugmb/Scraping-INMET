from __future__ import annotations

import pendulum
from airflow.sdk import dag, task


@dag(
    dag_id="teste_hello_world",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["teste"],
)
def teste_hello_world():
    @task
    def hello():
        print("Hello, Airflow!")
        return "ok"

    @task
    def world(mensagem: str):
        print(f"World! (recebido do task anterior: {mensagem})")

    world(hello())


teste_hello_world()
