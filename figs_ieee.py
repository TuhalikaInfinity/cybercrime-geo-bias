# Makes all four figures at IEEE column sizes. Run in Colab after the files are uploaded.
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
BLUE, ORANGE, GREY = '#2a78d6', '#eb6834', '#9aa0a6'
plt.rcParams.update({'font.size': 7, 'axes.titlesize': 7.5, 'axes.labelsize': 7,
                     'xtick.labelsize': 6.5, 'ytick.labelsize': 6.5, 'legend.fontsize': 6.5,
                     'axes.spines.top': False, 'axes.spines.right': False})
OUT = {'map': 'fig1_map_ic3_vs_umd.png', 'fig1': 'fig2_broadband_vs_complaints.png',
       'fig2': 'fig3_umd_unknown_state.png', 'fig3': 'fig4_ai_probe_2023.png', 'fig4': 'fig5_rq3_p1.png'}

# ---------- shared data ----------
umd = pd.read_csv('cyber_events_2026-11-10.csv', low_memory=False)
ic3 = pd.read_csv('ic3_complaints_by_state_v2.csv')
pop = pd.read_csv('ACSDT1Y2025.B01003-2026-11-10T204727.csv')
net = pd.read_csv('ACSST1Y2025.S2801-2026-11-10T204620.csv')
est = pop.iloc[0, 1:]
est = est[[c for c in est.index if c.endswith('!!Estimate')]]
pop_df = pd.DataFrame({'state': [c.replace('!!Estimate', '') for c in est.index],
                       'population': est.astype(str).str.replace(',', '').astype(int).values})
t = ic3.merge(pop_df, on='state', how='inner')
t['per100k_2025'] = (t['complaints_2025'] / t['population'] * 100000).round(1)

# ---------- Figure 1: tile-grid maps, IC3 vs UMD ----------
from matplotlib.colors import Normalize
ab = {'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE','District of Columbia':'DC','Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY','Puerto Rico':'PR'}
grid = {'AK':(0,0),'ME':(0,10),'VT':(1,9),'NH':(1,10),
 'WA':(2,0),'ID':(2,1),'MT':(2,2),'ND':(2,3),'MN':(2,4),'IL':(2,5),'WI':(2,6),'MI':(2,7),'NY':(2,8),'RI':(2,9),'MA':(2,10),
 'OR':(3,0),'NV':(3,1),'WY':(3,2),'SD':(3,3),'IA':(3,4),'IN':(3,5),'OH':(3,6),'PA':(3,7),'NJ':(3,8),'CT':(3,9),
 'CA':(4,0),'UT':(4,1),'CO':(4,2),'NE':(4,3),'MO':(4,4),'KY':(4,5),'WV':(4,6),'VA':(4,7),'MD':(4,8),'DE':(4,9),
 'AZ':(5,1),'NM':(5,2),'KS':(5,3),'AR':(5,4),'TN':(5,5),'NC':(5,6),'SC':(5,7),'DC':(5,8),
 'OK':(6,3),'LA':(6,4),'MS':(6,5),'AL':(6,6),'GA':(6,7),
 'HI':(7,0),'TX':(7,3),'FL':(7,8),'PR':(7,10)}
us_ = umd[umd['country'] == 'United States of America']
rec = us_[us_['year'].between(2023, 2025) & us_['state'].notna() & (us_['state'] != 'Undetermined')]
cnt = rec['state'].value_counts().rename_axis('state').reset_index(name='umd_events')
m = t.merge(cnt, on='state', how='left').fillna({'umd_events': 0})
m['ic3'] = m['complaints_2025'] / m['population'] * 1e5
m['umd'] = m['umd_events'] / m['population'] * 1e6
m['abbr'] = m['state'].map(ab)
def tiles(ax, col, title, label):
    vals = m.set_index('abbr')[col]
    norm = Normalize(vmin=vals.min(), vmax=vals.max()); cmap = plt.cm.Blues
    for a,(r,c) in grid.items():
        v = vals[a]; rgba = cmap(0.12+0.83*norm(v))
        ax.add_patch(plt.Rectangle((c,-r),0.92,0.92,color=rgba,lw=0))
        lum = 0.299*rgba[0]+0.587*rgba[1]+0.114*rgba[2]
        ax.text(c+0.46,-r+0.46,a,ha='center',va='center',fontsize=5.5,color='white' if lum<0.55 else '#222')
    ax.set_xlim(-0.1,11); ax.set_ylim(-7.1,1); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title,fontsize=7.5)
    sm = plt.cm.ScalarMappable(norm=Normalize(vals.min(),vals.max()),cmap=plt.matplotlib.colors.LinearSegmentedColormap.from_list('b',[cmap(0.12),cmap(0.95)]))
    cb = plt.colorbar(sm,ax=ax,orientation='horizontal',fraction=0.05,pad=0.02,aspect=30); cb.ax.tick_params(labelsize=6); cb.set_label(label,fontsize=6.5); cb.outline.set_linewidth(0)
fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.2))
tiles(axs[0], 'ic3', '(a) IC3 complaints, 2025', 'complaints per 100,000 residents')
tiles(axs[1], 'umd', '(b) UMD events, 2023-2025', 'events per million residents')
fig.subplots_adjust(top=0.92, bottom=0.17, left=0.01, right=0.99, wspace=0.05)
plt.savefig(OUT['map'], dpi=300); plt.close()

# ---------- Figure 2: broadband vs complaints ----------
net['label'] = net.iloc[:, 0].str.replace('\xa0', '', regex=False).str.strip()
row = net[net['label'] == 'Broadband of any type'].iloc[0]
cols = [c for c in net.columns if c.endswith('Percent!!Estimate')]
bb = pd.DataFrame({'state': [c.split('!!')[0] for c in cols],
                   'broadband_pct': [float(str(row[c]).replace('%', '')) for c in cols]})
t2 = t.merge(bb, on='state')
fig, ax = plt.subplots(figsize=(3.4, 2.6))
ax.scatter(t2['broadband_pct'], t2['per100k_2025'], s=9, alpha=0.8, color=BLUE, linewidths=0)
for _, r in t2.iterrows():
    if r['per100k_2025'] > 370 or r['per100k_2025'] < 150:
        ax.annotate(r['state'], (r['broadband_pct'], r['per100k_2025']), fontsize=5.5,
                    xytext=(2, 2), textcoords='offset points')
ax.set_xlabel('Households with broadband (%), ACS 2025')
ax.set_ylabel('IC3 complaints per 100,000, 2025')
ax.yaxis.grid(True, color='#e5e5e5', lw=0.5); ax.set_axisbelow(True)
plt.tight_layout(); plt.savefig(OUT['fig1'], dpi=300); plt.close()

# ---------- Figure 3: UMD unknown state ----------
us = umd[umd['country'] == 'United States of America'].copy()
us['unknown_state'] = us['state'].isna() | (us['state'] == 'Undetermined')
g = us[us['year'].between(2014, 2025)].groupby('year')['unknown_state'].agg(['mean', 'size']).reset_index()
fig, ax = plt.subplots(figsize=(3.4, 2.4))
ax.bar(g['year'], g['mean'] * 100, color=BLUE, width=0.65)
ax.set_xticks(g['year']); ax.set_xticklabels([str(y)[2:] for y in g['year']])
for idx in [g['mean'].idxmax(), g['mean'].idxmin()]:
    ax.text(g.loc[idx, 'year'], g.loc[idx, 'mean'] * 100 + 0.8, f"{g.loc[idx, 'mean']*100:.0f}%",
            ha='center', fontsize=6.5)
ax.set_xlabel("Year (20xx)"); ax.set_ylabel('% of U.S. events, state unknown')
ax.yaxis.grid(True, color='#e5e5e5', lw=0.5); ax.set_axisbelow(True)
plt.tight_layout(); plt.savefig(OUT['fig2'], dpi=300); plt.close()

# ---------- Figure 4: AI estimates (two panels, full width) ----------
pr = pd.read_csv('probe_2023_estimates.csv')
pr['estimate'] = pd.to_numeric(pr['estimate'], errors='coerce')
r = pr.merge(t[['state', 'complaints_2023', 'population']], on='state')
r['abs_log_err'] = np.log(r['estimate'] / r['complaints_2023']).abs()
gg = r.dropna(subset=['estimate']).groupby('state').agg(est_mean=('estimate', 'mean'),
        abs_log_err=('abs_log_err', 'mean')).reset_index().merge(t[['state', 'complaints_2023', 'population']], on='state')
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6))
ax[0].scatter(gg['complaints_2023'], gg['est_mean'], s=9, alpha=0.8, color=BLUE, linewidths=0)
lims = [gg['complaints_2023'].min() * 0.6, gg['complaints_2023'].max() * 1.6]
ax[0].plot(lims, lims, color='black', ls='--', lw=0.7); ax[0].set_xscale('log'); ax[0].set_yscale('log')
ax[0].set_xlabel('IC3 complaints 2023 (actual)'); ax[0].set_ylabel('Model estimate (mean of 3 runs)')
ax[0].set_title('(a) Estimate vs. actual, by state')
ax[1].scatter(gg['population'], gg['abs_log_err'], s=9, alpha=0.8, color=BLUE, linewidths=0)
ax[1].set_xscale('log'); ax[1].set_xlabel('State population'); ax[1].set_ylabel('Mean |log(estimate / actual)|')
ax[1].set_title('(b) Error vs. state size')
plt.tight_layout(); plt.savefig(OUT['fig3'], dpi=300); plt.close()

# ---------- Figure 5: RQ3, P1 answers (4 strata) ----------
rq = pd.concat([pd.read_csv('probe_rq3.csv'), pd.read_csv('probe_rq3_size.csv')], ignore_index=True)
p1 = rq[rq['probe'] == 'P1']
order = ['S1_high', 'S2_one_event', 'S3_zero_events', 'S4_zero_midsize']
labels = ['High\n(70-236 events)', 'One event', 'No record,\ntiny (<1,000)', 'No record,\nmid-size (25-60k)']
cols4 = {'yes': BLUE, 'no': ORANGE, 'unknown': GREY}
ct = pd.crosstab(p1['stratum'], p1['answer']).reindex(order).reindex(columns=['yes', 'no', 'unknown']).fillna(0)
fig, ax = plt.subplots(figsize=(3.4, 2.5))
left = np.zeros(len(order))
for a in ['yes', 'no', 'unknown']:
    share = (ct[a] / ct.sum(axis=1)).values * 100
    ax.barh(labels, share, left=left, color=cols4[a], edgecolor='white', linewidth=1.5, height=0.6, label=a)
    for i, (l, s_) in enumerate(zip(left, share)):
        if s_ > 6:
            ax.text(l + s_ / 2, i, f"{int(ct[a].iloc[i])}", ha='center', va='center', color='white',
                    fontsize=7, fontweight='bold')
    left += share
ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xlabel('% of P1 responses (numbers = response counts)')
ax.legend(ncol=3, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.28))
plt.tight_layout(); plt.savefig(OUT['fig4'], dpi=300, bbox_inches='tight'); plt.close()
print('done:', list(OUT.values()))

# ---------- download the four figures ----------
from google.colab import files
for f in OUT.values():
    files.download(f)
