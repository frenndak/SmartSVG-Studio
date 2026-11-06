"""Bounded project browsing, including projects beyond the former 100 limit."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
import sys
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))
from smartsvg_core.project_workspace_g22 import ManagedWorkspace, WorkspaceError


class ProjectPaginationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.workspace = ManagedWorkspace(temporary.name)
        for index in range(105):
            (self.workspace.root / f'project{index:03d}.smartsvg').write_bytes(b'invalid synthetic archive')
        # Sidecars must not duplicate a project or conceal a recoverable one.
        (self.workspace.root / 'project000.previous.smartsvg').write_bytes(b'backup')
        (self.workspace.root / 'backup_only.previous.smartsvg').write_bytes(b'backup')

    def test_pages_cover_every_project_once_with_bounded_inspections(self):
        before = {p.name: p.read_bytes() for p in self.workspace.root.iterdir()}
        names = []
        offset = 0
        while True:
            with patch.object(self.workspace, 'inspect', wraps=self.workspace.inspect) as inspect:
                page = self.workspace.list_projects_page(offset=offset, limit=20)
            self.assertLessEqual(inspect.call_count, 20)
            self.assertEqual(page['pagination']['total'], 106)
            names.extend(project['name'] for project in page['projects'])
            if not page['pagination']['has_more']:
                self.assertIsNone(page['pagination']['next_offset'])
                break
            offset = page['pagination']['next_offset']
        self.assertEqual(names, sorted({'backup_only', *(f'project{i:03d}' for i in range(105))}))
        self.assertEqual({p.name: p.read_bytes() for p in self.workspace.root.iterdir()}, before)

    def test_legacy_list_stays_a_bounded_list_and_offsets_reach_later_projects(self):
        self.assertIsInstance(self.workspace.list_projects(), list)
        self.assertEqual(len(self.workspace.list_projects()), 100)
        tail = self.workspace.list_projects(offset=100)
        self.assertEqual(len(tail), 6)
        self.assertEqual(tail[-1]['name'], 'project104')

    def test_real_healthy_project_after_first_hundred_can_be_opened(self):
        spec = spec_from_file_location('pagination_png_fixture', ENGINE / 'tests' / 'test_project_workspace_g22.py')
        fixture = module_from_spec(spec)
        spec.loader.exec_module(fixture)
        raw = fixture.png()
        self.workspace.create('project105', raw, profile='Sticker - contour du sujet')
        page = self.workspace.list_projects_page(offset=100)
        last = page['projects'][-1]
        self.assertEqual(last['name'], 'project105')
        self.assertEqual(last['status'], 'PROJECT_HEALTHY')
        self.assertEqual(self.workspace.source_png(last['name']), raw)

    def test_invalid_page_bounds_fail_before_inspecting(self):
        for bounds in ({'offset': -1}, {'offset': True}, {'offset': 1.0},
                       {'limit': 0}, {'limit': 101}, {'limit': False}, {'limit': '20'}):
            with self.subTest(bounds=bounds), patch.object(self.workspace, 'inspect') as inspect:
                with self.assertRaisesRegex(WorkspaceError, 'INVALID_PROJECT_PAGE'):
                    self.workspace.list_projects_page(**bounds)
                inspect.assert_not_called()

    def test_empty_and_out_of_range_pages_have_explicit_metadata(self):
        for item in self.workspace.root.iterdir():
            item.unlink()
        for offset in (0, 100):
            page = self.workspace.list_projects_page(offset=offset)
            self.assertEqual(page['projects'], [])
            self.assertEqual(page['pagination']['total'], 0)
            self.assertFalse(page['pagination']['has_more'])


class ProjectPaginationRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_route_keeps_legacy_payload_and_validates_query_bounds(self):
        package = 'smartsvg_pagination_route_tests'
        pkg = ModuleType(package)
        pkg.__path__ = [str(ENGINE)]
        class Routes:
            def __init__(self): self.handlers = {}
            def get(self, path):
                def register(fn): self.handlers[path] = fn; return fn
                return register
            post = get
        web = SimpleNamespace(json_response=lambda payload, status=200, **kw:
                              SimpleNamespace(payload=payload, status=status))
        with patch.dict(sys.modules, {package: pkg, 'aiohttp': SimpleNamespace(web=web)}):
            spec = spec_from_file_location(package + '.project_routes_g22', ENGINE / 'project_routes_g22.py')
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            with tempfile.TemporaryDirectory() as temporary:
                routes = Routes()
                workspace = module.register_project_routes(routes, temporary)
                for index in range(101):
                    (workspace.root / f'p{index:03d}.smartsvg').write_bytes(b'synthetic invalid archive')
                handler = routes.handlers['/smartsvg/g22/projects']
                first = await handler(SimpleNamespace(query={}))
                self.assertTrue(first.payload['ok'])
                self.assertEqual(len(first.payload['projects']), 100)
                self.assertEqual(first.payload['pagination']['total'], 101)
                self.assertFalse(first.payload['certified'])
                last = await handler(SimpleNamespace(query={'offset': '100', 'limit': '20'}))
                self.assertEqual([p['name'] for p in last.payload['projects']], ['p100'])
                self.assertIsNone(last.payload['pagination']['next_offset'])
                for query in ({'offset': '-1'}, {'limit': '0'}, {'limit': '101'},
                              {'limit': '1.5'}, {'offset': 'x'}, {'offset': '9' * 5000}):
                    with self.subTest(query={k: v[:12] for k, v in query.items()}):
                        response = await handler(SimpleNamespace(query=query))
                        self.assertEqual(response.status, 400)
                        self.assertEqual(response.payload['error_code'], 'INVALID_PROJECT_PAGE')


if __name__ == '__main__':
    unittest.main()
