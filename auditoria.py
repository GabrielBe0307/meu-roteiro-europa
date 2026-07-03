#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDITORIA INDEPENDENTE das contas da viagem.

Recalcula tudo do zero (lógica própria, sem reaproveitar o gerador),
verifica as leis de conservação e, por fim, compara os resultados com
os do gerador da imagem (gerar_resumo.py). Só passa se TODAS as
verificações baterem.

Uso: python3 auditoria.py
"""
import json, subprocess, os, sys

PEOPLE = ["Gabriel", "Clara", "Aline", "Renan", "Fonte", "Rosana"]
RATE = 5.95
HERE = os.path.dirname(os.path.abspath(__file__))

falhas = []
def check(cond, msg):
    status = "OK  " if cond else "FALHA"
    if not cond:
        falhas.append(msg)
    print(f"  [{status}] {msg}")
    return cond

# ---------- parsing próprio (independente do gerador) ----------
def parse_cents(v):
    s = str(v).strip()
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")
    return int(round(float(s) * 100))

def split_cents(total, n):
    base, rem = divmod(total, n)
    return [base + (1 if i < rem else 0) for i in range(n)]

def load():
    out = subprocess.check_output(
        ["node", "-e",
         "global.window={};require('./lancamentos.js');"
         "process.stdout.write(JSON.stringify(global.window.LANCAMENTOS||[]))"],
        cwd=HERE)
    return json.loads(out.decode("utf-8"))

def brl(c):  # formata em reais
    s = f"{abs(c)/100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if c < 0 else "") + "R$ " + s

def eur(c):
    s = f"{abs(c)/100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if c < 0 else "") + "€ " + s

# ---------- 1. conservação por lançamento ----------
print("\n=== 1. Conservação por lançamento (pago = devido, em centavos) ===")
raw = load()
exps = []
for e in raw:
    cents = parse_cents(e["valor"])
    pagou, dividir = e["pagou"], e["dividir"]
    paid_parts = split_cents(cents, len(pagou))
    owed_parts = split_cents(cents, len(dividir))
    ok = (sum(paid_parts) == cents) and (sum(owed_parts) == cents)
    check(ok, f'{e["moeda"]} {e["desc"][:38]:38} {cents:>7}c  pago={sum(paid_parts)} devido={sum(owed_parts)}')
    exps.append({**e, "cents": cents})

# ---------- 2. saldos por moeda ----------
def balances(moeda):
    paid = {n: 0 for n in PEOPLE}
    owed = {n: 0 for n in PEOPLE}
    total = 0
    for e in exps:
        if e["moeda"] != moeda:
            continue
        if e.get("tipo") != "acerto":
            total += e["cents"]
        for n, c in zip(e["pagou"], split_cents(e["cents"], len(e["pagou"]))):
            paid[n] += c
        for n, c in zip(e["dividir"], split_cents(e["cents"], len(e["dividir"]))):
            owed[n] += c
    bal = {n: paid[n] - owed[n] for n in PEOPLE}
    return total, paid, owed, bal

print("\n=== 2. Saldos por pessoa e soma zero ===")
eur_total, eur_paid, eur_owed, eur_bal = balances("EUR")
brl_total, brl_paid, brl_owed, brl_bal = balances("BRL")
for moeda, tot, paid, owed, bal, f in [("EUR", eur_total, eur_paid, eur_owed, eur_bal, eur),
                                       ("BRL", brl_total, brl_paid, brl_owed, brl_bal, brl)]:
    print(f"  -- {moeda} -- total em compras: {f(tot)}")
    for n in PEOPLE:
        print(f"     {n:8} pagou {f(paid[n]):>12}  cota {f(owed[n]):>12}  saldo {f(bal[n]):>12}")
    check(sum(bal.values()) == 0, f"{moeda}: soma dos saldos = {sum(bal.values())} (deve ser 0)")

# ---------- 3. conversão e acumulado ----------
print("\n=== 3. Conversão (€ -> R$ 5,95) e acumulado ===")
conv = {n: int(round(eur_bal[n] * RATE)) for n in PEOPLE}
residual = -sum(conv.values())
alvo = max(PEOPLE, key=lambda n: abs(conv[n]))
if residual != 0:
    conv[alvo] += residual
check(abs(residual) <= 3, f"resíduo de arredondamento da conversão = {residual}c (ajustado em {alvo})")
comb = {n: brl_bal[n] + conv[n] for n in PEOPLE}
acum_total = brl_total + int(round(eur_total * RATE))
print(f"  total acumulado: {brl(acum_total)}")
for n in PEOPLE:
    print(f"     {n:8} real {brl(brl_bal[n]):>12}  + € conv {brl(conv[n]):>12}  = {brl(comb[n]):>12}")
check(sum(comb.values()) == 0, f"acumulado: soma dos saldos = {sum(comb.values())} (deve ser 0)")

# ---------- 4. acerto (settlement) e validação ----------
def settle(bal):
    cr = sorted([[n, bal[n]] for n in PEOPLE if bal[n] > 0], key=lambda x: -x[1])
    de = sorted([[n, -bal[n]] for n in PEOPLE if bal[n] < 0], key=lambda x: -x[1])
    tx, i, j = [], 0, 0
    while i < len(de) and j < len(cr):
        p = min(de[i][1], cr[j][1])
        if p > 0:
            tx.append((de[i][0], cr[j][0], p))
        de[i][1] -= p; cr[j][1] -= p
        if de[i][1] == 0: i += 1
        if cr[j][1] == 0: j += 1
    return tx

def audit_settlement(nome, bal, tx):
    print(f"\n=== 4.{nome} Acerto '{nome}' ===")
    # reconstrói saldos a partir das transferências
    recon = {n: 0 for n in PEOPLE}
    all_pos = True
    for frm, to, amt in tx:
        recon[frm] -= amt
        recon[to] += amt
        if amt <= 0:
            all_pos = False
    check(all_pos, f"{nome}: todas as transferências são positivas")
    ok_recon = all(recon[n] == bal[n] for n in PEOPLE)
    check(ok_recon, f"{nome}: transferências reconstroem exatamente os saldos")
    total_transf = sum(a for _, _, a in tx)
    total_credito = sum(v for v in bal.values() if v > 0)
    check(total_transf == total_credito, f"{nome}: soma das transferências ({total_transf}c) = total a receber ({total_credito}c)")
    check(len(tx) <= len(PEOPLE) - 1, f"{nome}: nº de transferências ({len(tx)}) <= {len(PEOPLE)-1}")
    for frm, to, amt in tx:
        print(f"     {frm} -> {to}: {bal is comb and brl(amt) or ''}")
    return recon

eur_tx = settle(eur_bal)
brl_tx = settle(brl_bal)
comb_tx = settle(comb)
audit_settlement("EUR", eur_bal, eur_tx)
audit_settlement("BRL", brl_bal, brl_tx)
audit_settlement("ACUM", comb, comb_tx)
print("  Transferências do acumulado (final):")
for frm, to, amt in comb_tx:
    print(f"     {frm} -> {to}: {brl(amt)}")

# ---------- 5. cruzamento com o gerador (gerar_resumo.py) ----------
print("\n=== 5. Cruzamento com o gerador da imagem (implementação separada) ===")
try:
    import gerar_resumo as G
    gexps = G.load_expenses()
    get, _, _, geb = G.compute(gexps, "EUR")
    gbt, _, _, gbb = G.compute(gexps, "BRL")
    gcomb, gconv = G.combined_balances(geb, gbb)
    check(get == eur_total and gbt == brl_total, f"totais batem (EUR {get}={eur_total}, BRL {gbt}={brl_total})")
    check(all(geb[n] == eur_bal[n] for n in PEOPLE), "saldos EUR batem com o gerador")
    check(all(gbb[n] == brl_bal[n] for n in PEOPLE), "saldos BRL batem com o gerador")
    check(all(gcomb[n] == comb[n] for n in PEOPLE), "saldos ACUMULADOS batem com o gerador")
    gtx = G.settle(gcomb)
    check(gtx == comb_tx, "acerto final idêntico ao do gerador")
except Exception as ex:
    check(False, f"erro ao cruzar com o gerador: {ex}")

# ---------- resultado ----------
print("\n" + "=" * 50)
if falhas:
    print(f"RESULTADO: {len(falhas)} FALHA(S):")
    for f in falhas:
        print("  -", f)
    sys.exit(1)
else:
    print("RESULTADO: TUDO CERTO ✓  (todas as verificações passaram)")
