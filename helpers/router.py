class Router:
    def __new__(cls, controller: str, method: str, params: list = None) -> None:
        try:
            controller_method = getattr(cls, controller)
            controller_method(method, params)
        except AttributeError:
            print("Class " + controller + " don't allowed")

    @staticmethod
    def call_method(instance, method: str, params: list = None) -> None:
        controller_name = instance.__class__.__name__
        try:
            call_method = getattr(instance, method)
            call_method(*params)
        except AttributeError:
            print("Method " + method + " don't allowed from controller " + controller_name)

    @staticmethod
    def CentersController(method: str, params: list = None) -> None:
        from controllers.centers import CentersController
        Router.call_method(CentersController(), method, params)

    @staticmethod
    def SectionsController(method: str, params: list = None) -> None:
        from controllers.sections import SectionsController
        Router.call_method(SectionsController(), method, params)

    @staticmethod
    def PostsController(method: str, params: list = None) -> None:
        from controllers.posts import PostsController
        Router.call_method(PostsController(), method, params)
