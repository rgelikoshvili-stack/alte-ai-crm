// VARIANT 4 — "Pro" — sidebar-based, professional/agency-grade
// Forks the user's original alte_university_ai_chatbot.html and polishes it.

const proCss = `
.pro-root{ width:100%; height:100%; font-family:'Noto Sans Georgian','Inter',sans-serif; color:#0f1a1c; }
.pro-root *{ box-sizing:border-box; }

/* Page backdrop for launcher */
.pro-page{ width:100%; height:100%; background:#f4f1ea; position:relative; overflow:hidden; }
.pro-page .nav{ height:60px; background:#fff; border-bottom:1px solid #e2dccc; display:flex; align-items:center; padding:0 22px; gap:20px; }
.pro-page .nav-logo{ font-family:'Fraunces',serif; font-weight:700; font-size:19px; color:#074045; letter-spacing:-0.02em; }
.pro-page .nav-items{ display:flex; gap:18px; font-size:12px; color:#3a4548; }
.pro-page .nav-items .active{ color:#074045; font-weight:600; }
.pro-page .nav-r{ margin-left:auto; display:flex; gap:8px; align-items:center; font-size:11px; color:#5a6c6d; }
.pro-page .nav-r .lang-on{ color:#074045; font-weight:700; }
.pro-page .nav-r .apply{ background:#074045; color:#fff; padding:8px 14px; border-radius:6px; font-weight:600; }

.pro-page .hero{ padding:42px 28px 0; max-width:380px; }
.pro-page .hero .eyebrow{ font-size:11px; font-weight:700; color:#074045; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:10px; }
.pro-page .hero h1{ font-family:'Fraunces',serif; font-size:32px; line-height:1.1; color:#0f1a1c; font-weight:700; letter-spacing:-0.02em; margin:0 0 14px; }
.pro-page .hero p{ font-size:13px; color:#3a4548; line-height:1.6; margin:0 0 22px; max-width:300px; }
.pro-page .hero .stats{ display:flex; gap:24px; }
.pro-page .hero .stats .stat .n{ font-family:'Fraunces',serif; font-size:24px; font-weight:700; color:#074045; }
.pro-page .hero .stats .stat .l{ font-size:10.5px; color:#5a6c6d; margin-top:1px; }
.pro-page .pic{ position:absolute; right:24px; top:90px; bottom:24px; width:46%; background:linear-gradient(160deg,#074045 0%,#0a5258 60%,#16766f 100%); border-radius:14px; padding:20px; color:#fff; display:flex; flex-direction:column; justify-content:flex-end; }
.pro-page .pic::before{ content:''; position:absolute; right:18px; top:18px; padding:5px 11px; background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.25); border-radius:20px; font-size:9.5px; font-weight:600; letter-spacing:0.04em; text-transform:uppercase; }
.pro-page .pic::after{ content:'WHO · NCEQE აღიარებული'; position:absolute; right:18px; top:18px; padding:5px 11px; font-size:9.5px; font-weight:600; letter-spacing:0.04em; }
.pro-page .pic .qt{ font-family:'Fraunces',serif; font-size:18px; font-weight:600; line-height:1.3; letter-spacing:-0.01em; margin-bottom:12px; }
.pro-page .pic .by{ font-size:10.5px; opacity:0.75; }

/* Launcher pill */
.pro-launcher{ position:absolute; right:22px; bottom:22px; display:flex; align-items:center; gap:11px; }
.pro-launcher .pill{ background:#fff; border:1px solid #e2dccc; border-radius:24px; padding:10px 18px 10px 12px; box-shadow:0 10px 30px rgba(7,64,69,0.12); display:flex; align-items:center; gap:10px; }
.pro-launcher .pill .av{ width:32px; height:32px; border-radius:50%; background:#074045; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px; position:relative; flex-shrink:0; }
.pro-launcher .pill .av::after{ content:''; position:absolute; bottom:-2px; right:-2px; width:10px; height:10px; border-radius:50%; background:#1ca672; border:2px solid #fff; }
.pro-launcher .pill .tx .nm{ font-size:11.5px; font-weight:700; color:#0f1a1c; line-height:1.2; }
.pro-launcher .pill .tx .sb{ font-size:10px; color:#5a6c6d; }
.pro-launcher .pill .arr{ width:26px; height:26px; border-radius:50%; background:#074045; color:#fff; display:flex; align-items:center; justify-content:center; }

/* Shell — sidebar + main */
.pro-shell{ width:100%; height:100%; background:#fff; display:flex; overflow:hidden; }

/* Sidebar */
.pro-side{ width:200px; background:#f6f2e8; border-right:1px solid #e8e2d4; display:flex; flex-direction:column; flex-shrink:0; }
.pro-side .brand{ padding:16px 14px; border-bottom:1px solid #e8e2d4; display:flex; align-items:center; gap:10px; }
.pro-side .brand .logo{ width:34px; height:34px; border-radius:10px; background:#074045; color:#fff; display:flex; align-items:center; justify-content:center; font-family:'Fraunces',serif; font-weight:700; font-size:16px; flex-shrink:0; }
.pro-side .brand .nm{ font-family:'Fraunces',serif; font-size:14px; font-weight:700; color:#0f1a1c; letter-spacing:-0.01em; line-height:1.15; }
.pro-side .brand .sb{ font-size:10px; color:#5a6c6d; margin-top:1px; }
.pro-side .nav{ flex:1; padding:10px 7px; overflow-y:auto; }
.pro-side .sec{ font-size:9.5px; font-weight:700; color:#7a8588; letter-spacing:0.08em; text-transform:uppercase; padding:11px 9px 5px; }
.pro-side .item{ display:flex; align-items:center; gap:8px; padding:8px 9px; border-radius:8px; font-size:12px; color:#3a4548; font-weight:500; line-height:1.3; cursor:pointer; }
.pro-side .item .ic{ width:16px; height:16px; opacity:0.65; flex-shrink:0; }
.pro-side .item:hover{ background:rgba(7,64,69,0.06); color:#074045; }
.pro-side .item.on{ background:#074045; color:#fff; }
.pro-side .item.on .ic{ opacity:1; }
.pro-side .item.human{ background:#fff; border:1px solid #e8e2d4; margin-top:4px; color:#074045; font-weight:600; }
.pro-side .item.human .ic{ opacity:1; color:#074045; }
.pro-side .foot{ padding:11px 12px; border-top:1px solid #e8e2d4; display:flex; align-items:center; gap:9px; }
.pro-side .foot .av{ width:28px; height:28px; border-radius:50%; background:#fff; border:1px solid #e8e2d4; color:#074045; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; flex-shrink:0; }
.pro-side .foot .who{ font-size:11.5px; font-weight:600; color:#0f1a1c; line-height:1.2; }
.pro-side .foot .rl{ font-size:10px; color:#7a8588; }

/* Main column */
.pro-main{ flex:1; display:flex; flex-direction:column; min-width:0; background:#fff; position:relative; }
.pro-hdr{ padding:13px 16px; border-bottom:1px solid #e8e2d4; display:flex; align-items:center; gap:11px; flex-shrink:0; }
.pro-hdr .av{ width:36px; height:36px; border-radius:50%; background:#074045; color:#fff; display:flex; align-items:center; justify-content:center; font-family:'Fraunces',serif; font-size:14px; font-weight:700; position:relative; }
.pro-hdr .av::after{ content:''; position:absolute; bottom:-1px; right:-1px; width:11px; height:11px; border-radius:50%; background:#1ca672; border:2px solid #fff; }
.pro-hdr .nm{ font-family:'Fraunces',serif; font-size:14px; font-weight:700; color:#0f1a1c; letter-spacing:-0.01em; }
.pro-hdr .stt{ font-size:10.5px; color:#5a6c6d; display:flex; align-items:center; gap:5px; margin-top:1px; }
.pro-hdr .stt::before{ content:''; width:6px; height:6px; border-radius:50%; background:#1ca672; }
.pro-hdr .acts{ margin-left:auto; display:flex; gap:6px; align-items:center; }
.pro-hdr .lang{ display:flex; height:28px; border:1px solid #e8e2d4; border-radius:7px; overflow:hidden; font-size:10.5px; font-weight:600; }
.pro-hdr .lang span{ padding:0 10px; display:flex; align-items:center; color:#5a6c6d; }
.pro-hdr .lang span.on{ background:#074045; color:#fff; }
.pro-hdr .ic{ width:28px; height:28px; border-radius:7px; border:1px solid #e8e2d4; background:#fff; color:#5a6c6d; display:flex; align-items:center; justify-content:center; cursor:pointer; }
.pro-hdr .ic:hover{ background:#f6f2e8; }

.pro-trust{ padding:6px 16px; background:#eef7f5; font-size:10.5px; color:#16766f; display:flex; align-items:center; gap:6px; border-bottom:1px solid #d4e8e3; }
.pro-trust strong{ color:#074045; }

.pro-msgs{ flex:1; overflow-y:auto; padding:14px 16px; display:flex; flex-direction:column; gap:11px; background:#fff; }
.pro-comp{ border-top:1px solid #e8e2d4; padding:10px 12px; display:flex; gap:7px; align-items:center; flex-shrink:0; background:#fff; }
.pro-comp .inp{ flex:1; height:36px; padding:0 12px; border:1px solid #e8e2d4; border-radius:9px; font-size:12.5px; color:#0f1a1c; display:flex; align-items:center; }
.pro-comp .inp.placeholder{ color:#9aa5a8; }
.pro-comp .send{ height:36px; padding:0 14px; background:#074045; color:#fff; border-radius:9px; font-size:12px; font-weight:600; display:flex; align-items:center; gap:6px; }

/* Bubbles */
.pro-row{ display:flex; gap:7px; align-items:flex-end; }
.pro-row.u{ flex-direction:row-reverse; }
.pro-av{ width:24px; height:24px; border-radius:50%; background:#eef7f5; color:#074045; display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:700; flex-shrink:0; }
.pro-av.u{ background:#f0e6d2; color:#5a6c6d; }
.pro-av.op{ background:#fff3e0; color:#c2410c; }
.pro-bub{ background:#f6f2e8; border:1px solid #e8e2d4; border-radius:12px 12px 12px 3px; padding:9px 12px; font-size:12.5px; line-height:1.55; color:#0f1a1c; max-width:78%; }
.pro-row.u .pro-bub{ background:#074045; color:#fff; border-color:#074045; border-radius:12px 12px 3px 12px; }
.pro-bub strong{ color:#074045; }
.pro-row.u .pro-bub strong{ color:#bef264; }

.pro-dept{ display:inline-flex; align-items:center; gap:5px; padding:3px 8px; background:#eef7f5; color:#074045; border-radius:20px; font-size:10px; font-weight:600; margin-bottom:5px; }

.pro-src{ display:inline-flex; align-items:center; gap:5px; margin-top:6px; padding:4px 10px; background:#fff; border:1px solid #e8e2d4; border-radius:20px; font-size:10.5px; color:#0a5258; font-weight:500; }

.pro-typing{ display:flex; gap:4px; padding:2px 0; }
.pro-typing span{ width:6px; height:6px; border-radius:50%; background:#7a8588; animation:proBlink 1.4s infinite both; }
.pro-typing span:nth-child(2){ animation-delay:0.2s; }
.pro-typing span:nth-child(3){ animation-delay:0.4s; }
@keyframes proBlink{ 0%,80%,100%{ opacity:0.3;} 40%{ opacity:1;} }

/* Greeting */
.pro-greet{ padding:8px 0 6px; }
.pro-greet h2{ font-family:'Fraunces',serif; font-size:20px; font-weight:700; color:#0f1a1c; letter-spacing:-0.015em; margin:0 0 4px; }
.pro-greet p{ font-size:12px; color:#3a4548; line-height:1.55; margin:0; }
.pro-greet .row{ display:flex; gap:7px; margin-top:14px; flex-wrap:wrap; }
.pro-greet .chip{ background:#f6f2e8; border:1px solid #e8e2d4; padding:7px 11px; border-radius:8px; font-size:11.5px; color:#0f1a1c; font-weight:500; display:flex; gap:5px; align-items:center; }
.pro-greet .chip .ic{ font-size:13px; }

.pro-greet .feat{ margin-top:16px; padding:12px; background:#f6f2e8; border:1px solid #e8e2d4; border-radius:11px; display:flex; gap:11px; }
.pro-greet .feat .ic{ width:34px; height:34px; border-radius:9px; background:#074045; color:#fff; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.pro-greet .feat .ttl{ font-size:12.5px; font-weight:700; color:#0f1a1c; }
.pro-greet .feat .desc{ font-size:11px; color:#5a6c6d; line-height:1.45; margin-top:1px; }

/* Handover */
.pro-handover{ margin-top:4px; background:#fff; border:1px solid #f0c890; border-left:3px solid #ea7615; border-radius:10px; padding:11px 13px; }
.pro-handover .h{ display:flex; align-items:center; gap:7px; font-size:11.5px; font-weight:700; color:#c2410c; margin-bottom:7px; }
.pro-handover .h .ic{ width:22px; height:22px; border-radius:7px; background:#fff3e0; display:flex; align-items:center; justify-content:center; }
.pro-handover .dept-pill{ display:inline-flex; align-items:center; gap:5px; padding:3px 9px; background:#fff3e0; color:#c2410c; border-radius:20px; font-size:10.5px; font-weight:600; margin-bottom:7px; }
.pro-handover .note{ font-size:11.5px; color:#3a4548; line-height:1.5; }
.pro-handover .note strong{ color:#0f1a1c; }
.pro-handover .acts{ display:flex; gap:6px; margin-top:9px; padding-top:9px; border-top:1px dashed #e8e2d4; }
.pro-handover .btn-p{ background:#074045; color:#fff; padding:7px 13px; border-radius:7px; font-size:11px; font-weight:600; }
.pro-handover .btn-s{ background:#fff; color:#074045; padding:7px 13px; border-radius:7px; font-size:11px; font-weight:600; border:1px solid #074045; }

/* Modal */
.pro-overlay{ position:absolute; inset:0; background:rgba(15,26,28,0.55); backdrop-filter:blur(1px); display:flex; align-items:center; justify-content:center; padding:20px; z-index:10; }
.pro-modal{ background:#fff; border-radius:14px; width:100%; max-width:360px; box-shadow:0 20px 60px rgba(0,0,0,0.3); overflow:hidden; }
.pro-modal .head{ padding:18px 20px 6px; border-bottom:1px solid #e8e2d4; position:relative; }
.pro-modal .head .close{ position:absolute; right:14px; top:14px; width:26px; height:26px; border-radius:7px; background:#f6f2e8; color:#5a6c6d; display:flex; align-items:center; justify-content:center; }
.pro-modal .head h3{ font-family:'Fraunces',serif; font-size:18px; font-weight:700; color:#0f1a1c; margin:0 0 4px; letter-spacing:-0.015em; }
.pro-modal .head .sb{ font-size:11.5px; color:#5a6c6d; line-height:1.5; margin-bottom:14px; }
.pro-modal .body{ padding:14px 20px 18px; }
.pro-modal .field{ margin-bottom:11px; }
.pro-modal .field label{ display:block; font-size:10.5px; font-weight:600; color:#5a6c6d; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:5px; }
.pro-modal .field .inp{ width:100%; padding:10px 12px; border:1px solid #e8e2d4; border-radius:8px; font-size:13px; color:#0f1a1c; background:#fff; }
.pro-modal .field .inp.placeholder{ color:#9aa5a8; }
.pro-modal .field .inp.active{ border-color:#074045; box-shadow:0 0 0 3px rgba(7,64,69,0.08); }
.pro-modal .field-row{ display:flex; gap:8px; }
.pro-modal .field-row .field{ flex:1; }
.pro-modal .chips{ display:flex; flex-wrap:wrap; gap:5px; }
.pro-modal .chip{ padding:6px 10px; border:1px solid #e8e2d4; border-radius:20px; font-size:11px; color:#3a4548; }
.pro-modal .chip.on{ background:#074045; color:#fff; border-color:#074045; }
.pro-modal .submit{ width:100%; padding:11px; background:#074045; color:#fff; border-radius:9px; font-size:12.5px; font-weight:700; display:flex; align-items:center; justify-content:center; gap:6px; margin-top:5px; }
.pro-modal .consent{ font-size:10px; color:#7a8588; line-height:1.45; margin-top:11px; display:flex; gap:6px; align-items:flex-start; }
.pro-modal .consent .cb{ width:13px; height:13px; border-radius:3px; background:#074045; flex-shrink:0; margin-top:1px; display:flex; align-items:center; justify-content:center; color:#fff; font-size:8px; }
.pro-modal .consent a{ color:#074045; font-weight:600; }

/* Settings */
.pro-settings h4{ font-size:10.5px; font-weight:700; color:#5a6c6d; text-transform:uppercase; letter-spacing:0.06em; margin:0 0 8px; }
.pro-settings h4:not(:first-child){ margin-top:14px; }
.pro-settings .lang-cards{ display:grid; grid-template-columns:1fr 1fr; gap:7px; }
.pro-settings .lc{ padding:11px; border:1.5px solid #e8e2d4; border-radius:10px; position:relative; cursor:pointer; }
.pro-settings .lc.on{ border-color:#074045; background:#eef7f5; }
.pro-settings .lc .fg{ font-size:18px; }
.pro-settings .lc .nm{ font-size:12px; font-weight:700; color:#0f1a1c; margin-top:4px; }
.pro-settings .lc .sub{ font-size:10px; color:#5a6c6d; }
.pro-settings .lc .ck{ position:absolute; top:8px; right:8px; width:18px; height:18px; border-radius:50%; background:#074045; color:#fff; display:flex; align-items:center; justify-content:center; font-size:10px; }
.pro-settings .opt{ background:#f6f2e8; border-radius:10px; padding:10px 11px; display:flex; align-items:center; gap:10px; margin-bottom:6px; }
.pro-settings .opt .ic{ width:28px; height:28px; border-radius:8px; background:#fff; color:#5a6c6d; display:flex; align-items:center; justify-content:center; font-size:13px; flex-shrink:0; }
.pro-settings .opt .lb{ flex:1; font-size:12px; font-weight:600; color:#0f1a1c; line-height:1.2; }
.pro-settings .opt .sb{ font-size:10.5px; color:#7a8588; margin-top:1px; font-weight:400; }
.pro-settings .sw{ width:32px; height:18px; background:#074045; border-radius:20px; position:relative; flex-shrink:0; }
.pro-settings .sw::after{ content:''; position:absolute; right:2px; top:2px; width:14px; height:14px; border-radius:50%; background:#fff; }
.pro-settings .sw.off{ background:#cbd5e1; }
.pro-settings .sw.off::after{ left:2px; right:auto; }
.pro-settings .ftr{ font-size:10px; color:#7a8588; margin-top:12px; padding-top:10px; border-top:1px solid #e8e2d4; display:flex; justify-content:space-between; }
.pro-settings .ftr a{ color:#074045; font-weight:600; }
`;

function ProScreen({ screen }){
  React.useEffect(()=>{
    if(document.getElementById('pro-css')) return;
    const s=document.createElement('style'); s.id='pro-css'; s.textContent=proCss; document.head.appendChild(s);
  },[]);

  if(screen==='launcher') return <ProLauncher/>;
  return (
    <div className="pro-root">
      <div className="pro-shell">
        <ProSidebar screen={screen}/>
        <div className="pro-main">
          <ProHeader/>
          <div className="pro-trust">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#16766f" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>
            <span>პასუხები <strong>alte.edu.ge</strong>-ს ოფიციალური წყაროებიდან · არ ვიგონებთ ფაქტებს</span>
          </div>
          {screen==='greeting' && <ProGreeting/>}
          {screen==='chat' && <ProChat/>}
          {screen==='handover' && <ProHandover/>}
          {screen==='file' && <ProFile/>}
          {screen==='lead' && <ProLead/>}
          {screen==='settings' && <ProSettings/>}
          <ProComposer placeholder={screen==='greeting'}/>
        </div>
      </div>
    </div>
  );
}

function ProSidebar({ screen }){
  const active = screen==='chat' ? 'med' : screen==='handover' ? 'adm' : screen==='lead' ? 'adm' : 'adm';
  return (
    <nav className="pro-side">
      <div className="brand">
        <div className="logo">A</div>
        <div>
          <div className="nm">Alte Assistant</div>
          <div className="sb">AI · 6 დეპარტამენტი</div>
        </div>
      </div>
      <div className="nav">
        <div className="sec">მენიუ</div>
        <div className={"item"+(active==='adm'?' on':'')}>
          <svg className="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
          მიღება
        </div>
        <div className="item">
          <svg className="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          პროგრამები
        </div>
        <div className="item">
          <svg className="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><line x1="12" y1="6" x2="12" y2="18"/></svg>
          დაფინანსება
        </div>
        <div className="item">
          <svg className="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10 15 15 0 0 1 4-10z"/></svg>
          საერთ. სტუდენტები
        </div>
        <div className={"item"+(active==='med'?' on':'')}>
          <svg className="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
          მედიცინა · MD
        </div>

        <div className="sec">სხვა</div>
        <div className="item">
          <svg className="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V2H6.5A2.5 2.5 0 0 0 4 4.5z"/></svg>
          ბიბლიოთეკა
        </div>
        <div className="item">
          <svg className="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
          კარიერა
        </div>
        <div className="item">
          <svg className="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
          IT დახმარება
        </div>
        <div className="item human">
          <svg className="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1v-6h3z"/><path d="M3 19a2 2 0 0 0 2 2h1v-6H3z"/></svg>
          ცოცხალი ოპერატორი
        </div>
      </div>
      <div className="foot">
        <div className="av">N</div>
        <div>
          <div className="who">ნინო</div>
          <div className="rl">აბიტურიენტი</div>
        </div>
      </div>
    </nav>
  );
}

function ProHeader(){
  return (
    <div className="pro-hdr">
      <div className="av">A</div>
      <div>
        <div className="nm">Alte AI Assistant</div>
        <div className="stt">ონლაინ · Claude AI</div>
      </div>
      <div className="acts">
        <div className="lang"><span className="on">KA</span><span>EN</span></div>
        <div className="ic">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
        </div>
        <div className="ic">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h0a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h0a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v0a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        </div>
        <div className="ic">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </div>
      </div>
    </div>
  );
}

function ProComposer({ placeholder }){
  return (
    <div className="pro-comp">
      <div className={"inp "+(placeholder?'placeholder':'')}>{placeholder?'მკითხე პროგრამაზე, მიღებაზე, დაფინანსებაზე…':'როდის არის ჩარიცხვის ბოლო ვადა?'}</div>
      <div className="send">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        გაგზავნა
      </div>
    </div>
  );
}

function ProLauncher(){
  return (
    <div className="pro-root">
      <div className="pro-page">
        <div className="nav">
          <div className="nav-logo">Alte University</div>
          <div className="nav-items">
            <span>ჩვენ შესახებ</span>
            <span className="active">მიღება</span>
            <span>სწავლა</span>
            <span>სტუდენტებისთვის</span>
            <span>აბიტურიენტებისთვის</span>
          </div>
          <div className="nav-r">
            <span>EN</span>
            <span className="lang-on">KA</span>
            <span className="apply">აპლიკაცია</span>
          </div>
        </div>
        <div className="hero">
          <div className="eyebrow">მიღება 2026</div>
          <h1>აღმოაჩინე შენი მომავალი ალტეში.</h1>
          <p>24 წლის გამოცდილება. 4 სკოლა — ბიზნესი, სამართალი, საერთ. მედიცინა, IT. სრულად ავტორიზებული.</p>
          <div className="stats">
            <div className="stat"><div className="n">2,500+</div><div className="l">სტუდენტი</div></div>
            <div className="stat"><div className="n">45</div><div className="l">ქვეყანა</div></div>
            <div className="stat"><div className="n">4</div><div className="l">სკოლა</div></div>
          </div>
        </div>
        <div className="pic">
          <div className="qt">„ალტეში მე ვისწავლე — როგორ ვისწავლო. ეს ცხოვრებისეული უნარია."</div>
          <div className="by">— ლუკა, MD კურსდამთავრებული 2024</div>
        </div>

        <div className="pro-launcher">
          <div className="pill">
            <div className="av">A</div>
            <div className="tx">
              <div className="nm">Alte AI Assistant</div>
              <div className="sb">დაგვისვი ნებისმიერი კითხვა</div>
            </div>
            <div className="arr">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProGreeting(){
  return (
    <div className="pro-msgs">
      <div className="pro-greet">
        <h2>გამარჯობა, ნინო 👋</h2>
        <p>მე ვარ ალტეს AI ასისტენტი. სიდბარდან აირჩიე დეპარტამენტი ან პირდაპირ მომწერე კითხვა.</p>

        <div className="feat">
          <div className="ic">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/></svg>
          </div>
          <div>
            <div className="ttl">პოპულარული 2026</div>
            <div className="desc">MD პროგრამა · ბაკალავრიატის ვადები · საერთ. სტუდენტი · დაფინანსება</div>
          </div>
        </div>

        <div className="row">
          <div className="chip"><span className="ic">🎓</span>როგორ ჩავაბარო?</div>
          <div className="chip"><span className="ic">💰</span>რა ღირს სწავლა?</div>
        </div>
        <div className="row">
          <div className="chip"><span className="ic">🩺</span>MD პროგრამა</div>
          <div className="chip"><span className="ic">🌍</span>საერთ. სტუდენტებისთვის</div>
          <div className="chip"><span className="ic">📅</span>ჩარიცხვის ვადები</div>
        </div>
      </div>
    </div>
  );
}

function ProChat(){
  return (
    <div className="pro-msgs">
      <div className="pro-row u">
        <div className="pro-av u">ნ</div>
        <div className="pro-bub">MD პროგრამის შესახებ მინდა ინფო</div>
      </div>
      <div className="pro-row">
        <div className="pro-av">A</div>
        <div>
          <div className="pro-dept">🩺 მედიცინა · MD</div>
          <div className="pro-bub">
            <strong>Doctor of Medicine (MD)</strong> — 6-წლიანი ერთსაფეხურიანი პროგრამა.
            <br/><br/>
            • ხანგრძლივობა: <strong>6 წელი</strong><br/>
            • ენა: ინგლისური<br/>
            • წლიური საფასური: <strong>$5,500</strong><br/>
            • WHO/NCEQE აღიარებული
            <br/><br/>
            გინდა გავაგრძელო ჩარიცხვის პროცესზე?
            <div>
              <div className="pro-src">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                alte.edu.ge/ka/ertsafekhuriani-sameditsino-programebi-2
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="pro-row u">
        <div className="pro-av u">ნ</div>
        <div className="pro-bub">და ჩარიცხვის ბოლო ვადა?</div>
      </div>
      <div className="pro-row">
        <div className="pro-av">A</div>
        <div className="pro-bub" style={{paddingRight:14}}>
          <div className="pro-typing"><span></span><span></span><span></span></div>
        </div>
      </div>
    </div>
  );
}

function ProHandover(){
  return (
    <div className="pro-msgs">
      <div className="pro-row u">
        <div className="pro-av u">ნ</div>
        <div className="pro-bub">გადამამისამართე ცოცხალ ოპერატორთან</div>
      </div>
      <div className="pro-row">
        <div className="pro-av">A</div>
        <div style={{maxWidth:'85%'}}>
          <div className="pro-bub">გესმის — გადაგრთავ <strong>მიღების</strong> გუნდის ცოცხალ ოპერატორთან.</div>
          <div className="pro-handover">
            <div className="h">
              <div className="ic">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#c2410c" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1v-6h3z"/><path d="M3 19a2 2 0 0 0 2 2h1v-6H3z"/></svg>
              </div>
              ოპერატორი ჩაერთო
            </div>
            <div className="dept-pill">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              მიღების ოფისი · Admissions
            </div>
            <div className="note">
              სამუშაო საათები: <strong>ორშ–პარ 09:00–18:00</strong>. ოპერატორი დაგიკავშირდება საშ. 3 სთ-ში. გსურს კონტაქტი დატოვო?
            </div>
            <div className="acts">
              <div className="btn-p">დიახ, კონტაქტი დავტოვო</div>
              <div className="btn-s">დაელოდე</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProLead(){
  return (
    <>
      <div className="pro-msgs" style={{filter:'blur(1.5px)',pointerEvents:'none'}}>
        <div className="pro-row">
          <div className="pro-av">A</div>
          <div className="pro-bub">დიდი მადლობა! მიღების გუნდი დაგიკავშირდება…</div>
        </div>
      </div>
      <div className="pro-overlay">
        <div className="pro-modal">
          <div className="head">
            <div className="close">×</div>
            <h3>დატოვე კონტაქტი</h3>
            <div className="sb">მიღების გუნდი დაგიკავშირდება 24 საათში. ვერ ჩავუტარებთ AI-ით სრულ პასუხს.</div>
          </div>
          <div className="body">
            <div className="field">
              <label>სახელი და გვარი</label>
              <div className="inp">ნინო კვარაცხელია</div>
            </div>
            <div className="field-row">
              <div className="field" style={{flex:1.5}}>
                <label>ტელეფონი</label>
                <div className="inp active">+995 599 12 34 56</div>
              </div>
              <div className="field">
                <label>ენა</label>
                <div className="inp">KA</div>
              </div>
            </div>
            <div className="field">
              <label>ელ.ფოსტა (არასავალდებულო)</label>
              <div className="inp placeholder">nino@example.com</div>
            </div>
            <div className="field">
              <label>ინტერესის სფერო</label>
              <div className="chips">
                <div className="chip">🎓 ბაკალავრი</div>
                <div className="chip on">🩺 MD</div>
                <div className="chip">🌍 საერთ.</div>
                <div className="chip">💰 დაფინ.</div>
              </div>
            </div>
            <div className="submit">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              გაგზავნა
            </div>
            <div className="consent">
              <div className="cb">✓</div>
              <div>ვეთანხმები <a>კონფიდენციალურობის პოლიტიკას</a>. ჩემი მონაცემები გამოყენებული იქნება მხოლოდ მიღების მიზნებისთვის.</div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function ProSettings(){
  return (
    <>
      <div className="pro-msgs" style={{filter:'blur(1.5px)',pointerEvents:'none'}}>
        <div className="pro-row">
          <div className="pro-av">A</div>
          <div className="pro-bub">გამარჯობა, ნინო. რით დაგეხმარო?</div>
        </div>
      </div>
      <div className="pro-overlay">
        <div className="pro-modal pro-settings">
          <div className="head">
            <div className="close">×</div>
            <h3>პარამეტრები</h3>
            <div className="sb">აირჩიე ენა, შეტყობინება და კონფიდენციალურობა</div>
          </div>
          <div className="body">
            <h4>ენა · Language</h4>
            <div className="lang-cards">
              <div className="lc on">
                <div className="ck">✓</div>
                <div className="fg">🇬🇪</div>
                <div className="nm">ქართული</div>
                <div className="sub">Georgian</div>
              </div>
              <div className="lc">
                <div className="fg">🇬🇧</div>
                <div className="nm">English</div>
                <div className="sub">International</div>
              </div>
            </div>

            <h4>გამოცდილება</h4>
            <div className="opt">
              <div className="ic">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
              </div>
              <div style={{flex:1}}>
                <div className="lb">წყაროების ბმულები</div>
                <div className="sb">alte.edu.ge ბმული ყოველ პასუხთან</div>
              </div>
              <div className="sw"></div>
            </div>
            <div className="opt">
              <div className="ic">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
              </div>
              <div style={{flex:1}}>
                <div className="lb">დაბრუნების შეტყობინება</div>
                <div className="sb">თუ ოპერატორი დაგიკავშირდება</div>
              </div>
              <div className="sw"></div>
            </div>
            <div className="opt">
              <div className="ic">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
              </div>
              <div style={{flex:1}}>
                <div className="lb">მუქი თემა</div>
                <div className="sb">თვალისთვის უფრო კომფორტული</div>
              </div>
              <div className="sw off"></div>
            </div>

            <h4>კონფიდენციალურობა</h4>
            <div className="opt">
              <div className="ic">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-2 14a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L5 6"/></svg>
              </div>
              <div style={{flex:1}}>
                <div className="lb">საუბრის ისტორიის წაშლა</div>
                <div className="sb">ყველა შეტყობინება წაიშლება</div>
              </div>
              <div style={{color:'#c2410c',fontSize:11.5,fontWeight:700}}>წაშლა</div>
            </div>
            <div className="ftr">
              <span>v2.0 · Claude AI</span>
              <a>კონფიდენციალურობის პოლიტიკა</a>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function ProFile(){
  return (
    <div className="pro-msgs">
      <div className="pro-row u">
        <div className="pro-av u">ნ</div>
        <div style={{maxWidth:'82%'}}>
          <div style={{background:'#074045',borderRadius:'12px 12px 3px 12px',padding:6,marginBottom:5}}>
            <div style={{background:'#fff',borderRadius:8,padding:'8px 10px',display:'flex',gap:9,alignItems:'center'}}>
              <div style={{width:32,height:40,background:'#c2410c',borderRadius:5,display:'flex',alignItems:'center',justifyContent:'center',color:'#fff',fontSize:8,fontWeight:800,flexShrink:0}}>PDF</div>
              <div style={{flex:1,minWidth:0}}>
                <div style={{fontSize:11.5,fontWeight:700,color:'#0f1a1c',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>atestati_2024.pdf</div>
                <div style={{fontSize:10,color:'#7a8588'}}>456 KB · 2 გვერდი</div>
              </div>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#1ca672" strokeWidth="2.6" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
          </div>
          <div className="pro-bub">ჩემი ატესტატია. MD-ში ჩაბარება შემიძლია?</div>
        </div>
      </div>

      <div className="pro-row">
        <div className="pro-av">A</div>
        <div style={{maxWidth:'82%'}}>
          <div className="pro-dept">🎓 მიღება</div>
          <div className="pro-bub">
            გამოვიკვლიე. შენი ატესტატი მოერგება <strong>MD პროგრამის</strong> მოთხოვნებს.
            <br/><br/>
            ანალიზი (3 პარამეტრი):<br/>
            • GPA: <strong>3.7 / 4.0</strong> — დამაკმაყოფილებელი<br/>
            • ბიოლოგია/ქიმია: <strong>ადეკვატური დონე</strong><br/>
            • ინგლისური: <strong>B2+ დასადასტურებად</strong>
            <br/><br/>
            გინდა, გავაგრძელო აპლიკაციის ჩაბარებაზე?
            <div>
              <div className="pro-src">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                alte.edu.ge/ka/migebis-pirobebi
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { ProScreen });
