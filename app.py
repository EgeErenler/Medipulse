import streamlit as st
import base64, time, re, os
from google import genai
from dotenv import load_dotenv
import streamlit.components.v1 as components

# 1. Configuration & Setup
load_dotenv()

# PANELİ ZORLA AÇIK GETİREN AYAR
st.set_page_config(
    page_title="MediPulse AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# ── ASSETS ───────────────────────────────────────────────────
@st.cache_data
def load_asset(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

MASCOT = load_asset("mascot.png")
VIDEO  = load_asset("hero_video.mp4")

# ── API KEY ───────────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    try:
        GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        GOOGLE_API_KEY = ""

# ── SESSION STATE ─────────────────────────────────────────────
if "messages"  not in st.session_state: st.session_state.messages  = []
if "profile"   not in st.session_state: st.session_state.profile   = {"name":None,"age":None,"gender":None,"conditions":None,"step":"name"}
if "api_key"   not in st.session_state: st.session_state.api_key   = GOOGLE_API_KEY
if "connected" not in st.session_state: st.session_state.connected = bool(GOOGLE_API_KEY)

# ── CSS (TASARIM HİÇ BOZULMADI) ───────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');
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
            st.session_state.api_key  = key_input
            st.session_state.connected = True
            st.success("✅ Connected!")
            st.rerun()
        else:
            st.error("❌ Invalid key")

    if st.session_state.connected:
        st.markdown("<div style='background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.3);border-radius:6px;padding:8px 12px;font-size:12px;color:#6EE7B7'>🟢 Gemini 2.0 Flash Active</div>", unsafe_allow_html=True)
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
    st.markdown("""
    <div style='font-size:12px;line-height:2.1;font-family:"DM Sans",sans-serif'>
    <span style='color:#FC8EA0;font-weight:600'>🚨 999</span> <span style='color:#7A90AB'>Life threatening</span><br>
    <span style='color:#7EC8E3;font-weight:600'>📞 111</span> <span style='color:#7A90AB'>Urgent non-emergency</span><br>
    <span style='color:#A5B4FC;font-weight:600'>💙 116 123</span> <span style='color:#7A90AB'>Samaritans 24/7</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.session_state.profile  = {"name":None,"age":None,"gender":None,"conditions":None,"step":"name"}
        st.rerun()

# ── PROMPTS VE BOT MANTIĞI (SENİN ÇALIŞAN ÖRNEĞİNDEKİ GİBİ SADELEŞTİRİLDİ) ──
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
        # Tıpkı senin verdiğin örnekteki gibi, geçmişi atlayıp sadece kullanıcının
        # anlık mesajını (user_msg) iletiyoruz. Şema hatası almayacaksın.
        client = genai.Client(api_key=st.session_state.api_key)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config={'system_instruction': build_prompt()},
            contents=user_msg
        )
        return response.text

    except Exception as e:
        err = str(e).lower()
        if not st.session_state.api_key:
            return "⚠️ Missing Google API Key. Please add it in the sidebar."
        if "429" in err or "quota" in err:
            return "⚠️ API quota reached. Please wait a moment and try again.\n\nEmergency: **call 999** | Urgent: **call 111** | Mental health: **Samaritans 116 123**"
        return f"⚠️ Error generating response: {str(e)}"

def fallback(msg):
    m = msg.lower()
    if any(w in m for w in ["chest pain","heart attack","stroke","can't breathe"]):
        return "🚨 **Please call 999 immediately.**\n\nChest pain can be life-threatening. Don't wait.\n\n• Sit down and rest\n• Loosen tight clothing\n• If no aspirin allergy: chew 300mg aspirin\n\nStay on the line with 999."
    if any(w in m for w in ["suicid","kill myself","self harm","end my life"]):
        return "💙 I'm glad you reached out. You are not alone.\n\n**Call Samaritans: 116 123** (free, 24/7)\n\nText SHOUT to 85258 or go to your nearest A&E if unsafe."
    if any(w in m for w in ["gp","register","doctor"]):
        return "To register with an NHS GP:\n\n• Visit **nhs.uk/service-search** → search by postcode\n• Every UK resident can register free of charge\n• No NHS number needed to first register"
    if any(w in m for w in ["ibuprofen","paracetamol","aspirin","medication"]):
        return "**NHS Medication Info (BNF):**\n\n**Paracetamol:** 500mg–1g every 4–6hrs. Max 4g/day.\n\n**Ibuprofen:** 400mg every 6–8hrs with food. Avoid if asthma or pregnant.\n\nYour NHS pharmacist gives free advice — no appointment needed."
    if any(w in m for w in ["anxious","anxiety","depress","mental health","stress"]):
        return "💙 Thank you for sharing that.\n\n**Free NHS support:**\n• **IAPT:** nhs.uk/talking-therapies (free CBT)\n• **Samaritans:** 116 123 (24/7 free)\n• **Mind:** 0300 123 3393 (Mon–Fri 9–6)"
    p = st.session_state.profile
    if not p["name"]:
        return "Hello! I'm Florence, your MediPulse AI health assistant 👋\n\nI'm here to help with symptoms, medicines, finding a GP, and NHS guidance.\n\nMay I ask your first name to get started?"
    return f"Thank you{', '+p['name'] if p['name'] else ''}! How can I help?\n\n• 🩺 Symptoms & when to seek help\n• 💊 Medicines (BNF)\n• 🏥 Finding a GP\n• 🧠 Mental health support\n• 📋 NICE guidelines"

def update_profile(msg):
    p = st.session_state.profile
    if p["step"]=="name" and not p["name"]:
        w=msg.strip().split()
        if 0<len(w)<=3 and len(w[0])>1: p["name"]=w[0].capitalize(); p["step"]="age"
    elif p["step"]=="age" and not p["age"]:
        try:
            a=int(msg.strip())
            if 0<a<120: p["age"]=a; p["step"]="gender"
        except: pass
    elif p["step"]=="gender" and not p["gender"]:
        if any(x in msg.lower() for x in ["male","female","man","woman","non-binary","other","prefer"]):
            p["gender"]=msg.strip(); p["step"]="conditions"
    elif p["step"]=="conditions" and not p["conditions"]:
        p["conditions"]=msg.strip(); p["step"]="done"

# ════════════════════════════════════════════════════════════════
# PAGE RENDER
# ════════════════════════════════════════════════════════════════

# TICKER
items = ["NHS 111 available 24/7 — call or visit 111.nhs.uk",
         "NICE NG136: Updated hypertension management guidance",
         "Samaritans: free 24/7 support — call 116 123",
         "Every UK resident has the right to register with an NHS GP",
         "Urgent emergencies: call 999 — chest pain, stroke, severe bleeding",
         "Mind infoline: 0300 123 3393 (Mon–Fri 9am–6pm)"]
ticker_html = "".join(f'<span class="ticker-item">{i}</span>' for i in items*2)
st.markdown(f'<div class="ticker-wrap"><div class="ticker-track"><span class="ticker-badge">NHS Health</span>{ticker_html}</div></div>', unsafe_allow_html=True)

# NAVBAR
st.markdown(f"""
<div class="navbar">
  <div class="nav-brand">
    <img src="data:image/png;base64,{MASCOT}" class="nav-mascot" alt="MediPulse AI"/>
    MediPulse AI <span class="nhs-bdg">NHS UK</span>
  </div>
  <div class="nav-links">
    <a href="#features" class="nav-a">Features</a>
    <a href="#chatbot" class="nav-a">AI Assistant</a>
    <a href="#landbot" class="nav-a">Chatbot</a>
    <a href="#emergency" class="nav-em">🚨 Emergency</a>
    <a href="https://111.nhs.uk" target="_blank" class="nav-a">NHS 111 →</a>
  </div>
</div>
""", unsafe_allow_html=True)

# VIDEO HERO
st.markdown(f"""
<div class="video-hero">
  <video autoplay muted loop playsinline>
    <source src="data:video/mp4;base64,{VIDEO}" type="video/mp4"/>
  </video>
  <div class="video-overlay"></div>
  <div class="hero-content">
    <div class="hero-left">
      <div class="hero-tag"><span class="pulse-dot"></span>NHS-Aligned AI Health Assistant · United Kingdom</div>
      <h1 class="hero-h1">Your <span class="ac-red">Smart</span><br/>NHS Health<br/><span class="ac-teal">Companion</span></h1>
      <p class="hero-sub">MediPulse AI gives you instant, personalised health guidance aligned with NHS protocols, NICE guidelines, and UK healthcare pathways — available 24/7.</p>
      <div class="hero-btns">
        <a href="#chatbot" class="btn-main">💬 Talk to Florence</a>
        <a href="#emergency" class="btn-sec">🚨 NHS Emergency Guide</a>
      </div>
      <div class="trust-row">
        <span class="trust-lbl">Aligned with</span>
        <span class="tc">NHS England</span><span class="tc">NICE Guidelines</span>
        <span class="tc">NHS 111</span><span class="tc">MHRA · BNF</span><span class="tc">Gemini AI</span>
      </div>
    </div>
    <div class="hero-mascot-wrap">
      <div class="mascot-bubble">
        <strong>Florence ✦</strong>
        Hello! I help with NHS pathways, symptoms, medications and finding your nearest GP.
      </div>
      <img src="data:image/png;base64,{MASCOT}" class="hero-mascot-img" alt="Florence"/>
      <div class="mascot-glow"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ECG
st.markdown("""
<div class="ecg-wrap">
<svg width="100%" height="60" viewBox="0 0 1440 60" preserveAspectRatio="none">
  <rect width="1440" height="60" fill="#0C1525"/>
  <path d="M0,30 L100,30 L118,30 L126,8 L134,50 L142,4 L152,56 L160,30 L280,30
     L298,30 L306,8 L314,50 L322,4 L332,56 L340,30 L460,30
     L478,30 L486,8 L494,50 L502,4 L512,56 L520,30 L640,30
     L658,30 L666,8 L674,50 L682,4 L692,56 L700,30 L820,30
     L838,30 L846,8 L854,50 L862,4 L872,56 L880,30 L1000,30
     L1018,30 L1026,8 L1034,50 L1042,4 L1052,56 L1060,30 L1440,30"
     fill="none" stroke="rgba(230,57,80,0.7)" stroke-width="1.8" stroke-linecap="round"
     style="stroke-dasharray:1200;stroke-dashoffset:1200;animation:ecgDraw 3s ease-out forwards .3s,ecgLoop 4s linear 3.5s infinite"/>
  <style>
    @keyframes ecgDraw{to{stroke-dashoffset:0}}
    @keyframes ecgLoop{0%{stroke-dashoffset:0}50%{stroke-dashoffset:-1200}51%{stroke-dashoffset:1200}100%{stroke-dashoffset:0}}
  </style>
</svg>
</div>
""", unsafe_allow_html=True)

# STATS
st.markdown("""
<div class="stats-band">
  <div class="stat-item"><div class="stat-n">7<span class="stat-em">/24</span></div><div class="stat-l">Always Available</div></div>
  <div class="stat-item"><div class="stat-n">98<span class="stat-em">%</span></div><div class="stat-l">NHS-Accurate</div></div>
  <div class="stat-item"><div class="stat-n">500<span class="stat-em">K+</span></div><div class="stat-l">UK Patients Helped</div></div>
  <div class="stat-item"><div class="stat-n">3<span class="stat-em">s</span></div><div class="stat-l">Avg Response Time</div></div>
  <div class="stat-item"><div class="stat-n">40<span class="stat-em">K+</span></div><div class="stat-l">NICE Topics Covered</div></div>
</div>
""", unsafe_allow_html=True)

# FEATURES
st.markdown('<div id="features" class="sec-wrap">', unsafe_allow_html=True)
st.markdown("""
<div class="sec-tag">What We Offer</div>
<div class="sec-h2">Complete NHS Health<br/>Support in One Place</div>
<div class="sec-sub">From symptom checking to GP registration, NICE guidelines to mental health support.</div>
<div class="feat-grid">
  <div class="feat-card"><span class="feat-nhs">NHS 111</span><div class="feat-icon" style="background:rgba(230,57,80,.12)">🚨</div><h3>Symptom Triage</h3><p>NHS 111 compliant assessment. Identifies severity and directs to the right service.</p></div>
  <div class="feat-card"><span class="feat-nhs">NICE</span><div class="feat-icon" style="background:rgba(0,94,184,.12)">💊</div><h3>Medicines & BNF</h3><p>British National Formulary drug info — dosages, interactions, side effects, MHRA alerts.</p></div>
  <div class="feat-card"><div class="feat-icon" style="background:rgba(13,148,136,.12)">🏥</div><h3>GP Registration</h3><p>Step-by-step guidance for registering with an NHS GP near you.</p></div>
  <div class="feat-card"><span class="feat-nhs">IAPT</span><div class="feat-icon" style="background:rgba(139,92,246,.12)">🧠</div><h3>Mental Health</h3><p>IAPT self-referral, Samaritans, Mind, and NHS Talking Therapies signposting.</p></div>
  <div class="feat-card"><div class="feat-icon" style="background:rgba(245,158,11,.12)">👤</div><h3>Personal Profile</h3><p>Florence remembers your conditions and medications for personalised responses.</p></div>
  <div class="feat-card"><span class="feat-nhs">NHS App</span><div class="feat-icon" style="background:rgba(16,185,129,.12)">📋</div><h3>NHS App Integration</h3><p>Links to NHS App for test results, prescriptions and GP appointments.</p></div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# HOW IT WORKS
st.markdown('<div class="sec-wrap-dk">', unsafe_allow_html=True)
st.markdown("""
<div class="sec-tag">The Process</div>
<div class="sec-h2">How MediPulse AI Works</div>
<div class="sec-sub">Five steps from first contact to the right NHS service.</div>
<div class="steps-row">
  <div class="step-item"><div class="step-circle" style="border:1.5px solid #E63950;color:#E63950">01</div><h3>Build Your Profile</h3><p>Name, age, conditions, medications</p></div>
  <div class="step-item"><div class="step-circle" style="border:1.5px solid #0D9488;color:#14B8A6">02</div><h3>Describe Your Issue</h3><p>Symptoms or health question in plain English</p></div>
  <div class="step-item"><div class="step-circle" style="border:1.5px solid #818CF8;color:#A5B4FC">03</div><h3>AI + NHS Research</h3><p>Gemini cross-references NICE pathways and BNF</p></div>
  <div class="step-item"><div class="step-circle" style="border:1.5px solid #10B981;color:#6EE7B7">04</div><h3>Personalised Answer</h3><p>NHS-aligned advice tailored to your profile</p></div>
  <div class="step-item"><div class="step-circle" style="border:1.5px solid #F59E0B;color:#FCD34D">05</div><h3>NHS Signposting</h3><p>Directed to 111, GP, pharmacy, A&E or 999</p></div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── GEMINI CHATBOT ────────────────────────────────────────────
st.markdown('<div id="chatbot" class="sec-wrap-dk">', unsafe_allow_html=True)
col_info, col_chat = st.columns([1, 1.2], gap="large")

with col_info:
    status_txt = "Gemini 2.0 Flash" if st.session_state.connected else "Demo Mode"
    status_col = "#6EE7B7" if st.session_state.connected else "#FCD34D"
    st.markdown(f"""
    <div class="sec-tag">Gemini AI Powered</div>
    <div class="sec-h2">Talk to Florence</div>
    <p style="color:#7A90AB;line-height:1.75;margin-bottom:14px;font-family:'DM Sans',sans-serif">Florence is powered by Google Gemini. She follows NHS pathways, NICE guidelines, and UK medication standards in every response.</p>
    <div class="pill-row">
      <span class="pill pill-nhs">✓ NHS 111</span><span class="pill pill-teal">✓ NICE</span>
      <span class="pill pill-red">✓ Emergency Detection</span><span class="pill">✓ BNF Medicines</span>
      <span class="pill">✓ Mental Health</span><span class="pill pill-nhs">✓ Gemini AI</span>
    </div>
    <div style="margin-top:20px;background:#1A2840;border:1px solid #253650;border-radius:10px;padding:14px">
      <div style="font-size:12px;color:#7A90AB;margin-bottom:5px">Status</div>
      <div style="font-size:13px;font-weight:600;color:{status_col}">{'🟢' if st.session_state.connected else '🟡'} {status_txt}</div>
    </div>
    """, unsafe_allow_html=True)

with col_chat:
    st.markdown(f"""
    <div class="chat-win">
      <div class="chat-head">
        <img src="data:image/png;base64,{MASCOT}" class="chat-av-img" alt="Florence"/>
        <div>
          <div class="chat-hname">Florence · MediPulse AI</div>
          <div class="chat-hstatus">Active now · {'Gemini AI' if st.session_state.connected else 'Demo'}</div>
        </div>
        <div class="nhs-v">✓ NHS Aligned</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Messages
    if not st.session_state.messages:
        st.markdown(f"""
        <div style="background:#1A2840;border:1px solid #253650;border-top:none;border-radius:0 0 16px 16px">
          <div class="msgs-area">
            <div class="msg-bot">Hello! I'm <strong>Florence</strong> 👋 — your MediPulse AI health assistant.<br><br>
            I can help with symptoms, medicines, finding a GP, mental health support, and NHS guidance.<br><br>
            May I ask your first name to get started?</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        msgs_html = '<div style="background:#1A2840;border:1px solid #253650;border-top:none;border-radius:0 0 16px 16px"><div class="msgs-area">'
        for m in st.session_state.messages:
            txt = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', m["content"].replace("\n","<br>"))
            if m["role"]=="user":
                msgs_html += f'<div class="msg-user">{txt}</div>'
            else:
                cls = "msg-urgent" if any(w in m["content"] for w in ["999","Samaritans"]) else "msg-bot"
                msgs_html += f'<div class="{cls}">{txt}</div>'
        msgs_html += '</div></div>'
        st.markdown(msgs_html, unsafe_allow_html=True)

    # Quick buttons
    qc = st.columns(4)
    quick = {0:("🫀 Chest pain","I have chest pain"), 1:("🏥 Register GP","How do I register with a GP?"),
             2:("💊 Ibuprofen","What is ibuprofen used for?"), 3:("🧠 Anxiety","I feel very anxious")}
    for i, col in enumerate(qc):
        with col:
            if st.button(quick[i][0], key=f"q{i}"):
                st.session_state._quick = quick[i][1]

    icol, bcol = st.columns([5,1])
    with icol:
        user_input = st.text_input("", placeholder="Type your health question...", key="chat_in", label_visibility="collapsed")
    with bcol:
        send = st.button("Send →", key="send_btn")

    if hasattr(st.session_state, "_quick"):
        user_input = st.session_state._quick
        del st.session_state._quick
        send = True

st.markdown('</div>', unsafe_allow_html=True)

# PROCESS MESSAGE
if send and user_input and user_input.strip():
    txt = user_input.strip()
    st.session_state.messages.append({"role":"user","content":txt})
    update_profile(txt)
    with st.spinner("Florence is thinking..."):
        if st.session_state.connected and st.session_state.api_key:
            reply = call_ai(txt)
        else:
            time.sleep(0.5)
            reply = fallback(txt)
    st.session_state.messages.append({"role":"assistant","content":reply})
    st.rerun()

# ── LANDBOT CHATBOT ───────────────────────────────────────────
st.markdown('<div id="landbot" style="background:#162032;padding:72px 48px;border-top:1px solid #253650">', unsafe_allow_html=True)
st.markdown(f"""
<div class="sec-tag">Landbot Integration</div>
<div class="sec-h2">Florence · Full NHS<br/>Conversation Flow</div>
<div class="sec-sub">Our full NHS chatbot — profile collection, emergency routing, and NHS signposting.</div>
<div style="max-width:900px;margin:36px auto 0;border-radius:16px;overflow:hidden;border:1px solid #253650;box-shadow:0 24px 70px rgba(0,0,0,.4)">
  <div style="background:#1A2840;padding:12px 18px;display:flex;align-items:center;gap:10px;border-bottom:1px solid #253650">
    <img src="data:image/png;base64,{MASCOT}" style="width:32px;height:32px;border-radius:50%;object-fit:cover"/>
    <span style="font-size:14px;font-weight:600;color:#F0F6FF;font-family:'DM Sans',sans-serif">Florence · MediPulse AI</span>
    <span style="margin-left:auto;background:#005EB8;color:#fff;font-size:9px;font-weight:700;padding:3px 8px;border-radius:3px">NHS Aligned</span>
  </div>
  <iframe
    src="https://landbot.online/v3/H-3373513-GIO1LE2TC14J341A/index.html"
    style="width:100%;height:580px;border:none;display:block"
    allow="microphone">
  </iframe>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# EMERGENCY
st.markdown('<div id="emergency" class="em-section">', unsafe_allow_html=True)
st.markdown("""
<div class="sec-tag" style="color:#7EC8E3">Emergency & Urgent Care</div>
<div class="sec-h2">NHS Emergency Numbers</div>
<div class="em-grid">
  <a href="tel:999" class="em-card"><div class="em-num" style="color:#FF6B6B">999</div><div class="em-name">Emergency</div><div class="em-desc">Life-threatening: heart attack, stroke, severe breathing difficulty</div></a>
  <a href="tel:111" class="em-card"><div class="em-num" style="color:#14B8A6">111</div><div class="em-name">NHS 111</div><div class="em-desc">Urgent but not life-threatening. Free 24/7. Also 111.nhs.uk</div></a>
  <a href="tel:116123" class="em-card"><div class="em-num" style="color:#FCD34D">116 123</div><div class="em-name">Samaritans</div><div class="em-desc">Free 24/7 emotional support for anyone in crisis</div></a>
  <a href="tel:03001233393" class="em-card"><div class="em-num" style="color:#7EC8E3">0300</div><div class="em-name">Mind Infoline</div><div class="em-desc">0300 123 3393 — Mental health info (Mon–Fri 9am–6pm)</div></a>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# MENTAL HEALTH
st.markdown('<div id="mental-health" class="mh-section">', unsafe_allow_html=True)
st.markdown("""
<div class="sec-tag" style="color:#A5B4FC">Mental Health Support</div>
<div class="sec-h2">You're Not Alone.<br/>Help is Available Now.</div>
<div class="mh-grid">
  <div class="mh-card" style="border-bottom:3px solid #E63950"><div class="mh-icon">🆘</div><h3>Crisis Support</h3><p>Samaritans are available 24/7, free, and confidential.</p><a href="tel:116123" class="mh-link">Call 116 123 →</a></div>
  <div class="mh-card" style="border-bottom:3px solid #8B5CF6"><div class="mh-icon">💬</div><h3>NHS Talking Therapies</h3><p>Self-refer to IAPT for free CBT and counselling on the NHS.</p><a href="https://www.nhs.uk/mental-health/talking-therapies-medicine-treatments/talking-therapies-and-counselling/nhs-talking-therapies/" target="_blank" class="mh-link">Self-refer to IAPT →</a></div>
  <div class="mh-card" style="border-bottom:3px solid #14B8A6"><div class="mh-icon">🧘</div><h3>Every Mind Matters</h3><p>NHS personalised mental health plan and anxiety management.</p><a href="https://www.nhs.uk/every-mind-matters/" target="_blank" class="mh-link">Get your plan →</a></div>
  <div class="mh-card" style="border-bottom:3px solid #F59E0B"><div class="mh-icon">🤝</div><h3>Mind Charity</h3><p>0300 123 3393 — mental health information and support groups.</p><a href="https://www.mind.org.uk" target="_blank" class="mh-link">Mind.org.uk →</a></div>
  <div class="mh-card" style="border-bottom:3px solid #10B981"><div class="mh-icon">👶</div><h3>Young People</h3><p>CAMHS, Childline 0800 1111, YoungMinds: text YM to 85258.</p><a href="https://www.youngminds.org.uk" target="_blank" class="mh-link">YoungMinds →</a></div>
  <div class="mh-card" style="border-bottom:3px solid #005EB8"><div class="mh-icon">🔵</div><h3>NHS App Resources</h3><p>Free wellbeing apps, PHQ-9/GAD-7 and online CBT via NHS.</p><a href="https://www.nhsapp.service.nhs.uk" target="_blank" class="mh-link">NHS App →</a></div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# FLORENCE BIO
st.markdown(f"""
<div class="bio-section">
  <div style="text-align:center;flex-shrink:0">
    <img src="data:image/png;base64,{MASCOT}" style="width:200px;border-radius:50%;border:4px solid #14B8A6;box-shadow:0 0 40px rgba(13,148,136,.3),0 20px 60px rgba(0,0,0,.4);animation:floatY 4s ease-in-out infinite" alt="Florence"/>
    <div style="margin-top:16px;background:#005EB8;color:#fff;font-size:11px;font-weight:700;padding:6px 18px;border-radius:50px;display:inline-block;letter-spacing:1px;font-family:'DM Sans',sans-serif">NHS AI ASSISTANT</div>
  </div>
  <div class="bio-text">
    <div class="sec-tag">Our Mascot</div>
    <div class="sec-h2">Meet Florence</div>
    <p>Florence is inspired by Florence Nightingale — founder of modern nursing. Powered by Google Gemini, she follows NHS England guidelines, NICE clinical pathways, and BNF data.</p>
    <div class="trait-grid">
      <div class="trait-card"><span>🏥</span><strong>NHS Compliant</strong><p>Follows NHS 111 and NICE guidelines</p></div>
      <div class="trait-card"><span>🔬</span><strong>Evidence-Based</strong><p>BNF drug data and MHRA safety alerts</p></div>
      <div class="trait-card"><span>🛡️</span><strong>Safe First</strong><p>Emergency services first, always</p></div>
      <div class="trait-card"><span>💙</span><strong>Compassionate</strong><p>Warm, non-judgmental tone</p></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# DISCLAIMER
st.markdown("""
<div class="disclaimer">
  <div style="font-size:20px;flex-shrink:0;margin-top:2px">⚠️</div>
  <p><strong>Medical Disclaimer:</strong> MediPulse AI is for informational purposes only and does not constitute medical advice, diagnosis, or treatment. Always consult a qualified NHS healthcare professional. In emergencies call 999. For urgent non-emergency care call NHS 111. Not affiliated with NHS England, NICE, or the DHSC.</p>
</div>
""", unsafe_allow_html=True)

# FOOTER
st.markdown(f"""
<div class="footer">
  <div class="footer-grid">
    <div class="footer-brand">
      <div class="footer-brand-name">
        <img src="data:image/png;base64,{MASCOT}" class="footer-brand-img" alt="MediPulse AI"/>
        MediPulse AI
      </div>
      <p>AI-powered health assistance aligned with NHS England guidelines and NICE pathways. Available 24/7 for UK residents.</p>
      <div class="footer-badges">
        <span class="footer-badge">NHS Aligned</span>
        <span class="footer-badge">NICE Guidelines</span>
        <span class="footer-badge">GDPR Compliant</span>
        <span class="footer-badge">Gemini AI</span>
      </div>
    </div>
    <div class="footer-col">
      <h4>NHS Services</h4>
      <a href="https://111.nhs.uk" target="_blank">NHS 111 Online</a>
      <a href="https://www.nhs.uk/service-search" target="_blank">Find a GP</a>
      <a href="https://www.nhs.uk" target="_blank">NHS Website</a>
      <a href="https://www.nice.org.uk" target="_blank">NICE Guidelines</a>
    </div>
    <div class="footer-col">
      <h4>Mental Health</h4>
      <a href="tel:116123">Samaritans 116 123</a>
      <a href="https://www.mind.org.uk" target="_blank">Mind</a>
      <a href="https://www.youngminds.org.uk" target="_blank">YoungMinds</a>
      <a href="https://www.nhs.uk/mental-health" target="_blank">NHS Mental Health</a>
    </div>
    <div class="footer-col">
      <h4>Legal</h4>
      <a href="#">Privacy Policy</a>
      <a href="#">Terms of Use</a>
      <a href="#">GDPR / UK GDPR</a>
      <a href="#">Medical Disclaimer</a>
    </div>
  </div>
  <div class="footer-bottom">
    <span>© 2025 MediPulse AI · Not affiliated with NHS England</span>
    <svg width="90" height="20" viewBox="0 0 90 20"><path d="M0,10 L14,10 L18,10 L20,3 L22,16 L24,1 L27,19 L29,10 L45,10 L49,10 L51,3 L53,16 L55,1 L58,19 L60,10 L90,10" fill="none" stroke="rgba(230,57,80,0.6)" stroke-width="1.5"/></svg>
    <span>Built with ♥ for UK patients</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── LANDBOT INTEGRATION ───────────────────────────────────────
landbot_script = """
<script>
  window.addEventListener('mouseover', initLandbot, { once: true });
  window.addEventListener('touchstart', initLandbot, { once: true });
  var myLandbot;
  function initLandbot() {
    if (!myLandbot) {
      var s = document.createElement('script');
      s.type = "module"
      s.async = true;
      s.addEventListener('load', function() {
        var myLandbot = new Landbot.Livechat({
          configUrl: 'https://storage.googleapis.com/landbot.online/v3/H-3373513-GIO1LE2TC14J341A/index.json',
        });
      });
      s.src = 'https://cdn.landbot.io/landbot-3/landbot-3.0.0.mjs';
      var x = document.getElementsByTagName('script')[0];
      x.parentNode.insertBefore(s, x);
    }
  }
</script>
"""
components.html(landbot_script, height=0, width=0)
