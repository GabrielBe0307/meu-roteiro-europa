#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera uma imagem (PNG) com o resumo das despesas da viagem, pronta para
mandar no WhatsApp. Lê os dados de lancamentos.js (a mesma fonte do app).

Mostra, por moeda (Euro e Real, sempre separados):
  - total gasto
  - saldo de cada pessoa
  - acerto de contas (quem transfere para quem)
  - histórico de compras (com quem pagou e, em letra menor, quem dividiu)

Uso:  python3 gerar_resumo.py
Saída: resumo.png
"""
import json, subprocess, os
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Sao_Paulo")
except Exception:
    TZ = None
from PIL import Image, ImageDraw, ImageFont

PEOPLE = ["Gabriel", "Clara", "Aline", "Renan", "Fonte", "Rosana"]
HERE = os.path.dirname(os.path.abspath(__file__))
CUR = {"EUR": {"sym": "€", "name": "EURO"}, "BRL": {"sym": "R$", "name": "REAL"}}

# ---------- carregar dados de lancamentos.js ----------
def parse_cents(v):
    if v is None: return None
    s = str(v).strip()
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")
    try:
        return round(float(s) * 100)
    except ValueError:
        return None

def load_expenses():
    out = subprocess.check_output(
        ["node", "-e",
         "global.window={};require('./lancamentos.js');"
         "process.stdout.write(JSON.stringify(global.window.LANCAMENTOS||[]))"],
        cwd=HERE)
    raw = json.loads(out.decode("utf-8"))
    exps = []
    for e in raw:
        cents = parse_cents(e.get("valor", e.get("cents")))
        moeda = "BRL" if str(e.get("moeda", "EUR")).upper() == "BRL" else "EUR"
        pagou = [n for n in e.get("pagou", []) if n in PEOPLE]
        dividir = [n for n in e.get("dividir", []) if n in PEOPLE]
        if cents is None or cents <= 0 or not pagou or not dividir:
            continue
        exps.append({"desc": e.get("desc", ""), "cents": cents, "moeda": moeda,
                     "pagou": pagou, "dividir": dividir, "data": e.get("data", ""),
                     "tipo": e.get("tipo", "compra")})
    return exps

def split_cents(total, n):
    base = total // n
    rem = total - base * n
    return [base + (1 if i < rem else 0) for i in range(n)]

def fmt(cents, sym):
    neg = cents < 0
    s = f"{abs(cents)/100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if neg else "") + sym + " " + s

def compute(exps, moeda):
    # paid/owed (e portanto o saldo) incluem compras E acertos;
    # o "total gasto" considera apenas compras (acertos só movem dinheiro).
    paid = {n: 0 for n in PEOPLE}
    owed = {n: 0 for n in PEOPLE}
    total = 0
    for e in exps:
        if e["moeda"] != moeda: continue
        if e["tipo"] != "acerto":
            total += e["cents"]
        for n, c in zip(e["pagou"], split_cents(e["cents"], len(e["pagou"]))):
            paid[n] += c
        for n, c in zip(e["dividir"], split_cents(e["cents"], len(e["dividir"]))):
            owed[n] += c
    bal = {n: paid[n] - owed[n] for n in PEOPLE}
    return total, paid, owed, bal

RATE = 5.95  # 1 € = R$ 5,95

def eur_to_brl_cents(eur_cents):
    return round(eur_cents * RATE)

def combined_balances(eur_bal, brl_bal):
    # converte o saldo em euro para reais e soma ao saldo em real;
    # ajusta 1-2 centavos de arredondamento para a soma fechar em zero.
    conv = {n: eur_to_brl_cents(eur_bal[n]) for n in PEOPLE}
    residual = -sum(conv.values())
    if residual != 0:
        alvo = max(PEOPLE, key=lambda n: abs(conv[n]))
        conv[alvo] += residual
    comb = {n: brl_bal[n] + conv[n] for n in PEOPLE}
    return comb, conv

def settle(bal):
    cr = sorted([{"name": n, "amt": bal[n]} for n in PEOPLE if bal[n] > 0], key=lambda x: -x["amt"])
    de = sorted([{"name": n, "amt": -bal[n]} for n in PEOPLE if bal[n] < 0], key=lambda x: -x["amt"])
    tx, i, j = [], 0, 0
    while i < len(de) and j < len(cr):
        p = min(de[i]["amt"], cr[j]["amt"])
        if p > 0:
            tx.append((de[i]["name"], cr[j]["name"], p))
        de[i]["amt"] -= p; cr[j]["amt"] -= p
        if de[i]["amt"] == 0: i += 1
        if cr[j]["amt"] == 0: j += 1
    return tx

# ---------- fontes ----------
# Renderização em alta resolução (supersampling nativo): toda a lógica de
# layout usa coordenadas "lógicas"; na hora de desenhar, um proxy multiplica
# tudo por SCALE e troca a fonte pela versão ampliada -> texto nítido no zoom.
SCALE = 3
FD = "/usr/share/fonts/truetype/dejavu/"
_FONTS = {}  # fonte lógica (medição) -> fonte ampliada (desenho)
def F(name, size):
    lf = ImageFont.truetype(FD + name, size)
    _FONTS[lf] = ImageFont.truetype(FD + name, size * SCALE)
    return lf
f_title  = F("DejaVuSans-Bold.ttf", 40)
f_sub    = F("DejaVuSans.ttf", 24)
f_sec    = F("DejaVuSans-Bold.ttf", 34)
f_sectot = F("DejaVuSans-Bold.ttf", 26)
f_name   = F("DejaVuSans-Bold.ttf", 27)
f_val    = F("DejaVuSans-Bold.ttf", 27)
f_lbl    = F("DejaVuSans.ttf", 21)
f_txb    = F("DejaVuSans-Bold.ttf", 25)
f_tx     = F("DejaVuSans.ttf", 25)
f_subh   = F("DejaVuSans-Bold.ttf", 25)
f_entry  = F("DejaVuSans-Bold.ttf", 24)
f_small  = F("DejaVuSans.ttf", 19)
f_date   = F("DejaVuSans-Bold.ttf", 19)
f_upd    = F("DejaVuSans.ttf", 21)
f_foot   = F("DejaVuSans.ttf", 20)

# cores
C_BG = (244, 246, 249)
C_HEAD = (26, 77, 122)
C_WHITE = (255, 255, 255)
C_TEXT = (26, 26, 26)
C_MUTED = (107, 114, 128)
C_GREEN = (31, 157, 85)
C_RED = (214, 69, 69)
C_LINE = (229, 231, 235)
C_CARD = (255, 255, 255)

W = 1080
PAD = 48
CONTENT_W = W - 2 * PAD
_md = ImageDraw.Draw(Image.new("RGB", (10, 10)))  # medição em coordenadas lógicas

class ScaledDraw:
    """Desenha em alta resolução: escala coordenadas por SCALE e usa a fonte ampliada."""
    def __init__(self, d): self.d = d
    def _f(self, font): return _FONTS.get(font, font)
    def text(self, xy, txt, font=None, fill=None):
        self.d.text((xy[0] * SCALE, xy[1] * SCALE), txt, font=self._f(font), fill=fill)
    def line(self, xy, fill=None, width=1):
        self.d.line([c * SCALE for c in xy], fill=fill, width=max(1, width * SCALE))
    def rectangle(self, xy, fill=None):
        self.d.rectangle([c * SCALE for c in xy], fill=fill)
    def rounded_rectangle(self, xy, radius=0, fill=None):
        self.d.rounded_rectangle([c * SCALE for c in xy], radius=radius * SCALE, fill=fill)
    def textlength(self, txt, font=None):
        return self.d.textlength(txt, font=font)  # medição lógica (fonte lógica)

def wrap(text, font, first_w, rest_w=None):
    rest_w = rest_w if rest_w is not None else first_w
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        max_w = first_w if not lines else rest_w
        if _md.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines or [""]

def entry_layout(e, sym):
    valtxt = fmt(e["cents"], sym)
    vw = _md.textlength(valtxt, font=f_entry)
    dlines = wrap(e["desc"], f_entry, CONTENT_W - vw - 18)
    d = e.get("data", "")
    datestr = (d[8:10] + "/" + d[5:7] + "/" + d[0:4]) if len(d) >= 10 else ""
    dw = (_md.textlength(datestr, font=f_date) + 14) if datestr else 0
    if e["tipo"] == "acerto":
        meta = e["pagou"][0] + " pagou " + e["dividir"][0] + "  ·  dívida quitada ✓"
    else:
        share = fmt(round(e["cents"] / len(e["dividir"])), sym)
        meta = ("Pagou: " + ", ".join(e["pagou"]) +
                "  ·  Dividiu: " + ", ".join(e["dividir"]) +
                "  ·  ÷" + str(len(e["dividir"])) + " = " + share + "/pessoa")
    mlines = wrap(meta, f_small, CONTENT_W - dw, CONTENT_W)
    h = len(dlines) * 30 + len(mlines) * 24 + 18
    return dlines, mlines, valtxt, vw, datestr, dw, h

def num(c):  # número sem símbolo (para as cotas)
    return f"{c/100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def shorten(desc, maxlen=17):
    d = desc.split(" (")[0].strip()          # tira o parêntese
    return d if len(d) <= maxlen else d[:maxlen - 1] + "…"

def balance_row_lines(n, paid, owed, compras, sym):
    # monta o texto "pagou X · cota Y = item(a) + item(b) + ..."
    itens = []
    for e in compras:
        if n in e["dividir"]:
            parts = split_cents(e["cents"], len(e["dividir"]))
            share = parts[e["dividir"].index(n)]
            itens.append(shorten(e["desc"]) + " " + num(share))
    head = "pagou " + fmt(paid, sym) + "  ·  cota " + fmt(owed, sym)
    texto = head + " = " + " + ".join(itens) if itens else head
    lines = wrap(texto, f_small, CONTENT_W)
    return lines

def balance_row_height(n, paid, owed, compras, sym):
    return 32 + len(balance_row_lines(n, paid, owed, compras, sym)) * 24 + 16

def card_height(rows, tx, compras, acertos, sym, paid, owed):
    h = 24            # top pad
    h += 64           # section title
    h += 14           # after line
    for n in rows:
        h += balance_row_height(n, paid[n], owed[n], compras, sym)
    h += 10
    h += 44           # settlement title
    h += 30           # explicação da lógica
    h += max(1, len(tx)) * 46
    h += 22           # gap
    h += 44           # compras title
    for e in compras:
        h += entry_layout(e, sym)[6]
    if acertos:
        h += 20 + 44  # gap + acertos title
        for e in acertos:
            h += entry_layout(e, sym)[6]
    h += 24           # bottom pad
    return h

def draw_image(exps):
    blocks = []
    for m in ["EUR", "BRL"]:
        total, paid, owed, bal = compute(exps, m)
        mexps = [e for e in exps if e["moeda"] == m]
        if not mexps:
            continue
        compras = sorted([e for e in mexps if e["tipo"] != "acerto"],
                         key=lambda e: (e.get("data", "9999"),))
        acertos = sorted([e for e in mexps if e["tipo"] == "acerto"],
                         key=lambda e: (e.get("data", "9999"),))
        rows = [n for n in PEOPLE if paid[n] != 0 or owed[n] != 0]
        blocks.append((m, total, paid, owed, bal, settle(bal), rows, compras, acertos))

    # ----- acumulado (tudo em R$) -----
    eur_total, _, _, eur_bal = compute(exps, "EUR")
    brl_total, _, _, brl_bal = compute(exps, "BRL")
    comb, conv = combined_balances(eur_bal, brl_bal)
    acum_total = brl_total + eur_to_brl_cents(eur_total)
    acum_tx = settle(comb)

    def acum_card_height(tx):
        return 24 + 64 + 36 + 14 + len(PEOPLE) * 58 + 10 + 44 + 34 + max(1, len(tx)) * 46 + 24

    HEAD_H = 188
    total_h = HEAD_H + 30
    for (m, total, paid, owed, bal, tx, rows, compras, acertos) in blocks:
        total_h += card_height(rows, tx, compras, acertos, CUR[m]["sym"], paid, owed) + 28
    total_h += acum_card_height(acum_tx) + 28
    total_h += 90

    img = Image.new("RGB", (W * SCALE, total_h * SCALE), C_BG)
    d = ScaledDraw(ImageDraw.Draw(img))

    # header
    d.rectangle([0, 0, W, HEAD_H], fill=C_HEAD)
    d.text((PAD, 34), "Resumo de Despesas", font=f_title, fill=C_WHITE)
    d.text((PAD, 88), "Viagem Europa · 6 pessoas · acumulado a R$ 5,95/€",
           font=f_sub, fill=(210, 224, 238))
    upd = "Atualizado em " + datetime.now(TZ).strftime("%d/%m/%Y às %H:%M")
    d.text((PAD, 132), upd, font=f_upd, fill=(150, 190, 225))
    y = HEAD_H + 30

    for (m, total, paid, owed, bal, tx, rows, compras, acertos) in blocks:
        sym = CUR[m]["sym"]
        ch = card_height(rows, tx, compras, acertos, sym, paid, owed)
        d.rounded_rectangle([PAD - 14, y, W - (PAD - 14), y + ch], radius=18, fill=C_CARD)
        cy = y + 24

        # título da seção + total
        accent = C_HEAD if m == "EUR" else C_GREEN
        d.rounded_rectangle([PAD, cy + 4, PAD + 10, cy + 40], radius=5, fill=accent)
        d.text((PAD + 26, cy), CUR[m]["name"], font=f_sec, fill=accent)
        ttot = fmt(total, sym)
        d.text((W - PAD - _md.textlength(ttot, font=f_sectot), cy + 6),
               ttot, font=f_sectot, fill=C_TEXT)
        cy += 64
        d.line([PAD, cy, W - PAD, cy], fill=C_LINE, width=2)
        cy += 14

        # saldos (com o porquê: pagou vs cota, e a composição da cota)
        for n in rows:
            v = bal[n]
            d.text((PAD + 4, cy), n, font=f_name, fill=C_TEXT)
            if v > 0:   txt, col, lbl = fmt(v, sym), C_GREEN, "a receber"
            elif v < 0: txt, col, lbl = fmt(v, sym), C_RED, "a pagar"
            else:       txt, col, lbl = fmt(0, sym), C_MUTED, "quitado"
            tw = _md.textlength(txt, font=f_val)
            d.text((W - PAD - tw, cy), txt, font=f_val, fill=col)
            lw = _md.textlength(lbl, font=f_lbl)
            d.text((W - PAD - tw - 12 - lw, cy + 4), lbl, font=f_lbl, fill=C_MUTED)
            lines = balance_row_lines(n, paid[n], owed[n], compras, sym)
            for i, ln in enumerate(lines):
                d.text((PAD + 4, cy + 32 + i * 24), ln, font=f_small, fill=C_MUTED)
            cy += 32 + len(lines) * 24 + 16

        cy += 10
        # acerto
        d.text((PAD + 4, cy), "→ Passar a régua (quem paga a quem):", font=f_txb, fill=C_HEAD)
        cy += 40
        d.text((PAD + 4, cy), "Quem tem saldo negativo paga quem tem positivo, até zerar.",
               font=f_small, fill=C_MUTED)
        cy += 34
        if not tx:
            d.text((PAD + 4, cy), "Tudo quitado.", font=f_tx, fill=C_MUTED); cy += 46
        for (frm, to, amt) in tx:
            d.text((PAD + 4, cy), frm, font=f_txb, fill=C_RED)
            fw = _md.textlength(frm, font=f_txb)
            d.text((PAD + 12 + fw, cy), "→", font=f_tx, fill=C_MUTED)
            aw2 = _md.textlength("→", font=f_tx)
            d.text((PAD + 20 + fw + aw2, cy), to, font=f_txb, fill=C_GREEN)
            amt_s = fmt(amt, sym)
            d.text((W - PAD - _md.textlength(amt_s, font=f_txb), cy), amt_s, font=f_txb, fill=C_HEAD)
            cy += 46

        def draw_entries(items, start_y, name_color):
            yy = start_y
            for e in items:
                dlines, mlines, valtxt, vw, datestr, dw, eh = entry_layout(e, sym)
                d.text((W - PAD - vw, yy), valtxt, font=f_entry, fill=name_color)
                for i, ln in enumerate(dlines):
                    d.text((PAD + 4, yy + i * 30), ln, font=f_entry, fill=name_color)
                my = yy + len(dlines) * 30 + 2
                if datestr:
                    d.text((PAD + 4, my), datestr, font=f_date, fill=accent)
                for i, ln in enumerate(mlines):
                    x = PAD + 4 + (dw if i == 0 else 0)
                    d.text((x, my + i * 24), ln, font=f_small, fill=C_MUTED)
                yy += eh
            return yy

        cy += 22
        # histórico de compras
        d.text((PAD + 4, cy), "Compras (histórico):", font=f_subh, fill=C_HEAD)
        cy += 44
        cy = draw_entries(compras, cy, C_TEXT)

        # acertos / pagamentos já feitos
        if acertos:
            cy += 20
            d.text((PAD + 4, cy), "Acertos já pagos:", font=f_subh, fill=C_GREEN)
            cy += 44
            cy = draw_entries(acertos, cy, C_GREEN)

        y += ch + 28

    # ===== card ACUMULADO (tudo em R$) =====
    C_GOLD = (176, 122, 20)
    ach = acum_card_height(acum_tx)
    d.rounded_rectangle([PAD - 14, y, W - (PAD - 14), y + ach], radius=18, fill=C_CARD)
    cy = y + 24
    d.rounded_rectangle([PAD, cy + 4, PAD + 10, cy + 40], radius=5, fill=C_GOLD)
    d.text((PAD + 26, cy), "ACUMULADO (R$)", font=f_sec, fill=C_GOLD)
    at = fmt(acum_total, "R$")
    d.text((W - PAD - _md.textlength(at, font=f_sectot), cy + 6), at, font=f_sectot, fill=C_TEXT)
    cy += 56
    d.text((PAD + 4, cy), "Euro convertido a R$ 5,95/€ + Real, somados.", font=f_small, fill=C_MUTED)
    cy += 30
    d.line([PAD, cy, W - PAD, cy], fill=C_LINE, width=2)
    cy += 14

    for n in PEOPLE:
        v = comb[n]
        d.text((PAD + 4, cy), n, font=f_name, fill=C_TEXT)
        brk = fmt(brl_bal[n], "R$") + " (real)  +  " + fmt(conv[n], "R$") + " (€ conv.)"
        d.text((PAD + 4, cy + 30), brk, font=f_small, fill=C_MUTED)
        if v > 0:   txt, col, lbl = fmt(v, "R$"), C_GREEN, "a receber"
        elif v < 0: txt, col, lbl = fmt(v, "R$"), C_RED, "a pagar"
        else:       txt, col, lbl = fmt(0, "R$"), C_MUTED, "quitado"
        d.text((W - PAD - _md.textlength(txt, font=f_val), cy - 2), txt, font=f_val, fill=col)
        d.text((W - PAD - _md.textlength(lbl, font=f_lbl), cy + 30), lbl, font=f_lbl, fill=C_MUTED)
        cy += 58

    cy += 10
    d.text((PAD + 4, cy), "→ Passar a régua FINAL (quem paga a quem):", font=f_txb, fill=C_GOLD)
    cy += 40
    d.text((PAD + 4, cy), "Saldo = tudo que a pessoa pagou menos suas cotas (€ já convertido).",
           font=f_small, fill=C_MUTED)
    cy += 34
    if not acum_tx:
        d.text((PAD + 4, cy), "Tudo quitado.", font=f_tx, fill=C_MUTED); cy += 46
    for (frm, to, amt) in acum_tx:
        d.text((PAD + 4, cy), frm, font=f_txb, fill=C_RED)
        fw = _md.textlength(frm, font=f_txb)
        d.text((PAD + 12 + fw, cy), "→", font=f_tx, fill=C_MUTED)
        aw2 = _md.textlength("→", font=f_tx)
        d.text((PAD + 20 + fw + aw2, cy), to, font=f_txb, fill=C_GREEN)
        amt_s = fmt(amt, "R$")
        d.text((W - PAD - _md.textlength(amt_s, font=f_txb), cy), amt_s, font=f_txb, fill=C_GOLD)
        cy += 46

    y += ach + 28

    d.text((PAD, y + 6),
           "€ e R$ mostrados separados; o acumulado converte € a R$ 5,95 e soma.",
           font=f_foot, fill=C_MUTED)

    img.save(os.path.join(HERE, "resumo.png"))
    print("resumo.png gerado:", img.size)

if __name__ == "__main__":
    draw_image(load_expenses())
