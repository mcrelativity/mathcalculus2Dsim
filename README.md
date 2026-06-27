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

### Versión 3D (vectorial)

La opción 3D extiende el mismo concepto a una posición **vectorial**
`r(t) = (x(t), y(t), z(t))`. La velocidad y la aceleración siguen siendo la
primera y la segunda derivada, pero ahora se derivan las **tres componentes**:

```
r(t) = ( x(t),  y(t),  z(t)  )
v(t) = r'(t)  = ( x'(t),  y'(t),  z'(t)  )   → vector velocidad
a(t) = r''(t) = ( x''(t), y''(t), z''(t) )   → vector aceleración
```

---

## 🗂️ Estructura del Proyecto

```
modelo_diferencial/
│
├── main.py                 ← Archivo principal (ejecutar este)
├── modelo.py               ← Núcleo matemático compartido (2D y 3D)
├── graficos.py             ← Gráficos con Matplotlib (2D)
├── simulacion_pygame.py    ← Objeto sobre una línea (Pygame, 2D)
├── simulacion_cohete.py    ← Cohete recorriendo la curva s(t) (Pygame, 2D)
├── simulacion_3d.py        ← Cohete recorriendo r(t)=(x,y,z) (Pygame, 3D)
├── unity/                  ← Versión 3D para Unity (scripts C# + guía)
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
[1]  Gráficos matemáticos          (Matplotlib, 2D)
[2]  Simulación objeto en línea     (Pygame, 2D)
[3]  Cohete en plano cartesiano     (Pygame, 2D)
[4]  Cohete en 3D — r(t)=(x,y,z)    (Pygame)
[5]  Todo junto 2D (misma función s(t))
[0]  Salir
```

Las opciones 2D piden una función escalar `s(t)`; la opción 3D pide las tres
componentes `x(t)`, `y(t)`, `z(t)` (o eliges una curva de ejemplo).
Cada script también puede ejecutarse por separado; en ese caso pedirá la
función directamente.

---

## 🎮 Controles de las Simulaciones (Pygame)

| Tecla / Acción | Efecto |
|----------------|--------|
| `SPACE` | Pausar / Reanudar |
| `R` | Reiniciar desde t = 0 |
| `↑` / `↓` | Más / menos velocidad de simulación |
| Arrastrar mouse | Rotar la cámara *(solo 3D)* |
| Rueda del mouse | Acercar / alejar *(solo 3D)* |
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

### Cohete en 3D (Pygame)
- Recorre una curva **vectorial** `r(t) = (x(t), y(t), z(t))` en un espacio 3D
  (motor de proyección propio: rotación + perspectiva, sin librerías extra).
- Dibuja la trayectoria completa, los ejes X/Y/Z y una rejilla de suelo.
- Muestra los **vectores velocidad** (verde, tangente a la curva) y
  **aceleración** (naranja) saliendo del cohete.
- HUD con `t`, `r(t)`, `v(t)`, `a(t)` y sus magnitudes `|v|`, `|a|`.
- Cámara orbital con el mouse y zoom con la rueda.

---

## 🔗 Fuentes utilizadas

1. Stewart, J. (2012). *Cálculo: Trascendentes tempranas* (7a ed.). Cengage Learning.
2. Documentación SymPy (cálculo simbólico): https://docs.sympy.org/latest/index.html
3. Documentación Matplotlib: https://matplotlib.org/stable/api/pyplot_summary.html
4. Documentación Pygame: https://www.pygame.org/docs/
