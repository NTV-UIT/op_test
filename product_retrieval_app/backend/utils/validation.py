# Input validation utilities

def validate_product_data(data):
    """Validate product data"""
    errors = []
    
    # Required fields
    if not data.get('name', '').strip():
        errors.append('Product name is required')
    
    # Optional validations
    name = data.get('name', '')
    if len(name) > 200:
        errors.append('Product name is too long (max 200 characters)')
    
    brand = data.get('brand', '')
    if len(brand) > 100:
        errors.append('Brand name is too long (max 100 characters)')
    
    ingredients = data.get('ingredients', '')
    if len(ingredients) > 1000:
        errors.append('Ingredients text is too long (max 1000 characters)')
    
    return len(errors) == 0, errors

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return ''
    
    # Basic sanitization
    text = str(text).strip()
    
    # Remove potentially harmful characters
    harmful_chars = ['<', '>', '"', "'", '&']
    for char in harmful_chars:
        text = text.replace(char, '')
    
    return text