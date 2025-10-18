import React from 'react';
import { cn } from '../../utils/cn';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

interface CardBodyProps {
  children: React.ReactNode;
  className?: string;
}

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ children, className }) => {
  return (
    <div className={cn('card', className)}>
      {children}
    </div>
  );
};

export const CardHeader: React.FC<CardHeaderProps> = ({ children, className }) => {
  return (
    <div className={cn('card-header', className)}>
      {children}
    </div>
  );
};

export const CardBody: React.FC<CardBodyProps> = ({ children, className }) => {
  return (
    <div className={cn('card-body', className)}>
      {children}
    </div>
  );
};

export const CardFooter: React.FC<CardFooterProps> = ({ children, className }) => {
  return (
    <div className={cn('card-footer', className)}>
      {children}
    </div>
  );
};