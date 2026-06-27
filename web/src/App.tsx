import { useEffect, useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import type { Card, Payload } from './types'
import { AnimatedContent, BlurText, useSpotlight } from './effects'
import CircularGallery from './CircularGallery'

const BASE = import.meta.env.BASE_URL
const IMG = (f: string) => `${BASE}img/${f}.jpg`
const THUMB = (f: string) => `${BASE}thumb/${f}.jpg`
const SWIPE_CAP = 160

const ALL = '__ALL__'
const FAV = '__FAV__'

export default function App() {
  const [data, setData] = useState<Payload | null>(null)
  const [curEx, setCurEx] = useState<string>(ALL)
  const [q, setQ] = useState('')
  const [type, setType] = useState('')
  const [dyn, setDyn] = useState('')
  const [mat, setMat] = useState('')
  const [stat, setStat] = useState('')
  const [view, setView] = useState<'grid' | 'swipe'>('grid')
  const [sel, setSel] = useState<Card | null>(null)

  useEffect(() => {
    fetch(`${BASE}data/cards.json`)
      .then((r) => r.json())
      .then((p: Payload) => {
        setData(p)
        const first = p.ex_order.find((e) => p.cards.some((c) => c.ex === e))
        setCurEx(first ?? ALL)
      })
  }, [])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setSel(null)
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const dyns = useMemo(() => (data ? uniq(data.cards.map((c) => c.dynasty)) : []), [data])
  const mats = useMemo(() => (data ? uniq(data.cards.map((c) => c.material)) : []), [data])

  const list = useMemo(() => {
    if (!data) return []
    let l = data.cards.filter((c) => match(c, { q, type, dyn, mat, stat }))
    if (curEx === FAV) l = l.filter((c) => c.highlight)
    else if (curEx !== ALL) l = l.filter((c) => c.ex === curEx)
    if (curEx !== FAV)
      l = l.slice().sort((a, b) => (b.highlight ? 1 : 0) - (a.highlight ? 1 : 0))
    return l
  }, [data, curEx, q, type, dyn, mat, stat])

  if (!data) return <div style={{ padding: 40, color: 'var(--ink2)' }}>載入中…</div>

  const favCount = data.cards.filter((c) => c.highlight).length
  const walls = curEx !== ALL && curEx !== FAV ? data.walls.filter((w) => w.ex === curEx) : []
  const exName = curEx === FAV ? '★ 精選口袋名單' : curEx === ALL ? '全部展區' : curEx
  const sub = `共 ${data.meta.total_cards} 張卡片 · ${data.meta.exhibitions} 大展區 · 主展 龍藏經 · 暗櫃照片已自動補光 · 含 ${data.meta.video_cards} 則影片截圖補充`

  return (
    <>
      <header className="hd">
        <h1 className="serif">
          <BlurText text="故宮 速記導覽" /> <span className="d">· 2026.06.25</span>
        </h1>
        <div className="sub">{sub}</div>
      </header>

      <div className="wrap">
        <nav>
          <div className="lbl">展區</div>
          <NavItem label="全部展區" count={data.meta.total_cards} active={curEx === ALL} onClick={() => setCurEx(ALL)} />
          {favCount > 0 && (
            <NavItem label="★ 精選口袋名單" count={favCount} active={curEx === FAV} cls="fav-nav" onClick={() => setCurEx(FAV)} />
          )}
          {data.exhibitions.map((ex) => (
            <NavItem key={ex.key} label={ex.short} count={ex.count} active={ex.key === curEx} onClick={() => setCurEx(ex.key)} />
          ))}
        </nav>

        <main>
          <div className="toolbar">
            <input type="search" placeholder="搜尋名稱 / 描述 / 編號…" value={q} onChange={(e) => setQ(e.target.value)} />
            <select value={type} onChange={(e) => setType(e.target.value)}>
              <option value="">類型：全部</option>
              <option value="artifact">展品照</option>
              <option value="label_only">僅告示牌</option>
              <option value="principle">視覺原理</option>
            </select>
            <select value={dyn} onChange={(e) => setDyn(e.target.value)}>
              <option value="">朝代：全部</option>
              {dyns.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
            <select value={mat} onChange={(e) => setMat(e.target.value)}>
              <option value="">材質：全部</option>
              {mats.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
            <select value={stat} onChange={(e) => setStat(e.target.value)}>
              <option value="">狀態：全部</option>
              <option value="complete">已確認</option>
              <option value="pending_label">名稱待確認</option>
              <option value="partial">部分</option>
            </select>
            <button className="btn" onClick={() => { setQ(''); setType(''); setDyn(''); setMat(''); setStat('') }}>重設</button>
            <div className="viewtog">
              <button className={view === 'grid' ? 'on' : ''} onClick={() => setView('grid')}>▦ 網格</button>
              <button className={view === 'swipe' ? 'on' : ''} onClick={() => setView('swipe')}>↔ 滑覽</button>
            </div>
          </div>

          <AnimatedContent reKey={curEx}>
            <div className="exhead">
              <h2 className="serif">{exName}</h2>
              <div className="meta"><b>{list.length}</b> 張</div>
            </div>

            {walls.length > 0 && (
              <details className="walls">
                <summary>展區說明牆 · {walls.length}</summary>
                {walls.map((w) => (
                  <div className="wallrow" key={w.img}>
                    <img loading="lazy" src={IMG(w.img)} onClick={() => window.open(IMG(w.img), '_blank')} />
                    <div className="t"><b>{w.section}</b><br />{w.text.slice(0, 600)}</div>
                  </div>
                ))}
              </details>
            )}

            {list.length === 0 ? (
              <div className="empty">沒有符合條件的項目</div>
            ) : view === 'swipe' ? (
              <SwipeView list={list} onPick={setSel} />
            ) : (
              <div className="grid">
                {list.map((c) => <CardItem key={c.uid} c={c} onClick={() => setSel(c)} />)}
              </div>
            )}
          </AnimatedContent>
        </main>
      </div>

      <AnimatePresence>{sel && <Modal c={sel} onClose={() => setSel(null)} />}</AnimatePresence>
    </>
  )
}

function NavItem({ label, count, active, onClick, cls = '' }: { label: string; count: number; active: boolean; onClick: () => void; cls?: string }) {
  return (
    <div className={`navitem ${cls} ${active ? 'active' : ''}`} onClick={onClick}>
      <span>{label}</span><span className="c">{count}</span>
    </div>
  )
}

function badge(c: Card) {
  if (c.video) return <span className="badge b-vid">影片</span>
  if (c.type === 'principle') return <span className="badge b-pr">圖解</span>
  if (c.type === 'label_only') return <span className="badge b-partial">僅告示牌</span>
  if (c.status === 'pending_label') return <span className="badge b-pend">名稱待確認</span>
  return null
}

function CardItem({ c, onClick }: { c: Card; onClick: () => void }) {
  const { ref, onMove } = useSpotlight()
  return (
    <div ref={ref} onMouseMove={onMove} className={`card ${c.highlight ? 'is-fav' : ''}`} onClick={onClick}>
      <div className="spot" />
      <div className="imgwrap">
        {badge(c)}
        {c.highlight && <div className="fav">★</div>}
        <img loading="lazy" src={THUMB(c.images[0])} />
      </div>
      <div className="cbody">
        <div className="ctitle serif">{c.title}</div>
        <div className="chips">
          {c.dynasty && <span className="chip dyn">{c.dynasty}</span>}
          {c.material && <span className="chip mat">{c.material}</span>}
        </div>
        {c.museum_id && <div className="cmid">{c.museum_id}</div>}
      </div>
    </div>
  )
}

function SwipeView({ list, onPick }: { list: Card[]; onPick: (c: Card) => void }) {
  const capped = list.length > SWIPE_CAP
  const shown = capped ? list.slice(0, SWIPE_CAP) : list
  const items = useMemo(
    () => shown.map((c) => ({
      image: THUMB(c.images[0]),
      text: c.title.length > 16 ? c.title.slice(0, 16) + '…' : c.title,
    })),
    [shown],
  )
  return (
    <div className="swipe">
      <div className="swipe-hint">↔ 拖曳 / 滾輪 / 方向鍵滑覽　·　點圖看詳情　·　共 {shown.length} 件{capped ? `（已顯示前 ${SWIPE_CAP} 件，縮小展區或用篩選看其餘）` : ''}</div>
      <div className="swipe-stage">
        <CircularGallery
          items={items}
          bend={0}
          wobble={0}
          textColor="#2c2823"
          borderRadius={0.06}
          font='bold 24px "Noto Sans TC","Microsoft JhengHei",sans-serif'
          scrollEase={0.06}
          onItemClick={(i) => onPick(shown[i])}
        />
      </div>
      <div className="swipe-grid">
        {shown.map((c) => (
          <button key={c.uid} className="swipe-chip" onClick={() => onPick(c)}>
            {c.highlight ? '★ ' : ''}{c.title.length > 12 ? c.title.slice(0, 12) + '…' : c.title}
          </button>
        ))}
      </div>
    </div>
  )
}

function Modal({ c, onClose }: { c: Card; onClose: () => void }) {
  const npm = 'https://digitalarchive.npm.gov.tw/'
  const gq = encodeURIComponent(`${c.name_zh} ${c.museum_id || ''} 故宮`)
  return (
    <motion.div className="modal" onClick={(e) => e.target === e.currentTarget && onClose()}
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}>
      <div className="mclose" onClick={onClose}>×</div>
      <motion.div className="mbox" initial={{ opacity: 0, scale: 0.96, y: 12 }} animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.97 }} transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}>
        <div className="mimgs">
          {c.images.map((im) => <img key={im} src={IMG(im)} onClick={() => window.open(IMG(im), '_blank')} />)}
        </div>
        <div className="minfo">
          <h3 className="serif">{c.highlight && <span style={{ color: '#c79a2e' }}>★ </span>}{c.title}</h3>
          {c.name_en && <div className="en">{c.name_en}</div>}
          <div className="mrow">
            {c.dynasty && <span className="chip dyn">{c.dynasty}</span>}
            {c.material && <span className="chip mat">{c.material}</span>}
            {c.museum_id && <span className="chip">{c.museum_id}</span>}
            <span className="chip">{c.ex.split('｜')[0]}</span>
          </div>
          {c.desc && <div className="msec"><h4>說明 · OCR</h4><div className="mdesc">{c.desc}</div></div>}
          {c.notes && <div className="msec"><h4>備註</h4><div className="mnotes">{c.notes}</div></div>}
          {c.name_zh && !c.video && (
            <div className="mlinks">
              <a className="dlink" target="_blank" rel="noopener" href={`https://www.google.com/search?q=${gq}`}>🔎 深入查詢</a>
              <a className="dlink" target="_blank" rel="noopener" href={npm}>🏛️ 故宮典藏庫</a>
            </div>
          )}
          <div className="fns">展區：{c.section}{c.image_count > 1 ? `　·　${c.image_count} 圖` : ''}　·　來源：{c.images.join(', ')}</div>
        </div>
      </motion.div>
    </motion.div>
  )
}

function uniq(a: string[]) {
  return [...new Set(a.filter(Boolean))].sort()
}
function match(c: Card, f: { q: string; type: string; dyn: string; mat: string; stat: string }) {
  if (f.type) {
    if (f.type === 'artifact' && !(c.type === 'artifact' || c.type === 'mixed')) return false
    if (f.type !== 'artifact' && c.type !== f.type) return false
  }
  if (f.dyn && c.dynasty !== f.dyn) return false
  if (f.mat && c.material !== f.mat) return false
  if (f.stat) {
    if (f.stat === 'partial') { if (c.marker !== 'partial') return false }
    else if (c.status !== f.stat) return false
  }
  if (f.q) {
    const s = `${c.title} ${c.name_en} ${c.desc} ${c.museum_id} ${c.section}`.toLowerCase()
    if (!s.includes(f.q.toLowerCase())) return false
  }
  return true
}
