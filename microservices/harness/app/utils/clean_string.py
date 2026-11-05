import re

def clean_string(response: str):
    
    clean_str = re.sub(r'<think>[\s\S]*?</think>', '', response, flags=re.IGNORECASE).strip()
    if clean_str.startswith("```json"):
        clean_str = clean_str[7:]
    elif clean_str.startswith("```"):
        clean_str = clean_str[3:]
    if clean_str.endswith("```"):
        clean_str = clean_str[:-3]
    clean_str = clean_str.strip()

    return clean_str