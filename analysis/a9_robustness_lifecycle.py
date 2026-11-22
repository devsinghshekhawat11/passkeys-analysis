# Phase 2, A9: robustness of guidance-consensus result, FDR correction, lifecycle-security exposure, F28 breakdown.
# Run from phase2/analysis:  python3 a9_robustness_lifecycle.py
import pandas as pd, numpy as np
from scipy.stats import spearmanr, fisher_exact, mannwhitneyu
from statsmodels.stats.multitest import multipletests
d=pd.read_excel('../data/ramat2026-site-scores.xlsx'); d.columns=[c.strip() for c in d.columns]
F=list(d.columns[5:]); ids=[f'F{i:02d}' for i in range(1,29)]
X=d[F].copy(); X.columns=ids
R=pd.read_csv('factor_stats.csv')
v={'M':3,'S':2,'O':1,'A':0.5,'X':0,'-':0}
codes="""S - S O S|S - A - -|O O - - -|S - S - S|O A S - O|O - S S O|O O S O -|S - S - S|O O A - -|O O O - -|O - S O -|O S S A -|- - S - -|O - S - -|A - A - -|O - - - -|X - X - A|S O S O S|S S S S S|O O - - -|O O - - -|O O - M -|S O S - S|S O S - S|O O S - -|- - - - -|O - - - -|O - A - -""".split('|')
S=np.array([[v[k] for k in c.split()] for c in codes])  # 28 x 5 (FIDO, WA, Google, Apple, MS)
R['tot']=S.sum(1)
print('== 1. Consensus vs inconsistency (entropy), robustness')
def sp(mask,label,col='tot'):
    r=spearmanr(R.loc[mask,col],R.loc[mask,'entropy']); print(f'{label:55s} n={mask.sum():2d} rho={r.statistic:+.2f} p={r.pvalue:.3f}')
allm=np.ones(28,bool); sp(allm,'all 28')
sp(~R.F.isin(['F10','F21']),'drop exact duplicates F10,F21')
sp(~R.F.isin(['F20','F21']),'drop browser-default F20,F21')
sp(~R.F.isin(['F07','F11','F16']),'drop small-n factors F07,F11,F16 (n<60)')
sp(R.n>=100,'only factors applicable to >=100 sites')
names=['FIDO','WebAuthn','Google','Apple','Microsoft']
for j,nm in enumerate(names):
    R['loo']=S.sum(1)-S[:,j]; sp(allm,f'leave out {nm}','loo')
# bootstrap CI over factors
rng=np.random.default_rng(42); bs=[]
for _ in range(5000):
    i=rng.integers(0,28,28); a=R.tot.values[i]; b=R.entropy.values[i]
    if np.ptp(a)>0 and np.ptp(b)>0: bs.append(spearmanr(a,b).statistic)
print('bootstrap 95% CI rho:',np.round(np.percentile(bs,[2.5,97.5]),2))
# permutation p
perm=[spearmanr(rng.permutation(R.tot.values),R.entropy.values).statistic for _ in range(10000)]
obs=spearmanr(R.tot,R.entropy).statistic; print('permutation p (two-sided):',np.mean(np.abs(perm)>=abs(obs)))
# Control for platform-default confound: default=1 if browser/library supplies behaviour unless RP breaks it
default={'F19':1,'F20':1,'F21':1,'F24':1,'F12':1,'F05':1,'F08':0}
R['default']=R.F.map(lambda f: default.get(f,0))
import statsmodels.api as sm
Z=R[['tot','default']].rank(); y=R.entropy.rank()
m=sm.OLS(y,sm.add_constant(Z)).fit(); print('rank-OLS entropy ~ consensus + default:',dict(zip(m.params.index,np.round(m.params.values,2))),'p:',dict(zip(m.pvalues.index,np.round(m.pvalues.values,3))))
print('== 2. Benjamini-Hochberg over the site-level tests reported in phase 2')
M=X.apply(lambda c: c.map(lambda x: np.nan if x==0 else (1.0 if x>=2 else 0.0)))
tests=[]
def pair(a,b):
    s=M[[a,b]].dropna(); t=pd.crosstab(s[a],s[b]).reindex(index=[0,1],columns=[0,1],fill_value=0); return fisher_exact(t.values)[1]
for a,b in [('F09','F10'),('F20','F21'),('F13','F26'),('F14','F27'),('F14','F16'),('F16','F27'),('F17','F18'),('F04','F03'),('F03','F09')]:
    tests.append((f'{a}~{b} co-occurrence',pair(a,b)))
rk=d.Ranking
for c in ['F04','F06','F14','F18','F19','F25']:
    s=M[c].dropna(); r=rk[s.index]; tests.append((f'{c} vs popularity rank',mannwhitneyu(r[s==1],r[s==0]).pvalue))
fin=d.Category.eq('Finance'); auth=d.Category.eq('Authentication Provider')
for c in ['F03','F09','F13','F22']:
    s=M[c].dropna(); t=pd.crosstab(fin[s.index],s).reindex(index=[False,True],columns=[0,1],fill_value=0); tests.append((f'{c} finance vs rest',fisher_exact(t.values)[1]))
for c in ['F06','F14','F27']:
    s=M[c].dropna(); t=pd.crosstab(auth[s.index],s).reindex(index=[False,True],columns=[0,1],fill_value=0); tests.append((f'{c} auth-provider vs rest',fisher_exact(t.values)[1]))
ecfin=d.Category.isin(['E-Commerce','Finance']); sel=d.Cluster.eq(2)
tests.append(('Selective cluster: e-com+finance vs rest',fisher_exact(pd.crosstab(ecfin,sel).values)[1]))
p=[t[1] for t in tests]; rej,q,_,_=multipletests(p,alpha=0.05,method='fdr_bh')
for (n,pp),qq,rr in sorted(zip(tests,q,rej),key=lambda z:z[0][1]): print(f'{n:45s} p={pp:.2g} q={qq:.2g} {"SIG" if rr else "ns"}')
print('tests:',len(tests),'significant after BH:',rej.sum())
print('== 3. Lifecycle-security exposure (per site)')
reauth_none=(X.F13==1)&(X.F26.isin([1]))
notif_none=(X.F14==1)&(X.F27==1)
print('applicable for both F13,F26:',((X.F13!=0)&(X.F26!=0)).sum())
print('no re-auth for add AND delete:',reauth_none.sum())
print('no re-auth AND no add-notification:',(reauth_none&(X.F14==1)).sum())
print('no re-auth AND no notification for add or delete:',(reauth_none&notif_none).sum())
print('re-auth on add only / delete only / both:',((X.F13>=2)&(X.F26==1)).sum(),((X.F13==1)&(X.F26>=2)).sum(),((X.F13>=2)&(X.F26>=2)).sum())
print('== 4. F28 breakdown (3 full, 2 partial, 1 non, 0 NA)',X.F28.value_counts().to_dict())
print('F28 partial among sites by cluster',pd.crosstab(d.Cluster,X.F28).to_string())
print('== 5. Recovery F11 and F19 fallback', X.F11.value_counts().to_dict(), X.F19.value_counts().to_dict())
print('== 6. F22 app mismatch', X.F22.value_counts().to_dict())
print('== 7. Sites with F09 non-match by category', d[X.F09==1].Category.value_counts().to_dict())
print('category counts', d.Category.value_counts().to_dict())
