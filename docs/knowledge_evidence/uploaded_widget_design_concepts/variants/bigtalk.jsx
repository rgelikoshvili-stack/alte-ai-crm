// VARIANT 3 — "Big Talk" — Duolingo-energy chunky bold playful
// Massive launcher, oversized type, confetti, bright accents

const bigtalkCss = `
.bt-root{ width:100%; height:100%; font-family:'Noto Sans Georgian','Inter',sans-serif; color:#0c1a1c; }
.bt-root *{ box-sizing:border-box; }

.bt-root{
  --teal:#074045; --teal-2:#0a5258; --teal-d:#03222a;
  --lime:#bef264; --lime-d:#84cc16;
  --coral:#ff6b6b; --coral-d:#e63946;
  --honey:#fbbf24; --honey-d:#d97706;
  --sky:#7dd3fc; --sky-d:#0284c7;
  --paper:#fffdf7;
}

/* page backdrop */
.bt-page{ width:100%; height:100%; background:#fffdf7; position:relative; overflow:hidden; }
.bt-page::after{ content:''; position:absolute; left:-40px; top:-40px; width:160px; height:160px; border-radius:50%; background:#fef3c7; opacity:0.7; }
.bt-page::before{ content:''; position:absolute; right:-60px; top:80px; width:120px; height:120px; border-radius:50%; background:#dbeafe; opacity:0.6; }
.bt-page .nav{ height:62px; background:#fff; border-bottom:3px solid #03222a; display:flex; align-items:center; padding:0 22px; gap:20px; position:relative; z-index:2; }
.bt-page .nav-logo{ font-family:'Fraunces',serif; font-weight:800; font-size:22px; color:#03222a; letter-spacing:-0.03em; }
.bt-page .nav-logo .dot{ color:#ff6b6b; }
.bt-page .nav-items{ display:flex; gap:18px; font-size:12.5px; color:#1a2628; font-weight:600; }
.bt-page .nav-r{ margin-left:auto; }
.bt-page .nav-r .btn{ background:#03222a; color:#fff; padding:8px 14px; border-radius:10px; font-size:11.5px; font-weight:700; }
.bt-page .hero{ padding:36px 28px 0; position:relative; z-index:2; }
.bt-page .hero h1{ font-family:'Fraunces',serif; font-size:38px; font-weight:800; color:#03222a; line-height:1; letter-spacing:-0.03em; margin:0 0 14px; max-width:340px; }
.bt-page .hero h1 .hl{ background:linear-gradient(180deg,transparent 60%,#bef264 60%); padding:0 4px; }
.bt-page .hero p{ font-size:14px; color:#1a2628; max-width:300px; line-height:1.5; margin:0 0 22px; font-weight:500; }
.bt-page .hero .btn{ display:inline-block; background:#03222a; color:#fff; padding:14px 22px; border-radius:14px; font-weight:700; font-size:13px; box-shadow:0 6px 0 #001012; }

/* MASSIVE Launcher */
.bt-launcher{ position:absolute; right:20px; bottom:20px; z-index:5; }
.bt-launcher .speech{ position:absolute; right:115px; bottom:42px; background:#fff; border:3px solid #03222a; border-radius:20px 20px 4px 20px; padding:12px 16px; font-size:13.5px; font-weight:600; color:#03222a; box-shadow:6px 6px 0 #03222a; max-width:200px; line-height:1.4; animation:btBob 4s ease-in-out infinite; }
.bt-launcher .speech::after{ content:''; position:absolute; bottom:-3px; right:-3px; width:14px; height:14px; background:#fff; border-right:3px solid #03222a; border-bottom:3px solid #03222a; transform:rotate(45deg) translate(-4px,-4px); }
.bt-launcher .big-btn{ width:118px; height:118px; border-radius:50%; background:#bef264; border:4px solid #03222a; box-shadow:0 10px 0 #03222a, 0 14px 30px rgba(0,0,0,0.25); display:flex; align-items:center; justify-content:center; position:relative; transform:rotate(-3deg); cursor:pointer; }
.bt-launcher .big-btn:hover{ transform:rotate(0deg) translateY(-2px); }
.bt-launcher .big-btn .face{ width:78px; height:78px; }
.bt-launcher .big-btn .badge{ position:absolute; top:-6px; right:-2px; background:#ff6b6b; color:#fff; font-size:11px; font-weight:800; padding:4px 9px; border-radius:20px; border:3px solid #03222a; box-shadow:0 3px 0 #03222a; transform:rotate(8deg); }
.bt-launcher .big-btn .ring{ position:absolute; inset:-12px; border:3px dashed #03222a; border-radius:50%; opacity:0.3; animation:btSpin 16s linear infinite; }
@keyframes btSpin{ to{ transform:rotate(360deg); } }
@keyframes btBob{ 0%,100%{ transform:translateY(0); } 50%{ transform:translateY(-4px); } }

/* widget shell */
.bt-shell{ width:100%; height:100%; background:#fffdf7; display:flex; flex-direction:column; overflow:hidden; position:relative; border:3px solid #03222a; }
.bt-topbar{ background:#03222a; color:#fff; padding:14px 16px; display:flex; align-items:center; gap:11px; }
.bt-topbar .face-circle{ width:44px; height:44px; border-radius:50%; background:#bef264; border:2.5px solid #fffdf7; display:flex; align-items:center; justify-content:center; position:relative; }
.bt-topbar .face-circle::after{ content:''; position:absolute; bottom:-2px; right:-2px; width:13px; height:13px; border-radius:50%; background:#84cc16; border:2px solid #03222a; }
.bt-topbar .nm{ font-family:'Fraunces',serif; font-size:17px; font-weight:800; letter-spacing:-0.02em; }
.bt-topbar .stt{ font-size:11px; color:#bef264; font-weight:600; }
.bt-topbar .acts{ margin-left:auto; display:flex; gap:7px; }
.bt-topbar .lang{ background:#fffdf7; color:#03222a; border-radius:10px; padding:5px 4px; display:flex; align-items:center; font-size:11px; font-weight:800; gap:2px; }
.bt-topbar .lang span{ padding:3px 8px; border-radius:7px; }
.bt-topbar .lang span.on{ background:#bef264; color:#03222a; }
.bt-topbar .ic{ width:34px; height:34px; border-radius:11px; background:rgba(255,255,255,0.1); display:flex; align-items:center; justify-content:center; color:#fffdf7; }

.bt-trust{ background:#bef264; color:#03222a; padding:7px 16px; font-size:11px; font-weight:700; display:flex; align-items:center; gap:7px; border-bottom:3px solid #03222a; }

.bt-msgs{ flex:1; overflow-y:auto; padding:16px; display:flex; flex-direction:column; gap:14px; background:#fffdf7; position:relative; }
.bt-msgs::before{ content:''; position:absolute; inset:0; background-image:radial-gradient(#03222a 1px, transparent 1px); background-size:18px 18px; opacity:0.04; pointer-events:none; }

.bt-composer{ background:#03222a; padding:12px 14px; display:flex; gap:9px; align-items:center; }
.bt-composer .inp{ flex:1; background:#fffdf7; border-radius:14px; padding:12px 14px; font-size:13px; color:#03222a; font-weight:500; border:2px solid #bef264; }
.bt-composer .inp.placeholder{ color:#5a6c6d; font-weight:500; }
.bt-composer .send{ width:46px; height:46px; border-radius:14px; background:#bef264; color:#03222a; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 0 #84cc16; }

/* Bubbles - chunky bold */
.bt-row{ display:flex; gap:9px; align-items:flex-end; }
.bt-row.u{ flex-direction:row-reverse; }
.bt-av{ width:38px; height:38px; border-radius:50%; background:#bef264; border:2.5px solid #03222a; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.bt-av.u{ background:#7dd3fc; }
.bt-bub{ background:#fff; border:2.5px solid #03222a; border-radius:18px 18px 18px 4px; padding:13px 16px; font-size:13.5px; line-height:1.55; color:#03222a; max-width:78%; font-weight:500; box-shadow:4px 4px 0 #03222a; }
.bt-bub strong{ background:#bef264; padding:0 4px; border-radius:4px; }
.bt-row.u .bt-bub{ background:#03222a; color:#fffdf7; border-radius:18px 18px 4px 18px; box-shadow:-4px 4px 0 #bef264; }
.bt-row.u .bt-bub strong{ background:#bef264; color:#03222a; }
.bt-row.u .bt-av{ font-size:13px; font-weight:800; color:#03222a; }

.bt-source{ display:inline-flex; align-items:center; gap:6px; margin-top:9px; padding:5px 11px; background:#fffdf7; border:2px solid #03222a; border-radius:20px; font-size:11px; font-weight:700; color:#03222a; }
.bt-source .ic{ width:13px; height:13px; }

.bt-dept{ display:inline-flex; align-items:center; gap:5px; padding:4px 11px; background:#ff6b6b; color:#fff; border-radius:20px; font-size:10.5px; font-weight:800; letter-spacing:0.02em; border:2px solid #03222a; margin-bottom:6px; box-shadow:2px 2px 0 #03222a; }

.bt-typing{ display:flex; gap:5px; padding:6px 0; }
.bt-typing span{ width:9px; height:9px; border-radius:50%; background:#03222a; animation:btDot 1.2s infinite; }
.bt-typing span:nth-child(2){ animation-delay:0.15s; background:#bef264; }
.bt-typing span:nth-child(3){ animation-delay:0.3s; background:#ff6b6b; }
@keyframes btDot{ 0%,80%,100%{ transform:translateY(0); } 40%{ transform:translateY(-6px); } }

/* Greeting */
.bt-greet{ text-align:center; padding:4px 4px 14px; position:relative; z-index:2; }
.bt-greet .confetti{ position:absolute; pointer-events:none; }
.bt-greet .big-face{ width:120px; height:120px; margin:6px auto 14px; background:#bef264; border-radius:50%; border:3px solid #03222a; display:flex; align-items:center; justify-content:center; position:relative; box-shadow:0 8px 0 #03222a; }
.bt-greet .big-face .stick{ position:absolute; top:-12px; right:-14px; background:#ff6b6b; color:#fff; padding:6px 10px; border:2.5px solid #03222a; border-radius:14px; transform:rotate(12deg); font-size:11px; font-weight:800; box-shadow:3px 3px 0 #03222a; }
.bt-greet h2{ font-family:'Fraunces',serif; font-size:30px; font-weight:800; color:#03222a; line-height:1.05; letter-spacing:-0.03em; margin:0 0 6px; }
.bt-greet h2 .hl{ background:#bef264; padding:0 5px; display:inline-block; transform:rotate(-1deg); }
.bt-greet p{ font-size:13px; color:#1a2628; line-height:1.5; font-weight:500; margin:0; padding:0 8px; }

.bt-quick{ display:flex; flex-direction:column; gap:9px; margin-top:18px; }
.bt-quick .q{ background:#fff; border:2.5px solid #03222a; border-radius:14px; padding:12px 14px; display:flex; align-items:center; gap:11px; font-size:13.5px; font-weight:700; color:#03222a; box-shadow:3px 3px 0 #03222a; text-align:left; }
.bt-quick .q .ic{ width:36px; height:36px; border-radius:11px; display:flex; align-items:center; justify-content:center; font-size:18px; flex-shrink:0; border:2px solid #03222a; }
.bt-quick .q .arr{ margin-left:auto; }

/* Handover */
.bt-handover{ background:#fef3c7; border:3px solid #03222a; border-radius:18px; padding:14px; box-shadow:4px 4px 0 #03222a; margin-top:6px; }
.bt-handover .h{ display:flex; align-items:center; gap:9px; margin-bottom:11px; }
.bt-handover .h .ic{ width:38px; height:38px; border-radius:50%; background:#ff6b6b; border:2.5px solid #03222a; display:flex; align-items:center; justify-content:center; color:#fff; }
.bt-handover .h .ttl{ font-family:'Fraunces',serif; font-size:16px; font-weight:800; color:#03222a; letter-spacing:-0.01em; }
.bt-handover .h .sub{ font-size:11px; font-weight:700; color:#92400e; }
.bt-handover .dept-row{ background:#fff; border:2.5px solid #03222a; border-radius:12px; padding:9px 11px; display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.bt-handover .dept-row .icc{ width:32px; height:32px; border-radius:10px; background:#03222a; color:#bef264; display:flex; align-items:center; justify-content:center; font-size:14px; font-weight:800; }
.bt-handover .dept-row .nm{ font-size:13px; font-weight:800; color:#03222a; }
.bt-handover .dept-row .desc{ font-size:11px; color:#5a6c6d; font-weight:600; }
.bt-handover .hours{ font-size:11.5px; color:#03222a; font-weight:600; line-height:1.5; padding:8px 0; }
.bt-handover .hours strong{ background:#bef264; padding:0 4px; border-radius:3px; font-weight:800; }
.bt-handover .actions{ display:flex; gap:7px; margin-top:6px; }
.bt-handover .btn-p{ flex:1; background:#03222a; color:#fffdf7; padding:11px; border-radius:11px; text-align:center; font-size:12.5px; font-weight:800; box-shadow:0 4px 0 #001012; }
.bt-handover .btn-s{ background:#fff; color:#03222a; padding:11px 14px; border-radius:11px; font-size:12.5px; font-weight:800; border:2px solid #03222a; }

/* Modal */
.bt-overlay{ position:absolute; inset:0; background:rgba(3,34,42,0.55); display:flex; align-items:center; justify-content:center; padding:14px; }
.bt-modal{ background:#fffdf7; border:3px solid #03222a; border-radius:22px; width:100%; box-shadow:0 8px 0 #03222a, 0 20px 60px rgba(0,0,0,0.3); overflow:hidden; }
.bt-modal .head{ background:#bef264; padding:18px 18px 16px; border-bottom:3px solid #03222a; position:relative; }
.bt-modal .head .sticker{ position:absolute; right:14px; top:-10px; background:#ff6b6b; color:#fff; padding:5px 10px; border:2.5px solid #03222a; border-radius:14px; font-size:10.5px; font-weight:800; transform:rotate(6deg); box-shadow:2px 2px 0 #03222a; }
.bt-modal h3{ font-family:'Fraunces',serif; font-size:22px; font-weight:800; color:#03222a; letter-spacing:-0.02em; margin:0 0 5px; max-width:280px; line-height:1.05; }
.bt-modal .sb{ font-size:12.5px; color:#03222a; font-weight:600; line-height:1.45; }
.bt-modal .body{ padding:18px; }
.bt-modal .field{ margin-bottom:12px; }
.bt-modal .field label{ display:block; font-size:11.5px; font-weight:800; color:#03222a; margin-bottom:6px; }
.bt-modal .field .inp{ width:100%; padding:13px 14px; border:2.5px solid #03222a; border-radius:14px; font-size:13.5px; color:#03222a; background:#fff; font-weight:600; }
.bt-modal .field .inp.placeholder{ color:#7a8588; font-weight:500; }
.bt-modal .field .inp.active{ background:#fef3c7; }
.bt-modal .field-row{ display:flex; gap:9px; }
.bt-modal .field-row .field{ flex:1; }
.bt-modal .picks{ display:flex; flex-wrap:wrap; gap:7px; }
.bt-modal .pick{ padding:9px 13px; border:2.5px solid #03222a; border-radius:14px; font-size:12px; font-weight:700; color:#03222a; background:#fff; box-shadow:2px 2px 0 #03222a; display:flex; align-items:center; gap:5px; }
.bt-modal .pick.on{ background:#bef264; }
.bt-modal .submit{ width:100%; padding:14px; background:#03222a; color:#fffdf7; border-radius:14px; font-size:14px; font-weight:800; display:flex; align-items:center; justify-content:center; gap:7px; box-shadow:0 5px 0 #001012; margin-top:4px; }
.bt-modal .ftr{ text-align:center; margin-top:10px; font-size:11px; color:#5a6c6d; font-weight:600; }

/* Settings */
.bt-settings .lang-grid{ display:grid; grid-template-columns:1fr 1fr; gap:9px; margin-bottom:14px; }
.bt-settings .lc{ padding:14px; border:2.5px solid #03222a; border-radius:14px; background:#fff; box-shadow:3px 3px 0 #03222a; position:relative; }
.bt-settings .lc.on{ background:#bef264; }
.bt-settings .lc .fg{ font-size:30px; margin-bottom:6px; }
.bt-settings .lc .nm{ font-family:'Fraunces',serif; font-size:16px; font-weight:800; color:#03222a; letter-spacing:-0.01em; }
.bt-settings .lc .sb{ font-size:11px; color:#03222a; font-weight:600; opacity:0.7; }
.bt-settings .lc .ck{ position:absolute; top:9px; right:9px; width:24px; height:24px; border-radius:50%; background:#03222a; color:#bef264; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:800; border:2px solid #03222a; }
.bt-settings h4{ font-family:'Fraunces',serif; font-size:14px; font-weight:800; color:#03222a; margin:12px 0 9px; letter-spacing:-0.01em; }
.bt-settings .opt{ background:#fff; border:2.5px solid #03222a; border-radius:13px; padding:12px 13px; display:flex; align-items:center; gap:11px; margin-bottom:7px; box-shadow:2px 2px 0 #03222a; }
.bt-settings .opt .ic{ width:36px; height:36px; border-radius:11px; background:#fef3c7; border:2px solid #03222a; display:flex; align-items:center; justify-content:center; font-size:15px; flex-shrink:0; }
.bt-settings .opt .lb{ flex:1; font-size:13px; font-weight:800; color:#03222a; }
.bt-settings .opt .sb{ font-size:11px; color:#5a6c6d; font-weight:600; margin-top:1px; }
.bt-settings .opt.colored .ic{ background:#bef264; }
.bt-settings .sw{ width:42px; height:24px; background:#03222a; border-radius:20px; position:relative; flex-shrink:0; }
.bt-settings .sw::after{ content:''; position:absolute; right:3px; top:3px; width:16px; height:16px; border-radius:50%; background:#bef264; }
.bt-settings .sw.off{ background:#cbd5e1; }
.bt-settings .sw.off::after{ left:3px; right:auto; background:#fff; }
`;

/* Mascot — same Pip style but bolder colors for this variant */
function BTFace({ size=44, color='#03222a' }){
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{display:'block'}}>
      <path d="M22 30 L26 12 L36 30 Z" fill={color}/>
      <path d="M78 30 L74 12 L64 30 Z" fill={color}/>
      <circle cx="50" cy="55" r="38" fill={color}/>
      <circle cx="38" cy="50" r="11" fill="#fffdf7"/>
      <circle cx="62" cy="50" r="11" fill="#fffdf7"/>
      <circle cx="40" cy="52" r="5" fill={color}/>
      <circle cx="64" cy="52" r="5" fill={color}/>
      <circle cx="41.5" cy="50" r="2" fill="#fff"/>
      <circle cx="65.5" cy="50" r="2" fill="#fff"/>
      <path d="M50 61 L45 72 Q50 76 55 72 Z" fill="#ff6b6b"/>
      <ellipse cx="28" cy="65" rx="6" ry="4" fill="#ff6b6b" opacity="0.5"/>
      <ellipse cx="72" cy="65" rx="6" ry="4" fill="#ff6b6b" opacity="0.5"/>
    </svg>
  );
}

function BigTalkScreen({ screen }){
  React.useEffect(()=>{
    if(document.getElementById('bt-css')) return;
    const s = document.createElement('style'); s.id='bt-css'; s.textContent=bigtalkCss; document.head.appendChild(s);
  },[]);

  if(screen === 'launcher') return <BTLauncher/>;
  return (
    <div className="bt-root">
      <div className="bt-shell">
        <BTTopbar/>
        <div className="bt-trust">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="#03222a" stroke="#03222a" strokeWidth="0"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          <span>100% ალტეს ოფიც. წყაროები</span>
          <span style={{marginLeft:'auto',background:'#03222a',color:'#bef264',padding:'2px 8px',borderRadius:20,fontSize:9.5,fontWeight:800}}>✓ Verified</span>
        </div>
        {screen==='greeting' && <BTGreeting/>}
        {screen==='chat' && <BTChat/>}
        {screen==='handover' && <BTHandover/>}
        {screen==='file' && <BTFile/>}
        {screen==='lead' && <BTLead/>}
        {screen==='settings' && <BTSettings/>}
        <BTComposer placeholder={screen==='greeting'}/>
      </div>
    </div>
  );
}

function BTTopbar(){
  return (
    <div className="bt-topbar">
      <div className="face-circle"><BTFace size={32}/></div>
      <div>
        <div className="nm">პიპი</div>
        <div className="stt">⚡ აქტიური · გელოდები</div>
      </div>
      <div className="acts">
        <div className="lang"><span className="on">KA</span><span>EN</span></div>
        <div className="ic">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </div>
      </div>
    </div>
  );
}

function BTComposer({ placeholder }){
  return (
    <div className="bt-composer">
      <div className={"inp " + (placeholder?'placeholder':'')}>{placeholder ? 'რა გჭირდება? დაწერე...' : 'მინდა MD-ზე ინფო'}</div>
      <div className="send">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
      </div>
    </div>
  );
}

function BTLauncher(){
  return (
    <div className="bt-root">
      <div className="bt-page">
        <div className="nav">
          <div className="nav-logo">alte<span className="dot">.</span>edu.ge</div>
          <div className="nav-items">
            <span>მიღება</span>
            <span>პროგრამები</span>
            <span>დაფინანსება</span>
          </div>
          <div className="nav-r"><div className="btn">აპლიკაცია →</div></div>
        </div>
        <div className="hero">
          <h1>გახდი ის,<br/>ვინც <span className="hl">გინდა</span>.</h1>
          <p>2,500+ სტუდენტი. 45 ქვეყანა. ერთი მიზანი — <strong>შენი მომავალი</strong>.</p>
          <div className="btn">პროგრამის არჩევა →</div>
        </div>

        <div className="bt-launcher">
          <div className="speech">გამარჯობა! 👋 აქ ვარ, შემეკითხე!</div>
          <div className="big-btn">
            <div className="ring"></div>
            <div className="badge">⚡ AI</div>
            <div className="face"><BTFace size={78}/></div>
          </div>
        </div>
      </div>
    </div>
  );
}

function BTGreeting(){
  return (
    <div className="bt-msgs">
      <div className="bt-greet">
        <svg className="confetti" style={{top:0,left:20,width:30}} viewBox="0 0 30 30"><rect x="2" y="2" width="6" height="6" fill="#ff6b6b" transform="rotate(20 5 5)"/><circle cx="20" cy="8" r="3" fill="#fbbf24"/><rect x="20" y="20" width="5" height="5" fill="#7dd3fc" transform="rotate(40 22 22)"/></svg>
        <svg className="confetti" style={{top:6,right:18,width:30}} viewBox="0 0 30 30"><circle cx="6" cy="6" r="3" fill="#bef264"/><rect x="18" y="14" width="6" height="6" fill="#ff6b6b" transform="rotate(-20 21 17)"/></svg>
        <div className="big-face">
          <div className="stick">⚡ AI</div>
          <BTFace size={88}/>
        </div>
        <h2>გამარჯობა!<br/><span className="hl">პიპი</span> ვარ</h2>
        <p>ალტეს AI ასისტენტი. დამისვი ნებისმიერი კითხვა — დეპარტამენტს თვითონ ვიპოვი 🎯</p>
      </div>
      <div className="bt-quick">
        <div className="q">
          <div className="ic" style={{background:'#bef264'}}>🎓</div>
          როგორ ჩავაბარო ალტეში?
          <div className="arr"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#03222a" strokeWidth="2.6" strokeLinecap="round"><polyline points="9 18 15 12 9 6"/></svg></div>
        </div>
        <div className="q">
          <div className="ic" style={{background:'#fbbf24'}}>💰</div>
          რა ღირს სწავლა?
          <div className="arr"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#03222a" strokeWidth="2.6" strokeLinecap="round"><polyline points="9 18 15 12 9 6"/></svg></div>
        </div>
        <div className="q">
          <div className="ic" style={{background:'#ff6b6b'}}>🩺</div>
          MD პროგრამის შესახებ
          <div className="arr"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#03222a" strokeWidth="2.6" strokeLinecap="round"><polyline points="9 18 15 12 9 6"/></svg></div>
        </div>
        <div className="q">
          <div className="ic" style={{background:'#7dd3fc'}}>🌍</div>
          საერთ. სტუდენტებისთვის
          <div className="arr"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#03222a" strokeWidth="2.6" strokeLinecap="round"><polyline points="9 18 15 12 9 6"/></svg></div>
        </div>
      </div>
    </div>
  );
}

function BTChat(){
  return (
    <div className="bt-msgs">
      <div className="bt-row u">
        <div className="bt-av u">თქ</div>
        <div className="bt-bub">გამარჯობა! მინდა MD პროგრამის შესახებ ვისწავლო</div>
      </div>
      <div className="bt-row">
        <div className="bt-av"><BTFace size={28}/></div>
        <div>
          <div className="bt-dept">🩺 მედიცინა · MD</div>
          <div className="bt-bub">
            გასაოცარი არჩევანი! 🎉 <strong>MD პროგრამა</strong> — 6-წლიანი, ინგლისურენოვანი, WHO აღიარებული.
            <br/><br/>
            წლიური საფასური: <strong>$5,500</strong>. სტუდენტი ხდები 45+ ქვეყნიდან მოსული თანატოლების გვერდით.
            <div className="bt-source">
              <svg className="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
              alte.edu.ge/ka/...sameditsino-programebi-2
            </div>
          </div>
        </div>
      </div>
      <div className="bt-row u">
        <div className="bt-av u">თქ</div>
        <div className="bt-bub">და ჩარიცხვის ვადა?</div>
      </div>
      <div className="bt-row">
        <div className="bt-av"><BTFace size={28}/></div>
        <div className="bt-bub" style={{paddingRight:16}}>
          <div className="bt-typing"><span></span><span></span><span></span></div>
        </div>
      </div>
    </div>
  );
}

function BTHandover(){
  return (
    <div className="bt-msgs">
      <div className="bt-row u">
        <div className="bt-av u">თქ</div>
        <div className="bt-bub">ცოცხალ ოპერატორთან გადამამისამართე</div>
      </div>
      <div className="bt-row">
        <div className="bt-av"><BTFace size={28}/></div>
        <div style={{maxWidth:'90%'}}>
          <div className="bt-bub">ნამდვილად 👍 ვაკავშირებ ცოცხალ ოპერატორთან!</div>
          <div className="bt-handover">
            <div className="h">
              <div className="ic">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1v-6h3z"/><path d="M3 19a2 2 0 0 0 2 2h1v-6H3z"/></svg>
              </div>
              <div>
                <div className="ttl">ცოცხალი ოპერატორი</div>
                <div className="sub">⚡ ჩაერთო რიგზე</div>
              </div>
            </div>
            <div className="dept-row">
              <div className="icc">🎓</div>
              <div style={{flex:1}}>
                <div className="nm">მიღების ოფისი</div>
                <div className="desc">Admissions · საქართველო</div>
              </div>
            </div>
            <div className="hours">⏰ <strong>ორშ–პარ 09:00–18:00</strong> · საშ. რეაქცია 3 სთ-ში</div>
            <div className="actions">
              <div className="btn-p">დატოვე კონტაქტი</div>
              <div className="btn-s">↩</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function BTLead(){
  return (
    <>
      <div className="bt-msgs" style={{filter:'blur(2px)',pointerEvents:'none'}}>
        <div className="bt-row">
          <div className="bt-av"><BTFace size={28}/></div>
          <div className="bt-bub">სუპერ! ერთი წუთი, კონტაქტი დატოვე...</div>
        </div>
      </div>
      <div className="bt-overlay">
        <div className="bt-modal">
          <div className="head">
            <div className="sticker">⚡ 24 საათში</div>
            <h3>დატოვე<br/>კონტაქტი 👋</h3>
            <div className="sb">მიღების გუნდი დაგიკავშირდება და ყველაფერი დაგეგმავთ ერთად.</div>
          </div>
          <div className="body">
            <div className="field">
              <label>როგორ გქვია?</label>
              <div className="inp">ნინო კვარაცხელია</div>
            </div>
            <div className="field-row">
              <div className="field" style={{flex:1.6}}>
                <label>ტელეფონი</label>
                <div className="inp active">+995 599 12 34 56</div>
              </div>
              <div className="field">
                <label>ენა</label>
                <div className="inp">🇬🇪 KA</div>
              </div>
            </div>
            <div className="field">
              <label>რა გაინტერესებს ყველაზე?</label>
              <div className="picks">
                <div className="pick">🎓 ბაკალავრი</div>
                <div className="pick on">🩺 MD</div>
                <div className="pick">💰 დაფინ.</div>
                <div className="pick">🌍 საერთ.</div>
              </div>
            </div>
            <div className="submit">
              გავაგზავნოთ!
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </div>
            <div className="ftr">ვეთანხმები <span style={{color:'#03222a',fontWeight:800,textDecoration:'underline'}}>კონფიდენციალურობას</span>.</div>
          </div>
        </div>
      </div>
    </>
  );
}

function BTSettings(){
  return (
    <>
      <div className="bt-msgs" style={{filter:'blur(2px)',pointerEvents:'none'}}>
        <div className="bt-row">
          <div className="bt-av"><BTFace size={28}/></div>
          <div className="bt-bub">გამარჯობა! რით დაგეხმარო? 🚀</div>
        </div>
      </div>
      <div className="bt-overlay">
        <div className="bt-modal bt-settings">
          <div className="head" style={{paddingBottom:14}}>
            <h3>პარამეტრები ⚙️</h3>
            <div className="sb">აირჩიე, როგორ მინდა ვისაუბრო შენთან</div>
          </div>
          <div className="body">
            <h4>ენა · Language</h4>
            <div className="lang-grid">
              <div className="lc on">
                <div className="ck">✓</div>
                <div className="fg">🇬🇪</div>
                <div className="nm">ქართული</div>
                <div className="sb">Georgian</div>
              </div>
              <div className="lc">
                <div className="fg">🇬🇧</div>
                <div className="nm">English</div>
                <div className="sb">International</div>
              </div>
            </div>

            <h4>გამოცდილება</h4>
            <div className="opt colored">
              <div className="ic">🎉</div>
              <div style={{flex:1}}>
                <div className="lb">პიპის ანიმაციები</div>
                <div className="sb">საუბრის დროს რეაგირებს</div>
              </div>
              <div className="sw"></div>
            </div>
            <div className="opt">
              <div className="ic">🔗</div>
              <div style={{flex:1}}>
                <div className="lb">წყაროების ბმულები</div>
                <div className="sb">alte.edu.ge ბმული ყოველ პასუხთან</div>
              </div>
              <div className="sw"></div>
            </div>
            <div className="opt">
              <div className="ic">🔔</div>
              <div style={{flex:1}}>
                <div className="lb">დაბრუნების შეტყობინება</div>
                <div className="sb">თუ ოპერატორი დაგიკავშირდება</div>
              </div>
              <div className="sw off"></div>
            </div>

            <div style={{textAlign:'center',marginTop:14,fontSize:11,color:'#5a6c6d',fontWeight:600}}>
              v2.0 · ⚡ Claude AI · ისტორიის წაშლა
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function BTFile(){
  return (
    <div className="bt-msgs">
      <div className="bt-row u">
        <div className="bt-av u">თქ</div>
        <div style={{maxWidth:'82%'}}>
          <div style={{background:'#03222a',border:'2.5px solid #03222a',borderRadius:'18px 18px 4px 18px',padding:9,marginBottom:7,boxShadow:'-4px 4px 0 #bef264'}}>
            <div style={{background:'#fffdf7',border:'2px solid #fffdf7',borderRadius:11,padding:'9px 11px',display:'flex',gap:10,alignItems:'center'}}>
              <div style={{width:40,height:48,background:'#ff6b6b',border:'2.5px solid #03222a',borderRadius:7,display:'flex',alignItems:'center',justifyContent:'center',color:'#fff',fontSize:9,fontWeight:800,flexShrink:0,transform:'rotate(-4deg)'}}>PDF</div>
              <div style={{flex:1,minWidth:0}}>
                <div style={{fontSize:12.5,fontWeight:800,color:'#03222a',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>my_transcript.pdf</div>
                <div style={{fontSize:11,color:'#5a6c6d',fontWeight:600}}>892 KB · ✓ ატვირთული</div>
              </div>
            </div>
          </div>
          <div className="bt-bub" style={{background:'#03222a',color:'#fffdf7',boxShadow:'-4px 4px 0 #bef264',borderRadius:'18px 18px 4px 18px'}}>ეს ჩემი გიმნაზიის ატესტატია! 📄</div>
        </div>
      </div>

      <div className="bt-row">
        <div className="bt-av"><BTFace size={28}/></div>
        <div>
          <div className="bt-dept">🎓 მიღება</div>
          <div className="bt-bub">
            წაკითხე! 🎉 GPA <strong>3.7</strong> — სუპერ შედეგებია.
            <br/><br/>
            ატესტატით <strong>5 პროგრამაზე</strong> გაქვს წვდომა — MD-ში ცია! წინ წავიდეთ?
            <div className="bt-source">
              <svg className="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
              alte.edu.ge/ka/migebis-pirobebi
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { BigTalkScreen });
