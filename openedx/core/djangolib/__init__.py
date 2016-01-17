'''
Ensures rules are followed regarding not using any forbidden dependencies.
'''
from openedx.tests.helpers import module_setup_teardown
# pylint: disable=invalid-name
setUpModule, tearDownModule = module_setup_teardown(forbidden_dependencies=['lms', 'cms', 'common'])
