# Project Board Setup Guide

## Manual Setup for GitHub Projects v2

Since GitHub Classic Projects are deprecated, you need to manually create a Projects v2 board. Here's how:

### Step 1: Create the Project

1. Go to your repository: https://github.com/Amichban/data_factory
2. Click on the **Projects** tab
3. Click **New project** (green button)
4. Choose **Board** view
5. Name it "Development Board"

### Step 2: Configure Columns

The board starts with default columns. Rename them to:
1. 📋 Backlog
2. 📝 Todo  
3. 🏃 In Progress
4. 👀 Review
5. 🚫 Blocked
6. ✅ Done

To rename: Click the three dots (...) on each column → Rename

### Step 3: Add Custom Fields

Click **+ Add field** and create:
- **Points** (Number field) - for story points
- **Risk** (Single select: Low, Medium, High)
- **Type** (Single select: vertical-slice, bug, feature, meta)

### Step 4: Add Issues to Board

#### Option A: Add All at Once
1. Click **+ Add items** at bottom of board
2. Search for `is:issue is:open`
3. Select all issues
4. Click **Add selected items**

#### Option B: Add Individually
1. Open each issue
2. In the right sidebar under Projects, click **+**
3. Select your Development Board

### Step 5: Configure Automation

Click ⚙️ Settings → Manage → Workflows

Enable these built-in automations:
- **Item added to project** → Set status to Backlog
- **Item closed** → Set status to Done
- **Item reopened** → Set status to Todo

### Step 6: Custom Automation Rules

Add custom rules:
1. Click **+ New workflow**
2. Choose **Auto-add to project**
3. Set filter: `is:issue label:vertical-slice`

## Using the Board with Status Labels

Our workflows automatically manage status labels. The board won't auto-sync with these labels (requires GraphQL API), but you can:

### Manual Sync Method
When you see a status label change, drag the card to the matching column:
- `status:backlog` → 📋 Backlog
- `status:todo` → 📝 Todo
- `status:in-progress` → 🏃 In Progress
- `status:review` → 👀 Review
- `status:blocked` → 🚫 Blocked
- `status:done` → ✅ Done

### Recommended Workflow

1. **Developer starts work**: 
   - Comments `/status:in-progress` on issue
   - Manually drags card to "In Progress" column

2. **Ready for review**:
   - Comments `/status:review`
   - Drags to "Review" column

3. **Completion**:
   - Close issue (auto-moves to Done)
   - Meta issue checkbox auto-updates

## Alternative: Use Labels as Primary Source

Since our automation maintains labels perfectly, you can:
1. Use the **Issues** tab with label filters
2. Filter by `status:in-progress` to see active work
3. The meta issue (#12) shows overall progress

## Quick Filters for Issues Tab

Save these URLs as bookmarks:

- [Backlog](https://github.com/Amichban/data_factory/issues?q=is%3Aissue+is%3Aopen+label%3Astatus%3Abacklog)
- [In Progress](https://github.com/Amichban/data_factory/issues?q=is%3Aissue+is%3Aopen+label%3A%22status%3Ain-progress%22)
- [Review](https://github.com/Amichban/data_factory/issues?q=is%3Aissue+is%3Aopen+label%3Astatus%3Areview)
- [Blocked](https://github.com/Amichban/data_factory/issues?q=is%3Aissue+is%3Aopen+label%3Astatus%3Ablocked)
- [Done](https://github.com/Amichban/data_factory/issues?q=is%3Aissue+label%3Astatus%3Adone)

## Future Enhancement: GraphQL Integration

To fully automate Projects v2, we'd need:
1. GitHub App or PAT with `project` scope
2. GraphQL mutations to update project items
3. Complex workflow using GitHub's GraphQL API

For now, the label-based system with manual board updates works well for solo developers.