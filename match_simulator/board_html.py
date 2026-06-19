"""전술 상황판 HTML/JS 렌더러."""

from __future__ import annotations

import html
import json


def render_tactics_board_html(
    frames: list[dict] | None,
    scenario: str,
    *,
    edit_mode: bool = False,
    initial_pieces: list[dict] | None = None,
) -> str:
    frames_json = json.dumps(frames or [], ensure_ascii=False)
    pieces_json = json.dumps(initial_pieces or [], ensure_ascii=False)
    safe_scenario = html.escape(scenario)
    mode = "edit" if edit_mode else "play"

    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: "Segoe UI", sans-serif; background: #eef2ea; color: #1a1a1a;
  }}
  .wrap {{ padding: 12px; max-width: 920px; margin: 0 auto; }}
  .toolbar {{
    display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 10px;
  }}
  .toolbar button, .toolbar label.mode {{
    border: 2px solid #1a1a1a; background: #fff; padding: 6px 12px;
    font-weight: 700; cursor: pointer; border-radius: 4px; font-size: 12px;
  }}
  .toolbar button.primary {{ background: #e02020; color: #fff; border-color: #e02020; }}
  .toolbar button.active {{ background: #1a1a1a; color: #fff; }}
  .toolbar label.mode {{ display: inline-flex; align-items: center; gap: 6px; cursor: default; }}
  .pitch-wrap {{ position: relative; }}
  .pitch {{
    position: relative; width: 100%; aspect-ratio: 2 / 3; max-height: 620px;
    background: linear-gradient(90deg, #2d6a4f 0%, #40916c 50%, #2d6a4f 100%);
    border: 4px solid #1a1a1a; border-radius: 8px; overflow: hidden;
    box-shadow: 8px 8px 0 #1a1a1a; touch-action: none;
  }}
  .pitch.editing {{ cursor: crosshair; }}
  .line {{ position: absolute; pointer-events: none; }}
  .center-line {{ left: 0; right: 0; top: 50%; height: 0; border-top: 2px solid rgba(255,255,255,0.55); }}
  .center-circle {{
    position: absolute; width: 18%; aspect-ratio: 1; border: 2px solid rgba(255,255,255,0.55);
    border-radius: 50%; left: 41%; top: 41%;
  }}
  .pen-area {{
    position: absolute; left: 25%; right: 25%; height: 16%; border: 2px solid rgba(255,255,255,0.35);
    pointer-events: none;
  }}
  .pen-top {{ top: 0; border-top: none; }}
  .pen-bottom {{ bottom: 0; border-bottom: none; }}
  #arrowLayer {{
    position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; z-index: 15;
  }}
  .piece {{
    position: absolute; transform: translate(-50%, -50%);
    min-width: 54px; max-width: 82px; padding: 4px 6px;
    border-radius: 999px; text-align: center; font-size: 10px; font-weight: 800;
    border: 2px solid #1a1a1a; box-shadow: 2px 2px 0 rgba(0,0,0,0.35);
    transition: left 0.85s ease, top 0.85s ease, opacity 0.35s ease, filter 0.35s ease;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; z-index: 10;
    user-select: none;
  }}
  .piece.kor {{ background: #e02020; color: #fff; }}
  .piece.mex {{ background: #059669; color: #fff; }}
  .piece.inactive {{ opacity: 0.2; filter: grayscale(0.9); }}
  .piece.injured {{
    background: #6b7280 !important; color: #fff; opacity: 0.55;
    border-style: dashed; text-decoration: line-through;
  }}
  .piece.injured::after {{
    content: "OUT"; position: absolute; right: -4px; top: -10px;
    font-size: 8px; background: #111; color: #fff; padding: 1px 4px; border-radius: 3px;
  }}
  .piece.subbed_out {{
    background: #9ca3af !important; color: #1f2937; opacity: 0.5;
    border-style: dotted;
  }}
  .piece.subbed_out::after {{
    content: "SUB"; position: absolute; right: -4px; top: -10px;
    font-size: 8px; background: #374151; color: #fff; padding: 1px 4px; border-radius: 3px;
  }}
  .piece.editable {{ cursor: grab; transition: box-shadow 0.15s; z-index: 30; }}
  .piece.editable:active {{ cursor: grabbing; box-shadow: 0 0 0 3px #fbbf24; }}
  .piece.dragging {{ transition: none; z-index: 40; }}
  .ball {{
    position: absolute; width: 12px; height: 12px; background: #fff;
    border: 2px solid #1a1a1a; border-radius: 50%; transform: translate(-50%, -50%);
    transition: left 0.65s ease, top 0.65s ease; z-index: 20;
    box-shadow: 0 0 8px rgba(255,255,255,0.8);
  }}
  .hud {{
    margin-top: 10px; padding: 10px; background: #fff; border: 2px solid #1a1a1a;
    border-radius: 6px; min-height: 56px;
  }}
  .minute {{ font-size: 11px; color: #666; font-weight: 700; }}
  .event {{ font-size: 14px; font-weight: 800; margin-top: 4px; }}
  .scenario {{ font-size: 11px; color: #555; margin-top: 6px; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 10px; font-size: 11px; margin-top: 8px; }}
  .legend span {{ display: inline-flex; align-items: center; gap: 4px; }}
  .dot {{ width: 10px; height: 10px; border-radius: 50%; border: 1px solid #111; }}
  .export-box {{
    margin-top: 10px; width: 100%; min-height: 72px; font-family: monospace; font-size: 11px;
    border: 2px solid #1a1a1a; border-radius: 6px; padding: 8px; display: none;
  }}
  .export-box.visible {{ display: block; }}
  @media (max-width: 640px) {{
    .piece {{ min-width: 44px; font-size: 9px; max-width: 68px; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <div class="toolbar">
    <button class="primary" id="playBtn">▶ 재생</button>
    <button id="pauseBtn">⏸ 일시정지</button>
    <button id="resetBtn">↺ 처음</button>
    <button id="editBtn">✋ 배치 편집</button>
    <button id="exportBtn" style="display:none;">📋 배치 JSON</button>
    <span id="stepInfo" style="font-size:12px;font-weight:700;margin-left:4px;"></span>
  </div>
  <div class="pitch-wrap">
    <div class="pitch" id="pitch">
      <div class="line center-line"></div>
      <div class="center-circle"></div>
      <div class="pen-area pen-top"></div>
      <div class="pen-area pen-bottom"></div>
      <svg id="arrowLayer" viewBox="0 0 100 100" preserveAspectRatio="none"></svg>
      <div id="ball" class="ball"></div>
    </div>
  </div>
  <div class="hud">
    <div class="minute" id="minute">0'</div>
    <div class="event" id="event">준비</div>
    <div class="scenario">상황: {safe_scenario}</div>
    <div class="legend">
      <span><i class="dot" style="background:#60a5fa"></i> 패스</span>
      <span><i class="dot" style="background:#f87171"></i> 슛/크로스</span>
      <span><i class="dot" style="background:#6b7280"></i> 부상 OUT</span>
      <span><i class="dot" style="background:#9ca3af"></i> 교체 SUB</span>
    </div>
  </div>
  <textarea class="export-box" id="exportBox" readonly placeholder="드래그 후 JSON 생성"></textarea>
</div>
<script>
const FRAMES = {frames_json};
const INITIAL_PIECES = {pieces_json};
const START_MODE = "{mode}";

let frameIndex = 0;
let playing = false;
let timer = null;
let editing = START_MODE === "edit";
const pitch = document.getElementById('pitch');
const ballEl = document.getElementById('ball');
const arrowLayer = document.getElementById('arrowLayer');
const pieceEls = {{}};
let dragState = null;

function pct(v) {{ return v + '%'; }}
function clamp(v, lo, hi) {{ return Math.max(lo, Math.min(hi, v)); }}

function pieceClass(p) {{
  let cls = 'piece ' + p.team;
  if (!p.active) cls += ' inactive';
  if (p.status === 'injured') cls += ' injured';
  else if (p.status === 'subbed_out') cls += ' subbed_out';
  if (editing && p.active !== false) cls += ' editable';
  return cls;
}}

function clearArrows() {{
  while (arrowLayer.firstChild) arrowLayer.removeChild(arrowLayer.firstChild);
}}

function drawArrows(arrows) {{
  clearArrows();
  if (!arrows || !arrows.length) return;
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  defs.innerHTML = `
    <marker id="arrowPass" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/>
    </marker>
    <marker id="arrowShot" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#f87171"/>
    </marker>`;
  arrowLayer.appendChild(defs);

  arrows.forEach(a => {{
    const color = (a.kind === 'pass') ? '#60a5fa' : '#f87171';
    const marker = (a.kind === 'pass') ? 'url(#arrowPass)' : 'url(#arrowShot)';
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', a.x1);
    line.setAttribute('y1', a.y1);
    line.setAttribute('x2', a.x2);
    line.setAttribute('y2', a.y2);
    line.setAttribute('stroke', color);
    line.setAttribute('stroke-width', a.kind === 'shot' ? '0.9' : '0.55');
    line.setAttribute('stroke-dasharray', a.kind === 'pass' ? '1.2 0.8' : 'none');
    line.setAttribute('marker-end', marker);
    line.setAttribute('opacity', '0.92');
    arrowLayer.appendChild(line);
  }});
}}

function ensurePieces(pieces) {{
  pieces.forEach(p => {{
    if (!pieceEls[p.id]) {{
      const el = document.createElement('div');
      el.className = pieceClass(p);
      el.id = 'piece-' + p.id;
      el.textContent = p.name;
      pitch.appendChild(el);
      pieceEls[p.id] = el;
      bindDrag(el, p.id);
    }}
    const el = pieceEls[p.id];
    el.className = pieceClass(p);
    el.textContent = p.name;
    el.style.left = pct(p.x);
    el.style.top = pct(p.y);
  }});
}}

function bindDrag(el, pid) {{
  el.addEventListener('pointerdown', (ev) => {{
    if (!editing) return;
    ev.preventDefault();
    dragState = {{ pid, el }};
    el.classList.add('dragging');
    el.setPointerCapture(ev.pointerId);
  }});
  el.addEventListener('pointermove', (ev) => {{
    if (!dragState || dragState.pid !== pid) return;
    const rect = pitch.getBoundingClientRect();
    const x = clamp(((ev.clientX - rect.left) / rect.width) * 100, 8, 92);
    const y = clamp(((ev.clientY - rect.top) / rect.height) * 100, 8, 92);
    dragState.el.style.left = pct(x);
    dragState.el.style.top = pct(y);
    dragState.x = x;
    dragState.y = y;
  }});
  el.addEventListener('pointerup', (ev) => {{
    if (!dragState || dragState.pid !== pid) return;
    dragState.el.classList.remove('dragging');
    dragState = null;
    el.releasePointerCapture(ev.pointerId);
  }});
}}

function collectLayout() {{
  const layout = {{}};
  Object.keys(pieceEls).forEach(id => {{
    const el = pieceEls[id];
    layout[id] = {{
      x: parseFloat(el.style.left),
      y: parseFloat(el.style.top),
    }};
  }});
  return layout;
}}

function renderFrame(idx) {{
  const frame = FRAMES[idx];
  if (!frame) return;
  ensurePieces(frame.pieces);
  ballEl.style.display = 'block';
  ballEl.style.left = pct(frame.ball[0]);
  ballEl.style.top = pct(frame.ball[1]);
  drawArrows(frame.arrows || []);
  document.getElementById('minute').textContent = frame.minute;
  document.getElementById('event').textContent = frame.label;
  document.getElementById('stepInfo').textContent = (idx + 1) + ' / ' + FRAMES.length;
}}

function renderEditLayout() {{
  clearArrows();
  ballEl.style.display = 'none';
  const pieces = INITIAL_PIECES.length ? INITIAL_PIECES : (FRAMES[0] ? FRAMES[0].pieces : []);
  ensurePieces(pieces);
  document.getElementById('minute').textContent = '편집';
  document.getElementById('event').textContent = '선수를 드래그해 배치한 뒤 JSON을 생성하세요';
  document.getElementById('stepInfo').textContent = pieces.length + '명';
}}

function setEditMode(on) {{
  editing = on;
  pause();
  pitch.classList.toggle('editing', on);
  document.getElementById('editBtn').classList.toggle('active', on);
  document.getElementById('exportBtn').style.display = on ? 'inline-block' : 'none';
  document.getElementById('playBtn').disabled = on;
  if (on) {{
    renderEditLayout();
  }} else if (FRAMES.length) {{
    renderFrame(frameIndex);
  }}
}}

function play() {{
  if (playing || editing || !FRAMES.length) return;
  playing = true;
  timer = setInterval(() => {{
    if (frameIndex >= FRAMES.length - 1) {{
      pause();
      return;
    }}
    frameIndex += 1;
    renderFrame(frameIndex);
  }}, 1400);
}}

function pause() {{
  playing = false;
  if (timer) clearInterval(timer);
}}

function reset() {{
  pause();
  frameIndex = 0;
  if (editing) renderEditLayout();
  else if (FRAMES.length) renderFrame(0);
}}

document.getElementById('playBtn').onclick = play;
document.getElementById('pauseBtn').onclick = pause;
document.getElementById('resetBtn').onclick = reset;
document.getElementById('editBtn').onclick = () => setEditMode(!editing);
document.getElementById('exportBtn').onclick = () => {{
  const json = JSON.stringify(collectLayout(), null, 2);
  const box = document.getElementById('exportBox');
  box.value = json;
  box.classList.add('visible');
  if (navigator.clipboard) navigator.clipboard.writeText(json).catch(() => {{}});
}};

if (START_MODE === 'edit' || !FRAMES.length) {{
  setEditMode(true);
}} else {{
  renderFrame(0);
  setTimeout(play, 700);
}}
</script>
</body>
</html>
"""


def render_board_editor_html(initial_pieces: list[dict], scenario: str = "") -> str:
    return render_tactics_board_html(None, scenario, edit_mode=True, initial_pieces=initial_pieces)
