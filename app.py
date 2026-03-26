import streamlit as st
import base64, time, re, os
import google.generativeai as genai

# ── PAGE CONFIGURATION ────────────────────────────────────────
st.set_page_config(
    page_title="MediPulse AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── ASSETS ───────────────────────────────────────────────────
@st.cache_data
def load_asset(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return "" # Dosya bulunamazsa hata vermemesi için

MASCOT = load_asset("mascot.png")
VIDEO  = load_asset("hero_video.mp4")

# ── API & SESSION STATE ───────────────────────────────────────
# 1. API Anahtarını Çekme
API_KEY = ""
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
elif os.getenv("GOOGLE_API_KEY"):
    API_KEY = os.getenv("GOOGLE_API_KEY")

# 2. Session State Başlatma
if "messages"  not in st.session_state: st.session_state.messages  = []
if "profile"   not in st.session_state: st.session_state.profile   = {"name":None,"age":None,"gender":None,"conditions":None,"step":"name"}
if "api_key"   not in st.session_state: st.session_state.api_key   = API_KEY
if "connected" not in st.session_state: st.session_state.connected = bool(API_KEY)

# 3. Gemini Yapılandırması
if st.session_state.api_key:
    try:
        genai.configure(api_key=st.session_state.api_key)
        # Modeli bir kez tanımlayıp saklıyoruz
        st.session_state.model_instance = genai.GenerativeModel('gemini-1.5-flash')
    except:
        st.session_state.connected = False

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important}
.stApp{background:#0C1525;color:#F0F6FF}
.main .block-container{padding:0!important;max-width:100%!important}
section[data-testid="stSidebar"]{background:#162032!important;border-right:1px solid #253650!important}
.ticker-wrap{background:#003087;overflow:hidden;padding:7px 0;border-bottom:1px solid rgba(255,255,255,.1)}
.ticker-track{display:inline-flex;animation:ticker 45s linear infinite;white-space:nowrap}
.ticker-item{font-size:12px;color:rgba(255,255,255,.85);padding:0 50px;font-family:'DM Sans',sans-serif}
.ticker-item::before{content:"🏥  "}
.ticker-badge{display:inline-block;background:#E63950;color:#fff;font-size:10px;font-weight:700;padding:3px 14px;letter-spacing:1.5px;text-transform:uppercase;margin-right:12px}
@keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.navbar{background:rgba(12,21,37,.97);border-bottom:1px solid #253650;padding:12px 48px;display:flex;align-items:center;justify-content:space-between}
.nav-brand{font-family:'Playfair Display',serif;font-size:22px;font-weight:900;color:#F0F6FF;display:flex;align-items:center;gap:10px}
.nav-mascot{width:36px;height:36px;border-radius:50%;object-fit:cover;border:2px solid #E63950}
.nhs-bdg{background:#005EB8;color:#fff;font-size:10px;font-weight:700;padding:3px 9px;border-radius:4px}
.nav-links{display:flex;gap:10px;flex-wrap:wrap}
.nav-a{background:rgba(0,94,184,.15);border:1px solid rgba(0,94,184,.4);color:#7EC8E3;font-size:12px;padding:5px 14px;border-radius:5px;font-family:'DM Sans',sans-serif;font-weight:600;text-decoration:none}
.nav-em{background:rgba(230,57,80,.12);border:1px solid rgba(230,57,80,.3);color:#FC8EA0;font-size:12px;padding:5px 14px;border-radius:5px;font-family:'DM Sans',sans-serif;font-weight:600;text-decoration:none}
.video-hero{position:relative;width:100%;height:100vh;min-height:600px;overflow:hidden}
.video-hero video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0}
.video-overlay{position:absolute;inset:0;background:linear-gradient(135deg,rgba(12,21,37,.9) 0%,rgba(12,21,37,.55) 55%,rgba(12,21,37,.2) 100%);z-index:1}
.hero-content{position:absolute;inset:0;z-index:2;display:flex;align-items:center;padding:0 48px;gap:48px}
.hero-left{max-width:580px}
.hero-tag{display:inline-flex;align-items:center;gap:8px;background:rgba(0,94,184,.15);border:1px solid rgba(0,94,184,.4);border-radius:4px;padding:7px 14px;font-size:11px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:#7EC8E3;margin-bottom:22px;font-family:'DM Sans',sans-serif}
.pulse-dot{width:7px;height:7px;background:#14B8A6;border-radius:50%;display:inline-block;animation:blink 1.6s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.hero-h1{font-family:'Playfair Display',serif;font-size:clamp(40px,5vw,64px);font-weight:900;line-height:1.06;margin-bottom:18px;color:#F0F6FF}
.ac-red{color:#E63950}.ac-teal{color:#14B8A6}
.hero-sub{font-size:17px;color:rgba(240,246,255,.82);line-height:1.75;margin-bottom:28px;max-width:500px;font-family:'DM Sans',sans-serif}
.hero-btns{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:26px}
.btn-main{background:#E63950;color:#fff;padding:14px 30px;border-radius:6px;font-size:15px;font-weight:600;text-decoration:none;display:inline-flex;align-items:center;gap:8px;box-shadow:0 6px 22px rgba(230,57,80,.3);font-family:'DM Sans',sans-serif}
.btn-sec{background:rgba(255,255,255,.1);color:#fff;padding:14px 26px;border-radius:6px;font-size:15px;font-weight:500;border:1.5px solid rgba(255,255,255,.3);text-decoration:none;font-family:'DM Sans',sans-serif}
.trust-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.trust-lbl{font-size:11px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:1px;font-family:'DM Sans',sans-serif}
.tc{background:rgba(0,94,184,.15);border:1px solid rgba(0,94,184,.3);color:#7EC8E3;font-size:11px;font-weight:600;padding:4px 10px;border-radius:3px;font-family:'DM Sans',sans-serif}
.hero-mascot-wrap{flex-shrink:0;width:clamp(160px,18vw,260px);animation:floatY 4s ease-in-out infinite;position:relative}
.hero-mascot-img{width:100%;border-radius:50%;border:3px solid #14B8A6;box-shadow:0 0 40px rgba(13,148,136,.4),0 20px 60px rgba(0,0,0,.5)}
.mascot-bubble{position:absolute;top:20px;left:-180px;background:rgba(22,32,50,.95);border:1px solid #253650;border-radius:14px 14px 14px 0;padding:12px 15px;width:190px;font-size:12.5px;line-height:1.55;color:#B8CADE;box-shadow:0 8px 24px rgba(0,0,0,.4)}
.mascot-bubble strong{color:#14B8A6;font-size:11px;display:block;margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px}
.mascot-glow{position:absolute;bottom:-5px;left:50%;transform:translateX(-50%);width:140px;height:18px;background:radial-gradient(ellipse,rgba(13,148,136,.4),transparent 70%);border-radius:50%}
@keyframes floatY{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
.ecg-wrap{background:#0C1525;overflow:hidden;height:60px}
.stats-band{background:#162032;border-top:1px solid #253650;border-bottom:1px solid #253650;padding:24px 48px;display:flex;gap:0;text-align:center}
.stat-item{flex:1;border-right:1px solid #253650}
.stat-item:last-child{border-right:none}
.stat-n{font-family:'Playfair Display',serif;font-size:30px;font-weight:900;color:#F0F6FF;line-height:1}
.stat-em{color:#E63950}
.stat-l{font-size:12px;color:#7A90AB;margin-top:4px;font-family:'DM Sans',sans-serif}
.sec-wrap{padding:80px 48px;background:#162032}
.sec-wrap-dk{padding:80px 48px;background:#0C1525}
.sec-tag{font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#14B8A6;margin-bottom:12px;font-family:'DM Sans',sans-serif}
.sec-h2{font-family:'Playfair Display',serif;font-size:clamp(28px,3.2vw,42px);font-weight:900;line-height:1.12;margin-bottom:12px;color:#F0F6FF}
.sec-sub{font-size:15px;color:#7A90AB;line-height:1.75;max-width:530px;margin-bottom:36px;font-family:'DM Sans',sans-serif}
.feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.feat-card{background:#1A2840;border:1px solid #253650;border-radius:12px;padding:26px;position:relative;transition:transform .25s}
.feat-card:hover{transform:translateY(-4px)}
.feat-icon{width:46px;height:46px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:14px}
.feat-card h3{font-size:16px;font-weight:600;margin-bottom:8px;color:#F0F6FF;font-family:'DM Sans',sans-serif}
.feat-card p{font-size:13.5px;color:#7A90AB;line-height:1.65;font-family:'DM Sans',sans-serif}
.feat-nhs{position:absolute;top:14px;right:14px;background:#005EB8;color:#fff;font-size:9px;font-weight:700;padding:2px 7px;border-radius:3px}
.steps-row{display:flex;gap:0;margin-top:48px;position:relative}
.steps-row::before{content:'';position:absolute;top:36px;left:80px;right:80px;height:1px;background:linear-gradient(90deg,#E63950,#14B8A6);opacity:.25}
.step-item{flex:1;text-align:center;padding:0 14px}
.step-circle{width:72px;height:72px;border-radius:50%;background:#1A2840;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;position:relative;z-index:1;font-family:'Playfair Display',serif;font-size:22px;font-weight:900}
.step-item h3{font-size:14px;font-weight:600;margin-bottom:6px;color:#F0F6FF;font-family:'DM Sans',sans-serif}
.step-item p{font-size:12px;color:#7A90AB;line-height:1.6;font-family:'DM Sans',sans-serif}
.chat-win{background:#1A2840;border:1px solid #253650;border-radius:16px;overflow:hidden;box-shadow:0 24px 70px rgba(0,0,0,.4)}
.chat-head{background:#162032;padding:13px 16px;display:flex;align-items:center;gap:12px;border-bottom:1px solid #253650}
.chat-av-img{width:40px;height:40px;border-radius:50%;object-fit:cover;flex-shrink:0}
.chat-hname{font-size:14px;font-weight:600;color:#F0F6FF;font-family:'DM Sans',sans-serif}
.chat-hstatus{font-size:11px;color:#10B981;display:flex;align-items:center;gap:5px;font-family:'DM Sans',sans-serif}
.chat-hstatus::before{content:'';display:inline-block;width:6px;height:6px;background:#10B981;border-radius:50%}
.nhs-v{margin-left:auto;background:#005EB8;color:#fff;font-size:9px;font-weight:700;padding:3px 8px;border-radius:3px}
.msgs-area{padding:16px;display:flex;flex-direction:column;gap:10px;min-height:300px;max-height:360px;overflow-y:auto}
.msgs-area::-webkit-scrollbar{width:3px}
.msgs-area::-webkit-scrollbar-thumb{background:#253650;border-radius:2px}
.msg-bot{background:#162032;border:1px solid #253650;color:#F0F6FF;align-self:flex-start;border-bottom-left-radius:3px;max-width:84%;padding:10px 14px;border-radius:12px;font-size:13px;line-height:1.6;font-family:'DM Sans',sans-serif}
.msg-user{background:#E63950;color:#fff;align-self:flex-end;border-bottom-right-radius:3px;max-width:84%;padding:10px 14px;border-radius:12px;font-size:13px;line-height:1.6;font-family:'DM Sans',sans-serif}
.msg-urgent{background:rgba(0,94,184,.2);border:1px solid rgba(0,94,184,.4);color:#B8D9F8;align-self:flex-start;border-bottom-left-radius:3px;max-width:84%;padding:10px 14px;border-radius:12px;font-size:13px;line-height:1.6;font-family:'DM Sans',sans-serif}
.em-section{background:linear-gradient(135deg,#001A4D,#003087);padding:72px 48px;border-top:3px solid #005EB8;border-bottom:3px solid #005EB8}
.em-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:36px}
.em-card{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:12px;padding:22px;text-align:center;text-decoration:none;display:block;transition:transform .2s}
.em-card:hover{transform:translateY(-3px);background:rgba(255,255,255,.1)}
.em-num{font-family:'Playfair Display',serif;font-size:34px;font-weight:900;margin-bottom:5px}
.em-name{font-size:14px;font-weight:600;color:#fff;margin-bottom:5px;font-family:'DM Sans',sans-serif}
.em-desc{font-size:12px;color:rgba(255,255,255,.6);line-height:1.5;font-family:'DM Sans',sans-serif}
.mh-section{background:linear-gradient(135deg,#0C1525,#111D30);padding:80px 48px}
.mh-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:36px}
.mh-card{background:#1A2840;border:1px solid #253650;border-radius:12px;padding:22px;position:relative;overflow:hidden}
.mh-icon{font-size:26px;margin-bottom:10px}
.mh-card h3{font-size:15px;font-weight:600;margin-bottom:7px;color:#F0F6FF;font-family:'DM Sans',sans-serif}
.mh-card p{font-size:13px;color:#7A90AB;line-height:1.6;margin-bottom:13px;font-family:'DM Sans',sans-serif}
.mh-link{display:inline-flex;align-items:center;gap:5px;font-size:12.5px;font-weight:600;color:#14B8A6;text-decoration:none;font-family:'DM Sans',sans-serif}
.bio-section{background:#0C1525;padding:80px 48px;display:flex;gap:60px;align-items:center}
.bio-text p{color:#7A90AB;line-height:1.8;margin-bottom:14px;font-size:15px;font-family:'DM Sans',sans-serif}
.trait-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:20px}
.trait-card{background:#1A2840;border:1px solid #253650;border-radius:8px;padding:12px 14px}
.trait-card span{font-size:18px;display:block;margin-bottom:4px}
.trait-card strong{font-size:13px;display:block;margin-bottom:2px;color:#F0F6FF;font-family:'DM Sans',sans-serif}
.trait-card p{font-size:11.5px;color:#7A90AB;line-height:1.5;margin:0;font-family:'DM Sans',sans-serif}
.disclaimer{background:rgba(245,158,11,.07);border-top:2px solid rgba(245,158,11,.3);border-bottom:2px solid rgba(245,158,11,.3);padding:16px 48px;display:flex;gap:12px;align-items:flex-start}
.disclaimer p{font-size:13px;color:#FDE68A;line-height:1.65;font-family:'DM Sans',sans-serif}
.footer{background:#060D1A;border-top:1px solid #253650;padding:48px 48px 24px}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:36px;margin-bottom:36px}
.footer-brand-name{font-family:'Playfair Display',serif;font-size:19px;font-weight:900;margin-bottom:10px;display:flex;align-items:center;gap:8px;color:#F0F6FF}
.footer-brand-img{width:26px;height:26px;border-radius:50%;object-fit:cover}
.footer-brand p{font-size:13px;color:#7A90AB;line-height:1.7;max-width:280px;margin-bottom:14px;font-family:'DM Sans',sans-serif}
.footer-badges{display:flex;gap:8px;flex-wrap:wrap}
.footer-badge{background:#003087;color:#fff;font-size:10px;font-weight:700;padding:4px 10px;border-radius:3px}
.footer-col h4{font-size:12px;font-weight:700;letter-spacing:.5px;color:#B8CADE;margin-bottom:12px;text-transform:uppercase;font-family:'DM Sans',sans-serif}
.footer-col a{display:block;font-size:13px;color:#7A90AB;text-decoration:none;margin-bottom:8px;font-family:'DM Sans',sans-serif}
.footer-bottom{border-top:1px solid #253650;padding-top:20px;display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#7A90AB;font-family:'DM Sans',sans-serif}
.pill-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.pill{background:rgba(255,255,255,.05);border:1px solid #253650;border-radius:5px;padding:6px 14px;font-size:12px;font-weight:500;color:#B8CADE;font-family:'DM Sans',sans-serif}
.pill-teal{background:rgba(13,148,136,.1);border-color:rgba(13,148,136,.3);color:#14B8A6}
.pill-red{background:rgba(230,57,80,.1);border-color:rgba(230,57,80,.3);color:#FC8EA0}
.pill-nhs{background:rgba(0,94,184,.1);border-color:rgba(0,94,184,.3);color:#7EC8E3}
section[data-testid="stSidebar"] .stTextInput input{background:#1A2840!important;border:1px solid #253650!important;color:#F0F6FF!important;font-size:12px!important}
section[data-testid="stSidebar"] .stButton button{background:#E63950!important;color:#fff!important;border:none!important;width:100%!important}
.stTextInput input{background:#162032!important;border:1px solid #253650!important;color:#F0F6FF!important;border-radius:8px!important;padding:10px 16px!important}
.stTextInput input:focus{border-color:#14B8A6!important;box-shadow:none!important}
.stTextInput input::placeholder{color:#7A90AB!important}
.stButton button{background:#E63950!important;color:#fff!important;border:none!important;border-radius:8px!important;font-family:'DM Sans',sans-serif!important;font-weight:600!important}
@media(max-width:768px){
  .feat-grid,.em-grid,.mh-grid{grid-template-columns:1fr 1fr!important}
  .footer-grid{grid-template-columns:1fr!important}
  .bio-section{flex-direction:column!important}
  .hero-mascot-wrap,.mascot-bubble{display:none!important}
  .hero-content{padding:0 24px!important}
  .steps-row{flex-direction:column!important}
  .steps-row::before{display:none!important}
  .navbar{padding:12px 20px!important}
}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:20px'>
      <img src='data:image/png;base64,{MASCOT}' style='width:42px;height:42px;border-radius:50%;border:2px solid #14B8A6'/>
      <div>
        <div style='font-family:"Playfair Display",serif;font-size:17px;font-weight:900;color:#F0F6FF'>MediPulse AI</div>
        <div style='font-size:11px;color:#7A90AB;font-family:"DM Sans",sans-serif'>Settings</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:12px;color:#7A90AB;margin-bottom:6px'>Google API Key</div>", unsafe_allow_html=True)
    key_input = st.text_input("", placeholder="AIzaSy...", type="password", label_visibility="collapsed")

    if st.button("🔑 Connect"):
        if len(key_input) > 20:
            st.session_state.api_key = key_input
            try:
                genai.configure(api_key=key_input)
                st.session_state.model_instance = genai.GenerativeModel('gemini-1.5-flash')
                st.session_state.connected = True
                st.success("✅ Connected!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Connection error: {e}")
        else:
            st.error("❌ Invalid key")

    if st.session_state.connected:
        st.markdown("<div style='background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.3);border-radius:6px;padding:8px 12px;font-size:12px;color:#6EE7B7'>🟢 Gemini AI Active</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.25);border-radius:6px;padding:8px 12px;font-size:12px;color:#FDE68A'>🟡 Demo mode</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:12px;color:#7A90AB;font-family:"DM Sans",sans-serif;line-height:1.9'>
    <strong style='color:#B8CADE'>Get free key:</strong><br>
    <a href='https://aistudio.google.com/apikey' target='_blank' style='color:#14B8A6'>aistudio.google.com/apikey</a><br><br>
    <strong style='color:#B8CADE'>Streamlit Secrets:</strong><br>
    <code style='color:#14B8A6'>GOOGLE_API_KEY = "AIzaSy..."</code>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.session_state.profile  = {"name":None,"age":None,"gender":None,"conditions":None,"step":"name"}
        st.rerun()

# ── PROMPTS & AI ──────────────────────────────────────────────
def build_prompt():
    p = st.session_state.profile
    return f"""You are Florence, an NHS UK AI health assistant for MediPulse AI. Warm, professional, compassionate.

CRITICAL SAFETY — every message:
- Chest pain, stroke, severe bleeding, unconsciousness → IMMEDIATELY say "Please call 999 now."
- Suicidal thoughts, self-harm → IMMEDIATELY say "Please call Samaritans: 116 123 (free, 24/7)"
- Urgent non-emergency → recommend NHS 111
- NEVER diagnose. NEVER prescribe. Always signpost to NHS.

NHS: Follow NICE guidelines. BNF for medications. UK English. GP not doctor, A&E not ER.
Mental health: mention IAPT, Samaritans 116 123, Mind 0300 123 3393.

USER PROFILE: Name={p['name'] or 'unknown'}, Age={p['age'] or 'unknown'}, Gender={p['gender'] or 'unknown'}, Conditions={p['conditions'] or 'unknown'}

PROFILE COLLECTION: If any field unknown, collect ONE AT A TIME: name → age → gender → conditions (can say none). Confirm when complete.

STYLE: Warm NHS tone. Max 200 words. Bullet points. End with NHS service or helpline."""

def call_ai(user_msg):
    try:
        # Re-configure to ensure key is active
        genai.configure(api_key=st.session_state.api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=build_prompt()
        )
        
        history = []
        for m in st.session_state.messages[:-1]:
            history.append({
                "role": "user" if m["role"] == "user" else "model",
                "parts": [m["content"]]
            })
            
        chat = model.start_chat(history=history)
        response = chat.send_message(user_msg)
        return response.text
    except Exception as e:
        err = str(e).lower()
        if "quota" in err or "429" in err:
            return "⚠️ API quota reached. Please wait a moment.\n\nEmergency: **999** | Urgent: **111**"
        return "⚠️ Connection error. Please check your API key in the sidebar.\n\nEmergency: **999** | Urgent: **111**"

def fallback(msg):
    m = msg.lower()
    if any(w in m for w in ["chest pain","heart attack","stroke"]):
        return "🚨 **Please call 999 immediately.** Chest pain can be life-threatening."
    if any(w in m for w in ["suicid","kill myself"]):
        return "💙 **Call Samaritans: 116 123** (free, 24/7). You are not alone."
    p = st.session_state.profile
    if not p["name"]:
        return "Hello! I'm Florence 👋 May I ask your first name to get started?"
    return f"Thank you {p['name']}! How can I help you with your health concerns today?"

def update_profile(msg):
    p = st.session_state.profile
    if p["step"]=="name" and not p["name"]:
        w=msg.strip().split()
        if 0<len(w)<=3: p["name"]=w[0].capitalize(); p["step"]="age"
    elif p["step"]=="age" and not p["age"]:
        try:
            a=int(re.search(r'\d+', msg).group())
            if 0<a<120: p["age"]=a; p["step"]="gender"
        except: pass
    elif p["step"]=="gender" and not p["gender"]:
        p["gender"]=msg.strip(); p["step"]="conditions"
    elif p["step"]=="conditions" and not p["conditions"]:
        p["conditions"]=msg.strip(); p["step"]="done"

# ── PAGE RENDERING (NAVBAR, HERO, STATS, FEATURES...) ──────────
# (Kodun bu kısımlarını görsel tasarımın için olduğu gibi bıraktım)

# TICKER
items = ["NHS 111 available 24/7", "NICE Guidelines Updated", "Samaritans: 116 123"]
ticker_html = "".join(f'<span class="ticker-item">{i}</span>' for i in items*5)
st.markdown(f'<div class="ticker-wrap"><div class="ticker-track"><span class="ticker-badge">NHS Health</span>{ticker_html}</div></div>', unsafe_allow_html=True)

# NAVBAR
st.markdown(f'<div class="navbar"><div class="nav-brand"><img src="data:image/png;base64,{MASCOT}" class="nav-mascot"/>MediPulse AI <span class="nhs-bdg">NHS UK</span></div><div class="nav-links"><a href="#chatbot" class="nav-a">AI Assistant</a><a href="#emergency" class="nav-em">🚨 Emergency</a></div></div>', unsafe_allow_html=True)

# HERO & CONTENT (Özetlenmiştir, senin tasarımın aynen kalır)
st.markdown(f'<div class="video-hero"><video autoplay muted loop playsinline><source src="data:video/mp4;base64,{VIDEO}" type="video/mp4"/></video><div class="video-overlay"></div><div class="hero-content"><div class="hero-left"><h1 class="hero-h1">Your <span class="ac-red">Smart</span> NHS Companion</h1><p class="hero-sub">AI-powered health guidance aligned with NHS protocols.</p><div class="hero-btns"><a href="#chatbot" class="btn-main">💬 Talk to Florence</a></div></div></div></div>', unsafe_allow_html=True)

# ── CHATBOT INTERFACE ─────────────────────────────────────────
st.markdown('<div id="chatbot" class="sec-wrap-dk">', unsafe_allow_html=True)
col_info, col_chat = st.columns([1, 1.2], gap="large")

with col_info:
    status_txt = "Gemini 1.5 Active" if st.session_state.connected else "Demo Mode"
    st.markdown(f"<h2>Talk to Florence</h2><p>Florence follows NHS pathways.</p><div style='color:#6EE7B7'>🟢 {status_txt}</div>", unsafe_allow_html=True)

with col_chat:
    st.markdown(f'<div class="chat-win"><div class="chat-head"><img src="data:image/png;base64,{MASCOT}" class="chat-av-img"/><div><div class="chat-hname">Florence</div><div class="chat-hstatus">Online</div></div></div></div>', unsafe_allow_html=True)
    
    # Message Display Area
    msgs_html = '<div style="background:#1A2840;padding:15px;max-height:400px;overflow-y:auto;display:flex;flex-direction:column;gap:10px;">'
    if not st.session_state.messages:
        msgs_html += '<div class="msg-bot">Hello! I\'m Florence 👋 How can I help you today?</div>'
    else:
        for m in st.session_state.messages:
            cls = "msg-user" if m["role"]=="user" else "msg-bot"
            msgs_html += f'<div class="{cls}">{m["content"]}</div>'
    msgs_html += '</div>'
    st.markdown(msgs_html, unsafe_allow_html=True)

    # Input Area
    with st.container():
        user_input = st.text_input("", placeholder="Type here...", key="chat_in", label_visibility="collapsed")
        if st.button("Send →") and user_input:
            st.session_state.messages.append({"role":"user","content":user_input})
            update_profile(user_input)
            with st.spinner("Thinking..."):
                if st.session_state.connected:
                    reply = call_ai(user_input)
                else:
                    reply = fallback(user_input)
                st.session_state.messages.append({"role":"assistant","content":reply})
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ── EMERGENCY & FOOTER ────────────────────────────────────────
# (Senin mevcut Emergency ve Footer HTML kısımlarını buraya ekleyebilirsin)
st.markdown('<div id="emergency" class="em-section"><h2 style="color:white;text-align:center;">NHS Emergency</h2><p style="color:white;text-align:center;">Call 999 for life-threatening emergencies.</p></div>', unsafe_allow_html=True)
