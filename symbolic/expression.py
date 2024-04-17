
from typing import MutableSet


# тривіальні приклади областей визначеності
def id_domain(x):
    return True


def nonzero(x):
    return x != 0


def domain_example(x):
    return x < 10


class Var:
    """Клас, що визначає змінну.

    Змінна характеризується лише її назвою. Відповідно існування двох різних
    змінних з однаковою назвою заборонене.

    Змінна може мати значення, а може бути невизначеною.

    Змінна може бути визначена на деякій обмеженій області. На даному етапі
    це визначається тільки за допомогою характеристичної функції.
    """

    __defined_vars = {}

    def __new__(cls, name, value=None, domain: callable=id_domain):
        """Реалізація шаблону 'одинак' -- в кожен момент часу може існувати тільки
        один об'єкт з заданою назвою.

        >>> x1 = Var('x')
        >>> x2 = Var('x')
        >>> x1 is x2   # тут х1 і х2 просто два посилання на один об'єкт
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
        """Забороняємо змінювати ім'я. Тільки читати."""
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
        """Для внутрішнього використання. Мусить повертати валідний пайтонівський
        код."""
        _domain = None if self._domain == id_domain else self._domain.__name__
        return f'Var("{self.name}", value={self.value}, domain={_domain})'

    def __str__(self):
        """Для юзера виводимо просто назву змінної."""
        return self.name

    # ================= для комфортного використання операції над змінними повинні повертати вираз ====================
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


# додаткові 'операції', які означають, що вираз був створений з коснтанти, змінної
# або просто деякої функції
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


# перевизначаємо дашок ^ на піднесення в степінь, бо ксор не матиме сенсу
BINARY_OPS = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y,
    '^': lambda x, y: x ** y,
}


ALL_OPERATIONS = AUXILIARY | set(UNARY_OPS.keys()) | set(BINARY_OPS.keys())


class Expression:
    """Клас, що визначає вираз.

    Вираз описується рекурсивно за наступними правилами:

    1. Змінна -- це вираз.
    2. Константа -- це вираз.
    3. Пайтонівська функція, яка приймає на вхід числові параметри -- це вираз.
    4. Сума / різниця / добуток / частка виразів -- це вираз.
    5. Композиція виразів -- це вираз.
    6. Інших виразів не існує.

    Відповідно, у реалізації вираз є деревом, де в кожній вершині є 'основна операція' і
    сини -- підвирази, від яких вираз залежить.
    """

    def __init__(self, variables: MutableSet[Var], operation: str, sons=None):
        """Внутрішній конструктор, який не має використовуватись користувачем.

        Parameters
        ----------
        variables : MutableSet[Var]
            множина змінних, від яких залежить вираз.
        operation : str
            основна операція, мусить бути з множини ALL_OPERATIONS
        sons : _type_, optional
            послідовність підвиразів. Можуть бути виразами, змінними, константами, функціями.
        """

        assert operation in ALL_OPERATIONS, f'invalid operation: {operation}'
        self._vars = variables
        self._operation = operation
        self._sons = sons

    @classmethod
    def from_universal(cls, value, variables=None):
        """Універсальний конструктор, який може використовувати юзер.

        Parameters
        ----------
        value : callable, Expression, float, Var
            з чого створити вираз. Можливі варіанти:

            Expression -- створити копію іншого виразу

            callable -- створити вираз з пайтонівської функції (або чогось, від чого можна викликати метод __call__)

            float, int, complex, etc.. -- створити вираз з константи

            Var -- створити вираз зі змінної

        variables : MutableSet[Var], optional
            опціональний параметр, для випадку <value: callable>. Описує змінні, від яких
            залежить пайтонівська функція

        Returns
        -------
        Expression
            відповідний вираз

        Raises
        ------
        TypeError
            якщо value має тип, який не було передбачено.
        """
        if isinstance(value, Expression):
            return value.copy()
        elif isinstance(value, (float, int, complex)):
            return cls.from_constant(value)
        elif isinstance(value, Var):
            return cls.from_variable(value)
        elif isinstance(value, callable) or hasattr(value, '__call__'):
            return cls.from_callable(value, variables)
        else:
            raise TypeError(f"Can't create expression from {type(value)}")

    # todo: ensure work for any numerical type, not only float
    @classmethod
    def from_constant(cls, const: float):
        """Створити вираз з константи.

        Відповідний вираз не буде залежати від жодних параметрів.

        Parameters
        ----------
        const : float   # fixme: any numerical
            числова константа, яка підтримує всі бінарні операції

        Returns
        -------
        Expression
        """
        return cls(set(), operation='CONST', sons=[const])

    @classmethod
    def from_variable(cls, var: Var):
        """Створити вираз зі змінної.

        Відповідний вираз буде залежати тільки від цієї змінної
        і повертати її значення, якщо воно визначене.

        Parameters
        ----------
        var : Var
            змінна

        Returns
        -------
        Expression
        """
        return cls({var, }, operation='VAR', sons=[var,])

    @classmethod
    def from_callable(cls, func: callable, variables: MutableSet[Var], derivative=None):
        """Створити змінну з довільного пайтонівського об'єкта, який
        можна викликати як функцію.

        Parameters
        ----------
        func : callable
            щось, що викликається і приймає на вхід змінні з variables
        variables : MutableSet[Var]
            _description_
        derivative : _type_, optional
            _description_, by default None

        Returns
        -------
        _type_
            _description_
        """
        # TODO: check whether amount of variables equals to args of func
        # TODO: store somehow proper sequence of variables OR use kwargs instead.
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
            elif self._operation == 'FUNC':
                sons_repr += '  ' * (indent + 1) + el.__name__
            else:
                sons_repr += '  ' * (indent + 1) + repr(el)
            sons_repr += ',\n'
        sons_repr += '  ' * indent + ']'
        exp_tabs = '  ' * indent
        tabs = '  ' * (indent + 1)
        return f'{exp_tabs}Expression(\n{tabs}variables={self._vars}, \n{tabs}operation="{self._operation}", \n{tabs}sons={sons_repr})'

    def copy(self):
        return self.__deepcopy__()

    def __deepcopy__(self):
        new_children = []
        for child in self._sons:
            if isinstance(child, Expression):
                new_children.append(child.copy())
            elif isinstance(child, (Var, float, int, callable, complex)):
                new_children.append(child)
            elif hasattr(child, 'copy'):
                new_children.append(child.copy())
            elif hasattr(child, '__deepcopy__'):
                new_children.append(child.__deepcopy__())
            else:
                raise ValueError("Unexpected child. Can't copy.")
        return Expression(self._vars.copy(), self._operation, new_children)

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
        """

        >>> e = Expression(...)
        >>> e.substitute(x=Expression(...))
        """
        res = self
        for var in kwargs:
            var = Var(var)
            if var not in self._vars:
                raise ValueError(f"Can't substitute variable {var} because expression dosen't depend on it.")
            res = res._substitude(var, kwargs[var.name])
        return res

    def _substitude(self, var: Var, value):
        # fixme: var == self._sons[0] -- redundant
        if self._operation == 'VAR' and var == self._sons[0]:
            return Expression.from_universal(value)

        new_children = []

        for child in self._sons:
            if isinstance(child, Expression) and var in child._vars:
                new_children.append(child._substitude(var, value))
            elif isinstance(child, Expression):
                new_children.append(child.copy())
            elif isinstance(child, (Var, float, int, callable, complex)):
                new_children.append(child)
            elif hasattr(child, 'copy'):
                new_children.append(child.copy())
            elif hasattr(child, '__deepcopy__'):
                new_children.append(child.__deepcopy__())
            else:
                raise ValueError("Unexpected child. Can't copy.")
        return Expression(self._vars.copy(), self._operation, new_children)

    # f'(x) ~ (f(x + dx) - f(x - dx)) / (2dx)
    # f''(x) ~ (f'(x + dx) - f'(x - dx)) / (2dx)
    # (f(g(x)))' = f'(g(x)) g'(x)
    # d / dx f(g(x, y), h(x, y)) = ...
    def derivative(self, ):
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



print("====================================== TEST 1 ================================================================")


x = Var('x', domain=domain_example)
y = Var('y')

exp = 2 * ((x + y) + 1) ^ y

# difference between __str__ and __repr__
print("String representation of expression:", exp)
print("\n\nRepr of expression:\n\n", repr(exp))

print('\n-----------------------------------------\n')
print(exp(x=1, y=2))
# print(exp(x=20, y=-1))


print("====================================== TEST 2 ================================================================")


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


print("====================================== TEST 3 ================================================================")


def sin(x, y):
    return x + y - 3

exp = Expression.from_callable(sin, {x, y})

print(exp)
print(repr(exp))



print("====================================== TEST 4 ================================================================")

import math

exp = Expression.from_callable(math.cos, {x})
print(exp)
print(repr(exp))


print("====================================== TEST 5 ================================================================")

x = Var('x', domain=domain_example)
y = Var('y')
z = Var('z')

exp = 2 * ((x + y) + 1) ^ y

exp2 = (z + 2) * z

print(exp.substitute(x=exp2))
print(exp.substitute(x=(x + 2)))

print(exp.substitute(x=exp2, y=exp))
print(exp.substitute(x=2))
print(exp.substitute(x=z))
