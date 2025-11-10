# Brillance Design System

## Overview

The Brillance Design System is a comprehensive design language for financial and business applications, derived from modern invoice management interfaces. It emphasizes clarity, efficiency, and professional aesthetics suitable for data-heavy applications.

### Design Philosophy
- **Clean & Minimal**: Focus on content with strategic use of whitespace
- **Data-First**: Optimized for scanning and processing financial information
- **Professional**: Trustworthy appearance appropriate for business contexts
- **Accessible**: High contrast ratios and inclusive design principles

---

## Color Palette

### Primary Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Primary Blue | `#2563eb` | Primary actions, active states, links |
| Dark Gray | `#1f2937` | Primary text, headings |
| Medium Gray | `#6b7280` | Secondary text, icons |
| Light Gray | `#f9fafb` | Background surfaces, table headers |
| White | `#ffffff` | Cards, main backgrounds |
| Border Gray | `#e5e7eb` | Dividers, borders, inactive states |

### Status Colors
| Status | Background | Text | Usage |
|--------|------------|------|-------|
| In Progress | `#dbeafe` | `#1e40af` | Active processes, pending items |
| Success/Paid | `#d1fae5` | `#065f46` | Completed actions, paid invoices |
| Warning/Overdue | `#fee2e2` | `#991b1b` | Attention required, overdue items |

### Color Usage Guidelines
- Use primary blue sparingly for key actions and active states
- Maintain 4.5:1 contrast ratio minimum for text
- Status colors should only be used in their designated contexts
- Avoid using multiple bright colors simultaneously

---

## Typography

### Font Family
**Primary**: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`

### Type Scale
| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| Page Title | 32px | 600 | 1.2 | Main page headings |
| Section Header | 24px | 600 | 1.3 | Section titles |
| Subsection | 18px | 500 | 1.4 | Component headers |
| Body Text | 16px | 400 | 1.5 | Main content |
| Small Text | 14px | 400 | 1.4 | Secondary information |
| Table Text | 14px | 400 | 1.3 | Data tables |
| Captions | 12px | 400 | 1.3 | Form labels, metadata |

### Typography Guidelines
- Use sentence case for most text elements
- Headings should use medium to semi-bold weights (500-600)
- Maintain consistent line spacing for readability
- Keep line length between 45-75 characters for optimal reading

---

## Spacing System

### Base Unit: 8px

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Fine adjustments, icon spacing |
| sm | 8px | Tight spacing, form elements |
| md | 16px | Standard spacing, component padding |
| lg | 24px | Section spacing, card padding |
| xl | 32px | Page margins, major sections |
| 2xl | 48px | Page-level spacing |

### Layout Grid
- **Container max-width**: 1200px
- **Sidebar width**: 240px
- **Content padding**: 24px
- **Card spacing**: 16px internal, 24px external

---

## Components

### Buttons

#### Primary Button
```css
background: #2563eb
color: #ffffff
padding: 8px 16px
border-radius: 6px
font-size: 14px
font-weight: 500
```
**Usage**: Main actions like "Create Invoice", "Save", "Submit"

#### Secondary Button
```css
background: #f3f4f6
color: #374151
border: 1px solid #d1d5db
padding: 8px 16px
border-radius: 6px
font-size: 14px
font-weight: 500
```
**Usage**: Secondary actions like "Cancel", "Clear all", "Import"

#### Button States
- **Hover**: Darken background by 10%
- **Active**: Darken background by 15%
- **Disabled**: 50% opacity, no pointer events

### Form Elements

#### Input Fields
```css
padding: 8px 12px
border: 1px solid #d1d5db
border-radius: 6px
font-size: 14px
background: #ffffff
```

#### Search Input
- Include search icon (magnifying glass) on left side
- Placeholder text: "Search"
- Icon spacing: 12px from left edge

#### Form States
- **Focus**: Blue border (`#2563eb`) with subtle blue shadow
- **Error**: Red border (`#dc2626`) with error message below
- **Disabled**: Gray background with reduced opacity

### Status Indicators

#### Badge Styling
```css
padding: 4px 12px
border-radius: 12px
font-size: 12px
font-weight: 500
text-transform: lowercase
```

#### Status Types
- **In Progress**: Blue background (`#dbeafe`), dark blue text (`#1e40af`)
- **Paid/Complete**: Green background (`#d1fae5`), dark green text (`#065f46`)
- **Overdue/Error**: Red background (`#fee2e2`), dark red text (`#991b1b`)

### Data Tables

#### Table Structure
```css
width: 100%
border-collapse: collapse
font-size: 14px
background: #ffffff
```

#### Header Styling
```css
background: #f9fafb
color: #6b7280
font-weight: 500
padding: 12px
border-bottom: 1px solid #e5e7eb
text-align: left
```

#### Row Styling
```css
padding: 12px
border-bottom: 1px solid #f3f4f6
hover: background #f9fafb
```

#### Table Guidelines
- Use zebra striping sparingly, prefer hover states
- Align numbers to the right
- Keep column headers concise and descriptive
- Include sorting indicators when applicable

### Navigation

#### Sidebar Navigation
- **Width**: 240px
- **Background**: `#f9fafb`
- **Border**: Right border `1px solid #e5e7eb`

#### Navigation Items
```css
padding: 8px 16px
border-radius: 6px
color: #6b7280
display: flex
align-items: center
gap: 12px
```

#### Navigation States
- **Hover**: Background `#f3f4f6`, text color `#1f2937`
- **Active**: Background `#eff6ff`, text color `#2563eb`

---

## Layout Patterns

### Main Application Layout
```
┌─────────────────────────────────────────┐
│ Header (Brand + User Menu)              │
├─────────┬───────────────────────────────┤
│ Sidebar │ Main Content Area             │
│ 240px   │                               │
│         │ ┌─────────────────────────┐   │
│         │ │ Page Header             │   │
│         │ ├─────────────────────────┤   │
│         │ │ Filters & Actions       │   │
│         │ ├─────────────────────────┤   │
│         │ │ Data Table/Content      │   │
│         │ └─────────────────────────┘   │
└─────────┴───────────────────────────────┘
```

### Page Header Pattern
- **Title**: Large heading (24px) with page name
- **Subtitle**: Descriptive text (14px, gray)
- **Actions**: Right-aligned button group
- **Spacing**: 24px bottom margin

### Filter Bar Pattern
- **Layout**: Horizontal row with left-aligned filters
- **Spacing**: 8px between filter elements
- **Clear Action**: Right-aligned "Clear all" link

---

## Iconography

### Icon Guidelines
- **Size**: 16px for inline icons, 20px for standalone
- **Style**: Outlined, consistent stroke weight
- **Color**: Match surrounding text color
- **Spacing**: 8px from adjacent text

### Common Icons
- Search: Magnifying glass
- User: Circle with person silhouette  
- Settings: Gear/cog
- Filter: Funnel
- Sort: Up/down arrows
- More actions: Three dots (horizontal)

---

## Interaction Patterns

### Hover Effects
- **Buttons**: Slight color darkening
- **Table rows**: Light gray background (`#f9fafb`)
- **Navigation items**: Background color change
- **Duration**: 0.2s ease transition

### Focus States
- **Outline**: 2px blue (`#2563eb`) with 2px offset
- **Input fields**: Blue border with subtle shadow
- **Keyboard navigation**: Clear focus indicators

### Loading States
- **Buttons**: Show spinner, disable interaction
- **Tables**: Skeleton rows or subtle loading indicator
- **Forms**: Disable inputs during submission

---

## Responsive Behavior

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px

### Mobile Adaptations
- Sidebar becomes overlay/drawer
- Tables scroll horizontally or stack
- Button text may be hidden, showing only icons
- Reduce padding and margins appropriately

---

## Accessibility

### Color Contrast
- **Normal text**: Minimum 4.5:1 ratio
- **Large text**: Minimum 3:1 ratio
- **Interactive elements**: Ensure sufficient contrast in all states

### Keyboard Navigation
- All interactive elements must be focusable
- Logical tab order throughout application
- Clear focus indicators
- Skip links for main navigation

### Screen Readers
- Proper semantic HTML structure
- ARIA labels for complex interactions
- Table headers properly associated
- Status announcements for dynamic content

---

## Implementation Guidelines

### CSS Architecture
- Use CSS custom properties for theming
- Implement design tokens for consistency
- Follow BEM or similar naming methodology
- Create reusable component classes

### Component Development
- Build components mobile-first
- Include all interactive states
- Test with keyboard navigation
- Validate color contrast ratios

### Quality Assurance
- Test across different screen sizes
- Verify accessibility compliance
- Validate with actual users
- Maintain design consistency audit

---

## Design Tokens

### CSS Custom Properties
```css
:root {
  /* Colors */
  --color-primary: #2563eb;
  --color-text-primary: #1f2937;
  --color-text-secondary: #6b7280;
  --color-background: #ffffff;
  --color-surface: #f9fafb;
  --color-border: #e5e7eb;
  
  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  
  /* Typography */
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;
  --font-size-2xl: 32px;
  
  /* Borders */
  --border-radius: 6px;
  --border-radius-lg: 8px;
  --border-radius-full: 50%;
}
```

---

This design system provides a solid foundation for building consistent, professional, and accessible business applications. Regular review and updates ensure it continues to serve user needs effectively.