import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from Modelo1Energia.Eventos import Eventos
from Modelo1Energia.EventosUser import EventosUser
from Modelo1Energia.BaseStation import BaseStation
from Modelo1Energia.Movilidad import Movilidad
from Modelo1Energia.Modelo1 import Modelo1




def main():
    # Ejemplo de creación de estaciones base eNB y RRH
    enb = BaseStation()
    enb.tipo = 0
    enb.numero_total = 8  # Número de estaciones eNB (pueden ser 0 o más)

    rrh = BaseStation()
    rrh.tipo = 1
    rrh.numero_total = 4  # Número de estaciones RRH (pueden ser 0 o más)

    num_estaciones = enb.numero_total + rrh.numero_total

    # Dimensiones del área de estudio
    dimension = (1000, 1000)

    # Ejemplo de creación de un objeto Eventos
    eventos_simulacion = Eventos()
    eventos_simulacion.eje_tiempo = [0, 10, 20, 30, 40, 60, 70, 80, 90, 100, 110, 120]

    dt = 4  # Cambia el valor de intervalo de tiempo en minutos

    # Ejemplo de creación de un objeto EventosUser
    eventos_usuario_simulacion = EventosUser()
    eventos_usuario_simulacion.eventos_usuario = [
        'Usuario 1 se conectó',
        'Usuario 2 se desconectó',
        'Usuario 3 se conectó',
        'Usuario 4 se desconectó',
        'Usuario 5 se conectó',
        'Usuario 6 se desconectó',
        'Usuario 7 se conectó',
        'Usuario 8 se desconectó',
        'Usuario 9 se conectó',
        'Usuario 10 se desconectó',
        'Usuario 11 se conectó',
        'Usuario 12 se desconectó'
    ]

    # Asegúrate de que el número de eventos de usuario sea igual al número de eventos ordenados
    eventos_ordenados = np.arange(1, len(eventos_usuario_simulacion.eventos_usuario) + 1)

    numero_usuarios = 12

    # Asegúrate de que el número de estaciones no sea mayor que el número de tiempos del eje de eventos
    assert num_estaciones <= len(
        eventos_simulacion.eje_tiempo), "El número de estaciones no puede ser mayor que el número de tiempos de eventos"

    # Asegúrate de que el número de usuarios no sea mayor que el número de estaciones base
    assert numero_usuarios <= num_estaciones, "El número de usuarios no puede ser mayor que el número de estaciones base"

    # Valor estático para la distancia en metros
    distancia_estatica = 500

    # Crea una instancia de la clase Movilidad
    s_mob_jf = Movilidad()

    # Inicializa la matriz de distancias estáticas para cada estación y evento
    for i in range(1, num_estaciones + 1):
        s_mob_jf.distancias[i] = {"distancia": []}

    for i in range(1, num_estaciones + 1):
        for j in range(len(eventos_simulacion.eje_tiempo)):
            distancia_estacion_evento = np.full((enb.numero_total + rrh.numero_total,), distancia_estatica)
            s_mob_jf.distancias[i]["distancia"].append(distancia_estacion_evento)

    # Valor de modelo utilizado en la simulación
    modelo = 1

    # Creación de la estructura BS
    bs = {"nbs": {"combinada": enb.numero_total + rrh.numero_total, "tipo": [enb.numero_total, rrh.numero_total]}}
    # Llama a la función Power1 y obtén los resultados
    modelo = Modelo1(bs, dimension, eventos_simulacion, dt, s_mob_jf, eventos_usuario_simulacion, eventos_ordenados,
                     numero_usuarios, modelo)

    # Llama al método power1 en el objeto modelo
    ptotal, pbc = modelo.power1()

    # Trazado de los datos de pbc
    fig, ax = plt.subplots()

    # Genera una paleta de colores personalizada basada en "Viridis" usando Seaborn
    custom_palette = sns.color_palette("viridis", as_cmap=True)

    for i in range(pbc.shape[0]):
        color = custom_palette(i / (bs["nbs"]["combinada"] - 1))  # Usa la paleta personalizada
        ax.plot(eventos_ordenados, pbc[i] / 1000, '-o', color=color,
                label=f'{enb.tipo if i < enb.numero_total else rrh.tipo} {i + 1}')

    ax.set_xlabel('Eventos')
    ax.set_ylabel('Potencia consumida (kW)')
    ax.set_title('Potencia consumida por estación')

    # Creación de la leyenda para BS
    legend_labels = [f'{enb.tipo} {i + 1}' if i < enb.numero_total else f'{rrh.tipo} {i + 1}' for i in
                     range(bs["nbs"]["combinada"])]
    ax.legend(legend_labels, loc='best')

    plt.show()


if __name__ == "__main__":
    main()
