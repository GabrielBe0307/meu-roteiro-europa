/* ============================================================
   LANÇAMENTOS DA VIAGEM
   ------------------------------------------------------------
   Este arquivo guarda todos os gastos. O Gabriel dita os gastos
   na conversa com o Claude, que atualiza esta lista e faz o push.
   Ao abrir/atualizar o app (despesas.html), os lançamentos aparecem.

   Formato de cada lançamento:
   {
     desc:    "Descrição do gasto",
     valor:   "45,90",          // aceita vírgula ou ponto
     moeda:   "EUR",            // "EUR" (€) ou "BRL" (R$)
     pagou:   ["Gabriel"],      // quem pagou (se +1, divide igual o que foi pago)
     dividir: TODOS,            // quem participa da divisão (custo rachado igual)
     data:    "2026-06-18"      // opcional (AAAA-MM-DD)
   }

   Atalho: use TODOS para marcar as 6 pessoas de uma vez.
   ============================================================ */

const TODOS = ["Gabriel", "Clara", "Aline", "Renan", "Fonte", "Rosana"];

window.LANCAMENTOS = [
  { desc: "Uber", valor: "12,97", moeda: "EUR", pagou: ["Gabriel"], dividir: TODOS, data: "2026-06-19" },
  { desc: "Uber", valor: "15,99", moeda: "EUR", pagou: ["Aline"], dividir: TODOS, data: "2026-06-19" },
  { desc: "Uber", valor: "8,97", moeda: "EUR", pagou: ["Gabriel"], dividir: ["Gabriel", "Clara", "Aline", "Fonte", "Rosana"], data: "2026-06-20" },
  { desc: "Uber", valor: "267,09", moeda: "BRL", pagou: ["Gabriel"], dividir: ["Gabriel", "Clara", "Fonte", "Rosana"], data: "2026-06-18" },
  { desc: "Compras diversas (passagem de ônibus, taxa de turismo e conta do restaurante)", valor: "176,50", moeda: "EUR", pagou: ["Gabriel"], dividir: ["Gabriel", "Clara"], data: "2026-06-20" },
  { desc: "Shots de licor de cereja", valor: "6,00", moeda: "EUR", pagou: ["Renan"], dividir: ["Gabriel", "Clara", "Aline", "Renan"], data: "2026-06-20" },
  { desc: "Restaurante", valor: "4,52", moeda: "EUR", pagou: ["Gabriel"], dividir: ["Gabriel", "Clara"], data: "2026-06-20" },
  { desc: "Restaurante", valor: "24,50", moeda: "EUR", pagou: ["Clara"], dividir: ["Clara", "Gabriel"], data: "2026-06-20" },
  { desc: "Uber", valor: "16,97", moeda: "EUR", pagou: ["Gabriel"], dividir: TODOS, data: "2026-06-20" },
  { desc: "Jantar e restaurante", valor: "97,00", moeda: "EUR", pagou: ["Clara"], dividir: ["Clara", "Gabriel"], data: "2026-06-20" },
  { desc: "Trem em Roma", valor: "75,00", moeda: "EUR", pagou: ["Gabriel"], dividir: TODOS, data: "2026-06-20" },
  { desc: "Croissant no Rock in Rio", valor: "7,00", moeda: "EUR", pagou: ["Gabriel"], dividir: ["Clara"], data: "2026-06-19" },
  { desc: "Uber para o aeroporto de Lisboa", valor: "17,98", moeda: "EUR", pagou: ["Gabriel"], dividir: TODOS, data: "2026-06-20" },
  { desc: "Uber para o aeroporto de Lisboa", valor: "16,97", moeda: "EUR", pagou: ["Aline"], dividir: TODOS, data: "2026-06-20" },

  // ----- Lote do encontro de contas final -----
  // Aline pagou
  { desc: "Van Castellammare–Vico Equense (ida)", valor: "9,00", moeda: "EUR", pagou: ["Aline"], dividir: ["Fonte", "Gabriel", "Rosana"] },
  { desc: "Restaurante do hotel (pizza)", valor: "68,00", moeda: "EUR", pagou: ["Aline"], dividir: TODOS },
  { desc: "Táxi Capri (ida e volta)", valor: "60,00", moeda: "EUR", pagou: ["Aline"], dividir: TODOS },
  { desc: "Uber Sorrento → hotel", valor: "50,00", moeda: "EUR", pagou: ["Aline"], dividir: ["Gabriel", "Clara", "Aline", "Fonte", "Rosana"] },
  { desc: "Uber aeroporto Fiumicino (Roma)", valor: "37,00", moeda: "EUR", pagou: ["Aline"], dividir: TODOS },
  // Clara pagou
  { desc: "Van Castellammare", valor: "12,00", moeda: "EUR", pagou: ["Clara"], dividir: ["Renan", "Gabriel", "Fonte", "Rosana"] },
  // Clara e Gabriel pagaram
  { desc: "Vinho", valor: "25,00", moeda: "EUR", pagou: ["Clara", "Gabriel"], dividir: ["Aline", "Renan", "Gabriel", "Clara"] },
  // Renan pagou
  { desc: "Taxa do Booking", valor: "21,35", moeda: "EUR", pagou: ["Renan"], dividir: TODOS },
  { desc: "Passeio Coliseu", valor: "1170,71", moeda: "BRL", pagou: ["Renan"], dividir: ["Rosana", "Fonte", "Renan", "Aline"] },
  { desc: "Hotel (Airbnb aeroporto)", valor: "1658,16", moeda: "BRL", pagou: ["Renan"], dividir: TODOS },
  // Fonte pagou
  { desc: "Táxi Capri (ida e volta)", valor: "60,00", moeda: "EUR", pagou: ["Fonte"], dividir: TODOS },
  // Gabriel pagou
  { desc: "Marinheiro (barqueiro)", valor: "40,00", moeda: "EUR", pagou: ["Gabriel"], dividir: TODOS },

  // ----- Acertos / pagamentos (não são compras; quitam dívidas) -----
  { desc: "Acerto — Clara pagou Gabriel", valor: "66,05", moeda: "EUR", pagou: ["Clara"], dividir: ["Gabriel"], data: "2026-06-20", tipo: "acerto" },
  { desc: "Acerto — Clara pagou Gabriel", valor: "66,77", moeda: "BRL", pagou: ["Clara"], dividir: ["Gabriel"], data: "2026-06-20", tipo: "acerto" },
  { desc: "Acerto — Fonte pagou Gabriel", valor: "27,76", moeda: "EUR", pagou: ["Fonte"], dividir: ["Gabriel"], data: "2026-06-20", tipo: "acerto" },
  { desc: "Acerto — Rosana pagou Gabriel", valor: "27,74", moeda: "EUR", pagou: ["Rosana"], dividir: ["Gabriel"], data: "2026-06-20", tipo: "acerto" },
  // Uber Sorrento: Fonte e Rosana já pagaram a parte (€10 cada) à Aline
  { desc: "Acerto — Fonte pagou Aline (Uber Sorrento)", valor: "10,00", moeda: "EUR", pagou: ["Fonte"], dividir: ["Aline"], tipo: "acerto" },
  { desc: "Acerto — Rosana pagou Aline (Uber Sorrento)", valor: "10,00", moeda: "EUR", pagou: ["Rosana"], dividir: ["Aline"], tipo: "acerto" },
];
