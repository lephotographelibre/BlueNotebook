 #!/usr/bin/env python

    # py-staticmaps
    # Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information
    #
    # pip install py-staticmaps[cairo]
    # sudo apt install libcairo2-dev
 
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OSM)

place = staticmaps.create_latlng(float("46.569317"), float("0.346048"))
context.add_object(staticmaps.Marker(place, size=5))

# render png via cairo
if staticmaps.cairo_is_supported():
    cairo_image = context.render_cairo(800, 500)
    cairo_image.write_to_png("static_map.cairo.png")

 

 