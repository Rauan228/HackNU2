import React from 'react';
import { cn } from '../../utils/cn';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  help?: string;
  icon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  help,
  icon,
  className,
  id,
  ...props
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="form-label">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <div className="text-secondary-400">
              {icon}
            </div>
          </div>
        )}
        <input
          id={inputId}
          className={cn(
            'form-input',
            icon && 'pl-10',
            error && 'border-danger-300 focus:border-danger-500 focus:ring-danger-500',
            className
          )}
          {...props}
        />
      </div>
      {error && <p className="form-error">{error}</p>}
      {help && !error && <p className="form-help">{help}</p>}
    </div>
  );
};