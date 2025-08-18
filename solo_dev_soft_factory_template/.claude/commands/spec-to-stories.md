---
name: spec-to-stories
description: Generate comprehensive user stories from an initial specification
tools: [Read, Write, Edit]
---

# Spec to Stories Generator

Transforms your initial specification or requirements document into a complete set of user stories, allowing you to review and refine each one individually.

## Usage

```bash
# From text specification
/spec-to-stories "I need a project management system with tasks, projects, team collaboration, and reporting"

# From detailed spec
/spec-to-stories --file requirements.md

# With priority hints
/spec-to-stories --prioritize "Your spec here"

# Group by epic
/spec-to-stories --group-by-epic "Your spec here"
```

## What It Does

### 1. **Analyzes Your Specification**

Takes your input and identifies:
- Core features and functionality
- User types/personas
- Key workflows
- Technical requirements
- Non-functional requirements

### 2. **Generates User Stories**

Creates multiple stories following the pattern:
- **Who**: User persona
- **What**: Specific capability
- **Why**: Business value

### 3. **Allows Individual Refinement**

Each story can be:
- Reviewed and edited
- Enhanced with more detail
- Prioritized
- Grouped into epics
- Linked to others

## Example Input/Output

### Input Specification:
```
"I need an e-commerce platform where customers can browse products, 
add to cart, checkout with payment, track orders. Admins should 
manage inventory, process orders, view analytics. Include search, 
filters, reviews, and recommendations."
```

### Generated Output:

```markdown
# Generated User Stories from Specification

## Analysis Summary
- Identified Personas: Customer, Admin, System
- Feature Areas: 7 main areas
- Total Stories: 18 stories
- Suggested Phases: 3 development phases

## Epic 1: Product Discovery
### US-001: Browse Products
**As a** customer  
**I want to** browse all available products  
**So that** I can discover items I want to purchase

**Acceptance Criteria:**
- [ ] Products displayed in grid/list view
- [ ] Each product shows image, name, price
- [ ] Pagination for large catalogs
- [ ] Loading states for smooth experience

**Priority:** P0 (Core)
**Estimate:** 5 points
**Dependencies:** None

---

### US-002: Search Products
**As a** customer  
**I want to** search for specific products  
**So that** I can quickly find what I'm looking for

**Acceptance Criteria:**
- [ ] Search bar prominently displayed
- [ ] Real-time search suggestions
- [ ] Search by name, description, SKU
- [ ] "No results" state handled gracefully

**Priority:** P0 (Core)
**Estimate:** 5 points
**Dependencies:** US-001

---

### US-003: Filter Products
**As a** customer  
**I want to** filter products by category, price, etc.  
**So that** I can narrow down my choices

**Acceptance Criteria:**
- [ ] Filter by category
- [ ] Filter by price range
- [ ] Filter by availability
- [ ] Multiple filters can be combined
- [ ] Clear all filters option

**Priority:** P1 (Important)
**Estimate:** 3 points
**Dependencies:** US-001

---

## Epic 2: Shopping Cart
### US-004: Add to Cart
**As a** customer  
**I want to** add products to my shopping cart  
**So that** I can purchase multiple items

**Acceptance Criteria:**
- [ ] "Add to Cart" button on each product
- [ ] Quantity selector
- [ ] Visual feedback when added
- [ ] Cart count updates immediately

**Priority:** P0 (Core)
**Estimate:** 3 points
**Dependencies:** US-001

---

### US-005: View Cart
**As a** customer  
**I want to** view my shopping cart  
**So that** I can review before checkout

**Acceptance Criteria:**
- [ ] See all items in cart
- [ ] Update quantities
- [ ] Remove items
- [ ] See total price
- [ ] Apply discount codes

**Priority:** P0 (Core)
**Estimate:** 5 points
**Dependencies:** US-004

---

## Epic 3: Checkout & Payment
### US-006: Checkout Process
**As a** customer  
**I want to** complete checkout with my cart items  
**So that** I can purchase the products

**Acceptance Criteria:**
- [ ] Enter shipping information
- [ ] Enter billing information
- [ ] Select shipping method
- [ ] Review order before payment

**Priority:** P0 (Core)
**Estimate:** 8 points
**Dependencies:** US-005

---

### US-007: Process Payment
**As a** customer  
**I want to** pay securely for my order  
**So that** I can complete my purchase

**Acceptance Criteria:**
- [ ] Multiple payment methods (card, PayPal)
- [ ] Secure payment processing
- [ ] Payment confirmation
- [ ] Error handling for failed payments

**Priority:** P0 (Core)
**Estimate:** 8 points
**Dependencies:** US-006

---

## Epic 4: Order Management
### US-008: Track Order
**As a** customer  
**I want to** track my order status  
**So that** I know when it will arrive

**Acceptance Criteria:**
- [ ] View order history
- [ ] See current order status
- [ ] Track shipping information
- [ ] Receive email updates

**Priority:** P1 (Important)
**Estimate:** 5 points
**Dependencies:** US-007

---

## Epic 5: Admin - Inventory
### US-009: Manage Products
**As an** admin  
**I want to** add, edit, and remove products  
**So that** I can maintain the catalog

**Acceptance Criteria:**
- [ ] CRUD operations for products
- [ ] Bulk upload via CSV
- [ ] Image management
- [ ] Inventory tracking

**Priority:** P0 (Core)
**Estimate:** 8 points
**Dependencies:** None

---

### US-010: Manage Inventory
**As an** admin  
**I want to** track and update inventory levels  
**So that** I can prevent overselling

**Acceptance Criteria:**
- [ ] Real-time inventory levels
- [ ] Low stock alerts
- [ ] Automatic stock updates on purchase
- [ ] Manual stock adjustments

**Priority:** P0 (Core)
**Estimate:** 5 points
**Dependencies:** US-009

---

## Epic 6: Admin - Orders
### US-011: Process Orders
**As an** admin  
**I want to** view and process customer orders  
**So that** I can fulfill purchases

**Acceptance Criteria:**
- [ ] View all orders
- [ ] Update order status
- [ ] Print shipping labels
- [ ] Mark as shipped

**Priority:** P0 (Core)
**Estimate:** 5 points
**Dependencies:** US-007

---

## Epic 7: Analytics & Reporting
### US-012: View Sales Analytics
**As an** admin  
**I want to** see sales analytics and reports  
**So that** I can make business decisions

**Acceptance Criteria:**
- [ ] Sales dashboard
- [ ] Revenue trends
- [ ] Product performance
- [ ] Customer analytics
- [ ] Export reports

**Priority:** P1 (Important)
**Estimate:** 8 points
**Dependencies:** US-011

---

## Epic 8: Reviews & Social
### US-013: Write Product Reviews
**As a** customer  
**I want to** write reviews for purchased products  
**So that** I can share my experience

**Acceptance Criteria:**
- [ ] Rate products (1-5 stars)
- [ ] Write text review
- [ ] Upload photos
- [ ] Mark as verified purchase

**Priority:** P2 (Nice to have)
**Estimate:** 5 points
**Dependencies:** US-008

---

### US-014: Read Product Reviews
**As a** customer  
**I want to** read reviews from other customers  
**So that** I can make informed decisions

**Acceptance Criteria:**
- [ ] Display average rating
- [ ] Show review list
- [ ] Filter/sort reviews
- [ ] Mark helpful reviews

**Priority:** P2 (Nice to have)
**Estimate:** 3 points
**Dependencies:** US-013

---

## Epic 9: Recommendations
### US-015: View Recommendations
**As a** customer  
**I want to** see personalized product recommendations  
**So that** I can discover relevant items

**Acceptance Criteria:**
- [ ] "You might also like" section
- [ ] Based on browsing history
- [ ] Based on purchase history
- [ ] Similar products

**Priority:** P2 (Nice to have)
**Estimate:** 8 points
**Dependencies:** US-001, US-008

---

## Refinement Options

Ready to refine individual stories? Use these commands:

1. **Review all stories:**
   ```bash
   /review-stories
   ```

2. **Enhance specific story:**
   ```bash
   /enhance-story US-001
   ```

3. **Add technical details:**
   ```bash
   /add-technical-specs US-001
   ```

4. **Generate incremental UI:**
   ```bash
   /story-ui US-001
   ```

5. **Create acceptance tests:**
   ```bash
   /acceptance-test US-001
   ```

## Suggested Implementation Phases

### Phase 1: MVP (Core Shopping)
- US-001: Browse Products
- US-004: Add to Cart
- US-005: View Cart
- US-006: Checkout Process
- US-007: Process Payment
- US-009: Manage Products (Admin)
- US-011: Process Orders (Admin)

### Phase 2: Enhanced Experience
- US-002: Search Products
- US-003: Filter Products
- US-008: Track Order
- US-010: Manage Inventory
- US-012: View Sales Analytics

### Phase 3: Growth Features
- US-013: Write Reviews
- US-014: Read Reviews
- US-015: Recommendations

## Story Metrics
- **Total Stories:** 15
- **Total Points:** 89
- **P0 (Core):** 7 stories (47%)
- **P1 (Important):** 4 stories (27%)
- **P2 (Nice to have):** 4 stories (27%)

## Next Steps
1. Review and refine each story
2. Adjust priorities based on business needs
3. Add missing stories if identified
4. Begin Phase 1 implementation
```

## How to Refine Stories

After generation, you can refine each story individually:

### 1. **Edit Story Details**
```bash
/edit-story US-001
# Opens story for editing with prompts for:
# - More detailed acceptance criteria
# - Technical requirements
# - UI/UX specifications
# - Performance requirements
```

### 2. **Add Incremental UI Steps**
```bash
/story-ui US-001
# Generates incremental UI development:
# Step 1: Display raw data in table
# Step 2: Add basic interactions
# Step 3: Apply styling
# Step 4: Add animations/polish
```

### 3. **Link Dependencies**
```bash
/link-stories US-001 US-002 US-003
# Creates dependency chain
```

### 4. **Group into Sprints**
```bash
/plan-sprint US-001 US-004 US-005
# Groups stories into executable sprint
```

## Best Practices

1. **Start Broad, Then Narrow**
   - Generate all possible stories first
   - Then prioritize and refine
   - Remove or defer less important ones

2. **Review for Completeness**
   - Check all user personas covered
   - Verify happy paths and error cases
   - Include admin/operational stories

3. **Validate Dependencies**
   - Ensure stories can be built in order
   - Identify blockers early
   - Plan parallel work opportunities

4. **Keep Stories Small**
   - If a story is > 8 points, split it
   - Each story should be 1-3 days of work
   - Clear, single responsibility

5. **Add Technical Stories**
   - Don't forget setup/infrastructure
   - Include monitoring/logging
   - Add performance optimization

## Integration with Other Commands

```bash
# Full workflow from spec to implementation
/spec-to-stories "Your specification"
/review-stories                      # Review all generated
/enhance-story US-001                # Enhance specific story
/story-ui US-001                     # Plan incremental UI
/acceptance-test US-001              # Generate tests
/implement US-001                    # Start building
```

## Output Files

```
user-stories/
├── generated/
│   ├── batch-001/
│   │   ├── summary.md
│   │   ├── US-001-browse-products.md
│   │   ├── US-002-search-products.md
│   │   └── ...
│   └── refinement-log.md
└── epics/
    ├── product-discovery.md
    ├── shopping-cart.md
    └── checkout-payment.md
```