"""Primitivas de desenho vetorial (reportlab) usadas nos diagramas UML.

Coordenadas dos diagramas: origem no canto superior esquerdo, y crescendo para baixo.
"""
import math

from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable

FONT_DIR = "/System/Library/Fonts/Supplemental/"
for _name, _file in [("Arial", "Arial.ttf"), ("Arial-Bold", "Arial Bold.ttf"),
                     ("Arial-Italic", "Arial Italic.ttf"), ("Mono", "Courier New.ttf")]:
    pdfmetrics.registerFont(TTFont(_name, FONT_DIR + _file))

pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic", boldItalic="Arial-Bold")

F, FB, FI, FM = "Arial", "Arial-Bold", "Arial-Italic", "Mono"

INK = colors.HexColor("#1f2933")
GRID = colors.HexColor("#9aa5b1")
IMPL_FILL = colors.HexColor("#e3f4ea")     # implementado na Sprint 2
IMPL_LINE = colors.HexColor("#2f855a")
PART_FILL = colors.HexColor("#fff4d6")     # parcialmente implementado
PART_LINE = colors.HexColor("#b7791f")
PLAN_FILL = colors.white                   # previsto (Sprint 3)
PLAN_LINE = colors.HexColor("#52606d")
LAYER_FILL = colors.HexColor("#f5f7fa")

STATUS_STYLE = {
    "impl": (IMPL_FILL, IMPL_LINE, None),
    "parcial": (PART_FILL, PART_LINE, None),
    "plan": (PLAN_FILL, PLAN_LINE, (3, 2)),
}


class Diagrama(Flowable):
    """Flowable com origem no topo esquerdo; subclasses implementam desenhar()."""

    def __init__(self, largura, altura, esc=1.0):
        super().__init__()
        self.w0, self.h0, self.esc = largura, altura, esc
        self.width, self.height = largura * esc, altura * esc
        self.c = None

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        self.c = self.canv
        self.c.saveState()
        self.c.translate(0, self.height)
        self.c.scale(self.esc, -self.esc)
        self.desenhar()
        self.c.restoreState()

    # ---- texto (a escala y=-1 exige espelhar o texto) -------------------
    def texto(self, x, y, s, fonte=F, tam=7, cor=INK, alinh="l"):
        c = self.c
        c.saveState()
        c.translate(x, y)
        c.scale(1, -1)
        c.setFont(fonte, tam)
        c.setFillColor(cor)
        if alinh == "c":
            c.drawCentredString(0, 0, s)
        elif alinh == "r":
            c.drawRightString(0, 0, s)
        else:
            c.drawString(0, 0, s)
        c.restoreState()

    def largura_texto(self, s, fonte=F, tam=7):
        return pdfmetrics.stringWidth(s, fonte, tam)

    # ---- formas -------------------------------------------------------------
    def estilo(self, linha=INK, preench=None, larg=0.8, tracejado=None):
        c = self.c
        c.setStrokeColor(linha)
        c.setLineWidth(larg)
        c.setDash(*tracejado) if tracejado else c.setDash([])
        if preench is not None:
            c.setFillColor(preench)

    def retangulo(self, x, y, w, h, status=None, raio=0, linha=None, preench=None, larg=0.8):
        fill, line, dash = (preench, linha or INK, None)
        if status:
            fill, line, dash = STATUS_STYLE[status]
        self.estilo(line, fill, larg, dash)
        if raio:
            self.c.roundRect(x, y, w, h, raio, stroke=1, fill=1 if fill is not None else 0)
        else:
            self.c.rect(x, y, w, h, stroke=1, fill=1 if fill is not None else 0)
        self.c.setDash([])

    def elipse(self, cx, cy, rx, ry, status="plan"):
        fill, line, dash = STATUS_STYLE[status]
        self.estilo(line, fill, 0.8, dash)
        self.c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, stroke=1, fill=1)
        self.c.setDash([])

    def linha(self, pts, tracejado=False, cor=INK, larg=0.8):
        c = self.c
        c.setStrokeColor(cor)
        c.setLineWidth(larg)
        c.setDash(3, 2) if tracejado else c.setDash([])
        p = c.beginPath()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        c.drawPath(p, stroke=1, fill=0)
        c.setDash([])

    # ---- pontas de seta -----------------------------------------------------
    def _base(self, ponta, de):
        ang = math.atan2(ponta[1] - de[1], ponta[0] - de[0])
        return ang

    def seta_aberta(self, ponta, de, tam=6, cor=INK):
        a = self._base(ponta, de)
        for d in (0.45, -0.45):
            self.linha([ponta, (ponta[0] - tam * math.cos(a - d), ponta[1] - tam * math.sin(a - d))], cor=cor)

    def triangulo_vazio(self, ponta, de, tam=8):
        a = self._base(ponta, de)
        p1 = (ponta[0] - tam * math.cos(a - 0.4), ponta[1] - tam * math.sin(a - 0.4))
        p2 = (ponta[0] - tam * math.cos(a + 0.4), ponta[1] - tam * math.sin(a + 0.4))
        self._poligono([ponta, p1, p2], colors.white)

    def losango(self, ponta, de, cheio, tam=9):
        a = self._base(ponta, de)
        m = (ponta[0] - tam * math.cos(a), ponta[1] - tam * math.sin(a))
        l1 = (ponta[0] - tam / 2 * math.cos(a) - 3.2 * math.sin(a), ponta[1] - tam / 2 * math.sin(a) + 3.2 * math.cos(a))
        l2 = (ponta[0] - tam / 2 * math.cos(a) + 3.2 * math.sin(a), ponta[1] - tam / 2 * math.sin(a) - 3.2 * math.cos(a))
        self._poligono([ponta, l1, m, l2], INK if cheio else colors.white)

    def _poligono(self, pts, preench):
        c = self.c
        c.setStrokeColor(INK)
        c.setFillColor(preench)
        c.setLineWidth(0.8)
        c.setDash([])
        p = c.beginPath()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.close()
        c.drawPath(p, stroke=1, fill=1)

    def rotulo(self, x, y, s, tam=6.2, alinh="c", fonte=FI):
        w = self.largura_texto(s, fonte, tam)
        bx = x - w / 2 if alinh == "c" else (x if alinh == "l" else x - w)
        self.c.setFillColor(colors.white)
        self.c.setStrokeColor(colors.white)
        self.c.rect(bx - 1.5, y - tam + 0.5, w + 3, tam + 1.5, stroke=0, fill=1)
        self.texto(x, y, s, fonte, tam, INK, alinh)

    # ---- elementos UML --------------------------------------------------------
    def classe(self, x, y, w, nome, atrib=(), metodos=(), estereotipo=None, status="plan",
               abstrata=False, tam=6.6, nota_nome=None):
        lh = tam + 2.4
        h = 6
        if estereotipo:
            h += lh
        h += lh + 3
        h += (len(atrib) * lh + 4) if atrib else 4
        if metodos:
            h += len(metodos) * lh + 4
        self.retangulo(x, y, w, h, status)
        cy = y + 3
        if estereotipo:
            cy += lh - 1
            self.texto(x + w / 2, cy, "«%s»" % estereotipo, F, tam - 0.4, INK, "c")
        cy += lh - (0 if not estereotipo else 1)
        self.texto(x + w / 2, cy, nome, FB if not abstrata else "Arial-Bold", tam + 0.4, INK, "c")
        cy += 3
        self.linha([(x, cy), (x + w, cy)])
        for a in atrib:
            cy += lh
            self.texto(x + 3, cy, a, F, tam)
        cy += 4 if atrib else 0
        if not atrib:
            cy += 4
        if metodos:
            self.linha([(x, cy), (x + w, cy)])
            for m in metodos:
                cy += lh
                self.texto(x + 3, cy, m, F, tam)
        return h

    def altura_classe(self, atrib, metodos, estereotipo=None, tam=6.6):
        lh = tam + 2.4
        h = 6 + (lh if estereotipo else 0) + lh + 3
        h += (len(atrib) * lh + 4) if atrib else 4
        if metodos:
            h += len(metodos) * lh + 4
        return h

    def ator(self, cx, y, nome, estereotipo=None, tam=7):
        c = self.c
        c.setStrokeColor(INK)
        c.setLineWidth(0.9)
        c.setFillColor(colors.white)
        c.circle(cx, y + 5, 4.5, stroke=1, fill=1)
        self.linha([(cx, y + 9.5), (cx, y + 22)])
        self.linha([(cx - 8, y + 14), (cx + 8, y + 14)])
        self.linha([(cx, y + 22), (cx - 7, y + 33)])
        self.linha([(cx, y + 22), (cx + 7, y + 33)])
        yy = y + 33 + tam + 1
        if estereotipo:
            self.texto(cx, yy, "«%s»" % estereotipo, F, tam - 1, INK, "c")
            yy += tam
        for i, linha in enumerate(nome.split("\n")):
            self.texto(cx, yy + i * (tam + 1), linha, FB, tam, INK, "c")

    def legenda(self, x, y, itens, tam=6.6):
        cx = x
        for status, txt in itens:
            self.retangulo(cx, y, 14, 8, status)
            self.texto(cx + 18, y + 6.3, txt, F, tam)
            cx += 18 + self.largura_texto(txt, F, tam) + 16
        return cx
