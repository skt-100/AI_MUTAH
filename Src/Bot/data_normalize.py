import re

def remove_prefix(name):
    if not name or not isinstance(name, str):
        return ""
        
    prefixes = r'^(أ\.د\.|أ\.د\s|د\.|د\s\.|الأستاذ الدكتور|الدكتور|الدكتورة|أ\.|م\.)'
    cleaned = re.sub(prefixes, '', name).strip()
    return cleaned

def normalize_arabic(text):

    if not text or not isinstance(text, str):
        return ""

    tashkeel_pattern = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
    text = re.sub(tashkeel_pattern, '', text)
    
    text = re.sub(r'[أإآ]', 'ا', text)
#    text = re.sub(r'[ى]', 'ي', text)
    text = re.sub(r'[ة]', 'ه', text)
    
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    return text

def clean_all(text, is_name=False):
    if is_name:
        text = remove_prefix(text)
    return normalize_arabic(text)
