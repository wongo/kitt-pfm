import { useState, useEffect } from 'react'

const API = ''

interface Category {
  id: string
  name: string
  icon: string
}

interface Transaction {
  id: string
  date: string
  amount: number
  category_id: string
  category_name: string
  category_icon: string
  description: string
  merchant: string
}

function formatAmount(amount: number): string {
  if (amount >= 10000) {
    return `¥${(amount / 10000).toFixed(1)}萬`
  }
  return `¥${amount.toLocaleString()}`
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}

export default function Transactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)

  // Form state
  const [formDate, setFormDate] = useState(new Date().toISOString().split('T')[0])
  const [formAmount, setFormAmount] = useState('')
  const [formCategory, setFormCategory] = useState('')
  const [formMerchant, setFormMerchant] = useState('')
  const [formDesc, setFormDesc] = useState('')
  const [formError, setFormError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    fetchTransactions()
    fetchCategories()
  }, [])

  function fetchTransactions() {
    setLoading(true)
    fetch(`${API}/api/transactions?limit=100`)
      .then(r => r.json())
      .then(d => { setTransactions(d); setLoading(false) })
      .catch(() => setLoading(false))
  }

  function fetchCategories() {
    fetch(`${API}/api/categories`)
      .then(r => r.json())
      .then(d => setCategories(d))
      .catch(() => {})
  }

  function openAdd() {
    setEditingId(null)
    setFormDate(new Date().toISOString().split('T')[0])
    setFormAmount('')
    setFormCategory(categories[0]?.id || '')
    setFormMerchant('')
    setFormDesc('')
    setFormError('')
    setShowForm(true)
  }

  function openEdit(tx: Transaction) {
    setEditingId(tx.id)
    setFormDate(tx.date)
    setFormAmount(tx.amount.toString())
    setFormCategory(tx.category_id)
    setFormMerchant(tx.merchant)
    setFormDesc(tx.description)
    setFormError('')
    setShowForm(true)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!formAmount || !formCategory) {
      setFormError('金額與類別為必填')
      return
    }
    setSaving(true)
    setFormError('')
    try {
      // DELETE old and CREATE new for edit
      if (editingId) {
        await fetch(`${API}/api/transactions/${editingId}`, { method: 'DELETE' })
      }
      const res = await fetch(`${API}/api/transactions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date: formDate,
          amount: parseFloat(formAmount),
          category_id: formCategory,
          merchant: formMerchant,
          description: formDesc,
        }),
      })
      if (!res.ok) throw new Error('儲存失敗')
      setShowForm(false)
      fetchTransactions()
    } catch (err: any) {
      setFormError(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(txId: string) {
    try {
      await fetch(`${API}/api/transactions/${txId}`, { method: 'DELETE' })
      setDeleteConfirm(null)
      fetchTransactions()
    } catch {
      setDeleteConfirm(null)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-[#888] text-xs tracking-widest mb-1">SYSTEM STATUS: ONLINE</div>
          <h1 className="text-3xl font-bold text-[#e0e0e0]">
            <span className="text-[#ff2d2d] kitt-glow">TRANSACTION</span> MANAGER
          </h1>
        </div>
        <button
          onClick={openAdd}
          className="px-6 py-3 bg-[#ff2d2d] text-black font-bold text-sm hover:bg-[#ff4a4a] transition-colors"
        >
          + ADD TRANSACTION
        </button>
      </div>

      {/* Add/Edit Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black80 z-50 flex items-center justify-center p-4">
          <div className="kitt-box border-[#ff2d2d] w-full max-w-md p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-bold text-[#e0e0e0]">
                {editingId ? 'EDIT TRANSACTION' : 'NEW TRANSACTION'}
              </h2>
              <button onClick={() => setShowForm(false)} className="text-[#888] hover:text-[#ff2d2d] text-xl">✕</button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Date */}
              <div>
                <label className="text-[#888] text-xs tracking-widest block mb-1">DATE</label>
                <input
                  type="date"
                  value={formDate}
                  onChange={e => setFormDate(e.target.value)}
                  className="w-full bg-[#0a0a0a] border border-[#2a2a2a] text-[#e0e0e0] px-4 py-2 focus:border-[#ff2d2d] outline-none"
                />
              </div>

              {/* Amount */}
              <div>
                <label className="text-[#888] text-xs tracking-widest block mb-1">AMOUNT (JPY)</label>
                <input
                  type="number"
                  value={formAmount}
                  onChange={e => setFormAmount(e.target.value)}
                  placeholder="1980"
                  className="w-full bg-[#0a0a0a] border border-[#2a2a2a] text-[#e0e0e0] px-4 py-2 focus:border-[#ff2d2d] outline-none font-mono"
                />
              </div>

              {/* Category */}
              <div>
                <label className="text-[#888] text-xs tracking-widest block mb-1">CATEGORY</label>
                <select
                  value={formCategory}
                  onChange={e => setFormCategory(e.target.value)}
                  className="w-full bg-[#0a0a0a] border border-[#2a2a2a] text-[#e0e0e0] px-4 py-2 focus:border-[#ff2d2d] outline-none"
                >
                  {categories.map(c => (
                    <option key={c.id} value={c.id}>{c.icon} {c.name}</option>
                  ))}
                </select>
              </div>

              {/* Merchant */}
              <div>
                <label className="text-[#888] text-xs tracking-widest block mb-1">MERCHANT</label>
                <input
                  type="text"
                  value={formMerchant}
                  onChange={e => setFormMerchant(e.target.value)}
                  placeholder="コメダ珈琲"
                  className="w-full bg-[#0a0a0a] border border-[#2a2a2a] text-[#e0e0e0] px-4 py-2 focus:border-[#ff2d2d] outline-none"
                />
              </div>

              {/* Description */}
              <div>
                <label className="text-[#888] text-xs tracking-widest block mb-1">DESCRIPTION</label>
                <input
                  type="text"
                  value={formDesc}
                  onChange={e => setFormDesc(e.target.value)}
                  placeholder="早餐"
                  className="w-full bg-[#0a0a0a] border border-[#2a2a2a] text-[#e0e0e0] px-4 py-2 focus:border-[#ff2d2d] outline-none"
                />
              </div>

              {formError && (
                <div className="text-[#ff2d2d] text-sm">{formError}</div>
              )}

              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 py-3 bg-[#ff2d2d] text-black font-bold text-sm hover:bg-[#ff4a4a] transition-colors disabled:opacity-50"
                >
                  {saving ? 'SAVING...' : editingId ? 'UPDATE' : 'ADD'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-6 py-3 bg-[#1a1a1a] border border-[#2a2a2a] text-[#888] text-sm hover:border-[#ff2d2d] hover:text-[#ff2d2d] transition-colors"
                >
                  CANCEL
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirm */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black80 z-50 flex items-center justify-center p-4">
          <div className="kitt-box border-[#ff2d2d] w-full max-w-sm p-8 text-center">
            <div className="text-[#ff2d2d] text-xs tracking-widest mb-4">CONFIRM DELETE</div>
            <div className="text-[#e0e0e0] mb-6">此筆交易刪除後無法恢復，確定刪除？</div>
            <div className="flex gap-3">
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="flex-1 py-3 bg-[#ff2d2d] text-black font-bold text-sm hover:bg-[#ff4a4a]"
              >
                DELETE
              </button>
              <button
                onClick={() => setDeleteConfirm(null)}
                className="px-6 py-3 bg-[#1a1a1a] border border-[#2a2a2a] text-[#888] text-sm hover:border-[#ff2d2d]"
              >
                CANCEL
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Transactions Table */}
      <div className="kitt-box border-[#2a2a2a]">
        <div className="p-6 border-b border-[#2a2a2a]">
          <div className="text-[#888] text-xs tracking-widest">ALL TRANSACTIONS</div>
        </div>

        {loading ? (
          <div className="p-12 text-center">
            <div className="w-8 h-8 border-2 border-[#ff2d2d] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <span className="text-[#888] text-sm">LOADING...</span>
          </div>
        ) : transactions.length === 0 ? (
          <div className="p-12 text-center text-[#888]">No transactions yet</div>
        ) : (
          <div className="divide-y divide-[#1a1a1a]">
            {transactions.map(tx => (
              <div key={tx.id} className="flex items-center justify-between p-4 hover:bg-[#1a1a1a] transition-colors">
                <div className="flex items-center gap-4">
                  <div className="text-2xl">{tx.category_icon}</div>
                  <div>
                    <div className="text-[#e0e0e0] text-sm font-medium">
                      {tx.merchant || tx.description || tx.category_name}
                    </div>
                    <div className="text-[#888] text-xs">
                      {formatDate(tx.date)} · {tx.category_name}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-[#ff2d2d] font-mono font-semibold text-right">
                    -{formatAmount(tx.amount)}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => openEdit(tx)}
                      className="px-3 py-1 text-xs text-[#888] border border-[#2a2a2a] hover:border-[#ff2d2d] hover:text-[#ff2d2d] transition-colors"
                    >
                      EDIT
                    </button>
                    <button
                      onClick={() => setDeleteConfirm(tx.id)}
                      className="px-3 py-1 text-xs text-[#888] border border-[#2a2a2a] hover:border-[#ff2d2d] hover:text-[#ff2d2d] transition-colors"
                    >
                      DEL
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
