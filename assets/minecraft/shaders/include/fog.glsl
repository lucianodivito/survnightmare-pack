#version 330

layout(std140) uniform Fog {
    vec4 FogColor;
    float FogEnvironmentalStart;
    float FogEnvironmentalEnd;
    float FogRenderDistanceStart;
    float FogRenderDistanceEnd;
    float FogSkyEnd;
    float FogCloudsEnd;
};

float linear_fog_value(float vertexDistance, float fogStart, float fogEnd) {
    if (vertexDistance <= fogStart) {
        return 0.0;
    } else if (vertexDistance >= fogEnd) {
        return 1.0;
    }

    return (vertexDistance - fogStart) / (fogEnd - fogStart);
}

float total_fog_value(float sphericalVertexDistance, float cylindricalVertexDistance, float environmentalStart, float environmantalEnd, float renderDistanceStart, float renderDistanceEnd) {
    return max(linear_fog_value(sphericalVertexDistance, environmentalStart, environmantalEnd), linear_fog_value(cylindricalVertexDistance, renderDistanceStart, renderDistanceEnd));
}

// SURV. NIGHTMARE: niebla espesa cuando hay una barra de jefe con niebla (la de todas las noches, el banco de niebla
// y la Luna de Sangre). El juego, con esa barra, deja la niebla entre 10 y 96 bloques (casi no se nota) y pone el
// fin del cielo y de las nubes igual que el de la niebla: asi la reconocemos y la acercamos mucho.
const float THICK_START = 2.0;               // desde donde empieza la niebla (bloques)
const float THICK_END = 30.0;                // donde ya no se ve nada
const vec3 MIST = vec3(0.55, 0.57, 0.60);    // gris de bruma
const float MIST_MIX = 0.25;                 // cuanto gris se le mezcla al color de la niebla

bool terror_boss_fog() {
    return FogEnvironmentalStart >= 0.0 && FogEnvironmentalStart <= 10.01
        && abs(FogEnvironmentalEnd - 96.0) < 0.01
        && abs(FogSkyEnd - FogEnvironmentalEnd) < 0.01
        && abs(FogCloudsEnd - FogEnvironmentalEnd) < 0.01;
}

vec4 apply_fog(vec4 inColor, float sphericalVertexDistance, float cylindricalVertexDistance, float environmentalStart, float environmantalEnd, float renderDistanceStart, float renderDistanceEnd, vec4 fogColor) {
    if (terror_boss_fog()) {
        environmentalStart = THICK_START;
        environmantalEnd = THICK_END;
        fogColor = vec4(mix(fogColor.rgb, MIST, MIST_MIX), fogColor.a);
    }
    float fogValue = total_fog_value(sphericalVertexDistance, cylindricalVertexDistance, environmentalStart, environmantalEnd, renderDistanceStart, renderDistanceEnd);
    return vec4(mix(inColor.rgb, fogColor.rgb, fogValue * fogColor.a), inColor.a);
}

float fog_spherical_distance(vec3 pos) {
    return length(pos);
}

float fog_cylindrical_distance(vec3 pos) {
    float distXZ = length(pos.xz);
    float distY = abs(pos.y);
    return max(distXZ, distY);
}
