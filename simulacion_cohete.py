"""
PROYECTO ABPro - Cálculo Diferencial
Simulación 2D — Cohete recorriendo la trayectoria de s(t)

El eje X representa el tiempo t y el eje Y la posición s(t).
El cohete vuela por la curva y muestra v(t) y a(t) en tiempo real,
orientando su nariz según la pendiente REAL de la curva en pantalla.

Si se ejecuta desde main.py usa la función elegida en el menú; si se
ejecuta de forma independiente, la pide al usuario.

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
# 1. MODELO (compartido con main.py)
# ─────────────────────────────────────────────────────
ctx       = modelo.obtener_contexto(globals(), "Cohete 2D — función s(t)")
s_func    = ctx["_s_func"]
v_func    = ctx["_v_func"]
a_func    = ctx["_a_func"]
expr_str  = ctx["_expr_str"]
v_str     = ctx["_v_str"]
a_str     = ctx["_a_str"]
T_MAX     = ctx["_T_MAX"]

# ─────────────────────────────────────────────────────
# 2. PRE-CALCULAR CURVA COMPLETA
# ─────────────────────────────────────────────────────
N = 600
t_arr = np.linspace(0, T_MAX, N)
s_arr = np.asarray(s_func(t_arr), dtype=float)
v_arr = np.asarray(v_func(t_arr), dtype=float)
a_arr = np.asarray(a_func(t_arr), dtype=float)


def _rango_finito(arr, defecto=(0.0, 1.0)):
    """min/max ignorando inf y nan (p. ej. derivadas que divergen en t=0)."""
    fin = arr[np.isfinite(arr)]
    if fin.size == 0:
        return defecto
    return float(np.min(fin)), float(np.max(fin))


S_MIN, S_MAX = _rango_finito(s_arr, (0.0, 1.0))
_vmin, _vmax = _rango_finito(v_arr, (-1.0, 1.0))
_amin, _amax = _rango_finito(a_arr, (-1.0, 1.0))
T_MIN_V = float(np.min(t_arr))
T_MAX_V = float(np.max(t_arr))
V_ABS = max(abs(_vmin), abs(_vmax), 0.01)
A_ABS = max(abs(_amin), abs(_amax), 0.01)

if abs(S_MAX - S_MIN) < 1e-9:
    S_MIN -= 1.0
    S_MAX += 1.0
if abs(T_MAX_V - T_MIN_V) < 1e-9:
    T_MAX_V = T_MIN_V + 1.0

# ─────────────────────────────────────────────────────
# 3. PYGAME SETUP
# ─────────────────────────────────────────────────────
pygame.init()

ANCHO, ALTO = 1100, 660
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(f"Cohete 2D  ·  s(t) = {expr_str}  |  ABPro Cálculo")

F_GRANDE = pygame.font.SysFont("consolas", 17, bold=True)
F_NORMAL = pygame.font.SysFont("consolas", 14)
F_PEQ    = pygame.font.SysFont("consolas", 12)

FONDO      = (8,   14,  30)
CUADRICULA = (20,  35,  60)
GRIS       = (120, 140, 170)
BLANCO     = (230, 240, 255)
CIAN       = (0,   210, 220)
VERDE      = (50,  220, 120)
ROJO       = (255,  70,  70)
NARANJA    = (255, 165,  40)
AMARILLO   = (255, 220,  50)
MORADO     = (170,  90, 230)
AZUL_OSC   = (30,   55, 100)
AZUL_MED   = (50,  110, 200)

reloj = pygame.time.Clock()

MARGEN_IZQ = 80
MARGEN_DER = 310
MARGEN_SUP = 70
MARGEN_INF = 60

PLANO_X = MARGEN_IZQ
PLANO_Y = MARGEN_SUP
PLANO_W = ANCHO - MARGEN_IZQ - MARGEN_DER
PLANO_H = ALTO - MARGEN_SUP - MARGEN_INF

PAD = 40

# Píxeles por unidad de cada eje (sirven para orientar el cohete sobre la curva)
KX = (PLANO_W - 2 * PAD) / (T_MAX_V - T_MIN_V)
KY = (PLANO_H - 2 * PAD) / (S_MAX - S_MIN)


def mundo_a_px(t_val, s_val):
    """Convierte coordenadas matemáticas (t, s) a píxeles en pantalla."""
    rx = (t_val - T_MIN_V) / (T_MAX_V - T_MIN_V)
    ry = (s_val - S_MIN) / (S_MAX - S_MIN)
    px = PLANO_X + PAD + rx * (PLANO_W - 2 * PAD)
    py = PLANO_Y + PLANO_H - PAD - ry * (PLANO_H - 2 * PAD)
    return int(px), int(py)


puntos_curva = [mundo_a_px(t_arr[i], s_arr[i]) for i in range(N)]


# ─────────────────────────────────────────────────────
# 4. DIBUJAR COHETE
# ─────────────────────────────────────────────────────
def dibujar_cohete(surf, cx, cy, angulo_rad, escala=1.0, color_llama=NARANJA):
    """Dibuja un cohete rotado según el ángulo de la tangente (en pantalla)."""
    cos_a = math.cos(angulo_rad)
    sin_a = math.sin(angulo_rad)

    def rotar(x, y):
        rx = x * cos_a - y * sin_a
        ry = x * sin_a + y * cos_a
        return (int(cx + rx * escala), int(cy + ry * escala))

    nariz    = rotar(18, 0)
    ala_izq  = rotar(-10, -9)
    ala_der  = rotar(-10, 9)
    cola_iz  = rotar(-14, -5)
    cola_der = rotar(-14, 5)

    llama1 = rotar(-18, 0)
    llama2 = rotar(-26, -5)
    llama3 = rotar(-26, 5)

    pygame.draw.circle(surf, (30, 60, 100), (cx, cy), int(16 * escala), 0)
    pygame.draw.polygon(surf, color_llama, [llama1, llama2, llama3])
    pygame.draw.polygon(surf, AMARILLO, [rotar(-18, 0), rotar(-22, -3), rotar(-22, 3)])
    pygame.draw.polygon(surf, BLANCO, [nariz, ala_izq, rotar(-8, 0), ala_der])
    pygame.draw.polygon(surf, CIAN, [ala_izq, cola_iz, rotar(-12, 0)])
    pygame.draw.polygon(surf, CIAN, [ala_der, cola_der, rotar(-12, 0)])

    ventana = rotar(6, 0)
    pygame.draw.circle(surf, AZUL_MED, ventana, int(4 * escala))
    pygame.draw.circle(surf, CIAN, ventana, int(4 * escala), 1)


def dibujar_barra_hud(surf, x, y, w, h, val, vmin, vmax, col, label):
    pygame.draw.rect(surf, AZUL_OSC, (x, y, w, h), border_radius=3)
    rng = vmax - vmin
    prop = max(0.0, min(1.0, (val - vmin) / rng)) if rng else 0.5
    fw = int(w * prop)
    if fw > 0:
        pygame.draw.rect(surf, col, (x, y, fw, h), border_radius=3)
    pygame.draw.rect(surf, GRIS, (x, y, w, h), 1, border_radius=3)
    surf.blit(F_PEQ.render(label, True, GRIS), (x, y - 15))


# ─────────────────────────────────────────────────────
# 5. BUCLE PRINCIPAL
# ─────────────────────────────────────────────────────
VEL_SIM  = 0.5
t_actual = 0.0
pausado  = False
rastro   = []

running = True
while running:
    dt = reloj.tick(60) / 1000.0

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                pausado = not pausado
            if ev.key == pygame.K_r:
                t_actual = 0.0
                rastro = []
            if ev.key == pygame.K_UP:
                VEL_SIM = min(VEL_SIM + 0.1, 3.0)
            if ev.key == pygame.K_DOWN:
                VEL_SIM = max(VEL_SIM - 0.1, 0.1)
            if ev.key == pygame.K_ESCAPE:
                running = False

    if not pausado:
        t_actual += dt * VEL_SIM
        if t_actual > T_MAX:
            t_actual = 0.0
            rastro = []

    try:
        s_val = float(s_func(t_actual))
        v_val = float(v_func(t_actual))
        a_val = float(a_func(t_actual))
    except Exception:
        s_val = v_val = a_val = 0.0

    cx, cy = mundo_a_px(t_actual, s_val)

    # Ángulo de la tangente EN PANTALLA (corrige la distinta escala de cada eje).
    # Avanzar dt:  dpx = KX·1   ;   dpy = -KY·v  (py disminuye al subir s)
    dpx = KX
    dpy = -KY * v_val
    angulo = math.atan2(dpy, dpx)

    if not pausado:
        rastro.append((cx, cy))
        if len(rastro) > 1200:
            rastro.pop(0)

    # ─── DIBUJO ───────────────────────────────────────
    pantalla.fill(FONDO)

    pygame.draw.rect(pantalla, CUADRICULA, (PLANO_X, PLANO_Y, PLANO_W, PLANO_H), 0)
    pygame.draw.rect(pantalla, AZUL_OSC, (PLANO_X, PLANO_Y, PLANO_W, PLANO_H), 1)

    for k in range(11):
        xg = PLANO_X + PAD + k * (PLANO_W - 2 * PAD) // 10
        pygame.draw.line(pantalla, AZUL_OSC, (xg, PLANO_Y), (xg, PLANO_Y + PLANO_H), 1)
        yg = PLANO_Y + PAD + k * (PLANO_H - 2 * PAD) // 10
        pygame.draw.line(pantalla, AZUL_OSC, (PLANO_X, yg), (PLANO_X + PLANO_W, yg), 1)

    for k in range(6):
        t_lbl = T_MIN_V + k * (T_MAX_V - T_MIN_V) / 5
        xp, _ = mundo_a_px(t_lbl, S_MIN)
        lbl = F_PEQ.render(f"{t_lbl:.1f}", True, GRIS)
        pantalla.blit(lbl, (xp - lbl.get_width() // 2, PLANO_Y + PLANO_H + 5))
        s_lbl = S_MIN + k * (S_MAX - S_MIN) / 5
        _, yp = mundo_a_px(T_MIN_V, s_lbl)
        lbl2 = F_PEQ.render(f"{s_lbl:.1f}", True, GRIS)
        pantalla.blit(lbl2, (PLANO_X - lbl2.get_width() - 5, yp - 7))

    eje_t = F_PEQ.render("t  [s]", True, GRIS)
    pantalla.blit(eje_t, (PLANO_X + PLANO_W // 2 - eje_t.get_width() // 2, PLANO_Y + PLANO_H + 22))
    eje_s = F_PEQ.render("s(t)  [m]", True, GRIS)
    pantalla.blit(pygame.transform.rotate(eje_s, 90), (PLANO_X - 55, PLANO_Y + PLANO_H // 2 - eje_s.get_width() // 2))

    if len(puntos_curva) >= 2:
        pygame.draw.lines(pantalla, (40, 80, 140), False, puntos_curva, 2)

    if len(rastro) >= 2:
        n = len(rastro)
        for i in range(1, n):
            alpha = i / n
            col_rastro = (int(CIAN[0] * alpha), int(CIAN[1] * alpha), int(CIAN[2] * alpha))
            pygame.draw.line(pantalla, col_rastro, rastro[i - 1], rastro[i], 2)

    color_llama = NARANJA if a_val >= 0 else ROJO
    dibujar_cohete(pantalla, cx, cy, angulo, escala=1.2, color_llama=color_llama)

    tit = F_GRANDE.render("Trayectoria del Cohete  —  Modelo Diferencial  |  ABPro Cálculo Diferencial", True, BLANCO)
    pantalla.blit(tit, (ANCHO // 2 - tit.get_width() // 2, 10))
    sub = F_NORMAL.render(f"s(t) = {expr_str}", True, CIAN)
    pantalla.blit(sub, (ANCHO // 2 - sub.get_width() // 2, 33))

    # Panel HUD
    px2 = ANCHO - MARGEN_DER + 15
    py2 = MARGEN_SUP
    pygame.draw.rect(pantalla, AZUL_OSC, (px2 - 10, py2 - 5, MARGEN_DER - 20, ALTO - MARGEN_SUP - MARGEN_INF + 5), border_radius=8)
    pygame.draw.rect(pantalla, AZUL_MED, (px2 - 10, py2 - 5, MARGEN_DER - 20, ALTO - MARGEN_SUP - MARGEN_INF + 5), 1, border_radius=8)

    pantalla.blit(F_GRANDE.render(">  HUD DE VUELO", True, CIAN), (px2, py2))

    datos = [
        ("TIEMPO",      f"t = {t_actual:.2f} s",  AMARILLO),
        ("POSICION",    f"s = {s_val:.3f} m",     AZUL_MED),
        ("VELOCIDAD",   f"v = {v_val:.3f} m/s",   VERDE if v_val >= 0 else ROJO),
        ("ACELERACION", f"a = {a_val:.3f} m/s2",  NARANJA if a_val >= 0 else MORADO),
    ]
    for i, (etiq, valor, col) in enumerate(datos):
        y_d = py2 + 35 + i * 55
        pantalla.blit(F_PEQ.render(etiq, True, GRIS), (px2, y_d))
        pantalla.blit(F_NORMAL.render(valor, True, col), (px2, y_d + 16))

    by = py2 + 265
    dibujar_barra_hud(pantalla, px2, by,      250, 14, s_val, S_MIN, S_MAX, AZUL_MED, "Posicion s(t)")
    dibujar_barra_hud(pantalla, px2, by + 40, 250, 14, v_val, -V_ABS, V_ABS, VERDE,   "Velocidad v(t)")
    dibujar_barra_hud(pantalla, px2, by + 80, 250, 14, a_val, -A_ABS, A_ABS, NARANJA, "Aceleracion a(t)")

    if abs(v_val) < 0.05:
        est_txt, est_col = "[ ]  EN REPOSO", AMARILLO
    elif v_val > 0:
        est_txt, est_col = "/^  ASCENDIENDO", VERDE
    else:
        est_txt, est_col = "\\v  DESCENDIENDO", ROJO

    if a_val > 0.05:
        acel_txt, acel_col = "++  ACELERANDO", NARANJA
    elif a_val < -0.05:
        acel_txt, acel_col = "--  FRENANDO", MORADO
    else:
        acel_txt, acel_col = "==  ACEL. NULA", GRIS

    pantalla.blit(F_NORMAL.render(est_txt, True, est_col), (px2, by + 110))
    pantalla.blit(F_NORMAL.render(acel_txt, True, acel_col), (px2, by + 135))

    pantalla.blit(F_PEQ.render(f"Velocidad sim: {VEL_SIM:.1f}x  (UP/DOWN)", True, GRIS), (px2, by + 165))

    pantalla.blit(F_PEQ.render(f"v(t) = {v_str[:28]}", True, VERDE), (px2, by + 195))
    pantalla.blit(F_PEQ.render(f"a(t) = {a_str[:28]}", True, NARANJA), (px2, by + 212))

    pw2 = PLANO_W - 2 * PAD
    px_prog = PLANO_X + PAD
    py_prog = ALTO - 35
    pygame.draw.rect(pantalla, AZUL_OSC, (px_prog, py_prog, pw2, 10), border_radius=5)
    fw3 = int(pw2 * t_actual / T_MAX) if T_MAX else 0
    pygame.draw.rect(pantalla, CIAN, (px_prog, py_prog, fw3, 10), border_radius=5)
    pygame.draw.rect(pantalla, GRIS, (px_prog, py_prog, pw2, 10), 1, border_radius=5)

    ctrl = F_PEQ.render("SPACE: pausar  |  R: reiniciar  |  UP/DOWN: velocidad  |  ESC: salir", True, GRIS)
    pantalla.blit(ctrl, (ANCHO // 2 - ctrl.get_width() // 2, ALTO - 18))

    if pausado:
        p = F_GRANDE.render("PAUSADO", True, AMARILLO)
        pantalla.blit(p, (PLANO_X + PLANO_W // 2 - p.get_width() // 2, PLANO_Y + PLANO_H // 2 - 15))

    pygame.display.flip()

pygame.quit()
sys.exit()
