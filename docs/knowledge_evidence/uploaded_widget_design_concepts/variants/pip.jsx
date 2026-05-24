// VARIANT 1 — "Pip" — friendly owl-like mascot, warm cream palette, illustrative
// Color: alte teal + cream/coral/honey/mint
// Personality: gentle, student-friendly, soft-rounded, hand-feeling

const pipCss = `
.pip-root { width:100%; height:100%; font-family:'Noto Sans Georgian','Inter',sans-serif; color:#1a2628; --teal:#074045; --teal-2:#0a5258; --teal-3:#16766f; --cream:#fff8ee; --paper:#fff3e0; --coral:#ff8a65; --honey:#ffc857; --mint:#7dd3c0; --pink:#f7b6d2; --ink:#1a2628; --ink-2:#5a6c6d; --line:rgba(7,64,69,0.10); }
.pip-root *{ box-sizing:border-box; }

/* ---- Website backdrop for launcher screen ---- */
.pip-page{ width:100%; height:100%; background:#f3eee5; position:relative; overflow:hidden; }
.pip-page .nav{ height:62px; background:#fff; border-bottom:1px solid #e8e2d4; display:flex; align-items:center; padding:0 22px; gap:22px; font-size:12px; color:#3a4548; }
.pip-page .nav-logo{ font-family:'Fraunces',serif; font-weight:800; font-size:18px; color:#074045; letter-spacing:-0.01em; }
.pip-page .nav-logo .dot{ color:#ff8a65; }
.pip-page .nav-items{ display:flex; gap:18px; margin-left:14px; }
.pip-page .nav-items span{ cursor:default; }
.pip-page .nav-right{ margin-left:auto; display:flex; gap:10px; align-items:center; color:#7a8588; font-size:11px; }
.pip-page .nav-right .lang{ padding:4px 9px; border-radius:6px; border:1px solid #e0d9c8; }
.pip-page .hero{ padding:38px 32px 0; }
.pip-page .hero h1{ font-family:'Fraunces',serif; font-size:34px; line-height:1.1; color:#1a2628; font-weight:700; max-width:340px; margin:0 0 14px; letter-spacing:-0.02em; }
.pip-page .hero h1 em{ color:#074045; font-style:normal; font-weight:800; }
.pip-page .hero p{ font-size:13px; color:#4a5558; max-width:330px; line-height:1.6; margin:0 0 22px; }
.pip-page .hero .ctas{ display:flex; gap:8px; }
.pip-page .hero .cta-p{ background:#074045; color:#fff; padding:11px 18px; border-radius:8px; font-size:12px; font-weight:600; }
.pip-page .hero .cta-s{ background:#fff; color:#074045; padding:11px 18px; border-radius:8px; font-size:12px; font-weight:600; border:1px solid #074045; }
.pip-page .stats{ position:absolute; bottom:32px; left:32px; right:32px; display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
.pip-page .stat{ background:#fff; border-radius:12px; padding:14px; border:1px solid #e8e2d4; }
.pip-page .stat .n{ font-family:'Fraunces',serif; font-size:24px; font-weight:700; color:#074045; }
.pip-page .stat .l{ font-size:10px; color:#7a8588; margin-top:2px; }

/* ---- Launcher bubble ---- */
.pip-launcher{ position:absolute; right:24px; bottom:24px; display:flex; flex-direction:column; align-items:flex-end; gap:10px; }
.pip-launcher .hello-bubble{ background:#fff; border-radius:18px 18px 4px 18px; padding:10px 14px; box-shadow:0 8px 24px rgba(7,64,69,0.18), 0 2px 6px rgba(7,64,69,0.08); font-size:12.5px; color:#1a2628; max-width:220px; line-height:1.45; border:1px solid #f0e6d2; position:relative; animation:pipPop .5s ease both; }
.pip-launcher .hello-bubble strong{ color:#074045; }
.pip-launcher .hello-bubble .close{ position:absolute; top:-6px; right:-6px; width:18px; height:18px; border-radius:50%; background:#fff; border:1px solid #e8e2d4; display:flex; align-items:center; justify-content:center; font-size:10px; color:#7a8588; }
.pip-launcher .pip-btn{ width:72px; height:72px; border-radius:50%; background:linear-gradient(160deg, #0a5258 0%, #074045 60%, #052e32 100%); display:flex; align-items:center; justify-content:center; box-shadow:0 12px 28px rgba(7,64,69,0.35), 0 4px 8px rgba(7,64,69,0.15); position:relative; cursor:pointer; }
.pip-launcher .pip-btn::after{ content:''; position:absolute; bottom:4px; right:4px; width:14px; height:14px; border-radius:50%; background:#7dd3c0; border:2px solid #fff; }
.pip-launcher .pip-btn .pip-svg{ animation:pipBob 3s ease-in-out infinite; }
@keyframes pipBob{ 0%,100%{ transform:translateY(0) rotate(-2deg);} 50%{ transform:translateY(-3px) rotate(2deg);} }
@keyframes pipPop{ from{ transform:translateY(8px) scale(.9); opacity:0;} to{ transform:translateY(0) scale(1); opacity:1;} }

/* ---- Widget shell (open states) ---- */
.pip-shell{ width:100%; height:100%; background:var(--cream); display:flex; flex-direction:column; overflow:hidden; position:relative; }
.pip-shell .topbar{ background:#fff; padding:14px 16px; display:flex; align-items:center; gap:11px; border-bottom:1px solid #f0e6d2; flex-shrink:0; }
.pip-shell .topbar .av{ width:42px; height:42px; border-radius:50%; background:linear-gradient(160deg,#0a5258,#074045); display:flex; align-items:center; justify-content:center; flex-shrink:0; box-shadow:0 4px 10px rgba(7,64,69,0.25); position:relative; }
.pip-shell .topbar .av::after{ content:''; position:absolute; bottom:0; right:0; width:11px; height:11px; border-radius:50%; background:#7dd3c0; border:2px solid #fff; }
.pip-shell .topbar .name{ font-family:'Fraunces',serif; font-size:15px; font-weight:700; color:#1a2628; letter-spacing:-0.01em; }
.pip-shell .topbar .status{ font-size:10.5px; color:#16766f; margin-top:1px; display:flex; align-items:center; gap:4px; font-weight:500; }
.pip-shell .topbar .status::before{ content:''; width:6px; height:6px; border-radius:50%; background:#1ca672; display:inline-block; }
.pip-shell .topbar .acts{ margin-left:auto; display:flex; gap:6px; }
.pip-shell .topbar .ic{ width:30px; height:30px; border-radius:9px; background:var(--cream); display:flex; align-items:center; justify-content:center; color:#5a6c6d; font-size:14px; border:1px solid transparent; cursor:pointer; }
.pip-shell .topbar .ic:hover{ background:#f0e6d2; }
.pip-shell .topbar .lang-pill{ background:var(--cream); border-radius:9px; padding:0; height:30px; display:flex; align-items:center; font-size:11px; font-weight:600; overflow:hidden; }
.pip-shell .topbar .lang-pill span{ padding:0 10px; height:100%; display:flex; align-items:center; color:#7a8588; }
.pip-shell .topbar .lang-pill span.on{ background:#074045; color:#fff; }

.pip-shell .trust{ padding:7px 16px; background:#fff8ee; font-size:10.5px; color:#16766f; display:flex; align-items:center; gap:6px; border-bottom:1px solid #f0e6d2; }
.pip-shell .trust i, .pip-shell .trust .ic-shield{ color:#16766f; }

.pip-shell .msgs{ flex:1; overflow-y:auto; padding:18px 16px; display:flex; flex-direction:column; gap:14px; background:linear-gradient(180deg, #fffaf0 0%, #fff8ee 100%); }
.pip-shell .composer{ background:#fff; padding:10px 12px; display:flex; gap:8px; border-top:1px solid #f0e6d2; flex-shrink:0; align-items:center; }
.pip-shell .composer .inp{ flex:1; background:var(--cream); border-radius:12px; padding:10px 14px; font-size:12.5px; color:#1a2628; border:1px solid #f0e6d2; }
.pip-shell .composer .inp.placeholder{ color:#9aa5a8; }
.pip-shell .composer .send{ width:40px; height:40px; border-radius:12px; background:#074045; color:#fff; display:flex; align-items:center; justify-content:center; flex-shrink:0; font-size:16px; box-shadow:0 4px 10px rgba(7,64,69,0.25); }
.pip-shell .composer .attach{ width:36px; height:36px; border-radius:10px; background:var(--cream); color:#5a6c6d; display:flex; align-items:center; justify-content:center; font-size:14px; }

/* messages */
.pip-row{ display:flex; gap:8px; align-items:flex-end; }
.pip-row.u{ flex-direction:row-reverse; }
.pip-mini{ width:28px; height:28px; border-radius:50%; background:linear-gradient(160deg,#0a5258,#074045); flex-shrink:0; display:flex; align-items:center; justify-content:center; }
.pip-mini.u{ background:#f0e6d2; color:#5a6c6d; font-size:11px; font-weight:600; }
.pip-bub{ background:#fff; border-radius:18px 18px 18px 4px; padding:11px 14px; font-size:13px; line-height:1.55; color:#1a2628; max-width:78%; border:1px solid #f0e6d2; box-shadow:0 1px 3px rgba(7,64,69,0.04); }
.pip-bub strong{ color:#074045; }
.pip-row.u .pip-bub{ background:#074045; color:#fff; border-radius:18px 18px 4px 18px; border-color:#074045; }
.pip-row.u .pip-bub strong{ color:#ffc857; }

.pip-source{ margin-top:6px; display:inline-flex; align-items:center; gap:5px; padding:5px 10px; background:#e8f4f2; border-radius:20px; font-size:10.5px; color:#0a5258; font-weight:500; }
.pip-source .ic-link{ width:11px; height:11px; }

.pip-dept-chip{ display:inline-flex; align-items:center; gap:5px; padding:3px 9px; background:#fff3e0; color:#c2410c; border-radius:20px; font-size:10px; font-weight:600; margin-bottom:5px; letter-spacing:0.01em; }

/* greeting state hero */
.pip-greet{ text-align:center; padding:8px 4px 18px; }
.pip-greet .big-pip{ width:90px; height:90px; margin:6px auto 14px; background:linear-gradient(160deg,#0a5258,#074045); border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 14px 30px rgba(7,64,69,0.25); position:relative; }
.pip-greet .big-pip::before{ content:''; position:absolute; width:24px; height:24px; border-radius:50%; background:#ffc857; right:-4px; top:6px; opacity:0.3; }
.pip-greet .big-pip::after{ content:''; position:absolute; width:18px; height:18px; border-radius:50%; background:#7dd3c0; left:-2px; bottom:8px; opacity:0.4; }
.pip-greet h2{ font-family:'Fraunces',serif; font-size:22px; font-weight:700; color:#1a2628; margin:0 0 4px; letter-spacing:-0.01em; }
.pip-greet h2 .wave{ display:inline-block; transform-origin:70% 70%; animation:wave 2s ease-in-out infinite; }
@keyframes wave{ 0%,60%,100%{ transform:rotate(0);} 10%,30%{ transform:rotate(14deg);} 20%{ transform:rotate(-8deg);} }
.pip-greet p{ font-size:12.5px; color:#4a5558; line-height:1.55; margin:0 auto; max-width:280px; }
.pip-greet p strong{ color:#074045; }

.pip-quick{ display:flex; flex-direction:column; gap:8px; margin-top:18px; }
.pip-quick .row{ display:flex; gap:8px; }
.pip-quick .chip{ flex:1; padding:11px 12px; background:#fff; border-radius:14px; border:1px solid #f0e6d2; display:flex; align-items:center; gap:9px; font-size:12px; color:#1a2628; font-weight:500; text-align:left; line-height:1.3; }
.pip-quick .chip .icb{ width:30px; height:30px; border-radius:9px; display:flex; align-items:center; justify-content:center; flex-shrink:0; font-size:14px; }

/* handover card */
.pip-handover{ margin-top:8px; background:#fff8ee; border:1.5px solid #ffc857; border-radius:18px; padding:14px; }
.pip-handover .h{ display:flex; align-items:center; gap:8px; font-size:12px; font-weight:700; color:#c2410c; margin-bottom:8px; }
.pip-handover .h .ico{ width:28px; height:28px; border-radius:10px; background:#ffc857; display:flex; align-items:center; justify-content:center; color:#7a3a00; font-size:14px; }
.pip-handover .dept{ display:inline-flex; align-items:center; gap:5px; padding:5px 12px; background:#fff; border-radius:20px; font-size:11px; font-weight:600; color:#074045; border:1px solid #f0e6d2; margin-bottom:8px; }
.pip-handover .note{ font-size:11.5px; color:#4a5558; line-height:1.5; }
.pip-handover .actions{ display:flex; gap:6px; margin-top:11px; }
.pip-handover .actions .btn-p{ background:#074045; color:#fff; padding:8px 14px; border-radius:10px; font-size:11.5px; font-weight:600; }
.pip-handover .actions .btn-s{ background:#fff; color:#074045; padding:8px 14px; border-radius:10px; font-size:11.5px; font-weight:600; border:1px solid #074045; }

/* typing dots */
.pip-dots{ display:flex; gap:4px; align-items:center; padding:4px 0; }
.pip-dots span{ width:7px; height:7px; border-radius:50%; background:#16766f; opacity:0.4; animation:pipBlink 1.4s infinite ease-in-out both; }
.pip-dots span:nth-child(2){ animation-delay:0.2s; }
.pip-dots span:nth-child(3){ animation-delay:0.4s; }
@keyframes pipBlink{ 0%,80%,100%{ opacity:0.25; transform:scale(0.9);} 40%{ opacity:1; transform:scale(1.1);} }

/* modal overlays (lead, settings) */
.pip-modal-bg{ position:absolute; inset:0; background:rgba(7,64,69,0.45); backdrop-filter:blur(2px); display:flex; align-items:flex-end; justify-content:center; padding:14px; }
.pip-modal{ background:#fff; border-radius:22px; width:100%; padding:20px 18px 18px; box-shadow:0 -12px 30px rgba(0,0,0,0.15); }
.pip-modal .grip{ width:34px; height:4px; background:#e0d9c8; border-radius:2px; margin:0 auto 14px; }
.pip-modal h3{ font-family:'Fraunces',serif; font-size:19px; font-weight:700; color:#1a2628; margin:0 0 4px; letter-spacing:-0.01em; }
.pip-modal h3 .em{ color:#074045; }
.pip-modal .sub{ font-size:12px; color:#4a5558; line-height:1.5; margin-bottom:14px; }
.pip-form{ display:flex; flex-direction:column; gap:10px; }
.pip-form .field label{ font-size:10.5px; font-weight:600; color:#5a6c6d; text-transform:uppercase; letter-spacing:0.05em; }
.pip-form .field .inp{ background:var(--cream); border:1px solid #f0e6d2; border-radius:12px; padding:11px 13px; font-size:13px; color:#1a2628; margin-top:5px; }
.pip-form .field .inp.placeholder{ color:#9aa5a8; }
.pip-form .field .inp.active{ border-color:#074045; }
.pip-form .field .inp.active::after{ content:'|'; color:#074045; animation:cursorBlink 1s infinite; }
@keyframes cursorBlink{ 50%{ opacity:0;} }
.pip-form .row{ display:flex; gap:8px; }
.pip-form .row .field{ flex:1; }
.pip-form .submit{ background:#074045; color:#fff; padding:13px; border-radius:12px; font-size:13px; font-weight:600; text-align:center; margin-top:6px; box-shadow:0 4px 10px rgba(7,64,69,0.2); display:flex; align-items:center; justify-content:center; gap:6px; }
.pip-form .later{ text-align:center; font-size:11.5px; color:#7a8588; font-weight:500; padding:8px; }
.pip-form .consent{ font-size:10.5px; color:#7a8588; line-height:1.45; display:flex; gap:6px; align-items:flex-start; padding:0 2px; }
.pip-form .consent .cbox{ width:14px; height:14px; border-radius:4px; background:#074045; flex-shrink:0; margin-top:1px; display:flex; align-items:center; justify-content:center; color:#fff; font-size:9px; }
.pip-form .consent a{ color:#074045; font-weight:600; }

.pip-settings .item{ display:flex; align-items:center; gap:12px; padding:13px; border-radius:14px; background:var(--cream); margin-bottom:8px; cursor:pointer; }
.pip-settings .item.on{ background:#074045; color:#fff; }
.pip-settings .item .flag{ width:38px; height:28px; border-radius:6px; overflow:hidden; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:18px; }
.pip-settings .item .nm{ font-size:14px; font-weight:600; }
.pip-settings .item .sb{ font-size:11px; opacity:0.7; margin-top:1px; }
.pip-settings .item .check{ margin-left:auto; width:22px; height:22px; border-radius:50%; background:#fff; color:#074045; display:flex; align-items:center; justify-content:center; font-size:12px; }
.pip-settings .item .check.off{ background:rgba(0,0,0,0.05); color:transparent; }
.pip-settings h4{ font-size:11px; font-weight:700; color:#5a6c6d; text-transform:uppercase; letter-spacing:0.05em; margin:14px 0 8px; }
.pip-settings .toggle-row{ display:flex; align-items:center; padding:11px 13px; background:var(--cream); border-radius:12px; margin-bottom:6px; }
.pip-settings .toggle-row .lb{ flex:1; font-size:12.5px; color:#1a2628; font-weight:500; }
.pip-settings .toggle-row .sb{ font-size:11px; color:#7a8588; }
.pip-settings .sw{ width:36px; height:20px; background:#074045; border-radius:20px; position:relative; }
.pip-settings .sw::after{ content:''; position:absolute; right:2px; top:2px; width:16px; height:16px; border-radius:50%; background:#fff; }
.pip-settings .sw.off{ background:#d8d2c2; }
.pip-settings .sw.off::after{ left:2px; right:auto; }
`;

/* Pip mascot SVG component */
function PipFace({ size=44, blink=false }){
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" className="pip-svg" style={{display:'block'}}>
      {/* tufts */}
      <path d="M22 30 L26 12 L36 30 Z" fill="#16766f"/>
      <path d="M78 30 L74 12 L64 30 Z" fill="#16766f"/>
      {/* face */}
      <circle cx="50" cy="55" r="38" fill="#0a5258"/>
      <circle cx="50" cy="55" r="38" fill="url(#pipGrad)" opacity="0.4"/>
      {/* eye whites */}
      <circle cx="38" cy="50" r="10" fill="#fff8ee"/>
      <circle cx="62" cy="50" r="10" fill="#fff8ee"/>
      {/* pupils */}
      <ellipse cx="39" cy="52" rx="4.2" ry={blink? 0.4 : 4.6} fill="#1a2628"/>
      <ellipse cx="63" cy="52" rx="4.2" ry={blink? 0.4 : 4.6} fill="#1a2628"/>
      {/* sparkle */}
      <circle cx="40.5" cy="49.5" r="1.5" fill="#fff"/>
      <circle cx="64.5" cy="49.5" r="1.5" fill="#fff"/>
      {/* beak */}
      <path d="M50 60 L46 71 Q50 75 54 71 Z" fill="#ff8a65"/>
      <path d="M50 60 L48 67 L52 67 Z" fill="#e96e4a"/>
      {/* cheeks */}
      <ellipse cx="29" cy="64" rx="5" ry="3" fill="#ffc857" opacity="0.55"/>
      <ellipse cx="71" cy="64" rx="5" ry="3" fill="#ffc857" opacity="0.55"/>
      <defs>
        <linearGradient id="pipGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#16766f"/>
          <stop offset="1" stopColor="#074045"/>
        </linearGradient>
      </defs>
    </svg>
  );
}

function PipScreen({ screen }){
  React.useEffect(()=>{
    if(document.getElementById('pip-css')) return;
    const s = document.createElement('style'); s.id='pip-css'; s.textContent=pipCss; document.head.appendChild(s);
  },[]);

  if(screen === 'launcher') return <PipLauncher/>;
  return (
    <div className="pip-root">
      <div className="pip-shell">
        <TopBar/>
        <div className="trust">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#16766f" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>
          <span>პასუხები <strong style={{color:'#0a5258'}}>alte.edu.ge</strong>-ს ოფიციალური წყაროებიდან</span>
        </div>
        {screen==='greeting' && <Greeting/>}
        {screen==='chat' && <ChatThread/>}
        {screen==='handover' && <HandoverThread/>}
        {screen==='file' && <FileThread/>}
        {screen==='lead' && <LeadOverlay/>}
        {screen==='settings' && <SettingsOverlay/>}
        <Composer placeholder={screen==='greeting'} />
      </div>
    </div>
  );
}

function TopBar(){
  return (
    <div className="topbar">
      <div className="av"><PipFace size={32}/></div>
      <div>
        <div className="name">პიპი <span style={{color:'#16766f',fontWeight:500,fontSize:11}}>· ალტეს ასისტენტი</span></div>
        <div className="status">ონლაინ · Claude AI</div>
      </div>
      <div className="acts">
        <div className="lang-pill"><span className="on">KA</span><span>EN</span></div>
        <div className="ic" title="settings">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h0a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h0a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v0a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        </div>
        <div className="ic" title="close">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </div>
      </div>
    </div>
  );
}

function Composer({ placeholder }){
  return (
    <div className="composer">
      <div className="attach">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
      </div>
      <div className={"inp " + (placeholder?'placeholder':'')}>{placeholder ? 'მკითხე პროგრამაზე, მიღებაზე, დაფინანსებაზე…' : 'როდის არის ჩარიცხვის ბოლო ვადა?'}</div>
      <div className="send">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
      </div>
    </div>
  );
}

function Greeting(){
  return (
    <div className="msgs">
      <div className="pip-greet">
        <div className="big-pip"><PipFace size={70}/></div>
        <h2>გამარჯობა <span className="wave">👋</span></h2>
        <p>მე <strong>პიპი</strong> ვარ — ალტეს AI ასისტენტი.<br/>დამისვი ნებისმიერი კითხვა მიღების, პროგრამების ან დაფინანსების შესახებ.</p>
      </div>
      <div className="pip-quick">
        <div className="row">
          <div className="chip"><div className="icb" style={{background:'#fff3e0',color:'#c2410c'}}>📚</div>როგორ ჩავაბარო?</div>
          <div className="chip"><div className="icb" style={{background:'#e8f4f2',color:'#0a5258'}}>💰</div>რა ღირს სწავლა?</div>
        </div>
        <div className="row">
          <div className="chip"><div className="icb" style={{background:'#fef9c3',color:'#854d0e'}}>🩺</div>MD პროგრამა</div>
          <div className="chip"><div className="icb" style={{background:'#e0e7ff',color:'#3730a3'}}>🌍</div>საერთ. სტუდენტები</div>
        </div>
        <div className="row">
          <div className="chip" style={{background:'#074045',color:'#fff',borderColor:'#074045'}}>
            <div className="icb" style={{background:'#ffc857',color:'#7a3a00'}}>👋</div>დამიკავშირდი ოპერატორთან
          </div>
        </div>
      </div>
    </div>
  );
}

function PipLauncher(){
  return (
    <div className="pip-root">
      <div className="pip-page">
        <div className="nav">
          <div className="nav-logo">alte<span className="dot">.</span>edu.ge</div>
          <div className="nav-items">
            <span>ჩვენ შესახებ</span>
            <span style={{color:'#074045',fontWeight:600}}>მიღება</span>
            <span>სწავლა</span>
            <span>სტუდენტებისთვის</span>
            <span>დაფინანსება</span>
          </div>
          <div className="nav-right">
            <span>EN</span>
            <span className="lang" style={{borderColor:'#074045',color:'#074045',fontWeight:600}}>KA</span>
          </div>
        </div>
        <div className="hero">
          <h1>შენი მომავალი<br/>იწყება <em>აქ</em>.</h1>
          <p>24 წლის გამოცდილება. 2,500+ სტუდენტი 45 ქვეყნიდან. WHO/NCEQE აკრედიტებული.</p>
          <div className="ctas">
            <div className="cta-p">პროგრამები</div>
            <div className="cta-s">აპლიკაცია</div>
          </div>
        </div>
        <div className="stats">
          <div className="stat"><div className="n">2,500+</div><div className="l">სტუდენტი</div></div>
          <div className="stat"><div className="n">45</div><div className="l">ქვეყანა</div></div>
          <div className="stat"><div className="n">4</div><div className="l">სკოლა</div></div>
        </div>

        <div className="pip-launcher">
          <div className="hello-bubble">
            <strong>გამარჯობა! 👋</strong><br/>კითხვა გაქვს მიღებაზე? შემეკითხე.
            <div className="close">×</div>
          </div>
          <div className="pip-btn">
            <PipFace size={48}/>
          </div>
        </div>
      </div>
    </div>
  );
}

function ChatThread(){
  return (
    <div className="msgs">
      <div className="pip-row">
        <div className="pip-mini"><PipFace size={20}/></div>
        <div>
          <div className="pip-dept-chip">🩺 მედიცინა · MD</div>
          <div className="pip-bub">
            <strong>Doctor of Medicine (MD)</strong> — 6-წლიანი ერთსაფეხურიანი პროგრამა ინგლისურ ენაზე.<br/><br/>
            • ხანგრძლივობა: <strong>6 წელი</strong><br/>
            • ენა: ინგლისური<br/>
            • წლიური საფასური: <strong>$5,500</strong><br/>
            • WHO/NCEQE აღიარებული<br/><br/>
            გინდა გავაგრძელო ჩარიცხვის პროცესზე?
            <div style={{display:'flex',gap:6,marginTop:10,flexWrap:'wrap'}}>
              <div className="pip-source">
                <svg className="ic-link" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                alte.edu.ge/ka/ertsafekhuriani
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="pip-row u">
        <div className="pip-mini u">თქ</div>
        <div className="pip-bub">როდის არის ჩარიცხვის ბოლო ვადა?</div>
      </div>

      <div className="pip-row">
        <div className="pip-mini"><PipFace size={20}/></div>
        <div className="pip-bub" style={{paddingRight:18}}>
          <div className="pip-dots" aria-label="typing"><span></span><span></span><span></span></div>
        </div>
      </div>
    </div>
  );
}

function HandoverThread(){
  return (
    <div className="msgs">
      <div className="pip-row u">
        <div className="pip-mini u">თქ</div>
        <div className="pip-bub">გადამამისამართე ოპერატორთან</div>
      </div>
      <div className="pip-row">
        <div className="pip-mini"><PipFace size={20}/></div>
        <div>
          <div className="pip-bub">რა თქმა უნდა! ვაკავშირებ <strong>მიღების</strong> გუნდის ცოცხალ ოპერატორთან 👇</div>
          <div className="pip-handover">
            <div className="h">
              <div className="ico">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1v-6h3z"/><path d="M3 19a2 2 0 0 0 2 2h1v-6H3z"/></svg>
              </div>
              ოპერატორი ჩაერთო
            </div>
            <div className="dept">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#074045" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              მიღების ოფისი · Admissions
            </div>
            <div className="note">სამუშაო საათები: <strong>ორშ–პარ, 09:00–18:00</strong>. შემოვტოვო შენი კონტაქტი, რომ მოგწერონ?</div>
            <div className="actions">
              <div className="btn-p">დიახ, კონტაქტი დავტოვო</div>
              <div className="btn-s">არა</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LeadOverlay(){
  return (
    <>
      <div className="msgs" style={{filter:'blur(1.5px)',pointerEvents:'none'}}>
        <div className="pip-row">
          <div className="pip-mini"><PipFace size={20}/></div>
          <div className="pip-bub">დიდი მადლობა! მხოლოდ რამდენიმე დეტალი მჭირდება, რომ მიღების გუნდმა დაგიკავშირდეს.</div>
        </div>
      </div>
      <div className="pip-modal-bg">
        <div className="pip-modal">
          <div className="grip"></div>
          <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:8}}>
            <div style={{width:36,height:36,borderRadius:12,background:'#074045',display:'flex',alignItems:'center',justifyContent:'center'}}>
              <PipFace size={26}/>
            </div>
            <div>
              <h3>დავტოვოთ <span className="em">კონტაქტი?</span></h3>
              <div className="sub" style={{marginBottom:0,fontSize:11.5}}>მიღების გუნდი 24 საათში დაგიკავშირდება</div>
            </div>
          </div>
          <div className="pip-form">
            <div className="field">
              <label>სახელი</label>
              <div className="inp">ნინო კვარაცხელია</div>
            </div>
            <div className="row">
              <div className="field" style={{flex:1.2}}>
                <label>ტელეფონი</label>
                <div className="inp active">+995 5__ __ __ __</div>
              </div>
              <div className="field">
                <label>ენა</label>
                <div className="inp" style={{display:'flex',alignItems:'center',gap:6}}>🇬🇪 KA</div>
              </div>
            </div>
            <div className="field">
              <label>ინტერესის სფერო</label>
              <div className="inp" style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
                <span>🩺 მედიცინა · MD პროგრამა</span>
                <span style={{color:'#7a8588'}}>▾</span>
              </div>
            </div>
            <div className="consent">
              <div className="cbox">✓</div>
              <div>ვეთანხმები <a>კონფიდენციალურობის პოლიტიკას</a>. ჩემი მონაცემები გამოყენებული იქნება მხოლოდ მიღების მიზნით.</div>
            </div>
            <div className="submit">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              გაგზავნა
            </div>
            <div className="later">ახლა არა, მადლობა</div>
          </div>
        </div>
      </div>
    </>
  );
}

function SettingsOverlay(){
  return (
    <>
      <div className="msgs" style={{filter:'blur(1.5px)',pointerEvents:'none'}}>
        <div className="pip-row">
          <div className="pip-mini"><PipFace size={20}/></div>
          <div className="pip-bub">გაგიხარდე! რით შემიძლია დაგეხმარო?</div>
        </div>
      </div>
      <div className="pip-modal-bg">
        <div className="pip-modal pip-settings">
          <div className="grip"></div>
          <h3>პარამეტრები</h3>
          <div className="sub">აირჩიე ენა და გამოცდილების სტილი</div>

          <h4>ენა · Language</h4>
          <div className="item on">
            <div className="flag">🇬🇪</div>
            <div style={{flex:1}}>
              <div className="nm">ქართული</div>
              <div className="sb">Georgian</div>
            </div>
            <div className="check">✓</div>
          </div>
          <div className="item">
            <div className="flag">🇬🇧</div>
            <div style={{flex:1}}>
              <div className="nm">English</div>
              <div className="sb">For international students</div>
            </div>
            <div className="check off">✓</div>
          </div>

          <h4>გამოცდილება</h4>
          <div className="toggle-row">
            <div style={{flex:1}}>
              <div className="lb">ხმოვანი შეტყობინება</div>
              <div className="sb">ჩათში გასაჟღერებლად</div>
            </div>
            <div className="sw off"></div>
          </div>
          <div className="toggle-row">
            <div style={{flex:1}}>
              <div className="lb">წყაროების ბმულები</div>
              <div className="sb">alte.edu.ge საიტიდან</div>
            </div>
            <div className="sw"></div>
          </div>
          <div className="toggle-row">
            <div style={{flex:1}}>
              <div className="lb">ანიმაციები</div>
              <div className="sb">პიპის ცოცხალი რეაქციები</div>
            </div>
            <div className="sw"></div>
          </div>

          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginTop:14,padding:'0 4px'}}>
            <div style={{fontSize:10.5,color:'#7a8588'}}>v2.0 · Powered by Claude AI</div>
            <div style={{fontSize:11.5,color:'#074045',fontWeight:600}}>ისტორიის გასუფთავება</div>
          </div>
        </div>
      </div>
    </>
  );
}

function FileThread(){
  return (
    <div className="msgs">
      <div className="pip-row u">
        <div className="pip-mini u">თქ</div>
        <div style={{maxWidth:'80%'}}>
          <div style={{background:'#074045',borderRadius:'14px 14px 4px 14px',padding:'8px',border:'1px solid #074045',marginBottom:6}}>
            <div style={{background:'#fff8ee',borderRadius:10,padding:'10px 12px',display:'flex',alignItems:'center',gap:9}}>
              <div style={{width:34,height:42,background:'#ff8a65',borderRadius:'5px 8px 5px 5px',position:'relative',flexShrink:0,display:'flex',alignItems:'center',justifyContent:'center'}}>
                <div style={{position:'absolute',top:0,right:0,width:9,height:9,background:'#e96e4a',clipPath:'polygon(0 0, 100% 100%, 100% 0)'}}></div>
                <span style={{fontSize:8,fontWeight:800,color:'#fff',marginTop:6}}>PDF</span>
              </div>
              <div style={{flex:1,minWidth:0}}>
                <div style={{fontSize:12,fontWeight:700,color:'#1a2628',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>cnoba_atestati.pdf</div>
                <div style={{fontSize:10.5,color:'#7a8588',marginTop:1}}>342 KB · 2 გვერდი</div>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16766f" strokeWidth="2.6" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
          </div>
          <div className="pip-bub" style={{background:'#074045',color:'#fff',borderColor:'#074045',borderRadius:'18px 18px 4px 18px'}}>ჩემი ატესტატია. გამოდგება?</div>
        </div>
      </div>

      <div className="pip-row">
        <div className="pip-mini"><PipFace size={20}/></div>
        <div className="pip-bub">
          გამიკვირდი წაკითხე 📄 უდებო ატესტატი ხარისხობა:<br/><br/>
          • GPA: <strong>3.7 / 4.0</strong> ✅<br/>
          • ინგლისური (B2+) ✅<br/>
          • ბიოლოგია/ქიმია: ადეკვატური<br/><br/>
          ატესტატი აკმაყოფილებს <strong>MD პროგრამის</strong> მოთხოვნებს. გავაგრზელოთ?
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { PipScreen });
