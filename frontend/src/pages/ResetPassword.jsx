/**
 * Página de Reset de Senha
 */

import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { resetPassword } from '../services/api';
import { Lock, CheckCircle, AlertCircle } from 'lucide-react';

export default function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    if (!token) {
      setMessage({
        type: 'error',
        text: 'Token inválido ou ausente',
      });
    }
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    if (formData.password !== formData.confirmPassword) {
      setMessage({ type: 'error', text: 'As senhas não coincidem' });
      return;
    }

    if (formData.password.length < 6) {
      setMessage({
        type: 'error',
        text: 'A senha deve ter no mínimo 6 caracteres',
      });
      return;
    }

    setLoading(true);

    try {
      await resetPassword(token, formData.password);

      setMessage({
        type: 'success',
        text: 'Senha alterada com sucesso! Redirecionando...',
      });

      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao resetar senha',
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
          <p className="text-gray-600 mt-2">Redefinir senha</p>
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
                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 mr-3" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 mr-3" />
              )}
              <p
                className={
                  message.type === 'success' ? 'text-green-700' : 'text-red-700'
                }
              >
                {message.text}
              </p>
            </div>
          )}

          {!message.text && token && (
            <>
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Lock className="w-8 h-8 text-blue-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Nova Senha
                </h2>
                <p className="text-sm text-gray-600 mt-2">
                  Digite sua nova senha abaixo
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nova Senha
                  </label>
                  <input
                    type="password"
                    required
                    value={formData.password}
                    onChange={(e) =>
                      setFormData({ ...formData, password: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Mínimo 6 caracteres"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confirmar Senha
                  </label>
                  <input
                    type="password"
                    required
                    value={formData.confirmPassword}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        confirmPassword: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Digite a senha novamente"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Alterando...' : 'Alterar Senha'}
                </button>
              </form>
            </>
          )}

          {!token && (
            <div className="text-center">
              <p className="text-gray-600 mb-4">
                Token inválido. Solicite um novo reset de senha.
              </p>
              <Link
                to="/forgot-password"
                className="text-blue-600 hover:text-blue-700 font-semibold"
              >
                Solicitar novo token
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
