# Places to inspect for weak types

This reference is not a definition of a finding or a coverage checklist. Form code-specific failure hypotheses before you read it. Then use it to choose more mutation targets and strengthening reviews.

Report proven erosion only when a plausible edit breaks a consumer without a checker error. Report a strengthening opportunity when you can describe an accepted error that a practical type design would reject. You do not need an established name for the error or its mechanism.

Search actively for mechanisms that this reference does not cover. Trace data flows, state changes, ownership boundaries, and type relationships. Describe a new mechanism in plain language when no known term fits it.

Do not rely on this reference for feature availability or semantics. Build the project capability profile in `SKILL.md`, then use [the current typing research guide](current-typing.md). Confirm recent or uncertain features with the typing specification, Python documentation, `typing_extensions` documentation, checker documentation, and an executed design probe.

## Terms

- **Type erosion:** Loss of a type checker's ability to detect a relevant error.
- **`Any` propagation:** An `Any` type spreads through inference beyond its intended boundary.
- **Unknown type:** Pyright's term for an implicit unknown type, such as a value from an untyped library or an unparameterized generic type.
- **Type laundering:** A value passes through `Any` or an unchecked cast and emerges with an unsupported type.
- **String-based typing:** Code represents an identifier as a runtime string, such as a `getattr` argument, mapping key, or status value.
- **Typed and untyped boundary:** The point where code validates external data and converts it to a trusted type.
- **Rename-opaque access:** A reference that a type checker cannot connect to a renamed declaration.
- **Invalid state:** A combination of values that the domain rejects but the model can represent.
- **Type relationship:** A rule that connects types, such as an input mode that determines a return type.

## Explicit type-checking bypasses

Inspect these patterns first, but report only a concrete effect:

- `Any` in public parameters, return types, `*args`, or `**kwargs`.
- `cast()` without an adjacent runtime check.
- Broad `# type: ignore` comments without an error code.
- Stale ignore comments that `--warn-unused-ignores` reports.
- Assertions that remove `None` without proving the domain rule.
- `Callable[..., Any]` where callers rely on a preserved signature.
- Repeated casts of one value in several consumers.

`object` is a safe unknown type. Do not treat it as equivalent to `Any`. Suggest a protocol only when required behavior exists and a protocol catches a named error.

## Implicit erosion

Search cannot find all of these cases:

- Bare generic types, such as `list`, `dict`, `Callable`, and `tuple`.
- Functions that return `Any` or an unknown type to many callers.
- Untyped decorators that erase the wrapped callable's signature.
- Classes that inherit from an untyped base class.
- Third-party libraries without stubs or a `py.typed` marker.
- Untyped deserialization from JSON, YAML, environment variables, or database drivers.
- Imports under `TYPE_CHECKING` whose runtime alternatives have different behavior.
- Generic functions that use `Any` instead of preserving an input type with `TypeVar`.

An untyped return usually has wider reach than an untyped input. Trace the value through callers before you set the priority.

## Dynamic access and dispatch

Inspect these mechanisms:

- `getattr`, `setattr`, `hasattr`, and `delattr` with literal or computed names.
- `getattr(obj, "field", None)`, which can hide a field deletion or rename.
- Custom `__getattr__` and `__setattr__` methods.
- `SimpleNamespace`, runtime class creation, monkey patching, and global-name dispatch.
- `**row`, `**config`, and similar expansion from an untyped mapping.
- `operator.attrgetter` and `operator.itemgetter` with string names.
- `functools.partial` when the resulting callable loses parameter details.
- Framework dispatch that uses route names, task names, signals, topics, or serializer field lists.

Dynamic access can be the correct design at a framework boundary. Check whether the dynamic value enters domain code before you report it.

## Weak domain models

Look for these strengthening opportunities:

- `dict[str, Any]` values whose consumers expect stable keys.
- Plain `str` or `int` values for distinct identifiers, units, currencies, or normalized values.
- Free-form strings for project-controlled states, modes, and kinds.
- Several optional fields that represent mutually exclusive workflow states.
- A status field combined with flags that permit contradictory states.
- Tuples that act as records and whose positions are easy to confuse.
- Same-typed positional parameters that callers can swap.
- Mutable models that can enter invalid intermediate states.
- Constructors that create incomplete objects for later setup.

For each case, name an invalid assignment, combination, or call that the proposed type rejects.

## Lost type relationships

Look for places where annotations describe possible types but lose a useful connection:

- A return type that depends on a literal mode argument.
- A function that returns the same type that it accepts.
- A container transform that must preserve its element type.
- A tuple operation that must preserve length or element positions.
- A decorator that must preserve a callable's parameters.
- A fluent method that must return the concrete subclass.
- A callback whose named parameters or overloads matter.
- A broad union that forces every caller to cast or narrow again.
- A generic interface whose bound, constraints, variance, or defaults do not match its mutation and substitution behavior.

Describe the relationship before choosing syntax. Research type parameters, overloads, `ParamSpec`, `Concatenate`, `Self`, callback protocols, and variadic generics as relevant. Compare bounds with constraints and generics with overloads. Verify native type parameter syntax, inferred variance, and type parameter defaults before recommending them.

## Modern declaration and mapping features

Inspect whether newer features can catch an error that older annotations leave open:

- `Required` and `NotRequired` for key presence that differs from value optionality.
- `ReadOnly` for writes that consumers must not make through a mapping interface.
- Current `TypedDict` openness controls when extra keys are the named risk.
- `override` for misspelled or accidentally detached overrides.
- `dataclass_transform` when a library generates constructors or other dataclass-like behavior.
- `LiteralString` when an API must distinguish literal-derived strings from arbitrary strings.
- Explicit aliases and native `type` statements when alias intent or generic alias relationships matter.
- Current type-expression features when an API accepts types as data.

Do not report a feature because it is new. Name the accepted mistake, compare nearby constructs, and run a positive and negative probe. Check grammar, runtime name, backport, checker, and runtime-consumer support separately.

## Open and closed sets

Inspect enums, literal unions, class hierarchies, and status strings.

For a project-controlled finite set, check whether dispatch is exhaustive. A catch-all branch can accept a new variant without requiring a consumer update. Use `assert_never` where the checker supports it.

Do not model an externally extensible set as closed unless the boundary includes an explicit unknown case.

## Boundary validation

Inspect values from these sources:

- `json.loads` and response `.json()` methods.
- YAML loaders and configuration files.
- Environment variables and command-line arguments.
- Database rows and raw queries.
- Plugin systems and runtime imports.
- Untyped third-party libraries.
- Pickle and other object deserializers.

Prefer one parser or validation model that returns a trusted domain type. Report repeated shape guesses when several consumers validate the same data independently.

A cast does not validate runtime data. Keep runtime validation when input can violate the annotation.

## Verification gaps

Identify the project's checker and normal command before you inspect local code. Look in project configuration, dependency files, task definitions, developer documentation, and continuous integration.

Check these gaps:

- The checker does not run in continuous integration.
- The checker runs but does not block a merge.
- Configuration excludes relevant paths.
- Diagnostic settings leave relevant function bodies, imports, decorators, or unknown types unchecked.
- A module-level suppression hides a file.
- The project accepts missing imports or unknown values without review.
- Generated code enters domain logic without a typed adapter.
- The checker configuration does not match the supported Python version.

Confirm a gap with configuration or a deliberate type error. Don't infer safety when the checker reports no errors.

## Checker configuration

Use the checker and command that the project already uses. Do not introduce a different checker as part of the audit.

For Pyright or basedpyright, inspect diagnostics that cover unknown values, missing type arguments, untyped decorators, untyped base classes, and unsupported casts. basedpyright also provides diagnostics for explicit and inferred `Any` types.

Do not infer feature support from a configured target Python version. The parser, runtime library, `typing_extensions`, checker, and runtime annotation consumers are separate support layers. Run a small probe for any recent or uncertain construct.

For ty or another checker, read its project configuration and command help. Identify the settings that govern unknown values, ignored code, imports, generic arguments, suppressions, and function bodies. Do not assume that settings or diagnostic names from another checker apply.

Ruff annotation rules can provide extra candidates when the project already uses Ruff. They do not replace the project's type checker or define the audit.

## Search commands

Use these commands to choose code for closer review. Every result needs a mutation, a traced counterexample, or a concrete strengthening case.

```bash
# Find reflection and mapping expansion.
rg -n --type py '\b(getattr|setattr|hasattr|delattr)\s*\('
rg -n --type py '\*\*\w+\s*\)'
rg -n --type py 'def __(get|set)attr__'

# Find explicit type-checking bypasses.
rg -n --type py '\bAny\b|\bcast\s*\(|type:\s*ignore(?!\[)'
rg -n --type py 'dict\[str,\s*Any\]|Callable\[\.\.\.'

# Find bare generic types in annotations.
rg -n --type py ':\s*(list|dict|set|tuple|Callable)\s*[,)=\]]'

# Find closed sets and check their dispatch.
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

## System design signals

Use these signals during the final review of all findings. One signal can justify a system design recommendation when the typing gain is material.

- Several consumers parse or validate the same external value.
- A transport or storage mapping crosses into domain logic.
- Each layer defines its own partial view of one data shape.
- Several callers repeat the same cast, narrowing check, or suppression.
- A general mapping or broad union passes through many interfaces unchanged.
- Domain objects contain many optional fields because they represent several lifecycle stages.
- Framework reflection or plugin values remain dynamic after they enter controlled code.
- Serialization field names appear throughout business logic.
- Decorators or adapters repeatedly erase and restore one callable signature.
- The same primitive value gains a different meaning in each layer.
- Local fixes require coordinated edits because no component clearly owns the type.

Trace a candidate from its source to its final consumers. Check whether one boundary can convert it to a trusted type for the rest of the flow.

Do not use repetition alone as proof of a design problem. Name the shared cause, the correct owner, and the added type guarantee.

## Type design options

| Current weakness | Type design to consider |
|---|---|
| Mapping with known keys | `TypedDict`, dataclass, or validation model |
| Attribute probing | `Protocol` with a justified `TypeGuard` or `TypeIs` |
| Distinct identifier roles | `NewType` or a validated value object |
| Project-controlled status strings | `Literal` or `Enum` |
| Nonexhaustive finite dispatch | `match` with `assert_never` |
| Untyped decorator | `ParamSpec` with `Concatenate` when needed |
| Callable with an erased signature | Callback protocol or `ParamSpec` |
| Return type selected by an input mode | `@overload` with literal parameters |
| Cast after reusable runtime validation | Ordinary narrowing, `TypeIs`, or `TypeGuard`, after comparing their semantics |
| Unvalidated external data | One parse function or validation model |
| Container that must preserve an element type | A type parameter with a verified bound, constraint, and variance design |
| Tuple operation that must preserve shape | Variadic generics or a fixed tuple form |
| Same-typed positional arguments | Keyword-only parameters, `NewType`, or value objects |
| Several mutually exclusive object states | Tagged union or separate state dataclasses |
| Fixed keyword argument shape | `Unpack[TypedDict]` |
| Keys with distinct presence rules | `Required` and `NotRequired` |
| Mapping writes that consumers must not make | `ReadOnly`, when interface-level protection is sufficient |
| Accidental failure to override | `override` |
| Library-generated dataclass behavior | `dataclass_transform` |
| Arbitrary string passed to a literal-derived API | `LiteralString`, when its construction model fits |
| Fluent return type | `Self` |
| Repeated parsing across layers | One boundary parser that returns a domain type |
| Transport shape in domain logic | Separate transport and domain models |
| Dynamic values beyond a framework boundary | Typed adapter at the boundary |
| One model for several lifecycle stages | State-specific models or a tagged union |
| Repeated local recovery of type relationships | A shared generic, overloaded, or protocol-based interface |

Choose the smallest local design that catches the named error. Then check whether a system design catches more errors or removes repeated recovery work. Include parser, runtime or backport, checker, runtime-consumer support, runtime validation, and migration cost. Run a valid and invalid design probe before reporting a nontrivial recommendation.
