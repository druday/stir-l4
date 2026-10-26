"""Audit 6: live ClinicalTrials.gov API v2 checks of every NCT id named in the conversation, and of the register claims."""
import json, ssl, urllib.request, time, sys, os
import certifi

CTX = ssl.create_default_context(cafile=certifi.where())
W = sys.argv[1]

def get(url):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'stir-l4-audit'}), context=CTX, timeout=60) as r:
                return json.loads(r.read())
        except Exception as e:
            err = e; time.sleep(2)
    raise err

SHOWN = {
 'NCT06095492': ('India', 'recruiting', ['lean mass', 'total fat']),
 'NCT07240844': ('South Korea', 'recruiting', ['body fat', 'extracellular water', 'total body water']),
 'NCT06448130': ('China', 'not yet recruiting', ['body fat']),
 'NCT06398977': ('China', 'recruiting', ['body water']),
 'NCT07687212': ('China', 'not yet recruiting', ['adiposity', 'body fat', 'sarcopenia']),
 'NCT06838286': ('South Korea', 'recruiting', ['body composition', 'body fat']),
 'NCT06782139': ('South Korea', 'recruiting', ['body composition', 'sarcopenia', 'skeletal muscle', 'visceral fat']),
 'NCT07711171': ('China', 'recruiting', ['body composition', 'body fat', 'skeletal muscle', 'visceral fat']),
}
for nct, (country, status, words) in SHOWN.items():
    s = get('https://clinicaltrials.gov/api/v2/studies/' + nct)
    ps = s['protocolSection']
    countries = sorted({l.get('country') for l in ps.get('contactsLocationsModule', {}).get('locations', [])})
    st = ps['statusModule']['overallStatus']
    outc = json.dumps(ps.get('outcomesModule', {})).lower()
    intr = [i.get('name') for i in ps.get('armsInterventionsModule', {}).get('interventions', [])]
    print(nct, '|', ps['identificationModule'].get('briefTitle', '')[:90])
    print('   live status', st, '| countries', countries, '| shown', country, status)
    print('   interventions', intr)
    print('   outcome words present:', {w: (w in outc) for w in words})
    print('   conditions', ps.get('conditionsModule', {}).get('conditions'))

print()
for nct in ['NCT05580510', 'NCT06668389', 'NCT05042973', 'NCT03193684']:
    s = get('https://clinicaltrials.gov/api/v2/studies/' + nct)
    ps = s['protocolSection']
    refs = ps.get('referencesModule', {}).get('references', [])
    pm = [(r.get('pmid'), r.get('type')) for r in refs]
    print(nct, '|', ps['identificationModule'].get('briefTitle', '')[:110])
    print('   conditions', ps.get('conditionsModule', {}).get('conditions'), '| status', ps['statusModule']['overallStatus'])
    print('   references (%d):' % len(refs), pm)
# version timestamp
v = get('https://clinicaltrials.gov/api/v2/version')
print('ctgov data timestamp now:', v)
