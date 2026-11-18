# SICAU Fácil

Prototipo en **C# / .NET 10** (un solo archivo) que genera una copia sencilla de la página *Estudiantes* del portal SICAU con dos botones nuevos:

- **Clases y talleres**: talleres por materia; cada uno abre un PDF de ejemplo.
- **Bienestar universitario**: cursos de baile, artes marciales y fútbol con un botón **Inscribirse** (solo visual).

Los botones originales del portal se ven pero no hacen nada.

## Integrantes

- _[Nombre integrante 1]_
- _[Nombre integrante 2]_

## Ejecutar

```bash
cd "codigo/SicauFacil"
dotnet run
```

La opción **1** genera la página en `pagina/` y la abre en el navegador. En `pagina/` (raíz del proyecto) hay una copia ya generada.

## Contenido

```
codigo/SicauFacil/Program.cs   # todo el programa
pagina/                        # index.html, talleres.html, bienestar.html y taller.pdf
pruebas/                       # entradas y salidas de las 3 pruebas
documentacion/                 # documento técnico (PDF y Word) y su generador
```

> Prototipo académico con datos de ejemplo; no es un sitio oficial de la institución.
