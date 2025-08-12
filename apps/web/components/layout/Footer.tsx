import Link from 'next/link';
import { NavItem } from '@/types';

const footerNavigation = {
  main: [
    { href: '/', label: 'Home' },
    { href: '/health', label: 'Health' },
    { href: '/about', label: 'About' },
  ] as NavItem[],
  legal: [
    { href: '/privacy', label: 'Privacy Policy' },
    { href: '/terms', label: 'Terms of Service' },
  ] as NavItem[],
  social: [
    { href: 'https://github.com', label: 'GitHub', external: true },
    { href: 'https://twitter.com', label: 'Twitter', external: true },
    { href: 'https://linkedin.com', label: 'LinkedIn', external: true },
  ] as NavItem[],
};

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-border/40 bg-background">
      <div className="container mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 md:grid-cols-4">
          {/* Company Info */}
          <div className="sm:col-span-2 md:col-span-1">
            <div className="flex items-center space-x-2">
              <div className="h-6 w-6 rounded-full bg-primary"></div>
              <span className="font-bold">QuantX Platform</span>
            </div>
            <p className="mt-4 text-sm text-muted-foreground">
              A comprehensive quantitative analysis platform built with modern
              technologies for trading and financial analysis.
            </p>
          </div>

          {/* Navigation */}
          <div>
            <h3 className="text-sm font-semibold text-foreground">
              Navigation
            </h3>
            <ul className="mt-4 space-y-2">
              {footerNavigation.main.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                    target={item.external ? '_blank' : undefined}
                    rel={item.external ? 'noopener noreferrer' : undefined}
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-sm font-semibold text-foreground">Legal</h3>
            <ul className="mt-4 space-y-2">
              {footerNavigation.legal.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                    target={item.external ? '_blank' : undefined}
                    rel={item.external ? 'noopener noreferrer' : undefined}
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Social */}
          <div>
            <h3 className="text-sm font-semibold text-foreground">Follow Us</h3>
            <ul className="mt-4 space-y-2">
              {footerNavigation.social.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                    target={item.external ? '_blank' : undefined}
                    rel={item.external ? 'noopener noreferrer' : undefined}
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom section */}
        <div className="mt-8 border-t border-border/40 pt-8">
          <div className="flex flex-col items-center justify-between space-y-4 sm:flex-row sm:space-y-0">
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              <p>&copy; {currentYear} QuantX Platform. All rights reserved.</p>
            </div>
            
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              <span>Version {process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0'}</span>
              <span>•</span>
              <span>Built with Next.js</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}