"""Bounded read-only GitHub Actions job log transport.

Follow at most one HTTPS signed-storage redirect, without credentials.
The returned job text is not a verified checkout or step-bound test proof.
"""
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener
from .smartsvg_controller_observation import ROOT, NoRedirect, ObservationError
from .smartsvg_controller_proof import MAX_LOG

# GitHub Actions signed blob endpoints; reject arbitrary hosts and IP literals.
STORAGE_SUFFIXES = (".blob.core.windows.net", ".actions.githubusercontent.com",
                    ".blob.storage.azure.net")


def _storage_url(url):
    if not isinstance(url,str) or len(url)>16384 or any(ord(c)<33 for c in url):
        raise ObservationError("invalid log redirect")
    try:
        p=urlsplit(url)
        host=p.hostname or ""
        if (p.scheme!="https" or p.username is not None or p.password is not None
                or p.port not in (None,443) or p.fragment
                or not any(host.endswith(s) and len(host)>len(s) for s in STORAGE_SUFFIXES)):
            raise ObservationError("unapproved log storage")
    except ValueError as exc:
        raise ObservationError("invalid log redirect") from exc
    return url


def _read(response):
    with response:
        if response.getcode()!=200:
            raise ObservationError("unexpected log response")
        raw=response.read(MAX_LOG+1)
    if len(raw)>MAX_LOG:
        raise ObservationError("log exceeds bound")
    try:
        return raw.decode("utf-8",errors="strict")
    except UnicodeDecodeError as exc:
        raise ObservationError("log is not UTF-8") from exc


def github_job_log(job_id, token=None, *, opener=None):
    if type(job_id) is not int or job_id<1:
        raise ValueError("invalid job ID")
    opener=opener or build_opener(NoRedirect())
    headers={"Accept":"application/vnd.github+json","User-Agent":"SmartSVG-R15-shadow"}
    if token:
        headers["Authorization"]="Bearer "+token
    req=Request(ROOT+"/actions/jobs/"+str(job_id)+"/logs",headers=headers)
    try:
        response=opener.open(req,timeout=20)
    except HTTPError as exc:
        try:
            if exc.code!=302:
                raise ObservationError("job log request failed") from None
            redirect=_storage_url(exc.headers.get("Location"))
        finally:
            exc.close()
        # Never copy authorization, cookies, API headers or signed URLs to logs.
        try:
            response=opener.open(Request(redirect,headers={"User-Agent":"SmartSVG-R15-shadow"}),
                                 timeout=20)
        except HTTPError as exc:
            exc.close()
            raise ObservationError("log storage request failed") from None
    return _read(response)
