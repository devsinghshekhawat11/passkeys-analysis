import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','Nimbus Roman','DejaVu Serif'],'font.size':8,'pdf.fonttype':42})
# Figure 1: methodology flow, horizontal
fig,ax=plt.subplots(figsize=(7,1.35)); ax.set_xlim(0,100); ax.set_ylim(0,20); ax.axis('off')
st=[('1 Dataset','111 sites x 28 factors\n(Ramat et al.)'),('2 Guidance coding','5 sources,\nstrength per factor'),('3 Inconsistency','Normalised entropy\nper factor'),('4 Hypothesis tests','Spearman, Fisher,\nMann-Whitney, BH'),('5 Cause and harm','6 cause codes,\n3 harm levels'),('6 Logged options','89 sites, WebAuthn\n(Jannett et al.)')]
w=14.0; g=3.2
for i,(n,b) in enumerate(st):
    x=i*(w+g)
    hi=i>=4
    ax.add_patch(FancyBboxPatch((x,2),w,16,boxstyle='round,pad=0,rounding_size=1.2',fc='#e8f0fb' if hi else 'white',ec='#2f6db5' if hi else '#555',lw=1.2 if hi else 0.8))
    ax.text(x+w/2,13.5,n,ha='center',va='center',fontweight='bold',fontsize=8)
    ax.text(x+w/2,7.5,b,ha='center',va='center',fontsize=7,color='#333')
    if i<len(st)-1: ax.annotate('',xy=(x+w+g-0.3,10),xytext=(x+w+0.3,10),arrowprops=dict(arrowstyle='->',color='#555',lw=0.8))
fig.savefig('fig1.pdf',bbox_inches='tight',pad_inches=0.02)
# Figure 2: scatter
d=[('F01',1.78,.29),('F02',1.44,.59),('F03',0.77,.62),('F04',1.7,.77),('F05',0.96,.24),('F06',1.08,.66),('F07',1.0,.24),('F08',1.7,.11),('F09',0.81,.43),('F10',0.85,.43),('F11',0.92,.14),('F12',1.04,.19),('F13',0.15,.65),('F14',0.85,.45),('F15',0.39,.63),('F16',0.7,.63),('F17',0.04,.40),('F18',1.85,.62),('F19',2.0,.08),('F20',0.77,.53),('F21',0.77,.54),('F22',1.0,.60),('F23',1.78,.24),('F24',1.78,.11),('F25',0.92,.49),('F26',0.0,.67),('F27',0.7,.57),('F28',0.74,.61)]
lab={'F04':(-6,0,'right'),'F06':(6,4,'left'),'F08':(-6,0,'right'),'F13':(6,3,'left'),'F18':(-6,0,'right'),'F19':(-6,-9,'right'),'F26':(5,6,'left')}
fig,ax=plt.subplots(figsize=(3.33,2.5))
xs=[r[1] for r in d]; ys=[r[2] for r in d]
ax.scatter(xs,ys,s=18,c='#9a9a9a',edgecolors='#555',linewidths=0.4,zorder=3)
n=len(d); mx=sum(xs)/n; my=sum(ys)/n; b=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs); a=my-b*mx
ax.plot([0,2],[a,a+2*b],'--',color='#2f6db5',lw=1)
for f,x,y in d:
    if f in lab:
        dx,dy,ha=lab[f]; ax.annotate(f,(x,y),xytext=(dx,dy),textcoords='offset points',ha=ha,fontsize=7)
ax.set_xlim(-0.1,2.1); ax.set_ylim(0,0.85)
ax.set_xlabel('Guidance consensus (weighted, FIDO 70%)'); ax.set_ylabel('Inconsistency (normalised entropy)')
ax.text(0.02,0.03,r'$\rho = -0.45$, $p = 0.016$',ha='left',fontsize=7.5)
ax.grid(alpha=0.3,lw=0.5); [s.set_linewidth(0.6) for s in ax.spines.values()]
fig.savefig('fig2.pdf',bbox_inches='tight',pad_inches=0.02)
# Figure 3: harm strip
R=[('F13',.65,3,'S','G'),('F26',.67,3,'S','G'),('F09',.43,3,'U','T'),('F10',.43,3,'U','T'),('F22',.60,3,'U','T'),('F25',.49,2,'U','G'),('F07',.24,2,'U','G'),('F28',.61,2,'U','G'),('F18',.62,2,'U','L'),('F14',.45,2,'S','L'),('F27',.57,2,'S','L'),('F04',.77,2,'U','B'),('F11',.14,2,'S','B'),('F02',.59,1,'U','G'),('F03',.62,1,'U','G'),('F17',.40,1,'U','G'),('F16',.63,1,'U','L'),('F06',.66,1,'U','B'),('F15',.63,1,'U','T'),('F20',.53,1,'U','M'),('F21',.54,1,'U','M')]
col={'G':'#2f6db5','T':'#e07b39','L':'#3a9a6b','B':'#1f3a68','M':'#a0a0a0'}
names={'G':'Guideline','T':'Technical','L':'Legacy','B':'Business','M':'Measurement'}
fig,ax=plt.subplots(figsize=(3.33,2.7))
lanes={}
for f,h,hm,k,c in sorted(R,key=lambda r:(r[2],r[1])):
    used=lanes.setdefault(hm,[]); j=next((i for i,v in enumerate(used) if h-v>=0.06),None)
    if j is None: j=len(used); used.append(h)
    else: used[j]=h
    y=hm-0.12*j+0.1
    ax.scatter([h],[y],s=30,facecolors='none' if k=='S' else col[c],edgecolors=col[c],linewidths=1.6 if k=='S' else 0.5,zorder=3)
    ax.annotate(f,(h,y),xytext=(4,-2.5),textcoords='offset points',fontsize=6.5)
ax.set_yticks([1,2,3]); ax.set_yticklabels(['Low','Medium','High']); ax.set_ylim(0.4,3.35); ax.set_xlim(0.1,0.88)
for yv in (1.5,2.5): ax.axhline(yv,color='#ccc',lw=0.6)
ax.set_xlabel('Inconsistency (normalised entropy)'); ax.set_ylabel('Harm')
from matplotlib.lines import Line2D
hs=[Line2D([],[],marker='o',ls='',color=col[c],label=names[c],markersize=4) for c in 'GTLBM']+[Line2D([],[],marker='o',ls='',mfc='none',mec='#333',mew=1.4,label='Security harm',markersize=4)]
ax.legend(handles=hs,fontsize=6,ncol=3,loc='upper center',bbox_to_anchor=(0.5,1.2),frameon=False,handletextpad=0.2,columnspacing=0.8)
[s.set_linewidth(0.6) for s in ax.spines.values()]
fig.savefig('fig3.pdf',bbox_inches='tight',pad_inches=0.02)
# Figure 4: platform-only registration by cluster and sector (counts from analysis/a13_output.txt)
panels=[('By original cluster',[('Standard',12,74),('Selective',13,14)]),
        ('By sector',[('Finance',6,11),('E-Comm.',4,11),('Other',15,67)])]
fig,axes=plt.subplots(1,2,figsize=(3.33,2.1),gridspec_kw={'width_ratios':[2,3]},sharey=True)
for ax,(title,rows) in zip(axes,panels):
    labels=[r[0] for r in rows]; vals=[100*r[1]/r[2] for r in rows]
    ax.bar(labels,vals,color='#2f6db5',width=0.6,edgecolor='white',linewidth=1)
    for i,(lbl,k,nn) in enumerate(rows):
        ax.text(i,100*k/nn+2,f'{100*k/nn:.0f}%\n{k}/{nn}',ha='center',va='bottom',fontsize=6.5)
    ax.set_title(title,fontsize=7.5); ax.set_ylim(0,118)
    ax.grid(axis='y',alpha=0.3,lw=0.5); ax.set_axisbelow(True)
    for s in ('top','right'): ax.spines[s].set_visible(False)
    [s.set_linewidth(0.6) for s in ax.spines.values()]
axes[0].set_ylabel('Platform-only registration (%)')
fig.tight_layout(w_pad=0.6)
fig.savefig('fig4.pdf',bbox_inches='tight',pad_inches=0.02)
print('ok')
