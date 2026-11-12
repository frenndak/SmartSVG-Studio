"""Explicit, single-flight recovery of the project selected in the desktop."""
from concurrent.futures import ThreadPoolExecutor

from smartsvg_core.project_recovery import RecoveryError, recovery_message


ACTIONS = {
    'restored_from_previous': (
        'Restaurer le secours',
        'Restaurer le projet principal depuis la version précédente ?',
        'Projet restauré depuis la version précédente.'),
    'staged_primary_restored': (
        'Récupérer le projet',
        'Rétablir le projet principal depuis la copie de la sauvegarde interrompue ?',
        'Projet rétabli depuis la sauvegarde interrompue.'),
    'unpublished_candidate_discarded': (
        'Clore la sauvegarde interrompue',
        'Retirer la copie temporaire identique au projet principal ? Le secours précédent est conservé.',
        'Sauvegarde interrompue close. Projet principal et secours précédent conservés.'),
    'pending_backup_finalized': (
        'Finaliser la sauvegarde',
        'Conserver le projet principal et mettre à jour le secours avec la copie de la sauvegarde interrompue ?',
        'Sauvegarde finalisée. Projet principal conservé et secours mis à jour.'),
}


class NativeRecoveryPanel:
    def __init__(self, root, parent, tk, ttk, messagebox, refresh, can_apply):
        self.root, self.messagebox = root, messagebox
        self.refresh, self.can_apply = refresh, can_apply
        self.plan, self.future, self.confirming = None, None, False
        self._running_plan = None
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix='smartsvg-recovery')
        self.button = ttk.Button(parent, text='Récupérer le projet', command=self.start)
        self.status = tk.StringVar()
        self.label = ttk.Label(parent, textvariable=self.status, wraplength=620)
        self.label.pack(anchor='w')

    @property
    def busy(self):
        return self.confirming or self.future is not None

    def load(self, plan):
        if plan is not None and getattr(plan, 'outcome', None) not in ACTIONS:
            self.plan = None
            self.button.pack_forget()
            self.status.set('Plan de récupération inconnu. Réexaminez le projet (F5).')
            return
        self.plan = plan
        if plan is None:
            self.button.pack_forget()
        else:
            self.button.configure(text=ACTIONS[plan.outcome][0], state='normal')
            self.button.pack(anchor='w', pady=(4, 4))

    def start(self):
        plan = self.plan
        if plan is None or self.busy or not self.can_apply():
            return
        action, question, _ = ACTIONS[plan.outcome]
        source = (plan.previous_sha256 if plan.pending_sha256 == 'missing'
                  else plan.pending_sha256)
        self.confirming = True
        try:
            agreed = self.messagebox.askyesno(
                action, f'{question}\n\nProjet : {plan.project_id}\nCopie vérifiée : SHA {source[:12]}',
                parent=self.root, default='no')
        except Exception:
            # An unavailable or destroyed dialog never authorizes disk writes.
            self.status.set('Confirmation indisponible. Réexaminez le projet avant un nouvel essai.')
            return
        finally:
            self.confirming = False
        # Only an explicit boolean True can authorize the recovery writer.
        if agreed is not True:
            return
        self.button.configure(state='disabled')
        self.status.set('Récupération du projet en cours…')
        try:
            future = self.worker.submit(plan.apply, confirmed=True)
        except RuntimeError:
            self.button.configure(state='normal')
            self.status.set('Récupération indisponible. Réexaminez le projet avant un nouvel essai.')
            return
        self.future = future
        self._running_plan = plan
        self.root.after(50, self.receive)

    def receive(self):
        if not self.future.done():
            self.root.after(50, self.receive)
            return
        future, self.future = self.future, None
        running_plan, self._running_plan = self._running_plan, None
        try:
            result = future.result()
        except RecoveryError as error:
            detail = recovery_message(error.code)
            self.status.set(detail['message_fr'] + ' ' + detail['action_fr'])
        except Exception:
            self.status.set('Récupération non confirmée. Réexaminez le projet et ses copies de secours.')
        else:
            # A worker receipt is not proof of success unless its action and
            # project match the confirmed, revision-pinned recovery plan.
            if (type(result) is dict and running_plan is not None and
                    running_plan.outcome in ACTIONS and
                    result.get('status') == running_plan.outcome and
                    result.get('project_id') == running_plan.project_id):
                self.status.set(ACTIONS[running_plan.outcome][2])
            else:
                self.status.set('Récupération non confirmée. Réexaminez le projet et ses secours.')
        self.refresh()

    def shutdown(self):
        self.worker.shutdown(wait=True)
