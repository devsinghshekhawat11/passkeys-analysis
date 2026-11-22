# A10: weighted guidance consensus. Chosen weighting (authors, 22 Nov): FIDO 70%; WebAuthn, Google, Apple, Microsoft 7.5% each.
# Other variants reported as robustness checks.
import pandas as pd, numpy as np
from scipy.stats import spearmanr
R=pd.read_csv('factor_stats.csv')
v={'M':3,'S':2,'O':1,'A':0.5,'X':0,'-':0}
codes="""S - S O S|S - A - -|O O - - -|S - S - S|O A S - O|O - S S O|O O S O -|S - S - S|O O A - -|O O O - -|O - S O -|O S S A -|- - S - -|O - S - -|A - A - -|O - - - -|X - X - A|S O S O S|S S S S S|O O - - -|O O - - -|O O - M -|S O S - S|S O S - S|O O S - -|- - - - -|O - - - -|O - A - -""".split('|')
S=np.array([[v[k] for k in c.split()] for c in codes]); F,W,G,A,M=S.T
variants={
 'equal (original, sum of 5)':F+W+G+A+M,
 'FIDO 70 / G,A,MS 10 each; WebAuthn excluded':0.7*F+0.1*(G+A+M),
 'FIDO+WebAuthn 70 (35 each) / G,A,MS 10 each':0.35*(F+W)+0.1*(G+A+M),
 'FIDO 70 / WebAuthn,G,A,MS 7.5 each':0.7*F+0.075*(W+G+A+M),
 'FIDO alone (100)':F}
for k,x in variants.items():
    for lab,mask in [('all 28',np.ones(28,bool)),('drop F10,F21',~R.F.isin(['F10','F21']).values)]:
        r=spearmanr(x[mask],R.entropy.values[mask]); print(f'{k:48s} {lab:13s} rho={r.statistic:+.2f} p={r.pvalue:.3f}')
rng=np.random.default_rng(42)
for k in list(variants)[1:4]:
    x=variants[k]; bs=[]
    for _ in range(5000):
        i=rng.integers(0,28,28)
        if np.ptp(x[i])>0 and np.ptp(R.entropy.values[i])>0: bs.append(spearmanr(x[i],R.entropy.values[i]).statistic)
    perm=np.mean([abs(spearmanr(rng.permutation(x),R.entropy).statistic)>=abs(spearmanr(x,R.entropy).statistic) for _ in range(5000)])
    print(k,'bootstrap CI',np.round(np.percentile(bs,[2.5,97.5]),2),'perm p',round(perm,3))

print('== Robustness for chosen weighting: FIDO 70%, WebAuthn/Google/Apple/Microsoft 7.5% each (authors choice, 22 Nov)')
import statsmodels.api as sm
x=0.7*F+0.075*(W+G+A+M); R['wc']=x
def sp(mask,lab):
    r=spearmanr(R.wc[mask],R.entropy[mask]); print(f'{lab:45s} n={mask.sum()} rho={r.statistic:+.2f} p={r.pvalue:.3f}')
one=np.ones(28,bool); sp(one,'all')
sp(~R.F.isin(['F10','F21']).values,'drop F10,F21'); sp(~R.F.isin(['F20','F21']).values,'drop F20,F21'); sp(~R.F.isin(['F07','F11','F16']).values,'drop F07,F11,F16')
ws=np.array([.7,.075,.075,.075,.075])
for j,nm in enumerate(['FIDO','WebAuthn','Google','Apple','Microsoft']):
    w=ws.copy(); w[j]=0; w=w/w.sum(); R['loo']=S@w
    r=spearmanr(R.loo,R.entropy); print(f'leave out {nm:10s} rho={r.statistic:+.2f} p={r.pvalue:.3f}')
default={'F19':1,'F20':1,'F21':1,'F24':1,'F12':1,'F05':1}
R['default']=R.F.map(lambda f: default.get(f,0))
m=sm.OLS(R.entropy.rank(),sm.add_constant(R[['wc','default']].rank())).fit()
print('rank-OLS',dict(zip(m.params.index,np.round(m.params.values,2))),dict(zip(m.pvalues.index,np.round(m.pvalues.values,3))))
print('weighted consensus per factor:',dict(zip(R.F,np.round(x,2))))
