#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera uma imagem (PNG) com o resumo das despesas da viagem, pronta para
mandar no WhatsApp. Lê os dados de lancamentos.js (a mesma fonte do app).

Uso:  python3 gerar_resumo.py
Saída: resumo.png
"""
import json, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont

PEOPLE = ["Gabriel", "Clara", "Aline", "Renan", "Fonte", "Rosana"]
HERE = os.path.dirname(os.path.abspath(__file__))
CUR = {"EUR": {"sym": "€", "name": "EURO"}, "BRL": {"sym": "R$", "name": "REAL"}}

# ---------- carregar dados de lancamentos.js ----------
def load_expenses():
    out = subprocess.check_output(
        ["node", "-e",
         "global.window={};require('./lancamentos.js');"
         "process.stdout.write(JSON.stringify(global.window.LANCAMENTOS||[]))"],
        cwd=HERE)
    raw = json.loads(out.decode("utf-8"))
    exps = []
    for e in raw:
        valor = e.get("valor", e.get("cents"))
        cents = parse_cents(valor)
        moeda = "BRL" if str(e.get("moeda", "EUR")).upper() == "BRL" else "EUR"
        pagou = [n for n in e.get("pagou", []) if n in PEOPLE]
        dividir = [n for n in e.get("dividir", []) if n in PEOPLE]
        if cents is None or cents <= 0 or not pagou or not dividir:
            continue
        exps.append({"desc": e.get("desc", ""), "cents": cents, "moeda": moeda,
                     "pagou": pagou, "dividir": dividir, "data": e.get("data", "")})
    return exps

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

def split_cents(total, n):
    base = total // n
    rem = total - base * n
    return [base + (1 if i < rem else 0) for i in range(n)]

def fmt(cents, sym):
    neg = cents < 0
    s = f"{abs(cents)/100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if neg else "") + sym + " " + s

def compute(exps, moeda):
    paid = {n: 0 for n in PEOPLE}
    owed = {n: 0 for n in PEOPLE}
    total = 0
    for e in exps:
        if e["moeda"] != moeda: continue
        total += e["cents"]
        for n, c in zip(e["pagou"], split_cents(e["cents"], len(e["pagou"]))):
            paid[n] += c
        for n, c in zip(e["dividir"], split_cents(e["cents"], len(e["dividir"]))):
            owed[n] += c
    bal = {n: paid[n] - owed[n] for n in PEOPLE}
    return total, paid, owed, bal

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
FD = "/usr/share/fonts/truetype/dejavu/"
def F(name, size): return ImageFont.truetype(FD + name, size)
f_title  = F("DejaVuSans-Bold.ttf", 40)
f_sub    = F("DejaVuSans.ttf", 24)
f_sec    = F("DejaVuSans-Bold.ttf", 34)
f_sectot = F("DejaVuSans-Bold.ttf", 26)
f_name   = F("DejaVuSans-Bold.ttf", 27)
f_val    = F("DejaVuSans-Bold.ttf", 27)
f_lbl    = F("DejaVuSans.ttf", 21)
f_tx     = F("DejaVuSans.ttf", 25)
f_txb    = F("DejaVuSans-Bold.ttf", 25)
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

def draw_image(exps):
    # primeiro mede a altura
    blocks = []  # (moeda) só as que têm gasto
    for m in ["EUR", "BRL"]:
        total, paid, owed, bal = compute(exps, m)
        if total > 0:
            blocks.append((m, total, paid, owed, bal, settle(bal)))

    # estimativa de altura
    h = 0
    h += 150  # header
    h += 30
    for (m, total, paid, owed, bal, tx) in blocks:
        h += 70                      # título seção
        rows = sum(1 for n in PEOPLE if paid[n] != 0 or owed[n] != 0)
        h += rows * 52 + 30          # saldos
        h += 50                      # subtítulo acerto
        h += max(1, len(tx)) * 46 + 30
        h += 40                      # respiro
    h += 90  # rodapé

    img = Image.new("RGB", (W, h), C_BG)
    d = ImageDraw.Draw(img)

    # ---- header ----
    d.rectangle([0, 0, W, 150], fill=C_HEAD)
    d.text((PAD, 38), "Resumo de Despesas", font=f_title, fill=C_WHITE)
    d.text((PAD, 92), "Viagem Europa · 6 pessoas · € e R$ separados",
           font=f_sub, fill=(210, 224, 238))
    y = 150 + 30

    def card(top, height):
        d.rounded_rectangle([PAD - 14, top, W - (PAD - 14), top + height],
                            radius=18, fill=C_CARD)

    for (m, total, paid, owed, bal, tx) in blocks:
        sym = CUR[m]["sym"]
        rows = [n for n in PEOPLE if paid[n] != 0 or owed[n] != 0]
        card_h = 70 + len(rows) * 52 + 30 + 50 + max(1, len(tx)) * 46 + 24
        card(y, card_h)
        cy = y + 24

        # título da seção
        accent = C_HEAD if m == "EUR" else C_GREEN
        d.rounded_rectangle([PAD, cy + 4, PAD + 10, cy + 40], radius=5, fill=accent)
        d.text((PAD + 26, cy), CUR[m]["name"], font=f_sec, fill=accent)
        ttot = fmt(total, sym)
        tw = d.textlength(ttot, font=f_sectot)
        d.text((W - (PAD) - tw, cy + 6), ttot, font=f_sectot, fill=C_TEXT)
        cy += 64
        d.line([PAD, cy, W - PAD, cy], fill=C_LINE, width=2)
        cy += 14

        # saldos
        for n in rows:
            v = bal[n]
            d.text((PAD + 4, cy), n, font=f_name, fill=C_TEXT)
            if v > 0:
                txt, col, lbl = fmt(v, sym), C_GREEN, "a receber"
            elif v < 0:
                txt, col, lbl = fmt(v, sym), C_RED, "a pagar"
            else:
                txt, col, lbl = fmt(0, sym), C_MUTED, "quitado"
            vw = d.textlength(txt, font=f_val)
            d.text((W - PAD - vw, cy - 2), txt, font=f_val, fill=col)
            lw = d.textlength(lbl, font=f_lbl)
            d.text((W - PAD - lw, cy + 28), lbl, font=f_lbl, fill=C_MUTED)
            cy += 52

        cy += 10
        d.text((PAD + 4, cy), "→ Quem transfere para quem:", font=f_txb, fill=C_HEAD)
        cy += 44
        if not tx:
            d.text((PAD + 4, cy), "Tudo quitado.", font=f_tx, fill=C_MUTED)
            cy += 46
        for (frm, to, amt) in tx:
            d.text((PAD + 4, cy), frm, font=f_txb, fill=C_RED)
            fw = d.textlength(frm, font=f_txb)
            d.text((PAD + 4 + fw + 8, cy), "→", font=f_tx, fill=C_MUTED)
            aw2 = d.textlength("→", font=f_tx)
            d.text((PAD + 4 + fw + 8 + aw2 + 8, cy), to, font=f_txb, fill=C_GREEN)
            amt_s = fmt(amt, sym)
            aw = d.textlength(amt_s, font=f_txb)
            d.text((W - PAD - aw, cy), amt_s, font=f_txb, fill=C_HEAD)
            cy += 46

        y += card_h + 28

    # rodapé
    d.text((PAD, y + 6),
           "Euro e Real contabilizados separadamente, sem câmbio.",
           font=f_foot, fill=C_MUTED)

    img.save(os.path.join(HERE, "resumo.png"))
    print("resumo.png gerado:", img.size)

if __name__ == "__main__":
    draw_image(load_expenses())
