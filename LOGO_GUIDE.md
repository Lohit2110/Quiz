# Logo Customization Guide

## Current Logo Setup

Your quiz application now includes a beautiful animated logo that appears on all pages. The logo consists of:

1. **Animated Logo Icon**: A floating purple gradient circle with the letter "Q"
2. **Brand Text**: "Quiz Master" with a subtitle
3. **Responsive Design**: Adapts to different screen sizes

## How to Replace with Your Own Logo

### Option 1: Replace with Image Logo

1. **Prepare your logo image**:
   - Recommended formats: PNG (with transparency), SVG, or JPG
   - Recommended size: 80x80 pixels or larger (square format works best)
   - Make sure the image is clear and looks good at small sizes

2. **Upload your logo**:
   - Place your logo file in the `static/images/` folder
   - Name it `logo.png`, `logo.svg`, or `logo.jpg`

3. **Update the templates** to use image instead of CSS logo:
   
   Replace the logo div in each template:
   ```html
   <!-- Current CSS logo -->
   <div class="logo">
     <span class="logo-text">Q</span>
   </div>
   
   <!-- Replace with image logo -->
   <div class="logo">
     <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Quiz Master Logo">
   </div>
   ```

### Option 2: Customize the CSS Logo

Edit `static/css/style.css` to change:

1. **Logo Colors**: Modify the `background` gradient in the `.logo` class
2. **Logo Text**: Change the "Q" to your preferred letter/symbol
3. **Logo Shape**: Adjust `border-radius` (20px = rounded, 50% = circle)
4. **Animation**: Modify or disable the `logoFloat` animation

### Option 3: Change Brand Text

Update the templates to change "Quiz Master" to your preferred brand name:

```html
<div class="logo-title">
  <h1 class="logo-main-text">Your Brand Name</h1>
  <p class="logo-sub-text">Your tagline here</p>
</div>
```

## Logo Placement

The logo appears in:
- ✅ Main dashboard (`index.html`)
- ✅ Create/Edit quiz page (`create_quiz.html`)
- ✅ Quiz taking page (`quiz.html`)
- ✅ Results page (`result.html`)

## Design Specifications

- **Main logo**: 80x80px (desktop), 60x60px (mobile)
- **Header logos**: 50x50px
- **Colors**: Purple gradient (#667eea to #764ba2)
- **Animation**: Gentle floating effect (3-second cycle)
- **Responsive**: Automatically adjusts for mobile devices

## Tips for Best Results

1. **Keep it simple**: Logos should be recognizable at small sizes
2. **Use high contrast**: Ensure your logo stands out against the background
3. **Test on mobile**: Check how your logo looks on smaller screens
4. **Consistent branding**: Use the same logo across all pages

## Need Help?

If you need assistance with logo implementation, check the CSS file at `static/css/style.css` for all logo-related styles.
