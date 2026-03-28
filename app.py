from flask import Flask, jsonify, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = 'monitoring.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>IoT Power Monitor</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family:Arial; background:#0f172a; color:white; padding:20px; }
    h1 { text-align:center; color:#94a3b8; margin-bottom:6px; font-size:22px; }
    .sub { text-align:center; color:#475569; font-size:12px; margin-bottom:20px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px; max-width:900px; margin:0 auto 20px; }
    .card { background:#1e293b; border-radius:12px; padding:16px; text-align:center; }
    .card .val { font-size:32px; font-weight:bold; margin:8px 0; }
    .card .unit { font-size:12px; color:#94a3b8; }
    .card .lbl { font-size:11px; color:#64748b; margin-top:4px; }
    .c1 .val{color:#f97316;} .c2 .val{color:#38bdf8;}
    .c3 .val{color:#a78bfa;} .c4 .val{color:#34d399;}
    .c5 .val{color:#fb7185;} .c6 .val{color:#fbbf24;}
    .c7 .val{color:#f97316;} .c8 .val{color:#38bdf8;}
    .table-wrap { max-width:900px; margin:0 auto; overflow-x:auto; }
    table { width:100%; border-collapse:collapse; font-size:13px; }
    th { background:#1e293b; padding:10px; text-align:left; color:#94a3b8; }
    td { padding:8px 10px; border-bottom:1px solid #1e293b; }
    tr:hover td { background:#1e293b; }
    .Normal { color:#86efac; } .Warning { color:#fbbf24; } .Alert { color:#f87171; }
    .status-bar { max-width:900px; margin:0 auto 16px; padding:10px 16px; border-radius:10px; text-align:center; font-size:14px; }
    .ok { background:#166534; color:#86efac; }
    .warn { background:#7f1d1d; color:#fca5a5; }
  </style>
</head>
<body>
  <h1>IoT Power & Environment Monitor</h1>
  <p class="sub">Data diperbarui setiap 3 detik</p>

  <div class="grid">
    <div class="card c1"><div class="val" id="v">--</div><div class="unit">V</div><div class="lbl">Tegangan</div></div>
    <div class="card c2"><div class="val" id="i">--</div><div class="unit">A</div><div class="lbl">Arus</div></div>
    <div class="card c3"><div class="val" id="p">--</div><div class="unit">W</div><div class="lbl">Daya</div></div>
    <div class="card c4"><div class="val" id="e">--</div><div class="unit">kWh</div><div class="lbl">Energi</div></div>
    <div class="card c5"><div class="val" id="f">--</div><div class="unit">Hz</div><div class="lbl">Frekuensi</div></div>
    <div class="card c6"><div class="val" id="pf">--</div><div class="unit">PF</div><div class="lbl">Power Factor</div></div>
    <div class="card c7"><div class="val" id="t">--</div><div class="unit">°C</div><div class="lbl">Suhu</div></div>
    <div class="card c8"><div class="val" id="h">--</div><div class="unit">%</div><div class="lbl">Kelembaban</div></div>
  </div>

  <div class="status-bar ok" id="st">Memuat data...</div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Waktu</th>
          <th>Tegangan (V)</th>
          <th>Arus (A)</th>
          <th>Daya (W)</th>
          <th>Suhu (°C)</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody id="tbl"></tbody>
    </table>
  </div>

  <script>
    function update() {
      fetch('/api/latest')
        .then(r => r.json())
        .then(d => {
          document.getElementById('v').textContent = d.voltage.toFixed(1);
          document.getElementById('i').textContent = d.current.toFixed(2);
          document.getElementById('p').textContent = d.power.toFixed(1);
          document.getElementById('e').textContent = d.energy.toFixed(3);
          document.getElementById('f').textContent = d.frequency.toFixed(1);
          document.getElementById('pf').textContent = d.power_factor.toFixed(2);
          document.getElementById('t').textContent = d.suhu.toFixed(1);
          document.getElementById('h').textContent = d.kelembaban.toFixed(1);
          const st = document.getElementById('st');
          if (d.status === 'Alert') {
            st.textContent = '🚨 ALERT! Periksa sistem segera!';
            st.className = 'status-bar warn';
          } else if (d.status === 'Warning') {
            st.textContent = '⚠️ Warning! Parameter di luar batas normal';
            st.className = 'status-bar warn';
          } else {
            st.textContent = '✅ Semua Parameter Normal';
            st.className = 'status-bar ok';
          }
        });

      fetch('/api/history')
        .then(r => r.json())
        .then(rows => {
          const tbody = document.getElementById('tbl');
          tbody.innerHTML = rows.map(r => `
            <tr>
              <td>${r.timestamp}</td>
              <td>${r.voltage.toFixed(1)}</td>
              <td>${r.current.toFixed(2)}</td>
              <td>${r.power.toFixed(1)}</td>
              <td>${r.suhu.toFixed(1)}</td>
              <td class="${r.status}">${r.status}</td>
            </tr>
          `).join('');
        });
    }
    update();
    setInterval(update, 3000);
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/latest')
def latest():
    db = get_db()
    row = db.execute('SELECT * FROM sensor_data ORDER BY id DESC LIMIT 1').fetchone()
    return jsonify(dict(row))

@app.route('/api/history')
def history():
    db = get_db()
    rows = db.execute('SELECT * FROM sensor_data ORDER BY id DESC LIMIT 10').fetchall()
    return jsonify([dict(r) for r in rows])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
