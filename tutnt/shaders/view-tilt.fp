void main()
{
    vec2 size=vec2(textureSize(InputTexture,0));
    float aspect=size.x/max(size.y,1.0);
    float angle=radians(clamp(tiltDegrees,-2.0,2.0));
    float c=cos(angle),s=sin(angle);
    // Fit the rotated view inside its source to prevent exposed black corners.
    float zoom=abs(c)+abs(s)*max(aspect,1.0/aspect);
    vec2 p=(TexCoord-0.5)*vec2(aspect,1.0)/zoom;
    p=mat2(c,-s,s,c)*p;
    FragColor=texture(InputTexture,p/vec2(aspect,1.0)+0.5);
}
