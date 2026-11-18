# Cómo funciona la fábrica de vídeos de Zona Leonida

1. `./setup.sh` prepara una sesión nueva: instala la voz (Kokoro), genera logo y mascota y enlaza los clips.
2. Se escribe `guiones/AAAA-MM-DD.json` con los vídeos del día (formato en `guiones/EJEMPLO.json`):
   - `id`: nombre corto sin espacios (A_..., B_..., C_...).
   - `fmt`: `"v"` vertical con mascota (Shorts, TikTok, Reels) o `"h"` horizontal (vídeo largo de YouTube).
   - `title`, `thumb` (3 textos de miniatura) y `slides`: cada escena con `lay` (hero, num, stat, list, car),
     `k` (etiqueta), `t` (título en pantalla), `b` (texto de apoyo) y `n` (lo que dice la voz).
3. `./run_day.sh guiones/AAAA-MM-DD.json` fabrica los vídeos en `out/` (cada uno de menos de 95 MB).
4. Los vídeos se suben a la rama `salida`, vidIQ los importa por su enlace directo y la rama se vacía enseguida.
5. `historial.json` guarda los temas ya publicados para no repetirlos.

Música: original, generada por código. Voz: sintética (Kokoro, Apache 2.0). Mascota: Lío, el caimán (diseño original).
Canal de fans, sin relación oficial con Rockstar Games.
