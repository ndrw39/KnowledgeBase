class Router:
    def __new__(cls, controller: str, method: str, params: list = None):
        try:
            controller_method = getattr(cls, controller)
            return controller_method(method, params)
        except AttributeError:
            print("Class " + controller + " don't allowed")

    @staticmethod
    def call_method(instance, method: str, params: list = None):
        controller_name = instance.__class__.__name__
        try:
            call_method = getattr(instance, method)
            return call_method(*params)
        except AttributeError:
            print("Method " + method + " don't allowed from controller " + controller_name)

    @staticmethod
    def CentersController(method: str, params: list = None):
        from controllers.centers import CentersController
        return Router.call_method(CentersController(), method, params)

    @staticmethod
    def SectionsController(method: str, params: list = None):
        from controllers.sections import SectionsController
        return Router.call_method(SectionsController(), method, params)

    @staticmethod
    def PostsController(method: str, params: list = None):
        from controllers.posts import PostsController
        return Router.call_method(PostsController(), method, params)
