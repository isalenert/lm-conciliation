/**
 * Página de Resultados da Conciliação - MELHORADA
 */

import { useLocation, useNavigate } from 'react-router-dom';
import { CheckCircle, AlertCircle, Activity, TrendingUp, PieChart as PieChartIcon } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import Navbar from '../components/Navbar';

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const { results } = location.state || {};

  if (!results) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <p className="text-red-700">Nenhum resultado encontrado</p>
          </div>
        </div>
      </div>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  const formatValue = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const hasPending = results.bank_only.length > 0 || results.internal_only.length > 0;

  // Dados para gráficos
  const pieData = [
    { name: 'Conciliadas', value: results.summary.matched_count, color: '#10b981' },
    { name: 'Pendentes Banco', value: results.summary.bank_only_count, color: '#f59e0b' },
    { name: 'Pendentes Sistema', value: results.summary.internal_only_count, color: '#f97316' },
  ];

  const barData = [
    { name: 'Banco', total: results.summary.total_bank_transactions },
    { name: 'Sistema', total: results.summary.total_internal_transactions },
  ];

  const statsCards = [
    {
      label: 'Conciliadas',
      value: results.summary.matched_count,
      color: 'green',
      icon: CheckCircle,
    },
    {
      label: 'Pendentes (Banco)',
      value: results.summary.bank_only_count,
      color: 'yellow',
      icon: AlertCircle,
    },
    {
      label: 'Pendentes (Sistema)',
      value: results.summary.internal_only_count,
      color: 'orange',
      icon: AlertCircle,
    },
    {
      label: 'Taxa de Match',
      value: `${results.summary.match_rate.toFixed(1)}%`,
      color: 'blue',
      icon: TrendingUp,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 flex items-center">
            <Activity className="w-8 h-8 mr-3 text-blue-600" />
            Resultados da Conciliação
          </h2>
          <p className="text-gray-600 mt-2">
            Análise completa com gráficos e detalhes
          </p>
        </div>

        {/* Cards de Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {statsCards.map((stat, index) => {
            const Icon = stat.icon;
            const colorClasses = {
              green: 'bg-green-50 text-green-600 border-green-200',
              yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
              orange: 'bg-orange-50 text-orange-600 border-orange-200',
              blue: 'bg-blue-50 text-blue-600 border-blue-200',
            };
            return (
              <div
                key={index}
                className={`${colorClasses[stat.color]} border-2 rounded-lg shadow-md p-6 text-center`}
              >
                <Icon className="w-8 h-8 mx-auto mb-2" />
                <p className="text-3xl font-bold">{stat.value}</p>
                <p className="text-sm mt-1">{stat.label}</p>
              </div>
            );
          })}
        </div>

        {/* Gráficos */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Gráfico de Pizza */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              <PieChartIcon className="w-5 h-5 mr-2 text-blue-600" />
              Distribuição de Transações
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Gráfico de Barras */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              <Activity className="w-5 h-5 mr-2 text-blue-600" />
              Volume por Fonte
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="total" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Resumo Detalhado */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h3 className="text-xl font-semibold mb-4">📊 Resumo Detalhado</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Total Conciliadas</p>
              <p className="text-2xl font-bold text-green-600">
                {results.summary.matched_count}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {((results.summary.matched_count / (results.summary.total_bank_transactions + results.summary.total_internal_transactions)) * 100).toFixed(1)}% do total
              </p>
            </div>
            <div className="p-4 bg-yellow-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Pendentes para Revisão</p>
              <p className="text-2xl font-bold text-yellow-600">
                {results.summary.bank_only_count + results.summary.internal_only_count}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Banco: {results.summary.bank_only_count} | Sistema: {results.summary.internal_only_count}
              </p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Eficiência</p>
              <p className="text-2xl font-bold text-blue-600">
                {results.summary.match_rate.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Taxa de sucesso automático
              </p>
            </div>
          </div>
        </div>

        {/* Transações Conciliadas */}
        <div className="bg-white rounded-lg shadow-md mb-8">
          <div className="px-6 py-4 border-b">
            <h3 className="text-xl font-semibold flex items-center text-green-600">
              <CheckCircle className="w-5 h-5 mr-2" />
              Transações Conciliadas ({results.matched.length})
            </h3>
          </div>
          <div className="p-6 max-h-96 overflow-y-auto">
            <div className="space-y-4">
              {results.matched.map((match, index) => (
                <div key={index} className="border-2 border-green-200 rounded-lg p-4 bg-green-50">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs font-semibold text-gray-500 mb-2">BANCO</p>
                      <p className="text-sm">
                        <strong>Data:</strong> {formatDate(match.bank_transaction.Data)}
                      </p>
                      <p className="text-sm">
                        <strong>Valor:</strong> {formatValue(match.bank_transaction.Valor)}
                      </p>
                      <p className="text-sm">
                        <strong>Descrição:</strong> {match.bank_transaction.Descricao}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-gray-500 mb-2">SISTEMA</p>
                      <p className="text-sm">
                        <strong>Data:</strong> {formatDate(match.internal_transaction.Data)}
                      </p>
                      <p className="text-sm">
                        <strong>Valor:</strong> {formatValue(match.internal_transaction.Valor)}
                      </p>
                      <p className="text-sm">
                        <strong>Descrição:</strong> {match.internal_transaction.Descricao}
                      </p>
                    </div>
                  </div>
                  <div className="mt-2 flex justify-between items-center">
                    <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded">
                      Confiança: {(match.confidence * 100).toFixed(1)}%
                    </span>
                    <span className="text-xs text-gray-500">
                      Match Automático
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Pendentes */}
        {hasPending && (
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Banco */}
            {results.bank_only.length > 0 && (
              <div className="bg-white rounded-lg shadow-md">
                <div className="px-6 py-4 border-b">
                  <h3 className="text-xl font-semibold flex items-center text-yellow-600">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    Pendentes no Banco ({results.bank_only.length})
                  </h3>
                </div>
                <div className="p-6 max-h-96 overflow-y-auto">
                  <div className="space-y-3">
                    {results.bank_only.map((transaction, index) => (
                      <div key={index} className="border-2 border-yellow-200 rounded-lg p-4 bg-yellow-50">
                        <p className="text-sm">
                          <strong>Data:</strong> {formatDate(transaction.Data)}
                        </p>
                        <p className="text-sm">
                          <strong>Valor:</strong> {formatValue(transaction.Valor)}
                        </p>
                        <p className="text-sm">
                          <strong>Descrição:</strong> {transaction.Descricao}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sistema */}
            {results.internal_only.length > 0 && (
              <div className="bg-white rounded-lg shadow-md">
                <div className="px-6 py-4 border-b">
                  <h3 className="text-xl font-semibold flex items-center text-orange-600">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    Pendentes no Sistema ({results.internal_only.length})
                  </h3>
                </div>
                <div className="p-6 max-h-96 overflow-y-auto">
                  <div className="space-y-3">
                    {results.internal_only.map((transaction, index) => (
                      <div key={index} className="border-2 border-orange-200 rounded-lg p-4 bg-orange-50">
                        <p className="text-sm">
                          <strong>Data:</strong> {formatDate(transaction.Data)}
                        </p>
                        <p className="text-sm">
                          <strong>Valor:</strong> {formatValue(transaction.Valor)}
                        </p>
                        <p className="text-sm">
                          <strong>Descrição:</strong> {transaction.Descricao}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Botão de Conciliação Manual */}
        {results.reconciliation_id && hasPending && (
          <div className="mb-8 p-6 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border-2 border-yellow-300">
            <h3 className="font-semibold text-yellow-900 mb-2 text-lg">
              ⚠️ Ação Necessária: Transações Pendentes
            </h3>
            <p className="text-sm text-yellow-800 mb-4">
              Foram identificadas <strong>{results.summary.bank_only_count + results.summary.internal_only_count} transações pendentes</strong> que não puderam ser conciliadas automaticamente.
              Você pode criar matches manuais para aumentar a taxa de conciliação.
            </p>
            <button
              onClick={() => navigate(`/manual-reconciliation/${results.reconciliation_id}`)}
              className="px-6 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 font-semibold shadow-md hover:shadow-lg transition-all"
            >
              🔗 Ir para Conciliação Manual
            </button>
          </div>
        )}

        {/* Botões de Ação */}
        <div className="flex gap-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex-1 py-3 px-6 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold shadow-md hover:shadow-lg transition-all"
          >
            Voltar ao Dashboard
          </button>
          <button
            onClick={() => navigate('/history')}
            className="flex-1 py-3 px-6 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold shadow-md hover:shadow-lg transition-all"
          >
            Ver Histórico
          </button>
          <button
            onClick={() => navigate('/upload')}
            className="flex-1 py-3 px-6 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-semibold shadow-md hover:shadow-lg transition-all"
          >
            Nova Conciliação
          </button>
        </div>
      </main>
    </div>
  );
}
