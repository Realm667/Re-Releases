// Distance Fade
// (C) 2020 Nash Muhandes
vec4 Process(vec4 color)
{
	vec2 uv = gl_TexCoord[0].st;
	vec4 c = getTexel(uv) * color;
	float maxDist = 150.0;
	float dist = pixelpos.w;
	c.a *= (1.0 - (maxDist / dist));
	return c;
}
