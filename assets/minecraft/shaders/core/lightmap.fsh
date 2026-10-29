#version 330

layout(std140) uniform LightmapInfo {
    float SkyFactor;
    float BlockFactor;
    float NightVisionFactor;
    float DarknessScale;
    float BossOverlayWorldDarkeningFactor;
    float BrightnessFactor;
    vec3 BlockLightTint;
    vec3 SkyLightColor;
    vec3 AmbientColor;
    vec3 NightVisionColor;
} lightmapInfo;

in vec2 texCoord;

out vec4 fragColor;

float get_brightness(float level) {
    return level / (4.0 - 3.0 * level);
}

vec3 notGamma(vec3 color) {
    float maxComponent = max(max(color.x, color.y), color.z);
    float maxInverted = 1.0f - maxComponent;
    float maxScaled = 1.0f - maxInverted * maxInverted * maxInverted * maxInverted;
    return color * (maxScaled / maxComponent);
}

float parabolicMixFactor(float level) {
    return (2.0 * level - 1.0) * (2.0 * level - 1.0);
}

// SURV. NIGHTMARE: las barras de jefe del server (niebla de todas las noches, banco de niebla, Luna de Sangre)
// oscurecen el mundo. Usamos esa senal (BossOverlayWorldDarkeningFactor) para que la noche sea oscura de verdad:
// casi nada de luz del cielo ni de luz ambiente, y sin que el brillo al maximo lo arregle. Las antorchas y demas
// luces de bloque siguen alumbrando igual. Sin esas barras (de dia, en cuevas sin barra), todo queda como vanilla.
const float NIGHT_SKY = 0.6;         // cuanto queda de la luz del cielo (luna)
const float NIGHT_AMBIENT = 0.5;    // cuanto queda de la luz ambiente minima
const float NIGHT_GAMMA = 0.45;      // cuanto queda del efecto del brillo de las opciones
// La vision nocturna (habilidad o pocion) con el mundo oscurecido: penumbra, no dia. Se ven formas, no colores.
const float NIGHT_VISION_DARK = 0.35;

void main() {
    float boss = lightmapInfo.BossOverlayWorldDarkeningFactor;
    // Calculate block and sky brightness levels based on texture coordinates
    float block_level = floor(texCoord.x * 16) / 15;
    float sky_level = floor(texCoord.y * 16) / 15;

    float block_brightness = get_brightness(block_level) * lightmapInfo.BlockFactor;
    float sky_brightness = get_brightness(sky_level) * lightmapInfo.SkyFactor * mix(1.0, NIGHT_SKY, boss);

    // Calculate ambient color with or without night vision
    vec3 nightVisionColor = lightmapInfo.NightVisionColor * lightmapInfo.NightVisionFactor * mix(1.0, NIGHT_VISION_DARK, boss);
    vec3 color = max(lightmapInfo.AmbientColor * mix(1.0, NIGHT_AMBIENT, boss), nightVisionColor);

    // Add sky light
    color += lightmapInfo.SkyLightColor * sky_brightness;

    // Add block light
    vec3 BlockLightColor = mix(lightmapInfo.BlockLightTint, vec3(1.0), 0.9 * parabolicMixFactor(block_level));
    color += BlockLightColor * block_brightness;

    // Apply boss overlay darkening effect
    color = mix(color, color * vec3(0.7, 0.6, 0.6), lightmapInfo.BossOverlayWorldDarkeningFactor);

    // Apply darkness effect scale
    color = color - vec3(lightmapInfo.DarknessScale);

    // Apply brightness
    color = clamp(color, 0.0, 1.0);
    vec3 notGamma = notGamma(color);
    // El brillo nunca pasa del maximo del menu (1.0): editar options.txt con "gamma:100" ya no hace de dia la noche
    float gamma = clamp(lightmapInfo.BrightnessFactor, 0.0, 1.0);
    color = mix(color, notGamma, gamma * mix(1.0, NIGHT_GAMMA, boss));

    fragColor = vec4(color, 1.0);
}
