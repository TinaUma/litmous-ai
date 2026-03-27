import { useState } from 'react'
import { runComparison } from '../api/compare'
import type { ModelResult, CompareResponse } from '../api/compare'

const ZONE_STYLES: Record<string, string> = {
  Green:  'bg-green-100 text-green-800',
  Orange: 'bg-yellow-100 text-yellow-800',
  Red:    'bg-red-100 text-red-800',
}

const ZONE_LABELS: Record<string, string> = {
  Green:  'Зелёная',
  Orange: 'Оранжевая',
  Red:    'Красная',
}

function ScoreBar({ score }: { score: number }) {
  const color = score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-200 rounded-full h-2">
        <div className={`h-2 rounded-full transition-all ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-sm font-bold w-8 text-right">{score}</span>
    </div>
  )
}

function ResultCard({ result }: { result: ModelResult }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div>
          <span className="font-semibold text-gray-900">{result.display_name}</span>
          {result.is_free && (
            <span className="ml-2 px-1.5 py-0.5 text-xs bg-blue-100 text-blue-700 rounded">free</span>
          )}
          <span className="ml-2 text-xs text-gray-400">{result.elapsed_sec}s</span>
        </div>
        {result.zone && (
          <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${ZONE_STYLES[result.zone]}`}>
            {ZONE_LABELS[result.zone]}
          </span>
        )}
      </div>

      {/* Score bar */}
      {result.score !== null && (
        <div className="mb-3">
          <ScoreBar score={result.score} />
        </div>
      )}

      {/* Error */}
      {result.error && (
        <p className="text-sm text-red-600 mb-2">Ошибка: {result.error}</p>
      )}

      {/* Generated text */}
      {result.text && (
        <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
          {expanded ? result.text : result.text.slice(0, 300) + (result.text.length > 300 ? '…' : '')}
          {result.text.length > 300 && (
            <button
              onClick={() => setExpanded(v => !v)}
              className="ml-1 text-blue-600 hover:underline text-xs"
            >
              {expanded ? 'Свернуть' : 'Развернуть'}
            </button>
          )}
        </div>
      )}

      {/* Breakdown toggle */}
      {result.breakdown && (
        <details className="mt-3">
          <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-600">
            Детали скоринга
          </summary>
          <div className="mt-2 grid grid-cols-2 gap-1 text-xs text-gray-600">
            {Object.entries(result.breakdown).map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <span>{k}</span>
                <span className={v < 0 ? 'text-red-600 font-medium' : 'font-medium'}>{v > 0 ? `+${v}` : v}</span>
              </div>
            ))}
          </div>
          {result.ai_isms_found.length > 0 && (
            <div className="mt-2 pt-2 border-t border-gray-100">
              <span className="text-orange-600 font-medium">AI-штампы найдены: </span>
              <span className="text-orange-700">{result.ai_isms_found.join(', ')}</span>
            </div>
          )}
        </details>
      )}
    </div>
  )
}

export default function ComparePage() {
  const [prompt, setPrompt] = useState('')
  const [systemPrompt, setSystemPrompt] = useState('')
  const [freeOnly, setFreeOnly] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [response, setResponse] = useState<CompareResponse | null>(null)

  const handleRun = async () => {
    if (!prompt.trim()) return
    setLoading(true)
    setError(null)
    setResponse(null)
    try {
      const res = await runComparison({
        prompt: prompt.trim(),
        system_prompt: systemPrompt.trim() || undefined,
        free_only: freeOnly,
      })
      setResponse(res)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Неизвестная ошибка'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl">
      {/* Title */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Сравнение LLM</h1>
        <p className="text-sm text-gray-500 mt-1">Запустите один промпт через несколько моделей и сравните качество</p>
      </div>

      {/* Form */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Промпт *</label>
          <textarea
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            rows={4}
            placeholder="Тема: «...» Напиши пост для Telegram-канала..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">System prompt (опционально)</label>
          <textarea
            value={systemPrompt}
            onChange={e => setSystemPrompt(e.target.value)}
            rows={2}
            placeholder="Ты опытный редактор Telegram-канала..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
          />
        </div>

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
            <input
              type="checkbox"
              checked={freeOnly}
              onChange={e => setFreeOnly(e.target.checked)}
              className="rounded"
            />
            Только бесплатные модели
          </label>

          <button
            onClick={handleRun}
            disabled={loading || !prompt.trim()}
            className="flex items-center gap-2 px-5 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading && (
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
            )}
            {loading ? 'Битва в процессе...' : 'Запустить'}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Results */}
      {response && (
        <div>
          <div className="flex items-center gap-3 mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Результаты</h2>
            <span className="text-sm text-gray-500">
              {response.successful}/{response.total_models} успешно
            </span>
          </div>
          <div className="space-y-4">
            {response.results.map(r => (
              <ResultCard key={r.model_id} result={r} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
