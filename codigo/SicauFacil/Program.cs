using System.Diagnostics;
using System.Text;

// ------------------------- DATOS (vectores paralelos) -----------------------
string[] botonesPortal =
{
    "Reserva de módulos", "Mis reservas de módulos", "Mis reservas de espacios",
    "Datos personales", "Inscripción a procesos", "Inscripción a apoyos socioeconómicos",
    "Inscripción trabajo de grado", "Hoja de vida", "Ingresar a Bibliotecas",
    "Calendario académico", "Mis insignias digitales"
};
string[] coloresPortal =
{
    "#fff", "#5cb85c", "#5bc0de", "#337ab7", "#5bc0de", "#fff",
    "#5cb85c", "#337ab7", "#337ab7", "#f0ad4e", "#5bc0de"
};

string[] tallerMateria = { "Matemáticas", "Matemáticas", "Cálculo", "Lógica y Algoritmos", "Programación en C#", "Inglés" };
string[] tallerTitulo = { "Taller 1: Fracciones", "Taller 2: Ecuaciones lineales", "Taller 1: Límites",
                          "Taller 1: Diagramas de flujo", "Taller 1: Vectores", "Workshop 1: Greetings" };
int[] tallerSemana = { 2, 4, 3, 2, 5, 1 };

string[] cursoNombre = { "Bachata", "Salsa", "Taekwondo", "Karate", "Fútbol sala", "Fútbol 11" };
string[] cursoCategoria = { "Baile", "Baile", "Artes marciales", "Artes marciales", "Fútbol", "Fútbol" };
string[] cursoHorario = { "Martes 4:00 p. m.", "Jueves 4:00 p. m.", "Lunes 6:00 p. m.",
                          "Miércoles 6:00 p. m.", "Viernes 2:00 p. m.", "Sábado 9:00 a. m." };
int[] cursoCupos = { 25, 25, 20, 20, 15, 22 };

// ------------------------------ MENÚ PRINCIPAL -----------------------------
Console.OutputEncoding = Encoding.UTF8;
if (Console.IsInputRedirected) Console.InputEncoding = Encoding.UTF8;
string carpeta = Path.Combine(Directory.GetCurrentDirectory(), "pagina");

int opcion = -1;
while (opcion != 0)
{
    Console.WriteLine();
    Console.WriteLine("========== SICAU FÁCIL ==========");
    Console.WriteLine(" 1. Generar y abrir la página");
    Console.WriteLine(" 2. Ver talleres en consola");
    Console.WriteLine(" 3. Ver cursos de bienestar en consola");
    Console.WriteLine(" 0. Salir");
    opcion = LeerOpcion("Opción: ", 0, 3);

    switch (opcion)
    {
        case 1:
            GenerarPagina();
            break;
        case 2:
            for (int i = 0; i < tallerTitulo.Length; i++)
                Console.WriteLine($"  {tallerMateria[i],-20} {tallerTitulo[i],-30} Semana {tallerSemana[i]}");
            break;
        case 3:
            for (int i = 0; i < cursoNombre.Length; i++)
                Console.WriteLine($"  {cursoNombre[i],-12} {cursoCategoria[i],-16} {cursoHorario[i],-22} {cursoCupos[i]} cupos");
            Console.WriteLine($"  Total de cupos ofrecidos: {SumarCupos(cursoCupos)}");
            break;
        case 0:
            Console.WriteLine("Hasta pronto.");
            break;
    }
}

// ================================ FUNCIONES ================================

// Lee un número entre min y max. Repite hasta que el dato sea válido.
int LeerOpcion(string mensaje, int min, int max)
{
    while (true)
    {
        Console.Write(mensaje);
        string? entrada = Console.ReadLine();
        if (entrada == null) return 0;                       // fin del archivo de pruebas
        if (Console.IsInputRedirected) Console.WriteLine(entrada);

        if (entrada.Trim() == "")
            Console.WriteLine("  [ERROR] No puede estar vacío.");
        else if (!int.TryParse(entrada, out int valor))
            Console.WriteLine("  [ERROR] Escriba un número.");
        else if (valor < min || valor > max)
            Console.WriteLine($"  [ERROR] Debe estar entre {min} y {max}.");
        else
            return valor;
    }
}

// Acumulador: suma los cupos de todos los cursos.
int SumarCupos(int[] cupos)
{
    int total = 0;
    for (int i = 0; i < cupos.Length; i++)
        total += cupos[i];
    return total;
}

// Escribe las tres páginas y el PDF de ejemplo, y abre el portal.
void GenerarPagina()
{
    Directory.CreateDirectory(carpeta);
    CrearPdfVacio(Path.Combine(carpeta, "taller.pdf"));

    // Portal: botones originales (no hacen nada) + sección NUEVO
    StringBuilder html = new StringBuilder("<h1>Estudiantes</h1><p class='est'><b>ESTUDIANTE DE PRUEBA - 1000000000 CC</b> " +
        "028 - TECNOLOGÍA EN DESARROLLO DE SOFTWARE (Presencial) | JORNADA: DIURNA</p>");
    for (int i = 0; i < botonesPortal.Length; i++)
    {
        if (i == 0) html.Append("<div class='bar'>RESERVAS</div><div class='grid'>");
        if (i == 3) html.Append("</div><div class='bar'>INFORMACIÓN E INSCRIPCIONES</div><div class='grid'>");
        html.Append($"<span class='btn'><i style='background:{coloresPortal[i]}'></i>{botonesPortal[i]}</span>");
    }
    html.Append("</div><div class='bar nuevo'>NUEVO</div><div class='grid'>" +
                "<a class='btn' href='talleres.html'><i style='background:#e8772e'></i>Clases y talleres</a>" +
                "<a class='btn' href='bienestar.html'><i style='background:#8e5bb5'></i>Bienestar universitario</a></div>");
    File.WriteAllText(Path.Combine(carpeta, "index.html"), Plantilla(html.ToString()));

    // Talleres: cada uno abre el PDF de ejemplo
    html.Clear().Append("<p><a href='index.html'>&larr; Estudiantes</a></p><h1>Clases y talleres</h1><div class='cards'>");
    for (int i = 0; i < tallerTitulo.Length; i++)
        html.Append($"<div class='card'><small>{tallerMateria[i]} · Semana {tallerSemana[i]}</small>" +
                    $"<b>{tallerTitulo[i]}</b><a class='boton' href='taller.pdf' target='_blank'>Abrir PDF</a></div>");
    File.WriteAllText(Path.Combine(carpeta, "talleres.html"), Plantilla(html + "</div>"));

    // Bienestar: el botón Inscribirse es solo visual
    html.Clear().Append("<p><a href='index.html'>&larr; Estudiantes</a></p><h1>Bienestar universitario</h1><div class='cards'>");
    for (int i = 0; i < cursoNombre.Length; i++)
        html.Append($"<div class='card'><small>{cursoCategoria[i]}</small><b>{cursoNombre[i]}</b>" +
                    $"<span>{cursoHorario[i]} · {cursoCupos[i]} cupos</span><button class='boton'>Inscribirse</button></div>");
    File.WriteAllText(Path.Combine(carpeta, "bienestar.html"), Plantilla(html + "</div>"));

    Console.WriteLine($"Página generada en: {carpeta}");
    if (!Console.IsInputRedirected)
        Process.Start(new ProcessStartInfo(Path.Combine(carpeta, "index.html")) { UseShellExecute = true });
}

// Encabezado, menú y estilos comunes (sin imágenes).
string Plantilla(string contenido)
{
    return "<!doctype html><html lang='es'><head><meta charset='utf-8'><title>SICAU Fácil</title><style>" +
        "body{margin:0;font-family:Arial,sans-serif;color:#333}" +
        "header{background:#f2f2f2;padding:16px;text-align:center;font-weight:900;color:#1b2a5c;font-size:28px}" +
        "header span{color:#1a8ad8;margin-left:60px}" +
        "nav{background:#2b3a55;padding:14px;text-align:center}nav a{color:#fff;margin:0 16px;text-decoration:none}" +
        "main{max-width:1100px;margin:auto;padding:0 16px 40px}h1{text-align:center;font-weight:400}.est{text-align:center;font-size:13px}" +
        ".bar{background:#3e86a8;color:#fff;font-weight:bold;text-align:center;padding:7px;margin-top:24px;font-size:14px}.nuevo{background:#e8772e}" +
        ".grid{display:flex;flex-wrap:wrap;justify-content:center;gap:20px;padding:20px 0}" +
        ".btn{width:240px;text-align:center;font-size:14px;color:#333;text-decoration:none}" +
        ".btn i{display:block;width:66px;height:66px;border-radius:50%;margin:0 auto 10px;border:1px solid #ccc}" +
        "a.btn{font-weight:bold}.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px}" +
        ".card{border:1px solid #ddd;border-radius:8px;padding:16px;display:flex;flex-direction:column;gap:6px}" +
        ".card small{color:#3e86a8}.boton{margin-top:8px;background:#e8772e;color:#fff;border:0;border-radius:4px;padding:8px;text-align:center;text-decoration:none;font-size:14px}" +
        "</style></head><body><header>PASCUAL BRAVO <span>SICAU</span></header>" +
        "<nav><a href='#'>Inicio</a><a href='index.html'>Estudiantes</a><a href='#'>Extensión</a></nav><main>" +
        contenido + "</main></body></html>";
}

// Crea un PDF válido de una página en blanco (ejemplo de taller).
void CrearPdfVacio(string ruta)
{
    string[] objetos =
    {
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>"
    };
    StringBuilder pdf = new StringBuilder("%PDF-1.4\n");
    int[] posiciones = new int[objetos.Length];
    for (int i = 0; i < objetos.Length; i++)
    {
        posiciones[i] = pdf.Length;
        pdf.Append($"{i + 1} 0 obj\n{objetos[i]}\nendobj\n");
    }
    int inicioXref = pdf.Length;
    pdf.Append($"xref\n0 {objetos.Length + 1}\n0000000000 65535 f \n");
    for (int i = 0; i < objetos.Length; i++)
        pdf.Append($"{posiciones[i]:D10} 00000 n \n");
    pdf.Append($"trailer\n<< /Size {objetos.Length + 1} /Root 1 0 R >>\nstartxref\n{inicioXref}\n%%EOF\n");
    File.WriteAllText(ruta, pdf.ToString(), Encoding.ASCII);
}
