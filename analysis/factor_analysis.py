import pandas as pd, numpy as np
from scipy.stats import spearmanr, chi2_contingency, kruskal
df=pd.read_excel('../data/ramat2026-site-scores.xlsx'); df.columns=[c.strip() for c in df.columns]
F=list(df.columns[5:]); print(len(df),len(F))
print(df.Category.value_counts().to_string())
paper={'Promotion':90,'Priority':36,'HSK-Awareness':43,'Educational-Resources':51,'Naming-Conventions':93,'Registration-Setup':25,'OTP-Setup':7,'Settings-Setup':97,'HSK-Setup':82,'Cross-Device-Setup':82,'Recovery-Setup':3,'Multicreation':95,'Setup-Authentication':30,'Setup-Notification':80,'Update-Option':47,'Update-Notification':53,'Sign-In-UI':84,'Autofill-Feature':42,'Fallback-Authentication':98,'Cross-Device-Usage':96,'HSK-Usage':96,'Mobile-App-Usage':63,'Management-UI':93,'Delete-Option':97,'Authenticator-Cleanup':23,'Deletion-Authentication':30,'Deletion-Notification':69,'Deletion-Confirmation':91}
v={'M':3,'S':2,'O':1,'A':0.5,'X':0,'-':0}
codes="""S - S O S|S - A - -|O O - - -|S - S - S|O A S - O|O - S S O|O O S O -|S - S - S|O O A - -|O O O - -|O - S O -|O S S A -|- - S - -|O - S - -|A - A - -|O - - - -|X - X - A|S O S O S|S S S S S|O O - - -|O O - - -|O O - M -|S O S - S|S O S - S|O O S - -|- - - - -|O - - - -|O - A - -""".split('|')
rows=[]
for i,f in enumerate(F):
    x=df[f]; a=x[x!=0]
    rate=round(100*(a>=2).mean()) ; full=round(100*(a==3).mean())
    p=a.value_counts(normalize=True); H=-(p*np.log2(p)).sum()/np.log2(3)
    maj=p.max()
    c=codes[i].split(); fido=v[c[0]]; tot=sum(v[k] for k in c)
    # category association (Cramer's V) on applicable sites, categories with >=5 sites
    sub=df[(df[f]!=0)]; top=sub.Category.value_counts(); sub=sub[sub.Category.isin(top[top>=5].index)]
    ct=pd.crosstab(sub.Category,sub[f]>=2)
    if ct.shape[1]>1 and ct.shape[0]>1:
        chi,pv,_,_=chi2_contingency(ct); V=np.sqrt(chi/(ct.values.sum()*(min(ct.shape)-1)))
    else: pv,V=np.nan,np.nan
    rk=spearmanr(sub.Ranking if False else df.loc[df[f]!=0,'Ranking'],df.loc[df[f]!=0,f]).statistic
    rows.append(dict(F=f'F{i+1:02d}',name=f,n=len(a),rate=rate,paper=paper[f],full=full,entropy=round(H,2),majority=round(maj,2),fido=fido,tot=tot,catV=round(V,2) if V==V else None,catp=round(pv,3) if pv==pv else None,rank_rho=round(rk,2) if rk==rk else None))
R=pd.DataFrame(rows); pd.set_option('display.width',250); print(R.to_string())
print('rate vs paper max diff',(R.rate-R.paper).abs().max())
for col in ['rate','entropy']:
  print(col,'~fido',spearmanr(R.fido,R[col]),' ~tot',spearmanr(R.tot,R[col]))
nd=R[~R.F.isin(['F20','F21'])]
print('excl defaults entropy~fido',spearmanr(nd.fido,nd.entropy))
R.to_csv('factor_stats.csv',index=False)
