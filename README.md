# SURV. NIGHTMARE · resource pack

Pack del servidor: sonidos, ambiente e íconos. Sin texturas nuevas.

- Editar los archivos en `assets/`.
- Publicar: `python build.py --publicar` (arma `dist/SurvNightmare.zip`, pone su SHA-1 en la config del plugin Terror y lo sube a GitHub). Después `/terror reload` en el server.
- El server lo descarga de https://raw.githubusercontent.com/lucianodivito/survnightmare-pack/main/dist/SurvNightmare.zip

Contenido:
- `textures/gui/sprites/boss_bar/pink_*`: transparentes. La barra rosa es la de la niebla de todas las noches: así no se ve.
- `shaders/core/lightmap.fsh`: con las barras de niebla del server (señal: `BossOverlayWorldDarkeningFactor`) la noche es más oscura y el brillo al máximo no la arregla. Ajustes: `NIGHT_SKY`, `NIGHT_AMBIENT`, `NIGHT_GAMMA`.
- `shaders/include/fog.glsl`: con esas barras, la niebla pasa de 10-96 bloques (vanilla) a 2-30 y se aclara un poco (bruma). Ajustes: `THICK_START`, `THICK_END`, `MIST`, `MIST_MIX`.
- `assets/terror/sounds.json` y `assets/terror/sounds/`: sonidos propios (ogg mono). Eventos `terror:susto`, `sabueso.aullido`, `sabueso.ladrido`, `susurro`, `detras` (el "behind you", solo el Acechador), `respiracion`, `criatura`, `lamento`, `risa`, `huesos`, `golpe`, `luna.inicio`, `luna.ambiente`. En el plugin: `world/Sounds`. De dónde salió cada uno: `CREDITOS.md`.
- `assets/minecraft/sounds.json`: **sin música**. Las 32 músicas del juego (`music.*`, menos los discos) suenan como un segundo de silencio (`terror:silencio`). El terror se apoya en el silencio y en los sonidos de ambiente.
- `assets/minecraft/font/default.json` + `assets/terror/textures/font/`: íconos en lugar de símbolos, en todo el juego (chat, scoreboard, menús): ✦ Esencia = llama de alma, ⛃ dinero = pepita de oro, ♛ habilidad estrella = corona (pixel art propio, en grises para que la tiña el color del texto), ☠ = alma que grita. Reusan texturas del juego.
- `textures/gui/sprites/boss_bar/red_*`: barra roja propia (Luna de Sangre): fondo casi negro, sangre con gotas. Ojo: las incursiones de aldeanos también usan la barra roja.
- `shaders/core/stars.fsh`: cielo sin estrellas.
- `textures/environment/celestial/moon/`: luna pálida y enferma (las fases del juego, recoloreadas y con manchas).
- `assets/minecraft/sounds.json` → `ambient.cave`: al ambiente de cueva del juego se le suman susurros, respiraciones, huesos, una criatura y un lamento (no se reemplaza nada).
- `assets/terror/font/menu.json` + `textures/gui/menu.png`: fondo oscuro del menú /habilidades (el cofre de 6 filas recoloreado en grises oscuros parejos, sin contraste fuerte). Va en el título del cofre: espacio -8, la imagen (ascent 13, alto 222) y espacio -169 para volver a donde empieza el texto.
- `textures/gui/container/**`: **todos los inventarios** (cofres, hornos, mesa de trabajo, yunque, aldeanos, inventario propio, creativo, etc.) en los mismos grises oscuros que el menú. Solo se cambian los grises puros; flechas, llamas y demás colores quedan.
- `shaders/core/text.fsh`: en los inventarios, el texto gris oscuro del juego (0x404040: "Inventario", "Cofre"...) pasa a gris claro para que se lea sobre el fondo oscuro.
- `assets/terror/font/menu.json` → `\ue001`: la calavera del título del menú, más grande (12 px).
- Los gritos (`sounds/susto/`) están recortados para que griten de entrada: sin silencio inicial (umbral -26 dB) y a `sus1` además se le sacan los primeros 0,45 s, que eran una subida lenta. Si se regeneran con el script de conversión, repetir el recorte.
