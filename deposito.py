class Deposito :
    def __init__(self, nombre:str, capacidad_contenedores:int):
        self._items = []
        self.nombre = nombre
        self.capacidad_contenedores = capacidad_contenedores
        self.contenedores = []
        self.pedidos = []

    def adicionar_item(self, item):
        self._items.append(item)

    def remover_item(self, item):
        if item in self._items:
            self._items.remove(item)

    def listar_items(self):
        return self._items