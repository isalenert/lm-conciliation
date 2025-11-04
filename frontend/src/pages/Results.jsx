/**
 * Página de Resultados da Conciliação
 */

import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, AlertTriangle, ArrowLeft, Download } from 'lucide-react';
import Navbar from '../components/Navbar';

<Navbar />

function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { results } = location.state || {};
  const [activeTab, setActiveTab] = useState('matched');

  if (!results) {
    navigate('/');
    return null;
  }

  const { matched, bank_only, internal_only, summary } = results;

  const downloadCSV = () => {
    const rows = [
      ['Tipo', 'Data', 'Valor', 'Descrição', 'Status'],
      ...matched.map((m) => [
        'Match',
        m.bank_transaction.Data || '',
        m.bank_transaction.Valor || '',
        m.bank_transaction.Descricao || '',
        `${(m.confidence * 100).toFixed(1)}%`,
      ]),
      ...bank_only.map((t) => [
        'Pendente Banco',
        t.Data || '',
        t.Valor || '',
        t.Descricao || '',
        '-',
      ]),
      ...internal_only.map((t) => [
        'Pendente Sistema',
        t.Data || '',
        t.Valor || '',
        t.Descricao || '',
        '-',
      ]),
    ];

    const csvContent = rows.map((row) => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'conciliacao_resultado.csv';
    a.click();
  };

  const renderTable = (data, type) => {
    if (data.length === 0) {
      return (
        <div className="text-center py-12 text-gray-500">
          <p>Nenhuma transação {type === 'matched' ? 'conciliada' : 'pendente'}</p>
        </div>
      );
    }

    if (type === 'matched') {
      return (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrição Banco</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrição Sistema</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confiança</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.map((match, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {match.bank_transaction.Data}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    R$ {match.bank_transaction.Valor?.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {match.bank_transaction.Descricao}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {match.internal_transaction.Descricao}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                      {(match.confidence * 100).toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrição</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((transaction, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {transaction.Data}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  R$ {transaction.Valor?.toFixed(2)}
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  {transaction.Descricao}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Resultados da Conciliação
          </h1>
          <p className="text-gray-600 mt-1">
            Análise completa das transações processadas
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Taxa de Match</p>
                <p className="text-3xl font-bold text-green-600">
                  {summary.match_rate.toFixed(1)}%
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {summary.matched_count} de {summary.total_bank_transactions}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Conciliadas</p>
                <p className="text-3xl font-bold text-blue-600">
                  {summary.matched_count}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-blue-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Transações pareadas</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Pendentes Banco</p>
                <p className="text-3xl font-bold text-yellow-600">
                  {summary.bank_only_count}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-yellow-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Apenas no banco</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Pendentes Sistema</p>
                <p className="text-3xl font-bold text-orange-600">
                  {summary.internal_only_count}
                </p>
              </div>
              <XCircle className="w-8 h-8 text-orange-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Apenas no sistema</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('matched')}
                className={`border-b-2 py-4 px-1 font-medium ${
                  activeTab === 'matched'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Conciliadas ({matched.length})
              </button>
              <button
                onClick={() => setActiveTab('bank_only')}
                className={`border-b-2 py-4 px-1 font-medium ${
                  activeTab === 'bank_only'
                    ? 'border-yellow-500 text-yellow-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Pendentes Banco ({bank_only.length})
              </button>
              <button
                onClick={() => setActiveTab('internal_only')}
                className={`border-b-2 py-4 px-1 font-medium ${
                  activeTab === 'internal_only'
                    ? 'border-orange-500 text-orange-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Pendentes Sistema ({internal_only.length})
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'matched' && renderTable(matched, 'matched')}
            {activeTab === 'bank_only' && renderTable(bank_only, 'pending')}
            {activeTab === 'internal_only' && renderTable(internal_only, 'pending')}
          </div>
        </div>

        <div className="mt-8 flex flex-col sm:flex-row gap-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center justify-center px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Nova Conciliação
          </button>

          <button
            onClick={downloadCSV}
            className="flex items-center justify-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Download className="w-5 h-5 mr-2" />
            Baixar Resultados (CSV)
          </button>
        </div>

        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-3">📊 Resumo Detalhado</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-800">
            <div>
              <p><strong>Total de transações do banco:</strong> {summary.total_bank_transactions}</p>
              <p><strong>Total de transações do sistema:</strong> {summary.total_internal_transactions}</p>
            </div>
            <div>
              <p><strong>Transações conciliadas:</strong> {summary.matched_count}</p>
              <p><strong>Taxa de sucesso:</strong> {summary.match_rate.toFixed(2)}%</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default ResultsPage;
