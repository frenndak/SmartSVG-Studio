import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from tools.smartsvg_controller_metrics import Period, Cycle, Delivery, summarize, compare

UTC = timezone.utc
START = datetime(2026,11,1,tzinfo=UTC)
BASE = Period("smartsvg","frenndak/SmartSVG-Studio",START,START+timedelta(days=7),
              (("A",55),("B",25)),"R13")
CURRENT = replace(BASE,start=BASE.end,end=BASE.end+timedelta(days=7),phase="R15")


def digest(text):
    return sha256(text.encode()).hexdigest()


def cycle(period, hour, role="A", outcome="PRODUCTIVE", **kwargs):
    scheduled = period.start + timedelta(hours=hour,minutes=dict(period.cadence)[role])
    tag = str(scheduled)+role
    fields = dict(scheduled_for=scheduled,role=role,run_digest=digest("run"+tag),
                  outcome=outcome,receipt_digest=digest("receipt"+tag),
                  artifact_digest=digest("artifact"+tag) if outcome=="PRODUCTIVE" else "")
    fields.update(kwargs)
    return Cycle(**fields)


def full(period, productive_hours):
    return tuple(cycle(period,h,r,"PRODUCTIVE" if h<productive_hours else "NO_PROGRESS")
                 for h in range(168) for r,_ in period.cadence)


def delivery(period,n,*,product=True,lead=24,**kwargs):
    merged = period.start+timedelta(hours=n)
    fields = dict(number=n,opened=merged-timedelta(hours=lead),merged=merged,
                  head=digest("head"+str(n))[:40],merge=digest("merge"+str(n))[:40],
                  acceptance_digest=digest("accepted"+str(n)),product=product)
    fields.update(kwargs)
    return Delivery(**fields)


class MetricsTests(unittest.TestCase):
    def test_missing_and_unknown_do_not_become_productive_or_unproductive(self):
        rows=(cycle(BASE,0),cycle(BASE,1,outcome="NO_PROGRESS"),
              cycle(BASE,2,outcome="WAIT_ONLY"),
              cycle(BASE,3,outcome="EXTERNAL_BLOCKED"),
              cycle(BASE,4,outcome="UNKNOWN",receipt_digest=""))
        s=summarize(BASE,rows)
        self.assertEqual((s.expected,s.productive,s.no_progress,s.wait_only,
                          s.external_blocked,s.unknown,s.missing),(336,1,1,1,1,1,331))
        self.assertEqual(s.eligible,2)
        self.assertEqual(s.productive_rate,.5)
        self.assertEqual(s.coverage,4/336)

    def test_no_data_no_rate_no_comparison(self):
        result=compare(BASE,CURRENT)
        self.assertEqual(result.status,"INSUFFICIENT_DATA")
        self.assertIsNone(result.productive_rate_change_pp)
        self.assertIsNone(result.current.productive_rate)
        self.assertFalse(result.optimization_authorized)

    def test_exact_duplicates_idempotent_conflicting_slot_unknown(self):
        a=cycle(BASE,0)
        self.assertEqual(summarize(BASE,(a,a)).productive,1)
        b=replace(a,outcome="NO_PROGRESS",artifact_digest="")
        s=summarize(BASE,(a,b))
        self.assertEqual((s.productive,s.unknown,s.missing),(0,1,335))

    def test_duplicate_run_or_receipt_across_slots_quarantines_both(self):
        a,b=cycle(BASE,0),cycle(BASE,1)
        for c in (replace(b,run_digest=a.run_digest),replace(b,receipt_digest=a.receipt_digest)):
            s=summarize(BASE,(a,c))
            self.assertEqual((s.productive,s.unknown),(0,2))

    def test_duplicate_material_artifact_is_not_new_work(self):
        a,b=cycle(BASE,0),cycle(BASE,1)
        s=summarize(BASE,(a,replace(b,artifact_digest=a.artifact_digest)))
        self.assertEqual((s.productive,s.unknown,s.duplicate_artifacts),(1,1,1))
        p=compare(BASE,CURRENT,baseline_cycles=(a,),
                  current_cycles=(replace(cycle(CURRENT,0),artifact_digest=a.artifact_digest),))
        self.assertEqual((p.current.productive,p.current.duplicate_artifacts),(0,1))

    def test_invalid_receipt_or_unscheduled_cycle_not_counted(self):
        a=cycle(BASE,0)
        s=summarize(BASE,(replace(a,receipt_digest=""),replace(a,scheduled_for=BASE.start),
                          replace(a,artifact_digest="raw secret"),))
        self.assertEqual((s.productive,s.rejected,s.missing),(0,3,336))

    def test_matched_full_windows_descriptive_not_causal(self):
        a,b=full(BASE,84),full(CURRENT,126)
        result=compare(BASE,CURRENT,baseline_cycles=a,current_cycles=b)
        self.assertEqual(result.status,"DESCRIPTIVE_COMPARISON")
        self.assertEqual(result.productive_rate_change_pp,25)
        self.assertEqual(result.baseline.coverage,1)
        self.assertFalse(result.causal_gain_established)
        self.assertFalse(result.optimization_authorized)

    def test_sparse_coverage_prevents_optimistic_claim(self):
        result=compare(BASE,CURRENT,baseline_cycles=full(BASE,84),
                       current_cycles=full(CURRENT,168)[:25])
        self.assertEqual(result.status,"INSUFFICIENT_DATA")
        self.assertIn("CURRENT_COVERAGE_INSUFFICIENT",result.reasons)
        self.assertIsNone(result.productive_rate_change_pp)

    def test_short_or_incompatible_windows(self):
        short=replace(BASE,end=BASE.start+timedelta(days=1))
        current=replace(CURRENT,end=CURRENT.start+timedelta(days=1))
        self.assertIn("WINDOW_TOO_SHORT",compare(short,current).reasons)
        for p in (replace(CURRENT,project="other"),replace(CURRENT,cadence=(("A",55),)),
                  replace(CURRENT,end=CURRENT.end+timedelta(hours=1)),
                  replace(CURRENT,start=BASE.start,end=BASE.end)):
            with self.assertRaises(ValueError):
                compare(BASE,p)

    def test_product_deliveries_exclude_governance_and_compute_median(self):
        s=summarize(BASE,deliveries=(delivery(BASE,1,lead=10),delivery(BASE,2,lead=20),
                                    delivery(BASE,3,product=False,lead=100)))
        self.assertEqual((s.delivered,s.lead_time_hours_median),(2,15))

    def test_conflicting_delivery_or_reused_merge_not_counted(self):
        a,b=delivery(BASE,1),delivery(BASE,2)
        s=summarize(BASE,deliveries=(a,replace(a,product=False)))
        self.assertEqual((s.delivered,s.delivery_rejected),(0,2))
        s=summarize(BASE,deliveries=(a,replace(b,merge=a.merge)))
        self.assertEqual((s.delivered,s.delivery_rejected),(0,2))
        result=compare(BASE,CURRENT,baseline_deliveries=(a,),
                       current_deliveries=(delivery(CURRENT,1),))
        self.assertEqual((result.baseline.delivered,result.current.delivered),(1,0))

    def test_timezone_and_bounds_are_explicit(self):
        a=cycle(BASE,0)
        shifted=replace(a,scheduled_for=a.scheduled_for.astimezone(
                        timezone(timedelta(hours=1))))
        self.assertEqual(summarize(BASE,(a,shifted)).productive,1)
        with self.assertRaises(ValueError):
            summarize(replace(BASE,start=BASE.start.replace(tzinfo=None)))
        with self.assertRaises(ValueError):
            summarize(replace(BASE,cadence=(("A",True),)))

    def test_cross_window_run_and_receipt_replay_is_unknown(self):
        a,b=cycle(BASE,0),cycle(CURRENT,0)
        for c in (replace(b,run_digest=a.run_digest),replace(b,receipt_digest=a.receipt_digest)):
            result=compare(BASE,CURRENT,baseline_cycles=(a,),current_cycles=(c,))
            self.assertEqual(result.baseline.productive,1)
            self.assertEqual((result.current.productive,result.current.unknown),(0,1))

    def test_cross_window_reused_merge_or_acceptance_is_rejected(self):
        a,b=delivery(BASE,1),delivery(CURRENT,2)
        for d in (replace(b,merge=a.merge),replace(b,acceptance_digest=a.acceptance_digest)):
            result=compare(BASE,CURRENT,baseline_deliveries=(a,),current_deliveries=(d,))
            self.assertEqual((result.baseline.delivered,result.current.delivered,
                              result.current.delivery_rejected),(1,0,1))

    def test_previously_conflicting_delivery_identity_not_recycled(self):
        a=delivery(BASE,1)
        b=replace(delivery(BASE,2),merge=a.merge)
        c=replace(delivery(CURRENT,3),merge=a.merge)
        result=compare(BASE,CURRENT,baseline_deliveries=(a,b),current_deliveries=(c,))
        self.assertEqual((result.baseline.delivered,result.current.delivered),(0,0))
