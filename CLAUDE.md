# Claude.md - Website Development Guide

## Project Overview
Transform the Next.js 15 baseline template into a minimalist, professional website for the m4rt1n.eu domain. The site will feature a clean, modern design centered around writing themes with strategic contact points for professional networking.

## Technical Foundation
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS for utility-first design
- **Domain**: m4rt1n.eu
- **Hosting**: Static deployment optimized

## Design Philosophy
Create a sophisticated, minimalist aesthetic that conveys professionalism and literary sophistication. The design should be clean, uncluttered, and focus attention on the central writing imagery while maintaining executive-level polish.

## Core Requirements

### 1. Domain Integration
- Configure Next.js for m4rt1n.eu deployment
- Update package.json with correct domain references
- Set up proper meta tags and SEO optimization for the domain
- Ensure all internal links reference the correct domain structure

### 2. Visual Design System

#### Color Palette
- Primary: Deep charcoal (#2D3436) or rich navy (#1E3A8A)
- Secondary: Warm cream (#FEF7E0) or soft white (#FAFAFA)
- Accent: Subtle gold (#D4AF37) or deep burgundy (#7C2D12)
- Text: High contrast dark gray (#1F2937) on light backgrounds

#### Typography
- Primary font: Inter or Crimson Pro for professional readability
- Headings: Clean, modern sans-serif
- Body text: Readable serif or sans-serif depending on primary choice
- Font weights: 300 (light), 400 (regular), 600 (semibold)

#### Layout Structure
- Full viewport height design
- Centered content with generous white space
- Responsive grid system using Tailwind's flex utilities
- Mobile-first approach with elegant desktop scaling

### 3. Content Architecture

#### Central Image Design
Create or source a sophisticated illustration featuring:
- **Primary Elements**: Fountain pen, quality paper, leather-bound books
- **Style**: Minimalist line art or elegant photography
- **Positioning**: Center of viewport, properly scaled
- **Aesthetic**: Professional, timeless, literary sophistication
- **Format**: SVG preferred for scalability, high-quality PNG alternative
- **Color treatment**: Monochrome or subtle color that complements the palette

#### Navigation Elements
- **LinkedIn Link**: 
  - URL: https://www.linkedin.com/in/francoisxaviermartin/
  - Visual: Professional LinkedIn icon or text link
  - Behavior: Opens in new tab
  - Styling: Consistent with overall design aesthetic

- **Email Contact**:
  - Email: contact@m4rt1n.eu
  - Visual: Email icon or text link
  - Behavior: Opens default email client
  - Styling: Matches LinkedIn link treatment

### 4. Component Implementation

#### Main Layout Structure
```typescript
// app/layout.tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <title>m4rt1n.eu</title>
        <meta name="description" content="Professional writing and communication" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="min-h-screen bg-gray-50">
        {children}
      </body>
    </html>
  )
}
```

#### Homepage Component
```typescript
// app/page.tsx
export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="max-w-4xl mx-auto text-center">
        {/* Central Image */}
        <div className="mb-8">
          <Image
            src="/images/writing-illustration.svg"
            alt="Writing and literature"
            width={400}
            height={300}
            className="mx-auto"
          />
        </div>
        
        {/* Contact Links */}
        <div className="flex justify-center space-x-8">
          <ContactLinks />
        </div>
      </div>
    </main>
  )
}
```

#### Contact Links Component
```typescript
// components/ContactLinks.tsx
export function ContactLinks() {
  return (
    <div className="flex items-center space-x-6">
      <a
        href="https://www.linkedin.com/in/francoisxaviermartin/"
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors"
      >
        <LinkedInIcon className="w-5 h-5" />
        <span>LinkedIn</span>
      </a>
      
      <a
        href="mailto:contact@m4rt1n.eu"
        className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors"
      >
        <EmailIcon className="w-5 h-5" />
        <span>Contact</span>
      </a>
    </div>
  )
}
```

### 5. Technical Implementation

#### File Structure
```
src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── ContactLinks.tsx
│   └── Icons.tsx
├── public/
│   └── images/
│       └── writing-illustration.svg
└── tailwind.config.js
```

#### Tailwind Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Crimson Pro', 'serif'],
      },
      colors: {
        primary: '#2D3436',
        secondary: '#FEF7E0',
        accent: '#D4AF37',
      },
    },
  },
  plugins: [],
}
```

#### Global Styles
```css
/* app/globals.css */
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Crimson+Pro:wght@300;400;600&display=swap');

html {
  scroll-behavior: smooth;
}

body {
  font-family: 'Inter', sans-serif;
  line-height: 1.6;
}
```

### 6. Performance Optimization

#### Image Optimization
- Use Next.js Image component for automatic optimization
- Implement proper alt text for accessibility
- Consider lazy loading for improved performance
- Optimize image formats (WebP, AVIF support)

#### SEO Configuration
```typescript
// app/layout.tsx metadata
export const metadata = {
  title: 'm4rt1n.eu',
  description: 'Professional writing and communication',
  keywords: 'writing, communication, professional',
  openGraph: {
    title: 'm4rt1n.eu',
    description: 'Professional writing and communication',
    url: 'https://m4rt1n.eu',
    siteName: 'm4rt1n.eu',
    type: 'website',
  },
}
```

### 7. Responsive Design

#### Mobile Optimization
- Ensure central image scales appropriately on mobile devices
- Stack contact links vertically on smaller screens
- Maintain readability and touch targets
- Test across iOS and Android devices

#### Breakpoint Strategy
- Mobile: 320px - 768px
- Tablet: 768px - 1024px
- Desktop: 1024px+

### 8. Deployment Configuration

#### Next.js Configuration
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig
```

#### Build Process
```bash
# Build commands
npm run build
npm run export

# Deployment verification
npm run start
```

### 9. Quality Assurance

#### Testing Checklist
- [ ] All links function correctly
- [ ] Images load and display properly
- [ ] Responsive design works across devices
- [ ] Email links open default client
- [ ] LinkedIn links open in new tab
- [ ] Performance metrics meet standards
- [ ] SEO metadata is complete
- [ ] Accessibility standards are met

#### Browser Compatibility
- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile Safari: Latest 2 versions

### 10. Maintenance and Updates

#### Content Updates
- Central image can be updated by replacing the file in /public/images/
- Contact information updates require component modification
- Style updates through Tailwind configuration

#### Technical Maintenance
- Regular Next.js updates
- Dependency security updates
- Performance monitoring
- Analytics integration (if required)

## Implementation Timeline

1. **Setup Phase** (Day 1): Configure Next.js project with TypeScript and Tailwind
2. **Design Phase** (Day 2): Implement layout, typography, and color system
3. **Content Phase** (Day 3): Add central image and contact links
4. **Optimization Phase** (Day 4): Performance tuning and SEO
5. **Testing Phase** (Day 5): Cross-browser and device testing
6. **Deployment Phase** (Day 6): Final deployment and verification

## Success Metrics

- Page load time under 2 seconds
- Mobile-friendly design score 100/100
- Accessibility compliance (WCAG 2.1 AA)
- Professional aesthetic that reflects writing expertise
- Clear, functional contact pathways

This comprehensive guide provides the foundation for creating a sophisticated, minimalist website that effectively represents professional writing services while maintaining the technical excellence expected in modern web development.