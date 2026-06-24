from flask import Flask, request, render_template_string
import numpy as np

app = Flask(__name__)

current = {}
student = ""

# =========================
def integral(P, V):
    return np.sum((P[:-1] + P[1:]) / 2 * (V[1:] - V[:-1]))

def T(P, V):
    return P * V

# =========================
def proceso(tipo, V, P0, V0):

    V = np.array(V)

    # =========================
    # ISOBÁRICO (P CONSTANTE)
    # =========================
    if tipo == "isobarico":
        return np.full_like(V, P0)
    # =========================
    # ISOCÓRICO (V CONSTANTE → SOLO SENTIDO GRÁFICO)
    # =========================
    elif tipo == "isocorico":
        # IMPORTANTE: en P-V se dibuja vertical
        return np.linspace(P0, P0 * 1.4, len(V))

    # =========================
    # ISOTÉRMICO (PV = cte)
    # =========================
    elif tipo == "isotermico":
        k = P0 * V0
        return k / V

    # =========================
    # ADIABÁTICO (PV^γ = cte)
    # =========================
    elif tipo == "adiabatico":
        gamma = 1.4
        k = P0 * (V0 ** gamma)
        return k / (V ** gamma)

# =========================
def generar():

    V1 = np.random.randint(2, 5)
    V2 = np.random.randint(6, 10)
    P1 = np.random.randint(80, 120)

    procesos = np.random.choice(
        ["isotermico", "isobarico", "isocorico", "adiabatico"],
        3,
        replace=False
    )

    # Estado A
    VA = float(V1)
    PA = float(P1)

    # ========= A → B =========
    if procesos[0] == "isocorico":

        VB = VA
        PB = PA + np.random.randint(20, 50)

        V_AB = np.full(80, VA)
        P_AB = np.linspace(PA, PB, 80)

    elif procesos[0] == "isobarico":

        VB = float(V2)
        PB = PA

        V_AB = np.linspace(VA, VB, 80)
        P_AB = np.full(80, PA)

    else:

        VB = float(V2)

        V_AB = np.linspace(VA, VB, 80)
        P_AB = proceso(procesos[0], V_AB, PA, VA)

        PB = float(P_AB[-1])

    # ========= B → C =========
    if procesos[1] == "isocorico":

        VC = VB
        PC = PB + np.random.randint(-40, 40)

        V_BC = np.full(80, VB)
        P_BC = np.linspace(PB, PC, 80)

    elif procesos[1] == "isobarico":

        VC = VA
        PC = PB

        V_BC = np.linspace(VB, VC, 80)
        P_BC = np.full(80, PB)

    else:

        VC = VA

        V_BC = np.linspace(VB, VC, 80)
        P_BC = proceso(procesos[1], V_BC, PB, VB)

        PC = float(P_BC[-1])

    # ========= C → A =========
    if procesos[2] == "isocorico":

        V_CA = np.full(80, VC)
        P_CA = np.linspace(PC, PA, 80)

    elif procesos[2] == "isobarico":

        V_CA = np.linspace(VC, VA, 80)
        P_CA = np.full(80, PA)

    else:

        V_CA = np.linspace(VC, VA, 80)
        P_CA = proceso(procesos[2], V_CA, PC, VC)

        # Forzar cierre exacto
        P_CA[-1] = PA

    # ========= Trabajo =========
    W = (
        int(round(integral(P_AB, V_AB))),
        int(round(integral(P_BC, V_BC))),
        int(round(integral(P_CA, V_CA)))
    )

    # ========= Datos =========
    data = {
        "A": (int(VA), int(PA), int(T(PA, VA))),
        "B": (int(VB), int(PB), int(T(PB, VB))),
        "C": (int(VC), int(PC), int(T(PC, VC)))
    }

    # ========= Gráfica =========
    plot = [
        {
            "V": V_AB.tolist(),
            "P": P_AB.tolist(),
            "name": f"A→B ({procesos[0]})",
            "color": "#3b82f6"
        },
        {
            "V": V_BC.tolist(),
            "P": P_BC.tolist(),
            "name": f"B→C ({procesos[1]})",
            "color": "#22c55e"
        },
        {
            "V": V_CA.tolist(),
            "P": P_CA.tolist(),
            "name": f"C→A ({procesos[2]})",
            "color": "#f97316"
        }
    ]

    return {
        "plot": plot,
        "data": data,
        "procesos": procesos,
        "W": W
    }
# ========================= HTML =========================
html = """
<!DOCTYPE html>
<html>
<head>
<title>PHET Termodinámica PRO</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

<style>
body{
    background:#0b1220;
    color:white;
    font-family:Arial;
    margin:0;
    text-align:center;
}

.container{
    display:flex;
    height:100vh;
}

.panel{
    width:30%;
    background:#111827;
    padding:20px;
}

.sim{
    width:70%;
    padding:10px;
}

.card{
    background:#1f2937;
    padding:15px;
    margin:10px;
    border-radius:12px;
}

input{
    width:90%;
    padding:8px;
    margin:5px;
}

button{
    width:95%;
    padding:10px;
    margin:5px;
    border:none;
    cursor:pointer;
    font-weight:bold;
}

.gen{background:#22c55e;color:white}
.ver{background:#3b82f6;color:white}
.new{background:#ef4444;color:white}

.good{color:#22c55e}
.bad{color:#ef4444}
</style>
</head>

<body>

<div class="container">

<div class="panel">

<h2>🧪 Simulador</h2>

<form method="POST">
<input name="nombre" placeholder="Estudiante" required>
<button class="gen" name="accion" value="generar">Generar ciclo</button>
</form>

{% if data %}

<div class="card">
<h3>📊 Estado del sistema</h3>

<table style="width:100%; border-collapse:collapse; text-align:center;">
    
    <tr style="background:#374151;">
        <th>Estado</th>
        <th>V</th>
        <th>P</th>
        <th>T</th>
    </tr>

    <tr>
        <td>A</td>
        <td>{{data.A[0]}}</td>
        <td>{{data.A[1]}}</td>
        <td>{{data.A[2]}}</td>
    </tr>

    <tr style="background:#1f2937;">
        <td>B</td>
        <td>{{data.B[0]}}</td>
        <td>{{data.B[1]}}</td>
        <td>{{data.B[2]}}</td>
    </tr>

    <tr>
        <td>C</td>
        <td>{{data.C[0]}}</td>
        <td>{{data.C[1]}}</td>
        <td>{{data.C[2]}}</td>
    </tr>

</table>
</div>

<p><b>Procesos:</b></p>
<p>{{procesos}}</p>
</div>

<div class="card">

<form method="POST">

<input name="w_ab" placeholder="W A→B" required>
<input name="w_bc" placeholder="W B→C" required>
<input name="w_ca" placeholder="W C→A" required>

<button class="ver" name="accion" value="verificar">Verificar</button>
<button class="new" name="accion" value="nuevo">Nuevo</button>

</form>

<h3 class="{% if mensaje=='Correcto' %}good{% else %}bad{% endif %}">
{{mensaje}}
</h3>

</div>

{% endif %}

</div>

<div class="sim">
<div id="graph"></div>
</div>

</div>

<script>

var dataPlot = {{ plot|tojson if plot else 'null' }};
var dataState = {{ data|tojson if data else 'null' }};

if (dataPlot && dataState) {

    var traces = dataPlot.map(p => ({
        x: p.V,
        y: p.P,
        mode: "lines+markers",
        name: p.name,
        line: {width: 3}
    }));

    var A = dataState.A;
    var B = dataState.B;
    var C = dataState.C;

    traces.push({
        x: [A[0]], y: [A[1]],
        mode: "markers+text",
        text: ["A"],
        textposition: "top center",
        marker: {size: 10, color: "red"},
        name: "A"
    });

    traces.push({
        x: [B[0]], y: [B[1]],
        mode: "markers+text",
        text: ["B"],
        textposition: "top center",
        marker: {size: 10, color: "yellow"},
        name: "B"
    });

    traces.push({
        x: [C[0]], y: [C[1]],
        mode: "markers+text",
        text: ["C"],
        textposition: "top center",
        marker: {size: 10, color: "lime"},
        name: "C"
    });

    Plotly.newPlot("graph", traces, {
        paper_bgcolor:"#0b1220",
        plot_bgcolor:"#0b1220",
        font:{color:"white"},
        title:"Diagrama P-V (Ciclo Termodinámico)",
        xaxis:{title:"Volumen"},
        yaxis:{title:"Presión"}
    });
}

</script>

</body>
</html>
"""

# ========================= APP =========================
@app.route("/", methods=["GET","POST"])
def home():

    global current, student
    mensaje = ""

    if request.method == "POST":

        accion = request.form["accion"]

        if accion == "generar":
            student = request.form["nombre"]
            current = generar()
            mensaje = ""

        elif accion == "verificar":

            W = current["W"]

            u = (
                float(request.form["w_ab"]),
                float(request.form["w_bc"]),
                float(request.form["w_ca"])
            )

            tol = 0.1

            ok = all(abs(u[i]-W[i]) <= tol*abs(W[i]) for i in range(3))

            mensaje = "Correcto" if ok else "Incorrecto"

        elif accion == "nuevo":
            current = {}
            student = ""
            mensaje = ""

    return render_template_string(html,
        plot=current.get("plot"),
        data=current.get("data"),
        procesos=current.get("procesos"),
        mensaje=mensaje
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
