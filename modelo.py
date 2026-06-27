"""
PROYECTO ABPro - Cálculo Diferencial
════════════════════════════════════════════════════════
modelo.py — Núcleo matemático compartido

Este módulo centraliza TODO lo relacionado con el modelo:
  · la lista de funciones de ejemplo
  · el cálculo simbólico de las derivadas (v = s', a = s'')
  · la creación de funciones numéricas evaluables
  · la búsqueda de puntos críticos e inflexión
  · el menú de selección de función

Antes, esta lógica estaba copiada (y a veces distinta) en main.py,
graficos.py y simulacion_cohete.py. Centralizarla evita inconsistencias
y hace que la MISMA función elegida se use en todas las visualizaciones.

Integrantes: Shaira Camacho, Emiliano Gómez, Gabriel Paredes, Vicente Schute
Docente:     Fernando Gaitero
Asignatura:  Cálculo Diferencial — INACAP
"""

import numpy as np
import sympy as sp

# Símbolo de tiempo usado en todo el proyecto
t_sym = sp.Symbol("t", real=True)

# ── Funciones de ejemplo ────────────────────────────
# Se escriben con sintaxis sympy (sin, cos, exp, sqrt...).
EJEMPLOS = [
    ("t**3 - 6*t**2 + 9*t",   "Polinómica cúbica  (la del proyecto)"),
    ("t**2 - 4*t + 3",         "Polinómica cuadrática"),
    ("sin(t)",                  "Sinusoidal"),
    ("exp(-t) * sin(t)",        "Exponencial amortiguada"),
    ("2*t**3 - 3*t**2",        "Otra polinómica"),
]

# Entorno seguro para interpretar la función del usuario.
# Solo se exponen el símbolo t y funciones matemáticas conocidas.
_ENTORNO_SEGURO = {
    "t": t_sym, "sp": sp,
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "exp": sp.exp, "log": sp.log, "ln": sp.log,
    "sqrt": sp.sqrt, "Abs": sp.Abs, "abs": sp.Abs,
    "pi": sp.pi, "E": sp.E,
}


# ─────────────────────────────────────────────────────
# Conversión expresión → modelo evaluable
# ─────────────────────────────────────────────────────
def _make_callable(expr):
    """
    Convierte una expresión sympy en una función numérica robusta.

    Funciona tanto si se le pasa un escalar como un array de numpy y,
    si la expresión es constante (sin t), devuelve un resultado con la
    misma forma que la entrada en lugar de un único número.
    """
    f = sp.lambdify(t_sym, expr, modules=["numpy"])

    def g(tt):
        out = f(tt)
        arr = np.asarray(out, dtype=float)
        if arr.shape != np.shape(tt):          # caso constante → difundir
            arr = np.broadcast_to(arr, np.shape(tt)).astype(float)
        return arr if np.ndim(tt) else float(arr)

    return g


def parsear_expresion(expr_str):
    """Interpreta el texto del usuario y devuelve una expresión sympy.

    Acepta tanto la sintaxis del proyecto (`sp.sin(t)`) como la sencilla
    (`sin(t)`). Lanza una excepción si la entrada no es válida.
    """
    expr = eval(expr_str, {"__builtins__": {}}, _ENTORNO_SEGURO)
    return sp.sympify(expr)


def construir_modelo(expr_str, t_max=5.0):
    """
    A partir del texto de s(t) construye el contexto completo del modelo:
    derivadas simbólicas, funciones numéricas y cadenas legibles.

    Devuelve un diccionario listo para inyectarse como contexto en
    graficos.py / simulacion_pygame.py / simulacion_cohete.py.
    """
    s_sym = parsear_expresion(expr_str)
    v_sym = sp.diff(s_sym, t_sym)            # primera derivada  → velocidad
    a_sym = sp.diff(v_sym, t_sym)            # segunda derivada  → aceleración

    return {
        "_s_sym":    s_sym,
        "_v_sym":    v_sym,
        "_a_sym":    a_sym,
        "_s_func":   _make_callable(s_sym),
        "_v_func":   _make_callable(v_sym),
        "_a_func":   _make_callable(a_sym),
        "_expr_str": str(s_sym),
        "_v_str":    str(v_sym),
        "_a_str":    str(a_sym),
        "_s_latex":  sp.latex(s_sym),
        "_v_latex":  sp.latex(v_sym),
        "_a_latex":  sp.latex(a_sym),
        "_T_MAX":    float(t_max),
    }


# ─────────────────────────────────────────────────────
# Puntos notables (genéricos, para cualquier función)
# ─────────────────────────────────────────────────────
def _raices_por_cambio_signo(t_arr, y_arr):
    """Devuelve los t donde y(t) cruza el cero, por interpolación lineal.

    Es un método numérico que funciona para CUALQUIER función (polinómica,
    trigonométrica, etc.), a diferencia de resolver simbólicamente que puede
    fallar con funciones trascendentes.
    """
    y_arr = np.asarray(y_arr, dtype=float)
    finitos = y_arr[np.isfinite(y_arr)]
    # Si la función es (casi) idénticamente nula, no hay raíces aisladas.
    if finitos.size == 0 or np.max(np.abs(finitos)) < 1e-9:
        return []

    raices = []
    n = len(t_arr)
    for i in range(1, n):
        y0, y1 = y_arr[i - 1], y_arr[i]
        if not (np.isfinite(y0) and np.isfinite(y1)):
            continue
        if y0 * y1 < 0:                       # cambio de signo entre nodos
            tr = t_arr[i - 1] + (t_arr[i] - t_arr[i - 1]) * (-y0) / (y1 - y0)
            raices.append(float(tr))
        elif y0 == 0.0 and 0 < i - 1:         # cero exacto en un nodo interior
            y_prev = y_arr[i - 2]
            if np.isfinite(y_prev) and y_prev * y1 < 0:   # cruce genuino
                raices.append(float(t_arr[i - 1]))
    # Eliminar duplicados muy cercanos
    raices_limpias = []
    for r in raices:
        if not any(abs(r - x) < 1e-6 for x in raices_limpias):
            raices_limpias.append(round(r, 4))
    return raices_limpias


def puntos_criticos(ctx, n=2000):
    """t donde v(t) = 0  →  máximos/mínimos de la posición."""
    t_arr = np.linspace(0, ctx["_T_MAX"], n)
    v_arr = np.asarray(ctx["_v_func"](t_arr), dtype=float)
    return _raices_por_cambio_signo(t_arr, v_arr)


def puntos_inflexion(ctx, n=2000):
    """t donde a(t) = 0  →  puntos de inflexión de la posición."""
    t_arr = np.linspace(0, ctx["_T_MAX"], n)
    a_arr = np.asarray(ctx["_a_func"](t_arr), dtype=float)
    return _raices_por_cambio_signo(t_arr, a_arr)


# ─────────────────────────────────────────────────────
# Selección interactiva (cuando un script se ejecuta solo)
# ─────────────────────────────────────────────────────
def pedir_modelo_interactivo(titulo="Selecciona la función de posición s(t)"):
    """Muestra el menú de funciones y el rango de tiempo, y devuelve el contexto.

    Lo usan los scripts cuando se ejecutan de forma independiente (sin main.py).
    """
    print("\n" + "═" * 60)
    print(f"  {titulo}")
    print("═" * 60)
    for i, (expr, desc) in enumerate(EJEMPLOS, 1):
        print(f"  [{i}] s(t) = {expr:<24} ({desc})")
    print("  [0] Escribir una función propia")
    print("─" * 60)
    print("  Funciones disponibles: sin(t)  cos(t)  exp(t)  sqrt(t)  log(t)")
    print("─" * 60)

    n_ej = len(EJEMPLOS)
    while True:
        op = input(f"  Elige [0-{n_ej}]: ").strip()
        if op in [str(i) for i in range(1, n_ej + 1)]:
            expr_str = EJEMPLOS[int(op) - 1][0]
        elif op == "0":
            expr_str = input("  Escribe s(t) = ").strip()
        else:
            print("  ⚠️  Opción no válida.")
            continue
        try:
            s_sym = parsear_expresion(expr_str)
            break
        except Exception as e:
            print(f"  ❌ Error: {e}. Intenta de nuevo.")

    while True:
        try:
            raw = input("  Rango de tiempo [0 a ?] (Enter = 5): ").strip()
            t_max = float(raw) if raw else 5.0
            if t_max > 0:
                break
            print("  ⚠️  Debe ser mayor a 0.")
        except ValueError:
            print("  ⚠️  Número inválido.")

    ctx = construir_modelo(str(s_sym), t_max)

    print("\n" + "─" * 60)
    print(f"  s(t) = {ctx['_expr_str']}")
    print(f"  v(t) = {ctx['_v_str']}   ← primera derivada")
    print(f"  a(t) = {ctx['_a_str']}   ← segunda derivada")
    print("─" * 60)
    return ctx


def obtener_contexto(espacio_global, titulo="Función de posición s(t)"):
    """Devuelve el contexto del modelo.

    Si el script fue lanzado desde main.py, el contexto ya está inyectado
    en las variables globales (se reutiliza). Si se ejecuta de forma
    independiente, se pide la función al usuario.
    """
    if "_s_func" in espacio_global and "_T_MAX" in espacio_global:
        return {
            k: espacio_global[k]
            for k in (
                "_s_sym", "_v_sym", "_a_sym",
                "_s_func", "_v_func", "_a_func",
                "_expr_str", "_v_str", "_a_str",
                "_s_latex", "_v_latex", "_a_latex", "_T_MAX",
            )
            if k in espacio_global
        }
    return pedir_modelo_interactivo(titulo)
