/* ============================================================
   LANÇAMENTOS DA VIAGEM — ENCONTRO DE CONTAS FINAL
   ------------------------------------------------------------
   O histórico anterior já foi acertado entre todos, então aqui
   ficam APENAS os lançamentos em aberto (o acerto final).

   Formato de cada lançamento:
   {
     desc:    "Descrição do gasto",
     valor:   "45,90",          // aceita vírgula ou ponto
     moeda:   "EUR",            // "EUR" (€) ou "BRL" (R$)
     pagou:   ["Gabriel"],      // quem pagou (se +1, divide igual o que foi pago)
     dividir: TODOS,            // quem participa da divisão (custo rachado igual)
     tipo:    "acerto"          // opcional; marca pagamentos que quitam dívida
   }

   Atalho: use TODOS para marcar as 6 pessoas de uma vez.
   ============================================================ */

const TODOS = ["Gabriel", "Clara", "Aline", "Renan", "Fonte", "Rosana"];

window.LANCAMENTOS = [
  // ----- Aline pagou -----
  { desc: "Van Castellammare–Vico Equense (ida)", valor: "9,00", moeda: "EUR", pagou: ["Aline"], dividir: ["Fonte", "Gabriel", "Rosana"] },
  { desc: "Restaurante do hotel (pizza)", valor: "68,00", moeda: "EUR", pagou: ["Aline"], dividir: TODOS },
  { desc: "Táxi Capri (ida e volta)", valor: "60,00", moeda: "EUR", pagou: ["Aline"], dividir: TODOS },
  { desc: "Uber Sorrento → hotel", valor: "50,00", moeda: "EUR", pagou: ["Aline"], dividir: ["Gabriel", "Clara", "Aline", "Fonte", "Rosana"] },
  { desc: "Uber aeroporto Fiumicino (Roma)", valor: "37,00", moeda: "EUR", pagou: ["Aline"], dividir: TODOS },

  // ----- Clara pagou -----
  { desc: "Van Castellammare", valor: "12,00", moeda: "EUR", pagou: ["Clara"], dividir: ["Renan", "Gabriel", "Fonte", "Rosana"] },

  // ----- Clara e Gabriel pagaram -----
  { desc: "Vinho", valor: "25,00", moeda: "EUR", pagou: ["Clara", "Gabriel"], dividir: ["Aline", "Renan", "Gabriel", "Clara"] },

  // ----- Renan pagou -----
  { desc: "Taxa do Booking", valor: "21,35", moeda: "EUR", pagou: ["Renan"], dividir: TODOS },
  { desc: "Passeio Coliseu", valor: "1170,71", moeda: "BRL", pagou: ["Renan"], dividir: ["Rosana", "Fonte", "Renan", "Aline"] },
  { desc: "Hotel (Airbnb aeroporto)", valor: "1658,16", moeda: "BRL", pagou: ["Renan"], dividir: TODOS },

  // ----- Fonte pagou -----
  { desc: "Táxi Capri (ida e volta)", valor: "60,00", moeda: "EUR", pagou: ["Fonte"], dividir: TODOS },

  // ----- Gabriel pagou -----
  { desc: "Marinheiro (barqueiro)", valor: "40,00", moeda: "EUR", pagou: ["Gabriel"], dividir: TODOS },

  // ----- Acertos já feitos (parte do Uber Sorrento: €10 cada à Aline) -----
  { desc: "Acerto — Fonte pagou Aline (Uber Sorrento)", valor: "10,00", moeda: "EUR", pagou: ["Fonte"], dividir: ["Aline"], tipo: "acerto" },
  { desc: "Acerto — Rosana pagou Aline (Uber Sorrento)", valor: "10,00", moeda: "EUR", pagou: ["Rosana"], dividir: ["Aline"], tipo: "acerto" },
];
