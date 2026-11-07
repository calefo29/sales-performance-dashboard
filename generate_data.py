"""Synthetic B2B SaaS sales dataset for the Sales Problem portfolio project.
All names, IDs and amounts are randomly generated. Run: python generate_data.py"""
import csv, random, math
from datetime import date, timedelta

random.seed(20261107)
OUT = "."
START, END = date(2023, 7, 1), date(2024, 12, 31)

def d(a, b):
    return a + timedelta(days=random.randint(0, (b - a).days))

# ---------- Date_Table ----------
dates = []
x = START
while x <= END:
    fy = x.year + 1 if x.month >= 7 else x.year
    fq = ((x.month - 7) % 12) // 3 + 1
    dates.append(dict(Date=x.isoformat(), Year=x.year, Quarter=(x.month - 1) // 3 + 1, Month=x.month,
                      MonthName=x.strftime("%B"), FiscalYear=fy, FiscalQuarter=fq,
                      IsCurrentQuarter=int(fy == 2025 and fq == 2), IsCurrentYear=int(fy == 2025)))
    x += timedelta(days=1)

# ---------- Sales_Reps ----------
first = ["Laura","Marcus","Priya","Diego","Hannah","Kenji","Olivia","Tomas","Nadia","Victor","Grace","Rafael",
         "Chloe","Andre","Maya","Felix","Sara","Hugo","Leah","Omar","Julia","Ivan","Nora","Caleb","Elena","Theo",
         "Alicia","Mateo","Ruby","Simon","Zoe","Bruno","Clara","Elias","Ines","Gabriel","Lena","Oscar","Vera",
         "Adrian","Paula","Noah","Lucia","Dominic","Iris","Samuel","Freya","Joel","Talia","Martin"]
last = ["Novak","Brennan","Okafor","Castillo","Lindqvist","Tanaka","Moreau","Petrov","Haddad","Sousa","Whitaker",
        "Ferreira","Kowalski","Duarte","Iyer","Larsen","Mendes","Fischer","Quinn","Rahman","Costa","Volkov",
        "Ashford","Romero","Nakamura","Becker","Delgado","Hughes","Marino","Svensson","Abbott","Reyes","Klein",
        "Osei","Vidal","Lambert","Horvat","Navarro","Cohen","Barros","Dalton","Esposito","Kaur","Morales",
        "Sinclair","Varga","Pereira","Lowe","Ortega","Holm"]
random.shuffle(last)
terr_w = {"West": 18, "East": 14, "Central": 11, "International": 7}
territories = [t for t, n in terr_w.items() for _ in range(n)]
random.shuffle(territories)
quotas = [500000]*9 + [750000]*15 + [1000000]*16 + [1250000]*5 + [1500000]*5
random.shuffle(quotas)
reps = []
for i in range(50):
    eid = f"EMP{i+1:04d}"
    reps.append(dict(EmployeeID=eid, RepName=f"{first[i]} {last[i]}", Territory=territories[i],
                     Segment=random.choice(["Commercial", "Enterprise"]),
                     HireDate=d(date(2020, 6, 1), date(2023, 6, 15)).isoformat(),
                     QuarterlyQuota=quotas[i],
                     ManagerID="" if i < 10 else f"EMP{random.randint(1,10):04d}"))
by_terr = {t: [r for r in reps if r["Territory"] == t] for t in terr_w}

# ---------- Accounts ----------
pre = ["Blue Harbor","Ironwood","Silverline","Northgate","Red Mesa","Clearwater","Brightpath","Summit Ridge",
       "Oakline","Coastal","Granite","Lumen","Vantage","Keystone","Meridian","Copperleaf","Harborview","Stonebridge",
       "Evergreen","Westfield","Falcon","Atlas","Pioneer","Riverbend","Crescent","Highland","Beacon","Sterling",
       "Cobalt","Juniper","Orion","Maple","Trident","Horizon","Redwood","Aurora","Bluepeak","Cedar","Polaris","Union"]
mid = ["Analytics","Systems","Logistics","Health","Media","Capital","Foods","Labs","Retail","Networks","Energy",
       "Partners","Software","Industries","Solutions","Ventures","Holdings","Digital","Works","Group"]
suf = ["Inc","LLC","Ltd","Co","Corp",""]
ind_w = {"Technology": 26, "Financial Services": 18, "Healthcare": 18, "Retail": 15, "Manufacturing": 13, "Media": 10}
tier_w = {"SMB": 50, "Mid-Market": 34, "Enterprise": 16}
reg_w = {"East": 32, "West": 31, "Central": 22, "International": 15}
emp_by_tier = {"SMB": [50,100,100,250,250,500,1000], "Mid-Market": [250,500,1000,1000,2500,5000],
               "Enterprise": [1000,2500,5000,10000,25000,50000]}
W = lambda dct: random.choices(list(dct), weights=list(dct.values()))[0]
accounts = []
for i in range(2000):
    tier = W(tier_w)
    name = f"{random.choice(pre)} {random.choice(mid)} {random.choice(suf)}".strip()
    if random.random() < 0.2:            # data-quality issue kept on purpose: trailing spaces
        name += " "
    accounts.append(dict(AccountID=f"ACC{i+1:05d}", AccountName=name, Industry=W(ind_w),
                         EmployeeCount=random.choice(emp_by_tier[tier]), AccountTier=tier, Region=W(reg_w),
                         FirstPurchaseDate=d(date(2021, 7, 1), date(2023, 12, 10)).isoformat(),
                         IsChurned=0, ChurnDate=""))

# churn: field only populated from Dec 2023 (kept on purpose), higher for SMB
churn_p = {"SMB": 0.11, "Mid-Market": 0.07, "Enterprise": 0.04}
for a in accounts:
    if random.random() < churn_p[a["AccountTier"]]:
        a["IsChurned"] = 1
        a["ChurnDate"] = d(date(2023, 12, 10), date(2024, 11, 15)).isoformat()

# ---------- Sales_Transactions ----------
def close_date():
    # monthly volume flat until Oct 2024, then the feed dries up (truncated last quarter, kept on purpose)
    while True:
        c = d(START, date(2024, 12, 12))
        if c < date(2024, 11, 1): return c
        if c.month == 11 and random.random() < 0.5: return c
        if c.month == 12 and random.random() < 0.08: return c

tier_mult = {"SMB": 0.55, "Mid-Market": 1.0, "Enterprise": 1.9}
def amount(deal, tier):
    base = random.lognormvariate(math.log(50000), 0.55) * tier_mult[tier]
    if deal == "Expansion":   base *= random.uniform(0.2, 0.45)
    if deal == "Contraction": base *= -random.uniform(0.08, 0.3)
    return round(max(base, 1500) if base > 0 else min(base, -1500), 2)

served = random.sample(accounts, 1900)       # 100 accounts with no closed deal (untouched)
txns = []
for a in served:
    own = random.random() < 0.8
    pool = by_terr[a["Region"]] if own else [r for r in reps if r["Territory"] != a["Region"]]
    rep = random.choice(pool)
    n = random.choices([1, 2, 3], weights=[62, 33, 5])[0]
    first_type = random.choices(["Renewal", "New Business"], weights=[61, 39])[0]
    for k in range(n):
        deal = first_type if k == 0 else random.choices(["Expansion", "Contraction", "Renewal"], weights=[58, 24, 18])[0]
        cd = close_date()
        if a["ChurnDate"] and cd >= date.fromisoformat(a["ChurnDate"]):
            cd = d(START, date.fromisoformat(a["ChurnDate"]) - timedelta(days=1))  # no deals after churn
        txns.append(dict(AccountID=a["AccountID"], OpportunityOwnerID=rep["EmployeeID"], CloseDate=cd.isoformat(),
                         BookingAmount=amount(deal, a["AccountTier"]),
                         ProductCategory=random.choice(["Analytics", "Platform", "Marketing", "Sales"]),
                         DealType=deal, ContractTerm=random.choice([12, 24, 36]), SalesStage="Closed Won"))
random.shuffle(txns)
for i, t in enumerate(txns):
    t["TransactionID"] = f"TXN{i+1:06d}"
txns.sort(key=lambda t: t["CloseDate"])
tcols = ["TransactionID","AccountID","OpportunityOwnerID","CloseDate","BookingAmount","ProductCategory","DealType","ContractTerm","SalesStage"]

def write(name, rows, cols):
    with open(f"{OUT}/{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)

write("Date_Table", dates, list(dates[0]))
write("Sales_Reps", reps, list(reps[0]))
write("Accounts", accounts, list(accounts[0]))
write("Sales_Transactions", txns, tcols)
print(len(dates), len(reps), len(accounts), len(txns))
