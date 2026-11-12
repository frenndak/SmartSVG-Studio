"""Recovery Tk receipt guards: no false success or stuck button on worker failure."""
from concurrent.futures import Future
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_recovery_tk_v34 import NativeRecoveryPanel


class Button:
    def __init__(self):
        self.state = 'normal'
        self.hidden = False
        self.text = None

    def configure(self, **kwargs):
        self.state = kwargs.get('state', self.state)
        self.text = kwargs.get('text', self.text)

    def pack_forget(self):
        self.hidden = True

    def pack(self, **_kwargs):
        self.hidden = False


class Variable:
    def __init__(self):
        self.value = ''

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


def plan(outcome='restored_from_previous', project_id='example'):
    return SimpleNamespace(
        outcome=outcome, project_id=project_id, previous_sha256='a' * 64,
        pending_sha256='missing',
        apply=lambda **_kwargs: {'status': outcome, 'project_id': project_id},
    )


class NativeRecoveryUITests(unittest.TestCase):
    def setUp(self):
        # Exercise callbacks without a window; real Tk is covered separately.
        self.scheduled = []
        self.refreshed = []
        self.panel = NativeRecoveryPanel.__new__(NativeRecoveryPanel)
        self.panel.button = Button()
        self.panel.status = Variable()
        self.panel.root = SimpleNamespace(
            after=lambda _delay, callback: self.scheduled.append(callback))
        self.panel.messagebox = SimpleNamespace(
            askyesno=lambda *_args, **_kwargs: True)
        self.panel.refresh = lambda: self.refreshed.append(True)
        self.panel.can_apply = lambda: True
        self.panel.worker = SimpleNamespace(
            submit=lambda action, **kwargs: self.completed(action(**kwargs)))
        self.panel.plan = None
        self.panel.future = None
        self.panel.confirming = False
        self.panel._running_plan = None

    @staticmethod
    def completed(value):
        future = Future()
        future.set_result(value)
        return future

    def test_unknown_plan_cannot_show_recovery_action(self):
        self.panel.load(plan(outcome='unexpected_action'))
        self.assertIsNone(self.panel.plan)
        self.assertTrue(self.panel.button.hidden)
        self.assertIn('inconnu', self.panel.status.get())
        self.assertFalse(self.panel.busy)

    def test_worker_rejection_restores_button_and_does_not_schedule_polling(self):
        def reject(*_args, **_kwargs):
            raise RuntimeError('executor shut down')

        self.panel.worker = SimpleNamespace(submit=reject)
        self.panel.load(plan())
        self.panel.start()
        self.assertEqual(self.panel.button.state, 'normal')
        self.assertIn('indisponible', self.panel.status.get())
        self.assertIsNone(self.panel.future)
        self.assertIsNone(self.panel._running_plan)
        self.assertEqual(self.scheduled, [])
        self.assertEqual(self.refreshed, [])

    def test_valid_receipt_reports_success_and_reexamines_project(self):
        self.panel.load(plan())
        self.panel.start()
        self.assertEqual(len(self.scheduled), 1)
        self.scheduled.pop()()
        self.assertIn('restauré', self.panel.status.get())
        self.assertEqual(self.refreshed, [True])
        self.assertFalse(self.panel.busy)

    def test_unexpected_receipts_do_not_claim_success_and_still_refresh(self):
        for receipt in (
            None, [], {}, {'status': 'unrecognized', 'project_id': 'example'},
            {'status': 'pending_backup_finalized', 'project_id': 'example'},
            {'status': 'restored_from_previous', 'project_id': 'another'},
        ):
            with self.subTest(receipt=receipt):
                self.panel.load(plan())
                self.panel.future = self.completed(receipt)
                self.panel._running_plan = self.panel.plan
                before = len(self.refreshed)
                self.panel.receive()
                self.assertIn('non confirmée', self.panel.status.get())
                self.assertEqual(len(self.refreshed), before + 1)
                self.assertIsNone(self.panel._running_plan)
                self.assertFalse(self.panel.busy)


    def test_explicit_boolean_confirmation_required_for_writer(self):
        # Tk normally returns bool; a faulty adapter must not turn "yes",
        # 1, or an object into permission to alter a V1 project.
        for answer in (None, False, 1, "yes", [], object()):
            with self.subTest(answer=repr(answer)):
                submissions = []
                self.panel.worker = SimpleNamespace(
                    submit=lambda *args, **kwargs: submissions.append((args, kwargs)))
                self.panel.messagebox = SimpleNamespace(
                    askyesno=lambda *args, **kwargs: answer)
                self.panel.load(plan())
                self.panel.start()
                self.assertEqual(submissions, [])
                self.assertFalse(self.panel.busy)
                self.assertIsNone(self.panel._running_plan)
                self.assertIsNone(self.panel.future)

    def test_dialog_exception_never_submits_and_unblocks_confirming(self):
        submissions = []
        def unavailable(*args, **kwargs):
            raise RuntimeError("Tk dialog destroyed")
        self.panel.worker = SimpleNamespace(
            submit=lambda *args, **kwargs: submissions.append((args, kwargs)))
        self.panel.messagebox = SimpleNamespace(askyesno=unavailable)
        self.panel.load(plan())
        self.panel.start()
        self.assertEqual(submissions, [])
        self.assertFalse(self.panel.busy)
        self.assertIsNone(self.panel.future)
        self.assertIn("indisponible", self.panel.status.get())
        self.assertEqual(self.scheduled, [])
        self.assertEqual(self.refreshed, [])



    def test_context_switched_inside_dialog_never_starts_old_recovery(self):
        submissions = []
        old = plan(project_id='old-project')
        new = plan(project_id='new-project')
        def confirm_and_switch(*_args, **_kwargs):
            # askyesno runs a nested Tk event loop; F5 or project navigation
            # may invalidate the originally displayed recovery plan.
            self.panel.load(new)
            return True
        self.panel.worker = SimpleNamespace(
            submit=lambda *args, **kwargs: submissions.append((args, kwargs)))
        self.panel.messagebox = SimpleNamespace(askyesno=confirm_and_switch)
        self.panel.load(old)
        self.panel.start()
        self.assertIs(self.panel.plan, new)
        self.assertEqual(submissions, [])
        self.assertFalse(self.panel.busy)
        self.assertIn('Sélection modifiée', self.panel.status.get())

    def test_completed_old_recovery_never_claims_current_project_was_restored(self):
        old = plan(project_id='old-project')
        new = plan(project_id='new-project')
        self.panel.load(old)
        self.panel.start()
        self.assertEqual(len(self.scheduled), 1)
        self.panel.load(new)
        self.scheduled.pop()()
        self.assertIs(self.panel.plan, new)
        self.assertIn('non confirmée', self.panel.status.get())
        self.assertEqual(self.refreshed, [True])
        self.assertFalse(self.panel.busy)


if __name__ == '__main__':
    unittest.main()
