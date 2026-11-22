import re, subprocess, sys
md=open('source-from-doc.md').read()
md=md.replace('&#91;','[')
import re as _re
md=_re.sub(r'```latex\n(.*?)\n```', lambda m: '```{=latex}\n\\begin{equation}\n'+m.group(1)+'\n\\end{equation}\n```', md, flags=_re.S)
lines=md.split('\n')
# cut author notes
cut=next((i for i,l in enumerate(lines) if l.startswith('## Author notes')),len(lines))
lines=lines[:cut]
# drop title, byline, author line (handled in template)
i_abs=next(i for i,l in enumerate(lines) if l.startswith('## Abstract'))
body=lines[i_abs:]

def pandoc_frag(texts):
    SEP='\n\nZZCELLSEPZZ\n\n'
    texts=[('\\'+t if t.startswith('#') else t) for t in texts]
    src=SEP.join(t if t.strip() else 'ZZEMPTYZZ' for t in texts)
    out=subprocess.run(['pandoc','-f','markdown-auto_identifiers','-t','latex','--wrap=none'],input=src,capture_output=True,text=True).stdout
    parts=out.split('ZZCELLSEPZZ')
    parts=[p.strip().replace('ZZEMPTYZZ','') for p in parts]
    assert len(parts)==len(texts),(len(parts),len(texts))
    return parts

R='>{\\raggedright\\arraybackslash}'
WIDE={'2','4','5','7','8','9','10','12','13'}
# column specs (X = wrapping)
SPEC={'1':'l'+R+'X'+R+'X',
 '2':R+'Xllccccccc',
 '3':'Xccc',
 '4':R+'p{3.3cm}cc'+R+'X'+R+'p{1.1cm}ll'+R+'X',
 '5':R+'X'+R+'p{1.4cm}'+R+'p{1.6cm}'+R+'p{2cm}'+R+'X',
 '6':R+'Xccc',
 '7':R+'X'+R+'X'+R+'p{1.4cm}'+R+'p{1.8cm}',
 '8':'lc'+R+'X'+R+'p{2.0cm}'+R+'p{3.6cm}'+R+'p{1.3cm}',
 '9':'l'+R+'X'+R+'p{1.6cm}'+R+'p{4cm}'+R+'p{1.3cm}',
 '10':'l'+R+'X'+R+'p{2.2cm}'+R+'p{3.8cm}'+R+'p{1.3cm}',
 '11':R+'Xlll',
 '12':R+'X'+R+'p{1.6cm}'+R+'p{2.8cm}'+R+'p{1.6cm}'+R+'p{1.8cm}'+R+'X',
 '13':R+'X'+R+'X'+R+'X'+R+'X',
 '14':R+'Xlll'}
SMALL={'2','4','5','7','8'}
FIG={'1':('fig1.pdf',True,'Methodology overview.'),
     '2':('fig2.pdf',False,'Guidance consensus and inconsistency across the 28 factors. Dashed line: least-squares trend.'),
     '3':('fig3.pdf',False,'Inconsistency and harm of the 21 non-converged factors, coloured by primary cause. Rings mark security harm.'),
     '4':('fig4.pdf',False,'Share of websites whose logged registration request sets \\texttt{authenticatorAttachment: "platform"}, by original cluster (left) and by service type (right). 89 websites with logged options.')}

out=[]; i=0
def raw(t): out.append('\n```{=latex}\n'+t+'\n```\n')
while i<len(body):
    l=body[i]
    m=re.match(r'\[embedded content: Figure (\d+):',l)
    if m:
        n=m.group(1); f,wide,cap=FIG[n]; env='figure*' if wide else 'figure'
        raw(f'\\begin{{{env}}}[t]\\centering\\includegraphics[width={"\\textwidth" if wide else "\\columnwidth"}]{{{f}}}\\caption{{{cap}}}\\label{{fig:{n}}}\\end{{{env}}}')
        i+=1; continue
    m=re.match(r'\*\*Table (\d+):\*\*\s*(.*)',l)
    if m:
        n,cap=m.group(1),m.group(2)
        j=i+1
        while not body[j].startswith('|'): j+=1
        rows=[]
        while j<len(body) and body[j].startswith('|'):
            cells=[c.strip() for c in body[j].strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?',c) for c in cells): rows.append(cells)
            j+=1
        flat=[c for r in rows for c in r]
        conv=pandoc_frag([cap]+flat); capt=conv[0]; conv=conv[1:]
        k=0; tr=[]
        for ri,r in enumerate(rows):
            cs=conv[k:k+len(r)]; k+=len(r)
            if ri==0: cs=['\\textbf{'+c+'}' for c in cs]
            tr.append(' & '.join(cs)+' \\\\'+(' \\midrule' if ri==0 else ''))
        wide=n in WIDE; env='table*' if wide else 'table'
        size='\\scriptsize' if n in SMALL else '\\footnotesize'
        width='\\textwidth' if wide else '\\columnwidth'
        raw(f'\\begin{{{env}}}[t]\\centering{size}\\setlength{{\\tabcolsep}}{{3pt}}\\caption{{{capt}}}\\label{{tab:{n}}}\n\\begin{{tabularx}}{{{width}}}{{{SPEC[n]}}}\\toprule\n'+'\n'.join(tr)+'\n\\bottomrule\\end{tabularx}\\end{'+env+'}')
        i=j; continue
    if l.startswith('## References'):
        j=i+1; refs=[]
        while j<len(body) and not body[j].startswith('## '):
            mm=re.match(r'\d+\.\s+(.*)',body[j])
            if mm: refs.append(mm.group(1))
            j+=1
        conv=pandoc_frag(refs)
        raw('\\begin{thebibliography}{99}\\small\\raggedright\n'+'\n'.join(f'\\bibitem{{r{k+1}}} '+c for k,c in enumerate(conv))+'\n\\end{thebibliography}')
        i=j; continue
    h=re.match(r'(#+)\s+(.*)',l)
    if h:
        lvl=len(h.group(1)); t=h.group(2)
        if t=='Abstract': i+=1; continue  # abstract handled below
        if t.startswith('A Guidance'): raw('\\appendix')
        t2=re.sub(r'^(\d+(\.\d+)*|[A-E])\s+','',t)
        num = t2!=t
        cmd={2:'section',3:'subsection',4:'subsubsection'}[lvl]
        out.append(f'\n```{{=latex}}\n\\{cmd}{"" if num else "*"}{{{t2}}}\n```\n'); i+=1; continue
    out.append(l); i+=1

txt='\n'.join(out)
src=txt
res=subprocess.run(['pandoc','-f','markdown-auto_identifiers+raw_attribute','-t','latex','--wrap=preserve'],input=src,capture_output=True,text=True)
if res.stderr: print(res.stderr,file=sys.stderr)
bodytex=res.stdout
# split abstract (text before first \section)
k=bodytex.index('\\section{Introduction}')
abstract=bodytex[:k].strip(); rest=bodytex[k:]
tpl=open('template.tex').read()
open('paper.tex','w').write(tpl.replace('%%ABSTRACT%%',abstract).replace('%%BODY%%',rest))
print('written')
