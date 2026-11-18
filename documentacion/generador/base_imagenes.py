"""Genera las imágenes del documento: diagramas de flujo, capturas de código
y capturas de la consola (a partir de las salidas reales de las pruebas)."""
import os
import re
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle
from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.lexers import CSharpLexer
from pygments.formatters import ImageFormatter

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CODIGO = os.path.join(BASE, "codigo", "SicauFacil")
PRUEBAS = os.path.join(BASE, "pruebas")
IMG = os.path.join(BASE, "documentacion", "imagenes")
os.makedirs(IMG, exist_ok=True)

# ---------------------------------------------------------------------------
#  DIAGRAMAS DE FLUJO
# ---------------------------------------------------------------------------
COL = {
    "oval": "#C8E6C9", "process": "#E3F2FD", "io": "#FFF3E0",
    "decision": "#FFF9C4", "sub": "#EDE7F6", "error": "#FFEBEE",
}


class Flujo:
    def __init__(self, xlim, ylim, escala=0.62):
        w = (xlim[1] - xlim[0]) * escala
        h = (ylim[1] - ylim[0]) * escala
        self.fig, self.ax = plt.subplots(figsize=(w, h))
        self.ax.set_xlim(*xlim)
        self.ax.set_ylim(*ylim)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.n = {}

    def nodo(self, id_, tipo, x, y, texto, w=3.4, h=0.9, fs=9):
        ax = self.ax
        color = COL["error"] if tipo == "error" else COL.get(tipo, "#FFFFFF")
        kw = dict(facecolor=color, edgecolor="#37474F", lw=1.3, zorder=2)
        if tipo == "oval":
            ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                        boxstyle=f"round,pad=0,rounding_size={h / 2}", **kw))
        elif tipo in ("process", "error"):
            ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, **kw))
        elif tipo == "sub":
            ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, **kw))
            for dx in (0.18, w - 0.18):
                ax.plot([x - w / 2 + dx] * 2, [y - h / 2, y + h / 2], color="#37474F", lw=1.1, zorder=3)
        elif tipo == "io":
            s = 0.3
            ax.add_patch(Polygon([(x - w / 2 + s, y + h / 2), (x + w / 2 + s, y + h / 2),
                                  (x + w / 2 - s, y - h / 2), (x - w / 2 - s, y - h / 2)], closed=True, **kw))
        elif tipo == "decision":
            ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)], closed=True, **kw))
        ax.text(x, y, texto, ha="center", va="center", fontsize=fs, zorder=4, family="DejaVu Sans")
        self.n[id_] = (x, y, w, h)

    def top(self, i): x, y, w, h = self.n[i]; return (x, y + h / 2)
    def bot(self, i): x, y, w, h = self.n[i]; return (x, y - h / 2)
    def izq(self, i): x, y, w, h = self.n[i]; return (x - w / 2, y)
    def der(self, i): x, y, w, h = self.n[i]; return (x + w / 2, y)

    def linea(self, puntos, flecha=True, etiqueta=None, pos_et=None):
        xs = [p[0] for p in puntos]
        ys = [p[1] for p in puntos]
        if flecha:
            self.ax.plot(xs[:-1], ys[:-1], color="#37474F", lw=1.3, zorder=1)
            self.ax.annotate("", xy=puntos[-1], xytext=puntos[-2],
                             arrowprops=dict(arrowstyle="-|>", color="#37474F", lw=1.3, mutation_scale=13), zorder=1)
        else:
            self.ax.plot(xs, ys, color="#37474F", lw=1.3, zorder=1)
        if etiqueta:
            px, py = pos_et if pos_et else puntos[0]
            self.ax.text(px, py, etiqueta, fontsize=8.5, fontweight="bold", color="#B71C1C", zorder=5)

    def guardar(self, nombre, titulo=None):
        if titulo:
            self.ax.set_title(titulo, fontsize=11, fontweight="bold", color="#263238")
        ruta = os.path.join(IMG, nombre)
        self.fig.savefig(ruta, dpi=170, bbox_inches="tight", facecolor="white")
        plt.close(self.fig)
        return ruta


def diagrama_general():
    f = Flujo((-1.3, 18.3), (-17.6, 0.7), escala=0.55)
    f.nodo("ini", "oval", 9, 0, "INICIO", w=2.2, h=0.8)
    f.nodo("carga", "sub", 9, -1.5, "Configurar consola\nCargarDatosIniciales()", w=4.0)
    f.nodo("op", "process", 9, -3.0, "opcion ← -1", w=3.0, h=0.8)
    f.nodo("d1", "decision", 9, -4.6, "¿opcion ≠ 0?", w=3.4, h=1.4)
    f.nodo("fin", "oval", 14, -4.6, "FIN", w=2.0, h=0.8)
    f.nodo("menu", "sub", 9, -6.2, "MostrarMenu()", w=3.4, h=0.8)
    f.nodo("leer", "io", 9, -7.7, "Leer opcion\nLeerEntero(\"…\", 0, 8)", w=3.8)
    f.nodo("seg", "decision", 9, -9.4, "Según\nopcion", w=3.0, h=1.4)
    ramas = ["1\nListar\ntalleres", "2\nVer\ndetalle", "3\nBuscar\ncomuna", "4\nBuscar tipo\ny especial.",
             "5\nRegistrar\ntaller", "6\nCalificar\ntaller", "7\nRanking", "8\nEstadísticas", "0\nMensaje\ndespedida"]
    for k, t in enumerate(ramas):
        f.nodo(f"r{k}", "sub" if k < 8 else "io", 1 + 2 * k, -11.8, t, w=1.85, h=1.35, fs=7.6)
    f.nodo("d3", "decision", 9, -14.4, "¿opcion ≠ 0?", w=3.4, h=1.2)
    f.nodo("pausa", "sub", 9, -16.0, "Pausar()", w=2.6, h=0.8)

    f.linea([f.bot("ini"), f.top("carga")])
    f.linea([f.bot("carga"), f.top("op")])
    f.linea([f.bot("op"), f.top("d1")])
    f.linea([f.der("d1"), f.izq("fin")], etiqueta="No", pos_et=(10.9, -4.4))
    f.linea([f.bot("d1"), f.top("menu")], etiqueta="Sí", pos_et=(9.2, -5.6))
    f.linea([f.bot("menu"), f.top("leer")])
    f.linea([f.bot("leer"), f.top("seg")])
    f.linea([f.bot("seg"), (9, -10.7)], flecha=False)
    f.linea([(1, -10.7), (17, -10.7)], flecha=False)
    for k in range(9):
        x = 1 + 2 * k
        f.linea([(x, -10.7), f.top(f"r{k}")])
        f.linea([f.bot(f"r{k}"), (x, -13.1)], flecha=False)
    f.linea([(1, -13.1), (17, -13.1)], flecha=False)
    f.linea([(9, -13.1), f.top("d3")])
    f.linea([f.bot("d3"), f.top("pausa")], etiqueta="Sí", pos_et=(9.2, -15.4))
    f.linea([f.der("d3"), (11.6, -14.4), (11.6, -17.0)], flecha=False, etiqueta="No", pos_et=(10.8, -14.2))
    f.linea([f.bot("pausa"), (9, -17.0), (-0.7, -17.0), (-0.7, -4.6), f.izq("d1")], flecha=True)
    f.linea([(11.6, -17.0), (9, -17.0)], flecha=False)
    return f.guardar("flujo_general.png")


def diagrama_leer_entero():
    f = Flujo((-1.4, 13.0), (-13.2, 0.7))
    f.nodo("ini", "oval", 6, 0, "INICIO LeerEntero(mensaje, min, max)", w=5.6, h=0.8)
    f.nodo("p1", "process", 6, -1.5, "valido ← falso\nvalor ← 0", w=3.0)
    f.nodo("d1", "decision", 6, -3.1, "¿valido = falso?", w=3.4, h=1.3)
    f.nodo("io", "io", 6, -4.7, "Mostrar mensaje\nLeer entrada", w=3.2)
    f.nodo("d2", "decision", 6, -6.3, "¿entrada\nvacía?", w=3.4, h=1.3)
    f.nodo("d3", "decision", 6, -8.1, "¿Es número\nentero?", w=3.4, h=1.3)
    f.nodo("d4", "decision", 6, -9.9, "¿min ≤ valor\n≤ max?", w=3.4, h=1.3)
    f.nodo("p2", "process", 6, -11.5, "valido ← verdadero", w=3.2, h=0.8)
    f.nodo("e1", "error", 1.4, -6.3, "Error: no puede\nestar vacío", w=2.6)
    f.nodo("e2", "error", 1.4, -8.1, "Error: debe ser\nnúmero entero", w=2.6)
    f.nodo("e3", "error", 1.4, -9.9, "Error: fuera\nde rango", w=2.6)
    f.nodo("ret", "io", 10.8, -5.0, "Retornar valor", w=2.8, h=0.8)
    f.nodo("fin", "oval", 10.8, -6.6, "FIN", w=2.0, h=0.8)

    f.linea([f.bot("ini"), f.top("p1")])
    f.linea([f.bot("p1"), f.top("d1")])
    f.linea([f.bot("d1"), f.top("io")], etiqueta="Sí", pos_et=(6.2, -4.05))
    f.linea([f.der("d1"), (10.8, -3.1), f.top("ret")], etiqueta="No", pos_et=(7.9, -2.9))
    f.linea([f.bot("ret"), f.top("fin")])
    f.linea([f.bot("io"), f.top("d2")])
    f.linea([f.izq("d2"), f.der("e1")], etiqueta="Sí", pos_et=(3.4, -6.1))
    f.linea([f.bot("d2"), f.top("d3")], etiqueta="No", pos_et=(6.2, -7.25))
    f.linea([f.izq("d3"), f.der("e2")], etiqueta="No", pos_et=(3.4, -7.9))
    f.linea([f.bot("d3"), f.top("d4")], etiqueta="Sí", pos_et=(6.2, -9.05))
    f.linea([f.izq("d4"), f.der("e3")], etiqueta="No", pos_et=(3.4, -9.7))
    f.linea([f.bot("d4"), f.top("p2")], etiqueta="Sí", pos_et=(6.2, -10.85))
    for e in ("e1", "e2", "e3"):
        f.linea([f.izq(e), (-0.9, f.n[e][1])], flecha=False)
    f.linea([f.bot("p2"), (6, -12.5), (-0.9, -12.5), (-0.9, -3.1), f.izq("d1")])
    return f.guardar("flujo_leer_entero.png")


def diagrama_promedio():
    f = Flujo((-0.6, 16.4), (-8.8, 0.7))
    f.nodo("ini", "oval", 5, 0, "INICIO CalcularPromedioTaller(sumas, opiniones, indice)", w=7.4, h=0.8, fs=8.5)
    f.nodo("d1", "decision", 5, -1.7, "¿opiniones[indice]\n= 0?", w=3.9, h=1.4)
    f.nodo("r1", "io", 10.6, -1.7, "Retornar 0", w=2.4, h=0.8)
    f.nodo("p1", "process", 5, -3.6, "numCriterios ← 4\ntotal ← 0\nc ← 0", w=3.0, h=1.2)
    f.nodo("d2", "decision", 5, -5.5, "¿c <\nnumCriterios?", w=3.6, h=1.4)
    f.nodo("p2", "process", 5, -7.3, "total ← total + sumas[indice, c]\nc ← c + 1", w=4.6, h=0.9)
    f.nodo("r2", "io", 10.9, -5.5, "Retornar total /\n(opiniones[indice] × numCriterios)", w=5.0, h=1.0, fs=8.5)
    f.nodo("fin", "oval", 15.0, -3.6, "FIN", w=1.8, h=0.8)

    f.linea([f.bot("ini"), f.top("d1")])
    f.linea([f.der("d1"), f.izq("r1")], etiqueta="Sí", pos_et=(7.1, -1.5))
    f.linea([f.bot("d1"), f.top("p1")], etiqueta="No", pos_et=(5.2, -2.75))
    f.linea([f.bot("p1"), f.top("d2")])
    f.linea([f.bot("d2"), f.top("p2")], etiqueta="Sí", pos_et=(5.2, -6.55))
    f.linea([f.bot("p2"), (5, -8.2), (0.0, -8.2), (0.0, -5.5), f.izq("d2")])
    f.linea([f.der("d2"), f.izq("r2")], etiqueta="No", pos_et=(6.9, -5.3))
    f.linea([f.der("r1"), (15.0, -1.7), f.top("fin")])
    f.linea([f.der("r2"), (15.0, -5.5), f.bot("fin")])
    return f.guardar("flujo_promedio.png")


def diagrama_calificar():
    f = Flujo((0.4, 15.0), (-15.5, 0.7))
    f.nodo("ini", "oval", 6, 0, "INICIO CalificarTaller()", w=4.0, h=0.8)
    f.nodo("d1", "decision", 6, -1.6, "¿totalTalleres\n= 0?", w=3.4, h=1.3)
    f.nodo("vac", "io", 11.4, -1.6, "Mostrar \"No hay\ntalleres registrados\"", w=3.2)
    f.nodo("sel", "sub", 6, -3.2, "i ← SeleccionarTaller()", w=3.8, h=0.8)
    f.nodo("c0", "process", 6, -4.5, "c ← 0", w=2.0, h=0.7)
    f.nodo("d2", "decision", 6, -6.0, "¿c < 4?", w=2.8, h=1.2)
    f.nodo("nota", "io", 6, -7.6, "notas[c] ← LeerEntero(1, 5)\nc ← c + 1", w=4.2)
    f.nodo("com", "io", 6, -9.7, "comentario ←\nLeerTextoOpcional(80)", w=3.8)
    f.nodo("d3", "decision", 6, -11.4, "¿Confirma\n(S/N)?", w=3.2, h=1.3)
    f.nodo("ag", "sub", 6, -13.1, "AgregarOpinion(i, notas, comentario)\nMostrar nuevo promedio", w=5.0, h=0.9, fs=8.5)
    f.nodo("desc", "io", 11.4, -11.4, "Mostrar \"Opinión\ndescartada\"", w=3.0)
    f.nodo("fin", "oval", 6, -14.8, "FIN", w=2.0, h=0.8)

    f.linea([f.bot("ini"), f.top("d1")])
    f.linea([f.der("d1"), f.izq("vac")], etiqueta="Sí", pos_et=(7.8, -1.4))
    f.linea([f.bot("d1"), f.top("sel")], etiqueta="No", pos_et=(6.2, -2.55))
    f.linea([f.bot("sel"), f.top("c0")])
    f.linea([f.bot("c0"), f.top("d2")])
    f.linea([f.bot("d2"), f.top("nota")], etiqueta="Sí", pos_et=(6.2, -6.95))
    f.linea([f.bot("nota"), (6, -8.45), (1.4, -8.45), (1.4, -6.0), f.izq("d2")])
    f.linea([f.der("d2"), (9.0, -6.0), (9.0, -8.85), (6, -8.85), f.top("com")], etiqueta="No", pos_et=(7.5, -5.8))
    f.linea([f.bot("com"), f.top("d3")])
    f.linea([f.bot("d3"), f.top("ag")], etiqueta="Sí", pos_et=(6.2, -12.4))
    f.linea([f.der("d3"), f.izq("desc")], etiqueta="No", pos_et=(7.8, -11.2))
    f.linea([f.bot("ag"), f.top("fin")])
    f.linea([f.bot("desc"), (11.4, -14.8), f.der("fin")])
    f.linea([f.der("vac"), (13.9, -1.6), (13.9, -14.8), (11.4, -14.8)], flecha=False)
    return f.guardar("flujo_calificar.png")


# ---------------------------------------------------------------------------
#  CAPTURAS DE CÓDIGO
# ---------------------------------------------------------------------------
def extraer_metodo(archivo, firma):
    """Devuelve el texto del método que contiene `firma`, con sus comentarios previos."""
    with open(os.path.join(CODIGO, archivo), encoding="utf-8") as fh:
        lineas = fh.read().split("\n")
    idx = next(i for i, l in enumerate(lineas) if firma in l)
    ini = idx
    while ini > 0 and lineas[ini - 1].strip().startswith("//"):
        ini -= 1
    nivel, fin, abierto = 0, idx, False
    for j in range(idx, len(lineas)):
        nivel += lineas[j].count("{") - lineas[j].count("}")
        if "{" in lineas[j]:
            abierto = True
        if abierto and nivel == 0:
            fin = j
            break
    bloque = lineas[ini:fin + 1]
    sangria = min(len(l) - len(l.lstrip()) for l in bloque if l.strip())
    return "\n".join(l[sangria:] for l in bloque), ini + 1


def extraer_rango(archivo, desde, hasta):
    with open(os.path.join(CODIGO, archivo), encoding="utf-8") as fh:
        lineas = fh.read().split("\n")
    i = next(k for k, l in enumerate(lineas) if desde in l)
    j = next(k for k, l in enumerate(lineas) if hasta in l and k >= i)
    bloque = lineas[i:j + 1]
    sangria = min(len(l) - len(l.lstrip()) for l in bloque if l.strip())
    return "\n".join(l[sangria:] for l in bloque), i + 1


def ventana(img, titulo, oscuro=True):
    """Agrega una barra de título tipo editor/terminal a una imagen."""
    barra = 34
    fondo = (37, 37, 38) if oscuro else (225, 228, 232)
    out = Image.new("RGB", (img.width, img.height + barra), fondo)
    out.paste(img, (0, barra))
    d = ImageDraw.Draw(out)
    for k, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((12 + k * 20, 11, 24 + k * 20, 23), fill=c)
    try:
        fnt = ImageFont.truetype("segoeui.ttf", 15)
    except OSError:
        fnt = ImageFont.load_default()
    d.text((84, 7), titulo, fill=(200, 200, 200) if oscuro else (60, 60, 60), font=fnt)
    marco = Image.new("RGB", (out.width + 2, out.height + 2), (90, 90, 90))
    marco.paste(out, (1, 1))
    return marco


def captura_codigo(nombre, archivo, codigo, linea_ini):
    fmt = ImageFormatter(font_name="Consolas", font_size=17, line_numbers=True,
                         line_number_start=linea_ini, style="vs", line_number_bg="#F3F3F3",
                         line_number_fg="#8A8A8A", image_pad=14, line_pad=4)
    png = highlight(codigo, CSharpLexer(), fmt)
    img = Image.open(io.BytesIO(png)).convert("RGB")
    img = ventana(img, f"{archivo}  —  SicauFacil (C# .NET)", oscuro=False)
    ruta = os.path.join(IMG, nombre)
    img.save(ruta)
    return ruta


# ---------------------------------------------------------------------------
#  CAPTURAS DE CONSOLA (salidas reales del programa)
# ---------------------------------------------------------------------------
def leer_salida(caso):
    with open(os.path.join(PRUEBAS, f"{caso}_salida.txt"), encoding="utf-8") as fh:
        return fh.read().replace("\r", "").split("\n")


def segmento(lineas, inicio, fin, ocurrencia=1, desde=0):
    vistos, i = 0, None
    for k in range(desde, len(lineas)):
        if inicio in lineas[k]:
            vistos += 1
            if vistos == ocurrencia:
                i = k
                break
    j = next(k for k in range(i, len(lineas)) if fin in lineas[k])
    return lineas[i:j + 1], j


def captura_consola(nombre, lineas, titulo="SICAU Fácil - Consola"):
    fnt = ImageFont.truetype("consola.ttf", 17)
    fntb = ImageFont.truetype("consolab.ttf", 17)
    alto_l = 22
    ancho = max(60, max(len(l) for l in lineas)) * 9.4 + 30
    img = Image.new("RGB", (int(ancho), len(lineas) * alto_l + 24), (12, 12, 12))
    d = ImageDraw.Draw(img)
    for k, l in enumerate(lineas):
        color, f = (204, 204, 204), fnt
        if "[ERROR]" in l:
            color = (240, 80, 80)
        elif l.startswith("¡Gracias") or "registrado con el número" in l:
            color = (80, 220, 100)
        elif re.match(r"^\s*(=+|RUTATALLER|-{5,}.*-{5,})", l.strip()) or l.strip().isupper():
            color, f = (97, 214, 214), fntb
        d.text((14, 12 + k * alto_l), l, fill=color, font=f)
    img = ventana(img, titulo)
    ruta = os.path.join(IMG, nombre)
    img.save(ruta)
    return ruta


def generar_todo():
    rutas = {}
    rutas["flujo_general"] = diagrama_general()
    rutas["flujo_leer_entero"] = diagrama_leer_entero()
    rutas["flujo_promedio"] = diagrama_promedio()
    rutas["flujo_calificar"] = diagrama_calificar()

    # --- Código ---
    cods = [
        ("cod_main", "Program.cs", extraer_rango("Program.cs", "public static void Main()", "        // ========================= PROCEDIMIENTOS")),
        ("cod_datos", "Program.cs", extraer_rango("Program.cs", "// ------------------- ARREGLOS PARALELOS", "static int totalTalleres")),
        ("cod_leer_entero", "Validaciones.cs", extraer_metodo("Validaciones.cs", "public static int LeerEntero(")),
        ("cod_telefono", "Validaciones.cs", extraer_metodo("Validaciones.cs", "public static string LeerTelefono(")),
        ("cod_promedio", "Calculos.cs", extraer_metodo("Calculos.cs", "public static double CalcularPromedioTaller(")),
        ("cod_categoria", "Calculos.cs", extraer_metodo("Calculos.cs", "public static string ObtenerCategoria(")),
        ("cod_ordenar", "Calculos.cs", extraer_metodo("Calculos.cs", "public static int[] OrdenarPorPromedio(")),
        ("cod_calificar", "Program.cs", extraer_metodo("Program.cs", "static void CalificarTaller()")),
        ("cod_agregar_opinion", "Program.cs", extraer_metodo("Program.cs", "static void AgregarOpinion(")),
        ("cod_buscar_tipo", "Program.cs", extraer_metodo("Program.cs", "static void BuscarPorTipoYEspecialidad()")),
    ]
    for nombre, archivo, (texto, linea) in cods:
        # El Main incluye la línea del separador final; se quita para que se vea limpio
        if nombre == "cod_main":
            texto = "\n".join(texto.split("\n")[:-1]).rstrip()
        rutas[nombre] = captura_codigo(nombre + ".png", archivo, texto, linea)

    # --- Consola ---
    c1 = leer_salida("caso1_normal")
    c2 = leer_salida("caso2_limite")
    c3 = leer_salida("caso3_errores")

    seg, _ = segmento(c1, "=====", "Seleccione una opción: 1")
    rutas["con_menu"] = captura_consola("con_menu.png", seg)
    seg, _ = segmento(c1, "TODOS LOS TALLERES", "Latonería Don Jairo")
    rutas["con_listado"] = captura_consola("con_listado.png", seg)
    seg, _ = segmento(c1, "Número del taller (1 a 6): 1", "Buen trabajo pero")
    rutas["con_detalle"] = captura_consola("con_detalle.png", seg)
    seg, _ = segmento(c1, "¿Qué vehículo tiene?", "Se encontraron")
    rutas["con_buscar_tipo"] = captura_consola("con_buscar_tipo.png", seg)
    seg, _ = segmento(c1, "RANKING DE MEJORES", "sin opiniones no aparecen")
    rutas["con_ranking1"] = captura_consola("con_ranking1.png", seg)

    seg, _ = segmento(c2, "REGISTRAR TALLER NUEVO", "registrado con el número")
    seg = [l for l in seg if not re.match(r"^\s{3,4}\d{1,2}\. ", l)]   # sin listas largas
    rutas["con_registro"] = captura_consola("con_registro.png", seg)
    seg, _ = segmento(c2, "Calificando: Taller Prueba", "¡Gracias!")
    rutas["con_calificar_5"] = captura_consola("con_calificar_5.png", seg)
    seg, _ = segmento(c2, "Número del taller (1 a 7): 4", "Tardaron una semana")
    rutas["con_electroauto"] = captura_consola("con_electroauto.png", seg)
    seg, _ = segmento(c2, "Talleres en la comuna 2", "No hay talleres registrados en esta comuna")
    rutas["con_comuna_vacia"] = captura_consola("con_comuna_vacia.png", seg)
    seg, _ = segmento(c2, "RANKING DE MEJORES", "sin opiniones no aparecen")
    rutas["con_ranking2"] = captura_consola("con_ranking2.png", seg)
    seg, _ = segmento(c2, "ESTADÍSTICAS GENERALES", "mejor: MotoExpress")
    rutas["con_estadisticas"] = captura_consola("con_estadisticas.png", seg)

    seg, fin = segmento(c3, "Seleccione una opción: ", "Seleccione una opción: 5")
    rutas["con_err_menu"] = captura_consola("con_err_menu.png", seg)
    seg, _ = segmento(c3, "REGISTRAR TALLER NUEVO", "registrado con el número")
    seg = [l for l in seg if not re.match(r"^\s{3,4}\d{1,2}\. ", l)]
    rutas["con_err_registro"] = captura_consola("con_err_registro.png", seg)
    seg, _ = segmento(c3, "Número del taller (1 a 7): 0", "Opinión descartada")
    rutas["con_err_calificar"] = captura_consola("con_err_calificar.png", seg)
    return rutas


if __name__ == "__main__":
    for k, v in generar_todo().items():
        print(k, v)
