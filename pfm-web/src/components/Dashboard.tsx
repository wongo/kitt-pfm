import { useState, useEffect } from 'react'

const API = (import.meta.env?.PUBLIC_API_URL as string) || ''

interface CategorySummary {
  category_id: string
  category_name: string
  category_icon: string
  total: number
  count: number
}

interface Transaction {
  id: string
  date: string
  amount: number
  currency: string
  category_name: string
  category_icon: string
  description: string
  merchant: string
}

interface MonthSummary {
  year: number
  month: number
  total: number
  by_category: CategorySummary[]
  transactions: Transaction[]
}

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function formatAmount(amount: number): string {
  if (amount >= 10000) {
    return `¥${(amount / 10000).toFixed(1)}萬`
  }
  return `¥${amount.toLocaleString()}`
}

export default function Dashboard() {
  const now = new Date()
  const [year, setYear] = useState(now.getFullYear())
  const [month, setMonth] = useState(now.getMonth() + 1)
  const [data, setData] = useState<MonthSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API}/api/summary/${year}/${month}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [year, month])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-[#ff2d2d] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <span className="text-[#888] text-sm">INITIALIZING DATA STREAM...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="kitt-box border-[#ff2d2d40] p-8 text-center">
        <div className="text-[#ff2d2d] text-xs mb-2">ERROR</div>
        <div className="text-[#e0e0e0]">{error}</div>
      </div>
    )
  }

  const maxCat = data?.by_category?.[0]?.total || 1

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-[#888] text-xs tracking-widest mb-1">SYSTEM STATUS: ONLINE</div>
          <h1 className="text-3xl font-bold text-[#e0e0e0]">
            <span className="text-[#ff2d2d] kitt-glow">KITT</span> PFM DASHBOARD
          </h1>
        </div>
        <div className="text-right">
          <div className="text-[#888] text-xs">SCAN MODE: ACTIVE</div>
          <div className="text-[#ff2d2d] text-sm">{MONTHS[month - 1]} {year}</div>
        </div>
      </div>

      {/* Month Navigator */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => { const m = month === 1 ? 12 : month - 1; const y = month === 1 ? year - 1 : year; setYear(y); setMonth(m); setLoading(true) }}
          className="px-4 py-2 bg-[#1a1a1a] border border-[#2a2a2a] text-[#888] hover:border-[#ff2d2d] hover:text-[#ff2d2d] transition-colors text-sm"
        >◄ PREV</button>
        <div className="flex-1 text-center text-lg font-semibold text-[#e0e0e0]">
          {year} — {MONTHS[month - 1].toUpperCase()}
        </div>
        <button
          onClick={() => { const m = month === 12 ? 1 : month + 1; const y = month === 12 ? year + 1 : year; setYear(y); setMonth(m); setLoading(true) }}
          className="px-4 py-2 bg-[#1a1a1a] border border-[#2a2a2a] text-[#888] hover:border-[#ff2d2d] hover:text-[#ff2d2d] transition-colors text-sm"
        >NEXT ►</button>
      </div>

      {/* Total Card */}
      <div className="kitt-box border-[#ff2d2d40] p-8">
        <div className="text-[#888] text-xs tracking-widest mb-2">TOTAL EXPENDITURE</div>
        <div className="text-5xl font-bold text-[#ff2d2d] kitt-glow">
          {formatAmount(data?.total || 0)}
        </div>
        <div className="text-[#888] text-xs mt-2">{data?.transactions?.length || 0} TRANSACTION{data?.transactions?.length !== 1 ? 'S' : ''} RECORDED</div>
      </div>

      {/* Category Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <div className="kitt-box border-[#2a2a2a] p-6">
          <div className="text-[#888] text-xs tracking-widest mb-6">CATEGORY BREAKDOWN</div>
          <div className="space-y-4">
            {data?.by_category?.length === 0 && (
              <div className="text-[#888] text-sm text-center py-8">No data for this period</div>
            )}
            {data?.by_category?.map((cat) => {
              const pct = (cat.total / maxCat) * 100
              return (
                <div key={cat.category_id} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-[#e0e0e0]">
                      {cat.category_icon} {cat.category_name}
                    </span>
                    <span className="text-[#ff2d2d] font-mono">{formatAmount(cat.total)}</span>
                  </div>
                  <div className="h-2 bg-[#1a1a1a] rounded overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-[#ff2d2d] to-[#ff6b6b] rounded"
                      style={{ width: `${pct}%` }}
                    ></div>
                  </div>
                  <div className="text-[#888] text-xs text-right">{cat.count}笔</div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Category Pie / Donut */}
        <div className="kitt-box border-[#2a2a2a] p-6">
          <div className="text-[#888] text-xs tracking-widest mb-6">SPENDING RATIO</div>
          <DonutChart categories={data?.by_category || []} total={data?.total || 0} />
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="kitt-box border-[#2a2a2a] p-6">
        <div className="text-[#888] text-xs tracking-widest mb-4">RECENT TRANSACTIONS</div>
        {data?.transactions?.length === 0 && (
          <div className="text-[#888] text-sm text-center py-8">No transactions this month</div>
        )}
        <div className="space-y-2">
          {data?.transactions?.slice(0, 10).map((tx) => (
            <div key={tx.id} className="flex items-center justify-between py-3 border-b border-[#1a1a1a] last:border-0">
              <div className="flex items-center gap-4">
                <div className="text-xl">{tx.category_icon}</div>
                <div>
                  <div className="text-[#e0e0e0] text-sm">{tx.merchant || tx.description || tx.category_name}</div>
                  <div className="text-[#888] text-xs">{formatDate(tx.date)} · {tx.category_name}</div>
                </div>
              </div>
              <div className="text-[#ff2d2d] font-mono font-semibold">
                -{formatAmount(tx.amount)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function DonutChart({ categories, total }: { categories: CategorySummary[]; total: number }) {
  if (categories.length === 0) {
    return <div className="text-[#888] text-sm text-center py-8">No data</div>
  }

  const COLORS = [
    '#ff2d2d', '#ffd93d', '#6bcbff', '#c56bff',
    '#ff9f6b', '#00ff88', '#ff8800', '#c8a87c'
  ]

  let cumulative = 0
  const segments = categories.map((cat, i) => {
    const start = cumulative
    cumulative += cat.total / total
    return { ...cat, start, end: cumulative, color: COLORS[i % COLORS.length] }
  })

  // SVG arc helper
  const cx = 100, cy = 100, r = 70
  const circumference = 2 * Math.PI * r

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 200 200" className="w-48 h-48">
        {segments.map((seg, i) => {
          const dashLen = (seg.end - seg.start) * circumference
          const dashGap = circumference - dashLen
          return (
            <circle
              key={seg.category_id}
              cx={cx} cy={cy} r={r}
              fill="none"
              stroke={seg.color}
              strokeWidth="24"
              strokeDasharray={`${dashLen} ${dashGap}`}
              strokeDashoffset={-(seg.start * circumference)}
              style={{ transition: 'all 0.3s' }}
            />
          )
        })}
        <text x={cx} y={cy - 8} textAnchor="middle" className="fill-[#e0e0e0]" fontSize="12" fontWeight="bold">TOTAL</text>
        <text x={cx} y={cy + 10} textAnchor="middle" className="fill-[#ff2d2d]" fontSize="10" fontWeight="bold">
          {total >= 10000 ? `¥${(total/10000).toFixed(1)}萬` : `¥${total.toLocaleString()}`}
        </text>
      </svg>
      <div className="grid grid-cols-2 gap-x-6 gap-y-1 mt-4">
        {segments.map((seg) => (
          <div key={seg.category_id} className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-sm" style={{ background: seg.color }}></div>
            <span className="text-[#e0e0e0]">{seg.category_icon} {seg.category_name}</span>
            <span className="text-[#888]">{((seg.end - seg.start) * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}
