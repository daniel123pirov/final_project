// client/script.js
// =====================================
// Clé (sessionStorage) + modal thème + déchiffrement côté front
// =====================================

let globalKey = null;

// --- storage ---
function loadStoredKey(){ try { return sessionStorage.getItem('kl_key') || null; } catch { return null; } }
function storeKey(v){ try { if (v) sessionStorage.setItem('kl_key', v); } catch {} }
globalKey = loadStoredKey();

// --- base URL ---
function baseUrl(){
  return (document.getElementById("baseUrl")?.value || "http://127.0.0.1:5001").trim().replace(/\/$/,'');
}

// --- modal (thème du site) : inject + open ---
function ensureKeyModalInjected(){
  if (!document.getElementById("km-style")){
    const style = document.createElement("style");
    style.id = "km-style";
    style.textContent = `
      .km-overlay{ position:fixed; inset:0; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,.55); z-index:9999; }
      .km-dialog{ width:min(92vw,480px); background:linear-gradient(180deg, rgba(46,165,101,.06), transparent 70%) #111712;
        border:1px solid #1b2a1e; border-radius:12px; padding:18px; color:#e2f7e7;
        box-shadow:0 0 18px rgba(46,165,101,.12), inset 0 0 0 1px rgba(46,165,101,.05);
        font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace; text-align:right; }
      .km-title{ font-weight:800; color:#a5dfbe; margin:0 0 8px; }
      .km-desc{ color:#9cc8a7; font-size:13px; margin:0 0 12px; }
      .km-input{ width:100%; padding:10px 12px; border-radius:8px; background:#0c130e; color:#e2f7e7; border:1px solid #1b2a1e; outline:none; }
      .km-actions{ display:flex; gap:8px; margin-top:12px; }
      .km-btn{ padding:10px 14px; border-radius:8px; cursor:pointer; font-weight:800; border:0; background:#2ea565; color:#06150c; }
      .km-btn:hover{ background:#278c55; }
      .km-btn.ghost{ background:transparent; color:#2ea565; border:1px solid #2ea565; }
      .km-btn.ghost:hover{ background:rgba(46,165,101,.12); }
    `;
    document.head.appendChild(style);
  }
  if (!document.getElementById("km-overlay")){
    const overlay = document.createElement("div");
    overlay.id = "km-overlay";
    overlay.className = "km-overlay";
    overlay.style.display = "none";
    overlay.innerHTML = `
      <div class="km-dialog" role="dialog" aria-modal="true" aria-labelledby="km-title">
  <h3 id="km-title" class="km-title">🔑 Enter Decryption Key</h3>
  <p class="km-desc">The data is encrypted. Without the key, the content cannot be displayed.</p>
  <input id="km-input" class="km-input" type="password" placeholder="Decryption Key" />
  <div class="km-actions">
    <button id="km-ok" class="km-btn" type="button">OK</button>
    <button id="km-cancel" class="km-btn ghost" type="button">Cancel</button>
  </div>
</div>
      </div>`;
    document.body.appendChild(overlay);
  }
}

function openKeyModal(){
  ensureKeyModalInjected();
  return new Promise((resolve)=>{
    const ov = document.getElementById("km-overlay");
    const inp = document.getElementById("km-input");
    const ok = document.getElementById("km-ok");
    const cancel = document.getElementById("km-cancel");

    function cleanup(v){
      ov.style.display = "none";
      ok.removeEventListener("click", onOK);
      cancel.removeEventListener("click", onCancel);
      inp.removeEventListener("keydown", onKey);
      resolve(v);
    }
    function onOK(){
      const v = (inp.value||"").trim();
      if (!v){ inp.focus(); return; }
      globalKey = v; storeKey(v);
      cleanup(v);
    }
    function onCancel(){ cleanup(null); }
    function onKey(e){
      if (e.key === "Enter"){ e.preventDefault(); onOK(); }
      if (e.key === "Escape"){ e.preventDefault(); onCancel(); }
    }

    ov.style.display = "flex";
    inp.value = "";
    setTimeout(()=>inp.focus(),0);
    ok.addEventListener("click", onOK);
    cancel.addEventListener("click", onCancel);
    inp.addEventListener("keydown", onKey);
  });
}

// --- utils ---
function xorDecryptHex(cipherHex, key){
  if (!cipherHex || !cipherHex.startsWith("ENC:")) return cipherHex || "";
  const hex = cipherHex.slice(4);
  const bytes = new Uint8Array(hex.match(/.{1,2}/g).map(b=>parseInt(b,16)));
  const keyBytes = new TextEncoder().encode(key);
  const out = new Uint8Array(bytes.length);
  for (let i=0;i<bytes.length;i++) out[i] = bytes[i] ^ keyBytes[i % keyBytes.length];
  return new TextDecoder().decode(out);
}
function showConsole(el,msg){ el.innerHTML = `<div class="console">${msg}</div>`; }

// =====================================
// HOME : bouton חיפוש → exige la clé → redirige
// =====================================
document.addEventListener("DOMContentLoaded", ()=>{
  const page = document.body?.dataset?.page || "";

  if (page === "home"){
    const goSearch = document.getElementById("goSearch");
    if (goSearch){
      goSearch.addEventListener("click", async (e)=>{
        e.preventDefault();
        // exige la clé (popup). Si annule → on reste sur l'accueil
        const v = await openKeyModal();
        if (v) window.location.href = "search.html";
      });
    }
  }

  if (page === "search"){
    // Si on arrive sans clé (URL directe), on renvoie vers l'accueil qui demandera la clé
    if (!globalKey){
      window.location.href = "index.html";
      return;
    }
    bindSearch();
  }

  if (page === "manager"){
    // Plus de popup bloquant au démarrage, on charge directement les machines
    loadMachines();
  }
});

// =====================================
// SEARCH
// =====================================
function bindSearch(){
  const btnSearch = document.getElementById("btnSearch");
  if (btnSearch){
    btnSearch.addEventListener("click", searchLogs);
    ["searchMachine","searchDate","searchKeywords"].forEach(id=>{
      const el = document.getElementById(id);
      if (el) el.addEventListener("keydown",(e)=>{ if (e.key==="Enter") searchLogs(); });
    });
  }
}

async function searchLogs(){
  const container = document.getElementById("searchResults");
  const key = globalKey; // garanti présent (gating à l'entrée)
  const machine = document.getElementById("searchMachine").value.trim();
  const date = document.getElementById("searchDate").value.trim();
  const q = document.getElementById("searchKeywords").value.trim();

  showConsole(container, "⏳ Searching...");

  const url = new URL(baseUrl()+"/api/search");
  if (machine) url.searchParams.set("machine_name", machine);
  if (date) url.searchParams.set("date", date);
  if (q) url.searchParams.set("q", q);

  try{
    const res = await fetch(url.toString());
    const json = await res.json();
    if (!json.results || !json.results.length){
      showConsole(container, "(No Results)");
      return;
    }
    const table = document.createElement("table");
    table.innerHTML = `<thead><tr><th>Computer</th><th>Date</th><th>Line</th></tr></thead><tbody></tbody>`;
    const tb = table.querySelector("tbody");

    json.results.forEach(r=>{
      const tr = document.createElement("tr");
      let line = r.line;
      try { line = xorDecryptHex(r.line, key); } catch {}
      tr.innerHTML = `<td>${r.machine}</td><td>${r.date}</td><td>${line}</td>`;
      tb.appendChild(tr);
    });

    container.innerHTML = "";
    container.appendChild(table);
  } catch(e){
    showConsole(container, "❌ Error: "+e.message);
  }
}

// =====================================
// MANAGER (machines → dates → log)
// =====================================
const machinesList = document.getElementById("machinesList");
const datesList = document.getElementById("datesList");
const logViewer = document.getElementById("logViewer");

async function loadMachines(){
  if (!machinesList) return;
  machinesList.innerHTML = "<li>Loading...</li>";
  try{
    const res = await fetch(baseUrl()+"/api/machines");
    const json = await res.json();
    machinesList.innerHTML = "";
    (json.machines||[]).forEach(name=>{
      const li = document.createElement("li");
      li.textContent = name;
      li.addEventListener("click", ()=>loadDates(name, li));
      machinesList.appendChild(li);
    });
  } catch {
    machinesList.innerHTML = "<li>Error</li>";
  }
}

async function loadDates(machine, liEl){
  [...machinesList.children].forEach(li=>li.classList.remove("active"));
  liEl.classList.add("active");
  datesList.innerHTML = "<li>Loading...</li>";
  if (logViewer) logViewer.textContent = "(Choose Date)";
  try{
    const res = await fetch(baseUrl()+`/api/dates?machine_name=${encodeURIComponent(machine)}`);
    const json = await res.json();
    datesList.innerHTML = "";
    (json.dates||[]).forEach(d=>{
      const li = document.createElement("li");
      li.textContent = d;
      li.addEventListener("click", ()=>loadLog(machine, d, li));
      datesList.appendChild(li);
    });
  } catch {
    datesList.innerHTML = "<li>Error</li>";
  }
}

async function loadLog(machine, date, liEl){
  // Popup obligatoire à chaque clic sur date (comme le bouton search dans home)
  const key = await openKeyModal();
  if (!key){
    if (logViewer) logViewer.textContent = "(No Key)";
    return;
  }

  [...datesList.children].forEach(li=>li.classList.remove("active"));
  liEl.classList.add("active");
  if (logViewer) logViewer.textContent = "⏳ Loading...";

  try{
    const url = new URL(baseUrl()+"/api/log");
    url.searchParams.set("machine_name", machine);
    url.searchParams.set("date", date);
    const res = await fetch(url.toString());
    const json = await res.json();

    const lines = (json.lines||[]).map(L=>{
      const [ts = "", cipher = ""] = L.split("\t"); // "[ts]\tENC:...."
      let plain = cipher;
      try { plain = xorDecryptHex(cipher, key); } catch {}
      return `${ts} ${plain}`;
    });
    if (logViewer) logViewer.textContent = lines.length ? lines.join("\n") : "(No Content)";
  } catch {
    if (logViewer) logViewer.textContent = "Loading Error";
  }
}