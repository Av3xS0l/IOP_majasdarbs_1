from pathlib import Path
from scipy.optimize import linprog
import pandas as pd

# datu izguve
xlsx_path = Path("./PartikasGrozsDati.xlsx")

raw_data = pd.read_excel(xlsx_path, sheet_name='produkti', header=None)
df = raw_data.iloc[5:109, :].copy()

# minimālās uzturvielu normas
normas = {
    'obv':      96.0,
    'tauki':    90.0,
    'ogh':      383.0,
    'kcal':     2400.0,
    'A':        1.5,
    'B1':       1.5,
    'B2':       2.0,
    'PP':       15.0,
    'C':        50.0,
    'Ca':       800.0,
    'P':        1000.0,
    'Fe':       15.0
}

df.columns =['produkts','obv','tauki','ogh','kJ','kcal','A','B1','B2','PP','C','Ca','P','Fe','cena_kg','cena_100g']
df['produkts'] = df['produkts'].str.strip()
minimalie_keys = ['obv','tauki','ogh','kcal','A','B1','B2','PP','C','Ca','P','Fe']
prod_count = len(df)

# minimālais modelis
C = df.iloc[:, -1]

A = [- df[key] for key in minimalie_keys]
B = [- normas[key] for key in minimalie_keys]

BOUNDS = [(0, None) for i in range(prod_count)] # daudzums >= 0

result = linprog(C, A_ub=A, b_ub=B, bounds=BOUNDS)

# funkcija strukturizētai un uzskatāmai datu izvadei
def izdevas(df, result, nosaukums):
    print('—'*35)
    print(f"{(35-len(nosaukums))//2*" "}{nosaukums}{(35-len(nosaukums))//2*" "}")
    print('—'*35)
    print("Produkti:")
    for i in range(len(result.x)):
        if result.x[i] > 0:
            print(f"{df.iloc[i, 0]}{(24-len(str(df.iloc[i, 0])))*" "}| {result.x[i] * 100 :.2f} g")
    print('—'*35)
    print(f'Minimālās izmaksas: {result.fun:.2f} eur')
    print('—'*35)
    print("Uzņemtās uzturvielas:")
    for viela in minimalie_keys:
        print(f"{viela} :\t{sum(df[viela] * result.x):.2f}\t(min {normas[viela]})")
    print('—'*35)
    print()

if result.success:
    izdevas(df, result, "Minimālais modelis")
    
else:
    print("Risinājums nav atrasts")     

# uzlabotais modelis
# izslēdzam vairākus produktus: 
udf = df.copy()
to_drop = ['Auzu putraimi', 'Šprotes', 'Kombinētie tauki', 'Cūkas tauki', 'Kausēts sviests', 'Pētersīļi', 'Zandarts']
udf = udf[~udf['produkts'].isin(to_drop)]
prod_count = len(udf)

UC = udf.iloc[:, -1]

UA = [- udf[key] for key in minimalie_keys]
UB = [- normas[key] for key in minimalie_keys]

UBOUNDS = [(0, None) for i in range(prod_count)] # daudzums >= 0

# pievienoti ierobežojumi:
#   ne vairāk kā 300 grami kviešu miltu
#   ne vairāk kā 100 grami govs piena
#   vismaz 150 grami apelsīnu
#   vismaz 200 grami makaronu
idx1 = list(udf['produkts']).index('Kviešu milti')
UBOUNDS[idx1] = (0, 3)
idx2 = list(udf['produkts']).index('Govs piens')
UBOUNDS[idx2] = (0, 1)
idx3 = list(udf['produkts']).index('Apelsīni')
UBOUNDS[idx3] = (1.5, None)
idx4 = list(udf['produkts']).index('Makaroni')
UBOUNDS[idx4] = (2, None)

Uresult = linprog(UC, A_ub=UA, b_ub=UB, bounds=UBOUNDS)

if Uresult.success:
    izdevas(udf, Uresult, "Uzlabotais modelis")
else:
    print("Risinājums nav atrasts")     



