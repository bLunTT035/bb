import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, send_file
import sqlite3
from io import BytesIO

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
    conn = get_conn(); cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute('CREATE TABLE IF NOT EXISTS produtos (id SERIAL PRIMARY KEY, nome TEXT, preco REAL, estoque INTEGER, categoria TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS atendimentos (id SERIAL PRIMARY KEY, cliente TEXT, servico TEXT, valor REAL, data TEXT, produtos TEXT, pagamento TEXT)')
    else:
        cur.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, preco REAL, estoque INTEGER, categoria TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS atendimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, servico TEXT, valor REAL, data TEXT, produtos TEXT, pagamento TEXT)')
    # Cria produtos padrão se estiver vazio
    cur.execute("SELECT COUNT(*) FROM produtos")
    qtd = cur.fetchone()[0]
    if qtd == 0:
        padrao = [
            ("Minoxidil 120ml", 85.00, 10, "Tratamento"),
            ("Pomada Modeladora", 30.00, 15, "Pomada"),
            ("Gel Cola", 25.00, 20, "Gel"),
            ("Creme de Barbear", 35.00, 12, "Creme"),
            ("Óleo para Barba", 40.00, 8, "Óleo"),
            ("Shampoo 2 em 1", 28.00, 10, "Shampoo")
        ]
        for nome, preco, est, cat in padrao:
            if USE_POSTGRES:
                cur.execute("INSERT INTO produtos (nome, preco, estoque, categoria) VALUES (%s,%s,%s,%s)", (nome, preco, est, cat))
            else:
                cur.execute("INSERT INTO produtos (nome, preco, estoque, categoria) VALUES (?,?,?,?)", (nome, preco, est, cat))
    conn.commit(); conn.close()

def buscar_atendimentos(filtro=""):
    conn = get_conn(); cur = conn.cursor()
    if filtro:
        q = f"%{filtro}%"
        if USE_POSTGRES: cur.execute("SELECT * FROM atendimentos WHERE cliente ILIKE %s OR servico ILIKE %s ORDER BY id DESC", (q,q))
        else: cur.execute("SELECT * FROM atendimentos WHERE cliente LIKE? OR servico LIKE? ORDER BY id DESC", (f"%{filtro}%", f"%{filtro}%"))
    else:
        cur.execute("SELECT * FROM atendimentos ORDER BY id DESC")
    rows = cur.fetchall(); conn.close()
    lista=[]
    for r in rows:
        if USE_POSTGRES: id_,cliente,servico,valor,data,prod,pag = r
        else: id_=r['id']; cliente=r['cliente']; servico=r['servico']; valor=r['valor']; data=r['data']; prod=r['produtos']; pag=r['pagamento']
        lista.append({"id":id_,"cliente":cliente,"servico":servico,"valor":valor or 0,"data":data,"prod":prod or "","pag":pag or ""})
    return lista

BASE = """
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Barbearia - Azul Vermelho Branco</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{background:#f0f3f8;color:#1a1a1a}
.navbar{background:#0d2a54!important;border-bottom:4px solid #d90429}
.card-custom{background:#fff;border:1px solid #dde3ed;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.05)}
.btn-blue{background:#0d2a54;color:#fff;font-weight:800;border:none;border-radius:8px}
.btn-blue:hover{background:#123a75;color:#fff}
.btn-red{background:#d90429;color:#fff;font-weight:800;border:none;border-radius:8px}
.btn-red:hover{background:#b00322;color:#fff}
.btn-light2{background:#e9eef5;color:#0d2a54;border:none;border-radius:8px;font-weight:600}
.table{--bs-table-bg:#fff!important;margin:0}
.table thead th{background:#0d2a54!important;color:#fff!important}
.produto-item{background:#f8f9fc;border:2px solid #e1e7f0;border-radius:10px;padding:12px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;cursor:pointer}
.produto-item.selected{background:#e3f2ff;border-color:#0d2a54}
.badge-cat{background:#d90429;color:#fff;font-size:10px;padding:2px 6px;border-radius:4px}
.small-label{color:#6c7a90;font-size:12px}
</style>
</head><body>
<nav class="navbar d-flex justify-content-between p-3">
<div class="fw-bold text-white">💈 BARBEARIA <span style="color:#ff2a4a">PRO</span></div>
<div class="d-flex gap-2">
<a href="/" class="btn btn-light2 btn-sm">Início</a>
<a href="/produtos" class="btn btn-light2 btn-sm">Produtos</a>
<a href="/historico" class="btn btn-light2 btn-sm">Histórico</a>
<a href="/novo" class="btn btn-red btn-sm">+ Novo</a>
</div>
</nav>
<div class="container py-4" style="max-width:950px">{{content|safe}}</div>
<script>
function toggleProd(el){el.classList.toggle('selected');let cb=el.querySelector('input');cb.checked=!cb.checked;calc()}
function calc(){let t=parseFloat(document.getElementById('valor_serv').value)||0;document.querySelectorAll('.produto-item.selected').forEach(i=>{t+=parseFloat(i.dataset.preco)||0});document.getElementById('valor_total').value=t.toFixed(2);document.getElementById('vd').innerText='R$ '+t.toFixed(2)}
</script>
</body></html>
"""

@app.route('/')
def index():
    init_db()
    conn=get_conn(); cur=conn.cursor()
    try: cur.execute("SELECT COUNT(*), COALESCE(SUM(valor),0) FROM atendimentos"); c=cur.fetchone(); total=c[0]; fat=c[1]
    except: total=0; fat=0
    conn.close()
    at = buscar_atendimentos()[:8]
    linhas="".join([f"<tr><td>{a['data']}</td><td><b>{a['cliente']}</b></td><td>{a['servico']}<br><span style='color:#d90429;font-size:12px'>{a['prod']}</span></td><td>R$ {float(a['valor']):.2f}</td><td><a href='/imprimir/{a['id']}' target='_blank' class='btn btn-sm btn-light2'>🖨️</a> <a href='/excluir/{a['id']}' class='btn btn-sm btn-red'>X</a></td></tr>" for a in at])
    html=f"""
    <div class="row g-3"><div class="col-6"><div class="card-custom p-4"><div class="fs-3 fw-bold" style="color:#0d2a54">{total}</div><div class="small-label">Atendimentos</div></div></div>
    <div class="col-6"><div class="card-custom p-4"><div class="fs-3 fw-bold" style="color:#d90429">R$ {float(fat):.2f}</div><div class="small-label">Faturado</div></div></div>
    <div class="col-12"><div class="card-custom p-4 d-flex gap-2"><a href="/novo" class="btn btn-blue w-100 py-3">+ NOVO ATENDIMENTO</a><a href="/exportar_excel" class="btn btn-light2 w-100">📊 Excel</a></div></div></div>
    <div class="card-custom p-4 mt-4"><h6 class="fw-bold" style="color:#0d2a54">Últimos Atendimentos</h6><table class="table table-striped mt-3"><thead><tr><th>Data</th><th>Cliente</th><th>Serviço + Produtos</th><th>Valor</th><th></th></tr></thead><tbody>{linhas}</tbody></table></div>
    """
    return render_template_string(BASE, content=html)

@app.route('/produtos', methods=['GET','POST'])
def produtos():
    init_db(); conn=get_conn(); cur=conn.cursor()
    if request.method=='POST':
        nome=request.form['nome']; preco=request.form['preco']; estoque=request.form['estoque']; cat=request.form['categoria']
        if USE_POSTGRES: cur.execute("INSERT INTO produtos (nome, preco, estoque, categoria) VALUES (%s,%s,%s,%s)", (nome, preco, estoque, cat))
        else: cur.execute("INSERT INTO produtos (nome, preco, estoque, categoria) VALUES (?,?,?,?)", (nome, preco, estoque, cat))
        conn.commit(); conn.close(); return redirect('/produtos')
    cur.execute("SELECT * FROM produtos ORDER BY id DESC"); rows=cur.fetchall(); conn.close()
    linhas=""
    for r in rows:
        idd=r[0] if USE_POSTGRES else r['id']; nome=r[1] if USE_POSTGRES else r['nome']; preco=r[2] if USE_POSTGRES else r['preco']; est=r[3] if USE_POSTGRES else r['estoque']; cat=r[4] if USE_POSTGRES else r['categoria']
        linhas+=f"<tr><td><b>{nome}</b> <span class='badge-cat'>{cat}</span></td><td>R$ {float(preco or 0):.2f}</td><td>{est}</td><td><a href='/excluir_prod/{idd}' class='btn btn-sm btn-red'>X</a></td></tr>"
    html=f"""<div class="card-custom p-4"><h5 class="fw-bold" style="color:#0d2a54">Produtos para Venda</h5>
    <form method="POST" class="row g-2 my-3">
      <div class="col-md-3"><input name="nome" class="form-control" placeholder="Nome (ex: Minoxidil)" required></div>
      <div class="col-md-2"><select name="categoria" class="form-control"><option>Minoxidil</option><option>Pomada</option><option>Gel</option><option>Creme</option><option>Óleo</option><option>Shampoo</option><option>Outro</option></select></div>
      <div class="col-md-2"><input name="preco" type="number" step="0.01" class="form-control" placeholder="Preço" required></div>
      <div class="col-md-2"><input name="estoque" type="number" class="form-control" placeholder="Qtd" required></div>
      <div class="col-md-3"><button class="btn btn-blue w-100">Adicionar Produto</button></div>
    </form>
    <table class="table table-striped"><thead><tr><th>Produto</th><th>Preço</th><th>Estoque</th><th></th></tr></thead><tbody>{linhas}</tbody></table></div>"""
    return render_template_string(BASE, content=html)

@app.route('/novo', methods=['GET','POST'])
def novo():
    init_db(); conn=get_conn(); cur=conn.cursor()
    cur.execute("SELECT * FROM produtos WHERE estoque > 0 ORDER BY categoria, nome ASC"); produtos=cur.fetchall()
    if request.method=='POST':
        cliente=request.form['cliente']; servico=request.form['servico']; valor=request.form['valor_total']; data=datetime.now().strftime("%d/%m/%Y %H:%M"); pag=request.form.get('pagamento','Dinheiro')
        sels=request.form.getlist('produtos'); nomes=[]
        for pid in sels:
            if USE_POSTGRES: cur.execute("SELECT nome FROM produtos WHERE id=%s", (int(pid),))
            else: cur.execute("SELECT nome FROM produtos WHERE id=?", (int(pid),))
            pr=cur.fetchone()
            if pr: nomes.append(pr[0] if USE_POSTGRES else pr['nome'])
            if USE_POSTGRES: cur.execute("UPDATE produtos SET estoque=estoque-1 WHERE id=%s", (int(pid),))
            else: cur.execute("UPDATE produtos SET estoque=estoque-1 WHERE id=?", (int(pid),))
        prod_txt=", ".join(nomes)
        if USE_POSTGRES: cur.execute("INSERT INTO atendimentos (cliente, servico, valor, data, produtos, pagamento) VALUES (%s,%s,%s,%s,%s,%s)", (cliente, servico, valor, data, prod_txt, pag))
        else: cur.execute("INSERT INTO atendimentos (cliente, servico, valor, data, produtos, pagamento) VALUES (?,?,?,?,?,?)", (cliente, servico, valor, data, prod_txt, pag))
        conn.commit(); conn.close(); return redirect('/')
    lista=""
    for r in produtos:
        idd=r[0] if USE_POSTGRES else r['id']; nome=r[1] if USE_POSTGRES else r['nome']; preco=float(r[2] if USE_POSTGRES else r['preco'] or 0); cat=r[4] if USE_POSTGRES else r['categoria']
        lista+=f"<div class='produto-item' data-preco='{preco}' onclick='toggleProd(this)'><div><input type='checkbox' name='produtos' value='{idd}' style='display:none'><span class='badge-cat'>{cat}</span> <b>{nome}</b><br><span class='small-label'>R$ {preco:.2f}</span></div><span>✓</span></div>"
    if not lista: lista="<div class='small-label'>Cadastre produtos primeiro</div>"
    conn.close()
    html=f"""
    <div class="card-custom p-4"><h5 class="fw-bold" style="color:#0d2a54">Novo Atendimento</h5>
    <form method="POST" class="row g-3 mt-2">
      <div class="col-md-6"><label class="small-label">Cliente *</label><input name="cliente" class="form-control" required></div>
      <div class="col-md-6"><label class="small-label">Pagamento</label><select name="pagamento" class="form-control"><option>Dinheiro</option><option>Pix</option><option>Cartão</option><option>Fiado</option></select></div>
      <div class="col-md-6"><label class="small-label">Serviço *</label><select name="servico" class="form-control" onchange="document.getElementById('valor_serv').value=this.selectedOptions[0].dataset.preco;calc()">
        <option data-preco="35" value="Corte Simples">Corte Simples - R$ 35</option>
        <option data-preco="20" value="Barba">Barba - R$ 20</option>
        <option data-preco="50" value="Corte + Barba">Corte + Barba - R$ 50</option>
        <option data-preco="45" value="Corte + Sobrancelha">Corte + Sobrancelha - R$ 45</option>
        <option data-preco="70" value="Combo Premium">Combo Premium - R$ 70</option>
      </select></div>
      <div class="col-md-3"><label class="small-label">Valor Serviço</label><input id="valor_serv" type="number" step="0.01" value="35" class="form-control" oninput="calc()"></div>
      <div class="col-md-3"><label class="small-label">Total (Auto)</label><input id="valor_total" name="valor_total" class="form-control" style="border:2px solid #0d2a54!important;font-weight:bold" readonly><div id="vd" class="small-label" style="color:#d90429;font-weight:bold">R$ 35.00</div></div>
      <div class="col-12 mt-3"><label class="small-label fw-bold" style="color:#0d2a54">PRODUTOS PARA VENDA - clique para adicionar (soma automático)</label><div style="max-height:300px;overflow:auto" class="mt-2">{lista}</div></div>
      <div class="col-12"><button class="btn btn-red w-100 py-2 mt-3">SALVAR ATENDIMENTO</button></div>
    </form></div>
    """
    return render_template_string(BASE, content=html)

@app.route('/historico')
def historico():
    q=request.args.get('q',''); lista=buscar_atendimentos(q)
    linhas="".join([f"<tr><td>{a['data']}</td><td><b>{a['cliente']}</b><br><span class='small-label'>{a['pag']}</span></td><td>{a['servico']}<br><span style='color:#d90429;font-size:12px'>{a['prod']}</span></td><td>R$ {float(a['valor']):.2f}</td><td><a href='/imprimir/{a['id']}' target='_blank' class='btn btn-sm btn-light2'>🖨️</a> <a href='/excluir/{a['id']}' class='btn btn-sm btn-red'>X</a></td></tr>" for a in lista])
    html=f"""<div class="card-custom p-4"><div class="d-flex justify-content-between mb-3"><h5 class="fw-bold" style="color:#0d2a54">Histórico</h5><a href="/exportar_excel" class="btn btn-blue btn-sm">Excel</a></div>
    <form class="mb-3"><div class="input-group"><input name="q" value="{q}" class="form-control" placeholder="Pesquisar cliente"><button class="btn btn-blue">Buscar</button></div></form>
    <table class="table table-striped"><thead><tr><th>Data</th><th>Cliente</th><th>Serviço</th><th>Valor</th><th></th></tr></thead><tbody>{linhas}</tbody></table></div>"""
    return render_template_string(BASE, content=html)

@app.route('/exportar_excel')
def exportar_excel():
    lista=buscar_atendimentos()
    try:
        import openpyxl; wb=openpyxl.Workbook(); ws=wb.active; ws.title="Barbearia"; ws.append(["Data","Cliente","Serviço","Produtos Vendidos","Pagamento","Valor"])
        for a in lista: ws.append([a['data'],a['cliente'],a['servico'],a['prod'],a['pag'],float(a['valor'])])
        bio=BytesIO(); wb.save(bio); bio.seek(0)
        return send_file(bio, as_attachment=True, download_name="barbearia.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except:
        out="Data,Cliente,Servico,Produtos,Pagamento,Valor\n"+"\n".join([f"\"{a['data']}\",\"{a['cliente']}\",\"{a['servico']}\",\"{a['prod']}\",\"{a['pag']}\",{a['valor']}" for a in lista])
        bio=BytesIO(out.encode()); return send_file(bio, as_attachment=True, download_name="barbearia.csv", mimetype="text/csv")

@app.route('/imprimir/<int:id>')
def imprimir(id):
    conn=get_conn(); cur=conn.cursor()
    if USE_POSTGRES: cur.execute("SELECT * FROM atendimentos WHERE id=%s", (id,))
    else: cur.execute("SELECT * FROM atendimentos WHERE id=?", (id,))
    r=cur.fetchone(); conn.close()
    if not r: return "Não achado"
    a = {"id":r[0] if USE_POSTGRES else r['id'], "cliente":r[1] if USE_POSTGRES else r['cliente'], "servico":r[2] if USE_POSTGRES else r['servico'], "valor":r[3] if USE_POSTGRES else r['valor'], "data":r[4] if USE_POSTGRES else r['data'], "prod":r[5] if USE_POSTGRES else r['produtos'], "pag":r[6] if USE_POSTGRES else r['pagamento']}
    return f"""<html><head><meta charset="utf-8"><style>body{{font-family:Arial;padding:30px}}.box{{border:1px solid #ddd;padding:15px;border-radius:8px;margin-bottom:15px}}.btn{{background:#0d2a54;color:#fff;padding:10px 20px;border:none;border-radius:6px;font-weight:bold}}@media print{{.no-print{{display:none}}}}</style></head>
    <body><h2 style="color:#0d2a54">💈 BARBEARIA PRO - #{a['id']}</h2><p>{a['data']}</p><div class="box"><b>Cliente:</b> {a['cliente']}<br><b>Pagamento:</b> {a['pag']}</div><div class="box"><b>Serviço:</b> {a['servico']}<br><b>Produtos vendidos:</b> {a['prod']}</div><div class="box"><h3 style="color:#d90429">Total: R$ {float(a['valor']):.2f}</h3></div><div class="no-print"><button class="btn" onclick="window.print()">🖨️ IMPRIMIR</button></div></body></html>"""

@app.route('/excluir/<int:id>')
def excluir(id):
    conn=get_conn(); cur=conn.cursor()
    if USE_POSTGRES: cur.execute("DELETE FROM atendimentos WHERE id=%s", (id,))
    else: cur.execute("DELETE FROM atendimentos WHERE id=?", (id,))
    conn.commit(); conn.close(); return redirect('/historico')

@app.route('/excluir_prod/<int:id>')
def excluir_prod(id):
    conn=get_conn(); cur=conn.cursor()
    if USE_POSTGRES: cur.execute("DELETE FROM produtos WHERE id=%s", (id,))
    else: cur.execute("DELETE FROM produtos WHERE id=?", (id,))
    conn.commit(); conn.close(); return redirect('/produtos')

if __name__ == '__main__':
    app.run(debug=True)
