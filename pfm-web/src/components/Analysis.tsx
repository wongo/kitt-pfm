import { useState, useEffect } from 'react'

const API = ''

interface CategorySummary {
  category_id: string
  category_name: string
  category_icon: string
  total: number
  count: number
}

interface MonthData {
  year: number
  month: number
  total: number
  by_category: CategorySummary[]
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const CURRENT_YEAR = new Date().getFullYear()
const COLORS = ['#ff2d2d', '#ffd93d', '#6bcbff', '#c56bff', '#ff9f6b', '#00ff88', '#ff8800', '#c8a87c', '#ff6b9d', '#9d6bff']

function formatAmount(amount: number): string {
  if (amount >= 10000) return `¥${(amount / 10000).toFixed(1)}萬`
  return `¥${amount.toLocaleString()}`
}

export default function Analysis() {
  const [year, setYear] = useState(CURRENT_YEAR)
  const [monthlyData, setMonthlyData] = useState<MonthData[]>([])
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadYear()
  }, [year])

  function loadYear() {
    setLoading(true)
    Promise.all(
      Array.from({ length: 12 }, (_, i) =>
        fetch(`${API}/api/summary/${year}/${i + 1}`).then(r => r.json())
      )
    ).then(results => {
      setMonthlyData(results)
      setLoading(false)
    }).catch(() => setLoading(false))
  }

  const selected = monthlyData[selectedMonth - 1]
  const maxMonth = Math.max(...monthlyData.map(m => m.total), 1)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-[#888] text-xs tracking-widest mb-1">SYSTEM STATUS: ONLINE</div>
          <h1 className="text-3xl font-bold text-[#e0e0e0]">
            <span className="text-[#ff2d2d] kitt-glow">ANALYSIS</span> ENGINE
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <select
            value={year}
            onChange={e => setYear(parseInt(e.target.value))}
            className="bg-[#1a1a1a] border border-[#2a2a2a] text-[#e0e0e0] px-4 py-2 text-sm focus:border-[#ff2d2d] outline-none"
          >
            {[2024, 2025, 2026].map(y => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Monthly Bar Chart */}
      <div className="kitt-box border-[#2a2a2a] p-6">
        <div className="text-[#888] text-xs tracking-widest mb-6">MONTHLY SPENDING OVERVIEW — {year}</div>
        {loading ? (
          <div className="h-48 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-[#ff2d2d] border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="flex items-end gap-2 h-48">
            {monthlyData.map((m, i) => {
              const height = m.total > 0 ? Math.max((m.total / maxMonth) * 100, 4) : 0
              const isSelected = i + 1 === selectedMonth
              return (
                <button
                  key={i}
                  onClick={() => setSelectedMonth(i + 1)}
                  className="flex-1 flex flex-col items-center gap-1 group"
                >
                  <div className="w-full flex flex-col items-center justify-end h-40">
                    <div
                      className={`w-full rounded-t transition-all ${isSelected ? 'bg-[#ff2d2d]' : 'bg-[#2a2a2a] group-hover:bg-[#ff2d2d80]'}`}
                      style={{ height: `${height}%` }}
                    ></div>
                  </div>
                  <div className={`text-xs ${isSelected ? 'text-[#ff2d2d]' : 'text-[#888]'}`}>
                    {MONTHS[i]}
                  </div>
                  <div className={`text-xs font-mono ${isSelected ? 'text-[#ff2d2d]' : 'text-[#555]'}`}>
                    {m.total > 0 ? formatAmount(m.total) : '-'}
                  </div>
                </button>
              )
            })}
          </div>
        )}
      </div>

      {/* Selected Month Detail */}
      {selected && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Category Breakdown */}
          <div className="kitt-box border-[#2a2a2a] p-6">
            <div className="text-[#888] text-xs tracking-widest mb-4">
              {MONTHS[selectedMonth - 1]} {year} — CATEGORY BREAKDOWN
            </div>
            <div className="text-2xl font-bold text-[#ff2d2d] kitt-glow mb-4">
              {formatAmount(selected.total)}
            </div>
            <div className="space-y-3">
              {selected.by_category.map((cat, i) => {
                const pct = selected.total > 0 ? (cat.total / selected.total) * 100 : 0
                return (
                  <div key={cat.category_id}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-[#e0e0e0]">
                        <span style={{ color: COLORS[i % COLORS.length] }}>{cat.category_icon}</span>{' '}
                        {cat.category_name}
                      </span>
                      <span className="text-[#ff2d2d] font-mono">{formatAmount(cat.total)}</span>
                    </div>
                    <div className="h-1.5 bg-[#1a1a1a] rounded overflow-hidden">
                      <div
                        className="h-full rounded"
                        style={{ width: `${pct}%`, background: COLORS[i % COLORS.length] }}
                      ></div>
                    </div>
                    <div className="text-[#555] text-xs text-right">{pct.toFixed(1)}% · {cat.count}筆</div>
                  </div>
                )
              })}
              {selected.by_category.length === 0 && (
                <div className="text-[#888] text-sm text-center py-6">No data</div>
              )}
            </div>
          </div>

          {/* Top Transactions */}
          <div className="kitt-box border-[#2a2a2a] p-6">
            <div className="text-[#888] text-xs tracking-widest mb-4">
              {MONTHS[selectedMonth - 1]} {year} — TOP SPENDING
            </div>
            <div className="space-y-2">
              {selected.by_category.slice(0, 5).map((cat, i) => (
                <div key={cat.category_id} className="flex items-center gap-4 py-2 border-b border-[#1a1a1a] last:border-0">
                  <div className="text-xl" style={{ color: COLORS[i % COLORS.length] }}>
                    {cat.category_icon}
                  </div>
                  <div className="flex-1">
                    <div className="text-[#e0e0e0] text-sm">{cat.category_name}</div>
                    <div className="text-[#888] text-xs">{cat.count} 筆交易</div>
                  </div>
                  <div className="text-[#ff2d2d] font-mono font-semibold">
                    {formatAmount(cat.total)}
                  </div>
                </div>
              ))}
              {selected.by_category.length === 0 && (
                <div className="text-[#888] text-sm text-center py-6">No data</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Year Summary */}
      <div className="kitt-box border-[#2a2a2a] p-6">
        <div className="text-[#888] text-xs tracking-widest mb-4">{year} YEAR-TO-DATE SUMMARY</div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <div className="text-[#888] text-xs mb-1">TOTAL SPENT</div>
            <div className="text-2xl font-bold text-[#ff2d2d]">
              {formatAmount(monthlyData.reduce((sum, m) => sum + m.total, 0))}
            </div>
          </div>
          <div>
            <div className="text-[#888] text-xs mb-1">AVG/MONTH</div>
            <div className="text-2xl font-bold text-[#e0e0e0]">
              {formatAmount(monthlyData.reduce((sum, m) => sum + m.total, 0) / 12)}
            </div>
          </div>
          <div>
            <div className="text-[#888] text-xs mb-1">TOP MONTH</div>
            <div className="text-2xl font-bold text-[#e0e0e0]">
              {MONTHS[monthlyData.findIndex(m => m.total === Math.max(...monthlyData.map(x => x.total)))]}
            </div>
          </div>
          <div>
            <div className="text-[#888] text-xs mb-1">ACTIVE CATEGORIES</div>
            <div className="text-2xl font-bold text-[#e0e0e0]">
              {[...new Set(monthlyData.flatMap(m => m.by_category.map(c => c.category_id)))].length}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
