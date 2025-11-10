# NIGCOMSAT PMS Design System Guide
**Extracted from UI References - Space Theme Professional System**

## 🎨 Core Design Principles

### **Clean Minimalism**
- Embrace whitespace - generous padding and margins
- Subtle shadows and borders
- Remove unnecessary visual clutter
- Focus on content hierarchy

### **Professional Aerospace Feel**
- Clean, technical aesthetic
- Precise alignment and spacing
- Subtle color usage with purpose
- Professional typography

## 📐 Layout System

### **8px Grid System**
- All spacing must follow 8px increments: 8px, 16px, 24px, 32px, 40px
- Component padding: 12px (1.5 × 8px) or 16px (2 × 8px)
- Section margins: 24px (3 × 8px) or 32px (4 × 8px)

### **Card Layouts**
```css
/* Standard card from images */
.card-standard {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  padding: 16px;
}
```

### **Table Layouts** (From User Management Image)
```css
/* Professional table styling */
.table-professional {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.table-header {
  background: #f9fafb;
  padding: 12px 16px;
  font-weight: 500;
  font-size: 14px;
  color: #6b7280;
  border-bottom: 1px solid #e5e7eb;
}

.table-row {
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;
  hover: background-color: #f9fafb;
}
```

## 🎯 Color System

### **Status Colors** (Extracted from Task Management)
```css
/* High Priority / Error */
.status-high, .status-error {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

/* Medium Priority / Warning */
.status-medium, .status-warning {
  background: #fffbeb;
  color: #d97706;
  border: 1px solid #fed7aa;
}

/* Low Priority / Success */
.status-low, .status-success {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

/* Inactive / Neutral */
.status-inactive {
  background: #f9fafb;
  color: #6b7280;
  border: 1px solid #e5e7eb;
}
```

### **Progress Indicators**
```css
/* Progress bars from task management */
.progress-container {
  width: 100%;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  transition: width 0.3s ease;
}

.progress-low { background: #dc2626; }     /* 0-30% */
.progress-medium { background: #d97706; }  /* 31-70% */
.progress-high { background: #16a34a; }    /* 71-100% */
```

## 🔲 Component Specifications

### **Buttons** (From All Images)
```css
/* Primary Action Button */
.btn-primary {
  background: var(--primary);
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--primary-600);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.12);
}

/* Secondary Button */
.btn-secondary {
  background: white;
  color: #374151;
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
}

/* Small Action Button (from user management) */
.btn-small {
  padding: 4px 12px;
  font-size: 12px;
  border-radius: 4px;
}
```

### **Input Fields** (From Appointment Form)
```css
.input-field {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  transition: border-color 0.2s;
}

.input-field:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.1);
}
```

### **Status Badges** (From Task Management)
```css
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
}
```

### **Toggle Switches** (From User Management)
```css
.toggle-switch {
  position: relative;
  width: 44px;
  height: 24px;
  background: #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.toggle-switch.active {
  background: var(--primary);
}

.toggle-switch::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: transform 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.toggle-switch.active::after {
  transform: translateX(20px);
}
```

## 📱 Navigation System

### **Sidebar Navigation** (From Appointment Interface)
```css
.sidebar {
  width: 256px;
  background: white;
  border-right: 1px solid #e5e7eb;
  padding: 16px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  color: #6b7280;
  text-decoration: none;
  transition: all 0.2s;
  margin: 2px 8px;
  border-radius: 6px;
}

.nav-item:hover {
  background: #f3f4f6;
  color: #374151;
}

.nav-item.active {
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary);
  font-weight: 500;
}

.nav-icon {
  width: 20px;
  height: 20px;
  margin-right: 12px;
}
```

### **Tab Navigation** (From Task Management)
```css
.tab-navigation {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.tab-item {
  padding: 12px 0;
  margin-right: 32px;
  color: #6b7280;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-item.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}
```

## 🗂️ Data Display

### **Table Design** (From User Management)
- **Row Height**: 56px minimum
- **Cell Padding**: 16px horizontal, 12px vertical  
- **Header Background**: #f9fafb
- **Hover State**: #f9fafb
- **Border**: 1px solid #e5e7eb between rows

### **Card Lists** (From Task Management)
```css
.card-list-item {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 8px;
  transition: all 0.2s;
}

.card-list-item:hover {
  border-color: #d1d5db;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
```

## 🎭 Interactive States

### **Hover Effects**
- Subtle elevation: `transform: translateY(-1px)`
- Shadow enhancement: `box-shadow: 0 4px 8px rgba(0,0,0,0.12)`
- Color darkening: 10-15% darker
- Border color change for inputs

### **Focus States**
- Primary color border
- Subtle shadow: `0 0 0 3px rgba(primary, 0.1)`
- No outline, use box-shadow instead

### **Loading States**
```css
.loading-skeleton {
  background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

## 📝 Typography System

### **Font Weights**
- **Regular (400)**: Body text, descriptions
- **Medium (500)**: Labels, navigation items  
- **Semibold (600)**: Headings, important text

### **Font Sizes**
- **12px**: Small labels, captions, badges
- **14px**: Body text, inputs, buttons
- **16px**: Subheadings, important body text
- **18px**: Section headings  
- **20px**: Page headings
- **24px**: Main titles

### **Text Colors**
- **Primary Text**: #111827 (dark gray)
- **Secondary Text**: #6b7280 (medium gray)
- **Muted Text**: #9ca3af (light gray)
- **Link Text**: var(--primary)

## 🚀 Space Theme Elements

### **When to Use Space Icons**
- **DO**: Navigation icons, status indicators, action buttons
- **DON'T**: Decorative illustrations, large graphics
- **NEED CONSULTATION**: Complex dashboard widgets, empty states

### **Professional Patterns**
- Clean geometric shapes
- Subtle grid backgrounds for dashboards
- Minimal use of gradients (only for backgrounds)
- Focus on functionality over decoration

## ✅ Implementation Checklist

### **Every Component Must Have:**
- [ ] Consistent 8px grid spacing
- [ ] Proper hover/focus states
- [ ] Loading states where applicable
- [ ] Responsive behavior
- [ ] Accessibility attributes
- [ ] Professional color usage

### **Quality Standards:**
- [ ] No visual clutter
- [ ] Clear information hierarchy  
- [ ] Consistent interaction patterns
- [ ] Professional space aesthetic
- [ ] Clean, minimal design

---

## 🎯 Key Takeaways

1. **Embrace Minimalism**: Less is more - focus on content
2. **Consistent Spacing**: Always use 8px grid system
3. **Professional Colors**: Use color with purpose, not decoration
4. **Subtle Interactions**: Enhance UX without being flashy
5. **Space Theme**: Technical, clean, professional - no cartoon elements

*This guide ensures NIGCOMSAT PMS maintains a professional aerospace aesthetic while providing excellent user experience.*