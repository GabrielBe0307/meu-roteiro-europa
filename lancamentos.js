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
];
