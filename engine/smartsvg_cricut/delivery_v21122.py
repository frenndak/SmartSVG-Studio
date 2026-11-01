"""One-click delivery checklist after manufacturing; never alters original PNG/SVG.

This is a conservative file/integrity check, NOT a Cricut Design Space import test.
"""
from __future__ import annotations
import hashlib,json,os
from pathlib import Path
from uuid import uuid4


class DeliveryError(ValueError):pass


def _owned_file(folder,raw):
    if not isinstance(raw,str) or not raw or len(raw)>4096:raise DeliveryError('Chemin de fichier manquant')
    p=Path(raw)
    if not p.is_absolute() or p.is_symlink():raise DeliveryError('Chemin relatif ou symbolique refuse')
    try:
        q=p.resolve(strict=True)
        q.relative_to(folder)
    except (OSError,ValueError):raise DeliveryError('Fichier hors projet ou introuvable') from None
    if not q.is_file() or q.stat().st_size==0:raise DeliveryError('Fichier vide ou non regulier')
    return q


def _hash(path):
    h=hashlib.sha256()
    with path.open('rb') as file:
        for block in iter(lambda:file.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def delivery_manifest(report):
    """Inspect published files without reading or changing image pixels."""
    root=report.get('dossier')
    if not isinstance(root,str) or not Path(root).is_absolute():raise DeliveryError('Projet manquant')
    root=Path(root)
    if root.is_symlink() or not root.is_dir():raise DeliveryError('Dossier projet invalide')
    root=root.resolve(strict=True)
    imported=report.get('import_direct_cricut_v218')
    objects=report.get('objets')
    if not isinstance(imported,dict) or not isinstance(objects,list) or not 1<=len(objects)<=32:
        raise DeliveryError('Rapport Cricut incomplet')
    entries=[]
    records=imported.get('objets')
    if not isinstance(records,list) or len(records)!=len(objects):raise DeliveryError('Nombre objets incorrect')
    for i,(item,check) in enumerate(zip(objects,records),1):
        warning=list(item.get('avertissements') or [])
        failures=[]
        files={}
        for key,path in [('impression',check.get('fichier_import')),
                         ('png_fabrication',item.get('fichier_png_cricut') or item.get('png')),
                         ('svg_contour',item.get('fichier_svg_contour') or item.get('svg_contour'))]:
            if path:
                try:
                    f=_owned_file(root,path)
                    files[key]={'chemin':str(f.relative_to(root)), 'octets':f.stat().st_size,'sha256':_hash(f)}
                except (OSError,DeliveryError) as err:
                    failures.append('FICHIER_'+key.upper()+'_INEXPLOITABLE: '+str(err)[:90])
            else:failures.append('FICHIER_'+key.upper()+'_ABSENT')
        # A preflighted copy may have been replaced since the preflight ran.
        # Both hashes are computed from current bytes; a stale/different PNG
        # must never be reported as a complete local delivery.
        if ('impression' in files and 'png_fabrication' in files and
                files['impression']['sha256'] != files['png_fabrication']['sha256']):
            failures.append('PNG_IMPRESSION_DIFFERENT_DU_PNG_FABRICATION')
        if check.get('type_decoupe_presumee')=='CADRE_RECTANGULAIRE_SANS_DETOURAGE':
            failures.append('CARTE_RECTANGULAIRE_NON_STICKER')
        if check.get('statut')!='PRET_POUR_IMPORT_LOCAL':
            failures.append('PRECONTROLE_CRICUT_NON_ACCEPTE')
        entries.append({'index':i,'nom':f'Sticker {i:03d}',
                        'etat':'PRECONTROLE_LOCAL_A_VERIFIER' if not failures else 'REVISION_PRIORITAIRE',
                        'fichiers':files,'avertissements':warning+failures,
                        'certification_semantique':False,'decoupe_reelle_verifiee':False})
    sheets=[]
    requested_sheets=imported.get('planches')
    if requested_sheets is None:requested_sheets=[]
    if not isinstance(requested_sheets,list) or any(not isinstance(sheet,dict) for sheet in requested_sheets):
        raise DeliveryError('Collection de planches Cricut invalide')
    for i,check in enumerate(requested_sheets,1):
        entry={'index':i,'statut':check.get('statut'),'avertissement':check.get('raison')}
        if check.get('fichier_import'):
            try:
                page=_owned_file(root,check['fichier_import'])
                entry['fichier']={'chemin':str(page.relative_to(root)), 'octets':page.stat().st_size,'sha256':_hash(page)}
            except (DeliveryError,OSError) as err:
                entry['statut']='A_VERIFIER';entry['avertissement']=str(err)[:120]
        sheets.append(entry)
    # An upstream batch can be A_VERIFIER even when its individual PNGs passed
    # (e.g. failed README/report publication or a malformed sheet collection).
    # Do not promote that incomplete handoff to a complete delivery.
    upstream_ready=imported.get('statut') in (
        'PRET_POUR_IMPORT_LOCAL', 'PRET_POUR_IMPORT_LOCAL_AVEC_CADRES')
    complete=(upstream_ready
              and all(e['etat']=='PRECONTROLE_LOCAL_A_VERIFIER' for e in entries)
              and all(s['statut']=='PRET_POUR_IMPORT_LOCAL' and 'fichier' in s for s in sheets))
    return {'version':'21.12.2','sujets_fabriques':len(entries),
            'png_import_precontroles':sum(e['etat']=='PRECONTROLE_LOCAL_A_VERIFIER' for e in entries),
            'planches_precontrolees':sum(s['statut']=='PRET_POUR_IMPORT_LOCAL' and 'fichier' in s for s in sheets),
            'statut':'CONTROLE_LOCAL_COMPLET_A_REVISER' if complete else 'REVISIONS_NECESSAIRES',
            'certification_cricut':False,'validation_physique':False,
            'action':'Importer les PNG dans Design Space comme Flat Graphic, contrôler l’aperçu et la dimension avant de découper.',
            'objets':entries,'planches':sheets}


def write_delivery(root,manifest):
    folder=Path(root).resolve(strict=True)/'07_LIVRAISON_STICKERS_V21_12_2'
    if folder.is_symlink():raise DeliveryError('Dossier livraison symbolique refuse')
    folder.mkdir(exist_ok=True)
    if not folder.resolve().is_relative_to(Path(root).resolve()):raise DeliveryError('Destination non autorisee')
    final=folder/'MANIFESTE_STICKERS.json'
    if final.is_symlink() or final.exists():raise DeliveryError('Manifeste deja present, aucun ecrasement')
    tmp=folder/('.manifest_'+uuid4().hex+'.tmp')
    try:
        with tmp.open('x',encoding='utf8') as file:
            json.dump(manifest,file,indent=2,ensure_ascii=False,allow_nan=False)
            file.flush()
            os.fsync(file.fileno())
        # os.replace() overwrites a concurrently created manifest; link() does not.
        try:
            os.link(tmp,final)
        except FileExistsError:
            raise DeliveryError('Manifeste deja present, aucun ecrasement') from None
        except OSError as exc:
            # An exclusive-copy fallback exposes a partially written manifest
            # to other readers before fsync completes. That is not a safe
            # publish-last operation. No portable atomic no-clobber fallback
            # exists here when the filesystem rejects hard links: fail closed.
            raise DeliveryError('Publication atomique impossible sur ce systeme de fichiers') from exc
    finally:tmp.unlink(missing_ok=True)
    return str(final)
