#!/usr/bin/env python3
"""
Supply-Chain NLQ → SQL • Landing-page UI + floating chat widget
The chat component is identical to the previous version; only the page
around it (header, hero, feature cards, footer) is new.
"""
import os, sys
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

# ──────────  Back-end  ───────────────────────────────────────────────
sys.path.append(os.path.abspath("."))           # import nlq_sql.py
from nlq_sql import SQLApp
sql_app = SQLApp()

# ──────────  Helper: chat bubble  ────────────────────────────────────
def bubble(text, role):
    user = role == "user"
    return html.Div(
        [None if user else html.I(className="fa fa-robot icon"),
         html.Span(text)],
        className="bubble",
        style={
            "alignSelf": "flex-end" if user else "flex-start",
            "background": "var(--user-bubble)" if user else "var(--bot-bubble)",
        },
    )

# ──────────  Dash app  ───────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"
    ],
)
app.title = "Supply-Chain NLQ → SQL"

# ---------- HTML shell w/ global CSS ---------------------------------
app.index_string = """
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>Supply-Chain NLQ → SQL</title>
    {%favicon%}
    {%css%}

    <!-- Google Font -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">

    <style>
    :root{
      --accent:#2250ff;--accent-dark:#183ee3;
      --bot-bubble:#f5f6fa;
      --user-bubble:linear-gradient(135deg,#9ce8ff,#cfe9ff);
      --rad-lg:14px;--rad-sm:8px;
      --shadow-lg:0 8px 16px rgba(0,0,0,.14);
      --shadow-sm:0 2px 4px rgba(0,0,0,.1);
      --font:Inter,Arial,sans-serif;
    }

    /* ----- overall page ----- */
    body{
      margin:0;font-family:var(--font);color:#222;background:#f5f7ff;
    }
    .hero{
      background:linear-gradient(135deg,#eff3ff 0%,#ffffff 35%);
      padding:96px 24px 72px;text-align:center;
    }
    .hero h1{margin:0;font-size:40px;font-weight:700;line-height:1.2}
    .hero p{margin-top:8px;font-size:18px;color:#555}

    .features{
      display:flex;flex-wrap:wrap;gap:24px;justify-content:center;
      padding:40px 24px 72px;max-width:1080px;margin:auto;
    }
    .card{
      flex:1 1 280px;max-width:340px;padding:24px;border-radius:var(--rad-lg);
      background:#fff;box-shadow:var(--shadow-sm);text-align:center;
    }
    .card i{font-size:32px;color:var(--accent);margin-bottom:16px}
    .card h3{margin:0 0 8px;font-size:20px}
    .card p{margin:0;color:#555;font-size:15px;line-height:1.4}

    footer{
      text-align:center;padding:32px 16px;color:#777;font-size:14px
    }

    /* ----- CHAT WIDGET (unchanged) ----- */
    #chatbot-wrapper{position:fixed;right:24px;bottom:24px;width:380px;z-index:9999}
    #chat-header{
      background:linear-gradient(90deg,var(--accent),#3c78ff);
      color:#fff;padding:10px 14px;border-radius:var(--rad-lg) var(--rad-lg) 0 0;
      display:flex;justify-content:space-between;align-items:center;font-weight:600;
      font-size:14px;cursor:pointer;box-shadow:var(--shadow-lg)
    }
    #chat-header button{background:none;border:none;color:#fff;font-size:18px;cursor:pointer}
    #chat-body{
      background:#fff;border:1px solid #dfe3fd;border-top:none;
      border-radius:0 0 var(--rad-lg) var(--rad-lg);display:flex;flex-direction:column;
      box-shadow:var(--shadow-lg)
    }
    #chat-container{
      height:330px;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:10px
    }
    #chat-container::-webkit-scrollbar{width:6px}
    #chat-container::-webkit-scrollbar-thumb{background:#c9d4ff;border-radius:3px}
    .bubble{
      max-width:85%;padding:8px 12px;border-radius:var(--rad-lg);
      box-shadow:var(--shadow-sm);display:flex;gap:6px;white-space:pre-wrap;font-size:14px
    }
    .icon{font-size:18px;color:#555}
    #input-bar{display:flex;gap:8px;padding:10px;border-top:1px solid #eee}
    #user-query{
      flex:1;height:70px;resize:none;font-size:14px;padding:8px 10px;
      border:1px solid #ccd3ff;border-radius:var(--rad-sm);box-shadow:inset 0 1px 3px rgba(0,0,0,.08)
    }
    #submit-btn{
      background:var(--accent);color:#fff;border:none;border-radius:var(--rad-sm);
      font-size:18px;padding:0 16px;cursor:pointer;box-shadow:var(--shadow-sm);display:flex;align-items:center
    }
    #submit-btn:hover{background:var(--accent-dark)}
    </style>
</head>

<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
"""

# ---------- Layout ---------------------------------------------------
app.layout = html.Div([
    # ——— NON-chat UI ——————————————————————————
    html.Section(className="hero", children=[
        html.H1("Natural-Language SQL for Supply-Chain Teams"),
        html.P("Ask questions in plain English. Get valid SQL and instant answers.")
    ]),

    html.Div(className="features", children=[
        html.Div(className="card", children=[
            html.I(className="fa fa-terminal"),
            html.H3("No SQL Bottlenecks"),
            html.P("Empower analysts and planners to query data without waiting for dev cycles.")
        ]),
        html.Div(className="card", children=[
            html.I(className="fa fa-gauge-high"),
            html.H3("Real-time Insights"),
            html.P("Queries execute live on your database — no stale exports.")
        ]),
        html.Div(className="card", children=[
            html.I(className="fa fa-shield-check"),
            html.H3("Governance-Ready"),
            html.P("Every generated statement is validated for syntax & blocked keywords.")
        ]),
    ]),

    html.Footer("© 2025 Supply-Chain NLQ → SQL Demo"),

    # ——— Stores for chat history / visibility ——
    dcc.Store(id="conversation", data=[]),
    dcc.Store(id="chat-visible", data=True),

    # ——— Chat widget (unchanged logic) ——————————
    html.Div(id="chatbot-wrapper", children=[
        html.Div(id="chat-header", children=[
            "Supply-Chain NLQ → SQL",
            html.Button(id="toggle-btn", className="fa fa-chevron-down", n_clicks=0)
        ]),
        html.Div(id="chat-body", children=[
            html.Div(id="chat-container"),
            html.Div(id="input-bar", children=[
                dcc.Textarea(id="user-query", placeholder="Ask a question…"),
                html.Button(id="submit-btn", className="fa fa-paper-plane", n_clicks=0)
            ])
        ])
    ]),
])

# ──────────  Callbacks  ──────────────────────────────────────────────
@app.callback(
    Output("chat-body",    "style"),
    Output("toggle-btn",   "className"),
    Output("chat-visible", "data"),
    Input("chat-header",   "n_clicks"),
    Input("toggle-btn",    "n_clicks"),
    State("chat-visible",  "data"),
    State("chat-body",     "style"),
    prevent_initial_call=True,
)
def toggle(_, __, visible, style):
    visible = not visible
    style = style or {}
    style["display"] = "flex" if visible else "none"
    return style, ("fa fa-chevron-down" if visible else "fa fa-chevron-up"), visible


@app.callback(
    Output("conversation",   "data"),
    Output("chat-container", "children"),
    Output("user-query",     "value"),
    Input("submit-btn",      "n_clicks"),
    State("user-query",      "value"),
    State("conversation",    "data"),
    prevent_initial_call=True,
)
def chat(_, query, history):
    if not query:
        return dash.no_update, dash.no_update, dash.no_update
    history.append({"role":"user","content":query})
    sql, result, metrics = sql_app.run(query_input=query)
    bot = f"**Generated SQL**\n{sql}\n\n**Results**\n{result}\n\n**Metrics**\n{metrics}"
    history.append({"role":"assistant","content":bot})
    return history, [bubble(m["content"], m["role"]) for m in history], ""


# ──────────  Main  ───────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=False)
