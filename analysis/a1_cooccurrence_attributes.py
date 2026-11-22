import pandas as pd, numpy as np, sys
from scipy.stats import fisher_exact, spearmanr, mannwhitneyu
d=pd.read_excel(sys.argv[1]); d.columns=[c.strip() for c in d.columns]
F=list(d.columns[5:]); names={f'F{i:02d}':c for i,c in enumerate(F,1)}
X=d[F].copy(); X.columns=list(names)
def m(c): # 1 match/partial, 0 non, nan NA
    v=X[c].astype(float); return v.map(lambda x: np.nan if x==0 else (1.0 if x>=2 else 0.0))
M=pd.DataFrame({c:m(c) for c in X})
def pair(a,b):
    s=M[[a,b]].dropna(); t=pd.crosstab(s[a],s[b]).reindex(index=[0,1],columns=[0,1],fill_value=0)
    o,p=fisher_exact(t.values); n=len(s); agree=(s[a]==s[b]).mean()
    phi=s[a].corr(s[b])
    return n,t.values.tolist(),round(agree,2),round(phi,2) if phi==phi else None,p
print("== H09a F09 vs F10, and their relation to F20/F21")
print(pair('F09','F10'))
s=X[(X.F09==1)]; print('F09 non-match sites:',len(s),'F10 non:',(s.F10==1).sum(),'F20 vals',s.F20.value_counts().to_dict(),'F21',s.F21.value_counts().to_dict(),'clusters',d.loc[s.index,'Cluster'].value_counts().to_dict())
print('F09 non sites:',sorted(d.loc[s.index,'Websites']))
print("== pairs")
for a,b in [('F13','F26'),('F14','F27'),('F14','F16'),('F16','F27'),('F17','F18'),('F02','F01'),('F25','F28'),('F15','F23'),('F03','F09'),('F06','F10'),('F13','F14'),('F26','F27'),('F04','F03')]:
    n,t,ag,phi,p=pair(a,b); print(a,b,'n',n,'tab[[a0b0,a0b1],[a1b0,a1b1]]',t,'agree',ag,'phi',phi,'p=%.2g'%p)
print("== full phi matrix top |phi|>=0.3")
cols=[c for c in M if M[c].nunique()>1]
res=[]
for i,a in enumerate(cols):
    for b in cols[i+1:]:
        n,t,ag,phi,p=pair(a,b)
        if phi is not None and abs(phi)>=0.3: res.append((round(phi,2),a,b,n,'%.1g'%p))
for r in sorted(res,reverse=True,key=lambda r:abs(r[0])): print(r)
print("== rank (Spearman of rank vs match, and Mann-Whitney)")
rk=d['Ranking']
for c in M:
    s=M[c].dropna()
    if s.nunique()<2: continue
    r=rk[s.index]; u=mannwhitneyu(r[s==1],r[s==0]); 
    print(c,names[c],'median rank match',int(r[s==1].median()),'non',int(r[s==0].median()),'p=%.2g'%u.pvalue)
print("== Authentication Provider vs others")
auth=d.Category.eq('Authentication Provider'); print(sorted(d.Websites[auth]))
for c in M:
    s=M[c].dropna(); a=s[auth[s.index]]; o=s[~auth[s.index]]
    if len(a)==0: continue
    t=[[int((a==1).sum()),int((a==0).sum())],[int((o==1).sum()),int((o==0).sum())]]
    p=fisher_exact(t)[1]
    print(c,names[c],'auth %d/%d=%.0f%%'%(t[0][0],len(a),100*a.mean()),'others %.0f%%'%(100*o.mean()),'p=%.2g'%p)
print("== Category (IT vs Finance vs E-Commerce) rates")
for cat in ['Information Technology','Finance','E-Commerce']:
    idx=d.Category.eq(cat)
    print(cat,{c:round(M.loc[idx,c].mean()*100) for c in ['F02','F03','F04','F09','F13','F18','F22','F25','F26']})
for c in ['F03','F09','F13','F18','F22','F26','F02','F04']:
    s=M[c].dropna(); fin=d.Category[s.index].eq('Finance')
    t=[[int((s[fin]==1).sum()),int((s[fin]==0).sum())],[int((s[~fin]==1).sum()),int((s[~fin]==0).sum())]]
    print('Finance vs rest',c,t,'p=%.2g'%fisher_exact(t)[1])
print("== F28 partials vs password present proxy? F28 values", X.F28.value_counts().to_dict())
print("== F17 non-match with F18", pd.crosstab(X.F17,X.F18).to_dict())
print("== F06 values", X.F06.value_counts().to_dict())
print("== F13/F26 joint (raw)", pd.crosstab(X.F13,X.F26).to_dict())
