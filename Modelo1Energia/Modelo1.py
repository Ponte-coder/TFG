import numpy as np
import math


class Modelo1:
    def __init__(self, bs, dimension, eventos, dt, s_mob_jf, eventos_user, eventos_ordenados, usuarios, modelo):
        """
        Constructor de la clase Modelo1.

        Parámetros:
            bs (dict): Información sobre las estaciones base (BS), número de estaciones totales y de cada tipo (RRH y eNB), y el número de routers de acceso.
            dimension (tuple): Dimensiones del área de estudio.
            eventos (array): Eje del tiempo y eventos que marcan el consumo de energía.
            dt (float): Divisiones del terreno.
            s_mob_jf (object): Información sobre la movilidad de los usuarios.
            eventos_user (object): Eventos relacionados con los usuarios.
            eventos_ordenados (array): Eventos ordenados en el tiempo.
            usuarios (int): Número de usuarios.
            modelo (int): Modelo de la red (1 o 2).
        """
        self.bs = bs
        self.dimension = dimension
        self.eventos = eventos
        self.dt = dt
        self.s_mob_jf = s_mob_jf
        self.eventos_user = eventos_user
        self.eventos_ordenados = eventos_ordenados
        self.usuarios = usuarios
        self.modelo = modelo

    def power1(self):
        """
        Método principal que realiza cálculos de potencia y consumo de energía.

        Retorna:
            ptotal (list): Lista de potencias totales en diferentes escenarios.
            pbc (array): Potencia consumida por las estaciones base.
        """
        # Cálculos de potencia y consumo de energía
        ptx, alfa, beta, delta, ro, max_dl, pmax_switch, pdl, pul, umax, p_lt, p_ht, c_lt, pswitch, maxsink = self.calcular_parametros()
        s_total, S, pbc, pbc_micro = self.calcular_potencia(ptx, alfa, beta, delta, ro)

        # Potencia "Interbackhaul" y "Intrabackhaul"
        inter_pbh = self.calcular_interbackhaul(s_total, umax, max_dl, pmax_switch, pdl, pul)
        intra_pbh_fb = self.calcular_intrabackhaul_fb(s_total, max_dl, pmax_switch, pdl, pul)
        intra_pbh_mw = self.calcular_intrabackhaul_mw(s_total, pswitch, p_lt, p_ht, c_lt)

        # Potencia total
        ptotal = self.calcular_potencia_total(pbc, inter_pbh, intra_pbh_fb, pbc_micro, intra_pbh_mw)

        return ptotal, pbc

    def calcular_parametros(self):
        """
        Función para calcular y retornar parámetros específicos.

        Retorna:
            ptx (array): Potencia transmitida por cada transmisor.
            alfa (list): Coeficientes de eficiencia de potencia transmitida.
            beta (list): Potencia de procesamiento y enfriamiento.
            delta (list): Constante de potencia dinámica.
            ro (float): Potencia SFP.
            max_dl (int): Número máximo de enlaces descendentes.
            pmax_switch (int): Potencia máxima consumida por un switch.
            pdl (int): Potencia de enlace de bajada.
            pul (int): Potencia de enlace de subida.
            umax (int): Capacidad máxima del switch.
            p_lt (int): Potencia para tráfico bajo (Fibra).
            p_ht (float): Potencia para tráfico alto (Fibra).
            c_lt (int): Capacidad (Fibra).
            pswitch (int): Potencia máxima consumida por un switch (Microwave).
            maxsink (int): Capacidad máxima (Microwave).
        """
        eventos_user_len = len(self.eventos_user.eventos_usuario)
        ptx = np.random.uniform(30, 45, size=(self.bs["nbs"]["combinada"], eventos_user_len)).round(1)
        alfa = [21.45, 5.5]
        beta = [354.44, 38]
        delta = [2, 0.2]
        ro = 1
        max_dl = 10
        pmax_switch = 300
        pdl = 1
        pul = 2
        umax = 10 * 1024
        p_lt = 37
        p_ht = 92.5
        c_lt = 500
        pswitch = 300
        maxsink = 36 * 1024
        maxsink = maxsink * 1024

        return ptx, alfa, beta, delta, ro, max_dl, pmax_switch, pdl, pul, umax, p_lt, p_ht, c_lt, pswitch, maxsink

    def calcular_potencia(self, ptx, alfa, beta, delta, ro):
        """
        Función para calcular potencia consumida por las estaciones base y más.

        Parámetros:
            ptx (array): Potencia transmitida por cada transmisor.
            alfa (list): Coeficientes de eficiencia de potencia transmitida.
            beta (list): Potencia de procesamiento y enfriamiento.
            delta (list): Constante de potencia dinámica.
            ro (float): Potencia SFP.

        Retorna:
            s_total (array): Suma total de bit rates en cada estación.
            S (array): Bit rate en cada estación en diferentes momentos en el tiempo.
            pbc (array): Potencia consumida por las estaciones base.
            pbc_micro (array): Potencia consumida por las estaciones base (Microwave).
        """
        area = self.dimension[0] * self.dimension[1] / 1000000
        t = list(range(10, 101, 10))
        s = 3  # bit rate de un usuario (Mbps)solo teniendo en cuenta telefonia 3G
        eventos_user_len = len(self.eventos_user.eventos_usuario)

        # Crear una matriz para S
        S = np.zeros((self.bs["nbs"]["combinada"], eventos_user_len))

        # Calcular el bit rate s para cada estación en diferentes momentos en el tiempo
        for j in range(0, eventos_user_len):
            usuarios_estacion = np.zeros(self.bs["nbs"]["combinada"])
            for i in range(1, self.usuarios):
                distancias_j = self.s_mob_jf.distancias[i]["distancia"][j]
                estacion = distancias_j[i - 1]
                usuarios_estacion[i - 1] = estacion
            S[:, j] = s * np.array(usuarios_estacion)

        # Calcular la suma total de bit rates en cada estación
        s_total = np.sum(S, axis=1)

        # Inicializar matrices para pbc y pbc_micro
        pbc = np.zeros((self.bs["nbs"]["combinada"], len(self.eventos_ordenados)))
        pbc_micro = np.zeros((self.bs["nbs"]["combinada"], len(self.eventos_ordenados)))

        # Calcular potencia consumida por las estaciones base y estaciones base de Microwave
        for i in range(0, self.bs["nbs"]["tipo"][0]):
            pbc[i, :] = alfa[0] * 10 ** ((ptx[i, :] - 30) / 10) + beta[0] + delta[0] * S[i, :] + ro
            pbc_micro[i, :] = alfa[0] * 10 ** ((ptx[i, :] - 30) / 10) + beta[0] + delta[0] * S[i, :]

        for i in range(self.bs["nbs"]["tipo"][0] + 1, self.bs["nbs"]["combinada"] + 1):
            pbc[i - 1, :] = alfa[1] * 10 ** ((ptx[i - 1, :] - 30) / 10) + beta[1] + delta[1] * S[i - 1, :] + ro
            pbc_micro[i - 1, :] = alfa[1] * 10 ** ((ptx[i - 1, :] - 30) / 10) + beta[1] + delta[1] * S[i - 1, :]

        return s_total, S, pbc, pbc_micro

    def calcular_interbackhaul(self, s_total, umax, max_dl, pmax_switch, pdl, pul):
        """
        Función para calcular la potencia "Interbackhaul".

        Parámetros:
            s_total (array): Suma total de bit rates en cada estación.
            umax (int): Capacidad máxima del switch.
            max_dl (int): Número máximo de enlaces descendentes.
            pmax_switch (int): Potencia máxima consumida por un switch.
            pdl (int): Potencia de enlace de bajada.
            pul (int): Potencia de enlace de subida.

        Retorna:
            inter_pbh (array): Potencia "Interbackhaul".
        """
        # Cálculo de potencia "Interbackhaul"
        ne_nb = self.bs["nbs"]["tipo"][0]
        n_ul = (s_total / umax).astype(int)

        inter_pbh = ((ne_nb / max_dl) * pmax_switch + 2 * ne_nb * pdl + n_ul * pul).astype(int)

        return inter_pbh

    def calcular_intrabackhaul_fb(self, s_total, max_dl, pmax_switch, pdl, pul):
        """
        Función para calcular la potencia "Intrabackhaul" para fibra.

        Parámetros:
            s_total (array): Suma total de bit rates en cada estación.
            max_dl (int): Número máximo de enlaces descendentes.
            pmax_switch (int): Potencia máxima consumida por un switch.
            pdl (int): Potencia de enlace de bajada.
            pul (int): Potencia de enlace de subida.

        Retorna:
            intra_pbh_fb (array): Potencia "Intrabackhaul" para fibra.
        """
        # Cálculo de potencia "Intrabackhaul" (Fibra)
        n_rrh = self.bs["nbs"]["combinada"] - self.bs["nbs"]["tipo"][0]
        n_ul = (s_total / 10).astype(int)

        intra_pbh_fb = (n_rrh / max_dl) * pmax_switch + n_ul * pul

        return intra_pbh_fb

    def calcular_intrabackhaul_mw(self, s_total, pswitch, p_lt, p_ht, c_lt):
        """
        Función para calcular la potencia "Intrabackhaul" para microwave.

        Parámetros:
            s_total (array): Suma total de bit rates en cada estación.
            pswitch (int): Potencia máxima consumida por un switch (Microwave).
            p_lt (int): Potencia para tráfico bajo (Fibra).
            p_ht (float): Potencia para tráfico alto (Fibra).
            c_lt (int): Capacidad (Fibra).

        Retorna:
            intra_pbh_mw (list): Potencia "Intrabackhaul" para microwave.
        """
        intra_pbh_mw = []
        for c in s_total:
            if c <= c_lt:
                intra_pbh_mw.append(math.ceil(c / 36) * pswitch + p_lt)
            else:
                intra_pbh_mw.append(math.ceil(c / 36) * pswitch + p_ht)

        return intra_pbh_mw

    def calcular_potencia_total(self, pbc, inter_pbh, intra_pbh_fb, pbc_micro, intra_pbh_mw):
        """
        Función para calcular la potencia total en diferentes escenarios.

        Parámetros:
            pbc (array): Potencia consumida por las estaciones base.
            inter_pbh (array): Potencia "Interbackhaul".
            intra_pbh_fb (array): Potencia "Intrabackhaul" para fibra.
            pbc_micro (array): Potencia consumida por las estaciones base (Microwave).
            intra_pbh_mw (list): Potencia "Intrabackhaul" para microwave.

        Retorna:
            ptotal (list): Lista de potencias totales en diferentes escenarios.
        """
        # Cálculo de potencia total
        ptotal = [
            np.sum(pbc),
            np.sum(pbc) + np.sum(inter_pbh) + intra_pbh_fb,
            np.sum(pbc_micro) + np.sum(intra_pbh_mw)
        ]

        return ptotal

