import React from 'react';
import { LayoutDashboard, ShoppingBag, Settings, LogOut } from 'lucide-react';

const Sidebar = () => {
  return (
    <aside className="w-64 bg-slate-900 text-white h-screen fixed left-0 top-0 flex flex-col">
      <div className="p-6 border-b border-slate-800">
        <h1 className="text-2xl font-bold text-blue-500">Fixwell<span className="text-white">Hub</span></h1>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        <button className="w-full flex items-center gap-3 px-4 py-3 bg-blue-600 rounded-lg text-white font-medium">
          <LayoutDashboard size={20} />
          Visão Geral
        </button>
        
        <button className="w-full flex items-center gap-3 px-4 py-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition">
          <ShoppingBag size={20} />
          Produtos
        </button>

        <button className="w-full flex items-center gap-3 px-4 py-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition">
          <Settings size={20} />
          Configurações
        </button>
      </nav>

      <div className="p-4 border-t border-slate-800">
        <button className="flex items-center gap-3 px-4 py-3 text-red-400 hover:bg-red-900/20 w-full rounded-lg transition">
          <LogOut size={20} />
          Sair
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;