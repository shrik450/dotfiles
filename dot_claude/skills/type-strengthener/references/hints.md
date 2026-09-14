# Inspection hints for weak types

Use this reference after you form failure hypotheses from the target code. It suggests more places to inspect, but it isn't a checklist or a definition of complete coverage.

Report a demonstrated checker gap only when a plausible edit breaks a consumer without a checker error. Report a type improvement only when a practical design rejects a concrete mistake that the current type accepts.

Search for mechanisms that this reference doesn't list. Trace data, state changes, ownership boundaries, and type relationships. Describe a new mechanism in plain language when no established term fits it.

Don't use this reference to decide whether a typing feature is available. First build the project capability profile from `SKILL.md`. Then use the [current typing research guide](current-typing.md) and primary sources. Test recent or uncertain features with the project's checker.

## Terms

- **Checker gap:** The checker doesn't detect a relevant error that stronger types could expose.
- **`Any` propagation:** An `Any` value spreads through inference beyond its intended boundary.
- **Unknown type:** Pyright's term for a type that the checker can't infer, such as a value from an untyped library or bare generic.
- **Type laundering:** A value passes through `Any` or an unchecked cast and receives a type that runtime evidence doesn't support.
- **String-based access:** Code names a program element with a runtime string, such as a `getattr` argument, mapping key, or status value.
- **Typed boundary:** Code validates untyped external data and converts it to a trusted type.
- **Rename-opaque access:** A checker can't connect a reference to the declaration that it names, so a declaration rename doesn't update or invalidate the reference.
- **Invalid state:** A value combination that the domain rejects but the model can represent.
- **Type relationship:** A rule that connects types, such as an input mode that determines a return type.

## Explicit checker bypasses

Inspect these patterns first, but report only a concrete effect:

- `Any` in public parameters, return types, `*args`, or `**kwargs`
- `cast()` without an adjacent runtime check
- Broad `# type: ignore` comments without an error code
- Stale ignores that `--warn-unused-ignores` reports
- Assertions that remove `None` without proving the domain rule
- `Callable[..., Any]` where callers need the original signature
- Repeated casts of the same value in several consumers

`object` represents a safe unknown value. Don't treat it as equivalent to `Any`. Recommend a protocol only when required behavior exists and the protocol rejects a named mistake.

## Implicit loss of type information

Search alone can't find every case. Inspect:

- Bare generic types, such as `list`, `dict`, `Callable`, and `tuple`
- Functions that return `Any` or an unknown type to many callers
- Untyped decorators that erase the wrapped function's signature
- Classes that inherit from an untyped base class
- Third-party libraries without stubs or a `py.typed` marker
- Untyped values from JSON, YAML, environment variables, or database drivers
- Imports under `TYPE_CHECKING` whose runtime alternatives behave differently
- Generic functions that use `Any` instead of preserving an input type with `TypeVar`

An untyped return value often affects more code than an untyped input. Trace it through callers before you set its priority.

## Dynamic access and dispatch

Inspect:

- `getattr`, `setattr`, `hasattr`, and `delattr` with literal or computed names
- `getattr(obj, "field", None)`, which can hide a deleted or renamed field
- Custom `__getattr__` and `__setattr__` methods
- `SimpleNamespace`, runtime class creation, monkey patching, and global-name dispatch
- `**row`, `**config`, and similar expansion from untyped mappings
- `operator.attrgetter` and `operator.itemgetter` with string names
- `functools.partial` when the result loses parameter details
- Framework dispatch through route names, task names, signals, topics, or serializer field lists

Dynamic access can be correct at a framework boundary. Report it only when the unchecked value creates a concrete risk or continues into controlled domain code.

## Weak domain models

Look for:

- `dict[str, Any]` values whose consumers expect stable keys
- Plain `str` or `int` values that represent different identifiers, units, currencies, or normalization states
- Free-form strings for project-controlled states, modes, and kinds
- Several optional fields that represent mutually exclusive workflow states
- Status fields and flags that allow conflicting states
- Tuples used as records when callers can confuse positions
- Same-typed positional parameters that callers can swap
- Mutable models that permit invalid intermediate states
- Constructors that create incomplete objects for later setup

For each case, name the invalid assignment, state, or call that the proposed type rejects.

## Lost type relationships

Look for annotations that list possible types but lose a relationship that callers need:

- A return type that depends on a literal mode argument
- A function that returns the same type that it accepts
- A collection operation that preserves its element type
- A tuple operation that preserves length or element positions
- A decorator that preserves callable parameters
- A fluent method that returns the concrete subclass
- A callback whose parameter names or overloads matter
- A broad union that makes each caller repeat the same cast or narrowing
- A generic interface with bounds, constraints, variance, or defaults that don't match its mutation and substitution behavior

Describe the relationship first. Then compare relevant options, such as type parameters, overloads, `ParamSpec`, `Concatenate`, `Self`, callback protocols, and variadic generics.

Don't treat bounds, constraints, generics, and overloads as interchangeable. Verify native type parameter syntax, inferred variance, and type parameter defaults before you recommend them.

## Modern declarations and mapping features

Check whether these features reject a mistake that older annotations permit:

- `Required` and `NotRequired` for key presence that differs from value optionality
- `ReadOnly` for writes that consumers must not make through a mapping interface
- Current `TypedDict` openness controls when unexpected keys are the risk
- `override` for misspelled or detached overrides
- `dataclass_transform` when a library generates dataclass-like constructors or fields
- `LiteralString` when an API must reject strings that aren't literal-derived
- Explicit aliases and native `type` statements when alias intent or generic relationships matter
- Current type-expression features when an API accepts types as data

Don't report a feature because it is recent. Name the accepted mistake, compare nearby options, and run a valid and invalid probe. Check syntax, runtime imports, backports, checker support, and runtime annotation consumers separately.

## Open and closed sets

Inspect enums, literal unions, class hierarchies, and status strings.

For a project-controlled finite set, check whether dispatch is exhaustive. A catch-all branch can accept a new variant without requiring a consumer update. Use `assert_never` when the checker supports it.

Don't model an externally extensible set as closed unless the boundary includes an explicit policy for unknown values.

## Boundary validation

Inspect values from:

- `json.loads` and response `.json()` methods
- YAML loaders and configuration files
- Environment variables and command-line arguments
- Database rows and raw queries
- Plugin systems and runtime imports
- Untyped third-party libraries
- Pickle and other deserializers

Prefer one parser or validation model that returns a trusted domain type. Report repeated shape guesses when several consumers validate the same data independently.

A cast doesn't validate runtime data. Keep runtime checks for inputs that can violate their annotations.

## Checker coverage gaps

Find the project's checker and normal command before you inspect local code. Read project configuration, dependencies, task definitions, developer documentation, and CI workflows.

Check whether:

- CI doesn't run the checker.
- CI runs the checker but doesn't block merges when it fails.
- Configuration excludes relevant paths.
- Diagnostics leave relevant function bodies, imports, decorators, or unknown values unchecked.
- A module-level suppression hides a file.
- The project accepts missing imports or unknown values without review.
- Generated code enters domain logic without a typed adapter.
- The configured Python target differs from the supported runtime versions.

Confirm uncertain coverage with a deliberate invalid assignment in a temporary copy. Don't treat a clean result as evidence when the checker didn't inspect the code.

## Checker configuration

Use the checker and command that the project already uses. Don't introduce another checker as part of the audit.

For Pyright or basedpyright, inspect diagnostics for unknown values, missing type arguments, untyped decorators, untyped base classes, and unsupported casts. basedpyright also reports explicit and inferred `Any` types.

For ty or another checker, read its configuration and command help. Find the settings for unknown values, ignored code, imports, generic arguments, suppressions, and function bodies. Don't apply diagnostic names from a different checker.

The configured Python target doesn't prove feature support. The parser, runtime, `typing_extensions`, checker, and runtime annotation consumers are separate. Test recent or uncertain constructs.

Ruff annotation rules can provide extra candidates when the project already uses Ruff. They don't replace a type checker or define audit coverage.

## Search commands

Use these searches to find code for closer review. Every result needs a mutation, a traced counterexample, or a concrete strengthening case.

```bash
# Find reflection and mapping expansion.
rg -n --type py '\b(getattr|setattr|hasattr|delattr)\s*\('
rg -n --type py '\*\*\w+\s*\)'
rg -n --type py 'def __(get|set)attr__'

# Find explicit checker bypasses.
rg -n --type py '\bAny\b|\bcast\s*\(|type:\s*ignore(?!\[)'
rg -n --type py 'dict\[str,\s*Any\]|Callable\[\.\.\.'

# Find bare generic types in annotations.
rg -n --type py ':\s*(list|dict|set|tuple|Callable)\s*[,)=\]]'

# Find closed sets and inspect their dispatch.
rg -n --type py 'class \w+\((str, )?(Enum|StrEnum|IntEnum)\)'
rg -n --type py -A3 'match .*:' | rg -n 'case _'
rg -c --type py 'assert_never'

# Find generic, alias, narrowing, mapping, and declaration features.
rg -n --type py '\b(TypeVar|TypeVarTuple|ParamSpec|Self|TypeIs|TypeGuard)\b|^type '
rg -n --type py '\b(TypedDict|Required|NotRequired|ReadOnly|Unpack)\b'
rg -n --type py '@(override|final)\b|\bdataclass_transform\b|\bLiteralString\b'

# Find checker configuration and task definitions.
rg -n -i 'pyright|basedpyright|\bty\b|type.?check|checker|strict|exclude|ignore' \
  pyproject.toml package.json justfile Makefile .github 2>/dev/null
rg -n --type py '^# type: ignore'
```

## Signals of a shared design problem

One signal can justify a system recommendation when the new design adds meaningful type protection:

- Several consumers parse or validate the same external value.
- A transport or storage mapping reaches domain logic.
- Each layer defines a different partial view of one data shape.
- Several callers repeat the same cast, narrowing check, or suppression.
- A general mapping or broad union crosses many interfaces unchanged.
- One domain object represents several lifecycle stages through optional fields.
- Framework reflection or plugin values remain dynamic after they enter controlled code.
- Serialization field names appear throughout domain logic.
- Decorators or adapters repeatedly erase and restore one callable signature.
- The same primitive type represents a different role in each layer.
- Local fixes require coordinated edits because no component owns the type.

Trace the value from its source to its final consumers. Identify the boundary that should convert it to a trusted type.

Repetition alone doesn't prove a design problem. Name the shared cause, the correct owner, and the errors that the proposed design catches.

## Type design options

| Current weakness | Options to compare |
|---|---|
| Mapping with known keys | `TypedDict`, dataclass, or validation model |
| Attribute probing | `Protocol` with a justified `TypeGuard` or `TypeIs` |
| Distinct identifier roles | `NewType` or a validated value object |
| Project-controlled strings | `Literal` or `Enum` |
| Nonexhaustive finite dispatch | `match` with `assert_never` |
| Untyped decorator | `ParamSpec`, with `Concatenate` when needed |
| Callable with an erased signature | Callback protocol or `ParamSpec` |
| Return type selected by an input mode | `@overload` with literal parameters |
| Cast after reusable validation | Ordinary narrowing, `TypeIs`, or `TypeGuard` |
| Unvalidated external data | One parser or validation model |
| Collection that preserves element type | A type parameter with verified bounds, constraints, and variance |
| Tuple operation that preserves shape | Variadic generics or a fixed tuple form |
| Same-typed positional arguments | Keyword-only parameters, `NewType`, or value objects |
| Mutually exclusive object states | Tagged union or separate state dataclasses |
| Fixed keyword argument shape | `Unpack[TypedDict]` |
| Keys with different presence rules | `Required` and `NotRequired` |
| Disallowed writes through a mapping interface | `ReadOnly` |
| Accidental failure to override | `override` |
| Library-generated dataclass behavior | `dataclass_transform` |
| Dynamic string passed to a literal-derived API | `LiteralString` |
| Fluent return type | `Self` |
| Repeated parsing across layers | One boundary parser that returns a domain type |
| Transport shape in domain logic | Separate transport and domain models |
| Dynamic values beyond a framework boundary | Typed adapter at the boundary |
| One model for several lifecycle stages | State-specific models or a tagged union |
| Repeated recovery of type relationships | A shared generic, overloaded, or protocol-based interface |

Choose the smallest local design that rejects the named mistake. Then check whether a shared design change rejects more errors or removes repeated recovery work.

For each recommendation, cover parser support, runtime imports or backports, checker support, runtime annotation consumers, remaining runtime validation, and migration cost. Run a valid and invalid design probe for every nontrivial recommendation.
