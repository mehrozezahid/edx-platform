"""
Provides test helpers to ensure forbidden dependencies aren't used within a
particular path.

Add the following to the tests/__init__.py for which you want to protect
against using certain dependencies that should be forbidden::
    from openedx.tests.helpers import module_setup_teardown
    # pylint: disable=invalid-name
    setUpModule, tearDownModule = module_setup_teardown(forbidden_dependencies=['lms', 'cms', 'common'])

This example might be used in a path that contains libraries used in lms and
cms, that shouldn't be dependent on either lms or cms.

"""
import sys


class ForbiddenDependencyModule(object):
    """
    Used as a temporary replacement for modules that are forbidden so that
    any forbidden import statements will raise an exception and fail tests.

    """
    def __init__(self, name):
        self.name = name

    def __getattr__(self, attr_name):
        msg = "You aren't allowed to import anything from %s!!" % self.name
        print msg
        raise Exception(msg)


def module_setup_teardown(forbidden_dependencies):
    """
    Creates setUpModule and tearDownModule methods to be used in an
    __init___.py in test directory that will replace forbidden
    dependencies so that they raise failures if they are used.

    Arguments:
        forbidden_dependencies: a list of dependencies that are forbidden.

    Returns:
        (setUpModule, tearDownModule): a tuple of methods to be used as
            the setUpModule and tearDownModule in an __init__.py in which
            you want to forbid certain imports.

    """
    def setUpModule():  # pylint: disable=invalid-name
        """
        A setUpModule method that can be used to replace forbidden modules
        with fake modules that will fail on import.
        """
        global original_modules  # pylint: disable=invalid-name, global-variable-undefined
        original_modules = {}
        for name in forbidden_dependencies:
            original_modules = {m: mod for m, mod in sys.modules.iteritems() if m.startswith(name + '.')}
            if name in sys.modules:
                original_modules[name] = sys.modules[name]

        for name in original_modules:
            sys.modules[name] = ForbiddenDependencyModule(name)

    def tearDownModule():  # pylint: disable=invalid-name
        """
        A tearDownModule method that can be used to restore forbidden modules.
        """
        for name, mod in original_modules.iteritems():
            sys.modules[name] = mod

    return setUpModule, tearDownModule
