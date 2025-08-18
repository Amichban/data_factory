import type { Meta, StoryObj } from '@storybook/react';
import { Button } from '../components/Button';
import { 
  ChevronRightIcon, 
  DownloadIcon, 
  PlusIcon,
  TrashIcon,
  SaveIcon 
} from 'lucide-react';

const meta: Meta<typeof Button> = {
  title: 'Design System/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#09090b' },
        { name: 'darker', value: '#000000' },
      ],
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'glass', 'ghost', 'outline', 'danger', 'success'],
    },
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
    },
    glow: {
      control: 'boolean',
    },
    loading: {
      control: 'boolean',
    },
    disabled: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// Primary button with gradient
export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Get Started',
    size: 'md',
  },
};

// Glass morphism button
export const Glass: Story = {
  args: {
    variant: 'glass',
    children: 'Glass Button',
    size: 'md',
  },
};

// Button with glow effect
export const WithGlow: Story = {
  args: {
    variant: 'primary',
    children: 'Glowing Button',
    glow: true,
    size: 'lg',
  },
};

// Loading state
export const Loading: Story = {
  args: {
    variant: 'primary',
    children: 'Saving...',
    loading: true,
  },
};

// Button with icons
export const WithLeftIcon: Story = {
  args: {
    variant: 'primary',
    children: 'Download',
    leftIcon: <DownloadIcon className="w-4 h-4" />,
  },
};

export const WithRightIcon: Story = {
  args: {
    variant: 'secondary',
    children: 'Next',
    rightIcon: <ChevronRightIcon className="w-4 h-4" />,
  },
};

// All sizes
export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Button size="xs">Extra Small</Button>
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
      <Button size="xl">Extra Large</Button>
    </div>
  ),
};

// All variants
export const Variants: Story = {
  render: () => (
    <div className="space-y-4">
      <div className="flex gap-4">
        <Button variant="primary">Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="glass">Glass</Button>
      </div>
      <div className="flex gap-4">
        <Button variant="ghost">Ghost</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="danger">Danger</Button>
        <Button variant="success">Success</Button>
      </div>
    </div>
  ),
};

// Icon buttons
export const IconButtons: Story = {
  render: () => (
    <div className="flex gap-4">
      <Button size="icon" variant="primary">
        <PlusIcon className="w-4 h-4" />
      </Button>
      <Button size="icon" variant="glass">
        <SaveIcon className="w-4 h-4" />
      </Button>
      <Button size="icon" variant="danger">
        <TrashIcon className="w-4 h-4" />
      </Button>
      <Button size="icon-sm" variant="ghost">
        <ChevronRightIcon className="w-4 h-4" />
      </Button>
      <Button size="icon-lg" variant="secondary">
        <DownloadIcon className="w-5 h-5" />
      </Button>
    </div>
  ),
};

// Button group example
export const ButtonGroup: Story = {
  render: () => (
    <div className="flex">
      <Button variant="outline" className="rounded-r-none">Left</Button>
      <Button variant="outline" className="rounded-none border-x-0">Center</Button>
      <Button variant="outline" className="rounded-l-none">Right</Button>
    </div>
  ),
};

// Interactive playground
export const Playground: Story = {
  args: {
    variant: 'primary',
    children: 'Customize Me',
    size: 'md',
    glow: false,
    loading: false,
    disabled: false,
  },
};