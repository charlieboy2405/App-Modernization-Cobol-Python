import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, Plus, Trash2, RefreshCw, DollarSign, BarChart3, Users } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Gainer {
  symbol: string
  name: string
  price: number
  change: number
  pct_change: number
}

interface Investment {
  id: number
  customer_name: string
  stock_symbol: string
  quantity: number
  purchase_price: number
  purchase_date: string
  created_at: string
}

interface PortfolioItem extends Investment {
  current_price: number
  invested_value: number
  current_value: number
  gain_loss: number
  gain_loss_pct: number
}

interface PortfolioSummary {
  portfolio: PortfolioItem[]
  total_invested: number
  total_current_value: number
  total_gain_loss: number
  total_gain_loss_pct: number
}

type TabType = 'gainers' | 'investments' | 'portfolio'

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('gainers')
  const [gainers, setGainers] = useState<Gainer[]>([])
  const [gainersLoading, setGainersLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)
  const [investments, setInvestments] = useState<Investment[]>([])
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null)
  const [portfolioLoading, setPortfolioLoading] = useState(false)

  // Form state
  const [customerName, setCustomerName] = useState('')
  const [stockSymbol, setStockSymbol] = useState('')
  const [quantity, setQuantity] = useState('')
  const [purchasePrice, setPurchasePrice] = useState('')
  const [purchaseDate, setPurchaseDate] = useState('')
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const fetchGainers = useCallback(async () => {
    setGainersLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/top-gainers`)
      const data = await res.json()
      setGainers(data.gainers || [])
      setLastUpdated(data.last_updated)
    } catch (err) {
      console.error('Failed to fetch gainers:', err)
    } finally {
      setGainersLoading(false)
    }
  }, [])

  const fetchInvestments = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/investments`)
      const data = await res.json()
      setInvestments(data.investments || [])
    } catch (err) {
      console.error('Failed to fetch investments:', err)
    }
  }, [])

  const fetchPortfolio = useCallback(async () => {
    setPortfolioLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/investments/portfolio`)
      if (!res.ok) throw new Error('Failed to fetch portfolio')
      const data = await res.json()
      setPortfolio(data)
    } catch (err) {
      console.error('Failed to fetch portfolio:', err)
    } finally {
      setPortfolioLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchGainers()
    fetchInvestments()
  }, [fetchGainers, fetchInvestments])

  useEffect(() => {
    if (activeTab === 'portfolio') {
      fetchPortfolio()
    }
  }, [activeTab, fetchPortfolio])

  const handleAddInvestment = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')

    if (!customerName || !stockSymbol || !quantity || !purchasePrice || !purchaseDate) {
      setFormError('All fields are required')
      return
    }

    setSubmitting(true)
    try {
      const res = await fetch(`${API_URL}/api/investments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_name: customerName,
          stock_symbol: stockSymbol.toUpperCase(),
          quantity: parseFloat(quantity),
          purchase_price: parseFloat(purchasePrice),
          purchase_date: purchaseDate,
        }),
      })

      if (!res.ok) throw new Error('Failed to add investment')

      setCustomerName('')
      setStockSymbol('')
      setQuantity('')
      setPurchasePrice('')
      setPurchaseDate('')
      fetchInvestments()
    } catch (err) {
      setFormError('Failed to add investment. Please try again.')
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: number) => {
    try {
      const res = await fetch(`${API_URL}/api/investments/${id}`, { method: 'DELETE' })
      if (!res.ok) throw new Error('Failed to delete')
      fetchInvestments()
    } catch (err) {
      console.error('Failed to delete investment:', err)
    }
  }

  const handleFetchPrice = async () => {
    if (!stockSymbol) return
    try {
      const res = await fetch(`${API_URL}/api/stock/price/${stockSymbol.toUpperCase()}`)
      if (res.ok) {
        const data = await res.json()
        setPurchasePrice(data.price.toString())
      }
    } catch (err) {
      console.error('Failed to fetch price:', err)
    }
  }

  return (
    <div className="min-h-screen bg-zinc-50">
      {/* Header */}
      <header className="bg-zinc-900 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BarChart3 size={32} className="text-emerald-400" />
              <div>
                <h1 className="text-2xl font-bold">NASDAQ Investment Tracker</h1>
                <p className="text-zinc-400 text-sm">Track top daily gainers &amp; manage customer investments</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 mt-6">
        <div className="flex gap-2 border-b border-zinc-200 pb-0">
          <button
            onClick={() => setActiveTab('gainers')}
            className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${
              activeTab === 'gainers'
                ? 'bg-white text-zinc-900 border border-zinc-200 border-b-white -mb-px'
                : 'text-zinc-500 hover:text-zinc-700 hover:bg-zinc-100'
            }`}
          >
            <TrendingUp size={16} className="inline mr-2" />
            Top 10 Gainers
          </button>
          <button
            onClick={() => setActiveTab('investments')}
            className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${
              activeTab === 'investments'
                ? 'bg-white text-zinc-900 border border-zinc-200 border-b-white -mb-px'
                : 'text-zinc-500 hover:text-zinc-700 hover:bg-zinc-100'
            }`}
          >
            <Users size={16} className="inline mr-2" />
            Investments
          </button>
          <button
            onClick={() => setActiveTab('portfolio')}
            className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${
              activeTab === 'portfolio'
                ? 'bg-white text-zinc-900 border border-zinc-200 border-b-white -mb-px'
                : 'text-zinc-500 hover:text-zinc-700 hover:bg-zinc-100'
            }`}
          >
            <DollarSign size={16} className="inline mr-2" />
            Portfolio
          </button>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Top Gainers Tab */}
        {activeTab === 'gainers' && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl">Top 10 NASDAQ Daily Gainers</CardTitle>
                  <CardDescription>
                    {lastUpdated
                      ? `Last updated: ${new Date(lastUpdated).toLocaleString()}`
                      : 'Fetching latest data...'}
                  </CardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={fetchGainers}
                  disabled={gainersLoading}
                >
                  <RefreshCw size={16} className={`mr-2 ${gainersLoading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {gainersLoading && gainers.length === 0 ? (
                <div className="flex items-center justify-center py-12">
                  <RefreshCw size={24} className="animate-spin text-zinc-400 mr-3" />
                  <span className="text-zinc-500">Loading top gainers from NASDAQ...</span>
                </div>
              ) : gainers.length === 0 ? (
                <div className="text-center py-12 text-zinc-500">
                  No data available. Click refresh to try again.
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">#</TableHead>
                      <TableHead>Symbol</TableHead>
                      <TableHead>Company</TableHead>
                      <TableHead className="text-right">Price</TableHead>
                      <TableHead className="text-right">Change</TableHead>
                      <TableHead className="text-right">% Change</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {gainers.map((gainer, index) => (
                      <TableRow key={gainer.symbol}>
                        <TableCell className="font-medium text-zinc-500">{index + 1}</TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="font-mono font-bold">
                            {gainer.symbol}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-medium">{gainer.name}</TableCell>
                        <TableCell className="text-right font-mono">
                          ${gainer.price.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right">
                          <span className={`font-mono flex items-center justify-end gap-1 ${
                            gainer.change >= 0 ? 'text-emerald-600' : 'text-red-600'
                          }`}>
                            {gainer.change >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                            ${Math.abs(gainer.change).toFixed(2)}
                          </span>
                        </TableCell>
                        <TableCell className="text-right">
                          <Badge
                            className={`font-mono ${
                              gainer.pct_change >= 0
                                ? 'bg-emerald-100 text-emerald-700 border-emerald-200'
                                : 'bg-red-100 text-red-700 border-red-200'
                            }`}
                          >
                            {gainer.pct_change >= 0 ? '+' : ''}{gainer.pct_change.toFixed(2)}%
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        )}

        {/* Investments Tab */}
        {activeTab === 'investments' && (
          <div className="space-y-6">
            {/* Add Investment Form */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Add New Investment</CardTitle>
                <CardDescription>Record a customer's stock investment</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleAddInvestment} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-zinc-700">Customer Name</label>
                      <Input
                        placeholder="e.g. John Smith"
                        value={customerName}
                        onChange={(e) => setCustomerName(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-zinc-700">Stock Symbol</label>
                      <div className="flex gap-2">
                        <Input
                          placeholder="e.g. AAPL"
                          value={stockSymbol}
                          onChange={(e) => setStockSymbol(e.target.value.toUpperCase())}
                          className="font-mono"
                        />
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={handleFetchPrice}
                          className="whitespace-nowrap"
                        >
                          Get Price
                        </Button>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-zinc-700">Quantity</label>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="e.g. 10"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-zinc-700">Purchase Price ($)</label>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="e.g. 150.00"
                        value={purchasePrice}
                        onChange={(e) => setPurchasePrice(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-zinc-700">Purchase Date</label>
                      <Input
                        type="date"
                        value={purchaseDate}
                        onChange={(e) => setPurchaseDate(e.target.value)}
                      />
                    </div>
                  </div>
                  {formError && (
                    <p className="text-red-500 text-sm">{formError}</p>
                  )}
                  <Button type="submit" disabled={submitting}>
                    <Plus size={16} className="mr-2" />
                    {submitting ? 'Adding...' : 'Add Investment'}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Investments List */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl">Customer Investments</CardTitle>
                    <CardDescription>{investments.length} investment(s) recorded</CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={fetchInvestments}>
                    <RefreshCw size={16} className="mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {investments.length === 0 ? (
                  <div className="text-center py-12 text-zinc-500">
                    No investments recorded yet. Add one above.
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Customer</TableHead>
                        <TableHead>Symbol</TableHead>
                        <TableHead className="text-right">Quantity</TableHead>
                        <TableHead className="text-right">Purchase Price</TableHead>
                        <TableHead className="text-right">Total Invested</TableHead>
                        <TableHead>Purchase Date</TableHead>
                        <TableHead className="w-12"></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {investments.map((inv) => (
                        <TableRow key={inv.id}>
                          <TableCell className="font-medium">{inv.customer_name}</TableCell>
                          <TableCell>
                            <Badge variant="secondary" className="font-mono font-bold">
                              {inv.stock_symbol}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right font-mono">{inv.quantity}</TableCell>
                          <TableCell className="text-right font-mono">${inv.purchase_price.toFixed(2)}</TableCell>
                          <TableCell className="text-right font-mono">
                            ${(inv.quantity * inv.purchase_price).toFixed(2)}
                          </TableCell>
                          <TableCell>{inv.purchase_date}</TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDelete(inv.id)}
                              className="text-red-500 hover:text-red-700 hover:bg-red-50"
                            >
                              <Trash2 size={16} />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Portfolio Tab */}
        {activeTab === 'portfolio' && (
          <div className="space-y-6">
            {/* Summary Cards */}
            {portfolio && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-sm font-medium text-zinc-500">Total Invested</div>
                    <div className="text-2xl font-bold font-mono mt-1">
                      ${portfolio.total_invested.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-sm font-medium text-zinc-500">Current Value</div>
                    <div className="text-2xl font-bold font-mono mt-1">
                      ${portfolio.total_current_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-sm font-medium text-zinc-500">Total Gain/Loss</div>
                    <div className={`text-2xl font-bold font-mono mt-1 ${
                      portfolio.total_gain_loss >= 0 ? 'text-emerald-600' : 'text-red-600'
                    }`}>
                      {portfolio.total_gain_loss >= 0 ? '+' : ''}
                      ${portfolio.total_gain_loss.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-sm font-medium text-zinc-500">Return %</div>
                    <div className={`text-2xl font-bold font-mono mt-1 ${
                      portfolio.total_gain_loss_pct >= 0 ? 'text-emerald-600' : 'text-red-600'
                    }`}>
                      {portfolio.total_gain_loss_pct >= 0 ? '+' : ''}
                      {portfolio.total_gain_loss_pct.toFixed(2)}%
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Portfolio Table */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl">Portfolio Details</CardTitle>
                    <CardDescription>Investment performance with live prices</CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={fetchPortfolio}
                    disabled={portfolioLoading}
                  >
                    <RefreshCw size={16} className={`mr-2 ${portfolioLoading ? 'animate-spin' : ''}`} />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {portfolioLoading && !portfolio ? (
                  <div className="flex items-center justify-center py-12">
                    <RefreshCw size={24} className="animate-spin text-zinc-400 mr-3" />
                    <span className="text-zinc-500">Fetching live portfolio data...</span>
                  </div>
                ) : !portfolio || portfolio.portfolio.length === 0 ? (
                  <div className="text-center py-12 text-zinc-500">
                    No investments in portfolio. Add investments in the Investments tab.
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Customer</TableHead>
                        <TableHead>Symbol</TableHead>
                        <TableHead className="text-right">Qty</TableHead>
                        <TableHead className="text-right">Buy Price</TableHead>
                        <TableHead className="text-right">Current Price</TableHead>
                        <TableHead className="text-right">Invested</TableHead>
                        <TableHead className="text-right">Current Value</TableHead>
                        <TableHead className="text-right">Gain/Loss</TableHead>
                        <TableHead className="text-right">Return %</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {portfolio.portfolio.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell className="font-medium">{item.customer_name}</TableCell>
                          <TableCell>
                            <Badge variant="secondary" className="font-mono font-bold">
                              {item.stock_symbol}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right font-mono">{item.quantity}</TableCell>
                          <TableCell className="text-right font-mono">${item.purchase_price.toFixed(2)}</TableCell>
                          <TableCell className="text-right font-mono">${item.current_price.toFixed(2)}</TableCell>
                          <TableCell className="text-right font-mono">${item.invested_value.toFixed(2)}</TableCell>
                          <TableCell className="text-right font-mono">${item.current_value.toFixed(2)}</TableCell>
                          <TableCell className="text-right">
                            <span className={`font-mono flex items-center justify-end gap-1 ${
                              item.gain_loss >= 0 ? 'text-emerald-600' : 'text-red-600'
                            }`}>
                              {item.gain_loss >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                              ${Math.abs(item.gain_loss).toFixed(2)}
                            </span>
                          </TableCell>
                          <TableCell className="text-right">
                            <Badge
                              className={`font-mono ${
                                item.gain_loss_pct >= 0
                                  ? 'bg-emerald-100 text-emerald-700 border-emerald-200'
                                  : 'bg-red-100 text-red-700 border-red-200'
                              }`}
                            >
                              {item.gain_loss_pct >= 0 ? '+' : ''}{item.gain_loss_pct.toFixed(2)}%
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-zinc-100 border-t border-zinc-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-4 text-center text-sm text-zinc-500">
          NASDAQ Investment Tracker - Data sourced from Yahoo Finance
        </div>
      </footer>
    </div>
  )
}

export default App
