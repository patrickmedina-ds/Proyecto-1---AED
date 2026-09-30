"""
Video educativo: Suffix Tree (CS2023).
La animación NO dibuja nada "a mano": ejecuta el binario C++ (suffix_tree),
lee la traza JSON que produce la estructura real y anima cada paso.
Render:  manim -pqh animacion.py SuffixTreeVideo
"""
import json, subprocess, os
from manim import *

BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "suffix_tree")
AZUL, VERDE, ROJO, AMAR = BLUE_C, GREEN_C, RED_C, YELLOW_C


def traza(texto, *patrones):
    out = subprocess.run([BIN, texto, *patrones], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def layout(tree, ancho=12.0, alto_nivel=1.25, top=2.3):
    """Posiciones: x por orden de hojas, y por profundidad."""
    nodos = {n["id"]: n for n in tree}
    pos, hojas = {}, []

    def dfs(i, d):
        n = nodos[i]
        if not n["children"]:
            hojas.append(i); pos[i] = [None, top - d * alto_nivel]
            return
        for c in n["children"]:
            dfs(c, d + 1)
        pos[i] = [None, top - d * alto_nivel]
    dfs(0, 0)
    k = max(len(hojas), 1)
    for j, h in enumerate(hojas):
        pos[h][0] = -ancho / 2 + ancho * (j + 0.5) / k

    def fijar_x(i):
        n = nodos[i]
        if n["children"]:
            xs = [fijar_x(c) for c in n["children"]]
            pos[i][0] = sum(xs) / len(xs)
        return pos[i][0]
    fijar_x(0)
    return {i: np.array([p[0], p[1], 0]) for i, p in pos.items()}


def dibujar(tree, color_nodos=None):
    """Devuelve dict id -> VGroup(círculo, arista, etiqueta)."""
    color_nodos = color_nodos or {}
    p = layout(tree)
    objs = {}
    for n in tree:
        i = n["id"]
        es_hoja = n["suffix"] >= 0
        c = Circle(0.22, color=color_nodos.get(i, VERDE if es_hoja else AZUL), fill_opacity=0.35).move_to(p[i])
        txt = Text(str(n["suffix"]) if es_hoja else ("R" if i == 0 else ""), font_size=18).move_to(p[i])
        g = VGroup(c, txt)
        if n["parent"] >= 0:
            a, b = p[n["parent"]], p[i]
            linea = Line(a, b, buff=0.22, color=GREY_B)
            lab = Text(n["label"], font_size=20, color=AMAR).move_to((a + b) / 2 + LEFT * 0.35)
            g.add(linea, lab)
        objs[i] = g
    return objs


class SuffixTreeVideo(Scene):
    def mostrar_arbol(self, viejo, tree, colores=None, rt=1.0):
        nuevo = dibujar(tree, colores)
        anims = []
        for i, g in nuevo.items():
            anims.append(Transform(viejo[i], g) if i in viejo else FadeIn(g))
            if i not in viejo:
                viejo[i] = g
        self.play(*anims, run_time=rt)
        return viejo

    def titulo(self, s):
        t = Text(s, font_size=34).to_edge(UP)
        self.play(Write(t))
        return t

    # ---------------- 1. Introducción ----------------
    def intro(self):
        t = Text("Suffix Tree (Árbol de Sufijos)", font_size=48, color=AMAR)
        self.play(Write(t)); self.wait(0.5)
        self.play(t.animate.to_edge(UP).scale(0.7))
        puntos = VGroup(
            Text("• Trie comprimido con TODOS los sufijos de una cadena S$", font_size=26),
            Text("• TDA: Diccionario / Índice de texto (consulta de subcadenas)", font_size=26),
            Text("• Toda subcadena de S es prefijo de algún sufijo", font_size=26),
            Text("• Usos: búsqueda de patrones, bioinformática (ADN),", font_size=26),
            Text("  subcadena repetida más larga, compresión de datos", font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT).next_to(t, DOWN, buff=0.6)
        for p in puntos:
            self.play(FadeIn(p, shift=RIGHT * 0.3), run_time=0.7)
        self.wait(2)
        self.play(FadeOut(VGroup(t, puntos)))

    # ---------------- 2. Construcción ----------------
    def construccion(self, d):
        t = self.titulo(f'Construcción: S = "{d["text"]}"')
        objs, info = {}, None
        for paso in d["steps"]:
            if paso["event"] == "root":
                objs = self.mostrar_arbol(objs, paso["tree"])
                continue
            msg = {"leaf": "no existe arista → nueva hoja",
                   "split": "desajuste en medio de una arista → se PARTE"}[paso["event"]]
            nueva = VGroup(
                Text(f'Insertar sufijo {paso["suffix"]}: "{paso["suffixText"]}"', font_size=26),
                Text(msg, font_size=22, color=ROJO if paso["event"] == "split" else VERDE),
            ).arrange(DOWN).to_edge(DOWN)
            self.play(FadeOut(info) if info else Wait(0.01), FadeIn(nueva)); info = nueva
            colores = {i: AMAR for i in paso["path"]}
            objs = self.mostrar_arbol(objs, paso["tree"], colores)
            self.wait(1)
            objs = self.mostrar_arbol(objs, paso["tree"], rt=0.4)
        self.wait(1.5)
        self.play(FadeOut(info), FadeOut(t))
        return objs, d["steps"][-1]["tree"]

    # ---------------- 3. Búsqueda ----------------
    def busquedas(self, d, objs, tree):
        t = self.titulo("Búsqueda de patrones: O(m + occ)")
        info = None
        for s in d["searches"]:
            colores = {i: (AMAR if s["found"] else ROJO) for i in s["path"]}
            txt = (f'"{s["pattern"]}" encontrado en posiciones {sorted(s["occurrences"])}'
                   if s["found"] else f'"{s["pattern"]}" NO aparece en S')
            nueva = Text(txt, font_size=26, color=VERDE if s["found"] else ROJO).to_edge(DOWN)
            self.play(FadeOut(info) if info else Wait(0.01), FadeIn(nueva)); info = nueva
            for k in range(1, len(s["path"]) + 1):   # recorrido paso a paso
                objs = self.mostrar_arbol(objs, tree, {i: colores[i] for i in s["path"][:k]}, rt=0.5)
            self.wait(1.5)
            objs = self.mostrar_arbol(objs, tree, rt=0.4)
        self.play(FadeOut(VGroup(t, info, *objs.values())))

    # ---------------- 4. Casos borde ----------------
    def casos_borde(self):
        t = self.titulo("Casos borde")
        vacio = traza("", "a")
        sub = Text('Cadena vacía: S = "" → solo el sufijo "$"', font_size=26).to_edge(DOWN)
        self.play(FadeIn(sub))
        objs = self.mostrar_arbol({}, vacio["steps"][-1]["tree"])
        self.wait(2)
        self.play(FadeOut(VGroup(sub, *objs.values())))

        peor = traza("aaaa", "aa")
        sub = Text('Peor caso para la construcción ingenua: S = "aaaa"\n'
                   'cada sufijo recorre todo el camino → O(n²)', font_size=24).to_edge(DOWN)
        self.play(FadeIn(sub))
        objs = {}
        for paso in peor["steps"]:
            objs = self.mostrar_arbol(objs, paso["tree"], {i: AMAR for i in paso["path"]}, rt=0.7)
        self.wait(2)
        self.play(FadeOut(VGroup(t, sub, *objs.values())))

    # ---------------- 5. Complejidad ----------------
    def complejidad(self):
        t = self.titulo("Análisis de complejidad (n = |S|, m = |patrón|)")
        tabla = Table(
            [["Construcción (ingenua, esta impl.)", "O(n²)"],
             ["Construcción (Ukkonen)", "O(n)"],
             ["Búsqueda / existencia", "O(m)"],
             ["Listar ocurrencias", "O(m + occ)"],
             ["Espacio (nodos)", "O(n)  ≤ 2n nodos"]],
            col_labels=[Text("Operación"), Text("Tiempo")],
            include_outer_lines=True).scale(0.5).next_to(t, DOWN, buff=0.5)
        self.play(Create(tabla), run_time=2)
        nota = Text("Clave: la búsqueda no depende de n, solo del patrón.", font_size=24,
                    color=AMAR).to_edge(DOWN)
        self.play(FadeIn(nota)); self.wait(4)
        self.play(FadeOut(VGroup(t, tabla, nota)))

    def construct(self):
        self.intro()
        d = traza("banana", "ana", "nan", "xyz")
        objs, tree = self.construccion(d)
        self.busquedas(d, objs, tree)
        self.casos_borde()
        self.complejidad()
        self.play(Write(Text("Gracias", font_size=48))); self.wait(1)
