import type { Meta, StoryObj } from '@storybook/react';
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription, 
  CardContent, 
  CardFooter,
  StatCard 
} from '../components/Card';
import { Button } from '../components/Button';
import { TrendingUpIcon, UsersIcon, DollarSignIcon, ActivityIcon } from 'lucide-react';

const meta: Meta<typeof Card> = {
  title: 'Design System/Card',
  component: Card,
  parameters: {
    layout: 'centered',
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#09090b' },
      ],
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['glass', 'solid', 'gradient', 'outline'],
    },
    padding: {
      control: 'select',
      options: ['none', 'sm', 'md', 'lg', 'xl'],
    },
    interactive: {
      control: 'boolean',
    },
    glow: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// Basic glass card
export const GlassCard: Story = {
  args: {
    variant: 'glass',
    padding: 'md',
    children: (
      <>
        <CardHeader>
          <CardTitle>Glass Morphism Card</CardTitle>
          <CardDescription>Beautiful translucent effect with backdrop blur</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-300">
            This is a glass morphism card with a subtle border and blur effect. 
            Perfect for modern dark theme interfaces.
          </p>
        </CardContent>
        <CardFooter>
          <Button variant="primary" size="sm">Learn More</Button>
        </CardFooter>
      </>
    ),
  },
};

// Interactive card with hover effect
export const InteractiveCard: Story = {
  args: {
    variant: 'glass',
    interactive: true,
    children: (
      <div className="p-6">
        <h3 className="text-lg font-semibold text-white mb-2">Click Me!</h3>
        <p className="text-gray-400">
          This card scales on hover and click. Perfect for clickable items.
        </p>
      </div>
    ),
  },
};

// Card with glow effect
export const GlowingCard: Story = {
  args: {
    variant: 'gradient',
    glow: true,
    children: (
      <div className="p-6">
        <h3 className="text-lg font-semibold text-white mb-2">Glowing Card</h3>
        <p className="text-gray-400">
          This card has a beautiful glow effect that draws attention.
        </p>
      </div>
    ),
  },
};

// All card variants
export const Variants: Story = {
  render: () => (
    <div className="grid grid-cols-2 gap-4 w-[600px]">
      <Card variant="glass">
        <CardHeader>
          <CardTitle>Glass</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-400">Translucent with blur</p>
        </CardContent>
      </Card>
      
      <Card variant="solid">
        <CardHeader>
          <CardTitle>Solid</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-400">Solid background</p>
        </CardContent>
      </Card>
      
      <Card variant="gradient">
        <CardHeader>
          <CardTitle>Gradient</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-400">Gradient border</p>
        </CardContent>
      </Card>
      
      <Card variant="outline">
        <CardHeader>
          <CardTitle>Outline</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-400">Simple border</p>
        </CardContent>
      </Card>
    </div>
  ),
};

// Stat cards showcase
export const StatCards: Story = {
  render: () => (
    <div className="grid grid-cols-3 gap-4 w-[800px]">
      <StatCard
        title="Total Revenue"
        value="$48,329"
        change={{ value: 12.5, trend: 'up' }}
        icon={<DollarSignIcon className="w-5 h-5 text-primary-400" />}
      />
      
      <StatCard
        title="Active Users"
        value="2,847"
        change={{ value: 8.2, trend: 'up' }}
        icon={<UsersIcon className="w-5 h-5 text-secondary-400" />}
      />
      
      <StatCard
        title="Performance"
        value="98.5%"
        change={{ value: 0.5, trend: 'down' }}
        icon={<ActivityIcon className="w-5 h-5 text-emerald-400" />}
      />
    </div>
  ),
};

// Complex card example
export const DashboardCard: Story = {
  render: () => (
    <Card variant="glass" className="w-[400px]">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>Analytics Overview</CardTitle>
            <CardDescription>Last 30 days performance</CardDescription>
          </div>
          <Button variant="ghost" size="icon-sm">
            <TrendingUpIcon className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-400">Page Views</span>
            <span className="text-lg font-semibold text-white">124,893</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-400">Unique Visitors</span>
            <span className="text-lg font-semibold text-white">48,329</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-400">Bounce Rate</span>
            <span className="text-lg font-semibold text-white">32.4%</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex gap-2">
        <Button variant="primary" size="sm" className="flex-1">
          View Details
        </Button>
        <Button variant="outline" size="sm" className="flex-1">
          Export
        </Button>
      </CardFooter>
    </Card>
  ),
};

// Card with chart mockup
export const ChartCard: Story = {
  render: () => (
    <Card variant="glass" className="w-[500px]">
      <CardHeader>
        <CardTitle>Revenue Trend</CardTitle>
        <CardDescription>Monthly revenue over time</CardDescription>
      </CardHeader>
      <CardContent>
        {/* Chart placeholder */}
        <div className="h-48 bg-gradient-to-r from-primary-500/10 to-secondary-500/10 rounded-lg flex items-center justify-center">
          <span className="text-gray-500">Chart Component Here</span>
        </div>
      </CardContent>
      <CardFooter>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
            <span className="text-gray-400">This Month</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-secondary-500 rounded-full"></div>
            <span className="text-gray-400">Last Month</span>
          </div>
        </div>
      </CardFooter>
    </Card>
  ),
};

// Nested cards
export const NestedCards: Story = {
  render: () => (
    <Card variant="solid" padding="lg" className="w-[600px]">
      <CardHeader>
        <CardTitle>Parent Card</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <Card variant="glass" padding="sm">
            <CardContent>
              <p className="text-sm text-gray-400">Nested Glass Card</p>
            </CardContent>
          </Card>
          <Card variant="outline" padding="sm">
            <CardContent>
              <p className="text-sm text-gray-400">Nested Outline Card</p>
            </CardContent>
          </Card>
        </div>
      </CardContent>
    </Card>
  ),
};