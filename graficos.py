"""
PROYECTO ABPro - Cálculo Diferencial
Diseño y validación de un modelo diferencial para el movimiento de objetos en 2D y 3D

Función de posición (por defecto): s(t) = t³ - 6t² + 9t
Velocidad:    v(t) = s'(t)
Aceleración:  a(t) = s''(t)

Si se ejecuta desde main.py usa la función elegida en el menú; si se
ejecuta de forma independiente, la pide al usuario.

Integrantes: Shaira Camacho, Emiliano Gómez, Gabriel Paredes, Vicente Schute
Docente:     Fernando Gaitero
Asignatura:  Cálculo Diferencial
"""

import os
import sys
import subprocess

import numpy as np
import matplotlib
# Backend sin ventana: NO depende de Tcl/Tk (que en algunas instalaciones de
# Python en Windows viene roto). Evita el error "Can't find a usable init.tcl".
# El gráfico se guarda como PNG y se abre con el visor del sistema operativo.
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO not in sys.path:
    sys.path.insert(0, DIRECTORIO)
import modelo

# ─────────────────────────────────────────────
# 1. OBTENER EL MODELO (compartido con main.py)
# ─────────────────────────────────────────────
ctx        = modelo.obtener_contexto(globals(), "Gráficos — función s(t)")
posicion   = ctx["_s_func"]
velocidad  = ctx["_v_func"]
aceleracion = ctx["_a_func"]
expr_str   = ctx["_expr_str"]
v_str      = ctx["_v_str"]
a_str      = ctx["_a_str"]
s_tex      = ctx.get("_s_latex", expr_str)
v_tex      = ctx.get("_v_latex", v_str)
a_tex      = ctx.get("_a_latex", a_str)
T_MAX      = ctx["_T_MAX"]

# ─────────────────────────────────────────────
# 2. RANGO DE TIEMPO Y EVALUACIÓN
# ─────────────────────────────────────────────
t = np.linspace(0, T_MAX, 500)
s = posicion(t)
v = velocidad(t)
a = aceleracion(t)

# Puntos notables calculados para CUALQUIER función (no hardcodeados).
t_criticos  = modelo.puntos_criticos(ctx)
s_criticos  = [float(posicion(tc)) for tc in t_criticos]
v_criticos  = [float(velocidad(tc)) for tc in t_criticos]
t_inflexion = modelo.puntos_inflexion(ctx)

# ─────────────────────────────────────────────
# 3. FIGURA PRINCIPAL: 3 GRÁFICOS
# ─────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
fig.suptitle(
    f"Modelo Diferencial de Movimiento  ·  $s(t) = {s_tex}$",
    fontsize=14, fontweight="bold", y=0.98,
)

colores = {"pos": "#1a7abf", "vel": "#27ae60", "acel": "#e74c3c"}

# ── Gráfico 1: Posición ──
ax1 = axes[0]
ax1.plot(t, s, color=colores["pos"], linewidth=2.5, label=f"$s(t) = {s_tex}$")
ax1.fill_between(t, s, alpha=0.08, color=colores["pos"])
if t_criticos:
    ax1.scatter(t_criticos, s_criticos, color="orange", zorder=5, s=80,
                label="Puntos críticos (v=0)")
for ti in t_inflexion:
    ax1.axvline(ti, color="gray", linestyle="--", linewidth=1)
if t_inflexion:
    # una sola entrada en la leyenda para las inflexiones
    ax1.axvline(t_inflexion[0], color="gray", linestyle="--", linewidth=1,
                label="Punto(s) de inflexión")
ax1.set_ylabel("Posición  s(t)  [m]", fontsize=11)
ax1.set_title("Posición", fontsize=11)
ax1.grid(True, alpha=0.3)
for tc, sc in zip(t_criticos, s_criticos):
    ax1.annotate(f"t={tc:g}\ns={sc:.1f}m", xy=(tc, sc),
                 xytext=(8, 10), textcoords="offset points",
                 fontsize=8, color="darkorange",
                 arrowprops=dict(arrowstyle="->", color="orange"))
ax1.legend(fontsize=9, loc="best")   # leyenda al final → recoge todo

# ── Gráfico 2: Velocidad ──
ax2 = axes[1]
ax2.plot(t, v, color=colores["vel"], linewidth=2.5, label=f"$v(t) = {v_tex}$")
ax2.axhline(0, color="black", linewidth=0.8, linestyle="--")
# Los rellenos se dibujan ANTES de la leyenda para que aparezcan en ella.
ax2.fill_between(t, v, 0, where=(v >= 0), alpha=0.12, color=colores["vel"],
                 label="Avanzando (v > 0)")
ax2.fill_between(t, v, 0, where=(v < 0), alpha=0.12, color="red",
                 label="Retrocediendo (v < 0)")
if t_criticos:
    ax2.scatter(t_criticos, v_criticos, color="orange", zorder=5, s=80,
                label="Velocidad = 0 (máx/mín de posición)")
ax2.set_ylabel("Velocidad  v(t)  [m/s]", fontsize=11)
ax2.set_title("Velocidad  —  Primera derivada de s(t)", fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=9, loc="best")

# ── Gráfico 3: Aceleración ──
ax3 = axes[2]
ax3.plot(t, a, color=colores["acel"], linewidth=2.5, label=f"$a(t) = {a_tex}$")
ax3.axhline(0, color="black", linewidth=0.8, linestyle="--")
if t_inflexion:
    ax3.scatter(t_inflexion, [0] * len(t_inflexion), color="purple",
                zorder=5, s=80, label="Punto(s) de inflexión (a=0)")
ax3.fill_between(t, a, 0, where=(a >= 0), alpha=0.10, color="green")
ax3.fill_between(t, a, 0, where=(a < 0), alpha=0.10, color="red")
ax3.set_ylabel("Aceleración  a(t)  [m/s²]", fontsize=11)
ax3.set_xlabel("Tiempo  t  [s]", fontsize=11)
ax3.set_title("Aceleración  —  Segunda derivada de s(t)", fontsize=11)
ax3.grid(True, alpha=0.3)
ax3.legend(fontsize=9, loc="best")

plt.tight_layout(rect=[0, 0, 1, 0.97])
ruta_png = os.path.join(DIRECTORIO, "graficos_modelo.png")
plt.savefig(ruta_png, dpi=150, bbox_inches="tight")
print(f"✅ Gráfico guardado en: {ruta_png}")

# ─────────────────────────────────────────────
# 4. TABLA DE VALORES EN CONSOLA
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print(f"{'t':>5} | {'s(t)':>8} | {'v(t)':>8} | {'a(t)':>8} | Estado")
print("-" * 55)
paso = T_MAX / 10 if T_MAX else 0.5
for ti in np.arange(0, T_MAX + paso / 2, paso):
    si = float(posicion(ti))
    vi = float(velocidad(ti))
    ai = float(aceleracion(ti))
    if vi > 1e-9:
        estado = "→ Avanzando"
    elif vi < -1e-9:
        estado = "← Retrocede"
    else:
        estado = "⏸ Parado"
    print(f"{ti:>5.1f} | {si:>8.3f} | {vi:>8.3f} | {ai:>8.3f} | {estado}")

plt.close(fig)

# ─────────────────────────────────────────────
# 5. ABRIR LA IMAGEN CON EL VISOR DEL SISTEMA
# ─────────────────────────────────────────────
# Se evita plt.show() a propósito: usa una ventana Tk que en algunas
# instalaciones de Windows está rota. Abrir el PNG es 100 % fiable.
def abrir_imagen(ruta):
    try:
        if sys.platform.startswith("win"):
            os.startfile(ruta)                                  # Windows
        elif sys.platform == "darwin":
            subprocess.run(["open", ruta], check=False)          # macOS
        else:
            subprocess.run(["xdg-open", ruta], check=False)      # Linux
    except Exception as e:
        print(f"  (No se pudo abrir la imagen automáticamente: {e})")
        print(f"  Ábrela manualmente en: {ruta}")


abrir_imagen(ruta_png)
