import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, send_file
import sqlite3
from io import BytesIO
import re

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = False
if DATABASE_URL:
    try:
        import psycopg2
        USE_POSTGRES = True
    except:
        USE_POSTGRES = False

def get_conn():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    else:
        conn = sqlite3.connect('barbearia.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute('CREATE TABLE IF NOT EXISTS produtos (id SERIAL PRIMARY KEY, nome TEXT, preco REAL, estoque INTEGER, categoria TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS servicos (id SERIAL PRIMARY KEY, cliente TEXT, servico TEXT, valor REAL, data TEXT, pagamento TEXT, produtos_usados TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS mensalistas (id SERIAL PRIMARY KEY, nome TEXT, telefone TEXT, plano TEXT, valor REAL)')
    else:
        cur.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, preco REAL, estoque INTEGER, categoria TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS servicos (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, servico TEXT, valor REAL, data TEXT, pagamento TEXT, produtos_usados TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS mensalistas (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, telefone TEXT, plano TEXT, valor REAL)')
    conn.commit()
    conn.close()

BASE = """
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rei da Navalha</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{background:#0a1931;color:#222;font-family:Inter,Arial;margin:0}
.navbar-custom{background:#fff!important;border-bottom:4px solid #c4002b;padding:10px 15px;display:flex;justify-content:space-between;align-items:center;position:relative;flex-wrap:wrap}
.logo{font-weight:900;font-size:22px;line-height:1.1}
.logo span{color:#c4002b}
.nav-links{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.btn-nav{background:#eee;color:#333;border:none;border-radius:20px;padding:6px 14px;font-weight:700;font-size:14px;text-decoration:none}
.btn-nav.active{background:#000;color:#fff}
.btn-new{background:#c4002b;color:#fff;border:none;border-radius:20px;padding:6px 16px;font-weight:900}
.hamburger{display:none;background:#000;color:#fff;border:none;border-radius:10px;padding:8px 12px;font-size:18px}
@media(max-width:768px){
 .nav-links{display:none;flex-direction:column;position:absolute;top:100%;left:0;right:0;background:#fff;z-index:999;padding:15px;box-shadow:0 10px 20px rgba(0,0,0,.2);border-bottom:4px solid #c4002b}
 .nav-links.show{display:flex}
 .hamburger{display:block}
 .btn-nav,.btn-new{width:100%;text-align:center}
}
.card-white{background:#fff;border-radius:18px;padding:20px;box-shadow:0 4px 15px rgba(0,0,0,.1)}
.input-dark{background:#f5f5f7;border:1px solid #ddd;border-radius:12px;padding:12px;font-weight:600;width:100%}
.produto-item{background:#f9f9f9;border:1px solid #eee;border-radius:12px;padding:12px 14px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;cursor:pointer}
.produto-item.selected{background:#fff0f2;border-color:#c4002b}
.total-box{background:#fff8c5;border:1px solid #f0e08c;border-radius:10px;padding:12px;font-weight:900;text-align:center}
</style>
</head><body>
<nav class="navbar-custom">
  <div class="logo">👑 REI<br>DA <span>NAVALHA</span></div>
  <button class="hamburger" onclick="toggleMenu()">☰</button>
  <div class="nav-links" id="navLinks">
    <a href="/" class="btn-nav active">Início</a>
    <a href="/mensalistas" class="btn-nav">Mensalistas</a>
    <a href="/produtos" class="btn-nav">Produtos</a>
    <a href="/historico" class="btn-nav">Histórico</a>
    <a href="/nova" class="btn-new">+ Novo</a>
  </div>
</nav>
<div class="container py-4" style="max-width:900px">{{content|safe}}</div>
<script>
function toggleMenu(){
  document.getElementById('navLinks').classList.toggle('show');
}
</script>
</body></html>
"""

@app.route('/')
def index():
    init_db()
    conn = get_conn(); cur = conn.cursor()
    try: cur.execute("SELECT COUNT(*) FROM servicos"); total = cur.fetchone()[0]
    except: total=0
    try: cur.execute("SELECT COALESCE(SUM(valor),0) FROM servicos"); fat = cur.fetchone()[0] or 0
    except: fat=0
    conn.close()
    html = f"""
    <div class="row g-3">
      <div class="col-6"><div class="card-white"><b style="font-size:28px">{total}</b><br>Atendimentos</div></div>
      <div class="col-6"><div class="card-white"><b style="font-size:28px">R$ {float(fat):.2f}</b><br>Faturado</div></div>
      <div class="col-12"><a href="/nova" class="btn-new w-100 py-3 d-block text-center text-decoration-none" style="border-radius:14px">+ NOVO ATENDIMENTO</a></div>
    </div>
    """
    return render_template_string(BASE, content=html)

@app.route('/nova', methods=['GET','POST'])
def nova():
    init_db()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM produtos WHERE estoque > 0 ORDER BY nome ASC"); produtos = cur.fetchall()

    # Serviços fixos da barbearia
    servicos_lista = [("Corte - R$ 30", 30), ("Barba - R$ 30", 30), ("Corte + Barba - R$ 50", 50), ("Pezinho - R$ 15", 15), ("Sobrancelha - R$ 10", 10)]

    if request.method == 'POST':
        cliente = request.form.get('cliente','')
        pagamento = request.form.get('pagamento','')
        servico = request.form.get('servico','')
        valor = request.form.get('valor_total','0')
        selecionados = request.form.getlist('produtos')
        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        nomes=[]
        for pid in selecionados:
            try:
                if USE_POSTGRES: cur.execute("SELECT nome FROM produtos WHERE id=%s", (int(pid),))
                else: cur.execute("SELECT nome FROM produtos WHERE id=?", (int(pid),))
                r = cur.fetchone()
                if r: nomes.append(r[0] if USE_POSTGRES else r['nome'])
                if USE_POSTGRES: cur.execute("UPDATE produtos SET estoque = estoque -1 WHERE id=%s", (int(pid),))
                else: cur.execute("UPDATE produtos SET estoque = estoque -1 WHERE id=?", (int(pid),))
            except: pass
        prod_txt = ", ".join(nomes)
        if USE_POSTGRES: cur.execute("INSERT INTO servicos (cliente, servico, valor, data, pagamento, produtos_usados) VALUES (%s,%s,%s,%s,%s,%s)", (cliente, servico, valor, data, pagamento, prod_txt))
        else: cur.execute("INSERT INTO servicos (cliente, servico, valor, data, pagamento, produtos_usados) VALUES (?,?,?,?,?,?)", (cliente, servico, valor, data, pagamento, prod_txt))
        conn.commit(); conn.close(); return redirect('/')

    conn.close()
    options_serv = ""
    for nome, preco in servicos_lista:
        options_serv += f'<option value="{nome}" data-preco="{preco}">{nome}</option>'

    lista_prod=""
    for r in produtos:
        id_, nome, preco, est, cat = (r[0], r[1], r[2], r[3], r[4] if len(r)>4 else "") if USE_POSTGRES else (r['id'], r['nome'], r['preco'], r['estoque'], r['categoria'] if 'categoria' in r.keys() else "")
        lista_prod += f"""
        <div class="produto-item" id="item-{id_}" data-preco="{float(preco or 0)}" onclick="toggleProd({id_})">
          <div><span style="background:#c4002b;color:#fff;border-radius:12px;padding:2px 8px;font-size:11px;font-weight:800">{cat or 'Produto'}</span> <b>{nome}</b><br><span style="font-size:13px">R$ {float(preco or 0):.2f}</span></div>
          <div><input type="checkbox" name="produtos" value="{id_}" id="chk-{id_}" style="display:none"><span id="ok-{id_}" style="font-weight:900">OK</span></div>
        </div>"""

    html = f"""
    <div class="card-white">
      <h4 class="fw-bold">Novo Atendimento</h4>
      <form method="POST">
        <label class="fw-bold small mt-3">CLIENTE *</label>
        <input name="cliente" class="input-dark" required>

        <label class="fw-bold small mt-3">PAGAMENTO</label>
        <select name="pagamento" class="input-dark"><option>Cartao</option><option>Pix</option><option>Dinheiro</option><option>Mensalista</option></select>

        <div class="row g-2 mt-3">
          <div class="col-6"><label class="fw-bold small">SERVICO</label>
            <select name="servico" id="servico_select" class="input-dark" onchange="atualizaServico()">{options_serv}</select>
          </div>
          <div class="col-3"><label class="fw-bold small">VALOR</label><input id="valor_servico" class="input-dark" value="30" type="number" oninput="calcTotal()"></div>
          <div class="col-3"><label class="fw-bold small">TOTAL</label><div id="total_box" class="total-box">30.00</div><input type="hidden" name="valor_total" id="valor_total" value="30"><div id="total_red" style="color:#c4002b;font-weight:900;font-size:14px;text-align:right;margin-top:4px">R$ 30.00</div></div>
        </div>

        <label class="fw-bold small mt-4">PRODUTOS - CLIQUE</label>
        <div class="mt-2" style="max-height:400px;overflow-y:auto">{lista_prod or '<div class=small>Nenhum produto</div>'}</div>
        <button class="btn-new w-100 py-3 mt-4" style="border-radius:14px">SALVAR ATENDIMENTO - <span id="btn_total">R$ 30.00</span></button>
      </form>
    </div>
    <script>
    function toggleProd(id){{
      const el=document.getElementById('item-'+id);
      const chk=document.getElementById('chk-'+id);
      const ok=document.getElementById('ok-'+id);
      el.classList.toggle('selected');
      chk.checked = el.classList.contains('selected');
      ok.innerText = chk.checked? 'X' : 'OK';
      calcTotal();
    }}
    function atualizaServico(){{
      const sel=document.getElementById('servico_select');
      const preco=sel.options[sel.selectedIndex].dataset.preco;
      document.getElementById('valor_servico').value=preco;
      calcTotal();
    }}
    function calcTotal(){{
      let t=parseFloat(document.getElementById('valor_servico').value)||0;
      document.querySelectorAll('.produto-item.selected').forEach(item=>{{
        t+=parseFloat(item.dataset.preco)||0;
      }});
      document.getElementById('total_box').innerText=t.toFixed(2);
      document.getElementById('valor_total').value=t.toFixed(2);
      document.getElementById('total_red').innerText='R$ '+t.toFixed(2);
      document.getElementById('btn_total').innerText='R$ '+t.toFixed(2);
    }}
    calcTotal();
    </script>
    """
    return render_template_string(BASE, content=html)

# Mantém as outras rotas que você já tinha...
@app.route('/produtos')
def produtos_route():
    return redirect('/')

@app.route('/historico')
def historico_route():
    return redirect('/')

@app.route('/mensalistas')
def mensalistas_route():
    return redirect('/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
