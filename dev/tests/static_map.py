#!/usr/bin/env python

# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information
#
# pip install py-staticmaps[cairo]
# si erreur pip install --force-reinstall --no-binary pycairo pycairo
# sudo apt install libcairo2-dev

import staticmaps
import sys

print("Test de génération de carte statique...")
print(f"Python executable: {sys.executable}")

# Diagnostic des imports Cairo pour comprendre l'échec de détection
try:
    import cairo

    print(f"✅ 'import cairo' (pycairo) fonctionne : {cairo}")
except Exception as e:
    print(f"⚠️ 'import cairo' a échoué : {e}")

try:
    import cairocffi

    print(f"✅ 'import cairocffi' fonctionne : {cairocffi}")
except Exception as e:
    print(f"⚠️ 'import cairocffi' a échoué : {e}")

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OSM)

place = staticmaps.create_latlng(float("46.569317"), float("0.346048"))
context.add_object(staticmaps.Marker(place, size=5))

# render png via cairo
if staticmaps.cairo_is_supported():
    print("render png via cairo")
    cairo_image = context.render_cairo(800, 500)
    cairo_image.write_to_png("static_map.cairo2.png")
    print("✅ Image sauvegardée : static_map.cairo2.png")
else:
    print("❌ Erreur : Le support Cairo n'est pas détecté dans py-staticmaps.")
