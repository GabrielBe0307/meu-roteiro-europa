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
];
