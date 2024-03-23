
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
        return f'Var("{self.name}", value={self.value}, domain={self._domain})'

    def __str__(self): 
        return self.name

    def __add__(self, other): 
        pass 

    def __sub__(self, other): 
        pass 

    def __mul__(self, other): 
        pass 

    def __truediv__(self, other): 
        pass 

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
    'VAR'
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

    def __abs__(self): 
        return Expression(self._vars, operation='ABS', sons=[self])

    def __add__(self, other): 
        if not isinstance(other, Expression): 
            raise NotImplementedError()
        return Expression(self._vars | other._vars, operation='+', sons=[self, other])
        
    def __sub__(self, other): 
        if not isinstance(other, Expression): 
            raise NotImplementedError()
        return Expression(self._vars | other._vars, operation='-', sons=[self, other])
        
    def __mul__(self, other): 
        if not isinstance(other, Expression): 
            raise NotImplementedError()
        return Expression(self._vars | other._vars, operation='*', sons=[self, other])
    
    def __truediv__(self, other): 
        if not isinstance(other, Expression): 
            raise NotImplementedError()
        return Expression(self._vars | other._vars, operation='/', sons=[self, other])

    def __repr__(self): 
        return f'Expression(variables={self._vars}, operation="{self._operation}", sons={self._sons})'

    def __str__(self): 
        if self._operation in BINARY_OPS: 
            return f'({self._sons[0]} {self._operation} {self._sons[1]})'
        elif self._operation in UNARY_OPS: 
            return f'({self._operation}{self._sons[0]})'
        elif self._operation in ["VAR", "CONST"]: 
            return str(self._sons[0])
        else: 
            raise NotImplementedError()

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
        else: 
            raise NotImplementedError()


x = Var('x', domain=domain_example)
y = Var('y')

x = Expression.from_variable(x)
y = Expression.from_variable(y)
tmp1 = Expression.from_constant(1)
tmp2 = Expression.from_constant(2)

exp = tmp2 * ((x + y) + tmp1)

# difference between __str__ and __repr__
print("String representation of expression:", exp)
print("\n\nRepr of expression:\n\n", repr(exp))

print('\n-----------------------------------------\n')
print(exp(x=1, y=2))
print(exp(x=20, y=-1))
