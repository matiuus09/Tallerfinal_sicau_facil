"""Imágenes del documento corto de SICAU Fácil."""
import os
import subprocess

from PIL import Image, ImageChops

import base_imagenes as B
from base_imagenes import Flujo, BASE, IMG

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PAGINA = os.path.join(BASE, "pagina")


def diagrama_general():
    f = Flujo((-1.3, 14.2), (-12.6, 0.7), escala=0.6)
    f.nodo("ini", "oval", 6, 0, "INICIO", w=2.2, h=0.8)
    f.nodo("datos", "process", 6, -1.5, "Cargar vectores de botones,\ntalleres y cursos", w=4.4)
    f.nodo("op", "process", 6, -3.0, "opcion ← -1", w=3.0, h=0.8)
    f.nodo("d1", "decision", 6, -4.6, "¿opcion ≠ 0?", w=3.4, h=1.4)
    f.nodo("fin", "oval", 11, -4.6, "FIN", w=2.0, h=0.8)
    f.nodo("menu", "io", 6, -6.2, "Mostrar menú\nopcion ← LeerOpcion(0, 3)", w=4.4)
    f.nodo("seg", "decision", 6, -7.9, "Según\nopcion", w=3.0, h=1.4)
    ramas = [("sub", "1\nGenerarPagina()"), ("io", "2\nMostrar\ntalleres"),
             ("io", "3\nMostrar cursos\ny SumarCupos()"), ("io", "0\n\"Hasta\npronto\"")]
    xs = [1.0, 4.4, 7.8, 11.2]
    for k, (tipo, t) in enumerate(ramas):
        f.nodo(f"r{k}", tipo, xs[k], -10.2, t, w=2.9, h=1.4, fs=8.5)
    f.linea([f.bot("ini"), f.top("datos")])
    f.linea([f.bot("datos"), f.top("op")])
    f.linea([f.bot("op"), f.top("d1")])
    f.linea([f.der("d1"), f.izq("fin")], etiqueta="No", pos_et=(7.9, -4.4))
    f.linea([f.bot("d1"), f.top("menu")], etiqueta="Sí", pos_et=(6.2, -5.55))
    f.linea([f.bot("menu"), f.top("seg")])
    f.linea([f.bot("seg"), (6, -9.1)], flecha=False)
    f.linea([(xs[0], -9.1), (xs[-1], -9.1)], flecha=False)
    for k, x in enumerate(xs):
        f.linea([(x, -9.1), f.top(f"r{k}")])
        f.linea([f.bot(f"r{k}"), (x, -11.5)], flecha=False)
    f.linea([(xs[0], -11.5), (xs[-1], -11.5)], flecha=False)
    f.linea([(6, -11.5), (6, -12.1), (-0.9, -12.1), (-0.9, -4.6), f.izq("d1")])
    return f.guardar("flujo_general.png")


def captura_web(pagina):
    ruta = os.path.join(IMG, f"web_{pagina}.png")
    url = "file:///" + os.path.join(PAGINA, f"{pagina}.html").replace("\\", "/").replace(" ", "%20")
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1300,1000",
                    f"--screenshot={ruta}", url], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    img = Image.open(ruta).convert("RGB")
    caja = ImageChops.difference(img, Image.new("RGB", img.size, (255, 255, 255))).getbbox()
    if caja:
        img = img.crop((0, 0, img.width, min(img.height, caja[3] + 20)))
    B.ventana(img, f"{pagina}.html — página generada por C#", oscuro=False).save(ruta)
    return ruta


def generar_todo():
    r = {"flujo_general": diagrama_general()}
    cods = [
        ("cod_datos", B.extraer_rango("Program.cs", "// ------------------------- DATOS", "int[] cursoCupos")),
        ("cod_menu", B.extraer_rango("Program.cs", "// ------------------------------ MENÚ", "// ================================ FUNCIONES")),
        ("cod_leer", B.extraer_metodo("Program.cs", "int LeerOpcion(")),
        ("cod_sumar", B.extraer_metodo("Program.cs", "int SumarCupos(")),
        ("cod_generar", B.extraer_metodo("Program.cs", "void GenerarPagina()")),
    ]
    for nombre, (texto, linea) in cods:
        if nombre == "cod_menu":
            texto = "\n".join(texto.split("\n")[:-1]).rstrip()
        r[nombre] = B.captura_codigo(nombre + ".png", "Program.cs", texto, linea)

    c1 = B.leer_salida("caso1_normal")
    c2 = B.leer_salida("caso2_limite")
    c3 = B.leer_salida("caso3_errores")
    s, _ = B.segmento(c1, "=====", "Total de cupos"); r["con_normal"] = B.captura_consola("con_normal.png", s)
    s, _ = B.segmento(c2, "Opción: 4", "Hasta pronto"); r["con_limite"] = B.captura_consola("con_limite.png", s)
    s, _ = B.segmento(c3, "Opción: ", "Hasta pronto"); r["con_errores"] = B.captura_consola("con_errores.png", s)

    for p in ("index", "talleres", "bienestar"):
        r[f"web_{p}"] = captura_web(p)
    return r
