from flask import Flask, render_template_string, request, redirect
import os
from datetime import datetime
from io import BytesIO

app = Flask(__name__)

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
mensalistas_db = [
    {"id": 1, "nome": "João Silva", "valor": 80.0, "vencimento": 10, "status": "Pendente", "cortes": 2, "ultimo_pag": "01/10/2026", "historico": ["02/10 - Corte", "15/10 - Corte"]},
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
    *{font-family:'Inter',sans-serif}
    body { margin:0; background: linear-gradient(135deg, #0d2d6b 0%, #06163a 100%); min-height:100vh; }
    .header { background: rgba(255,255,255,0.97); border-bottom: 4px solid #c8102e; padding: 14px 24px; display:flex; justify-content:space-between; align-items:center; position:sticky; top:0; z-index:100; }
    .header h1 { margin:0; color:#000; font-size:23px; font-weight:900; display:flex; align-items:center; gap:8px; }
    .header h1 span { color:#c8102e; }
    .crown { font-size:30px; }
    .nav a { text-decoration:none; color:#000; background:#f1f5f9; padding:8px 16px; border-radius:100px; font-size:13px; font-weight:800; margin-left:6px; border:1.5px solid #e2e8f0; }
    .nav a.active { background:#0d2d6b; color:white; }
    .nav a.cta { background:#c8102e; color:white; }
    .container { max-width: 950px; margin: 28px auto; padding: 16px; }
    .card { background: #fff; border-radius: 20px; padding: 24px; box-shadow: 0 15px 35px rgba(0,0,0,0.25); position:relative; overflow:hidden; margin-bottom:16px; }
    .card::before{content:''; position:absolute; top:0; left:0; right:0; height:5px; background:linear-gradient(90deg, #0d2d6b, #c8102e);}
    .card h2 { color:#000 !important; margin-top:0; font-weight:900; font-size:20px; }
    .grid3{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; margin-bottom:22px; }
    .stat { background:#fff; padding:18px; border-radius:18px; text-align:center; box-shadow:0 8px 20px rgba(0,0,0,0.2); }
    .stat b{ display:block; font-size:11px; text-transform:uppercase; color:#64748b; margin-bottom:6px; }
    .stat h3{ margin:0; font-size:26px; font-weight:900; }
    label { color: #000; font-weight: 800; font-size:12px; display:block; margin-top:14px; text-transform:uppercase; }
    input, select { width:100%; padding:12px 14px; border:2px solid #e2e8f0; border-radius:12px; margin-top:6px; box-sizing:border-box; color:#000; font-weight:700; background:#f8fafc; }
    .btn { background: linear-gradient(135deg, #c8102e 0%, #8f0c22 100%); color: white; border: none; padding: 14px; width:100%; border-radius:12px; font-weight:900; margin-top:18px; cursor:pointer; text-transform:uppercase; font-size:14px; }
    .btn-blue{ background: linear-gradient(135deg, #0d2d6b 0%, #1e4bb8 100%); }
    .prod-item { border:2px solid #f1f5f9; padding:12px 14px; border-radius:14px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; cursor:pointer; background:#f8fafc; color:#000; }
    .prod-item.selected { background:#0d2d6b; color:white; border-color:#0d2d6b; }
    .tag { background:#c8102e; color:white; font-size:10px; padding:3px 8px; border-radius:100px; font-weight:800; }
    .mini-btn{ padding:7px 12px; border-radius:8px; border:none; font-weight:800; font-size:12px; cursor:pointer; margin-left:6px; text-decoration:none; display:inline-block; }
    .badge-pago{ background:#dcfce7; color:#166534; padding:4px 10px; border-radius:100px; font-size:11px; font-weight:900; }
    .badge-pend{ background:#fee2e2; color:#991b1b; padding:4px 10px; border-radius:100px; font-size:11px; font-weight:900; }
    .import-box{ background:#f8fafc; border:2px dashed #0d2d6b; padding:16px; border-radius:14px; margin-top:12px; }
</style>
</head>
<body>
<div class="header">
  <h1><span class="crown">👑</span> REI DA <span>NAVALHA</span></h1>
  <div class="nav">
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
      <h2>👑 Rei da Navalha PRO</h2>
      <p style="color:#000; font-weight:700;">Com edicao e exclusao!</p>
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
            mensalistas_db.append({"id": next_id(mensalistas_db),"nome": request.form.get("nome"),"valor": float(request.form.get("valor") or 80),"vencimento": int(request.form.get("vencimento") or 10),"status": "Pendente","cortes": 0,"ultimo_pag": "-","historico": []})
        elif acao=="pagar" and mid:
            m=next((x for x in mensalistas_db if str(x["id"])==str(mid)),None)
            if m: m["status"]="Pago"; m["ultimo_pag"]=datetime.now().strftime("%d/%m/%Y")
        elif acao=="cortar" and mid:
            m=next((x for x in mensalistas_db if str(x["id"])==str(mid)),None)
            if m: m["cortes"]+=1; m["historico"].append(datetime.now().strftime("%d/%m - Corte"))
        elif acao=="pendente" and mid:
            m=next((x for x in mensalistas_db if str(x["id"])==str(mid)),None)
            if m: m["status"]="Pendente"
        elif acao=="excluir" and mid:
            mensalistas_db = [x for x in mensalistas_db if str(x["id"])!=str(mid)]
        elif acao=="editar" and mid:
            m=next((x for x in mensalistas_db if str(x["id"])==str(mid)),None)
            if m:
                m["nome"]=request.form.get("nome")
                m["valor"]=float(request.form.get("valor"))
                m["vencimento"]=int(request.form.get("vencimento"))
        return redirect("/mensalistas")

    edit_id = request.args.get("edit", type=int)
    lista=""
    for m in reversed(mensalistas_db):
        badge = "<span class='badge-pago'>PAGO</span>" if m["status"]=="Pago" else "<span class='badge-pend'>PENDENTE</span>"
        hist = "<br>".join(m["historico"][-3:]) if m["historico"] else "<small style='color:#94a3b8;'>Nenhum corte</small>"
        form_edit = ""
        if edit_id==m["id"]:
            form_edit = f"""
            <form method="POST" style="background:#f1f5f9; padding:12px; border-radius:10px; margin-top:12px;">
              <input type="hidden" name="acao" value="editar"><input type="hidden" name="id" value="{m['id']}">
              <div style="display:grid; grid-template-columns:2fr 1fr 1fr; gap:8px;">
                <input name="nome" value="{m['nome']}" required>
                <input name="valor" type="number" value="{m['valor']}">
                <input name="vencimento" type="number" value="{m['vencimento']}">
              </div>
              <button class="mini-btn" style="background:#0d2d6b; color:white; margin-top:8px;">Salvar</button>
              <a href="/mensalistas" class="mini-btn" style="background:#e2e8f0; color:#000;">Cancelar</a>
            </form>
            """
        lista+=f"""
        <div class="card" style="border-left:5px solid #0d2d6b;">
          <div style="display:flex; justify-content:space-between;"><div><b style="color:#000;">{m['nome']}</b><br><small>Venc dia {m['vencimento']} - R$ {m['valor']:.2f} - {m['cortes']} cortes</small></div><div>{badge}</div></div>
          <div style="margin-top:10px; background:#f8fafc; padding:8px; border-radius:8px; font-size:12px;">{hist}</div>
          {form_edit}
          <div style="margin-top:12px;">
            <form method="POST" style="display:inline;"><input type="hidden" name="acao" value="cortar"><input type="hidden" name="id" value="{m['id']}"><button class="mini-btn" style="background:#0d2d6b; color:white;">Corte</button></form>
            <form method="POST" style="display:inline;"><input type="hidden" name="acao" value="pagar"><input type="hidden" name="id" value="{m['id']}"><button class="mini-btn" style="background:#16a34a; color:white;">Pago</button></form>
            <a href="/mensalistas?edit={m['id']}" class="mini-btn" style="background:#fef3c7; color:#92400e;">Editar</a>
            <form method="POST" style="display:inline;" onsubmit="return confirm('Excluir?')"><input type="hidden" name="acao" value="excluir"><input type="hidden" name="id" value="{m['id']}"><button class="mini-btn" style="background:#fee2e2; color:#991b1b;">Excluir</button></form>
          </div>
        </div>
        """
    content=f"""
    <div class="card">
      <h2>Novo Mensalista</h2>
      <form method="POST" style="display:grid; grid-template-columns:2fr 1fr 1fr 1fr; gap:10px; align-items:end;">
        <input type="hidden" name="acao" value="novo">
        <div><label>Nome</label><input name="nome" required></div>
        <div><label>Valor</label><input name="valor" type="number" value="80"></div>
        <div><label>Venc.</label><input name="vencimento" type="number" value="10"></div>
        <div><button class="btn btn-blue" style="margin-top:6px;">Add</button></div>
      </form>
    </div>
    {lista}
    """
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="mensal")

@app.route("/produtos", methods=["GET","POST"])
def produtos():
    global produtos_db
    msg = ""
    if request.method=="POST":
        if 'arquivo' in request.files and request.files['arquivo'].filename != '':
            file = request.files['arquivo']
            try:
                try:
                    import pandas as pd
                    df = pd.read_excel(file)
                    cols = {c.lower().strip(): c for c in df.columns}
                    def find_col(names):
                        for n in names:
                            for k,v in cols.items():
                                if n in k:
                                    return v
                        return None
                    col_nome = find_col(['produto','nome','descricao','descrição','item'])
                    col_preco = find_col(['valor revenda','preco','preço','valor','price','revenda'])
                    col_cat = find_col(['categoria','cat','tipo','grupo'])
                    count=0
                    for _, row in df.iterrows():
                        nome = str(row[col_nome]).strip() if col_nome and str(row[col_nome])!='nan' else ""
                        if not nome or nome.lower() in ['nan','none','']: continue
                        if any(p['nome'].lower()==nome.lower() for p in produtos_db): 
                            p_ex = next(p for p in produtos_db if p['nome'].lower()==nome.lower())
                            try:
                                if col_preco:
                                    pr = float(row[col_preco])
                                    if pr>0: p_ex['preco']=pr
                            except: pass
                            continue
                        try:
                            preco = float(row[col_preco]) if col_preco else 0.0
                        except:
                            preco = 0.0
                        cat = str(row[col_cat]).strip() if col_cat and str(row[col_cat])!='nan' else "Geral"
                        if not cat or cat.lower()=='nan': cat="Geral"
                        if preco<=0: continue
                        produtos_db.append({"id": next_id(produtos_db), "nome": nome, "categoria": cat, "preco": preco})
                        count+=1
                    msg = f"<div style='background:#dcfce7; color:#166534; padding:12px; border-radius:10px; margin-bottom:12px; font-weight:800;'>✅ {count} produtos importados com sucesso! {len(df)} linhas lidas.</div>"
                except ImportError:
                    import openpyxl
                    wb = openpyxl.load_workbook(file)
                    ws = wb.active
                    headers = [str(ws.cell(1,c).value).lower() if ws.cell(1,c).value else "" for c in range(1, ws.max_column+1)]
                    def idx_of(names):
                        for i,h in enumerate(headers):
                            for n in names:
                                if n in h: return i
                        return None
                    i_nome = idx_of(['produto','nome','descricao'])
                    i_preco = idx_of(['valor revenda','preco','valor'])
                    i_cat = idx_of(['categoria','tipo'])
                    count=0
                    for r in range(2, ws.max_row+1):
                        nome = str(ws.cell(r, (i_nome+1) if i_nome is not None else 1).value or "").strip()
                        if not nome or nome.lower()=='none': continue
                        if any(p['nome'].lower()==nome.lower() for p in produtos_db): continue
                        try:
                            preco = float(ws.cell(r, (i_preco+1) if i_preco is not None else 2).value or 0)
                        except: preco=0
                        if preco<=0: continue
                        cat = str(ws.cell(r, (i_cat+1) if i_cat is not None else 3).value or "Geral").strip()
                        if not cat or cat.lower()=='none': cat="Geral"
                        produtos_db.append({"id": next_id(produtos_db), "nome": nome, "categoria": cat, "preco": preco})
                        count+=1
                    msg = f"<div style='background:#dcfce7; color:#166534; padding:12px; border-radius:10px; margin-bottom:12px; font-weight:800;'>✅ {count} produtos importados!</div>"
            except Exception as e:
                msg = f"<div style='background:#fee2e2; color:#991b1b; padding:12px; border-radius:10px; margin-bottom:12px; font-weight:800;'>❌ Erro ao importar: {e}</div>"
        else:
            acao=request.form.get("acao")
            mid=request.form.get("id")
            if acao=="novo":
                produtos_db.append({"id": next_id(produtos_db),"nome": request.form.get("nome"),"categoria": request.form.get("categoria"),"preco": float(request.form.get("preco") or 0)})
            elif acao=="excluir" and mid:
                produtos_db = [x for x in produtos_db if str(x["id"])!=str(mid)]
            elif acao=="editar" and mid:
                p=next((x for x in produtos_db if str(x["id"])==str(mid)),None)
                if p:
                    p["nome"]=request.form.get("nome")
                    p["categoria"]=request.form.get("categoria")
                    p["preco"]=float(request.form.get("preco"))
            return redirect("/produtos")
    edit_id = request.args.get("edit", type=int)
    rows=""
    for p in produtos_db:
        if edit_id==p["id"]:
            rows+=f"""<tr style="background:#f1f5f9;"><td colspan="3" style="padding:12px;">
              <form method="POST" style="display:grid; grid-template-columns:2fr 1fr 1fr 1fr; gap:8px;">
                <input type="hidden" name="acao" value="editar"><input type="hidden" name="id" value="{p['id']}">
                <input name="nome" value="{p['nome']}" required><input name="categoria" value="{p['categoria']}"><input name="preco" type="number" step="0.01" value="{p['preco']}">
                <div><button class="mini-btn" style="background:#0d2d6b; color:white;">Salvar</button><a href="/produtos" class="mini-btn" style="background:#e2e8f0;">Cancelar</a></div>
              </form></td></tr>"""
        else:
            rows+=f"""<tr style='color:#000;'><td style='padding:12px; border-bottom:1px solid #e2e8f0;'><span class='tag'>{p['categoria']}</span> <b style='margin-left:6px;'>{p['nome']}</b></td>
            <td style='padding:12px; border-bottom:1px solid #e2e8f0; font-weight:900;'>R$ {p['preco']:.2f}</td>
            <td style='padding:12px; border-bottom:1px solid #e2e8f0; text-align:right;'><a href="/produtos?edit={p['id']}" class="mini-btn" style="background:#fef3c7;">Editar</a>
            <form method="POST" style="display:inline;" onsubmit="return confirm('Excluir?')"><input type="hidden" name="acao" value="excluir"><input type="hidden" name="id" value="{p['id']}"><button class="mini-btn" style="background:#fee2e2;">Excluir</button></form></td></tr>"""
    content = f"""
    {msg}
    <div class="card">
      <h2>Novo Produto</h2>
      <form method="POST" style="display:grid; grid-template-columns:2fr 1fr 1fr 1fr; gap:10px; align-items:end;">
        <input type="hidden" name="acao" value="novo">
        <div><label>Nome</label><input name="nome" required></div>
        <div><label>Categoria</label><input name="categoria" value="Novo"></div>
        <div><label>Preco</label><input name="preco" type="number" step="0.01" required></div>
        <div><button class="btn btn-blue" style="margin-top:6px;">Add</button></div>
      </form>
      
      <div class="import-box">
        <h3 style="margin:0 0 8px 0; font-size:14px; font-weight:900; color:#0d2d6b;">📥 Importar Planilha (Excel)</h3>
        <p style="margin:0 0 10px 0; font-size:12px; color:#64748b;">Encaminhe sua planilha com os produtos da oficina/barbearia. Aceita .xlsx com colunas PRODUTO / VALOR REVENDA / CATEGORIA ou NOME / PRECO / CATEGORIA</p>
        <form method="POST" enctype="multipart/form-data" style="display:grid; grid-template-columns: 1fr auto; gap:10px; align-items:end;">
          <div><input type="file" name="arquivo" accept=".xlsx,.xls,.csv" required style="background:white;"></div>
          <div><button class="btn btn-blue" style="margin:0; padding:12px 20px;">IMPORTAR</button></div>
        </form>
        <small style="color:#94a3b8;">Dica: pode usar a sua PLANILHA_OFICINA_CERTA.xlsx direto. Ele ignora produtos sem preço.</small>
      </div>
    </div>
    <div class="card">
      <h2>Produtos ({len(produtos_db)})</h2>
      <table style="width:100%; border-collapse:collapse; margin-top:12px;">
        <tr style="background:#0d2d6b; color:white;"><th style="padding:12px; text-align:left;">Produto</th><th>Preco</th><th>Acoes</th></tr>
        {rows}
      </table>
    </div>
    """
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="prod")

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
        produtos_html += f'<div class="prod-item" id="p-{p["id"]}" onclick="toggleProd({p["id"]})"><div><span class="tag">{p["categoria"]}</span> <b style="margin-left:6px;">{p["nome"]}</b><br><small>R$ {p["preco"]:.2f}</small></div><div>OK</div><input type="hidden" id="preco-{p["id"]}" value="{p["preco"]}"></div>'
    servicos_opt = "".join([f'<option>{s}</option>' for s in servicos])
    content = f"""
    <div class="card">
      <h2>Novo Atendimento</h2>
      <form method="POST">
        <label>Cliente *</label><input name="cliente" required>
        <label>Pagamento</label><select name="pagamento"><option>Dinheiro</option><option>Pix</option><option>Cartao</option></select>
        <div style="display:grid; grid-template-columns: 2fr 1fr 1fr; gap:10px;">
          <div><label>Servico</label><select name="servico">{servicos_opt}</select></div>
          <div><label>Valor</label><input id="valor_servico" name="valor_servico" type="number" value="35" oninput="calcTotal()"></div>
          <div><label>Total</label><input id="total_auto" name="total_auto" readonly style="font-weight:900; background:#fef3c7;" value="35.00"><small id="total_view" style="color:#c8102e; font-weight:900;">R$ 35.00</small></div>
        </div>
        <label>Produtos - clique</label><input type="hidden" name="produtos" id="produtos_input"><div style="max-height:320px; overflow:auto; margin-top:8px;">{produtos_html}</div>
        <button class="btn" type="submit">SALVAR</button>
      </form>
    </div>
    """
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="novo")

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
