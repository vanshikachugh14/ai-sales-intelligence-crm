from pathlib import Path
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import joblib

rng=np.random.default_rng(42); n=1000
value=rng.lognormal(14,1,n); source=rng.choice(["Referral","Website","LinkedIn","Email","Cold Call"],n); industry=rng.choice(["Finance","Technology","Healthcare","Retail","Manufacturing"],n); engagement=rng.integers(0,11,n)
logit=-3+0.00000012*value+0.12*engagement+np.array([{"Referral":1.0,"Website":.6,"LinkedIn":.4,"Email":.1,"Cold Call":-.4}[x] for x in source])+np.array([{"Finance":.5,"Technology":.6,"Healthcare":.3,"Retail":0,"Manufacturing":.1}[x] for x in industry]); p=1/(1+np.exp(-logit)); y=rng.binomial(1,p)
X=np.column_stack([value,source,industry,engagement]);
from pandas import DataFrame
X=DataFrame(X,columns=["estimated_value","source","industry","engagement"]); X["estimated_value"]=X["estimated_value"].astype(float); X["engagement"]=X["engagement"].astype(int)
pre=ColumnTransformer([("cat",OneHotEncoder(handle_unknown="ignore"),["source","industry"])],remainder="passthrough")
model=Pipeline([("pre",pre),("clf",RandomForestClassifier(n_estimators=250,random_state=42,class_weight="balanced"))]); Xtr,Xt,ytr,yt=train_test_split(X,y,test_size=.2,random_state=42,stratify=y); model.fit(Xtr,ytr); print("ROC-AUC:",roc_auc_score(yt,model.predict_proba(Xt)[:,1])); Path(__file__).parent.mkdir(exist_ok=True); joblib.dump(model,Path(__file__).parent/"lead_conversion_model.joblib")
