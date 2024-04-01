
from typing import MutableSet


def id_domain(x): 
    return True


def nonzero(x): 
    return x != 0


def domain_example(x): 
    return x < 10 


class Var: 

    __defined_vars = {}

    def __new__(cls, name, value=None, domain: callable=id_domain): 
        """Implementation of Singleton pattern--only one variable with unique name 
        should exist.
        
        >>> x1 = Var('x')
        >>> x2 = Var('x')
        >>> x1 is x2   # these are two links to the **same** object
        True 
        """
        if name not in cls.__defined_vars: 
            self = super().__new__(cls)
            self._name = name 
            assert value is None or domain(value), 'value is not from domain'
            self._value = value 
            self._domain = domain
            cls.__defined_vars[self._name] = self

        return cls.__defined_vars[name]

    @property
    def name(self): 
        """Changing name is prohibited."""
        return self._name

    @property
    def value(self): 
        return self._value

    def set_value(self, value): 
        assert self._domain(value), 'value is not from domain'
        self._value = value

    def has_value(self): 
        return self.value is not None
    
    def __repr__(self): 
        _domain = None if self._domain == id_domain else self._domain.__name__
        return f'Var("{self.name}", value={self.value}, domain={_domain})'

    def __str__(self): 
        return self.name

    def __add__(self, other): 
        return Expression.from_variable(self).__add__(other)

    def __sub__(self, other): 
        return Expression.from_variable(self).__sub__(other)

    def __mul__(self, other): 
        return Expression.from_variable(self).__mul__(other)

    def __truediv__(self, other): 
        return Expression.from_variable(self).__truediv__(other)

    def __hash__(self): 
        return hash(self._name)

    def __eq__(self, other):
         if not isinstance(other, Var): 
             return False 
         return self._name == other._name


# additional unary operations for expression that is constant 
# or variable only 
AUXILIARY = {
    'CONST', 
    'VAR', 
    'FUNC',
}


UNARY_OPS = {
    'NEG': lambda x: -x, 
    'ABS': abs,
    'INV': lambda x: x**{-1},
}


BINARY_OPS = {
    '+': lambda x, y: x + y, 
    '-': lambda x, y: x - y, 
    '*': lambda x, y: x * y, 
    '/': lambda x, y: x / y, 
    '^': lambda x, y: x ** y,
}


class Expression: 

    def __init__(self, variables: MutableSet[Var], operation: str, sons=None): 
        self._vars = variables
        self._operation = operation
        self._sons = sons 

    @classmethod
    def from_constant(cls, const: float): 
        """Create expression that is only constant value."""
        return cls(set(), operation='CONST', sons=[const])
    
    @classmethod
    def from_variable(cls, var: Var): 
        """Create expression that is only variable."""
        return cls({var, }, operation='VAR', sons=[var,])

    @classmethod
    def from_callable(cls, func: callable, variables: MutableSet[Var]): 
        # TODO: check whether amount of variables equals to args of func
        return cls(variables, operation='FUNC', sons=[func])

    @classmethod
    def _wrapper(cls, other): 
        if isinstance (other, Var): 
            other = cls.from_variable(other)
        elif isinstance(other, int) or isinstance(other, float) or isinstance(other, complex): 
            other = cls.from_constant(other)
        elif not isinstance(other, Expression): 
            raise NotImplementedError()
        return other 

    def __abs__(self): 
        return Expression(self._vars, operation='ABS', sons=[self])

    def __add__(self, other): 
        other = self._wrapper(other)
        return Expression(self._vars | other._vars, operation='+', sons=[self, other])
    
    def __sub__(self, other): 
        other = self._wrapper(other)
        return Expression(self._vars | other._vars, operation='-', sons=[self, other])
        
    def __mul__(self, other): 
        other = self._wrapper(other)
        return Expression(self._vars | other._vars, operation='*', sons=[self, other])
    
    def __truediv__(self, other): 
        other = self._wrapper(other)
        return Expression(self._vars | other._vars, operation='/', sons=[self, other])

    def __xor__(self, other):
        other = self._wrapper(other)
        return Expression(self._vars | other._vars, operation='^', sons=[self, other])

    def __radd__(self, other):
        other = self._wrapper(other) 
        return Expression(self._vars | other._vars, operation='+', sons=[other, self])

    def __rsub__(self, other):
        other = self._wrapper(other) 
        return Expression(self._vars | other._vars, operation='-', sons=[other, self])

    def __rmul__(self, other): 
        other = self._wrapper(other) 
        return Expression(self._vars | other._vars, operation='*', sons=[other, self])        
    
    def __rtruediv__(self, other):
        other = self._wrapper(other) 
        return Expression(self._vars | other._vars, operation='/', sons=[other, self])        

    def __rxor__(self, other):
        other = self._wrapper(other)
        return Expression(self._vars | other._vars, operation='^', sons=[other, self])
    
    def __pow__(self, other): 
        return self.__xor__(other)
    
    def __rpow__(self, other): 
        return self.__rxor__(other)

    def _repr(self, indent=1): 
        sons_repr = '[\n'
        for el in self._sons: 
            if isinstance(el, Expression): 
                sons_repr += el._repr(indent=indent+1)
            else: 
                sons_repr += '  ' * (indent + 1) + repr(el)
            sons_repr += ',\n'
        sons_repr += '  ' * indent + ']'
        exp_tabs = '  ' * indent 
        tabs = '  ' * (indent + 1)
        return f'{exp_tabs}Expression(\n{tabs}variables={self._vars}, \n{tabs}operation="{self._operation}", \n{tabs}sons={sons_repr})'

    def __repr__(self): 
        return self._repr(0)

    def __str__(self): 
        if self._operation in BINARY_OPS: 
            return f'({self._sons[0]} {self._operation} {self._sons[1]})'
        elif self._operation in UNARY_OPS: 
            return f'({self._operation}{self._sons[0]})'
        elif self._operation in ["VAR", "CONST"]: 
            return str(self._sons[0])
        elif self._operation == "FUNC": 
            args = ', '.join(str(el) for el in self._vars)
            return f'{self._sons[0].__name__}({args})'
        else: 
            raise NotImplementedError()

    # TODO: 
    def substitute(self, **kwargs): 
        pass 

    def __call__(self, **kwargs): 
        for var in self._vars:
            if var.name not in kwargs and not var.has_value(): 
                raise ValueError('All variables should be defined.')
            elif var.name in kwargs: 
                var.set_value(kwargs[var.name])
        
        if self._operation in BINARY_OPS: 
            return BINARY_OPS[self._operation](self._sons[0](), self._sons[1]())
        elif self._operation in UNARY_OPS: 
            return UNARY_OPS[self._operation](self._sons[0]())
        elif self._operation == 'CONST': 
            return self._sons[0]
        elif self._operation == 'VAR': 
            return self._sons[0].value
        elif self._operation == 'FUNC': 

            # FIXME: check whether we shoudn't use kwargs
            # TODO: finish implement
            return self._sons[0](*self._vars)
        else: 
            raise NotImplementedError()


x = Var('x', domain=domain_example)
y = Var('y')

exp = 2 * ((x + y) + 1) ^ y

# difference between __str__ and __repr__
print("String representation of expression:", exp)
print("\n\nRepr of expression:\n\n", repr(exp))

print('\n-----------------------------------------\n')
print(exp(x=1, y=2))
# print(exp(x=20, y=-1))


test = Expression(
  variables={Var("y", value=None, domain=None), Var("x", value=None, domain=domain_example)}, 
  operation="^", 
  sons=[
  Expression(
    variables={Var("y", value=None, domain=None), Var("x", value=None, domain=domain_example)}, 
    operation="*", 
    sons=[
    Expression(
      variables=set(), 
      operation="CONST", 
      sons=[
      2,
    ]),
    Expression(
      variables={Var("y", value=None, domain=None), Var("x", value=None, domain=domain_example)}, 
      operation="+", 
      sons=[
      Expression(
        variables={Var("y", value=None, domain=None), Var("x", value=None, domain=domain_example)}, 
        operation="+", 
        sons=[
        Expression(
          variables={Var("x", value=None, domain=domain_example)}, 
          operation="VAR", 
          sons=[
          Var("x", value=None, domain=domain_example),
        ]),
        Expression(
          variables={Var("y", value=None, domain=None)}, 
          operation="VAR", 
          sons=[
          Var("y", value=None, domain=None),
        ]),
      ]),
      Expression(
        variables=set(), 
        operation="CONST", 
        sons=[
        1,
      ]),
    ]),
  ]),
  Expression(
    variables={Var("y", value=None, domain=None)}, 
    operation="VAR", 
    sons=[
    Var("y", value=None, domain=None),
  ]),
])


print(test)
print(exp)


def sin(x, y): 
    return x + y - 3


exp = Expression.from_callable(sin, {x, y})

print(exp)
