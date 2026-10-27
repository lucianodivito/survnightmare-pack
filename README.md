# SURV. NIGHTMARE · resource pack

Pack del servidor: sonidos, ambiente e íconos. Sin texturas nuevas.

- Editar los archivos en `assets/`.
- Publicar: `python build.py --publicar` (arma `dist/SurvNightmare.zip`, pone su SHA-1 en la config del plugin Terror y lo sube a GitHub). Después `/terror reload` en el server.
- El server lo descarga de https://raw.githubusercontent.com/lucianodivito/survnightmare-pack/main/dist/SurvNightmare.zip

Contenido:
- `textures/gui/sprites/boss_bar/pink_*`: transparentes. La barra rosa es la de la niebla de todas las noches: así no se ve.
- `shaders/core/lightmap.fsh`: con las barras de niebla del server (señal: `BossOverlayWorldDarkeningFactor`) la noche es más oscura y el brillo al máximo no la arregla. Ajustes: `NIGHT_SKY`, `NIGHT_AMBIENT`, `NIGHT_GAMMA`.
- `shaders/include/fog.glsl`: con esas barras, la niebla pasa de 10-96 bloques (vanilla) a 2-30 y se aclara un poco (bruma). Ajustes: `THICK_START`, `THICK_END`, `MIST`, `MIST_MIX`.
- `assets/terror/sounds.json` y `assets/terror/sounds/`: sonidos propios (ogg mono). Eventos `terror:susto`, `sabueso.aullido`, `sabueso.ladrido`, `susurro`, `respiracion`, `criatura`, `lamento`, `risa`, `huesos`, `golpe`, `luna.inicio`, `luna.ambiente`. En el plugin: `world/Sounds`. De dónde salió cada uno: `CREDITOS.md`.
