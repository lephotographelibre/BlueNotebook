import sys

import gpxpy
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OSM)

with open(sys.argv[1], "r") as file:
    gpx = gpxpy.parse(file)

for track in gpx.tracks:
    for segment in track.segments:
        line = [
            staticmaps.create_latlng(p.latitude, p.longitude) for p in segment.points
        ]
        context.add_object(staticmaps.Line(line))

for p in gpx.walk(only_points=True):
    pos = staticmaps.create_latlng(p.latitude, p.longitude)
    marker = staticmaps.ImageMarker(pos, "start.png", origin_x=27, origin_y=35)
    context.add_object(marker)
    break

# render non-anti-aliased png
# image = context.render_pillow(800, 500)
# image.save("draw_gpx.pillow.png")

# render anti-aliased png (this only works if pycairo is installed)
image = context.render_cairo(800, 500)
image.write_to_png("draw_gpx.cairo.png")
