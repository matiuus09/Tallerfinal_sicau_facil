"""Documento técnico corto de SICAU Fácil (Word + PDF).  Uso: python documento.py"""
import os

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm

import imagenes
import base_documento as D
from base_documento import h, p, viñetas, tabla, figura, salto, resaltado, GRIS, AZUL

D.SALIDA_DOCX = os.path.join(imagenes.BASE, "documentacion", "Documento_Tecnico_SICAU_Facil.docx")
D.SALIDA_PDF = os.path.join(imagenes.BASE, "documentacion", "Documento_Tecnico_SICAU_Facil.pdf")
C = WD_ALIGN_PARAGRAPH.CENTER


def portada():
    for _ in range(3):
        D.doc.add_paragraph()
    resaltado(p("", alinear=C), "INSTITUCIÓN UNIVERSITARIA PASCUAL BRAVO", 14, True)
    for _ in range(4):
        D.doc.add_paragraph()
    p("PROYECTO FINAL", negrita=True, alinear=C, tam=14, color=GRIS)
    p("SICAU Fácil", negrita=True, alinear=C, tam=30, color=AZUL, despues=2)
    p("Dos botones nuevos en el portal estudiantil: Clases y talleres, y Bienestar universitario",
      alinear=C, tam=13, color=GRIS)
    for _ in range(5):
        D.doc.add_paragraph()
    p("Integrantes:", negrita=True, alinear=C, tam=12, despues=2)
    for k in (1, 2, 3):
        resaltado(p("", alinear=C, despues=2), f"[Nombre del integrante {k}]", 12)
    D.doc.add_paragraph()
    par = p("", alinear=C, despues=2); par.add_run("Docente: ").bold = True; resaltado(par, "[Nombre del docente]", 12)
    par = p("", alinear=C, despues=2); par.add_run("Asignatura: ").bold = True; resaltado(par, "[Asignatura y grupo]", 12)
    for _ in range(4):
        D.doc.add_paragraph()
    p("Medellín, noviembre de 2026", alinear=C, tam=12)
    salto()


def contenido():
    h("1. Introducción")
    p("En el portal estudiantil SICAU no hay un acceso directo al material de clase (talleres de matemáticas y de las "
      "demás materias) ni a los cursos de Bienestar Universitario (baile, artes marciales, fútbol). **SICAU Fácil** es "
      "un prototipo en **C#** que genera una copia sencilla de la página \"Estudiantes\" y le agrega esos dos botones. "
      "Es una propuesta visual: solo funcionan los dos botones nuevos.")

    h("2. Levantamiento de requisitos")
    p("**Problema:** el material de clase llega disperso (correo, grupos, otras plataformas) y la oferta de Bienestar no "
      "se ve en el portal, así que muchos estudiantes no la conocen.")
    p("**Contexto:** estudiantes de la institución que ya usan SICAU. **Justificación:** agregar dos botones al portal "
      "que todos conocen es más simple que crear otra aplicación.")
    p("**Objetivo general:** mostrar con un programa en C# cómo se vería el portal con un acceso fácil a talleres y a "
      "cursos de Bienestar.", despues=2)
    p("**Objetivos específicos:**", despues=2)
    viñetas(["Guardar botones, talleres y cursos en vectores.",
             "Generar desde C# la página del portal, la de talleres (con su PDF) y la de bienestar.",
             "Validar con un ciclo la opción del menú."], "List Number")
    tabla(["Tipo", "Requerimiento"], [
        ["RF-01", "Menú en consola que se repite hasta elegir 0."],
        ["RF-02", "Generar y abrir la página: portal, talleres y bienestar."],
        ["RF-03", "En talleres, cada tarjeta abre un PDF de ejemplo (vacío)."],
        ["RF-04", "En bienestar, cada curso muestra horario, cupos y un botón \"Inscribirse\" (solo visual)."],
        ["RF-05", "Ver talleres y cursos en consola, con el total de cupos."],
        ["RNF-01", "C# / .NET 10, un solo archivo de código."],
        ["RNF-02", "La opción del menú se valida: no vacía, numérica y entre 0 y 3."],
        ["RNF-03", "Página sin imágenes y sin datos reales (estudiante de prueba)."],
    ], anchos=[2.2, 13.7], titulo="Requerimientos funcionales y no funcionales")
    p("**Usuarios:** estudiantes (consultan talleres y cursos), docentes (publicarían talleres) y Bienestar Universitario "
      "(publicaría cursos).")

    h("3. Análisis de la solución")
    tabla(["Entradas", "Procesos", "Salidas"], [
        ["Opción del menú (0 a 3)", "Validar con LeerOpcion y elegir con switch", "Acción elegida o mensaje de error"],
        ["Vectores de botones, talleres y cursos", "Recorrerlos con for y armar el HTML", "index.html, talleres.html, bienestar.html y taller.pdf"],
        ["Vector de cupos", "Sumar con un acumulador (SumarCupos)", "Total de cupos ofrecidos"],
    ], anchos=[4.6, 6.0, 5.3], titulo="Entradas, procesos y salidas")
    tabla(["Subproceso", "Parámetros → retorno", "Qué hace"], [
        ["LeerOpcion", "mensaje, min, max → int", "Pide la opción hasta que sea válida."],
        ["SumarCupos", "int[] cupos → int", "Suma los cupos de los cursos."],
        ["GenerarPagina", "—", "Escribe las tres páginas y el PDF, y abre el portal."],
        ["Plantilla", "contenido → string", "Agrega encabezado, menú y estilos comunes."],
        ["CrearPdfVacio", "ruta", "Crea un PDF válido de una página en blanco."],
    ], anchos=[3.4, 4.6, 7.9], titulo="Módulos (funciones)")
    figura("flujo_general", "Diagrama de flujo general.", 13)

    h("4. Desarrollo en C#")
    p("Todo el programa está en `codigo/SicauFacil/Program.cs`. Usa vectores paralelos, ciclo while para el menú, "
      "switch, ciclos for, condicionales anidadas en la validación, un acumulador y cinco funciones con parámetros.")
    figura("cod_datos", "Datos en vectores paralelos.", 15.5)
    figura("cod_menu", "Menú principal: ciclo while y switch.", 14)
    figura("cod_leer", "Función LeerOpcion (validación con ciclo).", 13)
    figura("cod_generar", "GenerarPagina: arma el HTML a partir de los vectores.", 15.5)
    h("4.1 Página generada", 2)
    figura("web_index", "Portal con la sección NUEVO. Los botones originales no hacen nada.", 15)
    figura("web_talleres", "Clases y talleres: cada botón abre el PDF de ejemplo.", 15)
    figura("web_bienestar", "Bienestar: baile, artes marciales y fútbol; \"Inscribirse\" es solo visual.", 15)

    h("5. Pruebas de escritorio")
    h("5.1 Prueba 1 – Caso normal: SumarCupos", 2)
    tabla(["i", "cupos[i]", "total"], [
        ["inicio", "–", "0"], ["0 (Bachata)", "25", "25"], ["1 (Salsa)", "25", "50"], ["2 (Taekwondo)", "20", "70"],
        ["3 (Karate)", "20", "90"], ["4 (Fútbol sala)", "15", "105"], ["5 (Fútbol 11)", "22", "**127**"],
    ], anchos=[4.0, 3.0, 3.0], titulo="Seguimiento de SumarCupos")
    p("**Esperado:** 127. **Obtenido:** \"Total de cupos ofrecidos: 127\". ✔")
    figura("con_normal", "Evidencia de la Prueba 1 (opciones 2, 3, 1 y 0).", 13)
    h("5.2 Prueba 2 – Caso límite: LeerOpcion(\"Opción: \", 0, 3)", 2)
    tabla(["Entrada", "¿Vacía?", "¿Número?", "0 ≤ valor ≤ 3", "Resultado"], [
        ["4", "No", "Sí", "No", "Error: debe estar entre 0 y 3"],
        ["3 (máximo)", "No", "Sí", "Sí", "Acepta 3 y muestra los cursos"],
        ["0 (mínimo)", "No", "Sí", "Sí", "Acepta 0 y sale"],
    ], anchos=[2.8, 2.0, 2.2, 3.0, 5.9], titulo="Prueba 2 – valores en el borde del rango")
    figura("con_limite", "Evidencia de la Prueba 2.", 12)
    h("5.3 Prueba 3 – Validación de errores", 2)
    tabla(["Entrada", "Regla que falla", "Mensaje esperado", "✔"], [
        ["(vacío)", "Dato obligatorio", "No puede estar vacío.", "Sí"],
        ["abc", "Debe ser número", "Escriba un número.", "Sí"],
        ["-1", "Rango 0 a 3", "Debe estar entre 0 y 3.", "Sí"],
        ["2.5", "Debe ser entero", "Escriba un número.", "Sí"],
    ], anchos=[2.8, 4.0, 6.5, 1.0], titulo="Prueba 3 – entradas inválidas")
    figura("con_errores", "Evidencia de la Prueba 3.", 9)

    h("6. Justificación, conclusiones y recomendaciones")
    viñetas([
        "**Un solo archivo y solo visual:** el objetivo es mostrar la idea; por eso solo funcionan los dos botones nuevos.",
        "**C# genera la página:** los vectores del programa son la fuente de los talleres y cursos que se ven en la web.",
        "**Sin imágenes ni datos reales:** el encabezado es texto y el estudiante es de prueba.",
    ])
    p("**Conclusión:** con pocos elementos (vectores, ciclos, switch y cinco funciones) se puede mostrar una mejora clara "
      "al portal: el estudiante encuentra sus talleres y los cursos de Bienestar en un clic.")
    p("**Recomendaciones:** conectar los talleres con los PDF reales de cada docente, hacer funcional la inscripción "
      "(cupos y horarios) y guardar los datos en una base de datos.")

    h("7. Bibliografía")
    for ref in ["Joyanes Aguilar, L. (2008). *Fundamentos de programación* (4.ª ed.). McGraw-Hill.",
                "Microsoft. (s. f.). *Documentación de C#*. https://learn.microsoft.com/es-es/dotnet/csharp/",
                "MDN Web Docs. (s. f.). *HTML*. https://developer.mozilla.org/es/docs/Web/HTML"]:
        par = D.doc.add_paragraph()
        par.paragraph_format.left_indent = Cm(1.0)
        par.paragraph_format.first_line_indent = Cm(-1.0)
        for k, parte in enumerate(ref.split("*")):
            par.add_run(parte).italic = (k % 2 == 1)
    resaltado(p("**Repositorio GitHub:** "), "[pegar aquí el link]", 11)


def main():
    D.IMG.update(imagenes.generar_todo())
    D.configurar_estilos()
    D.encabezado_pie()
    D.doc.sections[0].header.paragraphs[0].runs[0].text = "SICAU Fácil – Proyecto final"
    portada()
    D.indice()
    contenido()
    D.doc.save(D.SALIDA_DOCX)
    D.exportar_pdf()
    print("Listo:", D.SALIDA_PDF)


if __name__ == "__main__":
    main()
