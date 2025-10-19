import React from 'react';

interface LoaderProps {
  text?: string;
  className?: string;
}

export const Loader: React.FC<LoaderProps> = ({ text = 'Загрузка...', className = '' }) => {
  return (
    <div className={`flex items-center justify-center space-x-3 ${className}`}>
      <span className="inline-block w-5 h-5 border-2 border-gray-300 border-t-primary-500 rounded-full animate-spin" />
      <span className="text-sm text-gray-700">{text}</span>
    </div>
  );
};

export default Loader;