import React from 'react';

interface BreadcrumbProps {
  items: string[];
}

export default function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav className="flex items-center gap-2 mb-6 text-sm">
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && (
            <span className="material-symbols-rounded text-gray-400 text-lg">
              arrow_forward
            </span>
          )}
          <span
            className={
              index === items.length - 1
                ? 'text-primary font-medium'
                : 'text-gray-600 hover:text-gray-900 cursor-pointer'
            }
          >
            {item}
          </span>
        </React.Fragment>
      ))}
    </nav>
  );
}