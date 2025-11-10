/**
 * Página de Conciliação Manual
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPendingTransactions, createManualMatch } from '../services/api';
import { ArrowRight, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import Navbar from '../components/Navbar';

export default function ManualReconciliation() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matching, setMatching] = useState(false);
  
  const [selectedBank, setSelectedBank] = useState(null);
  const [selectedInternal, setSelectedInternal] = useState(null);

  useEffect(() => {
    loadPending();
  }, [id]);

  const loadPending = async () => {
    try {
      setLoading(true);
      setError('');
      const pendingData = await getPendingTransactions(id);
      setData(pendingData);
    } catch (err) {
      setError('Erro ao carregar transações pendentes: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMatch = async () => {
    if (!selectedBank || !selectedInternal) {
      setError('Selecione uma transação de cada lado');
      return;
    }

    try {
      setMatching(true);
      setError('');

      await createManualMatch({
        reconciliation_id: parseInt(id),
        bank_transaction_id: selectedBank,
        internal_transaction_id: selectedInternal,
      });

      // Recarregar transações pendentes
      await loadPending();
      
      // Limpar seleção
      setSelectedBank(null);
      setSelectedInternal(null);

      // Mostrar mensagem de sucesso
      alert('Match manual criado com sucesso!');

    } catch (err) {
      setError('Erro ao criar match: ' + err.response?.data?.detail || err.message);
    } finally {
      setMatching(false);
    }
  };

  const handleFinish = () => {
   navigate(`/history/${id}`);
  };

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

  if (error && !data) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  const noPending = data.bank_pending.length === 0 && data.internal_pending.length === 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Conciliação Manual</h2>
          <p className="text-gray-600 mt-2">
            Selecione uma transação de cada lado para criar um match manual
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 mr-3" />
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {noPending ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              Todas as transações foram conciliadas!
            </h3>
            <p className="text-gray-500 mb-6">
              Não há mais transações pendentes nesta conciliação
            </p>
            <button
              onClick={handleFinish}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Ver Resultado Final
            </button>
          </div>
        ) : (
          <>
            {/* Contador de Pendentes */}
            <div className="grid grid-cols-2 gap-6 mb-6">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-yellow-600">
                  {data.bank_pending.length}
                </p>
                <p className="text-sm text-gray-600 mt-1">Pendentes (Banco)</p>
              </div>
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-orange-600">
                  {data.internal_pending.length}
                </p>
                <p className="text-sm text-gray-600 mt-1">Pendentes (Sistema)</p>
              </div>
            </div>

            {/* Listas de Transações */}
            <div className="grid md:grid-cols-2 gap-6 mb-6">
              {/* Banco */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4 text-yellow-600">
                  📊 Transações do Banco
                </h3>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {data.bank_pending.map((transaction) => (
                    <div
                      key={transaction.id}
                      onClick={() => setSelectedBank(transaction.id)}
                      className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        selectedBank === transaction.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-sm font-medium text-gray-900">
                          {formatDate(transaction.date)}
                        </span>
                        <span className="text-sm font-bold text-gray-900">
                          {formatValue(transaction.value)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {transaction.description}
                      </p>
                      {selectedBank === transaction.id && (
                        <div className="mt-2 flex items-center text-blue-600 text-sm">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Selecionado
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Sistema Interno */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4 text-orange-600">
                  💻 Transações do Sistema
                </h3>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {data.internal_pending.map((transaction) => (
                    <div
                      key={transaction.id}
                      onClick={() => setSelectedInternal(transaction.id)}
                      className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        selectedInternal === transaction.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-sm font-medium text-gray-900">
                          {formatDate(transaction.date)}
                        </span>
                        <span className="text-sm font-bold text-gray-900">
                          {formatValue(transaction.value)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {transaction.description}
                      </p>
                      {selectedInternal === transaction.id && (
                        <div className="mt-2 flex items-center text-blue-600 text-sm">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Selecionado
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Botões de Ação */}
            <div className="flex gap-4">
              <button
                onClick={handleMatch}
                disabled={!selectedBank || !selectedInternal || matching}
                className="flex-1 py-3 px-6 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white font-semibold rounded-lg flex items-center justify-center transition-colors"
              >
                {matching ? (
                  <>
                    <Loader className="w-5 h-5 mr-2 animate-spin" />
                    Criando Match...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5 mr-2" />
                    Criar Match Manual
                  </>
                )}
              </button>

              <button
                onClick={handleFinish}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
              >
                Finalizar
                <ArrowRight className="w-5 h-5 ml-2" />
              </button>
            </div>

            {/* Instruções */}
            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h3 className="font-semibold text-blue-900 mb-2">📋 Instruções:</h3>
              <ol className="list-decimal list-inside text-sm text-blue-800 space-y-1">
                <li>Clique em uma transação do banco (amarelo)</li>
                <li>Clique em uma transação do sistema (laranja)</li>
                <li>Clique em "Criar Match Manual" para conciliar</li>
                <li>Repita para outras transações pendentes</li>
                <li>Clique em "Finalizar" quando terminar</li>
              </ol>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
