"""G1.1 pre-inventory: enumerate legacy graphs, classes and ports without editing graphs."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

BUILTINS = {'LoadImage', 'PreviewImage', 'InvertMask'}
MAX_JSON_BYTES = 4_000_000


def read_graph(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError('workflow non régulier ou trop volumineux')
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not isinstance(data.get('nodes'), list) or not isinstance(data.get('links'), list):
        raise ValueError('workflow JSON avec nodes/links requis')
    return data


def registry_from_root(root: Path) -> tuple[dict, dict]:
    name = '_smartsvg_governance_runtime'
    # Package import is needed for relative imports in historical nodes.
    spec = importlib.util.spec_from_file_location(name, root / '__init__.py', submodule_search_locations=[str(root)])
    if spec is None or spec.loader is None:
        raise ValueError('impossible de charger le registre de noeuds')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
        return dict(mod.NODE_CLASS_MAPPINGS), dict(mod.NODE_DISPLAY_NAME_MAPPINGS)
    finally:
        for key in tuple(sys.modules):
            if key == name or key.startswith(name + '.'):
                del sys.modules[key]


def classify_workflow(name: str, kinds: set[str]) -> str:
    low = name.lower()
    if 'expert' in low or any('ai' in k.lower() or 'diagnos' in k.lower() for k in kinds):
        return 'Expert / diagnostic (candidat)'
    if 'express' in low or 'cricut_direct' in low or 'png_alpha' in low:
        return 'Express (candidat)'
    return 'Historique / cas specialise (candidat)'


def _warn_graph(graph: dict, valid_types: set[str], registry: dict | None = None) -> list[str]:
    warnings: list[str] = []
    nodes = graph['nodes']; links = graph['links']
    node_ids = [node.get('id') for node in nodes if isinstance(node, dict)]
    if len(node_ids) != len(nodes) or len({str(x) for x in node_ids}) != len(nodes):
        warnings.append('NODE_ID_INVALIDE_OU_DUPLIQUE')
    if any(not isinstance(node, dict) or not isinstance(node.get('type'), str) for node in nodes):
        warnings.append('NODE_MALFORME')
    unknown = sorted({node.get('type') for node in nodes if isinstance(node, dict) and isinstance(node.get('type'), str) and node['type'] not in valid_types})
    if unknown:
        warnings.append('TYPE_INCONNU:' + ','.join(unknown))
    if registry is not None:
        for node in nodes:
            if not isinstance(node, dict):
                continue
            cls = registry.get(node.get('type'))
            if cls is None:
                continue
            try:
                spec = cls.INPUT_TYPES()
                required = set(spec.get('required', {}))
                permitted = required | set(spec.get('optional', {}))
                connected = [p.get('name') for p in node.get('inputs', [])]
                if required - set(connected):
                    warnings.append('PORT_REQUIS_MANQUANT:' + str(node['type']))
                if set(connected) - permitted:
                    warnings.append('PORT_INCONNU:' + str(node['type']))
                if [p.get('type') for p in node.get('outputs', [])] != list(getattr(cls, 'RETURN_TYPES', ())):
                    warnings.append('PORT_SORTIE_INCOMPATIBLE:' + str(node['type']))
            except (TypeError, KeyError, AttributeError, ValueError):
                warnings.append('PORTS_NON_VERIFIABLES:' + str(node.get('type')))
    mapping = {str(n['id']): n for n in nodes if isinstance(n, dict) and 'id' in n}
    seen_links: set[str] = set()
    for entry in links:
        if not isinstance(entry, list) or len(entry) < 5:
            warnings.append('LIEN_MALFORME'); continue
        link_id, src, src_port, dst, dst_port = entry[:5]
        if str(link_id) in seen_links:
            warnings.append('LIEN_ID_DUPLIQUE')
        seen_links.add(str(link_id))
        if str(src) not in mapping or str(dst) not in mapping:
            warnings.append('LIEN_NOEUD_ABSENT'); continue
        try:
            source_outputs = mapping[str(src)].get('outputs', [])
            target_inputs = mapping[str(dst)].get('inputs', [])
            if not (0 <= src_port < len(source_outputs) and 0 <= dst_port < len(target_inputs)):
                warnings.append('LIEN_PORT_ABSENT')
            elif len(entry) >= 6 and source_outputs[src_port].get('type') != entry[5]:
                warnings.append('LIEN_TYPE_SOURCE_INCOHERENT')
        except (TypeError, IndexError, AttributeError):
            warnings.append('LIEN_PORT_INVALIDE')
    return sorted(set(warnings))


def inventory(root: Path) -> dict:
    root = root.resolve()
    registry, display = registry_from_root(root)
    workflows = sorted((root / 'example_workflows').glob('*.json'))
    wf_rows: list[dict] = []
    type_usage: Counter[str] = Counter()
    fingerprints = defaultdict(list)
    errors: list[str] = []
    for path in workflows:
        try:
            graph = read_graph(path)
            types = Counter(str(n.get('type', '<invalide>')) for n in graph['nodes'] if isinstance(n, dict))
            type_usage.update(types)
            warnings = _warn_graph(graph, set(registry) | BUILTINS, registry)
            normalized = json.dumps(graph, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
            digest = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
            fingerprints[digest].append(path.name)
            wf_rows.append({
                'workflow': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'graph_sha256': digest, 'category': classify_workflow(path.name, set(types)),
                'node_count': len(graph['nodes']), 'link_count': len(graph['links']),
                'custom_node_types': '|'.join(sorted(t for t in types if t.startswith('SmartSVG'))),
                'unresolved_types': '|'.join(sorted(t for t in types if t not in registry and t not in BUILTINS)),
                'warnings': '|'.join(warnings),
            })
            if warnings:
                errors.append(path.name + ': ' + ', '.join(warnings))
        except (ValueError, UnicodeError, OSError, json.JSONDecodeError) as exc:
            errors.append(f'{path.name}: {type(exc).__name__}: {exc}')
    node_rows = []
    for node_id, cls in sorted(registry.items()):
        try:
            desc = cls.INPUT_TYPES()
            required = desc.get('required', {})
            optional = desc.get('optional', {})
            outputs = tuple(getattr(cls, 'RETURN_TYPES', ()))
            note = ''
        except Exception as exc:
            required, optional, outputs = {}, {}, ()
            note = f'PORTS_NON_LISIBLES:{type(exc).__name__}'
            errors.append(f'{node_id}: {note}')
        node_rows.append({
            'node_id': node_id, 'display_name': display.get(node_id, ''),
            'implementation_module': cls.__module__.split('.')[-1],
            'used_by_workflows': type_usage[node_id],
            'category': 'Utilise (historique compatible)' if type_usage[node_id] else 'Non reference par exemples',
            'required_inputs': '|'.join(required), 'optional_inputs': '|'.join(optional),
            'return_types': '|'.join(map(str, outputs)), 'warnings': note,
        })
    duplicate_groups = [names for names in fingerprints.values() if len(names) > 1]
    unused = sorted(t for t in type_usage if t not in registry and t not in BUILTINS)
    return {
        'report_type': 'READ_ONLY_PRE_INVENTORY_NOT_RUNTIME_VALIDATION',
        'workflow_count': len(workflows), 'workflow_parsed': len(wf_rows),
        'node_registration_count': len(registry), 'node_occurrences': sum(type_usage.values()),
        'custom_node_types_in_workflows': sum(1 for k in type_usage if k in registry),
        'unresolved_types': unused, 'duplicate_graph_groups': duplicate_groups,
        'warnings': errors, 'workflow_rows': wf_rows, 'node_rows': node_rows,
        'external_test_status': 'NOT_RUN: ComfyUI/Design Space/Explore 5',
    }


def write_inventory(root: Path, output: Path) -> dict:
    report = inventory(root)
    output.mkdir(parents=True, exist_ok=True)
    for key, name in (('node_rows', 'node_inventory.csv'), ('workflow_rows', 'workflow_inventory.csv')):
        rows = report[key]
        if rows:
            with (output / name).open('w', newline='', encoding='utf-8-sig') as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader(); writer.writerows(rows)
    summary = {k: v for k, v in report.items() if k not in ('workflow_rows', 'node_rows')}
    (output / 'inventory_result.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    lines = [
        '# G1.1 — Carte de compatibilité (pré-inventaire, aucune migration)', '',
        f'- Workflows présents : **{report["workflow_count"]}** ; JSON analysés : **{report["workflow_parsed"]}**.',
        f'- IDs SmartSVG enregistrés : **{report["node_registration_count"]}**.',
        f'- Types inconnus : {", ".join(report["unresolved_types"]) or "aucun dans les graphes analysés"}.',
        f'- Graphes identiques : {len(report["duplicate_graph_groups"])} groupe(s).',
        f'- Anomalies statiques : {len(report["warnings"])} workflow(s)/ID(s) signalés.', '',
        '## Politique de compatibilité', '',
        '1. Les anciens IDs restent inchangés ; aucune substitution automatique de nœud.',
        '2. « Candidat Express » et « historique » sont des étiquettes heuristiques, pas des garanties de bon fonctionnement.',
        '3. Un graphe JSON analysé n’est **pas** un graphe chargé dans ComfyUI.',
        '4. Les nœuds LoadImage, PreviewImage et InvertMask sont les types natifs autorisés par cette analyse.',
        '5. L’ouverture effective dans ComfyUI et les sorties CNC/Cricut nécessitent des essais sur PC cible.',
        '6. Aucune migration, aucune suppression, aucune modification des workflows sources.', '',
        '## Décision', '',
        'Pré-inventaire réalisé. G1.1 complet reste conditionné à la validation G0 et au chargement réel des workflows.',
    ]
    (output / 'compatibility_map.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return report
