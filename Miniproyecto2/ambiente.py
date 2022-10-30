import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

class lugarTablero(object):
    valor = 0
    seleccionado = False
    mina = False

    def __init__(self):
        self.seleccionado = False

    def __str__(self):
        return str(lugarTablero.valor)

    def isMine(self):
        if lugarTablero.valor == -1:
            return True
        return False

def truncar(x, n=8):
    if x < 0:
        return 0
    elif x > n-1:
        return n-1
    else:
        return x

def adyacentes(casilla,width,height):
    x, y = casilla
    if y%2 == 1:
        adyacentes = [
            (truncar(x - 1, width), y), (truncar(x + 1, width), y), 
            (x, truncar(y + 1, height)), (truncar(x + 1, width), truncar(y + 1, height)),
            (x, truncar(y - 1, height)),(truncar(x + 1, width), truncar(y - 1, height))]
    else: 
        adyacentes = [
            (truncar(x - 1), y), (truncar(x + 1), y), 
            (truncar(x - 1), truncar(y + 1)), (x, truncar(y + 1)),
            (truncar(x - 1), truncar(y - 1)),(x, truncar(y - 1))]
    adyacentes = list(set(adyacentes))
    adyacentes = [c for c in adyacentes if c != casilla]
    adyacentes_rem = []
    for x1, y1 in adyacentes:
        if x1 >= width or y1 >= height:
            adyacentes_rem.append((x1,y1))
    adyacentes = [adyac for adyac in adyacentes if adyac not in adyacentes_rem]
    return adyacentes

class Buscaminas():
    
    def __init__(self, width=8, height=8, num_minas=10):
        self.casillas = [(x, y) for x in range(width) for y in range(height)]
        self.tablero = [[lugarTablero() for x in range(width)] for y in range(height)]
        self.width = width
        self.height = height
        self.num_minas = num_minas
        self.lugar_seleccionable = width * height
        self.juego_activo = True
        self.flags = np.zeros((self.width, self.height), dtype=bool)
        self.transicion_bool = True
        self.game_won = False
        
        i = 0
        while i < num_minas:
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            if not self.tablero[x][y].mina:
                self.agregar_mina((x, y))
                i += 1
            else:
                i -= 1

    def casillas_adyacentes_sin_destapar(self):
        casillas_adyacentes_sin_destapar = []
        for x, y in self.casillas:
            if self.tablero[x][y].seleccionado == True:
                for x1, y1 in adyacentes((x,y), self.width, self.height):
                    if self.tablero[x1][y1].seleccionado == False:
                        casillas_adyacentes_sin_destapar.append((x1,y1))
        return list(set(casillas_adyacentes_sin_destapar))
                
    def agregar_mina(self, casilla):
        x, y = casilla
        self.tablero[x][y].valor = -1
        self.tablero[x][y].mina = True
        for x1,y1 in adyacentes((x,y), self.width, self.height):
            if self.tablero[x1][y1].valor != -1:
                self.tablero[x1][y1].valor += 1
    
    def pintar_todo(self):
        covered_color = '#DDDDDD'
        uncovered_color = '#AAAAAA'
        edge_color = '#888888'
        count_colors = ['none', 'blue', 'green', 'red', 'darkblue',
                        'darkred', 'darkgreen', 'black', 'black']
        flag_vertices = np.array([[0.25, 0.2], [0.25, 0.8],
                                  [0.75, 0.65], [0.25, 0.5]])
        
        fig = plt.figure(figsize=((self.width + 2) / 3., (self.height + 2) / 3.))
        ax = fig.add_axes((0.05, 0.05, 0.9, 0.9),
                                    aspect='equal', frameon=False,
                                    xlim=(-0.4, self.width + 1.4),
                                    ylim=(-0.4, self.height + 0.4))
        
        for axis in (ax.xaxis, ax.yaxis):
            axis.set_major_formatter(plt.NullFormatter())
            axis.set_major_locator(plt.NullLocator())
            
         
        # Create the grid of squares
        r = 0.64
        squares = []
        for i in range(self.height):
          col = []
          for j in range(self.width):
            if j%2==0:
              col.append(RegularPolygon(
                  (i+r, j+r*0.8),
                  numVertices=6,
                  radius=r,
                  orientation=np.pi,
                  ec=edge_color,
                  fc=covered_color))
            else:
              col.append(RegularPolygon(
                  (i+1.8*r, j+r*0.8),
                  numVertices=6,
                  radius=r ,
                  orientation=np.pi,
                  ec=edge_color,
                  fc=covered_color))
          squares.append(col)

        squares = np.array(squares)

        [ax.add_patch(sq) for sq in squares.flat]
        
        # Cargando imagen bomba
        arr_img_bomb = plt.imread("./imagenes/bomb.png", format='png')
        image_bomb = OffsetImage(arr_img_bomb, zoom=0.03)
        image_bomb.image.ax = ax
        
        # Cargando imagen bandera
        arr_img_flag = plt.imread("./imagenes/flag.png", format='png')
        image_flag = OffsetImage(arr_img_flag, zoom=0.03)
        image_flag.image.ax = ax
        
        # Pintando las casillas
        for casilla in self.casillas:
            x, y = casilla
            if self.tablero[x][y].valor == -1:
                if not self.juego_activo:
                    if self.flags[x][y] == True:
                        if y%2 == 0:
                            ab = AnnotationBbox(image_flag, [x + r, y + r*0.8], frameon=False)
                            ax.add_artist(ab)
                        else:
                            ab = AnnotationBbox(image_flag, [x + 1.76*r, y + r*0.8], frameon=False)
                            ax.add_artist(ab)         
                    else:
                        if y%2 == 0:
                            ab = AnnotationBbox(image_bomb, [x + r, y + r*0.8], frameon=False)
                            ax.add_artist(ab)
                        else:
                            ab = AnnotationBbox(image_bomb, [x + 1.76*r, y + r*0.8], frameon=False)
                            ax.add_artist(ab)

                else:
                    if y%2 == 0:
                        ab = AnnotationBbox(image_bomb, [x + r, y + r*0.8], frameon=False)
                        ax.add_artist(ab)
                    else:
                        ab = AnnotationBbox(image_bomb, [x + 1.76*r, y + r*0.8], frameon=False)
                        ax.add_artist(ab)
            else:
                if not self.juego_activo:
                    if self.flags[x][y] == True:
                        if y%2 == 0:
                            ab = AnnotationBbox(image_flag, [x + r, y + r*0.8], frameon=False)
                            ax.add_artist(ab)
                        else:
                            ab = AnnotationBbox(image_flag, [x + 1.76*r, y + r*0.8], frameon=False)
                            ax.add_artist(ab) 
                    else:
                        if y%2 == 0:
                            ax.text(x + r, y + r*0.8, str(self.tablero[x][y].valor),
                                    color=count_colors[self.tablero[x][y].valor],
                                    ha='center', va='center', fontsize=18,
                                    fontweight='bold')
                        else:
                            ax.text(x + 1.76*r, y + r*0.8, str(self.tablero[x][y].valor),
                                    color=count_colors[self.tablero[x][y].valor],
                                    ha='center', va='center', fontsize=18,
                                    fontweight='bold')
                else:
                    if y%2 == 0:
                        ax.text(x + r, y + r*0.8, str(self.tablero[x][y].valor),
                                color=count_colors[self.tablero[x][y].valor],
                                ha='center', va='center', fontsize=18,
                                fontweight='bold')
                    else:
                        ax.text(x + 1.76*r, y + r*0.8, str(self.tablero[x][y].valor),
                                color=count_colors[self.tablero[x][y].valor],
                                ha='center', va='center', fontsize=18,
                                fontweight='bold')
                
        if not self.juego_activo:
            for casilla in self.casillas:
                x, y = casilla
                if self.tablero[x][y].valor == -1 and ~self.flags[x][y]:
                    squares[x, y].set_facecolor('red')
                elif self.tablero[x][y].valor != -1 and self.flags[x][y]:  
                    squares[x, y].set_facecolor('red')
        return ax
    
    
    def pintar_casilla(self):
        covered_color = '#DDDDDD'
        uncovered_color = '#AAAAAA'
        edge_color = '#888888'
        count_colors = ['none', 'blue', 'green', 'red', 'darkblue',
                        'darkred', 'darkgreen', 'black', 'black']
        if self.juego_activo:
            flag_vertices = np.array([[0.25, 0.2], [0.25, 0.8],
                                      [0.75, 0.65], [0.25, 0.5]])

            fig = plt.figure(figsize=((self.width + 2) / 3., (self.height + 2) / 3.))
            ax = fig.add_axes((0.05, 0.05, 0.9, 0.9),
                                        aspect='equal', frameon=False,
                                        xlim=(-0.4, self.width + 1.4),
                                        ylim=(-0.4, self.height + 0.4))

            for axis in (ax.xaxis, ax.yaxis):
                axis.set_major_formatter(plt.NullFormatter())
                axis.set_major_locator(plt.NullLocator())


            # Create the grid of squares
            r = 0.64
            squares = []
            for i in range(self.height):
              col = []
              for j in range(self.width):
                if j%2==0:
                  col.append(RegularPolygon(
                      (i+r, j+r*0.8),
                      numVertices=6,
                      radius=r,
                      orientation=np.pi,
                      ec=edge_color,
                      fc=covered_color))
                else:
                  col.append(RegularPolygon(
                      (i+1.8*r, j+r*0.8),
                      numVertices=6,
                      radius=r ,
                      orientation=np.pi,
                      ec=edge_color,
                      fc=covered_color))
              squares.append(col)

            squares = np.array(squares)
            [ax.add_patch(sq) for sq in squares.flat]

            # Cargando imagen bomba
            arr_img_bomb = plt.imread("./imagenes/bomb.png", format='png')
            image_bomb = OffsetImage(arr_img_bomb, zoom=0.03)
            image_bomb.image.ax = ax
            
            # Cargando imagen bandera
            arr_img_flag = plt.imread("./imagenes/flag.png", format='png')
            image_flag = OffsetImage(arr_img_flag, zoom=0.03)
            image_flag.image.ax = ax

            # Pintando las casillas
            for casilla in self.casillas:
                x, y = casilla
                if self.tablero[x][y].seleccionado:
                    squares[x, y].set_facecolor(uncovered_color)

                    if y%2 == 0:
                        ab = AnnotationBbox(image_flag, [x + r, y + r*0.8], frameon=False)
                    else:
                        ab = AnnotationBbox(image_flag, [x + 1.76*r, y + r*0.8], frameon=False)
                    if self.flags[x][y] == True:
                        ax.add_artist(ab)
                    else:
                      
                        try:
                            ax.patches.remove(ab)
                        except: pass
                    if self.tablero[x][y].valor != -1 and self.flags[x][y] == False:
                        if y%2 == 0:
                            ax.text(x + r, y + r*0.8, str(self.tablero[x][y].valor),
                                    color=count_colors[self.tablero[x][y].valor],
                                    ha='center', va='center', fontsize=18,
                                    fontweight='bold')
                        else:
                            ax.text(x + 1.76*r, y + r*0.8, str(self.tablero[x][y].valor),
                                    color=count_colors[self.tablero[x][y].valor],
                                    ha='center', va='center', fontsize=18,
                                    fontweight='bold')
            return ax
        else: 
            None
    
    def agregar_quitar_bandera(self, casilla):
        bombas = np.zeros((self.width,self.height), dtype = bool)
        for x1,y1 in self.casillas:
            if self.tablero[x1][y1].valor == -1:
                bombas[x1][y1] = True        
        
        
        self.transicion_bool = False
        if self.juego_activo:
            x, y = casilla
            self.tablero[x][y].seleccionado = ~self.tablero[x][y].seleccionado
            self.flags[x][y] = ~self.flags[x][y]
            self.lugar_seleccionable -= 1
            
        if self.lugar_seleccionable == 0:
            self.juego_activo = False
            if np.all(self.flags == bombas):
                self.game_won = True
                print("¡Felicidades! Juego terminado")
            else:
                print("Perdiste, ¡Juego terminado!")
            # self.pintar_todo()
        
    def transicion(self, casilla):
        self.transicion_bool = True
        x, y = casilla
        bombas = np.zeros((self.width,self.height), dtype = bool)
        for x1,y1 in self.casillas:
            if self.tablero[x1][y1].valor == -1:
                bombas[x1][y1] = True        
        
        if self.juego_activo == True and self.flags[x][y] == False:
            self.tablero[x][y].seleccionado = True
            self.lugar_seleccionable -= 1

            if self.tablero[x][y].valor == -1:
                self.juego_activo = False
                print("Perdiste, ¡Juego terminado!")
                # ax = self.pintar_todo()

            if self.lugar_seleccionable == 0:
                self.juego_activo = False
                if np.all(self.flags == bombas):
                    self.game_won = True
                    print("¡Felicidades! Juego terminado")
                else:
                    print("Perdiste, ¡Juego terminado!")
                # self.pintar_todo()

            if self.tablero[x][y].valor == 0:
                for x1, y1 in adyacentes(casilla, self.width, self.height):
                    if not self.tablero[x1][y1].seleccionado:
                        self.transicion((x1,y1))

        elif self.juego_activo == True and self.flags[x][y] == True:
            print("La casilla tiene una bandera, pruebe otra movida.")
        else:
            print("El juego ha terminado.")

class Agente:

    def __init__(self, mundo, base_conocimiento = None, descriptor = None):
        self.mundo = mundo
        self.base_conocimiento = base_conocimiento
        self.cods = descriptor
        
    def make_percept_sentence(self):
        # Crea una conjuncion de literales para añadir a la base de datos
        literales = []
        for x, y in  self.mundo.casillas:
            if self.mundo.tablero[x][y].seleccionado == True and self.mundo.flags[x][y] == False:
                if self.mundo.tablero[x][y].valor == -1:
                    literales += [self.cods.P([x, y, 0])]
                elif self.mundo.tablero[x][y].valor == 0:
                    literales += ['-' + self.cods.P([x, y, 0])]
                else:
                    literales += [self.cods.P([x, y, self.mundo.tablero[x][y].valor])]
            if self.mundo.tablero[x][y].seleccionado == True and self.mundo.flags[x][y] == True:
                literales += [self.cods.P([x, y, 0])]
        literales = 'Y'.join(literales)
        return literales