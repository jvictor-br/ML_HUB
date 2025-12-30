import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  ShoppingBag, 
  Settings, 
  LogOut, 
  Package, 
  RefreshCw, 
  User, 
  Lock, 
  AlertCircle,
  ChevronRight,
  ExternalLink,
  Edit
} from 'lucide-react';

const API_URL = 'http://127.0.0.1:8000';

const Button = ({ children, onClick, variant = 'primary', className = '', loading = false, ...props }) => {
  const baseStyle = "flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-all focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 shadow-sm hover:shadow-md",
    outline: "bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 focus:ring-gray-200 shadow-sm",
    danger: "bg-red-50 text-red-600 hover:bg-red-100 focus:ring-red-200",
    ghost: "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
  };

  return (
    <button 
      onClick={onClick} 
      className={`${baseStyle} ${variants[variant]} ${className}`}
      disabled={loading}
      {...props}
    >
      {loading && <RefreshCw className="animate-spin" size={16} />}
      {children}
    </button>
  );
};

const Input = ({ label, type = "text", value, onChange, placeholder, icon: Icon }) => (
  <div className="space-y-1.5">
    {label && <label className="text-sm font-semibold text-gray-700 ml-1">{label}</label>}
    <div className="relative group">
      {Icon && (
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-blue-500 transition-colors">
          <Icon size={18} />
        </div>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full border border-gray-300 rounded-xl py-3 ${Icon ? 'pl-10' : 'pl-4'} pr-4 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all`}
      />
    </div>
  </div>
);

const LoginScreen = ({ onLogin }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleLogin = async () => {
    const formData = new URLSearchParams();
    formData.append('username', email); // API de login espera 'username' para o campo de email
    formData.append('password', password);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Falha na autenticação');
    }

    const data = await response.json();
    onLogin(data.access_token);
  };

  const handleRegister = async () => {
    if (password.length < 6) {
      throw new Error("A senha deve ter pelo menos 6 caracteres.");
    }
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Falha no registro.');
    }
    
    setSuccess('Usuário criado com sucesso! Faça o login.');
    setIsRegister(false); // Volta para a tela de login
    // Limpa os campos para o login
    setUsername('');
    setPassword('');
    // O email é mantido para conveniência
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      if (isRegister) {
        await handleRegister();
      } else {
        await handleLogin();
      }
    } catch (err) {
      console.error(err);
      setError(err.message || 'Ocorreu um erro. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsRegister(!isRegister);
    setError('');
    setSuccess('');
    // Limpar campos ao trocar de modo
    setUsername('');
    setEmail('');
    setPassword('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4 font-sans text-gray-900">
      <div className="bg-white max-w-md w-full rounded-2xl shadow-xl shadow-blue-900/5 p-8 space-y-6 border border-white/50 backdrop-blur-sm">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-100 text-blue-600 mb-2">
            <LayoutDashboard size={24} />
          </div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Fixwell<span className="text-blue-600">Hub</span></h1>
          <p className="text-gray-500">{isRegister ? 'Crie sua conta para começar' : 'Faça login para gerenciar sua operação'}</p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-xl flex items-start gap-3 text-sm border border-red-100 animate-in fade-in slide-in-from-top-2">
            <AlertCircle size={18} className="shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="bg-emerald-50 text-emerald-600 p-4 rounded-xl flex items-start gap-3 text-sm border border-emerald-100 animate-in fade-in slide-in-from-top-2">
            <AlertCircle size={18} className="shrink-0 mt-0.5" />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {isRegister && (
            <Input 
              label="Nome de Usuário" 
              placeholder="seu_usuario" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)}
              icon={User}
            />
          )}
          <Input 
            label="Email" 
            placeholder="seu@email.com" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)}
            icon={User}
          />
          <Input 
            label="Senha" 
            type="password" 
            placeholder="••••••••" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)}
            icon={Lock}
          />
          
          <Button type="submit" className="w-full py-3.5 text-lg shadow-blue-500/20 shadow-lg hover:shadow-blue-500/30 hover:-translate-y-0.5 transition-transform" loading={loading}>
            {loading ? (isRegister ? 'Criando conta...' : 'Autenticando...') : (isRegister ? 'Criar Conta' : 'Acessar Painel')}
          </Button>
        </form>

        <p className="text-center text-sm text-gray-600 pt-4 border-t border-gray-100">
          {isRegister ? 'Já tem uma conta? ' : 'Ainda não tem uma conta? '}
          <button onClick={toggleMode} className="font-semibold text-blue-600 hover:text-blue-700 underline-offset-2 hover:underline focus:outline-none">
            {isRegister ? 'Faça Login' : 'Cadastre-se'}
          </button>
        </p>
      </div>
    </div>
  );
};

const Sidebar = ({ activeTab, setActiveTab, onLogout }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Visão Geral', icon: LayoutDashboard },
    { id: 'products', label: 'Produtos', icon: ShoppingBag },
    { id: 'settings', label: 'Configurações', icon: Settings },
  ];

  return (
    <aside className="w-72 bg-slate-900 text-slate-300 h-screen fixed left-0 top-0 flex flex-col z-20 border-r border-slate-800">
      <div className="p-8 pb-6">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white">
            <Package size={18} fill="currentColor" className="text-blue-200" />
          </div>
          Fixwell
        </h1>
        <p className="text-xs font-medium text-slate-500 mt-2 ml-1">PAINEL ADMINISTRATIVO</p>
      </div>

      <nav className="flex-1 px-4 py-4 space-y-1.5 overflow-y-auto">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-xl font-medium transition-all duration-200 group relative overflow-hidden ${
              activeTab === item.id 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' 
                : 'hover:bg-slate-800 hover:text-white'
            }`}
          >
            <item.icon size={20} className={activeTab === item.id ? 'text-blue-200' : 'text-slate-500 group-hover:text-white transition-colors'} />
            <span className="relative z-10">{item.label}</span>
            {activeTab === item.id && <ChevronRight size={16} className="ml-auto text-blue-300" />}
          </button>
        ))}
      </nav>

      <div className="p-4 mt-auto border-t border-slate-800 bg-slate-950/50">
        <div className="flex items-center gap-3 mb-4 p-2 rounded-lg bg-slate-900/50 border border-slate-800">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center font-bold text-white text-xs shadow-inner">
            AD
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">Admin User</p>
            <p className="text-xs text-slate-500 truncate">admin@fixwell.com</p>
          </div>
        </div>
        <Button variant="danger" onClick={onLogout} className="w-full text-sm py-2.5 bg-slate-800/50 border border-slate-700 hover:bg-red-500/10 hover:border-red-500/50 hover:text-red-400">
          <LogOut size={16} />
          Sair do Sistema
        </Button>
      </div>
    </aside>
  );
};

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('access_token'));
  const [activeTab, setActiveTab] = useState('products');
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    if (token) {
      localStorage.setItem('access_token', token);
      fetchProducts();
    } else {
      localStorage.removeItem('access_token');
    }
  }, [token]);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/products/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.status === 401) {
        setToken(null);
        return;
      }
      
      const data = await response.json();
      setProducts(data);
    } catch (error) {
      console.error("Erro ao carregar produtos:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      // Usando o ID da loja que obtivemos no teste anterior
      const STORE_ID = "2698576402"; 
      
      const response = await fetch(`${API_URL}/products/sync/${STORE_ID}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        await fetchProducts();
        alert("Sincronização realizada com sucesso!");
      } else {
        const err = await response.json();
        alert(`Erro: ${err.detail?.error || 'Falha na sincronização'}`);
      }
    } catch (error) {
      alert("Erro de conexão. O backend está rodando?");
    } finally {
      setSyncing(false);
    }
  };

  if (!token) return <LoginScreen onLogin={setToken} />;

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans text-slate-900">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} onLogout={() => setToken(null)} />

      <main className="flex-1 ml-72 p-8 h-screen overflow-y-auto">
        <div className="max-w-7xl mx-auto space-y-8 pb-10">
          
          {activeTab === 'products' && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6">
              
              <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-white p-6 rounded-2xl shadow-sm border border-slate-200/60">
                <div className="space-y-1">
                  <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2.5">
                    <ShoppingBag className="text-blue-600" size={28} /> 
                    Meus Produtos
                  </h2>
                  <p className="text-slate-500">Gerencie seu catálogo e sincronize com o Mercado Livre</p>
                </div>
                
                <div className="flex gap-3">
                   <Button variant="outline" onClick={fetchProducts} disabled={loading} className="text-slate-600">
                    <RefreshCw size={18} className={loading ? "animate-spin text-blue-600" : ""} />
                  </Button>
                  <Button onClick={handleSync} loading={syncing} className="bg-blue-600 hover:bg-blue-700 shadow-blue-200 shadow-lg">
                    {syncing ? 'Sincronizando...' : 'Sincronizar Catálogo'}
                  </Button>
                </div>
              </header>

              {loading && !products.length ? (
                <div className="flex flex-col items-center justify-center py-40 text-slate-400 bg-white/50 rounded-3xl border border-dashed border-slate-200">
                  <div className="p-4 bg-white rounded-full shadow-lg mb-4">
                    <RefreshCw size={32} className="animate-spin text-blue-500" />
                  </div>
                  <p className="font-medium">Buscando produtos...</p>
                </div>
              ) : products.length === 0 ? (
                <div className="text-center py-32 bg-white rounded-3xl border border-dashed border-slate-300 shadow-sm">
                  <div className="bg-slate-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Package size={40} className="text-slate-400" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">Sua loja está vazia</h3>
                  <p className="text-slate-500 mb-8 max-w-md mx-auto">Parece que ainda não sincronizamos seus produtos. Clique no botão abaixo para puxar os dados do Mercado Livre.</p>
                  <Button onClick={handleSync} className="px-8">Importar Primeira Carga</Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {products.map((product) => (
                    <div key={product._id} className="group bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-xl hover:shadow-blue-900/5 hover:-translate-y-1 transition-all duration-300 flex flex-col h-full">
                      
                      {/* Image Area */}
                      <div className="h-56 bg-white p-6 flex items-center justify-center relative border-b border-slate-100 group-hover:border-blue-50 transition-colors">
                        {product.thumbnail ? (
                          <img src={product.thumbnail} alt={product.title} className="max-h-full w-auto object-contain mix-blend-multiply group-hover:scale-105 transition-transform duration-500" />
                        ) : (
                          <Package className="text-slate-200" size={64} />
                        )}
                        
                        <div className={`absolute top-4 right-4 px-3 py-1 text-[10px] font-bold rounded-full uppercase tracking-wider shadow-sm flex items-center gap-1.5 ${
                          product.status === 'active' 
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 ring-2 ring-emerald-500/10' 
                            : 'bg-amber-50 text-amber-700 border border-amber-200 ring-2 ring-amber-500/10'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${product.status === 'active' ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
                          {product.status === 'active' ? 'Ativo' : 'Pausado'}
                        </div>
                      </div>

                      {/* Content Area */}
                      <div className="p-5 flex-1 flex flex-col">
                        <div className="mb-4">
                          <h3 className="text-sm font-semibold text-slate-800 line-clamp-2 leading-relaxed mb-2 group-hover:text-blue-600 transition-colors" title={product.title}>
                            {product.title}
                          </h3>
                          <p className="text-xs text-slate-400 font-mono inline-block bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                            {product.ml_id}
                          </p>
                        </div>
                        
                        <div className="mt-auto pt-4 border-t border-slate-50 flex items-end justify-between">
                          <div>
                            <p className="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Preço</p>
                            <p className="text-xl font-bold text-slate-900">
                              R$ {product.price.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Estoque</p>
                            <p className={`font-bold text-sm ${product.available_quantity > 0 ? 'text-slate-700' : 'text-red-500 bg-red-50 px-2 py-0.5 rounded'}`}>
                              {product.available_quantity} un
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="p-3 px-5 bg-slate-50 border-t border-slate-100 grid grid-cols-2 gap-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <button className="flex items-center justify-center gap-2 text-xs font-semibold text-slate-600 hover:text-blue-600 py-2 rounded hover:bg-white hover:shadow-sm transition-all border border-transparent hover:border-slate-200">
                          <ExternalLink size={14} /> Ver no ML
                        </button>
                        <button className="flex items-center justify-center gap-2 text-xs font-semibold text-blue-600 hover:text-blue-700 py-2 rounded hover:bg-blue-50 transition-all border border-transparent hover:border-blue-100">
                          <Edit size={14} /> Editar
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab !== 'products' && (
             <div className="flex flex-col items-center justify-center h-[70vh] text-slate-400 border-2 border-dashed border-slate-200 rounded-3xl bg-slate-50/50">
               <div className="bg-white p-6 rounded-full shadow-sm mb-6">
                 {activeTab === 'dashboard' ? <LayoutDashboard size={48} className="text-blue-500" /> : <Settings size={48} className="text-slate-500" />}
               </div>
               <h2 className="text-2xl font-bold text-slate-700 mb-2">{activeTab === 'dashboard' ? 'Dashboard' : 'Configurações'}</h2>
               <p className="text-slate-500 max-w-sm text-center">Este módulo está em desenvolvimento. Volte em breve para novidades!</p>
             </div>
          )}
        </div>
      </main>
    </div>
  );
}