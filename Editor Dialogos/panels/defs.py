# Variable global que 
characters = {}

class character:
    def __init__(self, name="Character", color="#ffffff", font="", 
    sounds=[]):
        self.name = name
        self.color = color
        self.font = font
        self.sounds = sounds


class Digraph:
    def __init__(self):
        self.addys = {}

    def add_node(self, node_id):
        '''
        Añade un nodo si no eciste
        '''
        if node_id not in self.addys:
            self.addys[node_id] = []

    def add_edge(self, desde_id, hasta_id):
        '''
        Crea una arista desde -> hasta
        '''
        if desde_id in self.addys:
            if hasta_id not in self.addys[desde_id]:
                self.addys[desde_id].append(hasta_id)
        else:
            # Si el nodo de origen no existe, lo creamos
            self.addys[desde_id] = [hasta_id]
            
        # Aseguramos que el nodo destino también exista en el diccionario
        if hasta_id not in self.addys:
            self.addys[hasta_id] = []

    def obtener_vecinos(self, node_id):
        '''
        Obtenemos los vecinos
        '''
        return self.addys.get(node_id, [])

    def check_cycles(self):
        '''
        Comprueba si hay un camino desde inicio a fin
        '''
        visitados = set()    # Nodos totalmente procesados
        en_camino = set()    # Nodos en la pila de la ruta actual (recursión)

        def tiene_ciclo_dfs(u):
            visitados.add(u)
            en_camino.add(u)

            for v in self.addys.get(u, []):
                if v not in visitados:
                    if tiene_ciclo_dfs(v):
                        return True
                elif v in en_camino:
                    # Si el vecino ya está en la ruta actual, ¡es un ciclo!
                    return True

            en_camino.remove(u)
            return False

        # Revisamos cada nodo porque el grafo puede estar desconectado
        for nodo in self.addys:
            if nodo not in visitados:
                if tiene_ciclo_dfs(nodo):
                    return True
        return False

    def __str__(self):
        '''
        Representacion del grafo
        '''
        res = "Estructura del Grafo:\n"
        for nodo, vecinos in self.addys.items():
            res += f"{nodo} -> {vecinos}\n"
        return res