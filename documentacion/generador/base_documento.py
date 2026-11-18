"""Construye el documento técnico (Word) del proyecto RutaTaller Medellín y lo
exporta a PDF con Microsoft Word.

Uso:  python documento.py
"""
import os
import subprocess

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm, RGBColor

import imagenes

BASE = imagenes.BASE
SALIDA_DOCX = os.path.join(BASE, "documentacion", "Documento_Tecnico_RutaTaller.docx")
SALIDA_PDF = os.path.join(BASE, "documentacion", "Documento_Tecnico_RutaTaller.pdf")

AZUL = RGBColor(0x0D, 0x47, 0xA1)
GRIS = RGBColor(0x45, 0x5A, 0x64)

IMG = {}
doc = Document()
num_figura = [0]
num_tabla = [0]


# ---------------------------------------------------------------------------
#  Utilidades de formato
# ---------------------------------------------------------------------------
def configurar_estilos():
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.15
    for nivel, tam in ((1, 16), (2, 13), (3, 11.5)):
        h = doc.styles[f"Heading {nivel}"]
        h.font.name = "Calibri"
        h.font.size = Pt(tam)
        h.font.bold = True
        h.font.color.rgb = AZUL if nivel < 3 else GRIS
        h.element.rPr.rFonts.set(qn("w:asciiTheme"), "")
        h.paragraph_format.space_before = Pt(14 if nivel == 1 else 10)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True

    # Estilos compactos para la tabla de contenido (Word usa los ids TOC1, TOC2)
    from docx.enum.style import WD_STYLE_TYPE
    for nombre, sangria in (("TOC 1", 0), ("TOC 2", 0.5)):
        est = doc.styles.add_style(nombre, WD_STYLE_TYPE.PARAGRAPH)
        est.base_style = doc.styles["Normal"]
        est.paragraph_format.space_after = Pt(1)
        est.paragraph_format.space_before = Pt(0)
        est.paragraph_format.line_spacing = 1.0
        est.paragraph_format.left_indent = Cm(sangria)
        est.font.size = Pt(10.5)

    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(27.94), Cm(21.59)   # carta
    sec.left_margin = sec.right_margin = Cm(2.5)
    sec.top_margin = sec.bottom_margin = Cm(2.3)


def campo(parrafo, instruccion):
    """Inserta un campo de Word (PAGE, TOC, etc.)."""
    r = parrafo.add_run()
    for tipo, texto in (("begin", None), (None, instruccion), ("separate", None), (None, ""), ("end", None)):
        if tipo:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), tipo)
            r._r.append(fc)
        elif texto is not None and texto != "":
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = texto
            r._r.append(it)
    return r


def sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def p(texto="", negrita=False, cursiva=False, alinear=None, tam=None, color=None, despues=None):
    par = doc.add_paragraph()
    if texto:
        agregar_texto(par, texto, negrita, cursiva, tam, color)
    if alinear:
        par.alignment = alinear
    else:
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if despues is not None:
        par.paragraph_format.space_after = Pt(despues)
    return par


def agregar_texto(par, texto, negrita=False, cursiva=False, tam=None, color=None):
    """Permite **negrita** y `código` dentro del texto."""
    import re
    partes = re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", texto)
    for parte in partes:
        if not parte:
            continue
        if parte.startswith("**"):
            r = par.add_run(parte[2:-2]); r.bold = True
        elif parte.startswith("`"):
            r = par.add_run(parte[1:-1]); r.font.name = "Consolas"; r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(0xA3, 0x15, 0x15)
        else:
            r = par.add_run(parte); r.bold = negrita
        r.italic = cursiva or r.italic
        if tam: r.font.size = Pt(tam)
        if color: r.font.color.rgb = color
    return par


def viñetas(items, estilo="List Bullet"):
    for it in items:
        par = doc.add_paragraph(style=estilo)
        agregar_texto(par, it)
        par.paragraph_format.space_after = Pt(3)


def tabla(encabezados, filas, anchos=None, tam=9.5, titulo=None, color="0D47A1"):
    if titulo:
        num_tabla[0] += 1
        t = doc.add_paragraph()
        r = t.add_run(f"Tabla {num_tabla[0]}. "); r.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = GRIS
        r = t.add_run(titulo); r.italic = True; r.font.size = Pt(9.5); r.font.color.rgb = GRIS
        t.paragraph_format.keep_with_next = True
        t.paragraph_format.space_after = Pt(2)
    tb = doc.add_table(rows=1, cols=len(encabezados))
    tb.style = "Table Grid"
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    for k, h in enumerate(encabezados):
        c = tb.rows[0].cells[k]
        c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(tam); r.font.color.rgb = RGBColor(255, 255, 255)
        sombrear(c, color)
    # repetir encabezado en cada página
    trPr = tb.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
    for n, fila in enumerate(filas):
        cells = tb.add_row().cells
        for k, v in enumerate(fila):
            cells[k].text = ""
            par = cells[k].paragraphs[0]
            agregar_texto(par, str(v), tam=tam)
            par.paragraph_format.space_after = Pt(0)
            if n % 2 == 1:
                sombrear(cells[k], "EEF3FA")
    if anchos:
        for fila in tb.rows:
            for k, w in enumerate(anchos):
                fila.cells[k].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return tb


def figura(clave, pie, ancho=15.5):
    num_figura[0] += 1
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.keep_with_next = True
    par.add_run().add_picture(IMG[clave], width=Cm(ancho))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(f"Figura {num_figura[0]}. "); r.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = GRIS
    r = c.add_run(pie); r.italic = True; r.font.size = Pt(9.5); r.font.color.rgb = GRIS


def resaltado(par, texto, tam=13, negrita=False):
    r = par.add_run(texto)
    r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    r.font.size = Pt(tam)
    r.bold = negrita
    return r


def salto():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def h(texto, nivel=1):
    return doc.add_heading(texto, level=nivel)


# ---------------------------------------------------------------------------
#  Contenido
# ---------------------------------------------------------------------------
def portada():
    for _ in range(2):
        doc.add_paragraph()
    par = p("", alinear=WD_ALIGN_PARAGRAPH.CENTER)
    resaltado(par, "[NOMBRE DE LA INSTITUCIÓN]", 14, True)
    par = p("", alinear=WD_ALIGN_PARAGRAPH.CENTER)
    resaltado(par, "[Programa / Facultad]", 12)
    for _ in range(3):
        doc.add_paragraph()
    p("PROYECTO FINAL", negrita=True, alinear=WD_ALIGN_PARAGRAPH.CENTER, tam=14, color=GRIS)
    p("RutaTaller Medellín", negrita=True, alinear=WD_ALIGN_PARAGRAPH.CENTER, tam=30, color=AZUL, despues=2)
    p("Sistema de directorio y calificación de talleres para carros y motos",
      alinear=WD_ALIGN_PARAGRAPH.CENTER, tam=14, color=GRIS)
    p("Documento técnico: análisis, diseño, desarrollo en C# (.NET) y pruebas",
      cursiva=True, alinear=WD_ALIGN_PARAGRAPH.CENTER, tam=11, color=GRIS)
    for _ in range(4):
        doc.add_paragraph()
    p("Integrantes:", negrita=True, alinear=WD_ALIGN_PARAGRAPH.CENTER, tam=12, despues=2)
    for k in (1, 2, 3):
        par = p("", alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=2)
        resaltado(par, f"[Nombre completo del integrante {k}]  –  [Documento / código]", 12)
    doc.add_paragraph()
    par = p("", alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=2)
    par.add_run("Docente: ").bold = True
    resaltado(par, "[Nombre del docente]", 12)
    par = p("", alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=2)
    par.add_run("Asignatura: ").bold = True
    resaltado(par, "[Nombre de la asignatura]  –  Grupo [N°]", 12)
    for _ in range(3):
        doc.add_paragraph()
    p("Medellín, Antioquia", alinear=WD_ALIGN_PARAGRAPH.CENTER, tam=12, despues=0)
    p("Noviembre de 2026", alinear=WD_ALIGN_PARAGRAPH.CENTER, tam=12)
    salto()


def indice():
    p("Tabla de contenido", negrita=True, tam=16, color=AZUL, alinear=WD_ALIGN_PARAGRAPH.LEFT)
    par = doc.add_paragraph()
    campo(par, 'TOC \\o "1-2" \\h \\z \\u')
    salto()


def introduccion():
    h("1. Introducción")
    p("En Medellín una gran parte de la población se moviliza en carro o en moto, y tarde o temprano todo "
      "vehículo necesita un taller: un cambio de aceite, una revisión de frenos, una falla eléctrica o un "
      "golpe de latonería. Sin embargo, muchos talleres de barrio, que suelen ser los más cercanos y "
      "económicos, **no aparecen en Google Maps o tienen muy pocas reseñas**, por lo que el conductor termina "
      "eligiendo \"a ciegas\" o por recomendación de un conocido.")
    p("Este documento presenta **RutaTaller Medellín**, una solución informática desarrollada en **C# sobre "
      ".NET** que funciona como un directorio de talleres organizados por comuna, tipo de vehículo y "
      "especialidad, donde los usuarios pueden registrar talleres nuevos y calificarlos en cuatro criterios "
      "(precio, calidad, tiempo de entrega y atención). Con esas calificaciones el sistema calcula promedios, "
      "clasifica cada taller, arma un ranking y genera estadísticas que facilitan la toma de decisiones.")
    p("El documento sigue el proceso completo de una solución para un cliente real: levantamiento de requisitos, "
      "análisis, diseño con diagramas de flujo, implementación modular con vectores, matrices, funciones y "
      "procedimientos, pruebas de escritorio con casos normales, límite y de error, y finalmente las conclusiones "
      "y recomendaciones para versiones futuras.")


def requisitos():
    h("2. Levantamiento de requisitos")
    h("2.1 Descripción del problema", 2)
    p("Los conductores de carros y motos en Medellín no tienen una herramienta sencilla para **encontrar y comparar "
      "talleres** cercanos según el tipo de vehículo y el servicio que necesitan. Las plataformas de mapas existentes "
      "no incluyen muchos talleres informales o de barrio, y cuando aparecen, sus reseñas se reducen a una calificación "
      "general que no dice si el taller es caro, si se demora o si atiende bien. Esto genera pérdidas de tiempo y "
      "dinero, trabajos mal hechos y desconfianza.")
    h("2.2 Contexto de aplicación", 2)
    p("La solución se aplica en el **entorno social y empresarial de Medellín** (16 comunas urbanas). Los usuarios son "
      "conductores particulares, motociclistas, domiciliarios y conductores de plataformas que dependen de su vehículo "
      "para trabajar, así como los dueños de talleres pequeños que quieren hacerse visibles. El sistema se ejecuta en un "
      "computador con .NET, como prototipo de lo que luego puede convertirse en una aplicación web o móvil.")
    h("2.3 Justificación", 2)
    viñetas([
        "**Visibilidad:** permite registrar talleres que no existen en las plataformas de mapas.",
        "**Mejores decisiones:** al calificar por criterios separados el usuario sabe si un taller es barato pero lento, "
        "o costoso pero de muy buena calidad.",
        "**Ahorro de tiempo y dinero:** la búsqueda por comuna, vehículo y especialidad muestra solo los talleres útiles.",
        "**Beneficio para los talleres pequeños:** un buen servicio se refleja en el ranking sin necesidad de pagar publicidad.",
        "**Viabilidad:** no requiere servicios pagos ni conexión a internet para funcionar como prototipo.",
    ])
    h("2.4 Objetivos", 2)
    p("**Objetivo general:** desarrollar en C# un sistema de consola que permita registrar, buscar y calificar talleres "
      "de carros y motos de Medellín, calculando promedios, rankings y estadísticas que ayuden a los conductores a "
      "elegir el taller adecuado.")
    p("**Objetivos específicos:**", despues=2)
    viñetas([
        "Almacenar la información de los talleres en vectores paralelos y las calificaciones en una matriz de acumuladores.",
        "Implementar búsquedas por comuna, tipo de vehículo y especialidad.",
        "Calcular el promedio general y por criterio de cada taller y clasificarlo (Excelente, Bueno, Regular, Deficiente).",
        "Generar un ranking ordenado de los mejores talleres y estadísticas generales de la ciudad.",
        "Validar todas las entradas del usuario con ciclos para garantizar datos correctos.",
        "Documentar el análisis, el diseño y las pruebas de escritorio de la solución.",
    ], "List Number")

    h("2.5 Requerimientos funcionales", 2)
    tabla(["Código", "Requerimiento", "Opción del menú"], [
        ["RF-01", "Mostrar un menú principal que se repite hasta que el usuario elija salir.", "Menú"],
        ["RF-02", "Listar todos los talleres con comuna, tipo de vehículo y calificación.", "1"],
        ["RF-03", "Ver el detalle de un taller: datos, promedio por criterio y últimos comentarios.", "2"],
        ["RF-04", "Buscar talleres por comuna de Medellín.", "3"],
        ["RF-05", "Buscar talleres por tipo de vehículo (carro / moto) y especialidad.", "4"],
        ["RF-06", "Registrar un taller nuevo (nombre, dirección, comuna, teléfono, tipo, especialidad).", "5"],
        ["RF-07", "Calificar un taller de 1 a 5 en cuatro criterios y dejar un comentario opcional.", "6"],
        ["RF-08", "Mostrar el ranking de los 10 mejores talleres ordenado por promedio.", "7"],
        ["RF-09", "Mostrar estadísticas: totales, talleres por comuna y tipo, promedio de la ciudad y mejor taller por criterio.", "8"],
        ["RF-10", "Impedir el registro de talleres con nombre repetido.", "5"],
    ], anchos=[1.8, 11.5, 2.6], titulo="Requerimientos funcionales")

    h("2.6 Requerimientos no funcionales", 2)
    tabla(["Código", "Requerimiento", "Tipo"], [
        ["RNF-01", "Desarrollado en C# sobre .NET (aplicación de consola).", "Tecnología"],
        ["RNF-02", "Toda entrada se valida con ciclos; el programa nunca se cierra por un dato mal digitado.", "Confiabilidad"],
        ["RNF-03", "Mensajes de error claros, en español y en color rojo; confirmaciones en verde.", "Usabilidad"],
        ["RNF-04", "Código modular: mínimo tres archivos y funciones con parámetros.", "Mantenibilidad"],
        ["RNF-05", "Capacidad para 30 talleres y respuesta inmediata (< 1 segundo) en cualquier opción.", "Rendimiento"],
        ["RNF-06", "Funciona sin internet ni servicios pagos.", "Portabilidad / costo"],
        ["RNF-07", "Las calificaciones son anónimas: no se piden datos personales del usuario que opina.", "Privacidad"],
    ], anchos=[1.8, 11.0, 3.1], titulo="Requerimientos no funcionales")

    h("2.7 Usuarios involucrados", 2)
    tabla(["Usuario", "Descripción", "Qué hace en el sistema"], [
        ["Conductor de carro", "Persona que necesita un taller para su vehículo particular.", "Busca, consulta detalle, ve ranking y califica."],
        ["Motociclista / domiciliario", "Depende de la moto para trabajar; necesita talleres rápidos y económicos.", "Busca por moto y especialidad, califica el tiempo de entrega."],
        ["Dueño de taller", "Taller pequeño que no aparece en los mapas.", "Registra su taller para hacerse visible."],
        ["Comunidad", "Cualquier usuario que ya conoce un taller.", "Registra talleres y comparte opiniones."],
    ], anchos=[3.4, 6.3, 6.2], titulo="Usuarios del sistema")


def analisis():
    h("3. Análisis de la solución")
    h("3.1 Propuesta lógica", 2)
    p("Cada taller se identifica por una **posición i** común a varios vectores paralelos (nombre, dirección, comuna, "
      "teléfono, tipo y especialidad). Cuando un usuario califica el taller i, las cuatro notas se **suman** en la fila i "
      "de la matriz `sumaCalificaciones` y se incrementa el contador `cantidadOpiniones[i]`. Así no es necesario guardar "
      "cada opinión por separado: el promedio de cualquier taller se obtiene dividiendo la suma de su fila entre "
      "(opiniones × 4). A partir de esos promedios se clasifica el taller, se ordena el ranking con el método burbuja y "
      "se calculan las estadísticas.")
    h("3.2 Entradas, procesos y salidas", 2)
    tabla(["Entradas", "Procesos", "Salidas"], [
        ["Opción del menú (0 a 8)", "Validar opción y dirigir con Según (switch)", "Pantalla de la opción elegida"],
        ["Datos del taller: nombre, dirección, comuna, teléfono, tipo, especialidad",
         "Validar cada dato, verificar que el nombre no exista y guardarlo en los vectores", "Mensaje de registro y número asignado"],
        ["Número de taller, 4 notas (1-5), comentario, confirmación S/N",
         "Acumular notas en la matriz, aumentar contador, guardar comentario, recalcular promedio", "Nuevo promedio, estrellas y categoría"],
        ["Comuna, o tipo de vehículo + especialidad", "Recorrer los vectores y filtrar con operadores lógicos", "Lista de talleres encontrados y cantidad"],
        ["—", "Calcular promedios y ordenar con burbuja", "Ranking Top 10"],
        ["—", "Contadores y acumuladores por comuna, tipo y criterio", "Estadísticas generales"],
    ], anchos=[5.0, 6.0, 4.9], titulo="Matriz de entradas, procesos y salidas")

    h("3.3 Restricciones y validaciones", 2)
    tabla(["Dato", "Regla de validación", "Mensaje si falla"], [
        ["Opción de menú", "Entero entre 0 y 8, no vacío", "Debe escribir un número entero / entre 0 y 8"],
        ["Nombre del taller", "3 a 40 caracteres, no solo números, no repetido (sin importar mayúsculas)", "Ya existe un taller con ese nombre"],
        ["Dirección", "5 a 50 caracteres, no solo números", "Debe tener entre 5 y 50 caracteres"],
        ["Comuna", "Entero entre 1 y 16", "El número debe estar entre 1 y 16"],
        ["Teléfono", "Solo dígitos; 7 (fijo) o 10 (celular)", "Debe tener 7 o 10 dígitos"],
        ["Tipo de vehículo / especialidad", "Entero dentro de la lista mostrada", "El número debe estar entre 1 y N"],
        ["Calificación", "Entero entre 1 y 5 para cada criterio", "El número debe estar entre 1 y 5"],
        ["Comentario", "Opcional, máximo 80 caracteres", "Máximo 80 caracteres"],
        ["Confirmación", "Solo S o N", "Responda solamente S o N"],
        ["Capacidad", "Máximo 30 talleres", "Se alcanzó el máximo de 30 talleres"],
    ], anchos=[3.6, 7.0, 5.3], titulo="Validaciones implementadas")

    h("3.4 Descomposición en módulos", 2)
    p("El programa se divide en tres archivos (módulos), cada uno con una responsabilidad clara:")
    tabla(["Módulo / archivo", "Subproceso o función", "Parámetros → retorno", "Tipo"], [
        ["Validaciones.cs", "LeerEntero", "mensaje, min, max → int", "Función"],
        ["", "LeerTexto", "mensaje, minimo, maximo → string", "Función"],
        ["", "LeerTextoOpcional", "mensaje, maximo → string", "Función"],
        ["", "LeerTelefono", "mensaje → string", "Función"],
        ["", "LeerSiNo", "mensaje → bool", "Función"],
        ["", "EsSoloDigitos", "texto → bool", "Función"],
        ["", "MostrarError / Pausar", "mensaje / — ", "Procedimiento"],
        ["Calculos.cs", "CalcularPromedioTaller", "sumas[,], opiniones[], indice → double", "Función"],
        ["", "CalcularPromedioCriterio", "sumas[,], opiniones[], indice, criterio → double", "Función"],
        ["", "ObtenerCategoria", "promedio, numOpiniones → string", "Función"],
        ["", "ObtenerEstrellas", "promedio → string", "Función"],
        ["", "OrdenarPorPromedio", "sumas[,], opiniones[], total, out cantidad → int[]", "Función"],
        ["Program.cs", "Main", "—", "Principal"],
        ["", "MostrarMenu, ListarTalleres, VerDetalleTaller, BuscarPorComuna, BuscarPorTipoYEspecialidad, "
             "RegistrarTaller, CalificarTaller, MostrarRanking, MostrarEstadisticas", "—", "Procedimientos"],
        ["", "AgregarTaller", "nombre, direccion, comuna, telefono, tipo, especialidad → int", "Función"],
        ["", "AgregarOpinion", "i, notas[], comentario", "Procedimiento"],
        ["", "BuscarIndicePorNombre / BuscarMejorEnCriterio", "nombre → int / criterio → int", "Función"],
        ["", "MostrarOpciones, MostrarFilaTaller, Recortar, SeleccionarTaller", "varios", "Apoyo"],
    ], anchos=[3.0, 5.6, 5.2, 2.1], tam=9, titulo="Módulos, funciones y procedimientos")

    h("3.5 Estructuras de datos", 2)
    tabla(["Estructura", "Tipo y tamaño", "Contenido"], [
        ["nombres, direcciones, telefonos", "string[30] (vectores paralelos)", "Datos de texto de cada taller"],
        ["comunas, tipos, especialidades", "int[30] (vectores paralelos)", "Índice dentro de los vectores constantes"],
        ["COMUNAS, TIPOS_VEHICULO, ESPECIALIDADES, CRITERIOS", "string[16], [3], [6], [4]", "Catálogos fijos que se muestran como opciones"],
        ["sumaCalificaciones", "int[30, 4] (matriz)", "Acumulado de notas por taller (fila) y criterio (columna)"],
        ["cantidadOpiniones", "int[30] (vector contador)", "Número de opiniones de cada taller"],
        ["comentarios", "string[30, 3] (matriz)", "Los 3 comentarios más recientes de cada taller"],
        ["totalTalleres", "int (contador)", "Cantidad de posiciones ocupadas en los vectores"],
    ], anchos=[5.4, 4.6, 5.9], titulo="Vectores y matrices del sistema")
    figura("cod_datos", "Declaración de constantes, vectores paralelos y matrices (Program.cs).", 15.5)

    h("3.6 Diagrama de flujo general y descripción del menú", 2)
    p("El programa principal configura la consola, carga seis talleres de ejemplo y entra en un ciclo **mientras** "
      "(`while (opcion != 0)`). En cada vuelta muestra el menú, lee la opción con `LeerEntero(…, 0, 8)` (que ya garantiza "
      "una opción válida) y la estructura **Según** (`switch`) llama al procedimiento correspondiente.")
    figura("flujo_general", "Diagrama de flujo general del sistema (menú principal).", 15.5)
    tabla(["Opción", "Nombre", "Descripción"], [
        ["1", "Ver todos los talleres", "Tabla con nombre, comuna, vehículos que atiende, promedio, estrellas y n.° de opiniones."],
        ["2", "Ver detalle y opiniones", "Datos completos, promedio por criterio, categoría y últimos 3 comentarios."],
        ["3", "Buscar por comuna", "Muestra las 16 comunas y lista los talleres de la elegida (o un aviso si no hay)."],
        ["4", "Buscar por vehículo y especialidad", "Filtra talleres que atienden carro o moto y, opcionalmente, una especialidad."],
        ["5", "Registrar taller", "Pide y valida todos los datos; evita nombres repetidos."],
        ["6", "Calificar taller", "Notas de 1 a 5 en cuatro criterios, comentario opcional y confirmación."],
        ["7", "Ranking", "Top 10 por promedio (desempate: más opiniones). Excluye talleres sin calificar."],
        ["8", "Estadísticas", "Totales, conteo por tipo y comuna, promedio de la ciudad y mejor taller por criterio."],
        ["0", "Salir", "Muestra un mensaje de despedida y termina el ciclo."],
    ], anchos=[1.4, 4.2, 10.3], titulo="Descripción del menú principal")

    h("3.7 Diagramas de flujo de los subprocesos clave", 2)
    figura("flujo_leer_entero", "Función LeerEntero: validación con ciclo mientras y condicionales anidadas.", 13)
    figura("flujo_promedio", "Función CalcularPromedioTaller: ciclo para con acumulador.", 15.5)
    figura("flujo_calificar", "Procedimiento CalificarTaller.", 12.5)


def desarrollo():
    h("4. Desarrollo de la solución")
    h("4.1 Entorno de desarrollo", 2)
    viñetas([
        "**Lenguaje:** C# 14.",
        "**Plataforma:** .NET 10 (SDK 10.0), aplicación de consola.",
        "**Editor:** Visual Studio Code / Visual Studio.",
        "**Control de versiones:** Git y GitHub.",
        "**Ejecución:** `dotnet run` dentro de la carpeta `codigo/RutaTaller`.",
    ])
    h("4.2 Estructura del proyecto", 2)
    tabla(["Archivo", "Responsabilidad"], [
        ["RutaTaller.csproj", "Configuración del proyecto .NET."],
        ["Program.cs", "Datos (vectores y matrices), Main con el menú y los procedimientos de cada opción."],
        ["Validaciones.cs", "Funciones de lectura y validación de datos con ciclos."],
        ["Calculos.cs", "Funciones de cálculo: promedios, categoría, estrellas y ordenamiento del ranking."],
    ], anchos=[4.2, 11.7], titulo="Archivos del código fuente")

    h("4.3 Conceptos de programación aplicados", 2)
    tabla(["Concepto", "Dónde se aplica (ejemplo)"], [
        ["Variables y tipos de datos", "int, double, string, bool; constantes `MAX_TALLERES`, `MAX_COMENTARIOS`."],
        ["Operadores relacionales", "`<`, `>`, `<=`, `>=`, `==`, `!=` en LeerEntero, ObtenerCategoria y búsquedas."],
        ["Operadores lógicos", "`&&` y `||` en BuscarPorTipoYEspecialidad; `!` en `while (!valido)`."],
        ["Condicional simple", "`if (cantidadOpiniones[i] == 0) sinCalificar++;` en MostrarEstadisticas."],
        ["Condicional doble", "`if (LeerSiNo(...)) … else …` en CalificarTaller."],
        ["Condicionales anidadas", "ObtenerCategoria (if dentro de else) y la cadena if/else if de LeerEntero."],
        ["Según (switch)", "Selección de la opción del menú en Main."],
        ["Ciclo mientras (while)", "Menú principal y LeerEntero / LeerTexto."],
        ["Ciclo repetir (do-while)", "LeerTelefono, LeerTextoOpcional y nombre no repetido en RegistrarTaller."],
        ["Ciclo para (for)", "Recorrer talleres, criterios, comunas; burbuja con for anidados."],
        ["Contadores", "totalTalleres, cantidadOpiniones[i], encontrados, talleresPorComuna[k], talleresPorTipo[t]."],
        ["Acumuladores", "sumaCalificaciones[i, c], total (promedio), totalOpiniones, sumaPorCriterio[c]."],
        ["Vectores", "Vectores paralelos de talleres y catálogos de comunas, tipos, especialidades y criterios."],
        ["Matrices", "sumaCalificaciones[30, 4] y comentarios[30, 3]."],
        ["Funciones", "LeerEntero, CalcularPromedioTaller, ObtenerCategoria, OrdenarPorPromedio, etc. (retornan valor)."],
        ["Procedimientos", "MostrarMenu, RegistrarTaller, CalificarTaller, MostrarRanking, AgregarOpinion (void)."],
        ["Programación modular", "Tres archivos: Program.cs, Validaciones.cs, Calculos.cs."],
        ["Validación de datos", "Todas las lecturas pasan por el módulo Validaciones."],
        ["Menú funcional", "Ocho opciones más salir, repetido hasta elegir 0."],
    ], anchos=[4.4, 11.5], titulo="Conceptos aplicados en el código")

    h("4.4 Capturas del código C#", 2)
    figura("cod_main", "Programa principal: ciclo while del menú y estructura switch (Program.cs).", 15.5)
    figura("cod_leer_entero", "Función LeerEntero con validación por ciclo (Validaciones.cs).", 15.5)
    figura("cod_telefono", "Función LeerTelefono con ciclo repetir (do-while) (Validaciones.cs).", 15.5)
    figura("cod_promedio", "Función clave CalcularPromedioTaller (Calculos.cs).", 15.5)
    figura("cod_categoria", "Función ObtenerCategoria con condicionales anidadas (Calculos.cs).", 12)
    figura("cod_ordenar", "Ordenamiento del ranking con el método burbuja (Calculos.cs).", 15.5)
    figura("cod_calificar", "Procedimiento CalificarTaller (Program.cs).", 15.5)
    figura("cod_agregar_opinion", "Procedimiento AgregarOpinion: acumuladores, contador y matriz de comentarios.", 14)
    figura("cod_buscar_tipo", "Búsqueda con operadores lógicos (Program.cs).", 15.5)

    h("4.5 Capturas de la ejecución", 2)
    figura("con_menu", "Menú principal.", 11)
    figura("con_listado", "Opción 1: listado de talleres con promedio, estrellas y número de opiniones.", 15.5)
    figura("con_detalle", "Opción 2: detalle de un taller con promedio por criterio y comentarios.", 12)
    figura("con_buscar_tipo", "Opción 4: búsqueda de talleres que atienden motos.", 15.5)
    figura("con_registro", "Opción 5: registro de un taller nuevo (se omiten las listas de opciones).", 12)
    figura("con_estadisticas", "Opción 8: estadísticas generales.", 14)


def pruebas():
    h("5. Pruebas de escritorio")
    p("Las pruebas se diseñaron primero en papel (valores esperados) y luego se ejecutaron en el programa real. Para que "
      "la evidencia sea exacta, las entradas se guardaron en archivos de texto (`pruebas/caso*.txt`) y se ejecutaron con "
      "redirección: `dotnet run < ..\\..\\pruebas\\caso1_normal.txt`. Las salidas obtenidas están en `pruebas/caso*_salida.txt` "
      "y en las capturas de esta sección.", alinear=WD_ALIGN_PARAGRAPH.LEFT)
    p("Datos de partida (talleres precargados en `CargarDatosIniciales`):", despues=2)
    tabla(["i", "Taller", "Opiniones", "Sumas [Precio, Calidad, Tiempo, Atención]", "Promedio esperado"], [
        ["0", "Taller El Pistón", "4", "[13, 15, 12, 14] = 54", "54 / 16 = 3,375"],
        ["1", "MotoExpress Belén", "3", "[14, 14, 14, 15] = 57", "57 / 12 = 4,75"],
        ["2", "Frenos y Suspensión Castilla", "2", "[8, 9, 8, 7] = 32", "32 / 8 = 4,00"],
        ["3", "Electroauto Laureles", "2", "[4, 7, 4, 5] = 20", "20 / 8 = 2,50"],
        ["4", "Llantas La 80", "1", "[2, 2, 1, 2] = 7", "7 / 4 = 1,75"],
        ["5", "Latonería Don Jairo", "0", "[0, 0, 0, 0] = 0", "0 (sin calificar)"],
    ], anchos=[0.8, 5.0, 1.9, 5.0, 3.2], titulo="Datos iniciales usados en las pruebas")

    # ---------------- Prueba 1 ----------------
    h("5.1 Prueba 1 – Caso normal: CalcularPromedioTaller", 2)
    p("**Objetivo:** verificar que el promedio general de un taller con varias opiniones se calcula bien. "
      "**Llamado:** `CalcularPromedioTaller(sumaCalificaciones, cantidadOpiniones, 0)` (Taller El Pistón).")
    tabla(["Paso", "c", "c < 4", "sumas[0, c]", "total", "Observación"], [
        ["Inicio", "–", "–", "–", "–", "opiniones[0] = 4 ≠ 0 → continúa; numCriterios = 4; total = 0"],
        ["1", "0", "V", "13", "13", "total = 0 + 13"],
        ["2", "1", "V", "15", "28", "total = 13 + 15"],
        ["3", "2", "V", "12", "40", "total = 28 + 12"],
        ["4", "3", "V", "14", "54", "total = 40 + 14"],
        ["5", "4", "F", "–", "54", "Sale del ciclo"],
        ["Retorno", "–", "–", "–", "–", "54 / (4 × 4) = 54 / 16 = **3,375**"],
    ], anchos=[1.6, 1.0, 1.3, 2.2, 1.4, 8.4], titulo="Prueba 1 – seguimiento de variables")
    tabla(["Resultado esperado", "Resultado obtenido", "¿Cumple?"], [
        ["Promedio 3,375 → en pantalla 3,38; estrellas ***-- (3); categoría Regular (2,5 ≤ 3,375 < 3,5). "
         "Por criterio: Precio 13/4 = 3,25; Calidad 15/4 = 3,75; Tiempo 12/4 = 3,00; Atención 14/4 = 3,50.",
         "3,38 ***-- → Regular. Precio 3,25; Calidad 3,75; Tiempo 3,00; Atención 3,50 (Figura siguiente).", "Sí ✔"],
    ], anchos=[7.0, 7.0, 1.9], titulo="Prueba 1 – esperado vs. obtenido")
    figura("con_detalle", "Evidencia de la Prueba 1: detalle del Taller El Pistón.", 11.5)
    figura("con_ranking1", "Ranking con los datos iniciales: los promedios coinciden con la tabla de datos de partida.", 14)

    # ---------------- Prueba 2 ----------------
    h("5.2 Prueba 2 – Casos límite", 2)
    p("**Objetivo:** comprobar el comportamiento en las fronteras: taller sin opiniones (evita división por cero), "
      "promedio exactamente en el límite de una categoría, calificación máxima y búsqueda sin resultados.")
    tabla(["Caso", "Datos de entrada", "Cálculo / recorrido", "Esperado", "Obtenido", "✔"], [
        ["2a. Sin opiniones", "i = 5, Latonería Don Jairo, opiniones[5] = 0",
         "La condición opiniones = 0 es verdadera → retorna 0 sin entrar al ciclo (no divide por cero).",
         "\"sin opiniones\"; no aparece en el ranking", "\"sin opiniones\" y \"(1 taller(es) sin opiniones no aparecen en el ranking)\"", "Sí"],
        ["2b. Frontera de categoría", "i = 3, Electroauto, sumas [4, 7, 4, 5], opiniones 2",
         "total: 4 → 11 → 15 → 20; 20 / (2 × 4) = 2,50. ObtenerCategoria: 2,50 ≥ 4,5 F; ≥ 3,5 F; ≥ 2,5 V",
         "2,50 → Regular (no Deficiente)", "2,50 ***-- → Regular", "Sí"],
        ["2c. Calificación máxima", "Taller nuevo i = 6 con notas 5, 5, 5, 5",
         "sumas [5, 5, 5, 5]; total 20; 20 / (1 × 4) = 5,00 ≥ 4,5",
         "5,00 ***** Excelente; puesto 1 del ranking (empata en categoría con MotoExpress 4,75 pero tiene mayor promedio)",
         "5,00 ***** (Excelente); puesto 1 del ranking", "Sí"],
        ["2d. Búsqueda vacía", "Opción 3, comuna 2 (Santa Cruz)",
         "Ningún comunas[i] = 1 → encontrados = 0", "Mensaje \"No hay talleres registrados en esta comuna\"",
         "Mensaje mostrado", "Sí"],
    ], anchos=[2.4, 3.2, 4.3, 2.8, 2.6, 0.6], tam=8.5, titulo="Prueba 2 – casos límite")
    figura("con_calificar_5", "Evidencia 2c: calificación máxima de un taller recién registrado.", 13)
    figura("con_ranking2", "Evidencia 2a y 2c: el taller nuevo queda primero y el taller sin opiniones se excluye.", 14)
    figura("con_electroauto", "Evidencia 2b: promedio 2,50 clasificado como Regular.", 11.5)
    figura("con_comuna_vacia", "Evidencia 2d: búsqueda en una comuna sin talleres.", 15)

    # ---------------- Prueba 3 ----------------
    h("5.3 Prueba 3 – Validación de errores: LeerEntero", 2)
    p("**Objetivo:** verificar que la función no acepta datos vacíos, texto ni números fuera de rango y que sigue "
      "pidiendo el dato hasta que sea válido. **Llamado:** `LeerEntero(\"  Precio (1-5): \", 1, 5)` al calificar.")
    tabla(["Vuelta", "entrada", "¿vacía?", "¿es entero?", "valor", "1 ≤ valor ≤ 5", "valido", "Salida en pantalla"], [
        ["1", "\"\"", "V", "–", "0", "–", "F", "[ERROR] El dato no puede estar vacío."],
        ["2", "\"6\"", "F", "V", "6", "F", "F", "[ERROR] El número debe estar entre 1 y 5."],
        ["3", "\"cinco\"", "F", "F", "0", "–", "F", "[ERROR] Debe escribir un número entero."],
        ["4", "\"5\"", "F", "V", "5", "V", "V", "Sale del ciclo y retorna 5"],
    ], anchos=[1.3, 1.6, 1.3, 1.6, 1.1, 2.0, 1.3, 5.7], tam=9, titulo="Prueba 3 – seguimiento de LeerEntero")
    p("**Resultado esperado:** tres mensajes de error distintos y luego se acepta el 5. **Obtenido:** idéntico "
      "(figura siguiente). También se probó la confirmación con \"x\" (rechazada) y \"N\", que descarta la opinión. ✔")
    figura("con_err_calificar", "Evidencia de la Prueba 3: errores al seleccionar taller y al calificar.", 12.5)

    # ---------------- Prueba 4 ----------------
    h("5.4 Prueba 4 – Validación de errores en el menú y en el registro", 2)
    tabla(["Dato", "Entrada", "Regla que se incumple", "Mensaje esperado", "✔"], [
        ["Opción del menú", "(vacío)", "Dato obligatorio", "El dato no puede estar vacío.", "Sí"],
        ["Opción del menú", "abc", "Debe ser entero", "Debe escribir un número entero.", "Sí"],
        ["Opción del menú", "9 / -1", "Rango 0 a 8", "El número debe estar entre 0 y 8.", "Sí"],
        ["Nombre", "taller el pistón", "Nombre repetido (ignora mayúsculas)", "Ya existe un taller con ese nombre.", "Sí"],
        ["Nombre", "12345", "No puede ser solo números", "No puede contener solamente números.", "Sí"],
        ["Nombre", "AB", "Longitud 3 a 40", "Debe tener entre 3 y 40 caracteres.", "Sí"],
        ["Dirección", "Cl 1", "Longitud 5 a 50", "Debe tener entre 5 y 50 caracteres.", "Sí"],
        ["Comuna", "17 / 0", "Rango 1 a 16", "El número debe estar entre 1 y 16.", "Sí"],
        ["Teléfono", "(vacío)", "Dato obligatorio", "El teléfono no puede estar vacío.", "Sí"],
        ["Teléfono", "300-123", "Solo dígitos", "El teléfono solo puede tener números.", "Sí"],
        ["Teléfono", "12345", "7 o 10 dígitos", "Debe tener 7 dígitos (fijo) o 10 dígitos (celular).", "Sí"],
        ["Tipo de vehículo", "4", "Rango 1 a 3", "El número debe estar entre 1 y 3.", "Sí"],
        ["Especialidad", "7 / 0", "Rango 1 a 6", "El número debe estar entre 1 y 6.", "Sí"],
    ], anchos=[2.8, 2.6, 3.8, 5.9, 0.8], tam=9, titulo="Prueba 4 – entradas inválidas y mensajes")
    p("Después de los datos válidos el taller \"Taller Nuevo Robledo\" se registró con el número 7. ✔")
    figura("con_err_menu", "Evidencia de la Prueba 4: errores en la opción del menú.", 10)
    figura("con_err_registro", "Evidencia de la Prueba 4: errores durante el registro de un taller.", 12.5)

    h("5.5 Resumen de pruebas", 2)
    tabla(["Prueba", "Tipo", "Función / opción evaluada", "Resultado"], [
        ["1", "Normal", "CalcularPromedioTaller, detalle y ranking", "Aprobada"],
        ["2", "Límite", "División por cero, frontera 2,5, máximo 5,0, búsqueda vacía", "Aprobada"],
        ["3", "Error", "LeerEntero (vacío, texto, fuera de rango) y LeerSiNo", "Aprobada"],
        ["4", "Error", "Menú, LeerTexto, nombre repetido, LeerTelefono", "Aprobada"],
    ], anchos=[1.6, 2.0, 9.4, 2.9], titulo="Resumen de resultados")


def justificacion():
    h("6. Justificación de las decisiones tomadas")
    viñetas([
        "**Aplicación de consola y sin API de mapas:** el objetivo del curso es la lógica (ciclos, arreglos, funciones). "
        "La API de Google Maps exige una clave con facturación y una interfaz gráfica; para ubicar un taller basta con "
        "la dirección y la comuna. La integración con mapas queda como recomendación.",
        "**Vectores paralelos de tamaño fijo (30):** aplican directamente los vectores vistos en clase; el límite se "
        "controla con el contador `totalTalleres` y una validación de capacidad.",
        "**Matriz de acumuladores en lugar de guardar cada opinión:** con solo sumar las notas y contar las opiniones se "
        "obtiene cualquier promedio; ocupa poca memoria y no tiene límite de opiniones por taller.",
        "**Cuatro criterios de calificación:** un solo puntaje esconde información; separarlos permite saber si un taller "
        "es bueno pero caro o barato pero lento.",
        "**Comunas e ítems por número:** se eligen de una lista para evitar errores de escritura (\"Belen\", \"belén\") y "
        "poder contar talleres por comuna.",
        "**Cálculos separados de la entrada/salida (Calculos.cs):** las funciones de cálculo reciben todo por parámetros, "
        "lo que hace más fácil la prueba de escritorio y su reutilización.",
        "**Ranking sin talleres sin calificar y con desempate por número de opiniones:** un promedio de 0 no significa que "
        "el taller sea malo, y un promedio con más opiniones es más confiable.",
        "**Método burbuja:** es el algoritmo de ordenamiento estudiado en clase y es suficiente para 30 elementos.",
        "**Datos de ejemplo precargados (ficticios):** permiten demostrar todas las opciones sin tener que digitar datos "
        "cada vez que se ejecuta el programa.",
    ])


def cierre():
    h("7. Conclusiones")
    viñetas([
        "Se construyó una solución funcional en C# que responde a un problema real de Medellín: encontrar y comparar "
        "talleres que no aparecen en las plataformas de mapas.",
        "El uso de vectores paralelos y de una matriz de acumuladores permitió representar los talleres y sus "
        "calificaciones de forma sencilla y eficiente, sin guardar cada opinión por separado.",
        "La modularidad (tres archivos y más de veinte subprocesos) hizo que el código fuera más fácil de leer, probar y "
        "explicar; cada integrante puede ubicar rápidamente cualquier parte del algoritmo.",
        "Las validaciones con ciclos garantizan que el programa nunca falle por un dato mal digitado, como se comprobó en "
        "las pruebas de error.",
        "Las pruebas de escritorio coincidieron con los resultados obtenidos en ejecución, incluidos los casos límite "
        "(sin opiniones, frontera de categoría y calificación máxima).",
    ])
    h("8. Recomendaciones")
    viñetas([
        "**Persistencia de datos:** guardar los talleres y opiniones en un archivo o en una base de datos (por ejemplo "
        "SQLite) para que no se pierdan al cerrar el programa.",
        "**Integración con mapas:** agregar latitud y longitud a cada taller y usar la API de Google Maps u OpenStreetMap "
        "para mostrarlos en un mapa y calcular la distancia al usuario.",
        "**Aplicación web o móvil:** llevar la lógica a ASP.NET Core o .NET MAUI para que la comunidad la use desde el celular.",
        "**Usuarios registrados y moderación:** evitar opiniones falsas o repetidas y permitir que los dueños respondan.",
        "**Más información:** fotos, horarios, rango de precios y servicio a domicilio o grúa.",
        "**Ampliar la cobertura:** incluir los municipios del Valle de Aburrá y, como siguiente módulo, estaciones de carga "
        "para vehículos eléctricos y de gas.",
    ])
    h("9. Bibliografía")
    refs = [
        "Cairó, O. (2005). *Metodología de la programación: algoritmos, diagramas de flujo y programas* (3.ª ed.). Alfaomega.",
        "Deitel, P., & Deitel, H. (2016). *Visual C# How to Program* (6.ª ed.). Pearson.",
        "Joyanes Aguilar, L. (2008). *Fundamentos de programación: algoritmos, estructura de datos y objetos* (4.ª ed.). McGraw-Hill.",
        "Microsoft. (s. f.). *Documentación de C#*. Microsoft Learn. https://learn.microsoft.com/es-es/dotnet/csharp/",
        "Microsoft. (s. f.). *Matrices (referencia de C#)*. Microsoft Learn. https://learn.microsoft.com/es-es/dotnet/csharp/language-reference/builtin-types/arrays",
        "Sommerville, I. (2011). *Ingeniería de software* (9.ª ed.). Pearson Educación.",
    ]
    for ref in refs:
        par = doc.add_paragraph()
        par.paragraph_format.left_indent = Cm(1.0)
        par.paragraph_format.first_line_indent = Cm(-1.0)
        for k, parte in enumerate(ref.split("*")):
            r = par.add_run(parte)
            r.italic = (k % 2 == 1)

    h("Anexo A. Repositorio y ejecución")
    par = p("**Repositorio GitHub:** ")
    resaltado(par, "[pegar aquí el link del repositorio]", 11)
    p("**Pasos para ejecutar:**", despues=2)
    viñetas([
        "**Paso 1:** instalar el SDK de .NET 10 (https://dotnet.microsoft.com/download).",
        "**Paso 2:** abrir una terminal en la carpeta `proyecto final/codigo/RutaTaller`.",
        "**Paso 3:** ejecutar `dotnet run`.",
        "**Pruebas:** `dotnet run < ..\\..\\pruebas\\caso1_normal.txt` (también caso2_limite y caso3_errores).",
    ])
    p("Nota: los talleres precargados, sus direcciones, teléfonos y opiniones son **ficticios** y se usan solo para "
      "demostrar el funcionamiento del sistema.", cursiva=True, tam=9.5, color=GRIS)


def encabezado_pie():
    sec = doc.sections[0]
    sec.different_first_page_header_footer = True
    hp = sec.header.paragraphs[0]
    hp.text = "RutaTaller Medellín – Proyecto final"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for r in hp.runs:
        r.font.size = Pt(9); r.font.color.rgb = GRIS
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run("Página "); r.font.size = Pt(9)
    campo(fp, "PAGE").font.size = Pt(9)


def exportar_pdf():
    ps = f"""
$ErrorActionPreference = 'Stop'
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {{
  $d = $w.Documents.Open('{SALIDA_DOCX}')
  foreach ($id in -20, -21) {{
    $s = $d.Styles.Item($id)
    $s.ParagraphFormat.SpaceAfter = 1
    $s.ParagraphFormat.SpaceBefore = 0
    $s.ParagraphFormat.LineSpacingRule = 0
    $s.Font.Size = 10.5
  }}
  $d.TablesOfContents.Item(1).Update()
  $d.Save()
  $d.SaveAs2('{SALIDA_PDF}', 17)
  $d.Close(0)
}} finally {{ $w.Quit() }}
"""
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)


def main():
    IMG.update(imagenes.generar_todo())
    configurar_estilos()
    encabezado_pie()
    portada()
    indice()
    introduccion()
    requisitos()
    analisis()
    desarrollo()
    pruebas()
    justificacion()
    cierre()
    doc.save(SALIDA_DOCX)
    print("DOCX:", SALIDA_DOCX)
    exportar_pdf()
    print("PDF :", SALIDA_PDF)


if __name__ == "__main__":
    main()
