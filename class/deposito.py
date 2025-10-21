class Deposito :
    def __init__(self, nombre:str, capacidad_contenedores:int):
        self._items = []
        self.nombre = nombre
        self.capacidad_contenedores = capacidad_contenedores
        self.contenedores = []
        self.pedidos = []

    def agregar_contenedor(self, contenedor):
        if len(self.contenedores) < self.capacidad_contenedores:
            self.contenedores.append(contenedor)
        else:
            raise ValueError("Capacidad máxima de contenedores alcanzada")

    def listar_contenedores(self):
        return self.contenedores

    def agregar_pedido(self, pedido):
        self.pedidos.append(pedido)

    def listar_pedidos(self):
        return self.pedidos

    def __str__(self):
        return f"Depósito {self.nombre} (ID {self.id_deposito}) con {len(self.contenedores)} contenedores y {len(self.pedidos)} pedidos"