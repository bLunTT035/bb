from flask import Flask, render_template_string, request, redirect
import os
from datetime import datetime

app = Flask(__name__)

# BANCO DE DADOS
produtos_db = [
    {"id": 1, "nome": "Minoxidil 60ml", "categoria": "Minoxidil", "preco": 85.00},
    {"id": 2, "nome": "Pomada Modeladora", "categoria": "Pomada", "preco": 30.00},
    {"id": 3, "nome": "Gel Cola", "categoria": "Gel", "preco": 25.00},
    {"id": 4, "nome": "Creme de Barbear", "categoria": "Creme", "preco": 35.00},
    {"id": 5, "nome": "Shampoo 2 em 1", "categoria": "Shampoo", "preco": 28.00},
    {"id": 6, "nome": "Balm Pós-Barba", "categoria": "Balm", "preco": 32.00},
]
atendimentos_db = []
servicos = ["Corte Simples - R$ 35", "Barba - R$ 30", "Corte + Barba - R$ 60", "Pezinho - R$ 15", "Sobrancelha - R$ 10"]

# NOVO: MENSALISTAS
mensalistas_db = [
    {"id": 1, "nome": "João Silva", "valor": 80.0, "vencimento": 10, "status": "Pendente", "cortes": 2, "ultimo_pag": "01/10/2026", "historico": ["02/10 - Corte", "15/10 - Corte"]},
]

HTML_BASE = """
<!DOCTYPE html>
<html>
<head>
<title>Rei da Navalha - PRO</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
<style>
    *{font-family:'Inter',sans-serif}
    body { margin:0; background: #0a1f4d; background: linear-gradient(135deg, #0d2d6b 0%, #06163a 100%); min-height:100vh; }
    .header { background: rgba(255,255,255,0.97); backdrop-filter:blur(10px); border-bottom: 4px solid #c8102e; padding: 14px 24px; display:flex; justify-content:space-between; align-items:center; position:sticky; top:0; z-index:100; box-shadow:0 4px 20px rgba(0,0,0,0.3); }
    .header h1 { margin:0; color:#000; font-size:23px; font-weight:900; display:flex; align-items:center; gap:8px; letter-spacing:-0.5px; }
    .header h1 span { color:#c8102e; }
    .crown { font-size:30px; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.2)); }
    .nav a { text-decoration:none; color:#000; background:#f1f5f9; padding:8px 16px; border-radius:100px; font-size:13px; font-weight:800; margin-left:6px; border:1.5px solid #e2e8f0; transition:0.2s; }
    .nav a:hover { transform:translateY(-2px); }
    .nav a.active { background:#0d2d6b; color:white; border-color:#0d2d6b; box-shadow:0 4px 10px rgba(13,45,107,0.4); }
    .nav a.cta { background:#c8102e; color:white; border-color:#c8102e; }
    .container { max-width: 950px; margin: 28px auto; padding: 16px; }
    .card { background: #ffffff; border-radius: 20px; padding: 24px; box-shadow: 0 15px 35px rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.2); position:relative; overflow:hidden; }
    .card::before{content:''; position:absolute; top:0; left:0; right:0; height:5px; background:linear-gradient(90deg, #0d2d6b, #c8102e);}
    .card h2 { color:#000 !important; margin-top:0; font-weight:900; font-size:20px; }
    .grid3{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; margin-bottom:22px; }
    .stat { background:linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); padding:18px; border-radius:18px; text-align:center; box-shadow:0 8px 20px rgba(0,0,0,0.2); border:1px solid white; position:relative; }
    .stat b{ display:block; font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#64748b; margin-bottom:6px; }
    .stat h3{ margin:0; font-size:26px; font-weight:900; }
    label { color: #000; font-weight: 800; font-size:12px; display:block; margin-top:14px; text-transform:uppercase; letter-spacing:0.5px; }
    input, select { width:100%; padding:12px 14px; border:2px solid #e2e8f0; border-radius:12px; margin-top:6px; box-sizing:border-box; color:#000; font-weight:700; background:#f8fafc; transition:0.2s; }
    input:focus, select:focus{ border-color:#0d2d6b; background:white; outline:none; box-shadow:0 0 0 3px rgba(13,45,107,0.15); }
    .btn { background: linear-gradient(135deg, #c8102e 0%, #8f0c22 100%); color: white; border: none; padding: 14px; width:100%; border-radius:12px; font-weight:900; margin-top:18px; cursor:pointer; text-transform:uppercase; letter-spacing:1px; font-size:14px; box-shadow:0 6px 15px rgba(200,16,46,0.4); transition:0.2s; }
    .btn:hover { transform:translateY(-2px); box-shadow:0 8px 20px rgba(200,16,46,0.5); }
    .btn-blue{ background: linear-gradient(135deg, #0d2d6b 0%, #1e4bb8 100%); box-shadow:0 6px 15px rgba(13,45,107,0.4); }
    .prod-item { border:2px solid #f1f5f9; padding:12px 14px; border-radius:14px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; cursor:pointer; background:#f8fafc; color:#000; transition:0.2s; }
    .prod-item:hover{ border-color:#0d2d6b; transform:scale(1.01); }
    .prod-item.selected { background:#0d2d6b; color:white; border-color:#0d2d6b; box-shadow:0 6px 15px rgba(13,45,107,0.3); }
    .prod-item.selected b, .prod-item.selected small{ color:white !important; }
    .tag { background:#c8102e; color:white; font-size:10px; padding:3px 8px; border-radius:100px; font-weight:800; }
    .prod-item.selected .tag { background:white; color:#c8102e; }
    .mensal-card{ border-left:5px solid #0d2d6b; }
    .badge-pago{ background:#dcfce7; color:#166534; padding:4px 10px; border-radius:100px; font-size:11px; font-weight:900; }
    .badge-pend{ background:#fee2e2; color:#991b1b; padding:4px 10px; border-radius:100px; font-size:11px; font-weight:900; }
    .mini-btn{ padding:6px 12px; border-radius:8px; border:none; font-weight:800; font-size:12px; cursor:pointer; margin-right:6px; }
</style>
</head>
<body>
<div class="header">
  <h1><span class="crown">👑</span> REI DA <span>NAVALHA</span></h1>
  <div class="nav">
    <a href="/" class="{{'active' if active=='inicio' else ''}}">Início</a>
    <a href="/mensalistas" class="{{'active' if active=='mensal' else ''}}" style="{{'background:#0d2d6b;color:white;' if active=='mensal' else ''}}">💳 Mensalistas</a>
    <a href="/produtos" class="{{'active' if active=='prod' else ''}}">Produtos</a>
    <a href="/historico" class="{{'active' if active=='hist' else ''}}">Histórico</a>
    <a href="/novo" class="cta">+ Novo</a>
  </div>
</div>
<div class="container">
{{content}}
</div>
<script>
function toggleProd(id){const el=document.getElementById('p-'+id); const inp=document.getElementById('produtos_input'); let s=inp.value?inp.value.split(',').filter(x=>x):[]; if(el.classList.contains('selected')){el.classList.remove('selected'); s=s.filter(x=>x!=id);}else{el.classList.add('selected'); s.push(id);} inp.value=s.join(','); calcTotal();}
function calcTotal(){const v=parseFloat(document.getElementById('valor_servico').value)||0; let totP=0; (document.getElementById('produtos_input').value.split(',').filter(x=>x)).forEach(id=>{const p=document.getElementById('preco-'+id); if(p) totP+=parseFloat(p.value);}); const t=v+totP; document.getElementById('total_auto').value=t.toFixed(2); document.getElementById('total_view').innerText='R$ '+t.toFixed(2);}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    total_vendas = sum(a['total'] for a in atendimentos_db)
    total_mensal = sum(m['valor'] for m in mensalistas_db if m['status']=='Pago')
    pend = len([m for m in mensalistas_db if m['status']=='Pendente'])
    content = f"""
    <div class="grid3">
      <div class="stat"><b>Atendimentos</b><h3 style="color:#c8102e;">{len(atendimentos_db)}</h3></div>
      <div class="stat"><b>Faturamento Avulso</b><h3 style="color:#0d2d6b;">R$ {total_vendas:.2f}</h3></div>
      <div class="stat"><b>Mensalistas ({pend} pend.)</b><h3>R$ {total_mensal:.2f}</h3></div>
    </div>
    <div class="card">
      <h2>👑 Rei da Navalha PRO 2.0</h2>
      <p style="color:#000; font-weight:700; margin-bottom:6px;">Agora com controle de mensalistas + design premium.</p>
      <p style="color:#475569; font-size:14px;">Gerencie cortes avulsos e clientes que pagam por mês, controle de dias que vieram e pagamentos.</p>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:18px;">
        <a href="/novo"><button class="btn btn-blue">+ Novo Atendimento</button></a>
        <a href="/mensalistas"><button class="btn">💳 Ver Mensalistas</button></a>
      </div>
    </div>
    """
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="inicio")

@app.route("/mensalistas", methods=["GET","POST"])
def mensalistas():
    if request.method=="POST":
        acao = request.form.get("acao")
        if acao=="novo":
            mensalistas_db.append({
                "id": len(mensalistas_db)+1,
                "nome": request.form.get("nome"),
                "valor": float(request.form.get("valor") or 80),
                "vencimento": int(request.form.get("vencimento") or 10),
                "status": "Pendente",
                "cortes": 0,
                "ultimo_pag": "-",
                "historico": []
            })
        elif acao=="pagar":
            mid=int(request.form.get("id")); m=next((x for x in mensalistas_db if x["id"]==mid),None)
            if m: m["status"]="Pago"; m["ultimo_pag"]=datetime.now().strftime("%d/%m/%Y")
        elif acao=="cortar":
            mid=int(request.form.get("id")); m=next((x for x in mensalistas_db if x["id"]==mid),None)
            if m: m["cortes"]+=1; m["historico"].append(datetime.now().strftime("%d/%m - Corte"))
        elif acao=="pendente":
            mid=int(request.form.get("id")); m=next((x for x in mensalistas_db if x["id"]==mid),None)
            if m: m["status"]="Pendente"
        return redirect("/mensalistas")

    lista=""
    for m in reversed(mensalistas_db):
        badge = f"<span class='badge-pago'>● PAGO</span>" if m["status"]=="Pago" else f"<span class='badge-pend'>● PENDENTE</span>"
        hist = "<br>".join(m["historico"][-3:]) if m["historico"] else "<small style='color:#94a3b8;'>Nenhum corte ainda</small>"
        lista+=f"""
        <div class="card mensal-card" style="margin-bottom:14px; padding:18px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div><b style="font-size:16px; color:#000;">{m['nome']}</b><br><small style="color:#64748b;">Venc: todo dia {m['vencimento']} • R$ {m['valor']:.2f}/mês • {m['cortes']} cortes no mês</small></div>
            <div>{badge}</div>
          </div>
          <div style="margin-top:12px; background:#f8fafc; padding:10px 12px; border-radius:10px; font-size:12px; color:#000;"><b>Últimos cortes:</b><br>{hist}</div>
          <div style="margin-top:12px; display:flex;">
            <form method="POST" style="display:inline;"><input type="hidden" name="acao" value="cortar"><input type="hidden" name="id" value="{m['id']}"><button class="mini-btn" style="background:#0d2d6b; color:white;">✂️ Registrar Corte</button></form>
            <form method="POST" style="display:inline;"><input type="hidden" name="acao" value="pagar"><input type="hidden" name="id" value="{m['id']}"><button class="mini-btn" style="background:#16a34a; color:white;">💰 Pago</button></form>
            <form method="POST" style="display:inline;"><input type="hidden" name="acao" value="pendente"><input type="hidden" name="id" value="{m['id']}"><button class="mini-btn" style="background:#fee2e2; color:#991b1b;">Pendente</button></form>
          </div>
          <small style="color:#94a3b8;">Último pag: {m['ultimo_pag']}</small>
        </div>
        """

    content=f"""
    <div class="card" style="margin-bottom:18px;">
      <h2>💳 Novo Mensalista</h2>
      <form method="POST" style="display:grid; grid-template-columns:2fr 1fr 1fr 1fr; gap:10px; align-items:end;">
        <input type="hidden" name="acao" value="novo">
        <div><label>Nome do Cliente</label><input name="nome" required placeholder="Ex: Marcos"></div>
        <div><label>Valor Mensal</label><input name="valor" type="number" value="80"></div>
        <div><label>Vencimento (dia)</label><input name="vencimento" type="number" value="10" min="1" max="31"></div>
        <div><button class="btn btn-blue" style="margin-top:6px;">Adicionar</button></div>
      </form>
    </div>
    <h2 style="color:white; font-weight:900;">Seus Mensalistas ({len(mensalistas_db)})</h2>
    {lista if lista else "<div class='card'>Nenhum mensalista ainda</div>"}
    """
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="mensal")

@app.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        cliente = request.form.get("cliente")
        servico = request.form.get("servico")
        valor_servico = float(request.form.get("valor_servico") or 0)
        produtos_ids = request.form.get("produtos", "")
        total = float(request.form.get("total_auto") or 0)
        pagamento = request.form.get("pagamento")
        prod_nomes = []
        if produtos_ids:
            for pid in produtos_ids.split(","):
                if pid.strip().isdigit():
                    p = next((x for x in produtos_db if x["id"]==int(pid)), None)
                    if p: prod_nomes.append(p["nome"])
        atendimentos_db.append({"id": len(atendimentos_db)+1,"cliente": cliente,"servico": servico,"valor_servico": valor_servico,"produtos": ", ".join(prod_nomes),"total": total,"pagamento": pagamento,"data": datetime.now().strftime("%d/%m/%Y %H:%M")})
        return redirect("/historico")
    produtos_html = ""
    for p in produtos_db:
        produtos_html += f'<div class="prod-item" id="p-{p["id"]}" onclick="toggleProd({p["id"]})"><div><span class="tag">{p["categoria"]}</span> <b style="margin-left:6px;">{p["nome"]}</b><br><small style="margin-left:6px;">R$ {p["preco"]:.2f}</small></div><div>✓</div><input type="hidden" id="preco-{p["id"]}" value="{p["preco"]}"></div>'
    servicos_opt = "".join([f'<option>{s}</option>' for s in servicos])
    content = f"""
    <div class="card">
      <h2>Novo Atendimento Avulso</h2>
      <form method="POST">
        <label>Cliente *</label><input name="cliente" required placeholder="Nome do cliente">
        <label>Pagamento</label><select name="pagamento"><option>Dinheiro</option><option>Pix</option><option>Cartão</option></select>
        <div style="display:grid; grid-template-columns: 2fr 1fr 1fr; gap:10px;">
          <div><label>Serviço *</label><select name="servico">{servicos_opt}</select></div>
          <div><label>Valor Serviço</label><input id="valor_servico" name="valor_servico" type="number" value="35" oninput="calcTotal()"></div>
          <div><label>Total (Auto)</label><input id="total_auto" name="total_auto" readonly style="font-weight:900; background:#fef3c7; border-color:#000;" value="35.00"><small id="total_view" style="color:#c8102e; font-weight:900;">R$ 35.00</small></div>
        </div>
        <label style="margin-top:20px;">Produtos - clique para somar</label><input type="hidden" name="produtos" id="produtos_input"><div style="max-height:320px; overflow:auto; margin-top:8px;">{produtos_html}</div>
        <button class="btn" type="submit">SALVAR ATENDIMENTO</button>
      </form>
    </div>
    """
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="novo")

@app.route("/historico")
def historico():
    rows = ""
    for a in reversed(atendimentos_db):
        rows += f"<tr style='color:#000;'><td style='padding:10px; border-bottom:1px solid #e2e8f0;'>{a['data']}</td><td style='padding:10px; border-bottom:1px solid #e2e8f0; font-weight:800;'>{a['cliente']}</td><td style='padding:10px; border-bottom:1px solid #e2e8f0;'>{a['servico']}<br><small style='color:#c8102e; font-weight:700;'>{a['produtos']}</small></td><td style='padding:10px; border-bottom:1px solid #e2e8f0; font-weight:900;'>R$ {a['total']:.2f}</td></tr>"
    if not rows: rows = "<tr><td colspan=4 style='padding:24px; text-align:center; color:#000; font-weight:700;'>Nenhum atendimento ainda</td></tr>"
    content = f"""<div class="card"><h2>Histórico Avulso</h2><table style="width:100%; border-collapse:collapse; margin-top:12px;"><tr style="background:#0d2d6b; color:white;"><th style="padding:10px; text-align:left; border-radius:10px 0 0 0;">Data</th><th style="padding:10px; text-align:left;">Cliente</th><th style="padding:10px; text-align:left;">Serviço + Produtos</th><th style="padding:10px; text-align:left; border-radius:0 10px 0 0;">Total</th></tr>{rows}</table></div>"""
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="hist")

@app.route("/produtos")
def produtos():
    rows = ""
    for p in produtos_db:
        rows += f"<tr style='color:#000;'><td style='padding:12px; border-bottom:1px solid #e2e8f0;'><span class='tag'>{p['categoria']}</span> <b style='margin-left:6px;'>{p['nome']}</b></td><td style='padding:12px; border-bottom:1px solid #e2e8f0; font-weight:900;'>R$ {p['preco']:.2f}</td></tr>"
    content = f"""<div class="card"><h2>👑 Produtos - Rei da Navalha</h2><table style="width:100%; border-collapse:collapse; margin-top:12px;"><tr style="background:#0d2d6b; color:white;"><th style="padding:12px; text-align:left; border-radius:10px 0 0 0;">Produto</th><th style="padding:12px; text-align:left; border-radius:0 10px 0 0;">Preço</th></tr>{rows}</table></div>"""
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="prod")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
