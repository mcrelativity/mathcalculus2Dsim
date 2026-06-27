"""
PROYECTO ABPro - Cálculo Diferencial
════════════════════════════════════════════════════════
Diseño y validación de un modelo diferencial para el
movimiento de objetos en entornos interactivos 2D y 3D

Integrantes: Shaira Camacho, Emiliano Gómez,
             Gabriel Paredes, Vicente Schute
Docente:     Fernando Gaitero
Asignatura:  Cálculo Diferencial — INACAP
════════════════════════════════════════════════════════
"""

import sys
import os

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
# Asegura que los módulos del proyecto se puedan importar aunque main.py
# se ejecute desde otra carpeta.
if DIRECTORIO not in sys.path:
    sys.path.insert(0, DIRECTORIO)


# ── Verificar dependencias ──────────────────────────
# Se hace ANTES de importar numpy/sympy. (En la versión anterior numpy y
# sympy se importaban arriba del todo, así que si faltaban el programa
# reventaba antes de llegar a este aviso amistoso.)
def verificar():
    import importlib.util
    faltantes = [
        lib for lib in ("numpy", "sympy", "matplotlib", "pygame")
        if importlib.util.find_spec(lib) is None
    ]
    if faltantes:
        print("\n⚠️  Faltan librerías:")
        for lib in faltantes:
            print(f"   → {lib}")
        print(f"\n   Instálalas con:\n   pip install {' '.join(faltantes)}\n")
        sys.exit(1)


verificar()

import modelo  # noqa: E402  (se importa tras verificar dependencias)


# ── Selección de función ────────────────────────────
def pedir_funcion():
    return modelo.pedir_modelo_interactivo(
        "Selecciona la función de posición s(t)"
    )


# ── Menú principal ──────────────────────────────────
def menu():
    print("\n" + "═" * 60)
    print("  MODELO DIFERENCIAL — ABPro Cálculo Diferencial")
    print("═" * 60)
    print("  [1]  Gráficos matemáticos          (Matplotlib, 2D)")
    print("  [2]  Simulación objeto en línea     (Pygame, 2D)")
    print("  [3]  Cohete en plano cartesiano     (Pygame, 2D)")
    print("  [4]  Cohete en 3D — r(t)=(x,y,z)    (Pygame)")
    print("  [5]  Todo junto 2D (misma función s(t))")
    print("  [0]  Salir")
    print("─" * 60)
    while True:
        op = input("  Elige una opción: ").strip()
        if op in ("0", "1", "2", "3", "4", "5"):
            return op
        print("  ⚠️  Opción no válida.")


# ── Ejecutor ────────────────────────────────────────
def ejecutar(archivo, contexto):
    """Ejecuta un script del proyecto inyectándole el contexto del modelo.

    Captura SystemExit para que el `sys.exit()` final de un script (al
    cerrar su ventana) NO termine todo el programa. Gracias a esto, la
    opción «Todo junto» encadena correctamente los tres scripts.
    """
    ruta = os.path.join(DIRECTORIO, archivo)
    ctx = {"__name__": "__main__", "__file__": ruta}
    ctx.update(contexto)
    try:
        with open(ruta, encoding="utf-8") as f:
            exec(compile(f.read(), ruta, "exec"), ctx)
    except SystemExit:
        pass  # el script pidió salir; volvemos al flujo de main.py


# ── Main ────────────────────────────────────────────
if __name__ == "__main__":
    opcion = menu()

    if opcion == "0":
        print("\n  Hasta luego.\n")
        sys.exit(0)

    # La opción 3D usa una curva vectorial r(t)=(x,y,z); el resto usa s(t).
    if opcion == "4":
        ctx3d = modelo.pedir_modelo_3d_interactivo(
            "Selecciona la curva r(t) = (x(t), y(t), z(t))")
        ejecutar("simulacion_3d.py", ctx3d)
        sys.exit(0)

    ctx = pedir_funcion()

    if opcion == "1":
        ejecutar("graficos.py", ctx)
    elif opcion == "2":
        ejecutar("simulacion_pygame.py", ctx)
    elif opcion == "3":
        ejecutar("simulacion_cohete.py", ctx)
    elif opcion == "5":
        ejecutar("graficos.py", ctx)
        ejecutar("simulacion_pygame.py", ctx)
        ejecutar("simulacion_cohete.py", ctx)
