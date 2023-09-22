//===========================================================================
//
// Quake-style Water Shader
// Written by Jason Allen Doucette
// Source: https://www.shadertoy.com/view/MsKXzD
//
//===========================================================================

#define WARPSPEED 2.0

// the amount of shearing (shifting of a single column or row)
// 1.0 = entire screen height offset (to both sides, meaning it's 2.0 in total)
#define XDISTMAG 0.05
#define YDISTMAG 0.05

// cycle multiplier for a given screen height
// 2 * PI = you see a complete sine wave from top .. bottom
#define XSINECYCLES 6.28
#define YSINECYCLES 6.28

void SetupMaterial(inout Material mat)
{
	vec2 texCoord = vTexCoord.st;

	// the value for the sine has 2 inputs:
	// 1. the time, so that it animates.
	// 2. the y-row, so that ALL scanlines do not distort equally.
	float time = timer * WARPSPEED;
	float xAngle = time + texCoord.y * YSINECYCLES;
	float yAngle = time + texCoord.x * XSINECYCLES;

	vec2 distortOffset =
		vec2(sin(xAngle), sin(yAngle)) *	// amount of shearing
		vec2(XDISTMAG, YDISTMAG);			// magnitude adjustment

	// shear the coordinates
	texCoord += distortOffset;

	mat.Base = getTexel(texCoord);
	mat.Normal = ApplyNormalMap(texCoord);

#if defined(SPECULAR)
	mat.Specular = texture(speculartexture, texCoord).rgb;
	mat.Glossiness = uSpecularMaterial.x;
	mat.SpecularLevel = uSpecularMaterial.y;
#endif
#if defined(PBR)
	mat.Metallic = texture(metallictexture, texCoord).r;
	mat.Roughness = texture(roughnesstexture, texCoord).r;
	mat.AO = texture(aotexture, texCoord).r;
#endif
	mat.Bright = texture(brighttexture, texCoord);
}
