from pathlib import Path
import sys, re
sys.path.insert(0, str(Path('tmp/pdf-tools').resolve()))
import pymupdf as fitz

base = Path('labs/Lab4/Prelab')
source = fitz.open(base / 'CEG2136_Lab4.pdf')
assets = base / 'Lab4-assets'
assets.mkdir(exist_ok=True)
fonts = sorted({(s['font'], round(s['size'], 5)) for p in source
    for b in p.get_text('dict')['blocks'] if 'lines' in b
    for line in b['lines'] for s in line['spans'] if s['text'].strip()})
fontids = {key: 'labfont' + ''.join(chr(97+int(c)) for c in str(i)) for i,key in enumerate(fonts)}
def escape(text, font):
    special = {'\\': r'\textbackslash{}', '{':r'\{', '}':r'\}',
      '%':r'\%', '&':r'\&', '#':r'\#', '_':r'\_', '$':r'\$',
      '^':r'\textasciicircum{}', '~':r'\textasciitilde{}',
      '\u2013':r'\char21{}', '\u2019':r'\char39{}',
      '\u2022':r'\textbullet{}'}
    if font.startswith('CMSY'):
        special.update({c: r'\char'+str(n)+'{}' for c,n in
          [('×',2),('←',32),('→',33),('−',0),('∧',94),('∨',95),('′',48)]})
    if font.startswith('CMMI'):
        special.update({'δ':r'\char14{}','λ':r'\char21{}', ',':r'\char59{}', '.':r'\char58{}'})
    return ''.join(special.get(c,c) for c in text)

out = [r'''% Faithful, editable fixed-layout transcription of CEG2136_Lab4.pdf.
% Compile with pdflatex from this directory.
% Each LabLine is one baseline; LabText gives x position (bp), font, and text.
% Page coordinates and fonts preserve the reference's line and page breaks.
% Text is real LaTeX; diagrams and table rules are in Lab4-assets/graphics.pdf.
% Keep that companion file with this source. Longer edits need manual reflow.
\documentclass[12pt,letterpaper]{article}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{eso-pic}
\usepackage[margin=0pt]{geometry}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\unitlength}{1bp}
\newcommand{\comment}[1]{{\color{gray}#1}}
\newcommand{\LabText}[4]{\put(#1,0){\hbox{\csname #2\endcsname\color[HTML]{#3}#4}}}
\newcommand{\LabLine}[2]{\put(0,#1){#2}}
''']
for (font,size), name in fontids.items():
    tfm = ('ec' + font[2:].lower()) if font.startswith('SF') else font.lower()
    out.append(r'\expandafter\font\csname '+name+r'\endcsname='+tfm+' at '+f'{size:.5f}bp'+'\n')
out.append('\\begin{document}\n')
for page in source:
    out.append(f'\n% ==================== PAGE {page.number+1} ====================\n')
    out.append('\\AddToShipoutPictureBG*{\\AtPageLowerLeft{\\includegraphics[page='+str(page.number+1)+',width=612bp,height=792bp]{Lab4-assets/graphics.pdf}}}\n')
    out.append('\\AddToShipoutPictureFG*{\\AtPageLowerLeft{%\n\\setlength{\\unitlength}{1bp}%\n\\begin{picture}(612,792)\n')
    for block in page.get_text('dict')['blocks']:
        if 'lines' not in block: continue
        for line in block['lines']:
            spans = [s for s in line['spans'] if s['text'].strip()]
            if not spans: continue
            # Preserve mixed-font and subscript baselines instead of flattening math.
            groups = {}
            for s in spans: groups.setdefault(round(s['origin'][1],4),[]).append(s)
            for y, group in groups.items():
                out.append('\\LabLine{'+f'{792-y:.4f}'+'}{%\n')
                for s in group:
                    font = fontids[s['font'],round(s['size'],5)]
                    out.append('\\LabText{'+f"{s['origin'][0]:.4f}"+'}{'+font+'}{'+f"{s['color']:06X}"+'}{'+escape(s['text'],s['font'])+'}%\n')
                out.append('}\n')
    out.append('\\end{picture}}}\n\\null\\newpage\n')
out.append('\\end{document}\n')
(base/'Lab4.tex').write_text(''.join(out),encoding='utf-8')
# Retain only vector rules and the original image XObjects. All document text
# is supplied by the editable LaTeX above; this is not a full-page PDF wrapper.
for page in source:
    for xref in page.get_contents():
        data = source.xref_stream(xref)
        data = re.sub(rb'\bBT\b.*?\bET\b',b'',data,flags=re.S)
        source.update_stream(xref,data)
source.save(assets/'graphics.pdf', garbage=4, deflate=True)
print(f'Restored {len(source)} pages, {len(fonts)} font variants.')
