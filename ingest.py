import os, re, json, sys
ARCH='archive'
def slug(t):
    s=re.sub(r"[’'`]",'',t.lower()); s=re.sub(r'[^a-z0-9]+','-',s).strip('-'); return s[:95].rstrip('-')
def write(meta, body, claims):
    fn=f"{meta['published']}_{meta['outlet_slug']}_{slug(meta['title'])}.md"
    fm=['---',f'title: "{meta["title"].replace(chr(34),chr(39))}"',
        f'outlet: {meta["outlet"]}', f'author: {meta.get("author","")}',
        f'published: {meta["published"]}', f'url: {meta["url"]}',
        'retrieved: 2026-07-27',
        'retrieval_method: browser session (blocked to fetch tools)',
        f'stream: {meta.get("stream","gap-recovery-international")}',
        f'tier: {meta.get("tier","international-press")}',
        f'capture_fidelity: {meta.get("fidelity","extract")}',
        'key_claims:']
    for c in claims: fm.append(f'  - "{c.replace(chr(34),chr(39))}"')
    fm+=['---','']
    open(os.path.join(ARCH,fn),'w',encoding='utf-8').write('\n'.join(fm)+f'# {meta["title"]}\n\n'+body+'\n')
    return fn
