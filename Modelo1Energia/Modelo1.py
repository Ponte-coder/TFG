import numpy as np
import math

class Modelo1:
    # Parámetros constantes
    # El primer valor es para estaciones tipo eNB y los demás para los otros 6 tipos, RRH.
    alfa = [21.45, 5.5]  # Coeficiente de eficiencia de potencia transmitida
    beta = [354.44, 38]  # Potencia de procesamiento y enfriamiento (W)
    delta = [2, 0.2]  # Constante de potencia dinámica (W/Mbps)
    ro = 1  # Potencia SFP (W)
    max_dl = 10  # Número máximo de downlinks
    Pmax_switch = 300  # Potencia máxima consumida por un switch (W)
    Pdl = 1  # Potencia enlace de bajada (W)
    Pul = 2  # Potencia enlace de subida (W)
    Umax = 10 * 1024  # Capacidad máxima del switch (Mbps)
    P_LT = 37  # Potencia de backhauling para tráfico bajo (W)
    P_HT = 92.5  # Potencia de backhauling para tráfico alto (W)
    C_LT = 500  # Capacidad (Mbps)
    Pswitch = 300  # Potencia máxima consumida por un switch (W)
    MAXsink = 36 * 1024  # Capacidad (Mbps)

    def __init__(self, BS, dimension, Eventos, dt, s_mob_jf, Eventos_User, Eventos_ordenados, Usuarios, modelo):
        """
        Modelo 1 Energía. Green HetNet CoMP: Energy Efficiency Analysis and Optimization

        Este modelo está dividido en tres partes A, B y C. Para este modelo
        suponemos un throughput variable, no marcado por el número de usuarios.

        Las variables utilizadas son:
        - BS: de donde se obtiene el número de estaciones tanto total como de cada
          tipo (RRH y eNB) y el número de routers de acceso.
        - dimension: de donde se obtienen las dimensiones del área de estudio.
        - Eventos: de donde obtenemos el eje de tiempo, los eventos marcan el
          consumo de energía.
        - dt: nos proporciona las divisiones del terreno.
        - modelo: cuyos valores posibles son 1 y 2. El modelo 1 supone una
          estructura en la cual las estaciones eNB no están asociadas a los routers,
          sino que funcionan por su cuenta. Sin embargo, en el modelo 2 se supone
          que todas las estaciones tienen un router asociado.
        """
        self.BS = BS
        self.dimension = dimension
        self.Eventos = Eventos
        self.dt = dt
        self.s_mob_jf = s_mob_jf
        self.Eventos_User = Eventos_User
        self.Eventos_ordenados = Eventos_ordenados
        self.Usuarios = Usuarios
        self.modelo = modelo

    def power1(self):
        """
        Calcula el consumo de energía según el Modelo 1.
        """
        # Parámetros
        Ptx = np.random.rand(self.BS.NBS.Combinada,
                             len(self.Eventos_User)) * 16 + 30  # potencia transmitida por cada transmisor. (dBm)

        # Cálculo de área
        area = self.dimension[0] * self.dimension[1] / 1000000  # área de estudio (km^2)

        # Cálculo de tráfico
        T = list(range(10, 101, 10))
        s = 3  # bit rate de un usuario (Mbps) (solo teniendo en cuenta telefonía 3G)

        S = []

        for j in range(len(self.Eventos_User)):
            usuarios_estacion = np.zeros(self.BS.NBS.Combinada)
            for i in range(self.Usuarios):
                distancias_j = self.s_mob_jf.PHY[i].Distancia[:, j]
                estacion = np.argmin(distancias_j)
                usuarios_estacion[estacion] += 1
            S_j = [s * usuarios for usuarios in usuarios_estacion]
            S.append(S_j)

        S_total = np.sum(S, axis=0)

        # Potencia cada BS
        Pbc = np.zeros((self.BS.NBS.Combinada, len(self.Eventos_User)))
        Pbc_micro = np.zeros((self.BS.NBS.Combinada, len(self.Eventos_User)))

        for i in range(1, self.BS.NBS.tipo[0] + 1):
            Pbc[i - 1, :] = self.alfa[0] * 10 ** ((Ptx[i - 1, :] - 30) / 10) + self.beta[0] + self.delta[0] * S[i - 1, :] + self.ro  # potencia consumida BS tipo eNB (W)
            Pbc_micro[i - 1, :] = self.alfa[0] * 10 ** ((Ptx[i - 1, :] - 30) / 10) + self.beta[0] + self.delta[0] * S[i - 1, :]  # potencia consumida BS tipo eNB, microwave (W)

        for i in range(self.BS.NBS.tipo[0] + 1, self.BS.NBS.Combinada + 1):
            Pbc[i - 1, :] = self.alfa[1] * 10 ** ((Ptx[i - 1, :] - 30) / 10) + self.beta[1] + self.delta[1] * S[i - 1, :] + self.ro  # potencia consumida BS tipo RRH (W)
            Pbc_micro[i - 1, :] = self.alfa[1] * 10 ** ((Ptx[i - 1, :] - 30) / 10) + self.beta[1] + self.delta[1] * S[i - 1, :]  # potencia consumida BS tipo RRH, microwave (W)

        # Potencia "Backhaul" (red de retorno)
        # Esta se divide en potencia de "Interbackhaul" y potencia de
        # "Intrabackhaul".
        # B. Potencia "Interbackhaul"

        NeNB = self.BS.NBS.tipo[0]  # número de celdas macro eNB
        Nul = (S_total / self.Umax).astype(int)

        # Ecuación
        Inter_PBH = ((NeNB / self.max_dl) * self.Pmax_switch + 2 * NeNB * self.Pdl + Nul * self.Pul).astype(int)

        # C. Potencia "Intrabackhaul"
        # Fiber
        if self.modelo == 2:
            Nul = self.BS.NBS.Combinada  # número de uplinks
        else:
            Nul = self.BS.NBS.Combinada - self.BS.NBS.tipo[0]

        NRRH = self.BS.NBS.Combinada - self.BS.NBS.tipo[0]  # número de celdas micro RRH

        # Ecuación
        Intra_PBH_FB = int((NRRH / self.max_dl) * self.Pmax_switch + Nul * self.Pul)

        # Microwave
        # Ecuación
        C_Sink = S_total
        Intra_PBH_MW = [
            (math.ceil(C / self.MAXsink) * self.Pswitch + self.P_LT) if C <= self.C_LT
            else (math.ceil(C / self.MAXsink) * self.Pswitch + self.P_HT)
            for C in C_Sink
        ]

        # Potencia total
        # Tenemos tres potencias totales, la primera sin backhaul, la segunda
        # utilizando backhaul mediante fibra y la última utilizando backhaul
        # mediante microwave.
        Ptotal = [
            np.sum(Pbc),
            np.sum(Pbc) + np.sum(Inter_PBH) + np.sum(Intra_PBH_FB),
            np.sum(Pbc_micro) + np.sum(Intra_PBH_MW)
        ]

        return Ptotal, Pbc




