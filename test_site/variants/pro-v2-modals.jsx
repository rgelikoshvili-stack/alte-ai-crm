// Modals: Settings + Lead capture. Same modal CSS shared.

const modalCss = `
.cw-overlay{ position:absolute; inset:0; background:rgba(15,26,28,0.55); backdrop-filter:blur(2px); display:flex; align-items:center; justify-content:center; padding:16px; z-index:40; }
.cw-modal{ background:var(--alte-panel); border-radius:16px; width:100%; max-width:380px; box-shadow:0 24px 60px rgba(0,0,0,0.35); overflow:hidden; max-height:92%; display:flex; flex-direction:column; }
.cw-modal .head{ padding:16px 20px 12px; border-bottom:1px solid var(--alte-line); position:relative; flex-shrink:0; }
.cw-modal .head .close{ position:absolute; right:12px; top:12px; width:28px; height:28px; border-radius:8px; background:var(--alte-chip); color:var(--alte-mute); display:flex; align-items:center; justify-content:center; cursor:pointer; border:0; }
.cw-modal .head .close:hover{ background:var(--alte-soft); color:var(--alte-teal); }
.cw-modal .head h3{ font-family:'Fraunces',serif; font-size:18px; font-weight:700; color:var(--alte-ink); margin:0 0 4px; letter-spacing:-0.015em; }
.cw-modal .head .sb{ font-size:11.5px; color:var(--alte-mute); line-height:1.55; }
.cw-modal .body{ padding:14px 20px 18px; overflow-y:auto; }

.cw-modal .field{ margin-bottom:11px; }
.cw-modal .field label{ display:block; font-size:10px; font-weight:700; color:var(--alte-mute); text-transform:uppercase; letter-spacing:0.06em; margin-bottom:5px; }
.cw-modal .field .inp{ width:100%; padding:10px 12px; border:1px solid var(--alte-line); border-radius:9px; font-size:13px; color:var(--alte-ink); background:var(--alte-panel); font-family:inherit; outline:0; transition:.15s; }
.cw-modal .field .inp:focus{ border-color:var(--alte-teal); box-shadow:0 0 0 3px rgba(7,64,69,0.08); }
.cw-modal .field .inp::placeholder{ color:#9aa5a8; }
.cw-modal .field textarea.inp{ min-height:82px; resize:vertical; line-height:1.45; }
.cw-modal .field-row{ display:flex; gap:8px; }
.cw-modal .field-row .f1{ flex:1.6; }
.cw-modal .field-row .f2{ flex:1; }

.cw-modal .chips{ display:flex; flex-wrap:wrap; gap:5px; }
.cw-modal .chip{ padding:6px 11px; border:1px solid var(--alte-line); border-radius:20px; font-size:11px; color:var(--alte-ink); background:var(--alte-panel); cursor:pointer; transition:.12s; font-family:inherit; display:inline-flex; align-items:center; gap:5px; }
.cw-modal .chip:hover{ background:var(--alte-soft); }
.cw-modal .chip.on{ background:var(--alte-teal); color:#fff; border-color:var(--alte-teal); }

.cw-modal .submit{ width:100%; padding:12px; background:var(--alte-teal); color:#fff; border-radius:10px; font-size:13px; font-weight:700; display:flex; align-items:center; justify-content:center; gap:7px; margin-top:8px; border:0; cursor:pointer; font-family:inherit; transition:.15s; }
.cw-modal .submit:hover{ background:var(--alte-teal-deep); }
.cw-modal .submit:disabled{ opacity:.5; cursor:not-allowed; }

.cw-modal .consent{ font-size:10.5px; color:var(--alte-mute); line-height:1.5; margin-top:11px; display:flex; gap:7px; align-items:flex-start; cursor:pointer; }
.cw-modal .consent .cb{ width:14px; height:14px; border-radius:3.5px; background:var(--alte-panel); border:1.5px solid var(--alte-line); flex-shrink:0; margin-top:1px; display:flex; align-items:center; justify-content:center; color:#fff; transition:.12s; }
.cw-modal .consent.on .cb{ background:var(--alte-teal); border-color:var(--alte-teal); }
.cw-modal .consent a{ color:var(--alte-teal); font-weight:600; text-decoration:underline; }

/* Settings-specific */
.cw-settings h4{ font-size:10px; font-weight:700; color:var(--alte-mute); text-transform:uppercase; letter-spacing:0.08em; margin:0 0 8px; }
.cw-settings h4:not(:first-child){ margin-top:14px; }
.cw-settings .lang-cards{ display:grid; grid-template-columns:1fr 1fr; gap:7px; }
.cw-settings .lc{ padding:11px; border:1.5px solid var(--alte-line); border-radius:11px; position:relative; cursor:pointer; transition:.15s; background:var(--alte-panel); }
.cw-settings .lc:hover{ border-color:var(--alte-soft-line); background:var(--alte-soft); }
.cw-settings .lc.on{ border-color:var(--alte-teal); background:var(--alte-soft); }
.cw-settings .lc .fg{ font-size:20px; }
.cw-settings .lc .nm{ font-size:12px; font-weight:700; color:var(--alte-ink); margin-top:4px; }
.cw-settings .lc .sub{ font-size:10px; color:var(--alte-mute); }
.cw-settings .lc .ck{ position:absolute; top:8px; right:8px; width:18px; height:18px; border-radius:50%; background:var(--alte-teal); color:#fff; display:flex; align-items:center; justify-content:center; }
.cw-settings .opt{ background:var(--alte-paper); border-radius:11px; padding:10px 12px; display:flex; align-items:center; gap:11px; margin-bottom:6px; cursor:pointer; transition:.12s; }
.cw-settings .opt:hover{ background:var(--alte-soft); }
.cw-settings .opt .ic{ width:30px; height:30px; border-radius:9px; background:var(--alte-panel); color:var(--alte-mute); display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.cw-settings .opt.on .ic{ color:var(--alte-teal); }
.cw-settings .opt .lb{ flex:1; font-size:12px; font-weight:600; color:var(--alte-ink); line-height:1.2; }
.cw-settings .opt .sb{ font-size:10.5px; color:var(--alte-mute); margin-top:2px; font-weight:400; }
.cw-settings .sw{ width:34px; height:20px; background:var(--alte-teal); border-radius:20px; position:relative; flex-shrink:0; transition:.15s; }
.cw-settings .sw::after{ content:''; position:absolute; right:2px; top:2px; width:16px; height:16px; border-radius:50%; background:#fff; transition:.18s; box-shadow:0 1px 3px rgba(0,0,0,0.15); }
.cw-settings .sw.off{ background:#cbd5e1; }
.cw-settings .sw.off::after{ left:2px; right:auto; }
.cw-settings .danger-btn{ color:#c2410c; font-size:11.5px; font-weight:700; background:transparent; border:0; cursor:pointer; padding:6px 10px; border-radius:7px; font-family:inherit; }
.cw-settings .danger-btn:hover{ background:#fdf0e8; }
.cw-settings .ftr{ font-size:10px; color:var(--alte-mute); margin-top:14px; padding-top:11px; border-top:1px solid var(--alte-line); display:flex; justify-content:space-between; align-items:center; }
.cw-settings .ftr a{ color:var(--alte-teal); font-weight:600; text-decoration:none; }
.cw-settings .ftr a:hover{ text-decoration:underline; }
`;

function ensureModalCss(){
  if(document.getElementById('cw-modal-css')) return;
  const s=document.createElement('style'); s.id='cw-modal-css'; s.textContent=modalCss; document.head.appendChild(s);
}

const { useState: useState2 } = React;

function SettingsModal({ S, lang, setLang, state, setState, onClear, onClose }){
  React.useEffect(ensureModalCss,[]);
  const toggle = (k) => setState({...state, [k]:!state[k]});
  return (
    <div className="cw-overlay" onClick={onClose}>
      <div className="cw-modal cw-settings" onClick={e=>e.stopPropagation()}>
        <div className="head">
          <button className="close" onClick={onClose}><I name="x" size={13} sw={2.4}/></button>
          <h3>{S.settingsTitle}</h3>
          <div className="sb">{S.settingsSub}</div>
        </div>
        <div className="body">
          <h4>{S.settingsLang}</h4>
          <div className="lang-cards">
            <div className={"lc"+(lang==='KA'?' on':'')} onClick={()=>setLang('KA')}>
              {lang==='KA' && <div className="ck"><I name="check" size={10} sw={3}/></div>}
              <div className="fg">🇬🇪</div>
              <div className="nm">ქართული</div>
              <div className="sub">Georgian</div>
            </div>
            <div className={"lc"+(lang==='EN'?' on':'')} onClick={()=>setLang('EN')}>
              {lang==='EN' && <div className="ck"><I name="check" size={10} sw={3}/></div>}
              <div className="fg">🇬🇧</div>
              <div className="nm">English</div>
              <div className="sub">International</div>
            </div>
          </div>

          <h4>{S.settingsExp}</h4>
          <div className={"opt"+(state.sources?' on':'')} onClick={()=>toggle('sources')}>
            <div className="ic"><I name="link" size={15}/></div>
            <div style={{flex:1}}>
              <div className="lb">{S.optSources}</div>
              <div className="sb">{S.optSourcesSub}</div>
            </div>
            <div className={"sw"+(state.sources?'':' off')}></div>
          </div>
          <div className={"opt"+(state.notify?' on':'')} onClick={()=>toggle('notify')}>
            <div className="ic"><I name="bell" size={15}/></div>
            <div style={{flex:1}}>
              <div className="lb">{S.optNotify}</div>
              <div className="sb">{S.optNotifySub}</div>
            </div>
            <div className={"sw"+(state.notify?'':' off')}></div>
          </div>
          <div className={"opt"+(state.dark?' on':'')} onClick={()=>toggle('dark')}>
            <div className="ic"><I name="moon" size={15}/></div>
            <div style={{flex:1}}>
              <div className="lb">{S.optDark}</div>
              <div className="sb">{S.optDarkSub}</div>
            </div>
            <div className={"sw"+(state.dark?'':' off')}></div>
          </div>

          <h4>{S.settingsPriv}</h4>
          <div className="opt">
            <div className="ic"><I name="trash" size={15}/></div>
            <div style={{flex:1}}>
              <div className="lb">{S.optClear}</div>
              <div className="sb">{S.optClearSub}</div>
            </div>
            <button className="danger-btn" onClick={onClear}>{S.deleteWord}</button>
          </div>

          <div className="ftr">
            <span>{S.footVersion}</span>
            <a href="#" onClick={e=>e.preventDefault()}>{S.leadPrivacy}</a>
          </div>
        </div>
      </div>
    </div>
  );
}

function LeadModal({ S, lang, initialMessage='', onClose, onSubmit }){
  React.useEffect(ensureModalCss,[]);
  const [name, setName] = useState2('');
  const [phone, setPhone] = useState2('');
  const [email, setEmail] = useState2('');
  const [interest, setInterest] = useState2('md');
  const [message, setMessage] = useState2(initialMessage || '');
  const [consent, setConsent] = useState2(true);
  const valid = name.trim().length>1 && phone.trim().length>6 && consent;
  const items = [
    { id:'bsc',  ka:'🎓 ბაკალავრი',     en:'🎓 Bachelor' },
    { id:'md',   ka:'🩺 MD',           en:'🩺 MD' },
    { id:'intl', ka:'🌍 საერთ.',        en:'🌍 Intl.' },
    { id:'fin',  ka:'💰 დაფინ.',         en:'💰 Finance' },
  ];
  return (
    <div className="cw-overlay" onClick={onClose}>
      <div className="cw-modal" onClick={e=>e.stopPropagation()}>
        <div className="head">
          <button className="close" onClick={onClose}><I name="x" size={13} sw={2.4}/></button>
          <h3>{S.leadTitle}</h3>
          <div className="sb">{S.leadSub}</div>
        </div>
        <div className="body">
          <div className="field">
            <label>{S.leadName}</label>
            <input className="inp" value={name} onChange={e=>setName(e.target.value)}/>
          </div>
          <div className="field-row">
            <div className="field f1">
              <label>{S.leadPhone}</label>
              <input className="inp" value={phone} onChange={e=>setPhone(e.target.value)} type="tel"/>
            </div>
            <div className="field f2">
              <label>{S.settingsLang.split(' ')[0]}</label>
              <input className="inp" value={lang} readOnly style={{textAlign:'center',fontWeight:700}}/>
            </div>
          </div>
          <div className="field">
            <label>{S.leadEmail}</label>
            <input className="inp" value={email} onChange={e=>setEmail(e.target.value)}
              placeholder={lang==='KA'?'nino@example.com':'name@example.com'} type="email"/>
          </div>
          <div className="field">
            <label>{S.leadInterest}</label>
            <div className="chips">
              {items.map(it=>(
                <button key={it.id} className={"chip"+(interest===it.id?' on':'')} onClick={()=>setInterest(it.id)}>
                  {it[lang.toLowerCase()]}
                </button>
              ))}
            </div>
          </div>
          <div className="field">
            <label>{S.leadMessage}</label>
            <textarea
              className="inp"
              value={message}
              onChange={e=>setMessage(e.target.value)}
              placeholder={S.leadMessagePh}
              rows={3}
            />
          </div>
          <button className="submit" disabled={!valid} onClick={()=>onSubmit({ full_name:name, phone, email, interest, message, consent })}>
            <I name="send" size={13} sw={2.4}/>
            {S.leadSubmit}
          </button>
          <div className={"consent"+(consent?' on':'')} onClick={()=>setConsent(!consent)}>
            <div className="cb">{consent && <I name="check" size={9} sw={3.5}/>}</div>
            <div>{S.leadConsent}<a onClick={e=>e.preventDefault()}>{S.leadPrivacy}</a>.</div>
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { SettingsModal, LeadModal });
