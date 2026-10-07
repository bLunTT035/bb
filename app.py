from flask import Flask, render_template_string, request, redirect
import os
from datetime import datetime

app = Flask(__name__)

# PRODUTOS - REI DA NAVALHA
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

HTML_BASE = """
<!DOCTYPE html>
<html>
<head>
<title>Rei da Navalha - PRO</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    body { margin:0; font-family: Arial, sans-serif; background: #0d2d6b; }
    .header { background: #ffffff; border-bottom: 5px solid #c8102e; padding: 12px 20px; display:flex; justify-content:space-between; align-items:center; }
    .header h1 { margin:0; color: #000000; font-size: 22px; font-weight: 900; display:flex; align-items:center; gap:8px; }
    .header h1 span { color: #c8102e; }
    .crown { font-size:28px; }
    .header a { text-decoration:none; color:#000; background:#e5e7eb; padding:6px 12px; border-radius:20px; font-size:13px; font-weight:bold; margin-left:5px; border:1px solid #0d2d6b; }
    .header a.active { background:#c8102e; color:white; border-color:#c8102e; }
    .container { max-width: 800px; margin: 20px auto; padding: 15px; }
    .card { background: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border-left: 6px solid #c8102e; border-right: 6px solid #0d2d6b; }
    .card h2 { color: #000000 !important; margin-top:0; }
    label { color: #000000; font-weight: bold; font-size:13px; display:block; margin-top:12px; }
    input, select { width:100%; padding:10px; border:2px solid #0d2d6b; border-radius:8px; margin-top:4px; box-sizing:border-box; color:#000; font-weight:bold; background:white; }
    .btn { background: #c8102e; color: white; border: none; padding: 14px; width:100%; border-radius:8px; font-weight:900; margin-top:18px; cursor:pointer; text-transform:uppercase; letter-spacing:1px; font-size:15px; }
    .btn:hover { background:#a00d24; }
    .prod-item { border:1.5px solid #d1d5db; padding:10px; border-radius:8px; margin-bottom:8px; display:flex; justify-content:space-between; cursor:pointer; background:white; color:#000; }
    .prod-item.selected { background:#0d2d6b; color:white; border-color:#0d2d6b; }
    .prod-item.selected small, .prod-item.selected b { color:white !important; }
    .prod-item b { color:#000; }
    .prod-item small { color:#555; }
    .tag { background:#c8102e; color:white; font-size:10px; padding:2px 6px; border-radius:4px; }
    .prod-item.selected .tag { background:white; color:#c8102e; }
    .total-box { border:2.5px solid #000; background:#fffbe6; }
    .stat { background:white; padding:15px; border-radius:10px; text-align:center; border-bottom:4px solid #c8102e; border-top:4px solid #0d2d6b; }
    .stat h3 { margin:0; color:#000; }
    .stat p { margin:5px 0 0 0; color:#000; font-weight:bold; }
</style>
</head>
<body>
<div class="header">
  <h1><span class="crown">👑</span> REI DA <span>NAVALHA</span></h1>
  <div>
    <a href="/" class="{{'active' if active=='inicio' else ''}}">Início</a>
    <a href="/produtos" class="{{'active' if active=='prod' else ''}}">Produtos</a>
    <a href="/historico" class="{{'active' if active=='hist' else ''}}">Histórico</a>
    <a href="/novo" style="background:#c8102e; color:white;">+ Novo</a>
  </div>
</div>
<div class="container">
{{content}}
</div>
<script>
function toggleProd(id) {
  const el = document.getElementById('p-'+id);
  const input = document.getElementById('produtos_input');
  let selecionados = input.value ? input.value.split(',').filter(x=>x) : [];
  if(el.classList.contains('selected')) {
    el.classList.remove('selected');
    selecionados = selecionados.filter(x=> x != id);
  } else {
    el.classList.add('selected');
    selecionados.push(id);
  }
  input.value = selecionados.join(',');
  calcTotal();
}
function calcTotal() {
  const servicoVal = parseFloat(document.getElementById('valor_servico').value) || 0;
  const input = document.getElementById('produtos_input');
  let selecionados = input.value ? input.value.split(',').filter(x=>x) : [];
  let totalProd = 0;
  selecionados.forEach(sid => {
    const p = document.getElementById('preco-'+sid);
    if(p) totalProd += parseFloat(p.value);
  });
  const total = servicoVal + totalProd;
  document.getElementById('total_auto').value = total.toFixed(2);
  document.getElementById('total_view').innerText = 'R$ ' + total.toFixed(2);
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    total_vendas = sum(a['total'] for a in atendimentos_db)
    content = f"""
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-bottom:20px;">
      <div class="stat"><h3 style="color:#c8102e; font-size:24px;">{len(atendimentos_db)}</h3><p>Atendimentos</p></div>
      <div class="stat"><h3 style="color:#0d2d6b; font-size:20px;">R$ {total_vendas:.2f}</h3><p>Faturamento</p></div>
      <div class="stat"><h3 style="font-size:24px;">{len(produtos_db)}</h3><p>Produtos</p></div>
    </div>
    <div class="card">
      <h2>👑 Bem-vindo ao Rei da Navalha</h2>
      <p style="color:#000; font-weight:bold;">Sistema PRO - Fundo azul, detalhes branco e vermelho, letras pretas.</p>
      <p style="color:#000;">Gerencie cortes, barbas e venda de Minoxidil, Pomada, Gel e Creme com soma automática.</p>
      <a href="/novo"><button class="btn">+ Novo Atendimento</button></a>
    </div>
    """
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="inicio")

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
        atendimentos_db.append({
            "id": len(atendimentos_db)+1,
            "cliente": cliente,
            "servico": servico,
            "valor_servico": valor_servico,
            "produtos": ", ".join(prod_nomes),
            "total": total,
            "pagamento": pagamento,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        return redirect("/historico")
    
    produtos_html = ""
    for p in produtos_db:
        produtos_html += f"""
        <div class="prod-item" id="p-{p['id']}" onclick="toggleProd({p['id']})">
          <div><span class="tag">{p['categoria']}</span> <b>{p['nome']}</b><br><small>R$ {p['preco']:.2f}</small></div>
          <div>✓</div>
          <input type="hidden" id="preco-{p['id']}" value="{p['preco']}">
        </div>
        """

    servicos_opt = "".join([f'<option>{s}</option>' for s in servicos])
    
    content = f"""
    <div class="card">
      <h2>Novo Atendimento</h2>
      <form method="POST">
        <label>Cliente *</label>
        <input name="cliente" required placeholder="Nome do cliente">
        <label>Pagamento</label>
        <select name="pagamento"><option>Dinheiro</option><option>Pix</option><option>Cartão</option></select>
        <div style="display:grid; grid-template-columns: 2fr 1fr 1fr; gap:10px;">
          <div>
            <label>Serviço *</label>
            <select name="servico">{servicos_opt}</select>
          </div>
          <div>
            <label>Valor Serviço</label>
            <input id="valor_servico" name="valor_servico" type="number" value="35" oninput="calcTotal()">
          </div>
          <div>
            <label>Total (Auto)</label>
            <input id="total_auto" class="total-box" name="total_auto" readonly style="font-weight:900; color:#000;" value="35.00">
            <small id="total_view" style="color:#c8102e; font-weight:900;">R$ 35.00</small>
          </div>
        </div>
        <label style="margin-top:20px;">PRODUTOS PARA VENDA - clique para adicionar (soma automático)</label>
        <input type="hidden" name="produtos" id="produtos_input">
        <div style="max-height:320px; overflow:auto; margin-top:8px; padding-right:5px;">
        {produtos_html}
        </div>
        <button class="btn" type="submit">SALVAR ATENDIMENTO</button>
      </form>
    </div>
    """
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="novo")

@app.route("/historico")
def historico():
    rows = ""
    for a in reversed(atendimentos_db):
        rows += f"<tr style='color:#000;'><td style='padding:8px; border-bottom:1px solid #ccc;'>{a['data']}</td><td style='padding:8px; border-bottom:1px solid #ccc; font-weight:bold;'>{a['cliente']}</td><td style='padding:8px; border-bottom:1px solid #ccc;'>{a['servico']}<br><small style='color:#c8102e; font-weight:bold;'>{a['produtos']}</small></td><td style='padding:8px; border-bottom:1px solid #ccc; font-weight:900;'>R$ {a['total']:.2f}</td></tr>"
    if not rows:
        rows = "<tr><td colspan=4 style='padding:20px; text-align:center; color:#000; font-weight:bold;'>Nenhum atendimento ainda</td></tr>"
    content = f"""
    <div class="card">
      <h2>Histórico de Atendimentos</h2>
      <table style="width:100%; border-collapse:collapse; margin-top:10px;">
        <tr style="background:#0d2d6b; color:white;"><th style="padding:10px; text-align:left;">Data</th><th style="padding:10px; text-align:left;">Cliente</th><th style="padding:10px; text-align:left;">Serviço + Produtos</th><th style="padding:10px; text-align:left;">Total</th></tr>
        {rows}
      </table>
    </div>
    """
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="hist")

@app.route("/produtos")
def produtos():
    rows = ""
    for p in produtos_db:
        rows += f"<tr style='color:#000;'><td style='padding:10px; border-bottom:1px solid #ccc;'><span class='tag'>{p['categoria']}</span> <b style='margin-left:5px;'>{p['nome']}</b></td><td style='padding:10px; border-bottom:1px solid #ccc; font-weight:900;'>R$ {p['preco']:.2f}</td></tr>"
    content = f"""
    <div class="card">
      <h2>👑 Produtos - Rei da Navalha</h2>
      <table style="width:100%; border-collapse:collapse; margin-top:10px;">
        <tr style="background:#0d2d6b; color:white;"><th style="padding:10px; text-align:left;">Produto</th><th style="padding:10px; text-align:left;">Preço</th></tr>
        {rows}
      </table>
    </div>
    """
    return render_template_string(HTML_BASE.replace("{{content}}", content), active="prod")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
