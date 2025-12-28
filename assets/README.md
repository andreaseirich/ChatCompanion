# Assets

Dieses Verzeichnis enthält Logo- und Icon-Dateien für ChatCompanion.

## Logo

- `logo.svg` - Hauptlogo als skalierbares SVG

Das Logo wird automatisch in der Streamlit-UI angezeigt.

## Icon für Executable

Für PyInstaller-Builds können Sie ein Icon erstellen:

### macOS (ICNS)
```bash
# Erstellen Sie ein ICNS aus dem SVG (benötigt sips oder ein Tool wie iconutil)
# Oder verwenden Sie ein Online-Tool wie https://cloudconvert.com/svg-to-icns
```

### Windows (ICO)
```bash
# Erstellen Sie ein ICO aus dem SVG
# Verwenden Sie ein Tool wie https://cloudconvert.com/svg-to-ico
# Oder ImageMagick: convert logo.svg -resize 256x256 logo.ico
```

### Hinweis
PyInstaller unterstützt SVG nicht direkt als Icon. Für beste Ergebnisse:
1. Konvertieren Sie `logo.svg` zu `icon.ico` (Windows) oder `icon.icns` (macOS)
2. Aktualisieren Sie `scripts/build_executable.py` Zeile 114, um den Pfad zum Icon anzugeben

