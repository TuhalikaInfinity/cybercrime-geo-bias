# ===== CELL A: county populations (ACS 5-year) + size/documentation table =====
import os
import pandas as pd, numpy as np

def get_county_pop():
    # Census Population Estimates (vintage 2025): population of every county, including very small ones
    fname = "co-est2025-alldata.csv"
    url = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/" + fname
    src = fname if os.path.exists(fname) else url
    try:
        df = pd.read_csv(src, encoding="latin-1")
    except Exception as e:
        raise SystemExit("Could not download the Census file (" + str(e)[:80] + "). Download it in your browser from\n"
                         + url + "\nupload it to Colab (left Files panel) and run this cell again.")
    df = df[df["SUMLEV"] == 50].copy()          # 50 = county rows (40 = state rows)
    popcol = sorted(c for c in df.columns if c.startswith("POPESTIMATE"))[-1]
    df = df.rename(columns={"STNAME": "state", "CTYNAME": "county_name", popcol: "population"})
    print(f"Census {popcol}: {len(df)} counties")
    return df[["state", "county_name", "population"]]

def key(state, county):
    c = (county.astype(str).str.replace(r" (County|Parish)$", "", regex=True)
         .str.strip().str.lower())
    return state.astype(str).str.strip() + "|" + c

cp = get_county_pop()
cp["key"] = key(cp["state"], cp["county_name"])

rq = pd.read_csv("probe_rq3.csv")
p1 = rq[rq["probe"] == "P1"].copy()
p1["key"] = key(p1["state"], p1["county"])
tab = (p1.groupby(["stratum", "state", "county", "key"])["answer"].value_counts()
         .unstack(fill_value=0).reset_index())
for a in ["yes", "no", "unknown"]:
    if a not in tab: tab[a] = 0
tab = tab.merge(cp[["key", "population"]], on="key", how="left")
print("\nCounties not matched to Census (check spelling):",
      tab.loc[tab["population"].isna(), ["state", "county"]].values.tolist())
tab = tab.sort_values("population")
print(tab[["stratum", "state", "county", "population", "yes", "no", "unknown"]].to_string(index=False))
tab.to_csv("rq3_county_population.csv", index=False)



# ===== CELL B: new stratum - mid-size counties with NO UMD record, same P1 question =====
import os, time, json
import pandas as pd, numpy as np
try:
    client
except NameError:
    try:
        from google import genai
    except ImportError:
        import subprocess, sys
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "google-genai"])
        from google import genai
    from google.colab import userdata
    client = genai.Client(api_key=userdata.get("GEMINI_API_KEY"))
from google.genai import types
MODEL = "gemini-3.1-flash-lite"
cfg = types.GenerateContentConfig(response_mime_type="application/json", temperature=0.7)

# same P1 wording as before
P1 = ("Between 2014 and 2025, has any organization located in {county} County, {state} been publicly reported "
      "as the victim of a cyber attack (for example ransomware or a data breach)? Respond ONLY as JSON: "
      '{{"answer": "yes" or "no" or "unknown", "confidence": <number 0 to 1>, "note": "<one short sentence>"}}')

umd = pd.read_csv("cyber_events_2026-11-10.csv", low_memory=False)
us = umd[(umd["country"] == "United States of America") & umd["county"].notna() & umd["state"].notna()]
umd_keys = set(key(us["state"], us["county"]))

cand = cp[cp["county_name"].str.endswith(" County") & cp["population"].between(25000, 60000)].copy()
cand = cand[~cand["key"].isin(umd_keys)]
print("mid-size counties (25k-60k) with no UMD record:", len(cand))
pick = cand.sample(8, random_state=42).copy()
pick["county"] = pick["county_name"].str.replace(" County", "", regex=False)
print(pick[["state", "county", "population"]].to_string(index=False))

def ask_prompt(prompt, tries=3):
    for k in range(tries):
        try:
            r = client.models.generate_content(model=MODEL, contents=prompt, config=cfg)
            return json.loads(r.text)
        except Exception as e:
            print("  retry", str(e)[:60]); time.sleep(30 * (k + 1))
    return None

OUT, REPS, PAUSE = "probe_rq3_size.csv", 2, 10
rows = pd.read_csv(OUT).to_dict("records") if os.path.exists(OUT) else []
done = {(r["state"], r["county"], r["rep"]) for r in rows}
fails, stop = 0, False
for rep in range(REPS):
    for _, p in pick.iterrows():
        if (p.state, p.county, rep) in done: continue
        out = ask_prompt(P1.format(state=p.state, county=p.county))
        if out is None:
            fails += 1
            if fails >= 3: stop = True; break
            continue
        fails = 0
        out.update(stratum="S4_zero_midsize", state=p.state, county=p.county,
                   population=int(p.population), probe="P1", rep=rep)
        rows.append(out); pd.DataFrame(rows).to_csv(OUT, index=False); time.sleep(PAUSE)
    if stop: print("STOPPED: 3 failures in a row. Saved so far:", len(rows)); break
    print("round", rep, "finished | total saved:", len(rows))
print("DONE" if not stop else "PARTIAL", len(rows), "responses")



# ===== CELL C: compare same-size counties: 1 UMD event vs 0 UMD events =====
new = pd.read_csv("probe_rq3_size.csv")
rows_old = p1.merge(cp[["key", "population"]], on="key", how="left")
same = rows_old[(rows_old["stratum"] == "S2_one_event") & rows_old["population"].between(25000, 60000)]
grp = pd.concat([same[["stratum", "county", "population", "answer"]],
                 new[["stratum", "county", "population", "answer"]]])
print("Counties compared (population 25k-60k):")
print(grp.groupby(["stratum", "county"])["population"].first().to_string())
print("\nP1 answers, share of responses:")
print(pd.crosstab(grp["stratum"], grp["answer"], normalize="index").round(2).to_string())
print("\nP1 answers, counts:")
print(pd.crosstab(grp["stratum"], grp["answer"]).to_string())
if "confidence" in new:
    print("\nmean confidence (new stratum):", round(pd.to_numeric(new["confidence"], errors="coerce").mean(), 2))
