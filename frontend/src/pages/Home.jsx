/**
 * Página Home/Landing Page
 */

import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useEffect } from 'react';
import PublicNavbar from '../components/PublicNavbar';
import { Zap, Target, BarChart3, CheckCircle, ArrowRight } from 'lucide-react';

export default function Home() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <PublicNavbar />

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Conciliação Bancária
            <span className="text-blue-600"> Automatizada</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Sistema inteligente para conciliar extratos bancários com seus registros internos.
            Rápido, preciso e fácil de usar.
          </p>
          <button
            onClick={() => navigate('/signup')}
            className="px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-all shadow-lg hover:shadow-xl flex items-center gap-2 mx-auto"
          >
            Começar Agora - É Grátis!
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>

        {/* Features */}
        <div className="mt-20 grid md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <Zap className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Rápido</h3>
            <p className="text-gray-600">
              Processe milhares de transações em segundos com nosso algoritmo inteligente
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-16 h-16 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <Target className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Preciso</h3>
            <p className="text-gray-600">
              Matching automático com tolerância configurável e validação manual
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <BarChart3 className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Completo</h3>
            <p className="text-gray-600">
              Dashboard com gráficos, histórico e conciliação manual
            </p>
          </div>
        </div>

        {/* Como Funciona */}
        <div className="mt-20 bg-white rounded-xl shadow-lg p-12">
          <h2 className="text-3xl font-bold text-center mb-12">Como Funciona</h2>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                1
              </div>
              <h3 className="font-semibold mb-2">Upload</h3>
              <p className="text-sm text-gray-600">
                Faça upload do extrato bancário e arquivo do sistema
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                2
              </div>
              <h3 className="font-semibold mb-2">Mapeamento</h3>
              <p className="text-sm text-gray-600">
                Mapeie as colunas dos seus arquivos
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                3
              </div>
              <h3 className="font-semibold mb-2">Conciliação</h3>
              <p className="text-sm text-gray-600">
                Algoritmo processa e encontra matches automaticamente
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                <CheckCircle className="w-8 h-8" />
              </div>
              <h3 className="font-semibold mb-2">Resultado</h3>
              <p className="text-sm text-gray-600">
                Veja gráficos, detalhes e faça matches manuais
              </p>
            </div>
          </div>
        </div>

        {/* CTA Final */}
        <div className="mt-20 text-center bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-12 text-white shadow-2xl">
          <h2 className="text-3xl font-bold mb-4">
            Pronto para Automatizar sua Conciliação?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Crie sua conta gratuitamente e comece agora mesmo
          </p>
          <button
            onClick={() => navigate('/signup')}
            className="px-8 py-4 bg-white text-blue-600 text-lg font-semibold rounded-lg hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl"
          >
            Criar Conta Grátis
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white mt-20 py-8 border-t">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-600">
          <p>&copy; 2025 LM Conciliation. Sistema de Conciliação Bancária.</p>
        </div>
      </footer>
    </div>
  );
}
