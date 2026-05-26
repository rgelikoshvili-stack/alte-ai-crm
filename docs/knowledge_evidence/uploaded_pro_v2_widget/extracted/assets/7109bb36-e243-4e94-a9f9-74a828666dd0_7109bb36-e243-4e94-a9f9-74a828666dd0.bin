// PRO V2 — interactive chat widget with real Claude responses.
// All CSS lives in a single injected stylesheet using CSS variables tweaked by the host.

const { useState, useEffect, useRef, useMemo, useCallback } = React;

const proV2Css = `
.cw{ font-family:'Noto Sans Georgian','Inter',sans-serif; color:var(--alte-ink); }
.cw, .cw *{ box-sizing:border-box; }

/* ============ Floating chat window ============ */
.cw-win{
  position:fixed; right:22px; bottom:22px;
  width:min(94vw,420px); height:min(92vh,680px);
  background:var(--alte-panel); border-radius:18px;
  box-shadow:0 24px 80px -10px rgba(7,32,36,0.35), 0 8px 20px -8px rgba(7,32,36,0.25);
  display:flex; flex-direction:column; overflow:hidden;
  transform-origin:bottom right;
  z-index:50;
  border:1px solid rgba(15,26,28,0.06);
}
.cw-win.expanded{
  width:min(96vw,980px); height:min(92vh,720px);
  right:auto; bottom:auto; left:50%; top:50%;
  transform:translate(-50%,-50%);
}
.cw-backdrop{ position:fixed; inset:0; background:rgba(15,26,28,0.45); backdrop-filter:blur(3px); z-index:45; }

.cw-shell{ display:flex; flex:1; min-height:0; }

/* ============ Sidebar ============ */
.cw-side{
  width:188px; background:var(--alte-paper); border-right:1px solid var(--alte-line);
  display:flex; flex-direction:column; flex-shrink:0;
  transition:width .25s ease;
}
.cw-win:not(.expanded) .cw-side{ display:none; }
.cw-side.collapsed{ width:54px; }
.cw-side .brand{ padding:14px 12px; border-bottom:1px solid var(--alte-line); display:flex; align-items:center; gap:9px; min-height:60px; }
.cw-side .brand .nm{ font-family:'Fraunces',serif; font-size:13.5px; font-weight:700; color:var(--alte-ink); letter-spacing:-0.01em; line-height:1.15; }
.cw-side .brand .sb{ font-size:9.5px; color:var(--alte-mute); margin-top:1px; }
.cw-side.collapsed .brand-text{ display:none; }
.cw-side.collapsed .brand{ justify-content:center; padding:14px 8px; }

.cw-side .nav{ flex:1; padding:8px 6px; overflow-y:auto; }
.cw-side .sec{ font-size:9px; font-weight:700; color:var(--alte-mute); letter-spacing:0.1em; text-transform:uppercase; padding:10px 9px 5px; opacity:.75; }
.cw-side.collapsed .sec{ display:none; }
.cw-side .item{ display:flex; align-items:center; gap:9px; padding:7px 9px; border-radius:8px; font-size:11.5px; color:var(--alte-ink); font-weight:500; line-height:1.25; cursor:pointer; position:relative; user-select:none; }
.cw-side .item .ic{ width:16px; height:16px; opacity:0.6; flex-shrink:0; display:flex; align-items:center; justify-content:center; }
.cw-side .item:hover{ background:rgba(7,64,69,0.06); }
.cw-side .item:hover .ic{ opacity:.85; }
.cw-side .item.on{ background:var(--alte-teal); color:#fff; }
.cw-side .item.on .ic{ opacity:1; }
.cw-side .item.on .badge{ background:rgba(255,255,255,0.18); color:#fff; }
.cw-side .item .badge{ margin-left:auto; font-size:9px; font-weight:700; padding:1px 6px; border-radius:9px; background:var(--alte-chip); color:var(--alte-mute); }
.cw-side .item.human{ margin:6px 0 2px; background:var(--alte-panel); border:1px solid var(--alte-line); color:var(--alte-teal); font-weight:600; }
.cw-side .item.human .ic{ opacity:1; color:var(--alte-teal); }
.cw-side .item.human:hover{ background:var(--alte-soft); border-color:var(--alte-soft-line); }
.cw-side.collapsed .item-text, .cw-side.collapsed .badge{ display:none; }
.cw-side.collapsed .item{ justify-content:center; padding:9px; }

.cw-side .foot{ padding:10px; border-top:1px solid var(--alte-line); display:flex; align-items:center; gap:9px; }
.cw-side .foot .av{ width:28px; height:28px; border-radius:50%; background:var(--alte-panel); border:1px solid var(--alte-line); color:var(--alte-teal); display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; flex-shrink:0; }
.cw-side .foot .who{ font-size:11.5px; font-weight:600; color:var(--alte-ink); line-height:1.15; }
.cw-side .foot .rl{ font-size:9.5px; color:var(--alte-mute); margin-top:1px; }
.cw-side.collapsed .foot-text{ display:none; }
.cw-side .toggler{ padding:0 6px 8px; }
.cw-side .toggler button{ width:100%; background:transparent; border:1px dashed var(--alte-line); border-radius:7px; height:24px; display:flex; align-items:center; justify-content:center; color:var(--alte-mute); cursor:pointer; }
.cw-side .toggler button:hover{ color:var(--alte-teal); border-color:var(--alte-soft-line); }

/* ============ Main column ============ */
.cw-main{ flex:1; display:flex; flex-direction:column; min-width:0; background:var(--alte-panel); position:relative; }

/* Header */
.cw-hdr{ padding:11px 14px; border-bottom:1px solid var(--alte-line); display:flex; align-items:center; gap:11px; flex-shrink:0; background:var(--alte-panel); position:relative; z-index:2; }
.cw-hdr .av{ position:relative; }
.cw-hdr .av .stat-dot{ position:absolute; bottom:-1px; right:-1px; width:10px; height:10px; border-radius:50%; background:var(--alte-success); border:2px solid var(--alte-panel); z-index:2; }
.cw-hdr .nm{ font-family:'Fraunces',serif; font-size:14px; font-weight:700; color:var(--alte-ink); letter-spacing:-0.01em; }
.cw-hdr .stt{ font-size:10.5px; color:var(--alte-mute); display:flex; align-items:center; gap:5px; margin-top:1px; }
.cw-hdr .stt::before{ content:''; width:5px; height:5px; border-radius:50%; background:var(--alte-success); animation:cwPulse 2.4s infinite; }
@keyframes cwPulse{ 0%,100%{opacity:1} 50%{opacity:.4} }
.cw-hdr .acts{ margin-left:auto; display:flex; gap:5px; align-items:center; }
.cw-hdr .lang{ display:flex; height:26px; border:1px solid var(--alte-line); border-radius:7px; overflow:hidden; font-size:10.5px; font-weight:700; }
.cw-hdr .lang button{ padding:0 9px; display:flex; align-items:center; color:var(--alte-mute); background:transparent; border:0; cursor:pointer; font-family:inherit; font-weight:700; }
.cw-hdr .lang button.on{ background:var(--alte-teal); color:#fff; }
.cw-hdr .ic{ width:28px; height:28px; border-radius:7px; border:1px solid var(--alte-line); background:var(--alte-panel); color:var(--alte-mute); display:flex; align-items:center; justify-content:center; cursor:pointer; transition:.15s; }
.cw-hdr .ic:hover{ background:var(--alte-soft); color:var(--alte-teal); border-color:var(--alte-soft-line); }
.cw-hdr .ic.danger:hover{ background:#fdf0e8; color:#c2410c; border-color:#fadbc8; }

/* Trust bar */
.cw-trust{ padding:6px 14px; background:var(--alte-soft); font-size:10.5px; color:var(--alte-teal-mid,#16766f); display:flex; align-items:center; gap:7px; border-bottom:1px solid var(--alte-soft-line); }
.cw-trust strong{ color:var(--alte-teal); font-weight:700; }

/* Messages */
.cw-msgs{ flex:1; overflow-y:auto; padding:14px 14px 8px; display:flex; flex-direction:column; gap:var(--gap); background:var(--alte-panel); scroll-behavior:smooth; }
.cw-msgs.empty{ padding-top:8px; }

.cw-row{ display:flex; gap:8px; align-items:flex-end; }
@keyframes cwMsg{ from{ transform:translateY(6px); opacity:0 } to{ transform:translateY(0); opacity:1 } }
.cw-row.u{ flex-direction:row-reverse; }
.cw-av{ width:26px; height:26px; border-radius:50%; background:var(--alte-soft); color:var(--alte-teal); display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:700; flex-shrink:0; overflow:hidden; }
.cw-av.u{ background:var(--alte-chip); color:var(--alte-mute); }
.cw-av.op{ background:#fff3e0; color:#c2410c; }
.cw-av img{ width:100%; height:100%; object-fit:cover; }

.cw-bub-wrap{ max-width:82%; display:flex; flex-direction:column; gap:6px; align-items:flex-start; }
.cw-row.u .cw-bub-wrap{ align-items:flex-end; }
.cw-bub{ background:var(--alte-chip); border:1px solid var(--alte-line); border-radius:var(--bub-r) var(--bub-r) var(--bub-r) 3px; padding:var(--bub); font-size:var(--msg-font); line-height:1.55; color:var(--alte-ink); word-wrap:break-word; overflow-wrap:anywhere; }
.cw-row.u .cw-bub{ background:var(--alte-teal); color:#fff; border-color:var(--alte-teal); border-radius:var(--bub-r) var(--bub-r) 3px var(--bub-r); }
.cw-bub strong{ font-weight:700; color:var(--alte-teal); }
.cw-row.u .cw-bub strong{ color:#bef264; }
.cw-bub em{ color:var(--alte-mute); }
.cw-bub ul, .cw-bub ol{ margin:6px 0; padding-left:18px; }
.cw-bub li{ margin:2px 0; }
.cw-bub code{ background:rgba(7,64,69,0.08); padding:1px 5px; border-radius:4px; font-family:'JetBrains Mono',monospace; font-size:11.5px; }
.cw-bub a{ color:var(--alte-teal); text-decoration:underline; text-underline-offset:2px; }
.cw-bub p{ margin:0; }
.cw-bub p + p{ margin-top:6px; }

.cw-dept{ display:inline-flex; align-items:center; gap:5px; padding:3px 9px; background:var(--alte-soft); color:var(--alte-teal); border-radius:20px; font-size:10px; font-weight:700; letter-spacing:0.01em; }
.cw-dept .dot{ width:5px; height:5px; border-radius:50%; background:currentColor; }

.cw-srcs{ display:flex; gap:5px; flex-wrap:wrap; }
.cw-src{ display:inline-flex; align-items:center; gap:5px; padding:4px 9px 4px 6px; background:var(--alte-panel); border:1px solid var(--alte-line); border-radius:20px; font-size:10.5px; color:var(--alte-teal-mid,#0a5258); font-weight:500; cursor:pointer; transition:.15s; max-width:100%; }
.cw-src:hover{ border-color:var(--alte-soft-line); background:var(--alte-soft); }
.cw-src .n{ width:14px; height:14px; border-radius:50%; background:var(--alte-teal); color:#fff; font-size:8.5px; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.cw-src .u{ white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:240px; }

.cw-msg-acts{ display:flex; gap:4px; margin-top:2px; opacity:0; transition:.15s; }
.cw-row:hover .cw-msg-acts{ opacity:1; }
.cw-msg-acts button{ width:22px; height:22px; border-radius:6px; background:transparent; border:0; color:var(--alte-mute); cursor:pointer; display:flex; align-items:center; justify-content:center; transition:.12s; }
.cw-msg-acts button:hover{ background:var(--alte-chip); color:var(--alte-teal); }
.cw-msg-acts button.on{ color:var(--alte-success); }
.cw-msg-acts button.bad.on{ color:#c2410c; }

.cw-typing{ display:flex; gap:4px; padding:8px 12px; background:var(--alte-chip); border:1px solid var(--alte-line); border-radius:var(--bub-r) var(--bub-r) var(--bub-r) 3px; align-self:flex-start; }
.cw-typing span{ width:6px; height:6px; border-radius:50%; background:var(--alte-mute); animation:cwBlink 1.3s infinite both; }
.cw-typing span:nth-child(2){ animation-delay:.15s; }
.cw-typing span:nth-child(3){ animation-delay:.3s; }
@keyframes cwBlink{ 0%,80%,100%{ opacity:.25; transform:translateY(0); } 40%{ opacity:1; transform:translateY(-2px); } }

/* Greeting */
.cw-greet{ padding:6px 0 4px; }
.cw-greet h2{ font-family:'Fraunces',serif; font-size:22px; font-weight:700; color:var(--alte-ink); letter-spacing:-0.018em; margin:0 0 6px; }
.cw-greet p{ font-size:12.5px; color:var(--alte-mute); line-height:1.55; margin:0; }
.cw-feat{ margin-top:14px; padding:11px 12px; background:var(--alte-paper); border:1px solid var(--alte-line); border-radius:11px; display:flex; gap:11px; align-items:center; cursor:pointer; transition:.15s; }
.cw-feat:hover{ background:var(--alte-soft); border-color:var(--alte-soft-line); }
.cw-feat .ic{ width:34px; height:34px; border-radius:9px; background:var(--alte-teal); color:#fff; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.cw-feat .ttl{ font-size:12.5px; font-weight:700; color:var(--alte-ink); }
.cw-feat .desc{ font-size:10.5px; color:var(--alte-mute); line-height:1.4; margin-top:2px; }
.cw-feat .arrow{ margin-left:auto; color:var(--alte-mute); }
.cw-hint{ font-size:11px; color:var(--alte-mute); margin:14px 2px 8px; font-weight:500; }
.cw-chips{ display:flex; gap:6px; flex-wrap:wrap; }
.cw-chip{ background:var(--alte-paper); border:1px solid var(--alte-line); padding:8px 12px; border-radius:9px; font-size:11.5px; color:var(--alte-ink); font-weight:500; display:flex; gap:6px; align-items:center; cursor:pointer; transition:.15s; text-align:left; line-height:1.3; }
.cw-chip:hover{ background:var(--alte-soft); border-color:var(--alte-soft-line); color:var(--alte-teal); transform:translateY(-1px); }
.cw-chip .em{ font-size:13px; }

/* Handover card */
.cw-handover{ background:var(--alte-panel); border:1px solid #f5cab4; border-left:3px solid #e8714e; border-radius:10px; padding:10px 12px; }
.cw-handover .h{ display:flex; align-items:center; gap:7px; font-size:11.5px; font-weight:700; color:#c2410c; margin-bottom:7px; }
.cw-handover .h .ic{ width:22px; height:22px; border-radius:7px; background:#fdf0e8; display:flex; align-items:center; justify-content:center; color:#c2410c; }
.cw-handover .dept-pill{ display:inline-flex; align-items:center; gap:5px; padding:3px 9px; background:#fdf0e8; color:#c2410c; border-radius:20px; font-size:10px; font-weight:700; margin-bottom:7px; }
.cw-handover .note{ font-size:11.5px; color:var(--alte-ink); line-height:1.5; }
.cw-handover .note strong{ color:var(--alte-ink); }
.cw-handover .acts{ display:flex; gap:6px; margin-top:9px; padding-top:9px; border-top:1px dashed var(--alte-line); }
.cw-btn-p{ background:var(--alte-teal); color:#fff; padding:7px 13px; border-radius:7px; font-size:11px; font-weight:700; border:0; cursor:pointer; font-family:inherit; }
.cw-btn-p:hover{ background:var(--alte-teal-deep); }
.cw-btn-s{ background:var(--alte-panel); color:var(--alte-teal); padding:7px 13px; border-radius:7px; font-size:11px; font-weight:700; border:1px solid var(--alte-teal); cursor:pointer; font-family:inherit; }
.cw-btn-s:hover{ background:var(--alte-soft); }

/* File attachment card (in user bubble) */
.cw-file{ background:var(--alte-teal); padding:6px; border-radius:var(--bub-r) var(--bub-r) 3px var(--bub-r); }
.cw-file .inner{ background:var(--alte-panel); border-radius:8px; padding:8px 10px; display:flex; gap:9px; align-items:center; }
.cw-file .ext{ width:30px; height:38px; border-radius:5px; display:flex; align-items:center; justify-content:center; color:#fff; font-size:8.5px; font-weight:800; flex-shrink:0; letter-spacing:0.04em; }
.cw-file .pdf{ background:#c2410c; }
.cw-file .docx{ background:#0a5258; }
.cw-file .img{ background:#7a5af8; }
.cw-file .name{ font-size:11.5px; font-weight:700; color:var(--alte-ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:180px; }
.cw-file .sub{ font-size:10px; color:var(--alte-mute); margin-top:1px; }
.cw-file .ok{ color:var(--alte-success); flex-shrink:0; }

/* Composer */
.cw-comp{ border-top:1px solid var(--alte-line); padding:9px 11px 10px; flex-shrink:0; background:var(--alte-panel); position:relative; }
.cw-comp .att-strip{ display:flex; gap:6px; flex-wrap:wrap; padding-bottom:7px; }
.cw-comp .att{ display:inline-flex; align-items:center; gap:6px; padding:4px 7px 4px 4px; background:var(--alte-soft); border:1px solid var(--alte-soft-line); border-radius:7px; font-size:10.5px; color:var(--alte-teal); font-weight:600; }
.cw-comp .att .ext{ width:18px; height:22px; border-radius:3px; font-size:6.5px; }
.cw-comp .att .rm{ width:14px; height:14px; border-radius:50%; background:rgba(7,64,69,0.15); display:flex; align-items:center; justify-content:center; cursor:pointer; }
.cw-comp .att .rm:hover{ background:rgba(7,64,69,0.25); }

.cw-comp .box{ display:flex; align-items:flex-end; gap:6px; background:var(--alte-panel); border:1px solid var(--alte-line); border-radius:13px; padding:5px 5px 5px 9px; transition:.15s; }
.cw-comp .box.focus{ border-color:var(--alte-teal); box-shadow:0 0 0 3px rgba(7,64,69,0.08); }
.cw-comp textarea{ flex:1; min-width:0; border:0; outline:0; resize:none; font-family:inherit; font-size:13px; line-height:1.45; padding:7px 4px; background:transparent; color:var(--alte-ink); max-height:120px; }
.cw-comp textarea::placeholder{ color:#9aa5a8; }
.cw-comp .tool{ width:30px; height:30px; border-radius:8px; background:transparent; color:var(--alte-mute); border:0; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:.12s; flex-shrink:0; }
.cw-comp .tool:hover{ background:var(--alte-chip); color:var(--alte-teal); }
.cw-comp .send{ width:32px; height:32px; border-radius:9px; background:var(--alte-teal); color:#fff; border:0; cursor:pointer; display:flex; align-items:center; justify-content:center; flex-shrink:0; transition:.15s; }
.cw-comp .send:disabled{ background:var(--alte-chip); color:var(--alte-mute); cursor:not-allowed; }
.cw-comp .send:not(:disabled):hover{ background:var(--alte-teal-deep); transform:translateY(-1px); }
.cw-comp .hint{ font-size:9.5px; color:var(--alte-mute); margin-top:6px; padding:0 6px; display:flex; align-items:center; gap:5px; }
.cw-comp .hint .dot{ width:3px; height:3px; border-radius:50%; background:var(--alte-mute); }
.cw-comp .hint .verified{ color:var(--alte-teal); font-weight:600; }

/* Drag overlay */
.cw-drag{ position:absolute; inset:0; background:rgba(7,64,69,0.85); display:flex; align-items:center; justify-content:center; flex-direction:column; gap:10px; z-index:30; pointer-events:none; color:#fff; backdrop-filter:blur(4px); border-radius:18px; }
.cw-drag .ic{ width:60px; height:60px; border-radius:14px; border:2.5px dashed rgba(255,255,255,0.5); display:flex; align-items:center; justify-content:center; }
.cw-drag h3{ font-family:'Fraunces',serif; font-size:18px; margin:0; }
.cw-drag p{ font-size:11.5px; opacity:0.8; margin:0; }

/* Attach menu popup */
.cw-attach-menu{ position:absolute; bottom:62px; left:14px; background:var(--alte-panel); border:1px solid var(--alte-line); border-radius:12px; box-shadow:0 12px 30px rgba(0,0,0,0.12); padding:6px; display:flex; flex-direction:column; gap:2px; z-index:20; min-width:170px; }
.cw-attach-menu button{ display:flex; align-items:center; gap:9px; padding:8px 10px; border-radius:7px; background:transparent; border:0; cursor:pointer; font-family:inherit; font-size:12px; color:var(--alte-ink); text-align:left; }
.cw-attach-menu button:hover{ background:var(--alte-chip); color:var(--alte-teal); }
.cw-attach-menu button .ic{ width:26px; height:26px; border-radius:7px; background:var(--alte-soft); color:var(--alte-teal); display:flex; align-items:center; justify-content:center; flex-shrink:0; }

/* Action confirm tooltip */
.cw-toast{ position:absolute; bottom:78px; left:50%; transform:translateX(-50%); background:var(--alte-teal-deep); color:#fff; padding:6px 12px; border-radius:7px; font-size:11px; font-weight:600; box-shadow:0 6px 16px rgba(0,0,0,0.15); z-index:25; pointer-events:none; }
`;

// Mini markdown → JSX. Supports # headers, **bold**, *italic*, [link](url), `code`, • bullets, line breaks.
function md(text){
  if (!text) return null;
  const lines = text.split('\n');
  const out = [];
  let buf = [];
  const flushList = () => {
    if (buf.length){
      out.push(<ul key={out.length}>{buf.map((l,i)=><li key={i}>{inline(l)}</li>)}</ul>);
      buf = [];
    }
  };
  lines.forEach((ln, i) => {
    const m = ln.match(/^\s*[•\-\*]\s+(.*)$/);
    if (m){ buf.push(m[1]); return; }
    const nm = ln.match(/^\s*(\d+)\.\s+(.*)$/);
    if (nm){ buf.push(nm[2]); return; }
    flushList();
    if (ln.trim() === ''){ out.push(<div key={'br'+i} style={{height:6}}/>); return; }
    const h = ln.match(/^(#{1,3})\s+(.*)$/);
    if (h){
      const Tag = h[1].length===1?'h3':h[1].length===2?'h4':'h5';
      out.push(<Tag key={i} style={{margin:'4px 0 6px',fontFamily:"'Fraunces',serif",fontWeight:700,fontSize:h[1].length===1?16:14,color:'var(--alte-teal)',letterSpacing:'-0.01em'}}>{inline(h[2])}</Tag>);
      return;
    }
    out.push(<p key={i}>{inline(ln)}</p>);
  });
  flushList();
  return out;
}
function inline(s){
  const parts = [];
  let i = 0, k = 0;
  const re = /\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)/g;
  let m;
  while ((m = re.exec(s)) !== null){
    if (m.index > i) parts.push(s.slice(i, m.index));
    if (m[1]) parts.push(<strong key={k++}>{m[1]}</strong>);
    else if (m[2]) parts.push(<em key={k++}>{m[2]}</em>);
    else if (m[3]) parts.push(<code key={k++}>{m[3]}</code>);
    else if (m[4]) parts.push(<a key={k++} href={m[5]} target="_blank" rel="noopener">{m[4]}</a>);
    i = m.index + m[0].length;
  }
  if (i < s.length) parts.push(s.slice(i));
  return parts;
}

// ============ Sidebar ============
function Sidebar({ S, lang, currentDept, setDept, collapsed, setCollapsed, onHuman }){
  const main = DEPTS.slice(0, 5);
  const other = DEPTS.slice(5);
  return (
    <nav className={"cw-side"+(collapsed?' collapsed':'')}>
      <div className="brand">
        <AlteMark size={32}/>
        <div className="brand-text">
          <div className="nm">{S.appName}</div>
          <div className="sb">{S.appSub}</div>
        </div>
      </div>
      <div className="nav">
        <div className="sec">{S.menu}</div>
        {main.map(d=>(
          <div key={d.id} className={"item"+(currentDept===d.id?' on':'')} onClick={()=>setDept(d.id)} title={d[lang.toLowerCase()]}>
            <span className="ic"><I name={d.icon} size={15}/></span>
            <span className="item-text">{d[lang.toLowerCase()]}</span>
          </div>
        ))}
        <div className="sec">{S.other}</div>
        {other.map(d=>(
          <div key={d.id} className={"item"+(currentDept===d.id?' on':'')} onClick={()=>setDept(d.id)} title={d[lang.toLowerCase()]}>
            <span className="ic"><I name={d.icon} size={15}/></span>
            <span className="item-text">{d[lang.toLowerCase()]}</span>
          </div>
        ))}
        <div className="item human" onClick={onHuman} title={S.liveOperator}>
          <span className="ic"><I name="headset" size={15} sw={2.2}/></span>
          <span className="item-text">{S.liveOperator}</span>
        </div>
      </div>
      <div className="toggler">
        <button onClick={()=>setCollapsed(!collapsed)} title={collapsed?'expand':'collapse'}>
          <I name={collapsed?'chev':'chevLeft'} size={12}/>
        </button>
      </div>
      <div className="foot">
        <div className="av">{(S.you||'N')[0]}</div>
        <div className="foot-text">
          <div className="who">{S.you}</div>
          <div className="rl">{S.youRole}</div>
        </div>
      </div>
    </nav>
  );
}

// ============ Header ============
function Header({ S, lang, setLang, onSettings, onNew, onClose, onExpand, expanded }){
  return (
    <div className="cw-hdr">
      <div className="av" style={{width:34,height:34}}>
        <AlteMark size={34}/>
        <div className="stat-dot"></div>
      </div>
      <div>
        <div className="nm">{S.appName}</div>
        <div className="stt">{S.online}</div>
      </div>
      <div className="acts">
        <div className="lang">
          <button className={lang==='KA'?'on':''} onClick={()=>setLang('KA')}>KA</button>
          <button className={lang==='EN'?'on':''} onClick={()=>setLang('EN')}>EN</button>
        </div>
        <button className="ic" title={S.new} onClick={onNew}><I name="refresh" size={13}/></button>
        <button className="ic" title={S.settings} onClick={onSettings}><I name="settings" size={13}/></button>
        <button className="ic" title={expanded?S.collapse:S.expand} onClick={onExpand}><I name={expanded?'collapse':'expand'} size={12}/></button>
        <button className="ic danger" title={S.close} onClick={onClose}><I name="x" size={13} sw={2.4}/></button>
      </div>
    </div>
  );
}

// ============ Source pill ============
function SourceChip({ n, url }){
  const handle = (e) => { e.preventDefault(); window.open(url.startsWith('http')?url:'https://'+url,'_blank','noopener'); };
  const trimmed = url.replace(/^https?:\/\//,'');
  return (
    <a className="cw-src" href="#" onClick={handle} title={url}>
      <span className="n">{n}</span>
      <span className="u">{trimmed}</span>
    </a>
  );
}

// ============ Bubble actions ============
function MsgActions({ S, onCopy, onRegen, onGood, onBad, vote }){
  return (
    <div className="cw-msg-acts">
      <button title={S.chatActions.copy} onClick={onCopy}><I name="copy" size={12}/></button>
      <button title={S.chatActions.regen} onClick={onRegen}><I name="rotate" size={12}/></button>
      <button title={S.chatActions.good} className={vote==='up'?'on':''} onClick={onGood}><I name="thumb" size={12}/></button>
      <button title={S.chatActions.bad} className={'bad '+(vote==='down'?'on':'')} onClick={onBad}><I name="thumb" size={12} style={{transform:'rotate(180deg)'}}/></button>
    </div>
  );
}

// ============ Single message ============
function Message({ msg, S, lang, onCopy, onRegen, onVote, onHandover }){
  if (msg.kind === 'handover') return <HandoverCard msg={msg} S={S} lang={lang} onYes={onHandover}/>;
  const isUser = msg.role === 'user';
  const dept = msg.deptId ? DEPTS.find(d=>d.id===msg.deptId) : null;
  return (
    <div className={"cw-row "+(isUser?'u':'')}>
      <div className={"cw-av "+(isUser?'u':'')}>
        {isUser ? (S.you||'ნ')[0] : <AlteMark size={26}/>}
      </div>
      <div className="cw-bub-wrap">
        {!isUser && dept && (
          <div className="cw-dept">
            <span className="dot"></span>
            {dept[lang.toLowerCase()]}
          </div>
        )}
        {msg.file && (
          <div className="cw-file" style={{padding:isUser?6:0,background:isUser?'var(--alte-teal)':'transparent'}}>
            <div className="inner">
              <div className={"ext "+ (msg.file.kind||'pdf')}>{(msg.file.kind||'PDF').toUpperCase()}</div>
              <div style={{flex:1,minWidth:0}}>
                <div className="name">{msg.file.name}</div>
                <div className="sub">{msg.file.size}</div>
              </div>
              <span className="ok"><I name="check" size={13} sw={2.6} style={{color:'var(--alte-success)'}}/></span>
            </div>
          </div>
        )}
        {msg.text && <div className="cw-bub">{md(msg.text)}</div>}
        {msg.sources && msg.sources.length>0 && (
          <div className="cw-srcs">
            {msg.sources.map((s,i)=><SourceChip key={i} n={i+1} url={s}/>)}
          </div>
        )}
        {!isUser && msg.text && (
          <MsgActions S={S} onCopy={()=>onCopy(msg)} onRegen={()=>onRegen(msg)}
            onGood={()=>onVote(msg.id,'up')} onBad={()=>onVote(msg.id,'down')} vote={msg.vote}/>
        )}
      </div>
    </div>
  );
}

function HandoverCard({ msg, S, lang, onYes }){
  return (
    <div className="cw-row">
      <div className="cw-av"><AlteMark size={26}/></div>
      <div className="cw-bub-wrap" style={{maxWidth:'92%'}}>
        <div className="cw-bub">{md(msg.text)}</div>
        <div className="cw-handover" style={{alignSelf:'stretch'}}>
          <div className="h">
            <div className="ic"><I name="headset" size={12} sw={2.2}/></div>
            {S.handoverTitle}
          </div>
          <div className="dept-pill">
            <I name="building" size={10} sw={2.2}/>
            {S.handoverDept}
          </div>
          <div className="note">
            {S.handoverHours}<strong>{S.handoverHoursVal}</strong>. {S.handoverWait}
          </div>
          <div className="acts">
            <button className="cw-btn-p" onClick={onYes}>{S.handoverYes}</button>
            <button className="cw-btn-s">{S.handoverNo}</button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============ Greeting ============
function Greeting({ S, onChip, onFeat }){
  return (
    <div className="cw-greet">
      <h2>{S.greetingTitle}</h2>
      <p>{S.greetingBody}</p>
      <div className="cw-feat" onClick={onFeat}>
        <div className="ic"><I name="spark" size={16} sw={2.2}/></div>
        <div style={{flex:1}}>
          <div className="ttl">{S.featTitle}</div>
          <div className="desc">{S.featDesc}</div>
        </div>
        <div className="arrow"><I name="chev" size={14} sw={2.4}/></div>
      </div>
      <div className="cw-hint">{S.emptyHint}</div>
      <div className="cw-chips">
        {S.quickReplies.map((q,i)=>(
          <button key={i} className="cw-chip" onClick={()=>onChip(q.text)}>
            <span className="em">{q.emoji}</span>
            <span>{q.text}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

// ============ Composer ============
function Composer({ S, value, setValue, onSend, onFile, attaching, removeAttach, disabled }){
  const ref = useRef(null);
  const [focus, setFocus] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(()=>{
    const ta = ref.current; if(!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(120, ta.scrollHeight) + 'px';
  },[value]);

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey){
      e.preventDefault();
      if ((value.trim() || attaching) && !disabled) onSend();
    }
  };

  return (
    <div className="cw-comp">
      {attaching && (
        <div className="att-strip">
          <div className="att">
            <div className={"ext pdf"} style={{width:18,height:22,borderRadius:3,display:'flex',alignItems:'center',justifyContent:'center',color:'#fff',fontSize:6.5,fontWeight:800,background:'#c2410c'}}>{(attaching.kind||'PDF').toUpperCase().slice(0,3)}</div>
            <span>{attaching.name}</span>
            <span className="rm" onClick={removeAttach}><I name="x" size={9} sw={2.6}/></span>
          </div>
        </div>
      )}
      <div className={"box"+(focus?' focus':'')}>
        <button className="tool" title={S.attach} onClick={()=>setMenuOpen(m=>!m)}>
          <I name="plus" size={16} sw={2.2}/>
        </button>
        <textarea
          ref={ref}
          value={value}
          onChange={e=>setValue(e.target.value)}
          onFocus={()=>setFocus(true)}
          onBlur={()=>setFocus(false)}
          onKeyDown={handleKey}
          placeholder={S.composerPh}
          rows={1}
        />
        <button className="tool" title={S.voice}>
          <I name="mic" size={15}/>
        </button>
        <button className="send" disabled={(!value.trim() && !attaching) || disabled} onClick={onSend} title={S.send}>
          <I name={disabled?'stop':'send'} size={14} sw={2.4}/>
        </button>
      </div>
      <div className="hint">
        <I name="lock" size={9} sw={2.2}/>
        <span className="verified">{S.poweredVerified}</span>
        <span className="dot"></span>
        <span>{S.composerHint}</span>
      </div>
      {menuOpen && (
        <div className="cw-attach-menu" onMouseLeave={()=>setMenuOpen(false)}>
          <button onClick={()=>{ onFile('pdf'); setMenuOpen(false); }}>
            <span className="ic"><I name="file" size={13}/></span>
            <span>PDF / Document</span>
          </button>
          <button onClick={()=>{ onFile('img'); setMenuOpen(false); }}>
            <span className="ic"><I name="upload" size={13}/></span>
            <span>Image / Screenshot</span>
          </button>
        </div>
      )}
    </div>
  );
}

// ============ Trust bar ============
function TrustBar({ S }){
  return (
    <div className="cw-trust">
      <I name="shield" size={11} sw={2.4}/>
      <span>{T(S.trust)}</span>
    </div>
  );
}

// =====================================================================
// MAIN WIDGET — stateful root
// =====================================================================
function ChatWidget({ S, lang, setLang, tweaks, onClose, expanded, setExpanded }){
  useEffect(()=>{
    if(document.getElementById('cw-css')) return;
    const s = document.createElement('style'); s.id = 'cw-css'; s.textContent = proV2Css;
    document.head.appendChild(s);
  },[]);

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [attaching, setAttaching] = useState(null);
  const [typing, setTyping] = useState(false);
  const [currentDept, setCurrentDept] = useState('admissions');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showLead, setShowLead] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [toast, setToast] = useState(null);
  const [settingsState, setSettingsState] = useState({ sources:true, notify:true, dark:false });
  const msgsRef = useRef(null);

  // scroll on new message
  useEffect(()=>{
    const el = msgsRef.current; if(!el) return;
    requestAnimationFrame(()=>{ el.scrollTop = el.scrollHeight; });
  },[messages, typing]);

  const flashToast = (msg) => {
    setToast(msg);
    setTimeout(()=>setToast(null), 1400);
  };

  const dept = DEPTS.find(d=>d.id===currentDept);

  // Build conversation for Claude
  const buildHistory = useCallback((extraUserMsg) => {
    const sys = altePrompt(lang, dept);
    const hist = messages
      .filter(m => m.role==='user' || m.role==='assistant')
      .filter(m => m.text)
      .map(m => ({ role:m.role, content: m.text + (m.file?` [user attached: ${m.file.name}]`:'') }));
    if (extraUserMsg) hist.push({ role:'user', content: extraUserMsg });
    return { system: sys, messages: hist };
  }, [messages, lang, dept]);

  // Guess sources from text (look for alte.edu.ge mentions, else default to dept page)
  const inferSources = (text, deptId) => {
    const out = [];
    const urlRe = /alte\.edu\.ge\/[^\s\)\]]+/gi;
    let m;
    while ((m = urlRe.exec(text)) !== null) {
      if (out.indexOf(m[0]) === -1) out.push(m[0]);
    }
    if (out.length === 0) {
      const defaultUrls = {
        admissions:'alte.edu.ge/ka/migebis-pirobebi',
        programs:'alte.edu.ge/ka/programebi',
        finance:'alte.edu.ge/ka/datsva-da-stipendia',
        international:'alte.edu.ge/en/international-students',
        medicine:'alte.edu.ge/ka/ertsafekhuriani-sameditsino-programebi-2',
        library:'alte.edu.ge/ka/biblioteka',
        career:'alte.edu.ge/ka/karieris-centri',
        it:'alte.edu.ge/ka/it-dakhmareba',
      };
      out.push(defaultUrls[deptId] || 'alte.edu.ge');
    }
    return out.slice(0,3);
  };

  // Detect intent: handover request, lead request
  const detectIntent = (text) => {
    const t = text.toLowerCase();
    const handoverKw = ['ოპერატორ','live operator','human','agent','ცოცხალ','რეალურ','დაკავშირ','contact me','speak to'];
    if (handoverKw.some(k=>t.includes(k))) return 'handover';
    return null;
  };

  // SEND
  const send = useCallback(async (overrideText) => {
    const text = (overrideText ?? input).trim();
    if (!text && !attaching) return;
    if (typing) return;

    const userMsg = {
      id: 'u'+Date.now(),
      role:'user',
      text: text || (lang==='KA'?'ჩემი ფაილია':'My file'),
      file: attaching || null,
    };
    setMessages(m => [...m, userMsg]);
    setInput('');
    const wasAttaching = attaching;
    setAttaching(null);

    // Handover intent?
    if (detectIntent(text) === 'handover'){
      setTyping(true);
      setTimeout(()=>{
        setTyping(false);
        setMessages(m => [...m, {
          id:'a'+Date.now(),
          role:'assistant',
          kind:'handover',
          deptId:'admissions',
          text: lang==='KA' ? 'გესმის — გადაგრთავ **მიღების** გუნდის ცოცხალ ოპერატორთან.' : "I'll connect you with a live operator from **Admissions**.",
        }]);
      }, 700);
      return;
    }

    setTyping(true);
    try {
      const built = buildHistory(text + (wasAttaching?` [attached: ${wasAttaching.name}]`:''));
      const reply = await window.claude.complete({
        system: built.system,
        messages: built.messages,
      });
      setTyping(false);
      const aId = 'a'+Date.now();
      setMessages(m => [...m, {
        id: aId,
        role:'assistant',
        text: reply,
        deptId: currentDept,
        sources: settingsState.sources ? inferSources(reply, currentDept) : [],
      }]);
    } catch (err) {
      setTyping(false);
      setMessages(m => [...m, {
        id:'a'+Date.now(),
        role:'assistant',
        text: lang==='KA' ? '😔 ბოდიში, ვერ ვუპასუხე. სცადე ისევ ან გადადი **ცოცხალ ოპერატორზე**.' : "😔 Sorry, couldn't reach the model. Try again or **talk to a live operator**.",
        deptId: currentDept,
      }]);
    }
  }, [input, attaching, typing, buildHistory, lang, currentDept, settingsState.sources]);

  // Voting + copy + regen
  const vote = (id, v) => setMessages(m => m.map(x => x.id===id ? {...x, vote: x.vote===v?null:v} : x));
  const copy = (m) => { navigator.clipboard?.writeText(m.text||''); flashToast(lang==='KA'?'დაკოპირდა':'Copied'); };
  const regen = async (m) => {
    const idx = messages.findIndex(x=>x.id===m.id);
    if (idx<0) return;
    // find last user msg before this
    let lastUser = null;
    for (let i=idx-1; i>=0; i--) if (messages[i].role==='user'){ lastUser = messages[i]; break; }
    if (!lastUser) return;
    setMessages(messages.slice(0, idx));
    setTyping(true);
    try{
      const histBeforeUser = messages.slice(0, idx).filter(x=>x.role==='user'||x.role==='assistant').map(x=>({role:x.role, content:x.text||''}));
      const reply = await window.claude.complete({ system: altePrompt(lang, dept), messages: histBeforeUser });
      setTyping(false);
      setMessages(m => [...m, { id:'a'+Date.now(), role:'assistant', text: reply, deptId: currentDept, sources: settingsState.sources?inferSources(reply,currentDept):[] }]);
    } catch (e){ setTyping(false); }
  };

  // File pick (mocked — actual upload not supported in sandbox)
  const pickFile = (kind) => {
    const fake = {
      pdf: { name:'atestati_2024.pdf', size:'456 KB · 2 '+ (lang==='KA'?'გვერდი':'pages'), kind:'pdf' },
      img: { name:'transcript-photo.jpg', size:'1.2 MB · IMG', kind:'img' },
    };
    setAttaching(fake[kind]);
  };

  // Drag-drop handlers
  const onDragOver = (e) => { e.preventDefault(); setDragOver(true); };
  const onDragLeave = (e) => { e.preventDefault(); setDragOver(false); };
  const onDrop = (e) => { e.preventDefault(); setDragOver(false); pickFile('pdf'); };

  // Sidebar handlers
  const setDept = (id) => {
    setCurrentDept(id);
    const d = DEPTS.find(x=>x.id===id);
    if (!d) return;
    // If there's an open chat, drop a system context line; otherwise just set context
    if (messages.length > 0){
      const note = (lang==='KA'?'მზად ვარ ':'Switched to ')+d[lang.toLowerCase()]+'.';
      setMessages(m => [...m, { id:'sys'+Date.now(), role:'assistant', text:note, deptId:id, sources:[] }]);
    }
  };

  const startHandover = () => {
    setMessages(m => [...m, {
      id:'u'+Date.now(),
      role:'user',
      text: lang==='KA' ? 'გადამამისამართე ცოცხალ ოპერატორთან' : 'Connect me with a live operator',
    }]);
    setTimeout(()=>{
      setMessages(m => [...m, {
        id:'a'+Date.now(),
        role:'assistant',
        kind:'handover',
        deptId:'admissions',
        text: lang==='KA' ? 'გესმის — გადაგრთავ **მიღების** გუნდის ცოცხალ ოპერატორთან.' : "I'll connect you with a live operator from **Admissions**.",
      }]);
    }, 500);
  };

  const newChat = () => {
    if (messages.length === 0) return;
    if (confirm(lang==='KA'?'საუბრის წაშლა?':'Clear conversation?')){
      setMessages([]);
    }
  };

  const onLeadSubmit = () => {
    setShowLead(false);
    setMessages(m => [...m, {
      id:'a'+Date.now(),
      role:'assistant',
      text: S.leadDone,
      deptId:'admissions',
    }]);
  };

  return (
    <>
      {expanded && <div className="cw-backdrop" onClick={()=>setExpanded(false)}/>}
      <div className={"cw-win"+(expanded?' expanded':'')}
         onDragOver={onDragOver}
         onDragLeave={onDragLeave}
         onDrop={onDrop}>
      <div className="cw-shell">
        {tweaks.showSidebar && <Sidebar S={S} lang={lang} currentDept={currentDept} setDept={setDept}
                                       collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed}
                                       onHuman={startHandover}/>}
        <div className="cw-main">
          <Header S={S} lang={lang} setLang={setLang}
            onClose={onClose} onSettings={()=>setShowSettings(true)} onNew={newChat}
            onExpand={()=>setExpanded(!expanded)} expanded={expanded}/>
          <TrustBar S={S}/>
          <div ref={msgsRef} className={"cw-msgs "+(messages.length===0?'empty':'')}>
            {messages.length === 0 && (
              <Greeting S={S}
                onChip={(t)=>send(t)}
                onFeat={()=>send(S.quickReplies[2].text)}/>
            )}
            {messages.map(m => (
              <Message key={m.id} msg={m} S={S} lang={lang}
                onCopy={copy} onRegen={regen} onVote={vote}
                onHandover={()=>setShowLead(true)}/>
            ))}
            {typing && (
              <div className="cw-row">
                <div className="cw-av"><AlteMark size={26}/></div>
                <div className="cw-typing"><span></span><span></span><span></span></div>
              </div>
            )}
          </div>
          <Composer S={S} value={input} setValue={setInput}
            onSend={()=>send()} onFile={pickFile}
            attaching={attaching} removeAttach={()=>setAttaching(null)}
            disabled={typing}/>
          {toast && <div className="cw-toast">{toast}</div>}
        </div>
      </div>

      {dragOver && (
        <div className="cw-drag">
          <div className="ic"><I name="upload" size={26} sw={2}/></div>
          <h3>{S.fileDrop}</h3>
          <p>{S.fileMax}</p>
        </div>
      )}

      {showSettings && <SettingsModal S={S} lang={lang} setLang={setLang}
        state={settingsState} setState={setSettingsState}
        onClear={()=>{ setMessages([]); setShowSettings(false); }}
        onClose={()=>setShowSettings(false)}/>}
      {showLead && <LeadModal S={S} lang={lang} onClose={()=>setShowLead(false)} onSubmit={onLeadSubmit}/>}
    </div>
    </>
  );
}

Object.assign(window, { ChatWidget });
