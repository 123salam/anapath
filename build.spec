# build.spec
block_cipher = None

a = Analysis(
    ['run.py'],  # Utiliser le wrapper, pas app.py directement
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pandas', 'numpy', 'streamlit', 'altair', 'pyarrow'  # Modules souvent nécessaires
    ],
    hookspath=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    name='MonAppStreamlit',  # Nom du .exe
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compression (optionnel)
    runtime_tmpdir=None,
    console=True,  # Afficher la console (utile pour les logs)
    icon='icon.ico'  # Optionnel : chemin vers une icône
)