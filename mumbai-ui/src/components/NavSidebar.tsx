import React from 'react';
import { 
  Search, 
  Bookmark, 
  History, 
  Navigation, 
  Map as MapIcon, 
  Smartphone,
  Menu
} from 'lucide-react';

const NavSidebar: React.FC = () => {
  const items = [
    { icon: <Search size={28} />, label: 'Ask Maps', active: true },
    { icon: <Bookmark size={28} />, label: 'Saved' },
    { icon: <History size={28} />, label: 'Recents' },
  ];

  const bottomItems = [
    { icon: <Smartphone size={28} />, label: 'Get app' }
  ];

  const locations = [
    { name: 'Kurla', info: '36 min', img: 'https://images.unsplash.com/photo-1596422846543-75c6fc15a3bb?auto=format&fit=crop&w=40&h=40' },
    { name: 'Mumbai & Thane', info: '', img: 'https://images.unsplash.com/photo-1529253355930-dd343d11b346?auto=format&fit=crop&w=40&h=40' },
    { name: 'Bengaluru', info: '', img: 'https://images.unsplash.com/photo-1596761276644-5399a3028bb9?auto=format&fit=crop&w=40&h=40' },
  ];

  return (
    <nav className="flex h-screen w-[72px] flex-col items-center border-r border-slate-200 bg-white py-4 shadow-sm z-50">
      <button className="mb-6 flex h-10 w-10 items-center justify-center rounded-full hover:bg-slate-100">
        <Menu size={24} className="text-slate-600" />
      </button>

      <div className="flex flex-col gap-2 w-full px-2">
        {items.map((item, i) => (
          <button
            key={i}
            className={`flex flex-col items-center gap-1 rounded-xl py-3 transition-colors ${
              item.active 
                ? 'text-blue-600' 
                : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
            }`}
          >
            <div className={`p-2 rounded-full ${item.active ? 'bg-blue-50' : ''}`}>
              {item.icon}
            </div>
            <span className="text-[10px] font-medium leading-none">{item.label}</span>
          </button>
        ))}
      </div>

      <div className="mt-4 flex flex-col gap-3 px-2">
        {locations.map((loc, i) => (
          <button key={i} className="group relative flex flex-col items-center pt-2">
            <div className="h-10 w-10 overflow-hidden rounded-lg border border-slate-200 shadow-sm transition-transform group-hover:scale-105">
              <img src={loc.img} alt={loc.name} className="h-full w-full object-cover" />
            </div>
            <span className="mt-1 text-center text-[10px] font-medium text-slate-500 line-clamp-2 max-w-[60px]">
              {loc.name} {loc.info && <span><br/>{loc.info}</span>}
            </span>
          </button>
        ))}
      </div>

      <div className="mt-auto flex flex-col gap-2 w-full px-2">
        {bottomItems.map((item, i) => (
          <button
            key={i}
            className="flex flex-col items-center gap-1 rounded-xl py-3 text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-900"
          >
            {item.icon}
            <span className="text-[10px] font-medium leading-none">{item.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
};

export default NavSidebar;
