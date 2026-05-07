import { useState, useEffect } from 'react'

const API = ''

interface FixedCost {
  id: string
  name: string
  amount: number
  category_id: string
  category_name: string
  category_icon: string
  due_day: number
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

export default function FixedCosts() {
  const [data, setData] = useState<FixedCost[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ name: '', amount: '', category_id: '', due_day: '25' })

  const load = () => {
    fetch(`${API}/api/fixed-costs`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }

  const loadCategories = () => {
    fetch(`${API}/api/categories`)
      .then(r => r.json())
      .then(d => setCategories(d))
  }

  useEffect(() => { load() }, [])
  useEffect(() => { loadCategories() }, [])

  const addFixedCost = async () => {
    if (!form.name || !form.amount || !form.category_id) return
    await fetch(`${API}/api/fixed-costs?name=${encodeURIComponent(form.name)}&amount=${form.amount}&category_id=${form.category_id}&due_day=${form.due_day}`, { method: 'POST' })
    setForm({ name: '', amount: '', category_id: '', due_day: '25' })
    setShowAdd(false)
    load()
  }

  const deleteFixedCost = async (id: string) => {
    await fetch(`${API}/api/fixed-costs/${id}`, { method: 'DELETE' })
    load()
  }

  const total = data.reduce((sum, fc) => sum + fc.amount, 0)
  const today = new Date().getDate()

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-[#888] text-xs tracking-widest mb-1">SYSTEM STATUS: ONLINE</div>
          <h1 className="text-3xl font-bold text-[#e0e0e0]">
            <span className="text-[#ff2d2d] kitt-glow">FIXED</span> COSTS
          </h1>
        </div>
        <div className="text-right">
          <div className="text-[#888] text-xs">SCAN MODE: ACTIVE</div>
          <div className="text-[#ff2d2d] text-sm">{new Date().getFullYear()}年</div>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="kitt-box border-[#2a2a2a] p-6 text-center">
          <div className="text-[#888] text-xs tracking-widest mb-2">MONTHLY TOTAL</div>
          <div className="text-3xl font-bold text-[#ff2d2d]">{formatAmount(total)}</div>
        </div>
        <div className="kitt-box border-[#2a2a2a] p-6 text-center">
          <div className="text-[#888] text-xs tracking-widest mb-2">YEARLY PROJECTION</div>
          <div className="text-3xl font-bold text-[#e0e0e0]">{formatAmount(total * 12)}</div>
        </div>
        <div className="kitt-box border-[#2a2a2a] p-6 text-center">
          <div className="text-[#888] text-xs tracking-widest mb-2">ITEMS</div>
          <div className="text-3xl font-bold text-[#e0e0e0]">{data.length}</div>
        </div>
      </div>

      {/* Upcoming This Month */}
      <div className="kitt-box border-[#2a2a2a] p-6">
        <div className="text-[#888] text-xs tracking-widest mb-4">DUE THIS MONTH (DAY {today})</div>
        <div className="space-y-3">
          {data.filter(fc => fc.due_day >= today).length === 0 && (
            <div className="text-[#888] text-sm text-center py-4">No fixed costs due this month</div>
          )}
          {data.filter(fc => fc.due_day >= today).map((fc) => (
            <div key={fc.id} className="flex items-center justify-between py-2 border-b border-[#1a1a1a] last:border-0">
              <div className="flex items-center gap-3">
                <span className="text-xl">{fc.category_icon}</span>
                <div>
                  <div className="text-[#e0e0e0] text-sm">{fc.name}</div>
                  <div className="text-[#888] text-xs">Due: {fc.due_day}日</div>
                </div>
              </div>
              <span className="text-[#ff2d2d] font-mono font-semibold">{formatAmount(fc.amount)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* All Fixed Costs */}
      <div className="kitt-box border-[#2a2a2a] p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="text-[#888] text-xs tracking-widest">ALL FIXED COSTS</div>
          <button onClick={() => { setShowAdd(!showAdd); loadCategories() }}
            className="px-4 py-2 bg-[#ff2d2d] hover:bg-[#ff4444] text-white text-sm font-bold transition-colors">
            + ADD
          </button>
        </div>

        {/* Add Form */}
        {showAdd && (
          <div className="kitt-box border-[#ff2d2d40] p-6 mb-6 space-y-4">
            <div className="text-[#ff2d2d] text-xs tracking-widest mb-2">NEW FIXED COST</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
                placeholder="Name (e.g. 房租, 房貸)"
                className="bg-[#1a1a1a] border border-[#2a2a2a] text-[#e0e0e0] p-3 text-sm focus:border-[#ff2d2d] outline-none" />
              <input type="number" value={form.amount} onChange={e => setForm({ ...form, amount: e.target.value })}
                placeholder="Amount (JPY)"
                className="bg-[#1a1a1a] border border-[#2a2a2a] text-[#e0e0e0] p-3 text-sm focus:border-[#ff2d2d] outline-none" />
              <select value={form.category_id} onChange={e => setForm({ ...form, category_id: e.target.value })}
                className="bg-[#1a1a1a] border border-[#2a2a2a] text-[#e0e0e0] p-3 text-sm focus:border-[#ff2d2d] outline-none">
                <option value="">Select category...</option>
                {categories.map(c => (
                  <option key={c.id} value={c.id}>{c.icon} {c.name}</option>
                ))}
              </select>
              <input type="number" value={form.due_day} onChange={e => setForm({ ...form, due_day: e.target.value })}
                placeholder="Due day (1-31)"
                min="1" max="31"
                className="bg-[#1a1a1a] border border-[#2a2a2a] text-[#e0e0e0] p-3 text-sm focus:border-[#ff2d2d] outline-none" />
            </div>
            <div className="flex gap-3">
              <button onClick={addFixedCost}
                className="px-6 py-2 bg-[#ff2d2d] hover:bg-[#ff4444] text-white text-sm font-bold">SAVE</button>
              <button onClick={() => setShowAdd(false)}
                className="px-6 py-2 bg-[#2a2a2a] hover:bg-[#3a3a3a] text-[#888] text-sm">CANCEL</button>
            </div>
          </div>
        )}

        {loading && (
          <div className="text-center py-8">
            <div className="w-8 h-8 border-2 border-[#ff2d2d] border-t-transparent rounded-full animate-spin mx-auto"></div>
          </div>
        )}

        {!loading && data.length === 0 && (
          <div className="text-[#888] text-sm text-center py-8">No fixed costs set yet.</div>
        )}

        {!loading && data.map((fc) => (
          <div key={fc.id} className="flex items-center justify-between py-3 border-b border-[#1a1a1a] last:border-0">
            <div className="flex items-center gap-3">
              <span className="text-xl">{fc.category_icon}</span>
              <div>
                <div className="text-[#e0e0e0] text-sm font-semibold">{fc.name}</div>
                <div className="text-[#888] text-xs">{fc.category_name} · Due: {fc.due_day}日</div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-[#ff2d2d] font-mono font-bold">{formatAmount(fc.amount)}/月</span>
              <button onClick={() => deleteFixedCost(fc.id)}
                className="text-[#ff2d2d] hover:text-[#ff4444] text-xs">DELETE</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
