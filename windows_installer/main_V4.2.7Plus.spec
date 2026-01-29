# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_data_files, copy_metadata

block_cipher = None

# 1. Collecte automatique pour pyphen
datas_pyphen = collect_data_files('pyphen')

# 2. Collecte complète pour pymdownx
# On récupère tout : sources, données, binaires, imports cachés
pymdownx_ret = collect_all('pymdownx')
datas_pymdownx = pymdownx_ret[0]
binaries_pymdownx = pymdownx_ret[1]
hiddenimports_pymdownx = pymdownx_ret[2]

# AJOUT CRITIQUE : Copie des métadonnées du package pip
# Cela permet à pkg_resources de trouver la version de pymdown-extensions
datas_pymdownx += copy_metadata('pymdown-extensions')

# 3. Vos ressources manuelles
my_datas = [
    ('resources', 'resources'),
    ('i18n', 'i18n'),
]

# Fusion des listes de données
all_datas = datas_pyphen + datas_pymdownx + my_datas

# 4. Liste explicite des imports cachés (Ceinture et bretelles)
# On force l'inclusion des modules que vous utilisez dans preview.py
explicit_hiddenimports = [
    'PyQt5.QtPrintSupport',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtNetwork',
    'PyQt5.QtXml',
    'PyQt5.QtSvg',
    'weasyprint',
    'cairosvg',
    'pyphen',
    'markdown',
    'ebooklib',
    'fitz',
    # Modules pymdownx spécifiques
    'pymdownx',
    'pymdownx.tilde',
    'pymdownx.mark',
    'pymdownx.superfences',
    'pymdownx.tasklist',
    'pymdownx.emoji',
    'pymdownx.highlight',
    'pymdownx.inlinehilite',
    'pymdownx.magiclink',
    'pymdownx.saneheaders',
    'pymdownx.smartsymbols',
    'pymdownx.snippets',
    'pymdownx.keys',
    'pymdownx.details',
    'pymdownx.arithmatex',
    'pymdownx.betterem',
    'pymdownx.caret',
    'pymdownx.critic',
    'pymdownx.escapeall',
    'pymdownx.extra',
    'pymdownx.progressbar',
    'pymdownx.striphtml',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('resources/dll/*.dll', '.')] + binaries_pymdownx,
    datas=all_datas,
    hiddenimports=explicit_hiddenimports + hiddenimports_pymdownx,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BlueNotebook',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Gardez True pour voir si l'erreur change
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/bluenotebook.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BlueNotebook',
)
