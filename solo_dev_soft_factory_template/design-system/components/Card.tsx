import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../utils/cn';

const cardVariants = cva(
  'rounded-card overflow-hidden transition-all duration-300',
  {
    variants: {
      variant: {
        glass: [
          'bg-glass-card',
          'backdrop-blur-md',
          'border border-glass-border',
          'shadow-glass-md',
          'hover:shadow-glass-lg',
          'hover:border-glass-hover',
        ],
        solid: [
          'bg-dark-200',
          'border border-dark-300',
          'shadow-lg',
          'hover:shadow-xl',
        ],
        gradient: [
          'bg-gradient-card',
          'backdrop-blur-sm',
          'border border-glass-border',
          'shadow-glass-md',
          'hover:shadow-glow-sm',
        ],
        outline: [
          'bg-transparent',
          'border border-dark-400',
          'hover:border-primary-500/50',
          'hover:bg-glass',
        ],
      },
      padding: {
        none: 'p-0',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8',
        xl: 'p-10',
      },
      interactive: {
        true: 'cursor-pointer hover:scale-[1.02] active:scale-[0.99]',
        false: '',
      },
      glow: {
        true: 'shadow-glow-sm hover:shadow-glow-md',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'glass',
      padding: 'md',
      interactive: false,
      glow: false,
    },
  }
);

interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  children?: React.ReactNode;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, padding, interactive, glow, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(cardVariants({ variant, padding, interactive, glow }), className)}
        {...props}
      />
    );
  }
);

Card.displayName = 'Card';

// Card Header Component
const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 pb-6', className)}
    {...props}
  />
));

CardHeader.displayName = 'CardHeader';

// Card Title Component
const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, children, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      'text-2xl font-semibold leading-none tracking-tight text-white',
      className
    )}
    {...props}
  >
    {children}
  </h3>
));

CardTitle.displayName = 'CardTitle';

// Card Description Component
const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-gray-400', className)}
    {...props}
  />
));

CardDescription.displayName = 'CardDescription';

// Card Content Component
const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('', className)} {...props} />
));

CardContent.displayName = 'CardContent';

// Card Footer Component
const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center pt-6', className)}
    {...props}
  />
));

CardFooter.displayName = 'CardFooter';

// Stat Card Component (for dashboard metrics)
interface StatCardProps extends CardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    trend: 'up' | 'down';
  };
  icon?: React.ReactNode;
  chart?: React.ReactNode;
}

const StatCard = React.forwardRef<HTMLDivElement, StatCardProps>(
  ({ title, value, change, icon, chart, className, ...props }, ref) => {
    return (
      <Card ref={ref} className={cn('relative', className)} {...props}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-400">{title}</p>
            <p className="text-3xl font-bold text-white mt-2">{value}</p>
            
            {change && (
              <div className="flex items-center mt-2">
                <span
                  className={cn(
                    'text-sm font-medium',
                    change.trend === 'up' ? 'text-emerald-400' : 'text-red-400'
                  )}
                >
                  {change.trend === 'up' ? '↑' : '↓'} {Math.abs(change.value)}%
                </span>
                <span className="text-xs text-gray-500 ml-2">vs last period</span>
              </div>
            )}
          </div>
          
          {icon && (
            <div className="flex-shrink-0 p-3 bg-primary-500/10 rounded-xl">
              {icon}
            </div>
          )}
        </div>
        
        {chart && (
          <div className="mt-4 h-20">
            {chart}
          </div>
        )}
      </Card>
    );
  }
);

StatCard.displayName = 'StatCard';

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  StatCard,
  cardVariants,
};