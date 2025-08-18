import pymupdf4llm

markdown = pymupdf4llm.to_markdown(
    './2507.21046v3.pdf', 
    show_progress=False, 
    write_images=True,
    image_path='./image'
    )
md_path = './2507.21046v3.md'
        
with open(md_path, "w", encoding="utf-8") as f:
    f.write(markdown)