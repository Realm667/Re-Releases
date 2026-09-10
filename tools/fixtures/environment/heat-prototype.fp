void main()
{
 vec2 q=(TexCoord-focus)/max(extent,vec2(.001));
 float edge=1.0-smoothstep(.55,1.0,length(q));
 float amplitude=.006*edge;
 vec2 shift=vec2(sin(TexCoord.y*95.0+InputTimeGame*1.7),sin(TexCoord.x*61.0-InputTimeGame*.9)*.3)*amplitude;
 FragColor=texture(InputTexture,clamp(TexCoord+shift,vec2(.001),vec2(.999)));
}
