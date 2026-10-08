from flask import Flask, render_template_string, request, redirect
import os
from datetime import datetime
import re

app = Flask(__name__)

produtos_db = [
    {"id": 1, "nome": "Minoxidil 60ml", "categoria": "Minoxidil", "preco": 85.00},
    {"id": 2, "nome": "Pomada Modeladora", "categoria": "Pomada", "preco": 30.00},
]
atendimentos_db = []

planos_mensal = [
    {"id": 1, "nome": "CORTE", "valor": 85},
    {"id": 2, "nome": "BARBA", "valor": 85},
    {"id": 3, "nome": "CORTE + SOBRANCELHA", "valor": 90},
    {"id": 4, "nome": "CORTE + BARBA E SOBRANCELHA", "valor": 125},
]

servicos_avulso = [
    {"id": 1, "nome": "Corte Simples", "valor": 35},
    {"id": 2, "nome": "Barba", "valor": 30},
    {"id": 3, "nome": "Corte + Barba", "valor": 60},
    {"id": 4, "nome": "Pezinho", "valor": 15},
    {"id": 5, "nome": "Sobrancelha", "valor": 10},
]

mensalistas_db = [
    {"id": 1, "nome": "João Silva", "plano": "CORTE + BARBA E SOBRANCELHA", "valor": 125.0, "vencimento": 10, "status": "Pendente", "cortes": 2, "ultimo_pag": "01/10/2026", "historico": ["02/10 - Corte"]},
]

def next_id(lista):
    return max([x["id"] for x in lista], default=0) + 1

HTML_BASE = """
<!DOCTYPE html>
<html>
<head>
<title>Rei da Navalha - PRO</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
<style>
    *{font-family:'Inter',sans-serif; box-sizing:border-box}
    body { margin:0; background: linear-gradient(135deg, #0d2d6b 0%, #06163a 100%); min-height:100vh; }
   .header { background: rgba(255,255,255,0.97); border-bottom: 4px solid #c8102e; padding: 14px 24px; display:flex; justify-content:space-between; align-items:center; position:sticky; top:0; z-index:100; flex-wrap:wrap; gap:10px; }
   .header h1 { margin:0; color:#000; font-size:23px; font-weight:900; display:flex; align-items:center; gap:8px; flex:1; }
   .header h1 span { color:#c8102e; }
   .nav { display:flex; align-items:center; flex-wrap:wrap; gap:6px; }
   .nav a { text-decoration:none; color:#000; background:#f1f5f9; padding:8px 14px; border-radius:100px; font-size:13px; font-weight:800; border:1.5px solid #e2e8f0; white-space:nowrap; }
   .nav a.active { background:#0d2d6b; color:white; }
   .nav a.cta { background:#c8102e; color:white; }
   .hamburger { display:none; background:#0d2d6b; color:white; border:none; border-radius:10px; padding:8px 12px; font-size:20px; font-weight:900; cursor:pointer; }
   .container { max-width: 950px; margin: 28px auto; padding: 16px; }
   .card { background: #fff; border-radius: 20px; padding: 24px; box-shadow: 0 15px 35px rgba(0,0,0,0.25); position:relative; overflow:hidden; margin-bottom:16px; }
   .card::before{content:''; position:absolute; top:0; left:0; right:0; height:5px; background:linear-gradient(90deg, #0d2d6b, #c8102e);}
   .card h2 { color:#000!important; margin-top:0; font-weight:900; font-size:18px; display:flex; justify-content:space-between; align-items:center; }
   .grid3{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; margin-bottom:22px; }
   .stat { background:#fff; padding:18px; border-radius:18px; text-align:center; box-shadow:0 8px 20px rgba(0,0,0,0.2); }
   .stat b{ display:block; font-size:11px; text-transform:uppercase; color:#64748b; margin-bottom:6px; }
   .stat h3{ margin:0; font-size:26px; font-weight:900; }
    label { color: #000; font-weight: 800; font-size:12px; display:block; margin-top:14px; text-transform:uppercase; }
    input, select { width:100%; padding:12px 14px; border:2px solid #e2e8f0; border-radius:12px; margin-top:6px; box-sizing:border-box; color:#000; font-weight:700; background:#f8fafc; }
   .btn { background: linear-gradient(135deg, #c8102e 0%, #8f0c22 100%); color: white; border: none; padding: 14px; width:100%; border-radius:12px; font-weight:900; margin-top:18px; cursor:pointer; text-transform:uppercase; font-size:14px; }
   .btn-blue{ background: linear-gradient(135deg, #0d2d6b 0%, #1e4bb8 100%); }
   .btn-small{ padding:6px 10px; border-radius:8px; border:none; font-weight:800; font-size:11px; cursor:pointer; }
   .prod-item { border:2px solid #f1f5f9; padding:12px 14px; border-radius:14px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; cursor:pointer; background:#f8fafc; color:#000; }
   .prod-item.selected { background:#0d2d6b; color:white; border-color:#0d2d6b; }
   .tag { background:#c8102e; color:white; font-size:10px; padding:3px 8px; border-radius:100px; font-weight:800; }
   .mini-btn{ padding:7px 12px; border-radius:8px; border:none; font-weight:800; font-size:12px; cursor:pointer; margin-left:6px; text-decoration:none; display:inline-block; }
   .badge-pago{ background:#dcfce7; color:#166534; padding:4px 10px; border-radius:100px; font-size:11px; font-weight:900; }
   .badge-pend{ background:#fee2e2; color:#991b1b; padding:4px 10px; border-radius:100px; font-size:11px; font-weight:900; }
   .valor-card{ background:#f8fafc; padding:12px; border-radius:12px; display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; border-left:4px solid #0d2d6b; }
   .valor-card.mensal{ border-left-color:#c8102e; }
   .valor-actions{ display:flex; gap:4px; }
    @media(max-width:768px){
     .header { padding:10px 12px; }.header h1 { font-size:18px; }.hamburger { display:block; }
     .nav { display:none; width:100%; flex-direction:column; background:#fff; border-radius:14px; padding:10px; box-shadow:0 8px 20px rgba(0,0,0,0.15); }
     .nav.show { display:flex; }.nav a { width:100%; text-align:center; padding:12px; }
     .grid3 { grid-template-columns:1fr; }.container { margin:14px auto; padding:10px; }
    }
</style>
</head>
<body>
<div class="header">
  <h1>👑 REI DA <span>NAVALHA</span></h1>
  <button class="hamburger" onclick="toggleMenu()">☰</button>
  <div class="nav" id="navMenu">
    <a href="/" class="{{'active' if active=='inicio' else ''}}">Início</a>
    <a href="/mensalistas" class="{{'active' if active=='mensal' else ''}}">💳 Mensalistas</a>
    <a href="/produtos" class="{{'active' if active=='prod' else ''}}">Produtos</a>
    <a href="/historico" class="{{'active' if active=='hist' else ''}}">Histórico</a>
    <a href="/novo" class="cta">+ Novo</a>
  </div>
</div>
<div class="container">
{{content}}
</div>
<script>
function toggleMenu(){ document.getElementById('navMenu').classList.toggle('show'); }
function toggleProd(id){const el=document.getElementById('p-'+id); const inp=document.getElementById('produtos_input'); let s=inp.value?inp.value.split(',').filter(x=>x):[]; if(el.classList.contains('selected')){el.classList.remove('selected'); s=s.filter(x=>x!=id);}else{el.classList.add('selected'); s.push(id);} inp.value=s.join(','); calcTotal();}
function atualizaServico(){ const sel=document.getElementById('servico_select'); if(!sel) return; const preco=parseFloat(sel.options[sel.selectedIndex].dataset.preco)||0; document.getElementById('valor_servico').value=preco; calcTotal(); }
function atualizaPlanoMensal(){ const sel=document.getElementById('plano_mensal_select'); if(!sel) return; const preco=sel.options[sel.selectedIndex].dataset.preco; document.getElementById('valor_mensal_input').value=preco; }
function calcTotal(){ const el=document.getElementById('valor_servico'); if(!el) return; const v=parseFloat(el.value)||0; let totP=0; const inp=document.getElementById('produtos_input'); if(inp) (inp.value.split(',').filter(x=>x)).forEach(id=>{const p=document.getElementById('preco-'+id); if(p) totP+=parseFloat(p.value);}); const t=v+totP; const ta=document.getElementById('total_auto'); const tv=document.getElementById('total_view'); if(ta) ta.value=t.toFixed(2); if(tv) tv.innerText='R$ '+t.toFixed(2); }
</script>
</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def index():
    global planos_mensal, servicos_avulso
    if request.method=="POST":
        acao = request.form.get("acao")
        if acao=="novo_plano":
            planos_mensal.append({"id": next_id(planos_mensal), "nome": request.form.get("nome").upper(), "valor": float(request.form.get("valor") or 0)})
        elif acao=="editar_plano":
            pid=int(request.form.get("id")); p=next((x for x in planos_mensal if x["id"]==pid),None)
            if p: p["nome"]=request.form.get("nome").upper(); p["valor"]=float(request.form.get("valor") or 0)
        elif acao=="excluir_plano":
            pid=int(request.form.get("id")); planos_mensal=[x for x in planos_mensal if x["id"]!=pid]
        elif acao=="novo_avulso":
            servicos_avulso.append({"id": next_id(servicos_avulso), "nome": request.form.get("nome"), "valor": float(request.form.get("valor") or 0)})
        elif acao=="editar_avulso":
            pid=int(request.form.get("id")); p=next((x for x in servicos_avulso if x["id"]==pid),None)
            if p: p["nome"]=request.form.get("nome"); p["valor"]=float(request.form.get("valor") or 0)
        elif acao=="excluir_avulso":
            pid=int(request.form.get("id")); servicos_avulso=[x for x in servicos_avulso if x["id"]!=pid]
        return redirect("/")

    total_vendas = sum(a['total'] for a in atendimentos_db)
    total_mensal = sum(m['valor'] for m in mensalistas_db if m['status']=='Pago')
    pend = len([m for m in mensalistas_db if m['status']=='Pendente'])
    edit_tipo = request.args.get("edit_tipo")
    edit_id = request.args.get("edit_id", type=int)

    # HTML Planos Mensal
    html_planos=""
    for p in planos_mensal:
        if edit_tipo=="plano" and edit_id==p["id"]:
            html_planos+=f"""
            <form method="POST" style="background:#fff0f2; padding:10px; border-radius:12px; margin-bottom:8px; display:grid; grid-template-columns:1.5fr 0.5fr auto; gap:6px;">
              <input type="hidden" name="acao" value="editar_plano"><input type="hidden" name="id" value="{p['id']}">
              <input name="nome" value="{p['nome']}" required><input name="valor" type="number" value="{p['valor']}">
              <div><button class="btn-small" style="background:#0d2d6b; color:white;">Salvar</button><a href="/" class="btn-small" style="background:#e2e8f0; text-decoration:none; color:#000; padding:6px 8px;">X</a></div>
            </form>"""
        else:
            html_planos+=f"""
            <div class="valor-card mensal">
              <div><b style="font-size:12px;">{p['nome']}</b><br><span style="color:#c8102e; font-weight:900;">R$ {p['valor']:.0f}</span></div>
              <div class="valor-actions">
                <a href="/?edit_tipo=plano&edit_id={p['id']}" class="btn-small" style="background:#fef3c7; color:#92400e; text-decoration:none;">Editar</a>
                <form method="POST" style="display:inline;" onsubmit="return confirm('Excluir plano?')"><input type="hidden" name="acao" value="excluir_plano"><input type="hidden" name="id" value="{p['id']}"><button class="btn-small" style="background:#fee2e2; color:#991b1b;">X</button></form>
              </div>
            </div>"""

    # HTML Avulsos
    html_avulso=""
    for s in servicos_avulso:
        if edit_tipo=="avulso" and edit_id==s["id"]:
            html_avulso+=f"""
            <form method="POST" style="background:#f1f5f9; padding:10px; border-radius:12px; margin-bottom:8px; display:grid; grid-template-columns:1.5fr 0.5fr auto; gap:6px;">
              <input type="hidden" name="acao" value="editar_avulso"><input type="hidden" name="id" value="{s['id']}">
              <input name="nome" value="{s['nome']}" required><input name="valor" type="number" value="{s['valor']}">
              <div><button class="btn-small" style="background:#0d2d6b; color:white;">Salvar</button><a href="/" class="btn-small" style="background:#e2e8f0; text-decoration:none; color:#000; padding:6px 8px;">X</a></div>
            </form>"""
        else:
            html_avulso+=f"""
            <div class="valor-card">
              <div><b style="font-size:12px;">{s['nome']}</b><br><span style="color:#0d2d6b; font-weight:900;">R$ {s['valor']:.0f}</span></div>
              <div class="valor-actions">
                <a href="/?edit_tipo=avulso&edit_id={s['id']}" class="btn-small" style="background:#fef3c7; color:#92400e; text-decoration:none;">Editar</a>
                <form method="POST" style="display:inline;" onsubmit="return confirm('Excluir?')"><input type="hidden" name="acao" value="excluir_avulso"><input type="hidden" name="id" value="{s['id']}"><button class="btn-small" style="background:#fee2e2; color:#991b1b;">X</button></form>
              </div>
            </div>"""

    content = f"""
    <div class="grid3">
      <div class="stat"><b>Atendimentos</b><h3 style="color:#c8102e;">{len(atendimentos_db)}</h3></div>
      <div class="stat"><b>Faturamento Avulso</b><h3 style="color:#0d2d6b;">R$ {total_vendas:.2f}</h3></div>
      <div class="stat"><b>Mensalistas ({pend} pend.)</b><h3>R$ {total_mensal:.2f}</h3></div>
    </div>

    <div class="card">
      <h2>👑 Plano Mensal - Valores Oficiais <button onclick="document.getElementById('form-plano').style.display='block'" class="btn-small" style="background:#c8102e; color:white;">+ Add</button></h2>
      <div id="form-plano" style="display:none; background:#f8fafc; padding:12px; border-radius:12px; margin-bottom:12px;">
        <form method="POST" style="display:grid; grid-template-columns:1.5fr 0.7fr auto; gap:8px;">
          <input type="hidden" name="acao" value="novo_plano">
          <input name="nome" placeholder="Ex: CORTE" required>
          <input name="valor" type="number" placeholder="R$" required>
          <button class="btn-small" style="background:#0d2d6b; color:white; padding:12px;">Adicionar</button>
        </form>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">{html_planos}</div>
    </div>

    <div class="card">
      <h2>✂️ Avulso - Valores <button onclick="document.getElementById('form-avulso').style.display='block'" class="btn-small" style="background:#0d2d6b; color:white;">+ Add</button></h2>
      <div id="form-avulso" style="display:none; background:#f8fafc; padding:12px; border-radius:12px; margin-bottom:12px;">
        <form method="POST" style="display:grid; grid-template-columns:1.5fr 0.7fr auto; gap:8px;">
          <input type="hidden" name="acao" value="novo_avulso">
          <input name="nome" placeholder="Ex: Corte + Barba" required>
          <input name="valor" type="number" placeholder="R$" required>
          <button class="btn-small" style="background:#c8102e; color:white; padding:12px;">Adicionar</button>
        </form>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">{html_avulso}</div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:18px;">
        <a href="/novo"><button class="btn btn-blue">+ Novo Atendimento</button></a>
        <a href="/mensalistas"><button class="btn">Mensalistas</button></a>
      </div>
    </div>
    """
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="inicio")

@app.route("/mensalistas", methods=["GET","POST"])
def mensalistas():
    global mensalistas_db
    if request.method=="POST":
        acao = request.form.get("acao")
        mid = request.form.get("id")
        if acao=="novo":
            plano_nome = request.form.get("plano")
            valor_plano = next((v["valor"] for v in planos_mensal if v["nome"]==plano_nome), 80)
            try: valor_plano = float(request.form.get("valor") or valor_plano)
            except: pass
            mensalistas_db.append({"id": next_id(mensalistas_db),"nome": request.form.get("nome"),"plano": plano_nome, "valor": float(valor_plano),"vencimento": int(request.form.get("vencimento") or 10),"status": "Pendente","cortes": 0,"ultimo_pag": "-","historico": []})
        elif acao=="pagar" and mid:
            m=next((x for x in mensalistas_db if str(x["id"])==str(mid)),None)
            if m: m["status"]="Pago"; m["ultimo_pag"]=datetime.now().strftime("%d/%m/%Y")
        elif acao=="cortar" and mid:
            m=next((x for x in mensalistas_db if str(x["id"])==str(mid)),None)
            if m: m["cortes"]+=1; m["historico"].append(datetime.now().strftime("%d/%m - Corte"))
        elif acao=="excluir" and mid:
            mensalistas_db = [x for x in mensalistas_db if str(x["id"])!=str(mid)]
        elif acao=="editar" and mid:
            m=next((x for x in mensalistas_db if str(x["id"])==str(mid)),None)
            if m:
                m["nome"]=request.form.get("nome"); m["plano"]=request.form.get("plano"); m["valor"]=float(request.form.get("valor")); m["vencimento"]=int(request.form.get("vencimento"))
        return redirect("/mensalistas")
    edit_id = request.args.get("edit", type=int)
    options_planos = "".join([f'<option value="{p["nome"]}" data-preco="{p["valor"]}">{p["nome"]} - R$ {p["valor"]:.0f}</option>' for p in planos_mensal])
    lista=""
    for m in reversed(mensalistas_db):
        badge = "<span class='badge-pago'>PAGO</span>" if m["status"]=="Pago" else "<span class='badge-pend'>PENDENTE</span>"
        hist = "<br>".join(m["historico"][-3:]) if m.get("historico") else "<small style='color:#94a3b8;'>Nenhum</small>"
        form_edit = ""
        if edit_id==m["id"]:
            form_edit = f"""
            <form method="POST" style="background:#f1f5f9; padding:12px; border-radius:10px; margin-top:12px;">
              <input type="hidden" name="acao" value="editar"><input type="hidden" name="id" value="{m['id']}">
              <div style="display:grid; grid-template-columns:2fr 1.5fr 1fr 1fr; gap:8px;">
                <input name="nome" value="{m['nome']}" required><select name="plano">{options_planos}</select><input name="valor" type="number" value="{m['valor']}"><input name="vencimento" type="number" value="{m['vencimento']}">
              </div>
              <button class="mini-btn" style="background:#0d2d6b; color:white; margin-top:8px;">Salvar</button><a href="/mensalistas" class="mini-btn" style="background:#e2e8f0;">Cancelar</a>
            </form>"""
        lista+=f"""<div class="card" style="border-left:5px solid #0d2d6b;"><div style="display:flex; justify-content:space-between;"><div><b>{m['nome']}</b><br><small>{m.get('plano','')} - R$ {m['valor']:.2f}</small></div><div>{badge}</div></div><div style="margin-top:8px; background:#f8fafc; padding:8px; border-radius:8px; font-size:12px;">{hist}</div>{form_edit}
          <div style="margin-top:12px;"><form method="POST" style="display:inline;"><input type="hidden" name="acao" value="cortar"><input type="hidden" name="id" value="{m['id']}"><button class="mini-btn" style="background:#0d2d6b; color:white;">Corte</button></form>
          <form method="POST" style="display:inline;"><input type="hidden" name="acao" value="pagar"><input type="hidden" name="id" value="{m['id']}"><button class="mini-btn" style="background:#16a34a; color:white;">Pago</button></form>
          <a href="/mensalistas?edit={m['id']}" class="mini-btn" style="background:#fef3c7;">Editar</a>
          <form method="POST" style="display:inline;" onsubmit="return confirm('Excluir?')"><input type="hidden" name="acao" value="excluir"><input type="hidden" name="id" value="{m['id']}"><button class="mini-btn" style="background:#fee2e2;">Excluir</button></form></div></div>"""
    content=f"""<div class="card"><h2>Novo Mensalista</h2><form method="POST" style="display:grid; grid-template-columns:2fr 2fr 1fr 1fr 1fr; gap:10px; align-items:end;"><input type="hidden" name="acao" value="novo"><div><label>Nome</label><input name="nome" required></div><div><label>Plano</label><select name="plano" id="plano_mensal_select" onchange="atualizaPlanoMensal()">{options_planos}</select></div><div><label>Valor</label><input name="valor" id="valor_mensal_input" type="number" value="{planos_mensal[0]['valor'] if planos_mensal else 85}"></div><div><label>Venc.</label><input name="vencimento" type="number" value="10"></div><div><button class="btn btn-blue" style="margin-top:6px;">Add</button></div></form></div>{lista}"""
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="mensal")

@app.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        cliente = request.form.get("cliente"); servico = request.form.get("servico"); valor_servico = float(request.form.get("valor_servico") or 0); produtos_ids = request.form.get("produtos", ""); total = float(request.form.get("total_auto") or 0); pagamento = request.form.get("pagamento"); prod_nomes = []
        if produtos_ids:
            for pid in produtos_ids.split(","):
                if pid.strip().isdigit():
                    p = next((x for x in produtos_db if x["id"]==int(pid)), None)
                    if p: prod_nomes.append(p["nome"])
        atendimentos_db.append({"id": len(atendimentos_db)+1,"cliente": cliente,"servico": servico,"valor_servico": valor_servico,"produtos": ", ".join(prod_nomes),"total": total,"pagamento": pagamento,"data": datetime.now().strftime("%d/%m/%Y %H:%M")})
        return redirect("/historico")
    produtos_html = ""
    for p in produtos_db:
        produtos_html += f'<div class="prod-item" id="p-{p["id"]}" onclick="toggleProd({p["id"]})"><div><span class="tag">{p["categoria"]}</span> <b style="margin-left:6px;">{p["nome"]}</b><br><small>R$ {p["preco"]:.2f}</small></div><div>OK</div><input type="hidden" id="preco-{p["id"]}" value="{p["preco"]}"></div>'
    servicos_opt = "".join([f'<option value="{s["nome"]}" data-preco="{s["valor"]}">{s["nome"]} - R$ {s["valor"]:.0f}</option>' for s in servicos_avulso])
    content = f"""<div class="card"><h2>Novo Atendimento</h2><form method="POST"><label>Cliente *</label><input name="cliente" required><label>Pagamento</label><select name="pagamento"><option>Dinheiro</option><option>Pix</option><option>Cartao</option><option>Mensalista</option></select>
        <div style="display:grid; grid-template-columns: 2fr 1fr 1fr; gap:10px;"><div><label>Servico Avulso</label><select name="servico" id="servico_select" onchange="atualizaServico()">{servicos_opt}</select></div><div><label>Valor</label><input id="valor_servico" name="valor_servico" type="number" value="{servicos_avulso[0]['valor'] if servicos_avulso else 35}" oninput="calcTotal()"></div><div><label>Total</label><input id="total_auto" name="total_auto" readonly style="font-weight:900; background:#fef3c7;" value="{servicos_avulso[0]['valor'] if servicos_avulso else 35}"><small id="total_view" style="color:#c8102e; font-weight:900;">R$ {servicos_avulso[0]['valor'] if servicos_avulso else 35}</small></div></div>
        <label>Produtos - clique</label><input type="hidden" name="produtos" id="produtos_input"><div style="max-height:320px; overflow:auto; margin-top:8px;">{produtos_html}</div><button class="btn" type="submit">SALVAR</button></form></div>"""
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="novo")

@app.route("/produtos", methods=["GET","POST"])
def produtos():
    content = "<div class='card'><h2>Produtos em breve</h2></div>"
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="prod")

@app.route("/historico")
def historico():
    rows = ""
    for a in reversed(atendimentos_db):
        rows += f"<tr style='color:#000;'><td style='padding:10px; border-bottom:1px solid #e2e8f0;'>{a['data']}</td><td style='padding:10px; border-bottom:1px solid #e2e8f0; font-weight:800;'>{a['cliente']}</td><td style='padding:10px; border-bottom:1px solid #e2e8f0;'>{a['servico']}<br><small style='color:#c8102e;'>{a['produtos']}</small></td><td style='padding:10px; border-bottom:1px solid #e2e8f0; font-weight:900;'>R$ {a['total']:.2f}</td></tr>"
    if not rows: rows = "<tr><td colspan=4 style='padding:24px; text-align:center;'>Nenhum ainda</td></tr>"
    content = f"""<div class="card"><h2>Historico</h2><table style="width:100%; border-collapse:collapse; margin-top:12px;"><tr style="background:#0d2d6b; color:white;"><th style="padding:10px;">Data</th><th>Cliente</th><th>Servico</th><th>Total</th></tr>{rows}</table></div>"""
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="hist")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
