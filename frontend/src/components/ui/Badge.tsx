import React from 'react';
import { cn } from '../../utils/cn';
interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  className?: string;
}
export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'primary',
  className
}) => {
  const variantClasses = {
    primary: 'badge-primary',
    secondary: 'badge-secondary',
    success: 'badge-success',
    warning: 'badge-warning',
    danger: 'badge-danger',
  };
  return (
    <span className={cn('badge', variantClasses[variant], className)}>
      {children}
    </span>
  );
};
