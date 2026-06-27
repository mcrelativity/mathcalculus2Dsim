# Modelo Diferencial de Movimiento 2D
### ABPro — Cálculo Diferencial | INACAP

**Integrantes:** Shaira Camacho · Emiliano Gómez · Gabriel Paredes · Vicente Schute
**Docente:** Fernando Gaitero
**Carrera:** Ingeniería Informática

---

## 📐 Modelo Matemático

A partir de una función de posición `s(t)`, el programa calcula sus derivadas
con cálculo simbólico (sympy):

| Función | Expresión (por defecto) | Descripción |
|---------|-------------------------|-------------|
| Posición | `s(t) = t³ - 6t² + 9t` | Dónde está el objeto en el tiempo t |
| Velocidad | `v(t) = s'(t) = 3t² - 12t + 9` | Primera derivada — velocidad instantánea |
| Aceleración | `a(t) = s''(t) = 6t - 12` | Segunda derivada — aceleración instantánea |

Para la función por defecto:

- **Puntos críticos** (v = 0): `t = 1` y `t = 3`
- **Punto de inflexión** (a = 0): `t = 2`

> Estos puntos ya **no están fijos en el código**: se calculan automáticamente
> para cualquier función que elijas (polinómica, sinusoidal, exponencial, etc.).

---

## 🗂️ Estructura del Proyecto

```
modelo_diferencial/
│
├── main.py                 ← Archivo principal (ejecutar este)
├── modelo.py               ← Núcleo matemático compartido (derivadas, puntos críticos)
├── graficos.py             ← Gráficos con Matplotlib
├── simulacion_pygame.py    ← Simulación de un objeto sobre una línea (Pygame)
├── simulacion_cohete.py    ← Cohete recorriendo la curva en el plano (Pygame)
└── README.md               ← Este archivo
```

La función que eliges en el menú se usa **igual en las tres visualizaciones**,
gracias al módulo compartido `modelo.py`.

---

## ⚙️ Requisitos

- Python 3.8 o superior
- Librerías:

```bash
pip install numpy sympy matplotlib pygame
```

(Si falta alguna, `main.py` lo avisa y te indica el comando exacto a ejecutar.)

---

## ▶️ Cómo ejecutar

### Opción 1 — Desde VSCode
1. Abre la carpeta `modelo_diferencial` en VSCode
2. Abre el archivo `main.py`
3. Presiona `F5` o el botón ▶️ Run

### Opción 2 — Desde terminal
```bash
cd modelo_diferencial
python main.py
```

Luego elige una opción del menú:
```
[1]  Gráficos matemáticos         (Matplotlib)
[2]  Simulación objeto en línea    (Pygame)
[3]  Cohete en plano cartesiano    (Pygame)
[4]  Todo junto (misma función)
[0]  Salir
```

Y a continuación selecciona la función `s(t)` (o escribe la tuya con `0`).
Cada script también puede ejecutarse por separado; en ese caso pedirá la
función directamente.

---

## 🎮 Controles de las Simulaciones (Pygame)

| Tecla | Acción |
|-------|--------|
| `SPACE` | Pausar / Reanudar |
| `R` | Reiniciar desde t = 0 |
| `↑` / `↓` | Más / menos velocidad de simulación *(solo cohete)* |
| `ESC` | Salir |

---

## 📊 Qué muestra cada parte

### Gráficos (Matplotlib)
- **Posición:** curva de `s(t)`, marcando dónde el objeto se detiene (v = 0).
- **Velocidad:** `v(t)`, en verde cuando avanza y rojo cuando retrocede.
- **Aceleración:** `a(t)`, con el/los punto(s) de inflexión donde cambia el comportamiento.
- Tabla de valores en consola.

> El gráfico se guarda como `graficos_modelo.png` y se abre automáticamente con
> el visor de imágenes del sistema. (No se usa la ventana interactiva de
> Matplotlib porque depende de Tcl/Tk, que en algunas instalaciones de Python
> en Windows viene roto y provoca el error `Can't find a usable init.tcl`.)

### Simulación en línea (Pygame)
- Círculo que se mueve según `s(t)` en tiempo real (verde = avanza, rojo = retrocede, amarillo = casi detenido).
- Panel con `t`, `s(t)`, `v(t)` y `a(t)` actualizados por frame.
- Flecha de dirección, barras de magnitud, rastro y barra de progreso.

### Cohete en el plano (Pygame)
- Cohete que vuela por la curva `s(t)` (eje X = tiempo, eje Y = posición).
- La **nariz del cohete sigue la pendiente real de la curva en pantalla**.
- HUD de vuelo con valores en tiempo real, barras y estado (ascendiendo / descendiendo, acelerando / frenando).

---

## 🔗 Fuentes utilizadas

1. Stewart, J. (2012). *Cálculo: Trascendentes tempranas* (7a ed.). Cengage Learning.
2. Documentación SymPy (cálculo simbólico): https://docs.sympy.org/latest/index.html
3. Documentación Matplotlib: https://matplotlib.org/stable/api/pyplot_summary.html
4. Documentación Pygame: https://www.pygame.org/docs/
