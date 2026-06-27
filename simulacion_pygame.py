"""
PROYECTO ABPro - Cálculo Diferencial
Simulación Visual con Pygame — objeto sobre una línea

La posición del objeto en pantalla se calcula directamente desde el modelo
diferencial s(t). El objeto (círculo) se mueve según esa función y se muestran
en pantalla los valores de s(t), v(t) y a(t) en tiempo real.

Si se ejecuta desde main.py usa la función elegida en el menú; si se ejecuta
de forma independiente, la pide al usuario.

Integrantes: Shaira Camacho, Emiliano Gómez, Gabriel Paredes, Vicente Schute
Docente:     Fernando Gaitero
Asignatura:  Cálculo Diferencial
"""

import os
import sys

import numpy as np
import pygame

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO not in sys.path:
    sys.path.insert(0, DIRECTORIO)
import modelo

# ─────────────────────────────────────────────
# MODELO MATEMÁTICO (compartido con main.py)
# ─────────────────────────────────────────────
ctx        = modelo.obtener_contexto(globals(), "Simulación en línea — s(t)")
posicion   = ctx["_s_func"]
velocidad  = ctx["_v_func"]
aceleracion = ctx["_a_func"]
expr_str   = ctx["_expr_str"]
T_MAX      = ctx["_T_MAX"]

# Rangos reales de cada magnitud (para mapear a pantalla y a las barras).
_t_muestra = np.linspace(0, T_MAX, 600)
_s_m = np.asarray(posicion(_t_muestra), dtype=float)
_v_m = np.asarray(velocidad(_t_muestra), dtype=float)
_a_m = np.asarray(aceleracion(_t_muestra), dtype=float)
_s_m = _s_m[np.isfinite(_s_m)]
_v_m = _v_m[np.isfinite(_v_m)]
_a_m = _a_m[np.isfinite(_a_m)]

S_MIN_REAL = float(np.min(_s_m)) if _s_m.size else 0.0
S_MAX_REAL = float(np.max(_s_m)) if _s_m.size else 1.0
if abs(S_MAX_REAL - S_MIN_REAL) < 1e-9:
    S_MIN_REAL -= 1.0
    S_MAX_REAL += 1.0
V_LIM = max(abs(float(np.min(_v_m))) if _v_m.size else 1.0,
            abs(float(np.max(_v_m))) if _v_m.size else 1.0, 0.01)
A_LIM = max(abs(float(np.min(_a_m))) if _a_m.size else 1.0,
            abs(float(np.max(_a_m))) if _a_m.size else 1.0, 0.01)

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PYGAME
# ─────────────────────────────────────────────
pygame.init()

ANCHO, ALTO = 900, 560
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(
    f"Modelo Diferencial — s(t) = {expr_str}  |  ABPro Cálculo Diferencial"
)

fuente_grande  = pygame.font.SysFont("consolas", 20, bold=True)
fuente_normal  = pygame.font.SysFont("consolas", 16)
fuente_pequena = pygame.font.SysFont("consolas", 13)

FONDO       = (15,  25,  40)
BLANCO      = (255, 255, 255)
GRIS_CLARO  = (180, 190, 210)
GRIS_OSCURO = (40,  55,  75)
AZUL        = (52,  152, 219)
VERDE       = (39,  174,  96)
ROJO        = (231,  76,  60)
NARANJA     = (230, 126,  34)
AMARILLO    = (241, 196,  15)
MORADO      = (155,  89, 182)
CIAN        = (26,  188, 156)

reloj = pygame.time.Clock()

# ─────────────────────────────────────────────
# PARÁMETROS DE LA SIMULACIÓN
# ─────────────────────────────────────────────
VELOCIDAD_SIM = 0.6      # cuánto avanza t por segundo real

ZONA_Y     = 320
ZONA_X_MIN = 80
ZONA_X_MAX = ANCHO - 80
ZONA_ANCHO = ZONA_X_MAX - ZONA_X_MIN


def s_a_pixel_x(s):
    """Convierte valor matemático s → coordenada X en pantalla."""
    rango = S_MAX_REAL - S_MIN_REAL
    if rango == 0:
        return ZONA_X_MIN
    proporcion = (s - S_MIN_REAL) / rango
    return int(ZONA_X_MIN + proporcion * ZONA_ANCHO)


def dibujar_barra(superficie, x, y, ancho, alto, valor, v_min, v_max, color, etiqueta):
    """Dibuja una barra para mostrar un valor dentro de un rango."""
    pygame.draw.rect(superficie, GRIS_OSCURO, (x, y, ancho, alto), border_radius=4)
    rango = v_max - v_min
    proporcion = max(0.0, min(1.0, (valor - v_min) / rango)) if rango else 0.5
    fill_w = int(ancho * proporcion)
    if fill_w > 0:
        pygame.draw.rect(superficie, color, (x, y, fill_w, alto), border_radius=4)
    pygame.draw.rect(superficie, GRIS_CLARO, (x, y, ancho, alto), 1, border_radius=4)
    superficie.blit(fuente_pequena.render(etiqueta, True, GRIS_CLARO), (x, y - 18))


# ─────────────────────────────────────────────
# BUCLE PRINCIPAL
# ─────────────────────────────────────────────
t_actual    = 0.0
pausado     = False
trayectoria = []

running = True
while running:
    dt = reloj.tick(60) / 1000.0

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                pausado = not pausado
            if evento.key == pygame.K_r:
                t_actual = 0.0
                trayectoria = []
            if evento.key == pygame.K_ESCAPE:
                running = False

    if not pausado:
        t_actual += dt * VELOCIDAD_SIM
        if t_actual > T_MAX:
            t_actual = 0.0
            trayectoria = []

    s = float(posicion(t_actual))
    v = float(velocidad(t_actual))
    a = float(aceleracion(t_actual))
    px = s_a_pixel_x(s)
    py = ZONA_Y

    if not pausado:
        trayectoria.append((px, py))
        if len(trayectoria) > 800:
            trayectoria.pop(0)

    # ── DIBUJO ──
    pantalla.fill(FONDO)

    titulo = fuente_grande.render(
        "Modelo Diferencial de Movimiento 2D  —  ABPro Cálculo Diferencial",
        True, BLANCO)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 14))

    subtitulo = fuente_normal.render(f"s(t) = {expr_str}", True, CIAN)
    pantalla.blit(subtitulo, (ANCHO // 2 - subtitulo.get_width() // 2, 40))

    pygame.draw.line(pantalla, GRIS_OSCURO, (ZONA_X_MIN, ZONA_Y), (ZONA_X_MAX, ZONA_Y), 2)

    for t_marca in range(0, int(T_MAX) + 1):
        s_marca = float(posicion(t_marca))
        x_marca = s_a_pixel_x(s_marca)
        pygame.draw.line(pantalla, GRIS_CLARO, (x_marca, ZONA_Y - 8), (x_marca, ZONA_Y + 8), 1)
        lbl = fuente_pequena.render(f"t={t_marca}", True, GRIS_CLARO)
        pantalla.blit(lbl, (x_marca - lbl.get_width() // 2, ZONA_Y + 12))

    if len(trayectoria) >= 2:
        n = len(trayectoria)
        for i in range(1, n):
            alpha = i / n
            color_rastro = (int(CIAN[0] * alpha), int(CIAN[1] * alpha), int(CIAN[2] * alpha))
            pygame.draw.line(pantalla, color_rastro, trayectoria[i - 1], trayectoria[i], 2)

    radio = 22
    if abs(v) < 0.3:
        color_obj = AMARILLO
    elif v > 0:
        color_obj = VERDE
    else:
        color_obj = ROJO

    pygame.draw.circle(pantalla, color_obj, (px, py), radio)
    pygame.draw.circle(pantalla, BLANCO,    (px, py), radio, 2)

    if abs(v) > 0.1:
        dir_x = 1 if v > 0 else -1
        largo = min(40, int(abs(v) * 8))
        pygame.draw.line(pantalla, BLANCO, (px, py), (px + dir_x * (radio + largo), py), 3)
        pygame.draw.polygon(pantalla, BLANCO, [
            (px + dir_x * (radio + largo),     py),
            (px + dir_x * (radio + largo - 8), py - 5),
            (px + dir_x * (radio + largo - 8), py + 5),
        ])

    # Panel de datos
    panel_x = ANCHO - 260
    panel_y = 90
    pygame.draw.rect(pantalla, GRIS_OSCURO, (panel_x - 10, panel_y - 10, 250, 230), border_radius=8)
    pygame.draw.rect(pantalla, AZUL,        (panel_x - 10, panel_y - 10, 250, 230), 1, border_radius=8)

    pantalla.blit(fuente_normal.render("Valores en tiempo real", True, AZUL), (panel_x, panel_y))

    datos = [
        (f"t   = {t_actual:.2f} s",   AMARILLO),
        (f"s(t) = {s:.3f} m",         AZUL),
        (f"v(t) = {v:.3f} m/s",       VERDE if v >= 0 else ROJO),
        (f"a(t) = {a:.3f} m/s2",      NARANJA if a >= 0 else MORADO),
    ]
    for i, (texto, color) in enumerate(datos):
        pantalla.blit(fuente_normal.render(texto, True, color), (panel_x, panel_y + 30 + i * 28))

    if abs(v) < 0.3:
        estado_txt, estado_color = "[ ]  Objeto casi detenido", AMARILLO
    elif v > 0:
        estado_txt, estado_color = "->  Avanzando", VERDE
    else:
        estado_txt, estado_color = "<-  Retrocediendo", ROJO
    pantalla.blit(fuente_normal.render(estado_txt, True, estado_color), (panel_x, panel_y + 145))

    if a > 0:
        acel_txt, acel_color = "/\\  Acelerando", VERDE
    elif a < 0:
        acel_txt, acel_color = "\\/  Frenando", ROJO
    else:
        acel_txt, acel_color = "--  Aceleracion nula", AMARILLO
    pantalla.blit(fuente_normal.render(acel_txt, True, acel_color), (panel_x, panel_y + 170))

    # Barras visuales (rangos calculados de la función real)
    barra_y = 420
    dibujar_barra(pantalla, 80, barra_y,       220, 18, s, S_MIN_REAL, S_MAX_REAL, AZUL,    "Posicion s(t)")
    dibujar_barra(pantalla, 80, barra_y + 50,  220, 18, v, -V_LIM, V_LIM,          VERDE,   "Velocidad v(t)")
    dibujar_barra(pantalla, 80, barra_y + 100, 220, 18, a, -A_LIM, A_LIM,          NARANJA, "Aceleracion a(t)")

    # Progreso de tiempo
    prog_w = ANCHO - 160
    pygame.draw.rect(pantalla, GRIS_OSCURO, (80, ALTO - 30, prog_w, 10), border_radius=5)
    fill = int(prog_w * t_actual / T_MAX) if T_MAX else 0
    pygame.draw.rect(pantalla, CIAN, (80, ALTO - 30, fill, 10), border_radius=5)
    pygame.draw.rect(pantalla, GRIS_CLARO, (80, ALTO - 30, prog_w, 10), 1, border_radius=5)

    t_lbl = fuente_pequena.render(f"t = {t_actual:.2f} / {T_MAX:.1f} s", True, GRIS_CLARO)
    pantalla.blit(t_lbl, (80, ALTO - 48))

    controles = fuente_pequena.render("SPACE: pausar  |  R: reiniciar  |  ESC: salir", True, GRIS_CLARO)
    pantalla.blit(controles, (ANCHO // 2 - controles.get_width() // 2, ALTO - 48))

    if pausado:
        pausa = fuente_grande.render("PAUSADO", True, AMARILLO)
        pantalla.blit(pausa, (ANCHO // 2 - pausa.get_width() // 2, ALTO // 2 - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
