/**
 * Página de Recuperação de Senha
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { requestPasswordReset } from '../services/api';
import { Mail, ArrowLeft, CheckCircle, AlertCircle } from 'lucide-react';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '', token: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '', token: '' });

    try {
      const response = await requestPasswordReset(email);
      
      setMessage({
        type: 'success',
        text: response.message,
        token: response.token, // Em desenvolvimento apenas
      });
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao solicitar reset de senha',
        token: '',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-600">LM Conciliation</h1>
          <p className="text-gray-600 mt-2">Recuperar senha</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8">
          {message.text && (
            <div
              className={`mb-6 p-4 rounded-lg flex items-start ${
                message.type === 'success'
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-red-50 border border-red-200'
              }`}
            >
              {message.type === 'success' ? (
                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
              )}
              <div className="flex-1">
                <p
                  className={
                    message.type === 'success' ? 'text-green-700' : 'text-red-700'
                  }
                >
                  {message.text}
                </p>
                {message.token && (
                  <div className="mt-3">
                    <p className="text-sm text-green-600 font-semibold mb-2">
                      Token para desenvolvimento:
                    </p>
                    <code className="block p-2 bg-white border border-green-300 rounded text-xs break-all">
                      {message.token}
                    </code>
                    <Link
                      to={`/reset-password?token=${message.token}`}
                      className="mt-2 inline-block text-sm text-blue-600 hover:text-blue-700"
                    >
                      → Ir para página de reset
                    </Link>
                  </div>
                )}
              </div>
            </div>
          )}

          {!message.text && (
            <>
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Mail className="w-8 h-8 text-blue-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Esqueceu sua senha?
                </h2>
                <p className="text-sm text-gray-600 mt-2">
                  Digite seu email para receber instruções de recuperação
                </p>
              </div>

              <form onSubmit={handleSubmit}>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="seu@email.com"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Enviando...' : 'Enviar Instruções'}
                </button>
              </form>
            </>
          )}
        </div>

        <div className="mt-6 text-center">
          <Link
            to="/login"
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Voltar para login
          </Link>
        </div>
      </div>
    </div>
  );
}
