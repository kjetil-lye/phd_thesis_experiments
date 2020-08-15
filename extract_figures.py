import json
import sys
import os
import re
import shutil
import collections
import exifread
from PIL import PngImagePlugin, Image

def get_exif_tags(source):
    if source.endswith('.jpg'):
        with open(source, 'rb') as f:


            return exifread.process_file(f)
    else:
        im = Image.open(source)
        return im.info

def display_image(source, original_source):
    
    exif_tags = get_exif_tags(source)
    
    markdown_text =f"*original path*: [{original_source}]({original_source})\n"
    try:
        markdown_text += f"*git_commit*: ```{exif_tags['git_commit']}```\n"
        markdown_text += f"*git_repo*: ```{exif_tags['git_remote_url']}```\n"
    except:
        pass
    if 'commandrun' in exif_tags:
        if not 'jupyter' in exif_tags['commandrun']:
            markdown_text += f"*command run*:\n\n```bash\n{exif_tags['commandrun']}\n```\n\n"
        else:
            markdown_text += "Run in a notebook\n"
    
    markdown_text += f"![]({source}?raw=true)\n"

    return markdown_text

    

with open(sys.argv[1]) as f:
    l = json.load(f)
original_sources = {}
images_by_chapter = collections.defaultdict(lambda: collections.defaultdict(list))

for figure_pair in l['list']:
    name = figure_pair[0]
    fname = figure_pair[1]
    if not fname.endswith('.png'):
        fname = f'{fname}.png'
    fname = fname.replace('img_downscaled', 'img')
    match = re.search(r'{([A\d])\.(\d+)}', name)
    if not match:
        print (name)
        continue
    chapter = match.group(1)
    section = match.group(2)

    chapter_folder = f'chapter_{chapter}'

    destination = os.path.join(sys.argv[2], os.path.join(chapter_folder,
                                            os.path.basename(fname)))

    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    shutil.copyfile(fname, destination)
    shutil.copyfile(fname.replace('_notitle.png', '.png'),
                    destination.replace('_notitle.png', '.png'))

    original_sources[destination.replace('_notitle.png', '.png')] = fname.replace('_notitle.png', '.png')

    images_by_chapter[chapter][section].append(destination.replace('_notitle.png',
                                                               '.png'))

markdown_text = "List of figures\n=====================\n"
for chapter in sorted(images_by_chapter.keys()):
    if chapter != "A":
        markdown_text += f"\n\n# Chapter {chapter}\n\n"
    else:
        markdown_text += f"\n\n# Appendix {chapter}\n\n"
    for figure_id in sorted(images_by_chapter[chapter].keys()):
        markdown_text += f"\n## Figure {chapter}.{figure_id}\n"
        if len(images_by_chapter[chapter][figure_id]) > 1:
            for subfigure_id in range(len(images_by_chapter[chapter][figure_id])):
                subfigure_label = chr(ord('A')+subfigure_id)
                markdown_text += f"\n### Subfigure {chapter}.{figure_id}.{subfigure_label}\n"
                markdown_text += display_image(images_by_chapter[chapter][figure_id][subfigure_id], original_sources[images_by_chapter[chapter][figure_id][subfigure_id]])

        else:
            markdown_text += display_image(images_by_chapter[chapter][figure_id][0], original_sources[images_by_chapter[chapter][figure_id][0]])

print(markdown_text)
