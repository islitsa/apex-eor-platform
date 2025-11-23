import React from 'react';

export default function QuickActionsToolbar() {
  const actions = [
    { icon: 'cloud_download', label: 'Download', color: 'blue' },
    { icon: 'refresh', label: 'Refresh', color: 'green' },
    { icon: 'settings', label: 'Settings', color: 'gray' }
  ];

  return (
    <div className="fixed bottom-8 right-8 flex flex-col gap-4">
      {actions.map((action, index) => (
        <button
          key={index}
          className={`w-14 h-14 rounded-full bg-${action.color}-600 hover:bg-${action.color}-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center group relative`}
          title={action.label}
        >
          <span className="material-symbols-rounded text-2xl">
            {action.icon}
          </span>
          <span className="absolute right-16 bg-gray-900 text-white text-xs px-3 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            {action.label}
          </span>
        </button>
      ))}
    </div>
  );
}