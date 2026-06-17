// Faux alte.edu.ge landing page as backdrop, with floating launcher + Chat widget.

const pageCss = `
.alte-page{ position:fixed; inset:0; background:var(--alte-page); overflow:hidden; display:flex; flex-direction:column; color:var(--alte-ink); }
.alte-page *{ box-sizing:border-box; }

/* Top nav */
.alte-nav{ height:64px; background:var(--alte-panel); border-bottom:1px solid var(--alte-line); display:flex; align-items:center; padding:0 28px; gap:24px; flex-shrink:0; }
.alte-nav .nav-items{ display:flex; gap:20px; font-size:13px; color:var(--alte-mute); font-weight:500; margin-left:8px; }
.alte-nav .nav-items span{ cursor:pointer; padding:6px 0; position:relative; }
.alte-nav .nav-items span:hover{ color:var(--alte-ink); }
.alte-nav .nav-items span.active{ color:var(--alte-teal); font-weight:700; }
.alte-nav .nav-items span.active::after{ content:''; position:absolute; left:0; right:0; bottom:-4px; height:2px; background:var(--alte-orange); border-radius:2px; }
.alte-nav .nav-r{ margin-left:auto; display:flex; gap:10px; align-items:center; font-size:12px; color:var(--alte-mute); }
.alte-nav .nav-r .lng{ display:flex; gap:2px; font-weight:700; padding:6px 10px; }
.alte-nav .nav-r .lng span{ cursor:pointer; padding:2px 4px; border-radius:4px; }
.alte-nav .nav-r .lng .on{ color:var(--alte-teal); }
.alte-nav .nav-r .apply{ background:var(--alte-teal); color:#fff; padding:10px 18px; border-radius:8px; font-weight:700; font-size:12px; cursor:pointer; transition:.15s; display:inline-flex; align-items:center; gap:6px; }
.alte-nav .nav-r .apply:hover{ background:var(--alte-teal-deep); transform:translateY(-1px); }

/* Hero */
.alte-hero{ flex:1; display:grid; grid-template-columns:1.05fr 1fr; gap:36px; padding:48px 56px 48px; min-height:0; overflow:hidden; }
.alte-hero .left{ display:flex; flex-direction:column; justify-content:center; max-width:540px; }
.alte-hero .eyebrow{ font-size:12px; font-weight:700; color:var(--alte-teal); letter-spacing:0.14em; text-transform:uppercase; margin-bottom:18px; display:inline-flex; align-items:center; gap:10px; }
.alte-hero .eyebrow::before{ content:''; width:28px; height:2px; background:var(--alte-orange); }
.alte-hero h1{ font-family:'Fraunces',serif; font-size:clamp(38px,5vw,64px); line-height:1.04; color:var(--alte-ink); font-weight:700; letter-spacing:-0.025em; margin:0 0 22px; text-wrap:balance; }
.alte-hero h1 em{ font-style:italic; color:var(--alte-teal); font-weight:600; }
.alte-hero p{ font-size:16px; color:var(--alte-mute); line-height:1.65; margin:0 0 32px; max-width:480px; }
.alte-hero .ctas{ display:flex; gap:11px; margin-bottom:36px; }
.alte-hero .cta-p{ background:var(--alte-teal); color:#fff; padding:13px 22px; border-radius:10px; font-weight:700; font-size:13.5px; display:inline-flex; align-items:center; gap:8px; cursor:pointer; transition:.18s; }
.alte-hero .cta-p:hover{ background:var(--alte-teal-deep); transform:translateY(-1px); }
.alte-hero .cta-s{ background:var(--alte-panel); color:var(--alte-ink); border:1px solid var(--alte-line); padding:13px 22px; border-radius:10px; font-weight:600; font-size:13.5px; display:inline-flex; align-items:center; gap:8px; cursor:pointer; transition:.15s; }
.alte-hero .cta-s:hover{ background:var(--alte-soft); color:var(--alte-teal); border-color:var(--alte-soft-line); }

.alte-hero .stats{ display:flex; gap:36px; padding-top:28px; border-top:1px solid var(--alte-line); }
.alte-hero .stat .n{ font-family:'Fraunces',serif; font-size:32px; font-weight:700; color:var(--alte-teal); line-height:1; letter-spacing:-0.02em; }
.alte-hero .stat .l{ font-size:11.5px; color:var(--alte-mute); margin-top:5px; font-weight:500; letter-spacing:0.04em; text-transform:uppercase; }

/* Right side — quote card */
.alte-hero .right{ position:relative; min-height:0; display:flex; align-items:stretch; }
.alte-hero .pic{
  width:100%;
  background:linear-gradient(165deg, var(--alte-teal) 0%, var(--alte-teal-mid) 50%, #16766f 100%);
  border-radius:24px;
  padding:32px;
  color:#fff;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
  position:relative;
  overflow:hidden;
  box-shadow:0 20px 50px -10px rgba(7,64,69,0.35);
}
.alte-hero .pic::before{
  content:''; position:absolute; right:-80px; top:-80px; width:260px; height:260px;
  background:radial-gradient(circle, rgba(232,113,78,0.35), transparent 70%);
  border-radius:50%;
  pointer-events:none;
}
.alte-hero .pic::after{
  content:''; position:absolute; left:-100px; bottom:-100px; width:300px; height:300px;
  background:radial-gradient(circle, rgba(255,255,255,0.08), transparent 70%);
  border-radius:50%;
  pointer-events:none;
}
.alte-hero .pic .badge{
  align-self:flex-start;
  padding:7px 13px;
  background:rgba(255,255,255,0.12);
  backdrop-filter:blur(6px);
  border:1px solid rgba(255,255,255,0.18);
  border-radius:24px;
  font-size:11px; font-weight:600;
  letter-spacing:0.06em; text-transform:uppercase;
  display:inline-flex; align-items:center; gap:7px;
  position:relative; z-index:1;
}
.alte-hero .pic .qt{
  font-family:'Fraunces',serif;
  font-size:clamp(22px,2.3vw,30px);
  font-weight:600;
  line-height:1.25;
  letter-spacing:-0.015em;
  position:relative; z-index:1;
}
.alte-hero .pic .qt::before{
  content:'"';
  font-family:'Fraunces',serif;
  font-size:90px;
  line-height:1;
  position:absolute; top:-30px; left:-10px;
  color:rgba(232,113,78,0.5);
  font-weight:700;
}
.alte-hero .pic .by{ font-size:12.5px; opacity:0.85; font-weight:500; position:relative; z-index:1; display:flex; align-items:center; gap:10px; }
.alte-hero .pic .by .av{ width:32px; height:32px; border-radius:50%; background:linear-gradient(135deg,#e8714e,#c2410c); display:flex; align-items:center; justify-content:center; font-weight:800; font-size:13px; font-family:'Inter'; }

/* Launcher */
.alte-launcher{ position:fixed; right:22px; bottom:22px; z-index:40; }
.alte-launcher .pulse{ position:absolute; inset:-6px; border-radius:30px; border:2px solid var(--alte-teal); opacity:0; animation:alPulse 2.4s ease-out infinite; pointer-events:none; }
@keyframes alPulse{ 0%{ transform:scale(.9); opacity:.6 } 80%{ transform:scale(1.15); opacity:0 } 100%{ opacity:0 } }
.alte-launcher button.pill{
  background:var(--alte-panel); border:1px solid var(--alte-line); border-radius:28px; padding:10px 16px 10px 11px;
  box-shadow:0 14px 36px -6px rgba(7,64,69,0.25), 0 4px 12px -4px rgba(7,64,69,0.15);
  display:flex; align-items:center; gap:11px; cursor:pointer; font-family:inherit;
  transition:.2s cubic-bezier(.2,.9,.25,1.05);
}
.alte-launcher button.pill:hover{ transform:translateY(-2px); box-shadow:0 20px 50px -6px rgba(7,64,69,0.35), 0 8px 14px -4px rgba(7,64,69,0.2); }
.alte-launcher .av{ position:relative; flex-shrink:0; }
.alte-launcher .av .stat-dot{ position:absolute; bottom:-1px; right:-1px; width:11px; height:11px; border-radius:50%; background:var(--alte-success); border:2px solid var(--alte-panel); z-index:2; }
.alte-launcher .tx{ text-align:left; }
.alte-launcher .nm{ font-size:12.5px; font-weight:700; color:var(--alte-ink); line-height:1.2; }
.alte-launcher .sb{ font-size:10.5px; color:var(--alte-mute); margin-top:1px; }
.alte-launcher .arr{ width:28px; height:28px; border-radius:50%; background:var(--alte-teal); color:#fff; display:flex; align-items:center; justify-content:center; }

/* When chat open, fade page slightly */
.alte-page.with-chat{ /* nothing dramatic; chat is offset */ }

/* Subtle particle / cream texture overlay */
.alte-tex{ position:absolute; inset:0; pointer-events:none; opacity:.5;
  background-image: radial-gradient(circle at 18% 28%, rgba(232,113,78,0.06) 0%, transparent 28%),
                    radial-gradient(circle at 85% 75%, rgba(7,64,69,0.06) 0%, transparent 32%);
}

/* Footer band */
.alte-foot{ height:48px; background:var(--alte-panel); border-top:1px solid var(--alte-line); display:flex; align-items:center; padding:0 28px; font-size:11px; color:var(--alte-mute); justify-content:space-between; flex-shrink:0; }
.alte-foot .l{ display:flex; gap:18px; align-items:center; }
.alte-foot a{ color:var(--alte-mute); text-decoration:none; cursor:pointer; }
.alte-foot a:hover{ color:var(--alte-teal); }
.alte-foot .badge{ display:inline-flex; align-items:center; gap:5px; padding:3px 8px; background:var(--alte-soft); border:1px solid var(--alte-soft-line); border-radius:5px; font-size:10px; color:var(--alte-teal); font-weight:600; }

/* Banner above launcher on first load */
.alte-tip{
  position:fixed; right:24px; bottom:78px; z-index:39;
  background:var(--alte-ink); color:#fff; padding:9px 12px 9px 14px;
  border-radius:12px; font-size:11.5px; font-weight:500; max-width:230px;
  box-shadow:0 12px 30px rgba(0,0,0,0.25);
  display:flex; align-items:center; gap:8px;
  line-height:1.4;
}
.alte-tip::after{
  content:''; position:absolute; right:40px; bottom:-6px;
  width:12px; height:12px; background:var(--alte-ink);
  transform:rotate(45deg);
}
.alte-tip .close{ background:rgba(255,255,255,0.1); border:0; color:#fff; width:18px; height:18px; border-radius:50%; cursor:pointer; display:flex; align-items:center; justify-content:center; }
.alte-tip .close:hover{ background:rgba(255,255,255,0.2); }
@keyframes tipIn{ from{ transform:translateY(8px); opacity:0 } to{ transform:translateY(0); opacity:1 } }
`;

function FauxNav({ S, lang, setLang }){
  return (
    <div className="alte-nav">
      <AlteLogo height={32}/>
      <div className="nav-items">
        {S.navItems.map((it,i)=>(
          <span key={i} className={i===1?'active':''}>{it}</span>
        ))}
      </div>
      <div className="nav-r">
        <div className="lng">
          <span className={lang==='EN'?'on':''} onClick={()=>setLang('EN')}>EN</span>
          <span style={{opacity:.4}}>/</span>
          <span className={lang==='KA'?'on':''} onClick={()=>setLang('KA')}>KA</span>
        </div>
        <div className="apply">
          {S.apply}
          <I name="arrow" size={12} sw={2.4}/>
        </div>
      </div>
    </div>
  );
}

function FauxHero({ S }){
  const split = S.pageTitle.split(' ');
  return (
    <div className="alte-hero">
      <div className="alte-tex"></div>
      <div className="left">
        <div className="eyebrow">{S.pageEyebrow}</div>
        <h1>{S.pageTitle}</h1>
        <p>{S.pageBody}</p>
        <div className="ctas">
          <div className="cta-p">{S.apply}<I name="arrow" size={13} sw={2.4}/></div>
          <div className="cta-s">{S.navItems[2]}<I name="chev" size={11} sw={2.4}/></div>
        </div>
        <div className="stats">
          <div className="stat"><div className="n">2,500<span style={{color:'var(--alte-orange)'}}>+</span></div><div className="l">{S.statStudents}</div></div>
          <div className="stat"><div className="n">45</div><div className="l">{S.statCountries}</div></div>
          <div className="stat"><div className="n">4</div><div className="l">{S.statSchools}</div></div>
        </div>
      </div>
      <div className="right">
        <div className="pic">
          <div className="badge">
            <I name="shield" size={11} sw={2.4}/>
            {S.quoteBadge}
          </div>
          <div className="qt">{S.quote}</div>
          <div className="by">
            <div className="av">ლ</div>
            <span>{S.quoteBy}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function FauxFooter({ S, lang }){
  return (
    <div className="alte-foot">
      <div className="l">
        <span>© 2026 Alte University</span>
        <a>{S.leadPrivacy}</a>
        <a>{lang==='KA'?'წესები':'Terms'}</a>
      </div>
      <div className="badge">
        <I name="shield" size={9} sw={2.4}/>
        {lang==='KA'?'WHO · NCEQE აღიარებული':'WHO · NCEQE recognized'}
      </div>
    </div>
  );
}

function Launcher({ S, onOpen }){
  return (
    <div className="alte-launcher">
      <span className="pulse"></span>
      <button className="pill" onClick={onOpen}>
        <div className="av">
          <AlteMark size={34}/>
          <span className="stat-dot"></span>
        </div>
        <div className="tx">
          <div className="nm">{S.launcherTitle}</div>
          <div className="sb">{S.launcherSub}</div>
        </div>
        <div className="arr"><I name="chev" size={13} sw={2.6}/></div>
      </button>
    </div>
  );
}

function Page({ tweaks, S, setTweak }){
  React.useEffect(()=>{
    if(document.getElementById('page-css')) return;
    const s = document.createElement('style'); s.id = 'page-css'; s.textContent = pageCss;
    document.head.appendChild(s);
  },[]);

  const [open, setOpen] = React.useState(tweaks.openOnLoad);
  const [expanded, setExpanded] = React.useState(true);
  const [showTip, setShowTip] = React.useState(false);

  React.useEffect(()=>{
    if (!open && !showTip){
      const t = setTimeout(()=>setShowTip(true), 600);
      return ()=>clearTimeout(t);
    }
  },[open, showTip]);

  const setLang = (v) => setTweak('lang', v);
  const lang = tweaks.lang;

  return (
    <div className={"alte-page"+(open?' with-chat':'')}>
      <FauxNav S={S} lang={lang} setLang={setLang}/>
      <FauxHero S={S}/>
      <FauxFooter S={S} lang={lang}/>

      {!open && (
        <>
          {showTip && (
            <div className="alte-tip">
              <I name="spark" size={13} sw={2.2} style={{color:'var(--alte-orange)',flexShrink:0}}/>
              <span>{lang==='KA'?'რამე გაინტერესებს? დაგვისვი კითხვა.':'Have questions? Ask us anything.'}</span>
              <button className="close" onClick={()=>setShowTip(false)}><I name="x" size={9} sw={2.6}/></button>
            </div>
          )}
          <Launcher S={S} onOpen={()=>{ setOpen(true); setShowTip(false); }}/>
        </>
      )}

      {open && (
        <ChatWidget
          S={S} lang={lang} setLang={setLang}
          tweaks={tweaks}
          onClose={()=>setOpen(false)}
          expanded={expanded} setExpanded={setExpanded}
        />
      )}
    </div>
  );
}

Object.assign(window, { Page });
