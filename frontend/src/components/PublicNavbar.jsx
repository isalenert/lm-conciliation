/**
 * Navbar para páginas públicas (Home)
 */

import { useNavigate } from 'react-router-dom';
import { Activity, LogIn, UserPlus } from 'lucide-react';

export default function PublicNavbar() {
  const navigate = useNavigate();

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <div 
          className="flex items-center gap-2 cursor-pointer"
          onClick={() => navigate('/')}
        >
          <Activity className="w-8 h-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-blue-600">LM Conciliation</h1>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/login')}
            className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            <LogIn className="w-4 h-4" />
            Entrar
          </button>
          <button
            onClick={() => navigate('/signup')}
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <UserPlus className="w-4 h-4" />
            Criar Conta
          </button>
        </div>
      </div>
    </header>
  );
}
