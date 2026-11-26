import io
import unittest
from email.message import Message
from urllib.error import HTTPError

from tools.smartsvg_controller_log_transport import github_job_log
from tools.smartsvg_controller_observation import ObservationError
from tools.smartsvg_controller_proof import MAX_LOG


class Response(io.BytesIO):
    def getcode(self):
        return 200


class Opener:
    def __init__(self,items):
        self.items=list(items)
        self.requests=[]
    def open(self,req,timeout):
        self.requests.append(req)
        item=self.items.pop(0)
        if isinstance(item,Exception):
            raise item
        return item


def redirect(url,code=302):
    headers=Message()
    headers["Location"]=url
    return HTTPError("https://api.github.com/fixture",code,"fixture",headers,io.BytesIO())


class LogTransportTests(unittest.TestCase):
    def test_signed_redirect_no_token_forwarded(self):
        op=Opener([redirect("https://fixture.blob.core.windows.net/log?sig=fixture"),Response(b"test ok")])
        self.assertEqual(github_job_log(12,"fixture-token",opener=op),"test ok")
        self.assertEqual(op.requests[0].get_header("Authorization"),"Bearer fixture-token")
        self.assertIsNone(op.requests[1].get_header("Authorization"))
        self.assertIsNone(op.requests[1].get_header("Cookie"))

    def test_untrusted_redirect_rejected(self):
        for url in ("http://fixture.blob.core.windows.net/log",
                    "https://fixture.blob.core.windows.net.evil.test/log",
                    "https://127.0.0.1/log",
                    "https://user@fixture.blob.core.windows.net/log",
                    "https://fixture.blob.core.windows.net:444/log"):
            op=Opener([redirect(url)])
            with self.assertRaises(ObservationError):
                github_job_log(12,"fixture",opener=op)
            self.assertEqual(len(op.requests),1)

    def test_second_redirect_rejected(self):
        op=Opener([redirect("https://fixture.blob.core.windows.net/log"),
                   redirect("https://other.blob.core.windows.net/log")])
        with self.assertRaises(ObservationError):
            github_job_log(12,opener=op)
        self.assertEqual(len(op.requests),2)

    def test_direct_response_and_invalid_job(self):
        self.assertEqual(github_job_log(12,opener=Opener([Response(b"ok")])),"ok")
        with self.assertRaises(ValueError):
            github_job_log(True,opener=Opener([]))

    def test_log_size_and_invalid_encoding(self):
        for raw in (b"a"*(MAX_LOG+1),b"\xff"):
            with self.assertRaises(ObservationError):
                github_job_log(12,opener=Opener([Response(raw)]))

    def test_api_failure_not_redirect(self):
        op=Opener([redirect("https://fixture.blob.core.windows.net/log",403)])
        with self.assertRaises(ObservationError):
            github_job_log(12,opener=op)
        self.assertEqual(len(op.requests),1)
