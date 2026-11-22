import pandas as pd, numpy as np, sys
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
d=pd.read_excel(sys.argv[1]); d.columns=[c.strip() for c in d.columns]
F=list(d.columns[5:]); X=d[F].values.astype(float); X=pd.DataFrame(X,columns=[f'F{i:02d}' for i in range(1,29)])
def dist(A):
    n=len(A); D=np.zeros((n,n))
    for i in range(n):
        for j in range(i+1,n):
            m=(A[i]>0)&(A[j]>0); k=m.sum()
            D[i,j]=D[j,i]=np.sqrt(((A[i][m]-A[j][m])**2).sum()/k) if k else 0
    return D/D.max()
def run(cols,label,k=3):
    D=dist(X[cols].values); Z=linkage(squareform(D,checks=False),'average'); lab=fcluster(Z,k,'maxclust')
    tri=D[np.triu_indices(len(D),1)]
    ct=pd.crosstab(d.Cluster,lab)
    print('==',label,'mean %.2f median %.2f'%(tri.mean(),np.median(tri))); print(ct)
    return lab
allc=list(X.columns)
run(allc,'reproduce paper (all 28)')
# collapse F10 into F09 and F21 into F20 (perfectly redundant), keep F09/F20 once
c2=[c for c in allc if c not in ('F10','F21')]
run(c2,'drop redundant F10,F21')
# additionally recode F20 partial (defined by F09) as full
X2=X.copy(); X.loc[X.F20==2,'F20']=3; X.loc[X.F21==2,'F21']=3
Xs=X; X=X2; run(c2,'drop F10,F21 + F20 partial->full'); 
# drop converged factors >=90%
conv=['F01','F05','F08','F12','F19','F23','F24','F28','F20','F21']
run([c for c in c2 if c not in conv],'also drop converged factors')
for k in (4,5): run(c2,f'drop F10,F21 + recode, k={k}',k)
X=Xs
