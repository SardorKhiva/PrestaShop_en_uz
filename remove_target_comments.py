import re

def remove_comments_from_target_tags(file_path):
    """Remove all comment lines from inside target tags in XLIFF file, including multi-line comments."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Pattern to match target tags and their content
    target_pattern = r'(<target[^>]*>)(.*?)(</target>)'
    
    def clean_target_content(match):
        target_open = match.group(1)
        target_content = match.group(2)
        target_close = match.group(3)
        
        # Remove multi-line and single-line HTML comments from target content
        target_content = re.sub(r'<!--.*?-->', '', target_content, flags=re.DOTALL)
        
        # Clean up extra whitespace and empty lines
        lines = target_content.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip():  # Keep non-empty lines
                cleaned_lines.append(line)
            elif cleaned_lines and cleaned_lines[-1].strip():  # Keep one empty line between content
                cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        return target_open + cleaned_content + target_close
    
    # Apply the cleaning function to all target tags
    content = re.sub(target_pattern, clean_target_content, content, flags=re.DOTALL)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == "__main__":
    remove_comments_from_target_tags("AdminAdvparametersFeature.en-US.xlf")
    print("Comments removed from target tags in AdminAdvparametersFeature.en-US.xlf") 