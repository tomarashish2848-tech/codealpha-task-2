"""
Builds data/unemployment_india_raw.csv  (Jan 2019 - Dec 2021, 28 states/UTs, monthly).

IMPORTANT: This is a SIMULATED dataset in the same schema as the Kaggle
"Unemployment in India" (CMIE) file. National monthly pattern is anchored to
approximate CMIE-reported national rates (e.g. ~23.5% Apr-2020, ~11.9% May-2021);
state values = state baseline x national shock x noise. It also contains
deliberate data-quality problems (missing values, whitespace, mixed date
formats, impossible values, duplicates) so the cleaning step is meaningful.
To use REAL data, download the Kaggle CSV and put it at data/unemployment_india_raw.csv.
"""
import numpy as np, pandas as pd
rng = np.random.default_rng(42)

# state: (zone, baseline unemployment %, labour participation %, covid sensitivity)
states = {
 "Andhra Pradesh":("South",5.5,47,0.9),"Assam":("North-East",6.0,44,0.6),"Bihar":("East",12.0,38,1.1),
 "Chhattisgarh":("Central",6.5,50,0.8),"Delhi":("North",16.0,40,1.2),"Goa":("West",9.0,42,1.1),
 "Gujarat":("West",5.0,48,1.0),"Haryana":("North",23.0,42,1.0),"Himachal Pradesh":("North",15.0,55,0.9),
 "Jammu & Kashmir":("North",17.0,43,0.7),"Jharkhand":("East",11.0,41,1.1),"Karnataka":("South",4.5,46,1.1),
 "Kerala":("South",10.0,40,1.0),"Madhya Pradesh":("Central",5.0,48,0.9),"Maharashtra":("West",5.0,43,1.2),
 "Meghalaya":("North-East",3.0,60,0.5),"Odisha":("East",4.0,46,0.9),"Puducherry":("South",2.0,38,2.0),
 "Punjab":("North",10.0,41,0.9),"Rajasthan":("North",14.0,40,1.0),"Sikkim":("North-East",5.0,56,0.8),
 "Tamil Nadu":("South",1.5,45,2.5),"Telangana":("South",5.0,50,0.9),"Tripura":("North-East",19.0,50,1.0),
 "Uttar Pradesh":("North",9.0,38,1.0),"Uttarakhand":("North",7.0,40,1.1),"West Bengal":("East",6.5,48,1.0),
 "Chandigarh":("North",8.0,42,1.2)}

dates = pd.date_range("2019-01-31","2021-12-31",freq="ME")
shock = {"2020-03":1.4,"2020-04":3.2,"2020-05":2.9,"2020-06":1.4,"2020-07":1.05,"2020-08":1.15,
         "2020-09":0.95,"2020-10":0.95,"2020-11":0.9,"2020-12":0.97,"2021-01":0.9,"2021-02":0.9,
         "2021-03":0.95,"2021-04":1.25,"2021-05":1.6,"2021-06":1.25,"2021-07":1.0,"2021-08":1.02,
         "2021-09":0.92,"2021-10":0.88,"2021-11":0.88,"2021-12":0.92}
season = {1:0.97,2:0.98,3:1.0,4:1.02,5:1.03,6:1.02,7:0.98,8:0.97,9:0.97,10:0.98,11:1.0,12:1.02}

rows=[]
for st,(zone,base,lpr,sens) in states.items():
    emp0 = rng.uniform(5e6,6e7)
    for d in dates:
        s = shock.get(d.strftime("%Y-%m"),1.0)
        mult = 1+(s-1)*sens
        ur = base*0.85*mult*season[d.month]*rng.normal(1,0.06)
        ur = float(max(0.3, 45*np.tanh(ur/45)))   # soft ceiling ~45% so extreme states stay plausible
        lp = lpr*(1-0.08*(s-1)/2)*rng.normal(1,0.02)
        emp = emp0*(1-ur/100)*(lp/lpr)*rng.normal(1,0.01)
        rows.append([st,d,"M",round(ur,2),int(emp),round(lp,2),zone])
df = pd.DataFrame(rows,columns=["Region","Date","Frequency","Estimated Unemployment Rate (%)",
                                "Estimated Employed","Estimated Labour Participation Rate (%)","Zone"])
df["Date"] = df["Date"].dt.strftime("%d-%m-%Y")

# ---- inject data-quality problems ----
idx = rng.choice(len(df),size=200,replace=False)
U,E,L="Estimated Unemployment Rate (%)","Estimated Employed","Estimated Labour Participation Rate (%)"
df.loc[idx[:30],U] = np.nan
df.loc[idx[30:55],E] = np.nan
df.loc[idx[55:70],L] = np.nan
df.loc[idx[70:80],U] = -1.0       # impossible
df.loc[idx[80:83],U] = 250.0      # impossible
df.loc[idx[83:140],"Region"] = df.loc[idx[83:140],"Region"].apply(lambda x:" "+x+"  ")
df.loc[idx[140:160],"Date"] = pd.to_datetime(df.loc[idx[140:160],"Date"],format="%d-%m-%Y").dt.strftime("%Y/%m/%d")
df.loc[idx[160:170],"Frequency"]=" Monthly"
df = pd.concat([df,df.iloc[idx[170:180]]])      # duplicate rows
df.sample(frac=1,random_state=1).to_csv("data/unemployment_india_raw.csv",index=False)
print("raw rows:",len(df))
