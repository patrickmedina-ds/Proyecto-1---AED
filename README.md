# Proyecto Final 1 – Suffix Tree (CS2023)

## Archivos
- `suffix_tree.cpp`: implementación propia del árbol de sufijos (C++17). Genera una traza JSON de cada paso.
- `animacion.py`: video en Manim. Ejecuta el binario y anima la traza (animación dirigida por la estructura real).

## Reproducir el video
```bash
g++ -std=c++17 -O2 suffix_tree.cpp -o suffix_tree      # Windows: suffix_tree.exe (ajustar BIN en animacion.py)
pip install manim                                        # requiere ffmpeg y LaTeX opcional
manim -pqh animacion.py SuffixTreeVideo                  # salida: media/videos/animacion/1080p60/SuffixTreeVideo.mp4
```
Prueba rápida de la estructura sola:
```bash
./suffix_tree banana ana nan xyz
```

## Contenido del video (~4-5 min)
1. Introducción: qué es, TDA (índice de texto / diccionario de subcadenas), usos.
2. Construcción de `banana$` sufijo por sufijo (casos "hoja nueva" y "partir arista").
3. Búsquedas: `ana` (posiciones 1 y 3), `nan` (2), `xyz` (no existe).
4. Casos borde: cadena vacía y peor caso `aaaa` (O(n²) en construcción ingenua).
5. Tabla de complejidad.
