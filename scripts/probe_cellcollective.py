"""Read-only probe of the published-model endpoint used by official ccapi."""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = []
    for host in ('cellcollective.org', 'research.cellcollective.org', 'research.cellcollective.org/web'):
        url = f'https://{host}/api/model/cards/research?modelTypes=boolean&orderBy=recent&category=published&cards=10000'
        record = {'url': url, 'utc': datetime.now(timezone.utc).isoformat()}
        try:
            with urlopen(Request(url, headers={'User-Agent': 'cc-reduction-research', 'Accept': 'application/json'}), timeout=30) as response:
                data = response.read()
                record.update(status=response.status, content_type=response.headers.get('Content-Type'), bytes=len(data))
                try:
                    parsed = json.loads(data)
                    target = ROOT / 'data/cellcollective' / f'live-{host.replace("/", "-")}.json'
                    target.write_text(json.dumps(parsed, indent=2), encoding='utf-8')
                    record.update(json=True, items=len(parsed) if isinstance(parsed, (dict, list)) else None)
                except ValueError:
                    record.update(json=False, prefix=data[:120].decode('utf-8', errors='replace'))
        except Exception as error:
            record['error'] = str(error)
        records.append(record)
        print(json.dumps(record), flush=True)
    (ROOT / 'data/cellcollective/live_probe.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
