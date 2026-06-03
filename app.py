import streamlit as st
import urllib.request, json, random

st.set_page_config(page_title="Manunuzi AI — Uwazi wa Zabuni", page_icon="📋", layout="wide")
st.markdown("""<style>
.stApp{background:#0a0c10;color:#e8edf5}
.m-card{background:#0d1117;border:1px solid #21262d;border-radius:10px;padding:12px 16px;margin:6px 0}
.red-flag{background:#1a0000;border:1px solid #ff0000;border-radius:8px;padding:8px 12px;margin:4px 0}
.green{color:#56d364}.red{color:#f85149}.yellow{color:#e3b341}
.stButton>button{background:#1f6feb;color:#fff;border:none;border-radius:8px;padding:10px 20px;font-weight:700}
</style>""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY","")

# DEMO synthetic procurement data (source: DEMO — synthetic, not real PPO data)
random.seed(42)
DEMO_CONTRACTS = [
    {"id":"PPO/2024/001","ministry":"Ministry of Health","county":"Nairobi","description":"Supply of medical equipment to county hospitals","value":45_000_000,"supplier":"MedEquip Kenya Ltd","method":"Open Tender","bidders":7,"date":"2024-03-15","status":"Awarded","flags":[]},
    {"id":"PPO/2024/002","ministry":"Ministry of Roads","county":"Kiambu","description":"Tarmacking of rural access roads — Phase 3","value":120_000_000,"supplier":"BuildRight Construction","method":"Restricted Tender","bidders":1,"date":"2024-04-02","status":"Awarded","flags":["SINGLE_BID","HIGH_VALUE_RESTRICTED"]},
    {"id":"PPO/2024/003","ministry":"Ministry of Agriculture","county":"Nakuru","description":"Supply of certified maize seeds to farmers","value":8_500_000,"supplier":"SeedCo Kenya","method":"Open Tender","bidders":4,"date":"2024-02-28","status":"Awarded","flags":[]},
    {"id":"PPO/2024/004","ministry":"County Executive","county":"Mombasa","description":"Renovation of county headquarters offices","value":85_000_000,"supplier":"Premium Builders Ltd","method":"Direct Procurement","bidders":1,"date":"2024-05-10","status":"Awarded","flags":["DIRECT_PROCUREMENT","RELATED_PARTY_RISK"]},
    {"id":"PPO/2024/005","ministry":"Ministry of Education","county":"Kisumu","description":"Supply of school desks and furniture","value":12_000_000,"supplier":"FurniturePro Kenya","method":"Open Tender","bidders":9,"date":"2024-01-20","status":"Awarded","flags":[]},
    {"id":"PPO/2024/006","ministry":"Ministry of Water","county":"Turkana","description":"Borehole drilling — 12 sites","value":36_000_000,"supplier":"WaterWell Drillers","method":"Open Tender","bidders":3,"date":"2024-03-01","status":"Awarded","flags":[]},
    {"id":"PPO/2024/007","ministry":"County Health","county":"Nairobi","description":"Purchase of ambulances — emergency fleet","value":95_000_000,"supplier":"AutoMed International","method":"Restricted Tender","bidders":1,"date":"2024-06-05","status":"Under Review","flags":["SINGLE_BID","OVERPRICED_ESTIMATE"]},
]

FLAG_LABELS = {
    "SINGLE_BID": ("🚨 Single Bidder", "red", "Only one supplier bid — no competition. Risk of inflated prices."),
    "HIGH_VALUE_RESTRICTED": ("⚠️ High Value + Restricted", "yellow", "High-value contract awarded via restricted tender — reduced transparency."),
    "DIRECT_PROCUREMENT": ("🔴 Direct Procurement", "red", "No competitive process — direct award. Highest corruption risk."),
    "RELATED_PARTY_RISK": ("⚠️ Related Party", "yellow", "Supplier may have connections to procuring entity — verify."),
    "OVERPRICED_ESTIMATE": ("⚠️ Possible Overpricing", "yellow", "Contract value significantly above market estimates for this scope."),
}

def ask_ai(q):
    if not API_KEY: return "❌ API key not configured."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    body = {"contents":[{"role":"user","parts":[{"text":q}]}],
            "systemInstruction":{"parts":[{"text":"Wewe ni mchambuzi wa zabuni za serikali Kenya. Eleza ukweli kwa Kiswahili na Kiingereza. Toa uchambuzi wa hatari za ufisadi bila kuchukua upande wowote wa kisiasa."}]},
            "generationConfig":{"temperature":0.2,"maxOutputTokens":600}}
    try:
        req = urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(req,timeout=30) as r:
            return json.loads(r.read())["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e: return f"❌ {e}"

st.markdown("# 📋 Manunuzi AI")
st.markdown("**Uwazi wa Zabuni za Serikali Kenya | Government Procurement Transparency**")
st.warning("⚠️ **DEMO DATA** — Mikataba hii ni ya mfano (synthetic). Kwa data halisi: ppo.go.ke")

tab1, tab2, tab3 = st.tabs(["🔍 Tafuta Mikataba", "🚨 Alama za Hatari", "🤖 Uchambuzi wa AI"])

with tab1:
    c1,c2,c3 = st.columns(3)
    with c1: county_f = st.selectbox("Kaunti", ["Zote"]+list(set(c["county"] for c in DEMO_CONTRACTS)))
    with c2: min_v = st.number_input("Thamani min (KES)", value=0, step=1_000_000)
    with c3: flag_only = st.checkbox("Alama za hatari tu")
    filtered = [c for c in DEMO_CONTRACTS
                if (county_f=="Zote" or c["county"]==county_f)
                and c["value"]>=min_v
                and (not flag_only or c["flags"])]
    for c in filtered:
        flag_badges = " ".join([f'<span style="background:#1a0000;color:#ff5252;padding:2px 8px;border-radius:4px;font-size:0.72rem;margin:2px">{FLAG_LABELS[f][0]}</span>' for f in c["flags"]]) if c["flags"] else '<span style="color:#56d364">✅ Uchunguzi safi</span>'
        st.markdown(f"""<div class="m-card">
<b>{c["id"]}</b> — {c["ministry"]} ({c["county"]})<br>
{c["description"]}<br>
<b>KES {c["value"]:,}</b> | {c["method"]} | Washindani: {c["bidders"]} | {c["date"]}<br>
Muuzaji: {c["supplier"]}<br>{flag_badges}
</div>""", unsafe_allow_html=True)

with tab2:
    flagged = [c for c in DEMO_CONTRACTS if c["flags"]]
    st.markdown(f"### 🚨 {len(flagged)} kati ya {len(DEMO_CONTRACTS)} mikataba ina alama za hatari")
    for c in flagged:
        for flag in c["flags"]:
            lbl, color, desc = FLAG_LABELS[flag]
            st.markdown(f"""<div class="red-flag">
<b>{lbl}</b> — {c["id"]} ({c["ministry"]})<br>
<small>{desc}</small><br>
KES {c["value"]:,} | {c["method"]} | Muuzaji: {c["supplier"]}
</div>""", unsafe_allow_html=True)

with tab3:
    q_type = st.selectbox("Swali la uchambuzi:", [
        "Ni mikataba gani yenye hatari kubwa zaidi ya ufisadi?",
        "Linganisha thamani ya mikataba kwa kaunti zote",
        "Msambazaji gani amepewa mikataba mingi zaidi?",
        "Jinsi ya ripoti uchunguzi wa zabuni hii",
        "Eleza hatari za zabuni ya moja kwa moja (direct procurement)"
    ])
    if st.button("🤖 Changanua", key="ai_btn"):
        context = json.dumps([{"id":c["id"],"value":c["value"],"method":c["method"],"bidders":c["bidders"],"flags":c["flags"],"supplier":c["supplier"]} for c in DEMO_CONTRACTS])
        with st.spinner("Ninachambua..."):
            result = ask_ai(f"Data ya mikataba: {context}\n\nSwali: {q_type}")
        st.markdown(f'<div class="m-card">{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("📋 Manunuzi AI v1.0 | Data: DEMO synthetic | PPO Kenya: ppo.go.ke | CC BY-NC-ND 4.0")
