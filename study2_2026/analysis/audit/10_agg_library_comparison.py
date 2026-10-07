"""AGG library: published configuration files versus the block actually sent to the models.

Usage: python3 10_agg_library_comparison.py <study2_2026 dir> [output dir]

Reads only. It extracts the common-library block from every archived AGG request of both models,
checks that it is one and the same block everywhere, and compares it with
configuration/insights/AGG_LIBRARY_BLOCK.txt, AGG_LIBRARY.json and the hash in PROVENANCE.json.
With an output directory it writes the block as sent, so that it can be diffed or adopted.
"""
import sys, re, json, gzip, hashlib, difflib, os
from collections import Counter
R = sys.argv[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
def gz(p):
    with gzip.open(p, 'rt', encoding='utf-8') as f:
        for l in f:
            if l.strip(): yield json.loads(l)
START, END = 'COMMON INSIGHT LIBRARY', '\n\nTARGET OBSERVATION'
blocks = Counter(); n = Counter(); sysprompts = Counter(); where = Counter()
for model in ('qwen', 'gpt_oss'):
    for r in gz(f'{R}/requests/{model}_requests.jsonl.gz'):
        if r['arm'] != 'AGG': continue
        n[model] += 1
        u = r['wire']['messages'][1]['content']; i = u.index(START); j = u.index(END, i)
        blocks[u[i:j]] += 1; sysprompts[r['wire']['messages'][0]['content']] += 1
        where[(u[:i].count('LOCAL EXAMPLES') > 0, u[j:].startswith(END))] += 1
print('AGG requests per model:', dict(n))
print('distinct library blocks across all AGG requests:', len(blocks), '| distinct system prompts:', len(sysprompts))
sent = next(iter(blocks)); sb = sent.encode('utf-8')
print(f'block as sent: {len(sb)} bytes, sha256 {sha(sb)}')
print('first line of the block as sent:', sent.split('\n')[0])

pub_path = f'{R}/configuration/insights/AGG_LIBRARY_BLOCK.txt'
pub_raw = open(pub_path, 'rb').read(); pub = pub_raw.decode('utf-8')
print(f'\npublished AGG_LIBRARY_BLOCK.txt: {len(pub_raw)} bytes, sha256 {sha(pub_raw)}')
prov = json.load(open(f'{R}/configuration/PROVENANCE.json'))
def find(o, key):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key: return v
            x = find(v, key)
            if x is not None: return x
    if isinstance(o, list):
        for v in o:
            x = find(v, key)
            if x is not None: return x
declared = find(prov, 'aggregatedLibrarySha256')
print('PROVENANCE aggregatedLibrarySha256:', declared)
for name, data in (('published file, bytes as stored', pub_raw), ('published file, trailing newline removed', pub.rstrip('\n').encode()), ('block as sent', sb), ('block as sent + newline', sb + b'\n')):
    print(f'   equals sha256 of {name}: {sha(data) == declared}')
print('published file identical to the block as sent:', pub == sent)
print('published text occurs anywhere in an AGG request:', any(pub.strip() in u for u in [sent]))

# entry by entry
ent = lambda t: {m.group(1): m.group(0) for m in re.finditer(r'\[(AGG-INS-\d+)\][^\n]*(?:\n(?!\[AGG-INS-)[^\n]*)*', t)}
es, ep = ent(sent), ent(pub)
records = {}
for m in re.finditer(r'(?m)^\[(AGG-INS-\d+)\] entry kind: ([^|]+) \|[^\n]*\n(.*?)(?=\n\n\[AGG-INS-|$)', sent):
    records[m.group(1)] = (m.group(2).strip(), m.group(3).strip())
print(f'\nentries: as sent {len(es)}, published {len(ep)}, same IDs {sorted(es) == sorted(ep)}')
nums = lambda t: re.findall(r'(?<![A-Za-z-])\d+(?:\.\d+)?', re.sub(r'AGG-INS-\d+|P05-INS-F\d+|XMEAS-\d+|F\d+', '', t))
split = lambda e: (e.split('\n', 1) + [''])[:2]
same_text = same_num = hdr_kind = 0
added = Counter(); removed = Counter()
for k in sorted(es):
    hs, bs = split(es[k]); hp, bp = split(ep.get(k, ''))
    hdr_kind += ('entry kind:' in hs) and ('entry kind:' not in hp)
    norm = lambda t: re.sub(r'\s+', ' ', t).strip()
    same_text += norm(bs) == norm(bp); same_num += nums(es[k]) == nums(ep.get(k, ''))
    sm = difflib.SequenceMatcher(None, norm(bp).split(' '), norm(bs).split(' '), autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ('insert', 'replace'): added[' '.join(norm(bs).split(' ')[j1:j2])] += 1
        if tag in ('delete', 'replace'): removed[' '.join(norm(bp).split(' ')[i1:i2])] += 1
    print(f'   {k}: header as sent "{hs[:70]}" | published "{hp[:70]}"')
print(f'headers where only the block as sent has "entry kind:": {hdr_kind} of {len(es)}')
print(f'entries whose body text is identical: {same_text} of {len(es)}; entries with the same numbers in the same order: {same_num} of {len(es)}')
print('text present in the block as sent and absent from the published file (phrase: entries):')
for t, c in added.most_common(12): print(f'   {c:2d} x "{t[:110]}"')
print('text present in the published file and absent from the block as sent:')
for t, c in removed.most_common(12): print(f'   {c:2d} x "{t[:110]}"')

lib = json.load(open(f'{R}/configuration/insights/AGG_LIBRARY.json'))
lib_by_id = {e['entry_id']: e for e in lib['entries']}
structured_exact = len(lib_by_id) == len(records) and all(lib_by_id.get(i, {}).get('entry_kind') == k and lib_by_id.get(i, {}).get('text') == body for i, (k, body) in records.items())
print('AGG_LIBRARY.json entry kind/text exactly matches prompt blocks:', structured_exact)
flat = json.dumps(lib, ensure_ascii=False)
print('\nAGG_LIBRARY.json: contains "standard-deviation ratio":', 'standard-deviation ratio' in flat, '| contains "after linear detrending":', 'after linear detrending' in flat,
      '| contains "entry kind" or kind field:', ('entry kind' in flat) or ('"kind"' in flat) or ('entry_kind' in flat) or ('entryKind' in flat))
print('block as sent: contains "standard-deviation ratio":', 'standard-deviation ratio' in sent, '| "after linear detrending":', 'after linear detrending' in sent)
if len(sys.argv) > 2:
    os.makedirs(sys.argv[2], exist_ok=True)
    open(os.path.join(sys.argv[2], 'AGG_LIBRARY_BLOCK_as_sent.txt'), 'wb').write(sb)
    open(os.path.join(sys.argv[2], 'AGG_LIBRARY_BLOCK_published_vs_sent.diff'), 'w', encoding='utf-8').write(
        ''.join(difflib.unified_diff(pub.splitlines(True), sent.splitlines(True), 'published AGG_LIBRARY_BLOCK.txt', 'block as sent in the AGG requests')))
    print('written:', sys.argv[2])

failures=[]
if len(blocks)!=1: failures.append('archived requests do not contain exactly one library block')
if pub!=sent: failures.append('published block differs from prompt block')
if sha(pub_raw)!=declared: failures.append('provenance digest differs from published block')
if not structured_exact: failures.append('structured entry text differs from prompt block')
if failures: raise SystemExit('AGG library audit failed: '+'; '.join(failures))
print('AGG library audit passed: prompt block, structured text, and provenance digest match.')
