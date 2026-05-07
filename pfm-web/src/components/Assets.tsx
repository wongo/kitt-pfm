import { useState, useEffect } from 'react'

const API = ''

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
  bank: '銀行存款',
  credit_card: '信用卡',
  securities: '證券',
  e_money: '電子貨幣',
  cash: '現金',
  loan: '貸款',
  other: '其他',
}

const ACCOUNT_TYPE_ICONS: Record<string, string> = {
  bank: '🏦',
  credit_card: '💳',
  securities: '📈',
  e_money: '📱',
  cash: '💵',
  loan: '🏠',
  other: '📦',
}

interface Account {
  id: string
  name: string
  type: string
  balance: number
  currency: string
}

interface AccountTypeSummary {
  type: string
  total: number
  accounts: Account[]
}

interface AssetsSummary {
  total_assets: number
  total_debt: number
  net_worth: number
  by_type: AccountTypeSummary[]
  accounts: Account[]
}

function formatAmount(amount: number): string {
  const abs = Math.abs(amount)
  if (abs >= 10000) {
    return `¥${(abs / 10000).toFixed(1)}萬`
  }
  return `¥${abs.toLocaleString()}`
}

export default function Assets() {
  const [data, setData] = useState<AssetsSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API}/api/assets`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-[#ff2d2d] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <span className="text-[#888] text-sm">SCANNING ASSETS...</span>
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

  const total = (data?.total_assets || 0) + (data?.total_debt || 0)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-[#888] text-xs tracking-widest mb-1">SYSTEM STATUS: ONLINE</div>
          <h1 className="text-3xl font-bold text-[#e0e0e0]">
            <span className="text-[#ff2d2d] kitt-glow">ASSETS</span> OVERVIEW
          </h1>
        </div>
        <div className="text-right">
          <div className="text-[#888] text-xs">SCAN MODE: ACTIVE</div>
          <div className="text-[#ff2d2d] text-sm">TOTAL PORTFOLIO</div>
        </div>
      </div>

      {/* Net Worth Hero */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="kitt-box border-[#2a2a2a] p-6 text-center">
          <div className="text-[#888] text-xs tracking-widest mb-2">TOTAL ASSETS</div>
          <div className="text-3xl font-bold text-[#00ff88]">
            {formatAmount(data?.total_assets || 0)}
          </div>
        </div>
        <div className="kitt-box border-[#2a2a2a] p-6 text-center">
          <div className="text-[#888] text-xs tracking-widest mb-2">TOTAL DEBT</div>
          <div className="text-3xl font-bold text-[#ff6b6b]">
            {formatAmount(data?.total_debt || 0)}
          </div>
        </div>
        <div className="kitt-box border-[#ff2d2d40] p-6 text-center">
          <div className="text-[#888] text-xs tracking-widest mb-2">NET WORTH</div>
          <div className="text-3xl font-bold text-[#ff2d2d] kitt-glow">
            {formatAmount(data?.net_worth || 0)}
          </div>
        </div>
      </div>

      {/* Asset Allocation */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <div className="kitt-box border-[#2a2a2a] p-6">
          <div className="text-[#888] text-xs tracking-widest mb-6">ASSET ALLOCATION</div>
          <AllocationChart data={data?.by_type || []} total={data?.total_assets || 0} />
        </div>

        {/* Debt Breakdown */}
        <div className="kitt-box border-[#2a2a2a] p-6">
          <div className="text-[#888] text-xs tracking-widest mb-6">LIABILITY BREAKDOWN</div>
          <DebtChart data={data?.by_type || []} total={data?.total_debt || 0} />
        </div>
      </div>

      {/* Account List */}
      <div className="kitt-box border-[#2a2a2a] p-6">
        <div className="text-[#888] text-xs tracking-widest mb-6">ALL ACCOUNTS</div>
        <div className="space-y-6">
          {data?.by_type?.map((group) => (
            <div key={group.type}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{ACCOUNT_TYPE_ICONS[group.type] || '📦'}</span>
                  <span className="text-[#e0e0e0] font-semibold">{ACCOUNT_TYPE_LABELS[group.type] || group.type}</span>
                </div>
                <span className={`font-bold ${group.total >= 0 ? 'text-[#00ff88]' : 'text-[#ff6b6b]'}`}>
                  {formatAmount(group.total)}
                </span>
              </div>
              <div className="space-y-2 pl-6">
                {group.accounts.map((acc) => (
                  <div key={acc.id} className="flex items-center justify-between py-2 border-b border-[#1a1a1a] last:border-0">
                    <span className="text-[#e0e0e0] text-sm">{acc.name}</span>
                    <span className={`font-mono text-sm ${acc.balance >= 0 ? 'text-[#e0e0e0]' : 'text-[#ff6b6b]'}`}>
                      {formatAmount(acc.balance)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function AllocationChart({ data, total }: { data: AccountTypeSummary[]; total: number }) {
  if (total === 0) {
    return <div className="text-[#888] text-sm text-center py-16">No asset data</div>
  }

  const COLORS = ['#ff2d2d', '#ffd93d', '#6bcbff', '#c56bff', '#ff9f6b', '#00ff88', '#ff8800']

  // Only positive types
  const positiveData = data.filter(d => d.total > 0)

  let cumulative = 0
  const segments = positiveData.map((d, i) => {
    const start = cumulative
    cumulative += d.total / total
    return { ...d, start, end: cumulative, color: COLORS[i % COLORS.length] }
  })

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
              key={seg.type}
              cx={cx} cy={cy} r={r}
              fill="none"
              stroke={seg.color}
              strokeWidth="20"
              strokeDasharray={`${dashLen} ${dashGap}`}
              strokeDashoffset={-(seg.start * circumference)}
              style={{ transition: 'all 0.3s' }}
            />
          )
        })}
        <text x={cx} y={cy - 5} textAnchor="middle" className="fill-[#888]" fontSize="8">TOTAL</text>
        <text x={cx} y={cy + 10} textAnchor="middle" className="fill-[#ff2d2d]" fontSize="9" fontWeight="bold">
          {total >= 10000 ? `¥${(total/10000).toFixed(1)}萬` : `¥${total.toLocaleString()}`}
        </text>
      </svg>
      <div className="grid grid-cols-2 gap-x-6 gap-y-2 mt-4 w-full">
        {segments.map((seg) => (
          <div key={seg.type} className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-sm flex-shrink-0" style={{ background: seg.color }}></div>
            <span className="text-[#e0e0e0]">{ACCOUNT_TYPE_ICONS[seg.type]} {ACCOUNT_TYPE_LABELS[seg.type]}</span>
            <span className="text-[#888] ml-auto">{((seg.end - seg.start) * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function DebtChart({ data, total }: { data: AccountTypeSummary[]; total: number }) {
  if (total === 0) {
    return <div className="text-[#888] text-sm text-center py-16">No debt data</div>
  }

  // Only negative types
  const negativeData = data.filter(d => d.total < 0)
  const absTotal = Math.abs(total)

  return (
    <div className="space-y-4">
      {negativeData.map((d) => (
        <div key={d.type} className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="text-[#e0e0e0]">{ACCOUNT_TYPE_ICONS[d.type]} {ACCOUNT_TYPE_LABELS[d.type] || d.type}</span>
            <span className="text-[#ff6b6b] font-mono">{formatAmount(d.total)}</span>
          </div>
          <div className="h-3 bg-[#1a1a1a] rounded overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-[#ff6b6b] to-[#ff2d2d] rounded"
              style={{ width: `${(Math.abs(d.total) / absTotal) * 100}%` }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  )
}
