// Shared arena coordinates; C is the same room translated by (832,13952,-9384).
vec2 SourceArenaOffset(vec2 world)
{
 return world.y>6000.0?vec2(832.0,13952.0):vec2(0.0);
}
vec2 SourceSealCenter(vec2 world)
{
 return SourceArenaOffset(world)+vec2(128.0,-384.0);
}
bool SourceMiniatureBeam(vec2 world)
{
 return world.x>5120.0 && world.x<7808.0 && world.y>-1664.0 && world.y<1536.0;
}
float SourceBeamScale(vec2 world)
{
 // The miniature carrier is only 128 units deep; keep the round helix inside it.
 return SourceMiniatureBeam(world)?60.0/430.0:1.0;
}
vec2 SourceBeamCenter(vec2 world)
{
 if(SourceMiniatureBeam(world))return vec2(6464.0,704.0);
 vec2 offset=SourceArenaOffset(world);
 // CN additionally has the remote upper-shaft carrier used by its stacked view.
 return offset+((world-offset).x>6000.0?vec2(10624.0,-192.0):vec2(130.0,-382.0));
}
float SourceHeight(vec3 world)
{
 // Renderer axes are X,Z,Y; TNT04C's arena floor is 9384 units lower.
 return world.y+(world.z>6000.0?9384.0:0.0);
}
float SourceBeamHeight(vec3 world)
{
 return SourceMiniatureBeam(world.xz)?(world.y-768.0)/SourceBeamScale(world.xz)+3200.0:SourceHeight(world);
}
