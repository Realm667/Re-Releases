// Shared arena coordinates; C is the same room translated by (832,13952,-9384).
vec2 SourceArenaOffset(vec2 world)
{
 return world.y>6000.0?vec2(832.0,13952.0):vec2(0.0);
}
vec2 SourceSealCenter(vec2 world)
{
 return SourceArenaOffset(world)+vec2(128.0,-384.0);
}
vec2 SourceBeamCenter(vec2 world)
{
 vec2 offset=SourceArenaOffset(world);
 // CN additionally has the remote upper-shaft carrier used by its stacked view.
 return offset+((world-offset).x>6000.0?vec2(10624.0,-192.0):vec2(130.0,-382.0));
}
float SourceHeight(vec3 world)
{
 // Renderer axes are X,Z,Y; TNT04C's arena floor is 9384 units lower.
 return world.y+(world.z>6000.0?9384.0:0.0);
}
