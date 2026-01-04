import os
import re
import urllib.parse

def generate_project_entry(name, number, prt_file, image_file, relative_path_prefix=""):
    # URL encode filename for links (spaces to %20 etc)
    # We map spaces to %20 manually if needed, or rely on quote
    # quote default safe='/' which is what we want usually, but let's be careful with spaces
    encoded_image = urllib.parse.quote(image_file)
    encoded_prt = urllib.parse.quote(prt_file)
    
    # Construct paths - ensure forward slashes for markdown links
    if relative_path_prefix:
        image_path = f"{relative_path_prefix}/images/{encoded_image}"
        prt_path = f"{relative_path_prefix}/{encoded_prt}"
    else:
        image_path = f"images/{encoded_image}"
        prt_path = encoded_prt

    return f"""### {number}. {name}
<div align="center">
  <img src="{image_path}" alt="{name}" width="800">
  <p>
    <a href="{prt_path}">
      <img src="https://img.shields.io/badge/Download-Part_File-blue?style=for-the-badge&logo=siemens" alt="Download Part File">
    </a>
  </p>
</div>"""

def update_file(file_path, marker_start, marker_end, content):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()

    # Regex to find content between markers
    pattern = re.compile(f'({re.escape(marker_start)})(.*?)({re.escape(marker_end)})', re.DOTALL)
    
    if not pattern.search(file_content):
        print(f"Markers {marker_start}...{marker_end} not found in {file_path}")
        return

    # Replace content between markers
    # We add newlines around content to ensure separation
    new_content = pattern.sub(f'\\1\n{content}\n\\3', file_content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated {file_path}")

def main():
    # Define directories
    # Assuming script is run from repo root
    nx_dir = 'Nx'
    images_dir = os.path.join(nx_dir, 'images')
    
    projects = []
    
    # Scan for .prt files in Nx directory
    if os.path.exists(nx_dir):
        files = os.listdir(nx_dir)
        for filename in files:
            if filename.lower().endswith('.prt'):
                name = os.path.splitext(filename)[0]
                # Check for corresponding image (jpg, png, etc? User said jpg)
                # Let's check jpg specifically as per user files.
                image_name = f"{name}.jpg"
                image_full_path = os.path.join(images_dir, image_name)
                
                if os.path.exists(image_full_path):
                    # Try to extract number for sorting from name like "Example 1"
                    match = re.search(r'(\d+)', name)
                    number = int(match.group(1)) if match else 0
                    
                    projects.append({
                        'name': name,
                        'number': number,
                        'prt': filename,
                        'image': image_name
                    })
    
    print(f"Found {len(projects)} projects.")

    # Sort projects by number descending (newest first)
    projects.sort(key=lambda x: x['number'], reverse=True)
    
    # Generate content for Nx/README.md
    nx_readme_blocks = []
    for proj in projects:
        nx_readme_blocks.append(generate_project_entry(proj['name'], proj['number'], proj['prt'], proj['image']))
    
    nx_content_str = "\n\n---\n\n".join(nx_readme_blocks)
    update_file(os.path.join('Nx', 'README.md'), '<!-- PROJECTS_START -->', '<!-- PROJECTS_END -->', nx_content_str)

    # Generate content for README.md (root)
    root_readme_blocks = []
    for proj in projects:
        # Pass 'Nx' as prefix
        root_readme_blocks.append(generate_project_entry(proj['name'], proj['number'], proj['prt'], proj['image'], relative_path_prefix="Nx"))

    root_content_str = "\n\n---\n\n".join(root_readme_blocks)
    update_file('README.md', '<!-- NX_PROJECTS_START -->', '<!-- NX_PROJECTS_END -->', root_content_str)

if __name__ == "__main__":
    main()
