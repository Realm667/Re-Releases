// https://www.shadertoy.com/view/Mls3DH

const float speed		= 0.0035;
const float frequency	= 8.0;

vec2 shift(vec2 p)
{
	float d = timer * speed;
	vec2 f = frequency * (p + d);
	vec2 q = cos(vec2(cos(f.x - f.y) * cos(f.y), sin(f.x + f.y) * sin(f.y)));
	return q;
}

void main(void)
{
	vec2 texSize = vec2(textureSize(InputTexture, 0));
	vec2 r = TexCoord;
	vec2 p = shift(r);
	vec2 q = shift(r + 1.0);
	float amplitude = (texSize.x * 0.025) / texSize.x;
	vec2 s = r + amplitude * (p - q);
	FragColor = vec4(texture(InputTexture, s));
}
