import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../utils/cn';

const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none relative overflow-hidden',
  {
    variants: {
      variant: {
        // Primary with gradient and glow
        primary: [
          'bg-gradient-to-r from-primary-500 to-primary-600',
          'text-white',
          'hover:from-primary-600 hover:to-primary-700',
          'hover:shadow-glow-md',
          'focus:ring-primary-500',
          'active:scale-[0.98]',
        ],
        
        // Secondary with purple gradient
        secondary: [
          'bg-gradient-to-r from-secondary-500 to-secondary-600',
          'text-white',
          'hover:from-secondary-600 hover:to-secondary-700',
          'hover:shadow-glow-purple',
          'focus:ring-secondary-500',
          'active:scale-[0.98]',
        ],
        
        // Glass morphism style
        glass: [
          'bg-glass backdrop-blur-md',
          'text-white',
          'border border-glass-border',
          'hover:bg-glass-hover',
          'hover:border-glass-hover',
          'hover:shadow-glass-md',
          'focus:ring-white/20',
        ],
        
        // Ghost variant
        ghost: [
          'bg-transparent',
          'text-gray-300',
          'hover:bg-glass',
          'hover:text-white',
          'focus:ring-white/20',
        ],
        
        // Outline variant
        outline: [
          'bg-transparent',
          'text-primary-400',
          'border border-primary-400/50',
          'hover:bg-primary-500/10',
          'hover:border-primary-400',
          'hover:text-primary-300',
          'focus:ring-primary-500',
        ],
        
        // Danger variant
        danger: [
          'bg-red-500',
          'text-white',
          'hover:bg-red-600',
          'hover:shadow-glow-error',
          'focus:ring-red-500',
          'active:scale-[0.98]',
        ],
        
        // Success variant
        success: [
          'bg-emerald-500',
          'text-white',
          'hover:bg-emerald-600',
          'hover:shadow-glow-success',
          'focus:ring-emerald-500',
          'active:scale-[0.98]',
        ],
      },
      
      size: {
        xs: 'text-xs px-2.5 py-1.5 rounded-lg',
        sm: 'text-sm px-3 py-2 rounded-lg',
        md: 'text-sm px-4 py-2.5 rounded-xl',
        lg: 'text-base px-6 py-3 rounded-xl',
        xl: 'text-lg px-8 py-4 rounded-2xl',
        icon: 'h-10 w-10 rounded-xl',
        'icon-sm': 'h-8 w-8 rounded-lg',
        'icon-lg': 'h-12 w-12 rounded-xl',
      },
      
      glow: {
        true: 'shadow-glow-sm',
        false: '',
      },
      
      gradient: {
        true: 'bg-gradient-to-r',
        false: '',
      },
    },
    
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      glow: false,
      gradient: false,
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant, 
    size, 
    glow,
    gradient,
    loading = false,
    leftIcon,
    rightIcon,
    children,
    disabled,
    ...props 
  }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, glow, gradient, className }))}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {/* Loading spinner */}
        {loading && (
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        
        {/* Left icon */}
        {leftIcon && !loading && (
          <span className="mr-2 -ml-1">{leftIcon}</span>
        )}
        
        {/* Button content */}
        {children}
        
        {/* Right icon */}
        {rightIcon && (
          <span className="ml-2 -mr-1">{rightIcon}</span>
        )}
        
        {/* Hover effect overlay */}
        <span className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <span className="absolute inset-0 rounded-inherit bg-white opacity-0 hover:opacity-10 transition-opacity duration-300" />
        </span>
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button, buttonVariants };