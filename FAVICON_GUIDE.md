# Favicon Guide for Quiz Master

## What is a Favicon?

A favicon is the small icon that appears in browser tabs, bookmarks, and browser history next to your website title. It helps users identify your website at a glance.

## Current Favicon Setup

Your Quiz Master website now has a custom favicon that:
- ✅ Matches your website's purple gradient branding
- ✅ Features the letter "Q" for Quiz Master
- ✅ Works across all modern browsers
- ✅ Appears in browser tabs, bookmarks, and history

## Favicon Specifications

- **Design**: Purple gradient background with white "Q" letter
- **Format**: SVG (scalable vector graphics) with PNG fallback
- **Size**: 32x32 pixels (scales automatically)
- **Colors**: Matches your website theme (#667eea to #764ba2)

## How to Replace with Your Own Favicon

### Option 1: Replace the SVG File
1. Create or design your favicon as an SVG file
2. Make sure it's 32x32 pixels or uses a square viewBox
3. Replace the file at: `static/images/favicon.svg`
4. Keep the filename as `favicon.svg`

### Option 2: Use a PNG/ICO File
1. Create a 32x32 pixel PNG or ICO file
2. Save it as `static/images/favicon.png` or `favicon.ico`
3. Update the templates to use:
   ```html
   <link rel="icon" type="image/png" href="{{ url_for('static', filename='images/favicon.png') }}">
   ```

### Option 3: Use Online Favicon Generators
1. Visit websites like favicon.io or realfavicongenerator.net
2. Upload your logo or text
3. Download the generated favicon files
4. Replace the current favicon.svg file

## Design Tips for Favicons

1. **Keep it simple**: Favicons are very small, so avoid complex details
2. **Use high contrast**: Make sure your icon is visible on both light and dark backgrounds
3. **Test different sizes**: Check how it looks at 16x16, 32x32, and 48x48 pixels
4. **Match your brand**: Use colors and elements that represent your website

## Browser Compatibility

The current implementation supports:
- ✅ Chrome, Firefox, Safari, Edge (all modern browsers)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)
- ✅ Progressive Web App icons
- ✅ Bookmark icons

## Files Added

- `static/images/favicon.svg` - Main favicon file
- Updated all HTML templates with favicon links
- Added proper page titles with "Quiz Master" branding

## Testing Your Favicon

1. Clear your browser cache
2. Visit your website
3. Check the browser tab for your custom icon
4. Test on different browsers and devices
5. Try bookmarking the page to see the favicon in bookmarks

Your favicon will automatically appear on your deployed Render website after the next deployment!
