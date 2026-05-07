import { useState, useEffect } from 'react'

const API = ''

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

interface BudgetSummary {
  category_id: string
  category_name: string
  category_icon: string
  budget_amount: number
  actual_amount: number
  remaining: number
  percentage: number
}

interface BudgetsData {
  budgets: BudgetSummary[]
  total_budget: number
  total_actual: number
}

interface Category {
  id: string
  name: string
  icon: string
}

function formatAmount(amount: number): string {
  if (Math.abs(amount) >= 10000) {
    return `¥${(Math.abs(amount) / 10000).toFixed(1)}萬`
  }
  return `¥${Math.abs(amount).toLocaleString()}`
}

export default function Budget() {
  const now = new Date()
  const [year, setYear] = useState(now.getFullYear())
  const [month, setMonth] = useState(now.getMonth() + 1)
  const [data, setData] = useState<BudgetsData | null>(null)
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [newCat, setNewCat] = useState('')
  const [newAmount, setNewAmount] = useState('')

  const load = () => {
    setLoading(true)
    fetch(`${API}/api/budgets/${year}/${month}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }

  const loadCategories = () => {
    fetch(`${API}/api/categories`)
      .then(r => r.json())
      .then(d => setCategories(d))
      .catch(() => {})
  }

  useEffect(() => { load() }, [year, month])
  useEffect(() => { loadCategories() }, [])

  const prevMonth = () => {
    if (month === 1) { setYear(year - 1); setMonth(12) }
    else { setMonth(month - 1) }
  }
  const nextMonth = () => {
    if (month === 12) { setYear(year + 1); setMonth(1) }
    else { setMonth(month + 1) }
  }

  const addBudget = async () => {
    if (!newCat || !newAmount) return
    await fetch(`${API}/api/budgets?category_id=${newCat}&amount=${newAmount}`, { method: 'POST' })
    setNewCat(''); setNewAmount(''); setShowAdd(false); load()
  }

  const deleteBudget = async (id: string) => {
    await fetch(`${API}/api/budgets/${id}`, { method: 'DELETE' })
    load()
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-[#888] text-xs tracking-widest mb-1">SYSTEM STATUS: ONLINE</div>
          <h1 className="text-3xl font-bold text-[#e0e0e0]">
            <span className="text-[#ff2d2d] kitt-glow">BUDGET</span> MANAGEMENT
          </h1>
        </div>
        <div className="text-right">
          <div className="text-[#888] text-xs">SCAN MODE: ACTIVE</div>
          <div className="text-[#ff2d2d] text-sm">{MONTHS[month - 1]} {year}</div>
        </div>
      </div>

      {/* Month Navigator */}
      <div className="flex items-center gap-4">
        <button onClick={prevMonth}
          className="px-4 py-2 bg-[#1a1a1a] border border-[#2a2a2a] text-[#888] hover:border-[#ff2d2d] hover:text-[#ff2d2d] transition-colors text-sm">
          ◄ PREV
        </button>
        <div className="flex-1 text-center text-lg font-semibold text-[#e0e0e0]">
          {year} — {MONTHS[month - 1].toUpperCase()}
        </div>
        <button onClick={nextMonth}
          className="px-4 py-2 bg-[#1a1a1a] border border-[#2a2a2a] text-[#888] hover:border-[#ff2d2d] hover:text-[#ff2d2d] transition-colors text-sm">
          NEXT ►
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="kitt-box border-[#2a2a2a] p-6 text-center">
          <div className="text-[#888] text-xs tracking-widest mb-2">TOTAL BUDGET</div>
          <div className="text-3xl font-bold text-[#e0e0e0]">{formatAmount(data?.total_budget || 0)}</div>
        </div>
        <div className="kitt-box border-[#2a2a2a] p-6 text-center">
          <div className="text-[#888] text-xs tracking-widest mb-2">ACTUAL SPENT</div>
          <div className="text-3xl font-bold text-[#ff2d2d]">{formatAmount(data?.total_actual || 0)}</div>
        </div>
        <div className="kitt-box border-[#00ff8840] p-6 text-center">
          <div className="text-[#888] text-xs tracking-widest mb-2">REMAINING</div>
          <div className={`text-3xl font-bold ${(data?.total_budget || 0) - (data?.total_actual || 0) >= 0 ? 'text-[#00ff88]' : 'text-[#ff6b6b]'}`}>
            {formatAmount((data?.total_budget || 0) - (data?.total_actual || 0))}
          </div>
        </div>
      </div>

      {/* Add Budget Button */}
      <div className="flex justify-end">
        <button onClick={() => { setShowAdd(!showAdd); loadCategories() }}
          className="px-4 py-2 bg-[#ff2d2d] hover:bg-[#ff4444] text-white text-sm font-bold transition-colors">
          + ADD BUDGET
        </button>
      </div>

      {/* Add Budget Form */}
      {showAdd && (
        <div className="kitt-box border-[#ff2d2d40] p-6 space-y-4">
          <div className="text-[#ff2d2d] text-xs tracking-widest mb-2">NEW BUDGET</div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <select value={newCat} onChange={e => setNewCat(e.target.value)}
              className="bg-[#1a1a1a] border border-[#2a2a2a] text-[#e0e0e0] p-3 text-sm focus:border-[#ff2d2d] outline-none">
              <option value="">Select category...</option>
              {categories.map(c => (
                <option key={c.id} value={c.id}>{c.icon} {c.name}</option>
              ))}
            </select>
            <input type="number" value={newAmount} onChange={e => setNewAmount(e.target.value)}
              placeholder="Budget amount (JPY)"
              className="bg-[#1a1a1a] border border-[#2a2a2a] text-[#e0e0e0] p-3 text-sm focus:border-[#ff2d2d] outline-none" />
          </div>
          <div className="flex gap-3">
            <button onClick={addBudget}
              className="px-6 py-2 bg-[#ff2d2d] hover:bg-[#ff4444] text-white text-sm font-bold">SAVE</button>
            <button onClick={() => setShowAdd(false)}
              className="px-6 py-2 bg-[#2a2a2a] hover:bg-[#3a3a3a] text-[#888] text-sm">CANCEL</button>
          </div>
        </div>
      )}

      {/* Budget List */}
      <div className="kitt-box border-[#2a2a2a] p-6">
        <div className="text-[#888] text-xs tracking-widest mb-6">CATEGORY BUDGETS</div>
        {loading && (
          <div className="text-center py-8">
            <div className="w-8 h-8 border-2 border-[#ff2d2d] border-t-transparent rounded-full animate-spin mx-auto"></div>
          </div>
        )}
        {!loading && data?.budgets?.length === 0 && (
          <div className="text-[#888] text-sm text-center py-8">
            No budgets set. Click "+ ADD BUDGET" to start.
          </div>
        )}
        {!loading && data?.budgets?.map((b) => {
          const over = b.actual_amount > b.budget_amount
          return (
            <div key={b.category_id} className="mb-6 last:mb-0">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{b.category_icon}</span>
                  <span className="text-[#e0e0e0] font-semibold">{b.category_name}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-[#888] text-sm">
                    {formatAmount(b.actual_amount)} / {formatAmount(b.budget_amount)}
                  </span>
                  <button onClick={() => deleteBudget(b.category_id)}
                    className="text-[#ff2d2d] hover:text-[#ff4444] text-xs">DELETE</button>
                </div>
              </div>
              <div className="h-4 bg-[#1a1a1a] rounded overflow-hidden">
                <div
                  className={`h-full rounded transition-all ${
                    over ? 'bg-gradient-to-r from-[#ff6b6b] to-[#ff2d2d]' : 'bg-gradient-to-r from-[#ff2d2d] to-[#ff6b6b]'
                  }`}
                  style={{ width: `${Math.min(b.percentage, 100)}%` }}
                ></div>
              </div>
              <div className="flex justify-between mt-1">
                <span className={`text-xs ${over ? 'text-[#ff6b6b]' : 'text-[#888]'}`}>
                  {over ? '⚠ OVER BUDGET' : `${b.percentage.toFixed(1)}% used`}
                </span>
                <span className={`text-xs ${b.remaining >= 0 ? 'text-[#00ff88]' : 'text-[#ff6b6b]'}`}>
                  {b.remaining >= 0 ? `${formatAmount(b.remaining)} left` : `${formatAmount(Math.abs(b.remaining))} over`}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
