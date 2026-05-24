// VARIANT 2 — "Bento" — color-coded department blocks, modern structured
// Each dept = its own bold color identity. Brand teal as anchor.

const bentoCss = `
.bento-root{ width:100%; height:100%; font-family:'Noto Sans Georgian','Inter',sans-serif; color:#0f172a; }
.bento-root *{ box-sizing:border-box; }

/* Dept color palette */
.bento-root{
  --c-admissions: #074045;  --c-admissions-bg: #e8f4f2;
  --c-international: #6d28d9; --c-international-bg: #f3edff;
  --c-finance: #b45309; --c-finance-bg: #fef3c7;
  --c-medicine: #be123c; --c-medicine-bg: #ffe4e6;
  --c-services: #047857; --c-services-bg: #d1fae5;
  --c-it: #1d4ed8; --c-it-bg: #dbeafe;
}

/* Page backdrop for launcher */
.bento-page{ width:100%; height:100%; background:#f8fafc; position:relative; overflow:hidden; }
.bento-page .nav{ height:60px; background:#fff; border-bottom:1px solid #e2e8f0; display:flex; align-items:center; padding:0 22px; gap:22px; }
.bento-page .nav-logo{ font-family:'Fraunces',serif; font-weight:800; font-size:18px; color:#074045; }
.bento-page .nav-logo .dot{ color:#be123c; }
.bento-page .nav-items{ display:flex; gap:16px; font-size:12px; color:#475569; margin-left:8px; }
.bento-page .nav-items .active{ color:#074045; font-weight:600; }
.bento-page .nav-r{ margin-left:auto; font-size:11px; color:#64748b; display:flex; gap:10px; align-items:center; }
.bento-page .nav-r .kalang{ padding:4px 9px; border:1px solid #074045; color:#074045; border-radius:6px; font-weight:600; }
.bento-page .hero{ padding:36px 30px; }
.bento-page .hero h1{ font-family:'Fraunces',serif; font-size:32px; font-weight:700; color:#0f172a; max-width:340px; line-height:1.1; letter-spacing:-0.02em; margin:0 0 12px; }
.bento-page .hero h1 em{ color:#074045; font-style:normal; }
.bento-page .hero p{ color:#475569; font-size:13px; max-width:330px; line-height:1.6; margin:0; }
.bento-page .card-grid{ position:absolute; left:30px; right:30px; bottom:90px; display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.bento-page .card-mini{ padding:14px; border-radius:14px; background:#fff; border:1px solid #e2e8f0; }
.bento-page .card-mini .badge{ display:inline-block; padding:3px 8px; border-radius:20px; font-size:9.5px; font-weight:700; letter-spacing:0.04em; text-transform:uppercase; margin-bottom:6px; }
.bento-page .card-mini .ttl{ font-family:'Fraunces',serif; font-size:14px; font-weight:600; line-height:1.3; color:#0f172a; }

/* Launcher */
.bento-launcher{ position:absolute; bottom:24px; right:24px; display:flex; flex-direction:column; align-items:flex-end; gap:10px; }
.bento-launcher .tease{ background:#fff; border:1px solid #e2e8f0; border-radius:14px 14px 4px 14px; padding:11px 14px; box-shadow:0 10px 30px rgba(15,23,42,0.12); font-size:12px; color:#0f172a; max-width:230px; line-height:1.45; }
.bento-launcher .tease .head{ display:flex; align-items:center; gap:6px; font-size:11px; font-weight:600; color:#074045; margin-bottom:4px; }
.bento-launcher .tease .head .dot{ width:6px; height:6px; border-radius:50%; background:#10b981; }
.bento-launcher .blk-btn{ width:64px; height:64px; border-radius:20px; background:#074045; color:#fff; display:flex; align-items:center; justify-content:center; box-shadow:0 14px 30px rgba(7,64,69,0.3); position:relative; transform:rotate(-3deg); }
.bento-launcher .blk-btn::before{ content:''; position:absolute; inset:-6px -6px auto auto; width:20px; height:20px; background:#fbbf24; border-radius:8px; transform:rotate(8deg); }
.bento-launcher .blk-btn::after{ content:''; position:absolute; inset:auto auto -6px -6px; width:18px; height:18px; background:#be123c; border-radius:7px; transform:rotate(-12deg); }
.bento-launcher .blk-btn .ico{ position:relative; z-index:2; }
.bento-launcher .blk-btn .pulse{ position:absolute; top:6px; right:6px; width:9px; height:9px; border-radius:50%; background:#10b981; border:2px solid #fff; z-index:3; }

/* Shell */
.bento-shell{ width:100%; height:100%; background:#fff; display:flex; flex-direction:column; overflow:hidden; }
.bento-topbar{ background:#0f172a; color:#fff; padding:12px 16px; display:flex; align-items:center; gap:11px; }
.bento-topbar .blk{ width:36px; height:36px; border-radius:11px; background:#074045; display:flex; align-items:center; justify-content:center; position:relative; }
.bento-topbar .blk::before{ content:''; position:absolute; inset:-3px -3px auto auto; width:10px; height:10px; background:#fbbf24; border-radius:3px; }
.bento-topbar .nm{ font-family:'Fraunces',serif; font-size:15px; font-weight:700; letter-spacing:-0.01em; }
.bento-topbar .stt{ font-size:10.5px; color:#94a3b8; display:flex; align-items:center; gap:5px; margin-top:1px; }
.bento-topbar .stt::before{ content:''; width:6px; height:6px; border-radius:50%; background:#10b981; }
.bento-topbar .acts{ margin-left:auto; display:flex; gap:6px; align-items:center; }
.bento-topbar .lang{ display:flex; background:rgba(255,255,255,0.1); border-radius:8px; overflow:hidden; font-size:11px; font-weight:600; }
.bento-topbar .lang span{ padding:6px 9px; }
.bento-topbar .lang span.on{ background:#fff; color:#0f172a; }
.bento-topbar .ic{ width:32px; height:32px; border-radius:9px; background:rgba(255,255,255,0.08); display:flex; align-items:center; justify-content:center; color:#fff; }

.bento-shell .strip{ height:36px; background:#fff; border-bottom:1px solid #e2e8f0; padding:0 16px; display:flex; align-items:center; gap:8px; font-size:10.5px; color:#475569; }
.bento-shell .strip .pill{ background:#e8f4f2; color:#074045; padding:3px 9px; border-radius:20px; font-weight:600; font-size:10px; }

.bento-shell .msgs{ flex:1; overflow-y:auto; padding:16px; background:#f8fafc; display:flex; flex-direction:column; gap:12px; }

.bento-shell .composer{ background:#fff; border-top:1px solid #e2e8f0; padding:10px 12px; display:flex; gap:8px; align-items:center; }
.bento-shell .composer .inp{ flex:1; background:#f1f5f9; border:1px solid #e2e8f0; border-radius:10px; padding:10px 12px; font-size:12.5px; color:#0f172a; }
.bento-shell .composer .inp.placeholder{ color:#94a3b8; }
.bento-shell .composer .send{ width:40px; height:40px; border-radius:11px; background:#074045; color:#fff; display:flex; align-items:center; justify-content:center; }
.bento-shell .composer .mic{ width:38px; height:38px; border-radius:11px; background:#f1f5f9; color:#475569; display:flex; align-items:center; justify-content:center; }

/* Messages */
.bento-row{ display:flex; gap:8px; align-items:flex-end; }
.bento-row.u{ flex-direction:row-reverse; }
.bento-av{ width:30px; height:30px; border-radius:9px; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; color:#fff; }
.bento-bub{ background:#fff; border-radius:14px 14px 14px 4px; padding:12px 14px; font-size:13px; line-height:1.55; color:#0f172a; max-width:80%; border:1px solid #e2e8f0; }
.bento-row.u .bento-bub{ background:#074045; color:#fff; border-color:#074045; border-radius:14px 14px 4px 14px; }
.bento-row.u .bento-av{ background:#cbd5e1; color:#475569; }

.bento-dept-strip{ height:4px; border-radius:2px; margin:-12px -14px 10px; }

.bento-bub.dept{ padding:0; overflow:hidden; }
.bento-bub.dept .inner{ padding:12px 14px; }
.bento-bub.dept .head{ display:flex; align-items:center; justify-content:space-between; padding:8px 14px; font-size:10.5px; font-weight:700; letter-spacing:0.04em; text-transform:uppercase; }
.bento-bub.dept .head .conf{ background:rgba(255,255,255,0.5); padding:2px 7px; border-radius:20px; font-size:9.5px; }
.bento-bub.dept .src{ border-top:1px solid #e2e8f0; padding:8px 14px; font-size:11px; color:#475569; display:flex; align-items:center; gap:6px; background:#f8fafc; }
.bento-bub.dept .src a{ color:inherit; font-weight:600; }
.bento-bub.dept ul{ margin:6px 0 0; padding:0; list-style:none; display:flex; flex-direction:column; gap:5px; }
.bento-bub.dept ul li{ display:flex; gap:7px; align-items:flex-start; font-size:12.5px; line-height:1.5; }
.bento-bub.dept ul li::before{ content:''; width:5px; height:5px; border-radius:1px; margin-top:8px; flex-shrink:0; }
.bento-bub.dept.adm ul li::before{ background:#074045; }
.bento-bub.dept.med ul li::before{ background:#be123c; }
.bento-bub.dept.fin ul li::before{ background:#b45309; }

/* typing */
.bento-typing{ display:flex; gap:4px; padding:8px 0; }
.bento-typing span{ width:7px; height:7px; border-radius:2px; background:#94a3b8; animation:bentoBlink 1.4s infinite both; }
.bento-typing span:nth-child(2){ animation-delay:0.2s; }
.bento-typing span:nth-child(3){ animation-delay:0.4s; }
@keyframes bentoBlink{ 0%,80%,100%{ opacity:0.3;} 40%{ opacity:1;} }

/* Greeting bento cards */
.bento-greet{ padding:6px 0 4px; }
.bento-greet .hello{ font-family:'Fraunces',serif; font-size:22px; font-weight:700; color:#0f172a; letter-spacing:-0.02em; margin-bottom:4px; }
.bento-greet .sub{ font-size:12.5px; color:#475569; line-height:1.5; margin-bottom:16px; }
.bento-grid{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; }
.bento-card{ aspect-ratio:1; padding:11px; border-radius:14px; display:flex; flex-direction:column; justify-content:space-between; cursor:pointer; position:relative; overflow:hidden; }
.bento-card .ico{ width:30px; height:30px; border-radius:9px; background:rgba(255,255,255,0.6); display:flex; align-items:center; justify-content:center; font-size:14px; }
.bento-card .lb{ font-size:11.5px; font-weight:700; line-height:1.25; letter-spacing:-0.01em; }
.bento-card.wide{ aspect-ratio:auto; grid-column:span 3; min-height:54px; flex-direction:row; align-items:center; gap:10px; padding:12px 14px; }
.bento-card.wide .ico{ width:34px; height:34px; }
.bento-card.wide .lb{ flex:1; font-size:13px; }
.bento-card .arr{ position:absolute; right:9px; bottom:9px; opacity:0.5; }

/* Handover card */
.bento-handover{ margin-top:4px; border:1.5px solid #074045; border-radius:14px; background:#fff; overflow:hidden; }
.bento-handover .h{ background:#074045; color:#fff; padding:11px 13px; display:flex; align-items:center; gap:9px; font-size:12px; font-weight:700; }
.bento-handover .h .ico{ width:26px; height:26px; border-radius:8px; background:rgba(255,255,255,0.15); display:flex; align-items:center; justify-content:center; }
.bento-handover .body{ padding:13px; }
.bento-handover .dept-block{ display:flex; align-items:center; gap:9px; padding:9px 11px; border-radius:10px; margin-bottom:10px; }
.bento-handover .dept-block.adm{ background:#e8f4f2; color:#074045; }
.bento-handover .dept-block .ic{ width:30px; height:30px; border-radius:9px; background:#fff; display:flex; align-items:center; justify-content:center; }
.bento-handover .dept-block .nm{ font-size:12.5px; font-weight:700; }
.bento-handover .dept-block .desc{ font-size:10.5px; opacity:0.7; }
.bento-handover .hours{ display:flex; gap:7px; padding:8px 10px; background:#f8fafc; border-radius:9px; font-size:11px; color:#475569; align-items:center; }
.bento-handover .hours strong{ color:#0f172a; }
.bento-handover .actions{ display:flex; gap:6px; margin-top:11px; }
.bento-handover .btn-p{ flex:1; background:#074045; color:#fff; padding:11px; border-radius:10px; text-align:center; font-size:12px; font-weight:700; }
.bento-handover .btn-s{ background:#fff; color:#074045; padding:11px 14px; border-radius:10px; text-align:center; font-size:12px; font-weight:700; border:1px solid #074045; }

/* Modal */
.bento-overlay{ position:absolute; inset:0; background:rgba(15,23,42,0.5); display:flex; align-items:center; justify-content:center; padding:18px; }
.bento-modal{ background:#fff; border-radius:18px; width:100%; max-width:380px; overflow:hidden; box-shadow:0 20px 60px rgba(0,0,0,0.3); }
.bento-modal .head{ padding:18px 18px 10px; background:linear-gradient(180deg,#074045 0%,#0a5258 100%); color:#fff; position:relative; }
.bento-modal .head::after{ content:''; position:absolute; right:18px; top:18px; width:34px; height:34px; border-radius:10px; background:#fbbf24; transform:rotate(8deg); z-index:0; }
.bento-modal .head::before{ content:'⚡'; position:absolute; right:25px; top:24px; font-size:20px; z-index:1; }
.bento-modal h3{ font-family:'Fraunces',serif; font-size:18px; font-weight:700; margin:0 0 4px; letter-spacing:-0.01em; position:relative; z-index:2; max-width:240px; }
.bento-modal .sb{ font-size:12px; opacity:0.85; line-height:1.45; max-width:280px; }
.bento-modal .body{ padding:16px 18px 18px; }
.bento-modal .progress{ display:flex; gap:5px; margin-bottom:14px; }
.bento-modal .progress .step{ flex:1; height:3px; border-radius:2px; background:#e2e8f0; }
.bento-modal .progress .step.on{ background:#074045; }
.bento-modal .field{ margin-bottom:11px; }
.bento-modal .field label{ display:block; font-size:11px; font-weight:600; color:#475569; margin-bottom:5px; }
.bento-modal .field .inp{ width:100%; padding:11px 13px; border:1.5px solid #e2e8f0; border-radius:10px; font-size:13px; color:#0f172a; background:#fff; }
.bento-modal .field .inp.placeholder{ color:#94a3b8; }
.bento-modal .field .inp.active{ border-color:#074045; }
.bento-modal .field .hint{ font-size:10.5px; color:#94a3b8; margin-top:4px; }
.bento-modal .field-row{ display:flex; gap:8px; }
.bento-modal .field-row .field{ flex:1; }
.bento-modal .chips{ display:flex; flex-wrap:wrap; gap:6px; }
.bento-modal .chip{ padding:6px 11px; border:1.5px solid #e2e8f0; border-radius:20px; font-size:11px; color:#475569; font-weight:500; }
.bento-modal .chip.on{ background:#074045; color:#fff; border-color:#074045; }
.bento-modal .submit{ width:100%; padding:13px; background:#074045; color:#fff; border-radius:11px; font-size:13px; font-weight:700; display:flex; align-items:center; justify-content:center; gap:6px; }
.bento-modal .ftr{ text-align:center; margin-top:10px; font-size:10.5px; color:#94a3b8; padding:0 6px; line-height:1.5; }
.bento-modal .ftr a{ color:#074045; font-weight:600; }

/* Settings modal */
.bento-settings .langgrid{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:14px; }
.bento-settings .lang-card{ padding:13px; border-radius:12px; border:2px solid #e2e8f0; }
.bento-settings .lang-card.on{ border-color:#074045; background:#f0fdfa; }
.bento-settings .lang-card .flg{ font-size:22px; margin-bottom:6px; }
.bento-settings .lang-card .nm{ font-size:13px; font-weight:700; color:#0f172a; }
.bento-settings .lang-card .sub{ font-size:10.5px; color:#64748b; margin-top:1px; }
.bento-settings .lang-card .ck{ position:absolute; }
.bento-settings h4{ font-size:10.5px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.06em; margin:14px 0 8px; }
.bento-settings .opt{ padding:11px 13px; border-radius:11px; display:flex; align-items:center; gap:11px; border:1px solid #e2e8f0; margin-bottom:6px; }
.bento-settings .opt .ic{ width:32px; height:32px; border-radius:9px; background:#f1f5f9; display:flex; align-items:center; justify-content:center; font-size:14px; color:#475569; flex-shrink:0; }
.bento-settings .opt .lb{ flex:1; font-size:12.5px; font-weight:600; color:#0f172a; }
.bento-settings .opt .sb{ font-size:10.5px; color:#64748b; margin-top:1px; font-weight:400; }
.bento-settings .sw{ width:36px; height:20px; border-radius:20px; background:#074045; position:relative; }
.bento-settings .sw::after{ content:''; position:absolute; right:2px; top:2px; width:16px; height:16px; border-radius:50%; background:#fff; }
.bento-settings .sw.off{ background:#cbd5e1; }
.bento-settings .sw.off::after{ left:2px; right:auto; }
`;

const DEPTS = {
  adm: { lb:'მიღება · Admissions', short:'მიღება', color:'#074045', bg:'#e8f4f2', icon:'🎓' },
  int: { lb:'საერთ. სტუდენტები', short:'საერთ.', color:'#6d28d9', bg:'#f3edff', icon:'🌍' },
  fin: { lb:'ფინანსები', short:'ფინანსები', color:'#b45309', bg:'#fef3c7', icon:'💰' },
  med: { lb:'მედიცინა · MD', short:'მედიცინა', color:'#be123c', bg:'#ffe4e6', icon:'🩺' },
  svc: { lb:'სტუდ. სერვისები', short:'სერვისები', color:'#047857', bg:'#d1fae5', icon:'💚' },
  it:  { lb:'IT დახმარება', short:'IT', color:'#1d4ed8', bg:'#dbeafe', icon:'💻' },
};

function BentoScreen({ screen }){
  React.useEffect(()=>{
    if(document.getElementById('bento-css')) return;
    const s = document.createElement('style'); s.id='bento-css'; s.textContent=bentoCss; document.head.appendChild(s);
  },[]);

  if(screen === 'launcher') return <BentoLauncher/>;
  return (
    <div className="bento-root">
      <div className="bento-shell">
        <BentoTopbar/>
        <div className="strip">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#16766f" strokeWidth="2.4"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          <span>ოფიც. წყაროები · </span>
          <span className="pill">alte.edu.ge</span>
        </div>
        {screen==='greeting' && <BentoGreeting/>}
        {screen==='chat' && <BentoChat/>}
        {screen==='handover' && <BentoHandover/>}
        {screen==='file' && <BentoFile/>}
        {screen==='lead' && <BentoLead/>}
        {screen==='settings' && <BentoSettings/>}
        <BentoComposer placeholder={screen==='greeting'} />
      </div>
    </div>
  );
}

function BentoTopbar(){
  return (
    <div className="bento-topbar">
      <div className="blk">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
      </div>
      <div>
        <div className="nm">Alte Assistant</div>
        <div className="stt">ონლაინ · ექსპერტი 6 დეპარტამენტში</div>
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

function BentoComposer({ placeholder }){
  return (
    <div className="composer">
      <div className={"inp " + (placeholder?'placeholder':'')}>{placeholder ? 'მკითხე ნებისმიერი დეპარტამენტი…' : 'რა არის სტიპენდიის პირობები?'}</div>
      <div className="mic">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
      </div>
      <div className="send">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
      </div>
    </div>
  );
}

function BentoLauncher(){
  return (
    <div className="bento-root">
      <div className="bento-page">
        <div className="nav">
          <div className="nav-logo">alte<span className="dot">.</span>edu.ge</div>
          <div className="nav-items">
            <span>ჩვენ შესახებ</span>
            <span className="active">მიღება</span>
            <span>სწავლა</span>
            <span>სტუდენტებისთვის</span>
          </div>
          <div className="nav-r">
            <span>EN</span>
            <span className="kalang">KA</span>
          </div>
        </div>
        <div className="hero">
          <h1>აქ ყველა გზა <em>დიდია</em>.</h1>
          <p>აღმოაჩინე საბაკალავრო, სამედიცინო და სამაგისტრო პროგრამები ალტეში — 2,500+ სტუდენტი 45+ ქვეყნიდან.</p>
        </div>
        <div className="card-grid">
          <div className="card-mini">
            <div className="badge" style={{background:'#e8f4f2',color:'#074045'}}>მიღება</div>
            <div className="ttl">საბაკალავრო პროგრამები 2026</div>
          </div>
          <div className="card-mini">
            <div className="badge" style={{background:'#ffe4e6',color:'#be123c'}}>MD</div>
            <div className="ttl">Doctor of Medicine, EN</div>
          </div>
        </div>
        <div className="bento-launcher">
          <div className="tease">
            <div className="head"><span className="dot"></span>Alte Assistant ჩართულია</div>
            დაგეხმაროთ მიღების კითხვებზე?
          </div>
          <div className="blk-btn">
            <div className="pulse"></div>
            <svg className="ico" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          </div>
        </div>
      </div>
    </div>
  );
}

function BentoGreeting(){
  return (
    <div className="msgs">
      <div className="bento-greet">
        <div className="hello">გამარჯობა 👋</div>
        <div className="sub">აირჩიე თემა ან პირდაპირ ჩაწერე კითხვა. ვუპასუხებ ოფიც. წყაროებიდან.</div>
        <div className="bento-grid">
          <div className="bento-card" style={{background:'#e8f4f2'}}>
            <div className="ico" style={{color:'#074045'}}>🎓</div>
            <div className="lb" style={{color:'#074045'}}>მიღება<br/>2026</div>
          </div>
          <div className="bento-card" style={{background:'#ffe4e6'}}>
            <div className="ico" style={{color:'#be123c'}}>🩺</div>
            <div className="lb" style={{color:'#be123c'}}>მედიცინა<br/>MD · EN</div>
          </div>
          <div className="bento-card" style={{background:'#fef3c7'}}>
            <div className="ico" style={{color:'#b45309'}}>💰</div>
            <div className="lb" style={{color:'#b45309'}}>დაფინანსება სტიპენდია</div>
          </div>
          <div className="bento-card" style={{background:'#f3edff'}}>
            <div className="ico" style={{color:'#6d28d9'}}>🌍</div>
            <div className="lb" style={{color:'#6d28d9'}}>საერთ. სტუდენტი</div>
          </div>
          <div className="bento-card" style={{background:'#d1fae5'}}>
            <div className="ico" style={{color:'#047857'}}>💚</div>
            <div className="lb" style={{color:'#047857'}}>სტუდ. სერვისები</div>
          </div>
          <div className="bento-card" style={{background:'#dbeafe'}}>
            <div className="ico" style={{color:'#1d4ed8'}}>💻</div>
            <div className="lb" style={{color:'#1d4ed8'}}>IT დახმარება</div>
          </div>
          <div className="bento-card wide" style={{background:'#0f172a',color:'#fff'}}>
            <div className="ico" style={{background:'#fbbf24',color:'#0f172a'}}>👤</div>
            <div className="lb">დამიკავშირდი ცოცხალ ოპერატორთან</div>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinecap="round"><polyline points="9 18 15 12 9 6"/></svg>
          </div>
        </div>
      </div>
    </div>
  );
}

function BentoChat(){
  return (
    <div className="msgs">
      <div className="bento-row u">
        <div className="bento-av">თქ</div>
        <div className="bento-bub">რა ღირს MD პროგრამა?</div>
      </div>

      <div className="bento-row">
        <div className="bento-av" style={{background:'#be123c'}}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
        </div>
        <div className="bento-bub dept med" style={{maxWidth:'85%'}}>
          <div className="head" style={{background:'#ffe4e6',color:'#be123c'}}>
            <span>🩺 მედიცინა · MD</span>
            <span className="conf">95% კონფ.</span>
          </div>
          <div className="inner">
            <div><strong>Doctor of Medicine (MD)</strong></div>
            <ul>
              <li>წლიური საფასური: <strong>$5,500</strong></li>
              <li>ხანგრძლივობა: <strong>6 წელი</strong></li>
              <li>ენა: ინგლისური</li>
              <li>WHO/NCEQE აღიარებული</li>
            </ul>
          </div>
          <div className="src">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
            <a>alte.edu.ge/ka/ertsafekhuriani-sameditsino-programebi-2</a>
          </div>
        </div>
      </div>

      <div className="bento-row u">
        <div className="bento-av">თქ</div>
        <div className="bento-bub">სტიპენდიის სქემა მაქვს?</div>
      </div>

      <div className="bento-row">
        <div className="bento-av" style={{background:'#b45309'}}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><line x1="12" y1="6" x2="12" y2="18"/></svg>
        </div>
        <div className="bento-bub" style={{paddingRight:14}}>
          <div className="bento-typing"><span></span><span></span><span></span></div>
        </div>
      </div>
    </div>
  );
}

function BentoHandover(){
  return (
    <div className="msgs">
      <div className="bento-row u">
        <div className="bento-av">თქ</div>
        <div className="bento-bub">სტიპენდიის კონკრეტული პროცენტი მაინტერესებს</div>
      </div>
      <div className="bento-row">
        <div className="bento-av" style={{background:'#074045'}}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/></svg>
        </div>
        <div style={{maxWidth:'88%'}}>
          <div className="bento-bub">ეს კონკრეტული რიცხვები ცოცხალი ოპერატორის გადასამოწმებელია — ვუგზავნი მიღების გუნდს 👇</div>
          <div className="bento-handover">
            <div className="h">
              <div className="ico">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1v-6h3z"/><path d="M3 19a2 2 0 0 0 2 2h1v-6H3z"/></svg>
              </div>
              ცოცხალი ოპერატორი ჩაერთო
            </div>
            <div className="body">
              <div className="dept-block adm">
                <div className="ic">🎓</div>
                <div>
                  <div className="nm">მიღების ოფისი</div>
                  <div className="desc">Admissions team · alte.edu.ge</div>
                </div>
              </div>
              <div className="hours">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                <span>სამუშაო საათები: <strong>ორშ–პარ, 09:00–18:00</strong> · საშ. რეაქცია: 3 სთ</span>
              </div>
              <div className="actions">
                <div className="btn-p">დატოვე კონტაქტი</div>
                <div className="btn-s">დაელოდე</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function BentoLead(){
  return (
    <>
      <div className="msgs" style={{filter:'blur(2px)',pointerEvents:'none'}}>
        <div className="bento-row">
          <div className="bento-av" style={{background:'#074045'}}>🎓</div>
          <div className="bento-bub">დიდი მადლობა! მიღების გუნდი დაგიკავშირდება…</div>
        </div>
      </div>
      <div className="bento-overlay">
        <div className="bento-modal">
          <div className="head">
            <div style={{display:'inline-block',padding:'3px 9px',background:'rgba(255,255,255,0.2)',borderRadius:20,fontSize:10,fontWeight:700,letterSpacing:'0.05em',marginBottom:10}}>ნაბიჯი 1 / 2</div>
            <h3>დატოვე კონტაქტი</h3>
            <div className="sb">მიღების გუნდი 24 საათში დაგიკავშირდება. პასუხები ვერ მოგვცა AI-მ.</div>
          </div>
          <div className="body">
            <div className="progress">
              <div className="step on"></div>
              <div className="step"></div>
            </div>
            <div className="field">
              <label>სახელი და გვარი</label>
              <div className="inp">ნინო კვარაცხელია</div>
            </div>
            <div className="field-row">
              <div className="field" style={{flex:1.4}}>
                <label>ტელეფონი</label>
                <div className="inp active">+995 599 12 34 56</div>
              </div>
              <div className="field">
                <label>ენა</label>
                <div className="inp">KA</div>
              </div>
            </div>
            <div className="field">
              <label>ინტერესის სფერო</label>
              <div className="chips">
                <div className="chip">🎓 ბაკალავრი</div>
                <div className="chip on">🩺 MD</div>
                <div className="chip">🌍 საერთ.</div>
                <div className="chip">💰 ფინანსები</div>
              </div>
            </div>
            <div className="field">
              <label>კომენტარი (არასავალდებულო)</label>
              <div className="inp placeholder">ცოტა მეტი დეტალი…</div>
            </div>
            <div className="submit">
              გაგზავნა
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
            <div className="ftr">გაგზავნით ვეთანხმები <a>კონფიდენციალურობას</a> და მონაცემთა <a>დამუშავებას</a>.</div>
          </div>
        </div>
      </div>
    </>
  );
}

function BentoSettings(){
  return (
    <>
      <div className="msgs" style={{filter:'blur(2px)',pointerEvents:'none'}}>
        <div className="bento-row">
          <div className="bento-av" style={{background:'#074045'}}>🎓</div>
          <div className="bento-bub">გამარჯობა! რით დაგეხმარო?</div>
        </div>
      </div>
      <div className="bento-overlay">
        <div className="bento-modal bento-settings">
          <div className="head" style={{paddingBottom:14}}>
            <h3>პარამეტრები</h3>
            <div className="sb">ენა, შეტყობინებები, კონფიდენციალურობა</div>
          </div>
          <div className="body">
            <h4 style={{marginTop:0}}>ენა</h4>
            <div className="langgrid">
              <div className="lang-card on" style={{position:'relative'}}>
                <div className="flg">🇬🇪</div>
                <div className="nm">ქართული</div>
                <div className="sub">Georgian</div>
                <div style={{position:'absolute',top:10,right:10,width:18,height:18,borderRadius:50,background:'#074045',display:'flex',alignItems:'center',justifyContent:'center',color:'#fff',fontSize:11}}>✓</div>
              </div>
              <div className="lang-card">
                <div className="flg">🇬🇧</div>
                <div className="nm">English</div>
                <div className="sub">International</div>
              </div>
            </div>

            <h4>გამოცდილება</h4>
            <div className="opt">
              <div className="ic">🔔</div>
              <div style={{flex:1}}>
                <div className="lb">დაბრუნების შეტყობინება</div>
                <div className="sb">თუ კონტაქტი დატოვე, შეგატყობინებთ</div>
              </div>
              <div className="sw"></div>
            </div>
            <div className="opt">
              <div className="ic">🔗</div>
              <div style={{flex:1}}>
                <div className="lb">წყაროების ბმულები</div>
                <div className="sb">alte.edu.ge ბმულები ყოველ პასუხთან</div>
              </div>
              <div className="sw"></div>
            </div>
            <div className="opt">
              <div className="ic">🌙</div>
              <div style={{flex:1}}>
                <div className="lb">მუქი თემა</div>
                <div className="sb">თვალისთვის უფრო კომფორტული</div>
              </div>
              <div className="sw off"></div>
            </div>

            <div style={{marginTop:14,display:'flex',justifyContent:'space-between',alignItems:'center',padding:'10px 2px 0',borderTop:'1px solid #e2e8f0'}}>
              <div style={{fontSize:10.5,color:'#94a3b8'}}>Alte Assistant v2.0 · Claude AI</div>
              <div style={{fontSize:11.5,color:'#be123c',fontWeight:700}}>ისტორიის წაშლა</div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function BentoFile(){
  return (
    <div className="msgs">
      <div className="bento-row u">
        <div className="bento-av">თქ</div>
        <div style={{maxWidth:'85%'}}>
          <div style={{background:'#074045',borderRadius:'14px 14px 4px 14px',padding:6,marginBottom:6}}>
            <div style={{background:'#fff',borderRadius:10,padding:10,display:'flex',gap:10,alignItems:'center'}}>
              <div style={{width:36,height:44,background:'#be123c',borderRadius:6,display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0,color:'#fff',fontSize:8.5,fontWeight:800,letterSpacing:'0.04em'}}>PDF</div>
              <div style={{flex:1,minWidth:0}}>
                <div style={{fontSize:12.5,fontWeight:700,color:'#0f172a',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>application_form_2026.pdf</div>
                <div style={{fontSize:10.5,color:'#64748b'}}>1.2 MB · 4 გვერდი</div>
              </div>
              <div style={{display:'flex',flexDirection:'column',gap:3,alignItems:'flex-end'}}>
                <div style={{height:3,width:50,background:'#e2e8f0',borderRadius:2,overflow:'hidden'}}>
                  <div style={{height:'100%',width:'100%',background:'#10b981'}}></div>
                </div>
                <div style={{fontSize:9.5,color:'#10b981',fontWeight:700}}>✓ ატვირთულია</div>
              </div>
            </div>
          </div>
          <div className="bento-bub" style={{background:'#074045',color:'#fff',borderColor:'#074045',borderRadius:'14px 14px 4px 14px'}}>აპლიკაციის ფორმა შევავსე — შეიოწმეთ?</div>
        </div>
      </div>

      <div className="bento-row">
        <div className="bento-av" style={{background:'#074045'}}>🎓</div>
        <div className="bento-bub dept adm" style={{maxWidth:'85%'}}>
          <div className="head" style={{background:'#e8f4f2',color:'#074045'}}>
            <span>🎓 მიღება · Admissions</span>
            <span className="conf">🔍 შეოწმდა</span>
          </div>
          <div className="inner">
            გადავამოწმე! ფორმა <strong>95% სწორად შევსებულია</strong>.
            <ul>
              <li>პირადი მონაცემები ✓</li>
              <li>საათო განაცხადება ✓</li>
              <li style={{color:'#b45309'}}>საბანკო დოკუმენტი: <strong>აკლია</strong></li>
            </ul>
          </div>
          <div className="src">
            <span>გნებ დაეხმარო შევსებულ დოკუმენტების ატვირთვასთან?</span>
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { BentoScreen });
