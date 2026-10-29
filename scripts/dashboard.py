"""Render public GitHub repository metrics without third-party image services."""
import json
import os
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen

owner = 'Sabbirshay'
repos = []
for page in range(1, 101):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'profile-dashboard'}
    if os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    req = Request(f'https://api.github.com/users/{owner}/repos?type=owner&per_page=100&page={page}', headers=headers)
    with urlopen(req, timeout=30) as response:
        batch = json.load(response)
    repos.extend(r for r in batch if not r.get('private'))
    if len(batch) < 100:
        break

languages = Counter(r['language'] for r in repos if r.get('language') and not r.get('fork'))
metrics = [('PUBLIC REPOS', len(repos)), ('STARS', sum(r['stargazers_count'] for r in repos)), ('FORKS', sum(r['forks_count'] for r in repos))]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-labelledby="title"><title id="title">Public GitHub repository dashboard</title><rect width="1000" height="260" rx="18" fill="#0d1117"/><g font-family="DejaVu Sans,Arial,sans-serif">']
parts.append('<text x="35" y="40" fill="#c4b5fd" font-size="16">GITHUB / PUBLIC OVERVIEW</text>')
for i, (label, value) in enumerate(metrics):
    x = 35 + i * 320
    parts.append(f'<text x="{x}" y="112" fill="#f0f6fc" font-size="44">{value}</text><text x="{x}" y="145" fill="#9ca3af" font-size="14">{label}</text>')
summary = ' · '.join(f'{name}: {count} repos' for name, count in languages.most_common(5)) or 'No primary languages reported yet'
parts.append(f'<text x="35" y="195" fill="#c4b5fd" font-size="15">{escape(summary)}</text>')
stamp = datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M UTC')
parts.append(f'<text x="35" y="231" fill="#9ca3af" font-size="12">Updated {stamp} · Languages counted by primary repository language</text></g></svg>')
Path('assets').mkdir(exist_ok=True)
Path('assets/dashboard.svg').write_text(''.join(parts))
