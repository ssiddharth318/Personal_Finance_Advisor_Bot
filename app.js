let kind = "expense";

document.querySelectorAll(".kind").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".kind").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    kind = btn.dataset.kind;
  });
});

document.getElementById("txForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = {
    kind,
    amount: document.getElementById("amount").value,
    category: document.getElementById("category").value,
    note: document.getElementById("note").value
  };
  const r = await fetch("/api/transactions", {
    method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(data)
  });
  if (!r.ok) { alert("Please enter valid details."); return; }
  e.target.reset();
  loadAll();
});

async function loadAll(){
  const [summary, rows, advice] = await Promise.all([
    fetch("/api/summary").then(r=>r.json()),
    fetch("/api/transactions").then(r=>r.json()),
    fetch("/api/advice").then(r=>r.json())
  ]);
  document.getElementById("income").textContent = "₹" + summary.income.toLocaleString("en-IN",{maximumFractionDigits:2});
  document.getElementById("expense").textContent = "₹" + summary.expense.toLocaleString("en-IN",{maximumFractionDigits:2});
  document.getElementById("balance").textContent = "₹" + summary.balance.toLocaleString("en-IN",{maximumFractionDigits:2});
  document.getElementById("adviceTitle").textContent = advice.title;
  document.getElementById("adviceText").textContent = advice.text;
  document.getElementById("transactions").innerHTML = rows.length ? rows.map(x => `
    <tr><td class="${x.kind}-row">${x.kind === "income" ? "↑ Income" : "↓ Expense"}</td>
    <td>${x.category}</td><td>₹${Number(x.amount).toLocaleString("en-IN")}</td>
    <td>${x.note || "—"}</td><td>${x.created_at}</td></tr>`).join("") :
    `<tr><td colspan="5" style="text-align:center;color:#89919f;padding:22px">No transactions yet. Add your first income or expense.</td></tr>`;
}
loadAll();
