"""
PROYECTO ABPro - Cálculo Diferencial
Simulación 3D — Cohete recorriendo una curva r(t) = (x(t), y(t), z(t))

El cálculo es el mismo del proyecto, llevado a tres dimensiones:
    r(t)  = ( x(t),  y(t),  z(t)  )
    v(t)  = r'(t)   → vector velocidad      (flecha verde)
    a(t)  = r''(t)  → vector aceleración    (flecha naranja)

Usa un pequeño motor 3D propio (rotación + proyección en perspectiva) sobre
Pygame, así que NO necesita librerías nuevas ni Tcl/Tk.

Si se ejecuta desde main.py usa la curva elegida en el menú; si se ejecuta
de forma independiente, la pide al usuario.

Integrantes: Shaira Camacho, Emiliano Gómez, Gabriel Paredes, Vicente Schute
Docente:     Fernando Gaitero
Asignatura:  Cálculo Diferencial — INACAP
"""

import os
import sys
import math

import numpy as np
import pygame

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO not in sys.path:
    sys.path.insert(0, DIRECTORIO)
import modelo

# ─────────────────────────────────────────────────────
# 1. MODELO 3D (compartido con main.py)
# ─────────────────────────────────────────────────────
ctx = modelo.obtener_contexto_3d(globals(), "Cohete 3D — curva r(t)")
x_func, y_func, z_func    = ctx["_x_func"],  ctx["_y_func"],  ctx["_z_func"]
vx_func, vy_func, vz_func = ctx["_vx_func"], ctx["_vy_func"], ctx["_vz_func"]
ax_func, ay_func, az_func = ctx["_ax_func"], ctx["_ay_func"], ctx["_az_func"]
r_str = ctx["_r_str"]
T_MAX = ctx["_T_MAX"]


def R(t):
    return np.array([float(x_func(t)), float(y_func(t)), float(z_func(t))])


def Vel(t):
    return np.array([float(vx_func(t)), float(vy_func(t)), float(vz_func(t))])


def Acel(t):
    return np.array([float(ax_func(t)), float(ay_func(t)), float(az_func(t))])


# ─────────────────────────────────────────────────────
# 2. NORMALIZAR LA CURVA (para que cualquier función quepa en pantalla)
# ─────────────────────────────────────────────────────
N = 400
t_arr = np.linspace(0, T_MAX, N)
curva = np.array([R(t) for t in t_arr])
curva = curva[np.all(np.isfinite(curva), axis=1)]      # descartar inf/nan
if len(curva) == 0:
    curva = np.zeros((1, 3))

CENTRO = (curva.max(axis=0) + curva.min(axis=0)) / 2.0
RADIO = float(np.max(np.linalg.norm(curva - CENTRO, axis=1)))
if RADIO < 1e-9:
    RADIO = 1.0
ESCALA = 3.0   # la curva cabe en una esfera de radio ESCALA


def a_mundo(p):
    """Lleva un punto real al espacio normalizado centrado en el origen."""
    return (np.asarray(p, dtype=float) - CENTRO) / RADIO * ESCALA


def vec_mundo(v):
    """Escala un vector (velocidad/aceleración) al espacio normalizado."""
    return np.asarray(v, dtype=float) / RADIO * ESCALA


curva_n = np.array([a_mundo(p) for p in curva])
Y_PISO = float(curva_n[:, 1].min()) - 0.3   # altura de la rejilla de suelo

# ─────────────────────────────────────────────────────
# 3. PYGAME + CÁMARA
# ─────────────────────────────────────────────────────
pygame.init()
ANCHO, ALTO = 1100, 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(f"Cohete 3D  ·  r(t) = {r_str}  |  ABPro Cálculo")

F_GRANDE = pygame.font.SysFont("consolas", 17, bold=True)
F_NORMAL = pygame.font.SysFont("consolas", 14)
F_PEQ    = pygame.font.SysFont("consolas", 12)

FONDO    = (8, 12, 26)
GRIS     = (120, 140, 170)
BLANCO   = (230, 240, 255)
CIAN     = (0, 210, 220)
VERDE    = (50, 220, 120)
ROJO     = (255, 70, 70)
NARANJA  = (255, 165, 40)
AMARILLO = (255, 220, 50)
AZUL_OSC = (28, 48, 86)
AZUL_MED = (60, 120, 210)
ROJO_EJE = (220, 80, 80)
VERDE_EJE = (90, 210, 110)
AZUL_EJE = (90, 140, 230)

reloj = pygame.time.Clock()

# Parámetros de cámara (se controlan con el mouse)
cam = {"yaw": math.radians(35), "pitch": math.radians(22),
       "dist": 9.0, "f": 750.0,
       "cx": (ANCHO - 280) / 2 + 20, "cy": ALTO / 2}


def proyectar(puntos):
    """Proyecta puntos 3D (Nx3) a la pantalla. Devuelve (px Nx2, profundidad N)."""
    pts = np.atleast_2d(np.asarray(puntos, dtype=float))
    x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
    cy_, sy_ = math.cos(cam["yaw"]), math.sin(cam["yaw"])
    xr = x * cy_ + z * sy_
    zr = -x * sy_ + z * cy_
    cp, sp_ = math.cos(cam["pitch"]), math.sin(cam["pitch"])
    yrr = y * cp - zr * sp_
    zrr = y * sp_ + zr * cp
    zc = zrr + cam["dist"]
    zc_safe = np.where(zc <= 0.15, 0.15, zc)
    sx = cam["cx"] + xr * cam["f"] / zc_safe
    sy = cam["cy"] - yrr * cam["f"] / zc_safe
    return np.stack([sx, sy], axis=-1), zc


def p1(punto):
    """Proyecta un solo punto -> (x, y, profundidad)."""
    px, zc = proyectar([punto])
    return px[0], zc[0]


# Pre-proyectar la curva no sirve (la cámara rota), se hace por frame.

def dibujar_linea_3d(p_ini, p_fin, color, grosor=2):
    (a, za), (b, zb) = p1(p_ini), p1(p_fin)
    if za > 0.15 and zb > 0.15:
        pygame.draw.line(pantalla, color, a, b, grosor)


def dibujar_flecha_3d(origen, vector, color, grosor=3):
    """Dibuja una flecha 3D desde 'origen' en la dirección de 'vector'."""
    fin = origen + vector
    (a, za), (b, zb) = p1(origen), p1(fin)
    if za <= 0.15 or zb <= 0.15:
        return
    pygame.draw.line(pantalla, color, a, b, grosor)
    # Punta: dos pequeños segmentos hacia atrás del vector, en pantalla
    d = b - a
    long_d = math.hypot(d[0], d[1])
    if long_d < 1:
        return
    ux, uy = d[0] / long_d, d[1] / long_d
    for signo in (1, -1):
        pygame.draw.line(pantalla, color, b,
                         (b[0] - 10 * ux + signo * 6 * uy,
                          b[1] - 10 * uy - signo * 6 * ux), grosor)


def dibujar_rejilla():
    """Rejilla en el plano del suelo (y = Y_PISO) como referencia de profundidad."""
    pasos = 8
    lim = ESCALA
    for i in range(pasos + 1):
        c = -lim + 2 * lim * i / pasos
        dibujar_linea_3d([c, Y_PISO, -lim], [c, Y_PISO, lim], AZUL_OSC, 1)
        dibujar_linea_3d([-lim, Y_PISO, c], [lim, Y_PISO, c], AZUL_OSC, 1)


def dibujar_ejes():
    """Ejes X (rojo), Y (verde), Z (azul) desde el origen."""
    L = ESCALA * 1.05
    dibujar_linea_3d([0, 0, 0], [L, 0, 0], ROJO_EJE, 2)
    dibujar_linea_3d([0, 0, 0], [0, L, 0], VERDE_EJE, 2)
    dibujar_linea_3d([0, 0, 0], [0, 0, L], AZUL_EJE, 2)
    for p, txt, col in (([L, 0, 0], "X", ROJO_EJE),
                        ([0, L, 0], "Y", VERDE_EJE),
                        ([0, 0, L], "Z", AZUL_EJE)):
        (sx, sy), zc = p1(p)
        if zc > 0.15:
            pantalla.blit(F_PEQ.render(txt, True, col), (sx, sy))


def dibujar_curva():
    pix, zc = proyectar(curva_n)
    for i in range(1, len(pix)):
        if zc[i - 1] > 0.15 and zc[i] > 0.15:
            # color según profundidad (más lejos = más tenue)
            br = max(0.25, min(1.0, 1.4 - zc[i] / (cam["dist"] + ESCALA)))
            col = (int(40 * br), int(110 * br), int(150 * br))
            pygame.draw.line(pantalla, col, pix[i - 1], pix[i], 2)


# ─────────────────────────────────────────────────────
# 4. BUCLE PRINCIPAL
# ─────────────────────────────────────────────────────
VEL_SIM = 1.0
t_actual = 0.0
pausado = False
arrastrando = False
mouse_ant = (0, 0)
ESC_VEC = 0.5   # escala visual de los vectores

running = True
while running:
    dt = reloj.tick(60) / 1000.0

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:  pausado = not pausado
            if ev.key == pygame.K_r:      t_actual = 0.0
            if ev.key == pygame.K_UP:     VEL_SIM = min(VEL_SIM + 0.25, 5.0)
            if ev.key == pygame.K_DOWN:   VEL_SIM = max(VEL_SIM - 0.25, 0.1)
            if ev.key == pygame.K_ESCAPE: running = False
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == 1:
                arrastrando = True
                mouse_ant = ev.pos
            elif ev.button == 4:   # rueda arriba → acercar
                cam["dist"] = max(4.0, cam["dist"] - 0.6)
            elif ev.button == 5:   # rueda abajo → alejar
                cam["dist"] = min(20.0, cam["dist"] + 0.6)
        elif ev.type == pygame.MOUSEBUTTONUP:
            if ev.button == 1:
                arrastrando = False
        elif ev.type == pygame.MOUSEMOTION and arrastrando:
            dx = ev.pos[0] - mouse_ant[0]
            dy = ev.pos[1] - mouse_ant[1]
            cam["yaw"] += dx * 0.01
            cam["pitch"] = max(-1.4, min(1.4, cam["pitch"] + dy * 0.01))
            mouse_ant = ev.pos

    if not pausado:
        t_actual += dt * VEL_SIM
        if t_actual > T_MAX:
            t_actual = 0.0

    # Valores reales y normalizados
    r_real = R(t_actual)
    v_real = Vel(t_actual)
    a_real = Acel(t_actual)
    p_n = a_mundo(r_real)
    v_n = vec_mundo(v_real) * ESC_VEC
    a_n = vec_mundo(a_real) * ESC_VEC
    # Limitar longitud de las flechas para que no se salgan
    for vec in (v_n, a_n):
        L = np.linalg.norm(vec)
        if L > ESCALA:
            vec *= ESCALA / L

    # ─── DIBUJO ───────────────────────────────────────
    pantalla.fill(FONDO)
    dibujar_rejilla()
    dibujar_ejes()
    dibujar_curva()

    # Vectores velocidad (verde) y aceleración (naranja)
    dibujar_flecha_3d(p_n, v_n, VERDE, 3)
    dibujar_flecha_3d(p_n, a_n, NARANJA, 3)

    # Objeto (cohete) como esfera proyectada, tamaño según perspectiva
    (sx, sy), zc = p1(p_n)
    if zc > 0.15:
        radio_px = max(5, int(140 / zc))
        pygame.draw.circle(pantalla, CIAN, (int(sx), int(sy)), radio_px)
        pygame.draw.circle(pantalla, BLANCO, (int(sx), int(sy)), radio_px, 2)

    # ── Título ──
    tit = F_GRANDE.render("Cohete en 3D  —  Modelo Diferencial  |  ABPro Cálculo Diferencial", True, BLANCO)
    pantalla.blit(tit, (20, 12))
    pantalla.blit(F_NORMAL.render(f"r(t) = {r_str}", True, CIAN), (20, 36))

    # ── Panel HUD (derecha) ──
    px2 = ANCHO - 255
    pygame.draw.rect(pantalla, AZUL_OSC, (px2 - 12, 64, 252, 360), border_radius=8)
    pygame.draw.rect(pantalla, AZUL_MED, (px2 - 12, 64, 252, 360), 1, border_radius=8)
    pantalla.blit(F_GRANDE.render("HUD DE VUELO 3D", True, CIAN), (px2, 74))

    filas = [
        ("TIEMPO", f"t = {t_actual:.2f} s", AMARILLO),
        ("POSICION r(t)",
         [f"x = {r_real[0]:.2f}", f"y = {r_real[1]:.2f}", f"z = {r_real[2]:.2f}"], AZUL_MED),
        ("VELOCIDAD v(t)",
         [f"x = {v_real[0]:.2f}", f"y = {v_real[1]:.2f}", f"z = {v_real[2]:.2f}",
          f"|v| = {np.linalg.norm(v_real):.2f}"], VERDE),
        ("ACELERACION a(t)",
         [f"x = {a_real[0]:.2f}", f"y = {a_real[1]:.2f}", f"z = {a_real[2]:.2f}",
          f"|a| = {np.linalg.norm(a_real):.2f}"], NARANJA),
    ]
    y_d = 104
    for etiqueta, valor, col in filas:
        pantalla.blit(F_PEQ.render(etiqueta, True, GRIS), (px2, y_d))
        y_d += 16
        if isinstance(valor, str):
            pantalla.blit(F_NORMAL.render(valor, True, col), (px2, y_d))
            y_d += 24
        else:
            for linea in valor:
                pantalla.blit(F_NORMAL.render(linea, True, col), (px2 + 6, y_d))
                y_d += 18
            y_d += 6

    pantalla.blit(F_PEQ.render(f"velocidad sim: {VEL_SIM:.2f}x", True, GRIS), (px2, y_d))

    # ── Barra de progreso ──
    pw = ANCHO - 320
    py = ALTO - 30
    pygame.draw.rect(pantalla, AZUL_OSC, (20, py, pw, 10), border_radius=5)
    fw = int(pw * t_actual / T_MAX) if T_MAX else 0
    pygame.draw.rect(pantalla, CIAN, (20, py, fw, 10), border_radius=5)

    ctrl = F_PEQ.render(
        "Arrastrar: rotar | Rueda: zoom | SPACE: pausa | R: reinicia | UP/DOWN: velocidad | ESC: salir",
        True, GRIS)
    pantalla.blit(ctrl, (20, ALTO - 16))

    if pausado:
        pausa = F_GRANDE.render("PAUSADO", True, AMARILLO)
        pantalla.blit(pausa, (int(cam["cx"]) - pausa.get_width() // 2, 60))

    pygame.display.flip()

pygame.quit()
sys.exit()
