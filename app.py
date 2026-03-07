from flask import Flask, render_template_string, jsonify, request
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Portal de Ações</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  :root {
    --bg: #0a0a0f; --surface: #111118; --border: #1e1e2e;
    --accent: #00ff88; --accent3: #f59e0b;
    --text: #e2e8f0; --muted: #64748b;
    --positive: #00ff88; --negative: #ef4444;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: var(--bg); color: var(--text); font-family: 'JetBrains Mono', monospace; min-height: 100vh; overflow-x: hidden; }
  body::before {
    content: ''; position: fixed; inset: 0;
    background-image: linear-gradient(rgba(0,255,136,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,136,0.03) 1px, transparent 1px);
    background-size: 40px 40px; pointer-events: none; z-index: 0;
  }
  .container { max-width: 1300px; margin: 0 auto; padding: 0 24px; position: relative; z-index: 1; }
  header { border-bottom: 1px solid var(--border); padding: 20px 0; margin-bottom: 40px; }
  .header-inner { display: flex; align-items: center; justify-content: space-between; gap: 20px; }
  .logo { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.4rem; color: var(--accent); }
  .logo span { color: var(--muted); font-weight: 400; }
  .search-bar { display: flex; gap: 10px; flex: 1; max-width: 440px; }
  .search-bar input {
    flex: 1; background: var(--surface); border: 1px solid var(--border);
    color: var(--text); padding: 10px 16px; font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem; outline: none; text-transform: uppercase; letter-spacing: 2px; transition: border-color 0.2s;
  }
  .search-bar input:focus { border-color: var(--accent); }
  .search-bar input::placeholder { color: var(--muted); letter-spacing: 1px; text-transform: none; }
  .btn {
    background: var(--accent); color: #000; border: none; padding: 10px 20px;
    font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.85rem;
    cursor: pointer; letter-spacing: 1px; transition: opacity 0.2s;
  }
  .btn:hover { opacity: 0.85; }
  .ticker-hero {
    display: flex; align-items: flex-end; justify-content: space-between;
    margin-bottom: 32px; flex-wrap: wrap; gap: 16px;
    opacity: 0; transform: translateY(20px); transition: all 0.5s ease;
  }
  .ticker-hero.visible { opacity: 1; transform: translateY(0); }
  .ticker-name { font-family: 'Syne', sans-serif; }
  .ticker-name h1 { font-size: 2.8rem; font-weight: 800; color: #fff; letter-spacing: -2px; }
  .ticker-name p { color: var(--muted); font-size: 0.8rem; letter-spacing: 1px; margin-top: 4px; }
  .ticker-price { text-align: right; }
  .ticker-price .price { font-size: 2.4rem; font-weight: 500; color: var(--accent); }
  .ticker-price .var { font-size: 0.85rem; margin-top: 4px; }
  .ticker-price .var.up { color: var(--positive); }
  .ticker-price .var.down { color: var(--negative); }
  .highlights {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1px; background: var(--border); border: 1px solid var(--border); margin-bottom: 32px;
    opacity: 0; transform: translateY(20px); transition: all 0.5s ease 0.1s;
  }
  .highlights.visible { opacity: 1; transform: translateY(0); }
  .hl-card { background: var(--surface); padding: 20px 18px; transition: background 0.2s; }
  .hl-card:hover { background: #15151f; }
  .hl-card .label { font-size: 0.68rem; color: var(--muted); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px; }
  .hl-card .value { font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 700; color: #fff; }
  .hl-card .value.accent { color: var(--accent); }
  .hl-card .value.amber { color: var(--accent3); }
  .sections {
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;
    opacity: 0; transform: translateY(20px); transition: all 0.5s ease 0.2s;
  }
  .sections.visible { opacity: 1; transform: translateY(0); }
  .section-full {
    margin-bottom: 16px;
    opacity: 0; transform: translateY(20px); transition: all 0.5s ease 0.3s;
  }
  .section-full.visible { opacity: 1; transform: translateY(0); }
  @media (max-width: 768px) { .sections { grid-template-columns: 1fr; } .ticker-name h1 { font-size: 2rem; } }
  .card { background: var(--surface); border: 1px solid var(--border); padding: 24px; }
  .card-title {
    font-family: 'Syne', sans-serif; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase; color: var(--muted); margin-bottom: 20px;
    display: flex; align-items: center; gap: 8px;
  }
  .card-title::after { content: ''; flex: 1; height: 1px; background: var(--border); }
  .indicator-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .indicator-row:last-child { border-bottom: none; }
  .ind-label { color: var(--muted); font-size: 0.78rem; }
  .ind-value { font-weight: 500; font-size: 0.9rem; color: var(--text); }
  .ind-value.highlight { color: var(--accent); }
  .ind-value.amber { color: var(--accent3); }
  .chart-wrapper { position: relative; height: 300px; }
  .osc-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 1px; background: var(--border); }
  .osc-item { background: var(--surface); padding: 14px; text-align: center; }
  .osc-item .osc-label { font-size: 0.65rem; color: var(--muted); letter-spacing: 1px; margin-bottom: 6px; }
  .osc-item .osc-val { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; }
  .osc-val.up { color: var(--positive); }
  .osc-val.down { color: var(--negative); }
  .loading { display: none; text-align: center; padding: 60px; color: var(--muted); }
  .loading.active { display: block; }
  .spinner {
    width: 32px; height: 32px; border: 2px solid var(--border);
    border-top-color: var(--accent); border-radius: 50%;
    animation: spin 0.8s linear infinite; margin: 0 auto 16px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .empty { text-align: center; padding: 80px 20px; color: var(--muted); }
  .empty .big { font-size: 3rem; margin-bottom: 16px; opacity: 0.3; }
  .empty p { font-size: 0.85rem; letter-spacing: 1px; }
  .error-msg { display: none; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); color: #fca5a5; padding: 16px 20px; font-size: 0.85rem; margin-bottom: 24px; }
  .error-msg.active { display: block; }
  footer { border-top: 1px solid var(--border); padding: 24px 0; margin-top: 40px; text-align: center; color: var(--muted); font-size: 0.72rem; letter-spacing: 1px; }
</style>
</head>
<body>
<header>
  <div class="container">
    <div class="header-inner">
      <div class="logo">STOCK<span>PANEL</span></div>
      <div class="search-bar">
        <input type="text" id="tickerInput" placeholder="Digite o ticker: PETR4, VALE3..." maxlength="10" />
        <button class="btn" onclick="buscar()">BUSCAR</button>
      </div>
    </div>
  </div>
</header>

<div class="container">
  <div class="error-msg" id="errorMsg"></div>
  <div class="loading" id="loading"><div class="spinner"></div><p>CARREGANDO DADOS...</p></div>

  <div id="emptyState" class="empty">
    <div class="big">📊</div>
    <p>DIGITE UM TICKER PARA COMEÇAR</p>
  </div>

  <div id="dashboard" style="display:none">
    <div class="ticker-hero" id="tickerHero">
      <div class="ticker-name">
        <h1 id="heroTicker"></h1>
        <p id="heroNome"></p>
      </div>
      <div class="ticker-price">
        <div class="price" id="heroPreco"></div>
        <div class="var" id="heroVar"></div>
      </div>
    </div>

    <div class="highlights" id="highlights">
      <div class="hl-card"><div class="label">P / L</div><div class="value accent" id="hlPL">—</div></div>
      <div class="hl-card"><div class="label">P / VP</div><div class="value" id="hlPVP">—</div></div>
      <div class="hl-card"><div class="label">DIV. YIELD</div><div class="value amber" id="hlDY">—</div></div>
      <div class="hl-card"><div class="label">ROE</div><div class="value" id="hlROE">—</div></div>
      <div class="hl-card"><div class="label">EV/EBITDA</div><div class="value" id="hlEV">—</div></div>
      <div class="hl-card"><div class="label">MARG. LÍQ.</div><div class="value" id="hlMarg">—</div></div>
    </div>

    <div class="section-full" id="secOsc">
      <div class="card">
        <div class="card-title">Oscilações</div>
        <div class="osc-grid" id="oscGrid"></div>
      </div>
    </div>

    <div class="sections" id="secIndicadores">
      <div class="card">
        <div class="card-title">Valuation</div>
        <div id="valuation"></div>
      </div>
      <div class="card">
        <div class="card-title">Rentabilidade & Balanço</div>
        <div id="rentabilidade"></div>
      </div>
    </div>

    <div class="section-full" id="secDividendos">
      <div class="card">
        <div class="card-title">Histórico de Dividendos — Mês a Mês</div>
        <div class="chart-wrapper"><canvas id="dividendChart"></canvas></div>
      </div>
    </div>

    <div class="section-full" id="secTabela">
      <div class="card">
        <div class="card-title">Pagamentos Detalhados</div>
        <div id="tabelaDividendos"></div>
      </div>
    </div>
  </div>
</div>

<footer><div class="container">DADOS: FUNDAMENTUS.COM.BR — ATUALIZAÇÃO EM TEMPO REAL</div></footer>

<script>
let chartInstance = null;

document.getElementById('tickerInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') buscar();
});

function buscar() {
  const ticker = document.getElementById('tickerInput').value.trim().toUpperCase();
  if (!ticker) return;
  document.getElementById('emptyState').style.display = 'none';
  document.getElementById('dashboard').style.display = 'none';
  document.getElementById('errorMsg').classList.remove('active');
  document.getElementById('loading').classList.add('active');
  ['tickerHero','highlights','secOsc','secIndicadores','secDividendos','secTabela'].forEach(id => {
    document.getElementById(id).classList.remove('visible');
  });

  fetch(`/dados?ticker=${ticker}`)
    .then(r => r.json())
    .then(data => {
      document.getElementById('loading').classList.remove('active');
      if (data.erro) {
        document.getElementById('errorMsg').textContent = '⚠ ' + data.erro;
        document.getElementById('errorMsg').classList.add('active');
        return;
      }
      renderDashboard(data, ticker);
    })
    .catch(() => {
      document.getElementById('loading').classList.remove('active');
      document.getElementById('errorMsg').textContent = '⚠ Erro ao buscar dados. Tente novamente.';
      document.getElementById('errorMsg').classList.add('active');
    });
}

function colorVal(v) {
  if (!v || v === 'N/A') return '';
  const n = parseFloat(v.toString().replace(',', '.').replace('%',''));
  return isNaN(n) ? '' : (n >= 0 ? 'up' : 'down');
}

function row(label, value, cls='') {
  return `<div class="indicator-row">
    <span class="ind-label">${label}</span>
    <span class="ind-value ${cls}">${value || 'N/A'}</span>
  </div>`;
}

function renderDashboard(d, ticker) {
  const f = d.fundamentus;
  const divs = d.dividendos;

  document.getElementById('heroTicker').textContent = ticker;
  document.getElementById('heroNome').textContent = f['Empresa'] || '';
  document.getElementById('heroPreco').textContent = 'R$ ' + (f['Cotação'] || '—');
  const varDia = f['Dia'] || '';
  const varEl = document.getElementById('heroVar');
  varEl.textContent = 'Variação do dia: ' + varDia;
  varEl.className = 'var ' + colorVal(varDia);

  document.getElementById('hlPL').textContent   = f['P/L'] || '—';
  document.getElementById('hlPVP').textContent  = f['P/VP'] || '—';
  document.getElementById('hlDY').textContent   = f['Div. Yield'] || '—';
  document.getElementById('hlROE').textContent  = f['ROE'] || '—';
  document.getElementById('hlEV').textContent   = f['EV / EBITDA'] || '—';
  document.getElementById('hlMarg').textContent = f['Marg. Líquida'] || '—';

  const oscs = [
    {l:'DIA', v:f['Dia']}, {l:'MÊS', v:f['Mês']}, {l:'30 DIAS', v:f['30 dias']},
    {l:'12 MESES', v:f['12 meses']}, {l:'2026', v:f['2026']}, {l:'2025', v:f['2025']},
    {l:'2024', v:f['2024']}, {l:'2023', v:f['2023']},
  ];
  document.getElementById('oscGrid').innerHTML = oscs.map(o =>
    `<div class="osc-item"><div class="osc-label">${o.l}</div><div class="osc-val ${colorVal(o.v)}">${o.v || 'N/A'}</div></div>`
  ).join('');

  document.getElementById('valuation').innerHTML =
    row('Cotação', 'R$ ' + f['Cotação']) +
    row('P/L', f['P/L'], 'highlight') +
    row('P/VP', f['P/VP']) +
    row('P/EBIT', f['P/EBIT']) +
    row('PSR', f['PSR']) +
    row('EV/EBITDA', f['EV / EBITDA']) +
    row('EV/EBIT', f['EV / EBIT']) +
    row('LPA', 'R$ ' + f['LPA']) +
    row('VPA', 'R$ ' + f['VPA']) +
    row('Valor de Mercado', 'R$ ' + f['Valor de mercado']) +
    row('Valor da Firma', 'R$ ' + f['Valor da firma']) +
    row('Nro. Ações', f['Nro. Ações']);

  document.getElementById('rentabilidade').innerHTML =
    row('Div. Yield', f['Div. Yield'], 'amber') +
    row('ROE', f['ROE']) +
    row('ROIC', f['ROIC']) +
    row('Marg. Bruta', f['Marg. Bruta']) +
    row('Marg. EBIT', f['Marg. EBIT']) +
    row('Marg. Líquida', f['Marg. Líquida']) +
    row('Dív. Bruta', 'R$ ' + f['Dív. Bruta']) +
    row('Dív. Líquida', 'R$ ' + f['Dív. Líquida']) +
    row('Div Br/Patrim', f['Div Br/ Patrim']) +
    row('Liquidez Corr', f['Liquidez Corr']) +
    row('Patrim. Líq', 'R$ ' + f['Patrim. Líq']) +
    row('Cres. Rec (5a)', f['Cres. Rec (5a)']);

  renderChart(divs);

  if (divs && divs.length > 0) {
    document.getElementById('tabelaDividendos').innerHTML = `
      <table style="width:100%;border-collapse:collapse;font-size:0.8rem;">
        <thead>
          <tr style="border-bottom:1px solid #1e1e2e;">
            <th style="text-align:left;padding:10px 8px;color:#64748b;letter-spacing:1px;font-size:0.68rem;">DATA COM</th>
            <th style="text-align:right;padding:10px 8px;color:#64748b;letter-spacing:1px;font-size:0.68rem;">VALOR (R$)</th>
            <th style="text-align:left;padding:10px 8px;color:#64748b;letter-spacing:1px;font-size:0.68rem;">TIPO</th>
            <th style="text-align:left;padding:10px 8px;color:#64748b;letter-spacing:1px;font-size:0.68rem;">DATA PGTO</th>
          </tr>
        </thead>
        <tbody>
          ${divs.slice(0, 40).map(d => `
            <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
              <td style="padding:10px 8px;color:#94a3b8;">${d.data_com}</td>
              <td style="padding:10px 8px;text-align:right;color:#00ff88;font-weight:500;">R$ ${d.valor}</td>
              <td style="padding:10px 8px;color:#e2e8f0;">${d.tipo}</td>
              <td style="padding:10px 8px;color:#64748b;">${d.data_pgto || '—'}</td>
            </tr>`).join('')}
        </tbody>
      </table>`;
  } else {
    document.getElementById('tabelaDividendos').innerHTML = '<p style="color:#64748b;padding:20px;text-align:center;font-size:0.8rem;">Nenhum dividendo encontrado.</p>';
  }

  document.getElementById('dashboard').style.display = 'block';
  setTimeout(() => {
    ['tickerHero','highlights','secOsc','secIndicadores','secDividendos','secTabela'].forEach(id => {
      document.getElementById(id).classList.add('visible');
    });
  }, 50);
}

function renderChart(divs) {
  if (!divs || divs.length === 0) return;

  const mensal = {};
  divs.forEach(d => {
    const p = d.data_com.split('/');
    if (p.length < 3) return;
    const chave = `${p[2]}-${p[1]}`;
    const val = parseFloat(d.valor.replace(',', '.'));
    if (!isNaN(val)) mensal[chave] = (mensal[chave] || 0) + val;
  });

  const labels = Object.keys(mensal).sort().slice(-36);
  const valores = labels.map(l => mensal[l]);
  const meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];

  if (chartInstance) chartInstance.destroy();
  const ctx = document.getElementById('dividendChart').getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, 'rgba(0,255,136,0.4)');
  gradient.addColorStop(1, 'rgba(0,255,136,0.01)');

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.map(l => { const [a,m] = l.split('-'); return meses[parseInt(m)-1]+'/'+a.slice(2); }),
      datasets: [{
        label: 'Dividendo (R$)',
        data: valores,
        backgroundColor: gradient,
        borderColor: '#00ff88',
        borderWidth: 1,
        borderRadius: 2,
        hoverBackgroundColor: 'rgba(0,255,136,0.6)',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#111118', borderColor: '#1e1e2e', borderWidth: 1,
          titleColor: '#64748b', bodyColor: '#00ff88',
          titleFont: { family: 'JetBrains Mono', size: 11 },
          bodyFont: { family: 'JetBrains Mono', size: 13, weight: '500' },
          callbacks: { label: ctx => 'R$ ' + ctx.parsed.y.toFixed(4) }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.03)' },
          ticks: { color: '#475569', font: { family: 'JetBrains Mono', size: 10 }, maxRotation: 45 },
          border: { color: '#1e1e2e' }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#475569', font: { family: 'JetBrains Mono', size: 10 }, callback: v => 'R$ ' + v.toFixed(2) },
          border: { color: '#1e1e2e' }
        }
      }
    }
  });
}
</script>
</body>
</html>
"""

def scrape_fundamentus(ticker):
    scraper = cloudscraper.create_scraper()
    url = f"https://www.fundamentus.com.br/detalhes.php?papel={ticker}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = scraper.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    dados = {}
    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        for i in range(0, len(cols) - 1, 2):
            label = cols[i].get_text(strip=True).replace("?", "").strip()
            valor = cols[i+1].get_text(strip=True)
            if label:
                dados[label] = valor
    return dados

def scrape_dividendos(ticker):
    scraper = cloudscraper.create_scraper()
    url = f"https://www.fundamentus.com.br/proventos.php?papel={ticker}&tipo=2"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = scraper.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    dividendos = []
    tabela = soup.find("table", {"id": "resultado"})
    if not tabela:
        return dividendos
    for row in tabela.find_all("tr")[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) >= 3:
            dividendos.append({
                "data_com":  cols[0],
                "valor":     cols[1],
                "tipo":      cols[2],
                "data_pgto": cols[3] if len(cols) > 3 else ""
            })
    return dividendos

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/dados")
def dados():
    ticker = request.args.get("ticker", "").upper().strip()
    if not ticker:
        return jsonify({"erro": "Ticker não informado."})
    try:
        f = scrape_fundamentus(ticker)
        if not f or "Cotação" not in f:
            return jsonify({"erro": f"Ticker '{ticker}' não encontrado."})
        d = scrape_dividendos(ticker)
        return jsonify({"fundamentus": f, "dividendos": d})
    except Exception as e:
        return jsonify({"erro": str(e)})
