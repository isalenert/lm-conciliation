/**
 * Página de Histórico de Conciliações
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getHistory } from '../services/api';
import { Calendar, FileText, TrendingUp, Eye, Loader } from 'lucide-react';
import Navbar from '../components/Navbar';

export default function History() {
  const navigate = useNavigate();
  const [reconciliations, setReconciliations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getHistory();
      setReconciliations(data);
    } catch (err) {
      setError('Erro ao carregar histórico: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getMatchRateColor = (rate) => {
    if (rate >= 90) return 'text-green-600 bg-green-100';
    if (rate >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex items-center justify-center h-96">
          <Loader className="w-8 h-8 text-blue-600 animate-spin" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Histórico de Conciliações</h2>
          <p className="text-gray-600 mt-2">
            Veja todas as suas conciliações anteriores
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {reconciliations.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              Nenhuma conciliação ainda
            </h3>
            <p className="text-gray-500 mb-6">
              Faça sua primeira conciliação para ver o histórico aqui
            </p>
            <button
              onClick={() => navigate('/upload')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Nova Conciliação
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {reconciliations.map((reconciliation) => (
              <div
                key={reconciliation.id}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <FileText className="w-5 h-5 text-blue-600" />
                      <h3 className="text-lg font-semibold text-gray-900">
                        Conciliação #{reconciliation.id}
                      </h3>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-semibold ${getMatchRateColor(
                          reconciliation.match_rate
                        )}`}
                      >
                        {reconciliation.match_rate.toFixed(1)}% match
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Arquivos</p>
                        <p className="font-medium text-gray-900">
                          {reconciliation.bank_file_name}
                        </p>
                        <p className="font-medium text-gray-900">
                          {reconciliation.internal_file_name}
                        </p>
                      </div>

                      <div>
                        <p className="text-gray-500">Transações</p>
                        <p className="font-medium text-gray-900">
                          Banco: {reconciliation.total_bank_transactions}
                        </p>
                        <p className="font-medium text-gray-900">
                          Sistema: {reconciliation.total_internal_transactions}
                        </p>
                      </div>

                      <div>
                        <p className="text-gray-500">Resultados</p>
                        <p className="font-medium text-green-600">
                          ✓ {reconciliation.matched_count} conciliadas
                        </p>
                        <p className="font-medium text-yellow-600">
                          ⚠ {reconciliation.total_bank_transactions + reconciliation.total_internal_transactions - reconciliation.matched_count} pendentes
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 mt-3 text-sm text-gray-500">
                      <Calendar className="w-4 h-4" />
                      {formatDate(reconciliation.created_at)}
                    </div>
                  </div>

                  <button
                    onClick={() => navigate(`/history/${reconciliation.id}`)}
                    className="ml-6 flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    Ver Detalhes
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
