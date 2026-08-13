import pygame as pg 
from pygame.math import Vector2 as V2 
from random import randint as rnd 

screen = pg.display.set_mode((1200, 600)) 
pg.display.set_caption("Snake") 

tamaño_celda = 60
ancho_pantalla = 15 * tamaño_celda
alto_pantalla = 10 * tamaño_celda

hud_x = ancho_pantalla * tamaño_celda // 15

sheet1 = pg.image.load("snake_sprites6.png").convert_alpha()
sheet2 = pg.image.load("snake_sprites7.png").convert_alpha()
game_start = pg.transform.scale(pg.image.load("pantalla_carga.png"), (1200, 600))
lose       = pg.transform.scale(pg.image.load("game_over.png"), (900, 600))
win        = pg.transform.scale(pg.image.load("win.png"), (900, 600))



SPRITE_COORDS = {
    "head_right": (16, 27, 58, 39, sheet1),
    "head_left":  (95, 27, 59, 39, sheet1),
    "head_up":    (188, 16, 47, 61, sheet1),
    "head_down":  (273, 16, 47, 64, sheet1),
    "head_right_open": (354, 27, 59, 44, sheet1),
    "head_left_open":  (433, 27, 59, 44, sheet1),
    "body":       (10, 120, 64, 39, sheet1),
    "tail":       (95, 303, 64, 39, sheet1),
    "apple_1":    (352, 287, 58, 68, sheet1),
    "apple_2":    (436, 287, 59, 68, sheet1),
    "grass":      (594, 280, 81, 84, sheet1),
    "dirt":       (512, 284, 76, 80, sheet1),

    # nuevos, de la segunda hoja
    "head_open_front_1": (524, 284, 63, 81, sheet2),
    "head_open_front_2": (610, 284, 59, 79, sheet2),
    "curve": (352, 120, 64, 64, sheet2)
}

def cut_sprite(name):
    x, y, w, h, sheet = SPRITE_COORDS[name]
    result = pg.Surface((w, h), pg.SRCALPHA)
    result.blit(sheet, (0, 0), pg.Rect(x, y, w, h))
    return pg.transform.scale(result, (tamaño_celda, tamaño_celda))

def dir_angle(d):
    # "body"/"tail" apuntan hacia la DERECHA (1,0) por defecto
    angles = {(1,0): 0, (-1,0): 180, (0,-1): 90, (0,1): -90}
    try:
        key = (d.x, d.y)
    except AttributeError:
        key = tuple(d)
    return angles.get(key, 0)


sprite_fd = cut_sprite("apple_1")
dr = V2(1, 0)
dr_pendiente = V2(1, 0)
drs = {pg.K_UP: V2(0, -1), pg.K_DOWN: V2(0, 1), pg.K_LEFT: V2(-1, 0), pg.K_RIGHT: V2(1, 0)}
pcs = [V2(10, 5)]

def food():
    while True:
        valido = V2(rnd(0, 14), rnd(0, 9))
        if valido not in pcs:
            return valido

def reset_juego():
    global pcs, dr, dr_pendiente, fd, sprite_fd, puntos, manzanas_doradas, tipo_mazana_actual, ultimo_segundo_contado
    pcs = [V2(10, 5)]
    dr = V2(1, 0)
    dr_pendiente = V2(1, 0)
    fd = food()
    sprite_fd = cut_sprite("apple_1")
    puntos = 0
    manzanas_doradas = 0
    tipo_mazana_actual = "apple_1"
    ultimo_segundo_contado = 0

fd = food()  
puntos = 0
manzanas_doradas = 0
tipo_mazana_actual = "apple_1" 
ultimo_segundo_contado = 0 

apple_1 = cut_sprite("apple_1")
apple_2 = cut_sprite("apple_2")

HEAD_BY_DIR = {
    (1, 0):  "head_right",
    (-1, 0): "head_left",
    (0, -1): "head_up",
    (0, 1):  "head_down",
}

def head_sprite(cabeza, comida, direccion):
    diff = comida - cabeza
    misma_fila = diff.y == 0
    misma_columna = diff.x == 0
    distancia = abs(diff.x) + abs(diff.y)
    apuntando = V2(0,0)
    if misma_fila and diff.x != 0:
        apuntando = V2(1,0) if diff.x > 0 else V2(-1,0)
    elif misma_columna and diff.y != 0:
        apuntando = V2(0,1) if diff.y > 0 else V2(0,-1)
    boca_abierta = (misma_fila or misma_columna) and distancia <= 3 and direccion == apuntando
    if not boca_abierta:
        return cut_sprite(HEAD_BY_DIR[tuple(direccion)])
    if direccion == V2(1,0):
        return cut_sprite("head_right_open")
    elif direccion == V2(-1,0):
        return cut_sprite("head_left_open")
    elif direccion == V2(0,-1):
        return pg.transform.rotate(cut_sprite("head_open_front_1"),180)
    elif direccion == V2(0,1):
        return pg.transform.rotate(cut_sprite("head_open_front_2"),180)

def curva_angle(entra, sale):
    giro_horario = {
        ((0,-1), (1,0)):  0,    # viene de abajo, dobla a la derecha
        ((-1,0), (0,-1)): 90,   # viene de la derecha, dobla hacia arriba
        ((0,1),  (-1,0)): 180,  # viene de arriba, dobla hacia la izquierda
        ((1,0),  (0,1)):  270,  # viene de la izquierda, dobla hacia abajo
    }
    giro_antihorario = {
        ((0,1), (1,0)):  180,    # viene de abajo, dobla a la derecha
        ((1,0), (0,-1)): 270,   # viene de la derecha, dobla hacia arriba
        ((0,-1),  (-1,0)): 0,  # viene de arriba, dobla hacia la izquierda
        ((-1,0),  (0,1)):  90,  # viene de la izquierda, dobla hacia abajo
    }
    par = (tuple(entra), tuple(sale))
    base = cut_sprite("curve")
    if par in giro_horario:
        return pg.transform.rotate(base, giro_horario[par])
    elif par in giro_antihorario:
        base_flip = pg.transform.flip(base, True, False)
        return pg.transform.rotate(base_flip, giro_antihorario[par])
    return base 

def dir_wrap(desde, hacia, ancho=ancho_pantalla, alto=alto_pantalla):
    dx = (hacia.x - desde.x + ancho//2) % ancho - ancho//2
    dy = (hacia.y - desde.y + alto//2) % alto - alto//2
    return V2(dx, dy)

pg.init()
font1 = pg.font.SysFont("voluptuous bubble", 150)
font2 = pg.font.SysFont("voluptuous bubble", 80)
font3 = pg.font.SysFont("voluptuous bubble", 55)
estado = "inicio"
# Rects para game_start (1200x600)
boton_play_inicio = pg.Rect(406, 257, 406, 84)
boton_exit_inicio = pg.Rect(406, 362, 406, 81)

# Rects para lose/win (900x600)
boton_play_fin = pg.Rect(305, 257, 305, 84)
boton_exit_fin = pg.Rect(305, 362, 305, 81)

while True:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            exit()

        if e.type == pg.KEYDOWN:
            if e.key == pg.K_g:
                estado = "gano"
            elif e.key == pg.K_l:
                estado = "perdido"
            elif estado == "jugando":
                nueva_dir = drs.get(e.key)
                if nueva_dir and nueva_dir != -dr:
                    dr_pendiente = nueva_dir

        elif e.type == pg.MOUSEBUTTONDOWN:
            pos = e.pos
            if estado == "inicio":
                if boton_play_inicio.collidepoint(pos):
                    estado = "jugando"
                elif boton_exit_inicio.collidepoint(pos):
                    exit()
            elif estado in ("perdido", "gano"):
                if boton_play_fin.collidepoint(pos):
                    reset_juego()
                    estado = "jugando"
                elif boton_exit_fin.collidepoint(pos):
                    exit()

    if estado == "jugando":
        ...
        for y in range(10):
            for x in range(ancho_pantalla // tamaño_celda):
                pg.draw.rect(screen, "darkgreen", (x*tamaño_celda, y*tamaño_celda, tamaño_celda, tamaño_celda))
                screen.blit(cut_sprite("grass"), (x*tamaño_celda, y*tamaño_celda))
        for y in range(10):
            for x in range(15, 20):
                pg.draw.rect(screen, "saddlebrown", (x*tamaño_celda, y*tamaño_celda, tamaño_celda, tamaño_celda))
                screen.blit(cut_sprite("dirt"), (x * tamaño_celda, y * tamaño_celda))

        texto_titulo = font1.render(f"snake", True, "white")
        screen.blit(texto_titulo, (ancho_pantalla + 25, 15))

        apple_counter = font3.render(f"apples: {len(pcs)-1}", True, "white")
        screen.blit(apple_counter, (ancho_pantalla + 70, 420))

        gold_counter = font3.render(f"goden apples: {manzanas_doradas}", True, "white")
        screen.blit(gold_counter, (ancho_pantalla + 15, 480))

        contador = font2.render(f"score: {puntos}", True, "white")
        screen.blit(contador, (ancho_pantalla + 20, 170))

        segundos_totales = pg.time.get_ticks() // 1000
        horas = segundos_totales // 3600
        minutos = (segundos_totales % 3600) // 60
        segundos = segundos_totales % 60
        if horas > 0:
            tiempo_str = f"{horas}:{minutos:02d}:{segundos:02d}"
        else:
            tiempo_str = f"{minutos:02d}:{segundos:02d}"
        timer = font2.render(f"time {tiempo_str}", True, "white")
        screen.blit(timer, (ancho_pantalla + 20, 290))

        segundos_totales = pg.time.get_ticks() // 1000
        if segundos_totales != ultimo_segundo_contado:
            puntos += 1
            ultimo_segundo_contado = segundos_totales

        dr = dr_pendiente
        if pcs[0] == fd:
            if tipo_mazana_actual == "apple_1":   
                puntos += 10
            else:
                puntos += 100
                manzanas_doradas +=1
            fd, pcs = food(), pcs + [pcs[0]]

            numero = rnd(1, 9)
            if numero == 9:
                sprite_fd = cut_sprite("apple_2")
                tipo_mazana_actual = "apple_2"
            else:
                sprite_fd = cut_sprite("apple_1")
                tipo_mazana_actual = "apple_1"

        for i, pc in enumerate(pcs):
            if i == 0:
                spr = head_sprite(pcs[0], fd, dr)
            elif i == len(pcs) - 1:
                seg_dir = dir_wrap(pc, pcs[i-1])
                spr = pg.transform.rotate(cut_sprite("tail"), dir_angle(seg_dir))
            else:
                dir_hacia = dir_wrap(pc, pcs[i-1])
                dir_desde = dir_wrap(pcs[i+1], pc)
                if dir_hacia == dir_desde:
                    spr = pg.transform.rotate(cut_sprite("body"), dir_angle(dir_hacia))
                else:
                    spr = curva_angle(dir_desde, dir_hacia)  
            screen.blit(spr, (pc.x*tamaño_celda, pc.y*tamaño_celda))
        screen.blit(sprite_fd, (fd.x*tamaño_celda, fd.y*tamaño_celda))
        pcs.insert(0, pcs[0] + dr)
        pcs.pop(-1)
        pcs[0].x, pcs[0].y = pcs[0].x % 15, pcs[0].y % 10
        if pcs[0] in pcs[1:]:
            estado = "perdido"
        if len(pcs) >= 15 * 10:
                estado = "gano"

    if estado == "inicio":
     screen.blit(game_start, (0, 0))
    elif estado == "perdido":
        screen.blit(lose, (0, 0))
    elif estado == "gano":
        screen.blit(win, (0, 0))
    pg.display.update()
    pg.time.wait(100)

    