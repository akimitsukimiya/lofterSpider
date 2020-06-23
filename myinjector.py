import importlib
# NOTE:For many classes, only one instance should ever exit!

def providable(obj):
    isp =  hasattr(obj, '__isprovider__') \
            and getattr(obj, '__isprovider__')
    return isp

class Provider(object):
    __isprovider__ = True

    


class Singleton(Provider):
    
    #NOTE:there could be multiple providers.Singleton instances for one class    
    def __init__(self, c, *providers, **kwproviders):
        self.__cls__ = c
        self.__args = providers
        self.__kwargs = kwproviders
        self.__instance__ = None
    

    ##Principles for __init__ injection
    #1.All providers are only called once!!
    #2.Providers could be injected “as is” (delegated), if it is defined obviously. Check out Factory providers delegation.
    #3.All other injectable values are provided “as is”.
    #4.Positional context arguments will be appended after Factory positional injections.
    #5.Keyword context arguments have priority on Factory keyword injections and will be merged over them.
    def __call__(self, *args, **kwargs):
        if not self.__instance__:
            other_args = [i() if providable(i) else i\
                          for i in self.__args]
            #Principle 4
            args = other_args + list(args)
            for p in self.__kwargs:
                #Principle 5
                if p not in kwargs:
                    pval = self.__kwargs[p]
                    kwargs[p] = pval() if providable(pval) else pval 
            self.__instance__ = self.__cls__(*args, **kwargs)
        else:
            pass
            #self.__instance__.__init__(*args, **kwargs)
        return self.__instance__ 

    def reset(self):
        self.__instance__ = None





class Factory(Provider):
     

    provided_type = None

    def __init__(self, c, *providers, **other_injections):
        if self.provided_type:
            if not issubclass(c, self.provided_type):
                raise Exception('%s can be provided only!' % self.provided_type.__name__)
        self.__cls__ = c
        self.__args = providers
        self.__kwargs = kwproviders


    ##Creator of Factory provider
    ##Principles for __init__ injection
    #1.All providers (instances of Provider) are called every time when injection needs to be done.
    #2.Providers could be injected “as is” (delegated), if it is defined obviously. Check out Factory providers delegation.
    #3.All other injectable values are provided “as is”.
    #4.Positional context arguments will be appended after Factory positional injections.
    #5.Keyword context arguments have priority on Factory keyword injections and will be merged over them.
    def __call__(self, *args, **kwargs):

        #principle_1
        some_args = [i() for i in self.__args]
        #principle_4
        args = some_args + list(args)
        #principle_5
        for p in self.__kwargs:
            #principle_1
            if p not in kwargs:
                kwargs[p] = other_injections[p]()
        return self.__cls__(*args, **kwrags)


    def delegate(self, *args, **kwargs):

        def delegate_func(*a, **kwa):
            return self
        return delegate_func




class DelegatedFactory:

    
    def __init__(self, c, *providers, **other_injections):

        self.__cls__ = c
        self.__delegated_providers = providers
        self.__delegated_kwproviders = kwproviders


         
    def __call__(self, *args, **kwargs):

        some_args = [i for i in self.__args]
        args = some_args + list(args)
        for p in self.__kwargs:
            if p not in kwargs:
                kwargs[p] = other_injections[p]
        return self.__cls__(*args, **kwrags)


class Delegate(Provider):
    
    def __init__(self, a_provider):
        self.__a_provider__ = a_provider

    def __call__(self, *args, **kwargs):
        return self.__a_provider__ 


class AbstractFactory(Factory):
     
    def __init__(self, abc):
        #if self.provided_type:
        #    if not issubclass(c, self.provided_type):
        #        raise Exception('%s can be provided only!' % self.provided_type.__name__)
        self.__abc_class__ = abc
        self.__iscallable__ = False
        #self.__args = providers
        #self.__kwargs = kwproviders


    ##Creator of Factory provider
    ##Principles for __init__ injection
    #1.All providers (instances of Provider) are called every time when injection needs to be done.
    #2.Providers could be injected “as is” (delegated), if it is defined obviously. Check out Factory providers delegation.
    #3.All other injectable values are provided “as is”.
    #4.Positional context arguments will be appended after Factory positional injections.
    #5.Keyword context arguments have priority on Factory keyword injections and will be merged over them.
    def override(self, a_factory):
        c = a_factory.__base_class__
        if not issubclass(c, self.__abc_class__):
            raise Exception('%s can be provided only!' % self.__abc_class__.__name__)
        super().__init__(a_factory.__base_class__, *a_factory.__args, **a_factory.__kwargs)
        self.__iscallable__ = True

    def __call__(self, *args, **kwargs):
        if not self.__iscallable__:
            raise Exception("AbctractFactory should be overriden before being called!")
            return None
        super().__call__( *args, **kwargs)





class Callable(Provider):
    
    def __init__(self, func, *args, **kwargs):
        self.__function__ = func
        self.__args = list(args)
        self.__kwargs = kwargs

    def __call__(self, *args, **kwargs):
        #principle_4
        __args = [a() if providable(a) else a \
                 for a in self.__args]
        args = __args + list(args)
        #principle_5
        for p in self.__kwargs:
            #principle_1
            if p not in kwargs:
                kwargs[p] = self.__kwargs[p]
        return self.__function__(*args, **kwargs)


class ListArgsCallable(Provider):

    def __init__(self, func, largs):
        self.__function__ = func
        self.__largs = largs

    def __call__(self, *args):
        #principle_4
        args = self.__largs + list(args)
        return self.__function__(args)




class Object(Provider):

    def __init__(self, obj):
        self.__obj__ = obj


    def __call__(self):
        return self.__obj__


    

