---
name: story-ui
description: Build UI incrementally for a user story, from raw data to polished interface
tools: [Read, Write, Edit]
---

# Story UI - Incremental UI Development

Build the UI progressively for a user story, starting with raw data display and incrementally adding functionality, styling, and polish.

## Usage

```bash
# Build UI incrementally for a story
/story-ui US-001

# Start at specific step
/story-ui US-001 --step 2

# Generate all steps at once
/story-ui US-001 --all-steps

# For specific UI component
/story-ui US-001 --component table
```

## The Incremental UI Philosophy

Instead of building a complete, polished UI from the start, we build incrementally:

1. **Step 1**: Raw data display (see it works)
2. **Step 2**: Basic interactions (make it functional)
3. **Step 3**: Structure & layout (make it organized)
4. **Step 4**: Styling & polish (make it beautiful)

This approach:
- Provides immediate visual feedback
- Validates data flow early
- Allows for quick iterations
- Reduces wasted effort on wrong implementations

## Example: Building a Product List (US-001)

### Step 1: Raw Data Display ✅
**Goal**: Verify data is flowing correctly

```tsx
// app/products/page.tsx - Step 1: Raw Data
export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  
  useEffect(() => {
    fetch('/api/v1/products')
      .then(res => res.json())
      .then(data => setProducts(data));
  }, []);
  
  return (
    <div className="p-4">
      <h1>Products (Step 1: Raw Data)</h1>
      <pre className="bg-gray-100 p-4">
        {JSON.stringify(products, null, 2)}
      </pre>
      <div>Total: {products.length} products</div>
    </div>
  );
}
```

**What to Check**:
- ✅ Data loads from API
- ✅ Correct data structure
- ✅ All fields present
- ✅ Loading states work

---

### Step 2: Basic Table/List ✅
**Goal**: Make data readable and add basic interactions

```tsx
// app/products/page.tsx - Step 2: Basic Display
export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState(null);
  
  useEffect(() => {
    setLoading(true);
    fetch('/api/v1/products')
      .then(res => res.json())
      .then(data => {
        setProducts(data);
        setLoading(false);
      });
  }, []);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="p-4">
      <h1>Products (Step 2: Basic Table)</h1>
      
      {/* Simple table */}
      <table className="w-full border">
        <thead>
          <tr className="bg-gray-200">
            <th className="border p-2">ID</th>
            <th className="border p-2">Name</th>
            <th className="border p-2">Price</th>
            <th className="border p-2">Stock</th>
            <th className="border p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {products.map(product => (
            <tr key={product.id} className="hover:bg-gray-50">
              <td className="border p-2">{product.id}</td>
              <td className="border p-2">{product.name}</td>
              <td className="border p-2">${product.price}</td>
              <td className="border p-2">{product.stock}</td>
              <td className="border p-2">
                <button 
                  onClick={() => setSelectedProduct(product)}
                  className="text-blue-500 underline"
                >
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* Selected product details */}
      {selectedProduct && (
        <div className="mt-4 p-4 border">
          <h2>Selected Product:</h2>
          <pre>{JSON.stringify(selectedProduct, null, 2)}</pre>
          <button onClick={() => setSelectedProduct(null)}>Close</button>
        </div>
      )}
    </div>
  );
}
```

**What to Check**:
- ✅ Data displays in readable format
- ✅ Basic interactions work (click, select)
- ✅ Loading/error states
- ✅ Data updates correctly

---

### Step 3: Structure & Components ✅
**Goal**: Organize with proper components and layout

```tsx
// components/ProductTable.tsx - Step 3: Structured Components
function ProductTable({ products, onSelect }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {['Product', 'Price', 'Stock', 'Status', 'Actions'].map(header => (
              <th key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {products.map(product => (
            <ProductRow key={product.id} product={product} onSelect={onSelect} />
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ProductRow({ product, onSelect }) {
  const stockStatus = product.stock > 10 ? 'In Stock' : product.stock > 0 ? 'Low Stock' : 'Out of Stock';
  const statusColor = product.stock > 10 ? 'green' : product.stock > 0 ? 'yellow' : 'red';
  
  return (
    <tr className="hover:bg-gray-50">
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center">
          <div className="flex-shrink-0 h-10 w-10 bg-gray-300 rounded"></div>
          <div className="ml-4">
            <div className="text-sm font-medium text-gray-900">{product.name}</div>
            <div className="text-sm text-gray-500">{product.category}</div>
          </div>
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="text-sm text-gray-900">${product.price}</div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="text-sm text-gray-900">{product.stock} units</div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-${statusColor}-100 text-${statusColor}-800`}>
          {stockStatus}
        </span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
        <button onClick={() => onSelect(product)} className="text-indigo-600 hover:text-indigo-900">
          View Details
        </button>
      </td>
    </tr>
  );
}

// app/products/page.tsx - Using structured components
export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [view, setView] = useState('table'); // table or grid
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold text-gray-900">Products</h1>
          <div className="flex gap-2">
            <button onClick={() => setView('table')} className={view === 'table' ? 'font-bold' : ''}>
              Table
            </button>
            <button onClick={() => setView('grid')} className={view === 'grid' ? 'font-bold' : ''}>
              Grid
            </button>
          </div>
        </div>
        
        {view === 'table' ? (
          <ProductTable products={products} onSelect={setSelectedProduct} />
        ) : (
          <ProductGrid products={products} onSelect={setSelectedProduct} />
        )}
        
        {selectedProduct && (
          <ProductModal product={selectedProduct} onClose={() => setSelectedProduct(null)} />
        )}
      </div>
    </div>
  );
}
```

**What to Check**:
- ✅ Components are reusable
- ✅ Layout is responsive
- ✅ State management works
- ✅ User can switch views

---

### Step 4: Polish & Design System ✨
**Goal**: Apply design system, animations, and final polish

```tsx
// app/products/page.tsx - Step 4: Polished with Design System
import { Card, Button, StatCard } from '@/design-system/components';
import { DataGrid } from '@/design-system/components/DataVisualization';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [view, setView] = useState<'grid' | 'table'>('grid');
  const [loading, setLoading] = useState(true);
  
  return (
    <div className="min-h-screen bg-dark-950">
      {/* Header with glass morphism */}
      <div className="glass border-b border-glass-border">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-white">Products</h1>
            <div className="flex gap-2">
              <Button 
                variant={view === 'grid' ? 'primary' : 'ghost'}
                onClick={() => setView('grid')}
                size="sm"
              >
                Grid View
              </Button>
              <Button 
                variant={view === 'table' ? 'primary' : 'ghost'}
                onClick={() => setView('table')}
                size="sm"
              >
                Table View
              </Button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Stats Row */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="Total Products"
            value={products.length}
            change={{ value: 12, trend: 'up' }}
          />
          <StatCard
            title="In Stock"
            value={products.filter(p => p.stock > 0).length}
            change={{ value: 5, trend: 'up' }}
          />
          <StatCard
            title="Low Stock"
            value={products.filter(p => p.stock < 10).length}
            change={{ value: 2, trend: 'down' }}
          />
          <StatCard
            title="Total Value"
            value={`$${products.reduce((sum, p) => sum + p.price * p.stock, 0).toLocaleString()}`}
          />
        </div>
        
        {/* Product Display */}
        {view === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {products.map(product => (
              <Card 
                key={product.id} 
                variant="glass" 
                interactive 
                className="group"
              >
                <div className="aspect-square bg-gradient-to-br from-primary-500/20 to-secondary-500/20 rounded-lg mb-4" />
                <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 transition-colors">
                  {product.name}
                </h3>
                <p className="text-gray-400 text-sm mt-1">{product.category}</p>
                <div className="flex justify-between items-center mt-4">
                  <span className="text-2xl font-bold text-white">${product.price}</span>
                  <Badge variant={product.stock > 10 ? 'success' : 'warning'}>
                    {product.stock} in stock
                  </Badge>
                </div>
                <Button variant="primary" className="w-full mt-4" glow>
                  View Details
                </Button>
              </Card>
            ))}
          </div>
        ) : (
          <Card variant="glass">
            <DataGrid
              columns={[
                { key: 'name', label: 'Product' },
                { key: 'category', label: 'Category' },
                { key: 'price', label: 'Price' },
                { key: 'stock', label: 'Stock' },
                { key: 'status', label: 'Status' }
              ]}
              data={products}
            />
          </Card>
        )}
      </div>
    </div>
  );
}
```

**What to Check**:
- ✅ Design system applied
- ✅ Smooth animations
- ✅ Responsive on all devices
- ✅ Accessibility features
- ✅ Performance optimized

---

## Generated Files Structure

When you run `/story-ui US-001`, it generates:

```
apps/web/app/
├── [feature]/
│   ├── step-1-raw.tsx       # Raw data display
│   ├── step-2-basic.tsx     # Basic table/list
│   ├── step-3-structured.tsx # Components & layout
│   ├── step-4-polished.tsx  # Final with design system
│   └── page.tsx             # Current active version
└── components/
    └── [feature]/
        ├── [Feature]Table.tsx
        ├── [Feature]Grid.tsx
        ├── [Feature]Card.tsx
        └── [Feature]Modal.tsx
```

## Incremental Development Benefits

### 1. **Fast Feedback**
- See data immediately (Step 1)
- Validate API integration early
- Catch issues before investing in UI

### 2. **Iterative Refinement**
- Test interactions before styling
- Get user feedback on functionality
- Adjust based on real data

### 3. **Reduced Waste**
- Don't build complex UI for wrong data
- Avoid polishing features that might change
- Focus effort where it matters

### 4. **Clear Progress**
- Stakeholders see constant progress
- Each step is demonstrable
- Easy to rollback if needed

## Commands for Each Step

### Step 1: Raw Data
```bash
/story-ui US-001 --step 1
# Generates: Basic data fetch and display
# Focus: API connection, data structure
```

### Step 2: Basic UI
```bash
/story-ui US-001 --step 2
# Generates: Table or list with basic interactions
# Focus: Readability, basic functionality
```

### Step 3: Structure
```bash
/story-ui US-001 --step 3
# Generates: Proper components and layout
# Focus: Reusability, organization
```

### Step 4: Polish
```bash
/story-ui US-001 --step 4
# Generates: Final UI with design system
# Focus: Beauty, animations, perfect UX
```

## Integration with Story Workflow

```bash
# Complete story implementation flow
/user-story "As a user, I want to see products"
/story-ui US-001 --step 1    # Start with raw data
/backend Create products API  # Build backend
# Test Step 1 - See data flows

/story-ui US-001 --step 2    # Add basic table
# Test interactions work

/story-ui US-001 --step 3    # Structure properly
# Test components are reusable

/story-ui US-001 --step 4    # Apply design system
# Ship polished feature
```

## Best Practices

1. **Always Start with Step 1**
   - Even if it seems trivial
   - Validates your data pipeline
   - Catches integration issues early

2. **Get Feedback at Each Step**
   - Show Step 2 to stakeholders
   - Test Step 3 with users
   - Polish Step 4 based on feedback

3. **Don't Skip Steps**
   - Each step validates different aspects
   - Skipping leads to rework
   - Building on solid foundation

4. **Keep Steps in Version Control**
   - Commit after each step
   - Tag working versions
   - Easy to rollback if needed

5. **Test at Each Step**
   ```bash
   /story-ui US-001 --step 1
   /test-ui US-001 --step 1    # Test data loading
   
   /story-ui US-001 --step 2
   /test-ui US-001 --step 2    # Test interactions
   ```

## Common UI Patterns

### Data Display Stories
```bash
/story-ui US-001 --pattern data-table
# Step 1: JSON dump
# Step 2: Basic table
# Step 3: Sortable/filterable table
# Step 4: Advanced DataGrid component
```

### Form Stories
```bash
/story-ui US-002 --pattern form
# Step 1: Basic inputs, console.log submit
# Step 2: Validation and error display
# Step 3: Proper form components
# Step 4: Beautiful form with animations
```

### Dashboard Stories
```bash
/story-ui US-003 --pattern dashboard
# Step 1: Raw metrics display
# Step 2: Basic cards with numbers
# Step 3: Organized layout with sections
# Step 4: Interactive dashboard with charts
```

## Tips for Each Step

### Step 1 Tips
- Use `<pre>` tags for JSON
- Add data counters
- Show loading states
- Log to console

### Step 2 Tips
- Use native HTML elements
- Add basic hover states
- Simple click handlers
- Basic error boundaries

### Step 3 Tips
- Extract reusable components
- Add proper TypeScript types
- Implement state management
- Add keyboard navigation

### Step 4 Tips
- Apply design tokens
- Add micro-animations
- Optimize performance
- Ensure accessibility