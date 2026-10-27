"""User-visible README and feature-state document must match project reality.

Avoid making an obsolete private-repo protocol or a fictitious hardware
certification the landing page for a public SmartSVG contributor.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
README=ROOT/"README.md"
STATUS=ROOT/"docs/ETAT_ACTUEL_SMARTSVG.md"

class ProjectStatusPortalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme=README.read_text(encoding="utf-8")
        cls.status=STATUS.read_text(encoding="utf-8")

    def test_public_repo_has_link_to_current_status_and_immutable_plan(self):
        self.assertIn("Dépôt public",self.readme)
        self.assertNotIn("source privée",self.readme)
        self.assertNotIn("dans ce dépôt privé",self.readme)
        for target in ("docs/ETAT_ACTUEL_SMARTSVG.md",
                       "docs/ROADMAP_MASTER_v3_2.md",
                       "docs/G3_1_EXPRESS_REAL_SVG_REVIEW.md"):
            self.assertIn(target,self.readme)
            self.assertTrue((ROOT/target).is_file(),target)

    def test_stage_table_is_truthful_about_fictional_and_real_svg(self):
        for phrase in ("G3.0/G3.1","12 escargots","fictifs",
                       "n'effectue pas encore une segmentation IA",
                       "G2.7/G2.9","brouillon"):
            self.assertIn(phrase,self.readme)
        self.assertIn("aucune",self.readme.lower())
        self.assertIn("G3.2",self.status)
        self.assertIn("G3.3",self.status)
        self.assertIn("G3.4",self.status)

    def test_artifacts_are_not_mistaken_for_cricut_certification(self):
        for phrase in ("pas de version Cricut certifiée",
                       "RTX 3070", "Explore 5",
                       "651 empreintes", "V21.15.2"):
            self.assertIn(phrase,self.readme)
        self.assertIn("Certification Cricut",self.status)
        self.assertIn("Aucune",self.status)
        self.assertIn("Roadmap V3.2 et ZIP V21.15.2 intouchables",self.status)

if __name__=="__main__":
    unittest.main()
