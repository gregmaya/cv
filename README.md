# CV web · gregmaya.github.io/cv

Página del CV pensada para el móvil, con el PDF original para descargar y seguimiento de visitas por destinatario.

## Archivos
- `index.html`: la página completa (estilos y scripts incluidos).
- `Gregorio-Maya-CV.pdf`: el PDF que baja el botón "Descargar PDF". Se sirve tal cual.
- `og-cv-2.png`: la imagen de la tarjeta de vista previa en WhatsApp/LinkedIn.

## Seguimiento
Cada envío lleva un código: `https://gregmaya.github.io/cv/?r=k7`.
Los códigos y a quién se asignó cada uno viven en la hoja de Google "CV · Códigos de seguimiento"
(y en la mini app de Apps Script que la rellena desde el móvil). Los códigos que empiezan por `t` son pruebas.

La analítica es GoatCounter, sin cookies: https://gregmaya.goatcounter.com

Rutas que registra la página:

| Ruta | Qué significa |
|---|---|
| `cv/r/k7` | alguien abrió la página con el código `k7` |
| `cv/sin-codigo` | visita sin código (LinkedIn, URL escrita a mano…) |
| `pdf/r/k7` | descarga del PDF con ese código |
| `whatsapp/r/k7`, `email/r/k7`, `linkedin/r/k7`, `github/r/k7` | clic en ese botón de contacto |

Las rutas de visita se guardan con barra inicial (`/cv/r/k7`) y los clics sin ella (`pdf/r/k7`).

### Mantenimiento en GoatCounter
- **No contar tus propios dispositivos:** abre una vez en cada uno (portátil, móvil)
  `https://gregmaya.github.io/cv/#toggle-goatcounter`. Hay que repetirlo si borras los datos del navegador.
- **Borrar pruebas o resetear:** Settings → *Manage pageviews*. Filtra por `/r/t` para borrar todas las pruebas,
  o borra ruta por ruta.

## Analizar los datos (en la misma hoja de códigos)
1. En GoatCounter: Settings → *Export* → descarga el CSV (llega por correo o como descarga).
2. En la hoja de códigos: Archivo → Importar → sube el CSV → *Insertar hojas nuevas*. Renombra la pestaña a `Visitas`.
   Comprueba en qué columnas quedaron `Path`, `Location` y `Date`; abajo se asume B, M y O.
3. En la pestaña de códigos añade estas columnas (fila 2, luego arrastra hacia abajo):

| Columna | Fórmula |
|---|---|
| Visitas | `=COUNTIF(Visitas!B:B, "/cv/r/"&A2)` |
| PDF | `=COUNTIF(Visitas!B:B, "pdf/r/"&A2)` |
| Contactos | `=COUNTIF(Visitas!B:B, "whatsapp/r/"&A2)+COUNTIF(Visitas!B:B, "email/r/"&A2)+COUNTIF(Visitas!B:B, "linkedin/r/"&A2)` |
| Países | `=IFERROR(TEXTJOIN(", ", TRUE, UNIQUE(FILTER(Visitas!M:M, Visitas!B:B="/cv/r/"&A2))), "")` |
| Primera apertura | `=IFERROR(LEFT(SORT(FILTER(Visitas!O:O, Visitas!B:B="/cv/r/"&A2)), 10), "")` |

4. Para una vista rápida: filtra la columna Visitas por "mayor que 0", o crea un gráfico de barras
   de Visitas por Persona (Insertar → Gráfico).

Cómo leerlo:
- **Visitas > 0:** la persona abrió el enlace.
- **PDF > 0:** además lo descargó, una señal fuerte de interés.
- **Más de un país, o visitas días después del envío:** probablemente lo reenvió.

Cada vez que quieras actualizar, exporta de nuevo y reemplaza la pestaña `Visitas`; las fórmulas se recalculan solas.

## Actualizar el CV
- El texto se cambia en `index.html`; el PDF se reemplaza subiendo la nueva versión con el mismo nombre.
  Son independientes: si cambias uno, revisa el otro.
- WhatsApp guarda en caché la imagen de vista previa. Si la cambias, súbela con un nombre nuevo
  (p. ej. `og-cv-3.png`) y actualiza `og:image` y `og:image:secure_url` en `index.html`.
- Si un despliegue de Pages falla con `startup_failure`, es un fallo de GitHub: vuelve a lanzarlo
  o sube un commit vacío.
