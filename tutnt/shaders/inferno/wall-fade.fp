// True alpha fade on the lower wall models, below the map's visual-only floor.
void SetupMaterial(inout Material mat) {
 mat.Base=getTexel(vTexCoord.st);
 float wave=sin(pixelpos.x*.051+pixelpos.z*.039)*3.+sin(pixelpos.x*.023-pixelpos.z*.047)*2.;
 mat.Base.a*=smoothstep(-222.,-140.,pixelpos.y+wave);
 mat.Normal=normalize(vWorldNormal.xyz);
}
