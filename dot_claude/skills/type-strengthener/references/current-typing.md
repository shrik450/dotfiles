# Current Python typing research guide

Use this guide to find relevant feature families and semantic traps. It is not a compatibility matrix.

**Review date:** 2026-08-19

Python typing changes faster than a model's training data. Confirm every recent or uncertain feature against current sources and the project's installed versions. Do not infer support from this file's review date.

## Source order

Use these sources for different questions:

1. [Python typing specification](https://typing.python.org/en/latest/spec/) for current static semantics.
2. [Python `typing` documentation](https://docs.python.org/3/library/typing.html) for runtime availability in each Python release.
3. [`typing_extensions` documentation](https://typing-extensions.readthedocs.io/) for backports and version requirements.
4. The configured checker's documentation and release notes for implemented behavior and known limits.
5. The relevant PEP for motivation and design history.

A PEP is not always the maintained specification. A checker can also implement only part of an accepted feature.

## Build a project capability profile

Record these facts before you select a construct:

- The oldest Python parser that must read the source.
- The minimum and maximum supported Python versions.
- The configured checker target and exact checker version.
- The minimum supported `typing_extensions` version.
- Whether the project permits imports from `typing_extensions`.
- Whether a framework reads annotations at runtime.
- Whether annotations must survive serialization, schema generation, dependency injection, or validation.

For each proposed feature, answer these questions separately:

| Layer | Question |
|---|---|
| Grammar | Can the oldest supported parser read the syntax? |
| Runtime name | Does `typing` provide the object on every runtime? |
| Backport | Does the supported `typing_extensions` version provide equivalent behavior? |
| Checker | Does the configured checker implement the needed semantics? |
| Runtime consumer | Do frameworks that inspect annotations understand the form? |

A backport can provide a runtime object. It cannot backport new Python grammar.

## Research by required guarantee

Describe the guarantee first. Then inspect the relevant feature family.

### Preserve one type relationship

Investigate:

- Legacy `TypeVar` declarations.
- Native type parameter syntax.
- Bounds and constraints.
- Inferred and explicit variance.
- Type parameter defaults.
- `Self` for methods tied to the concrete class.
- Overloads for relationships selected by literal values.

Semantic traps:

- A bound preserves a subtype relationship. Constraints select from a fixed set. They are not interchangeable.
- Mutation often makes a generic type invariant.
- `Self` means the concrete class of the receiver. It is not a short spelling for every class-scoped type parameter.
- An overload set can hide an implementation that is too broad.
- Native syntax may fail on an older parser even when `typing_extensions` supplies related runtime objects.

Probe the inferred type at the consumer, not only whether the declaration parses.

### Preserve an arbitrary type sequence or tuple shape

Investigate:

- Variadic generics.
- Type-variable tuples.
- Unpacking in tuple and generic argument positions.
- Fixed and unbounded tuple forms.

Semantic traps:

- Tuple element type, tuple length, and an arbitrary sequence of type arguments are different guarantees.
- Checker support can vary for complex unpacking, aliases, and nested variadics.
- Replacing a precise tuple with `tuple[object, ...]` loses both position and length information.

Probe valid and invalid lengths, element positions, and unpacking sites.

### Preserve callable parameters

Investigate:

- `ParamSpec`.
- `Concatenate`.
- Callback protocols.
- Overloaded callback protocols.
- Decorator metadata such as `dataclass_transform` when a library generates typed methods.

Semantic traps:

- `Callable[..., T]` deliberately discards parameter checking.
- `ParamSpec` preserves a parameter list. A normal type parameter does not.
- A callback protocol can preserve parameter names and overloads that `Callable` cannot express.
- `dataclass_transform` describes generated behavior to a checker. It does not generate runtime behavior.

Probe positional, keyword, and keyword-only calls.

### Narrow after a runtime check

Investigate:

- Ordinary control-flow narrowing.
- Tagged unions and exhaustive matching.
- `TypeIs`.
- `TypeGuard`.
- `Never` and `assert_never`.

Semantic traps:

- Prefer ordinary checks when the checker can already understand them.
- `TypeIs` and `TypeGuard` have different subtype and branch-narrowing rules.
- A narrowing function is unsound when its runtime test does not prove its annotation.
- Mutable values can invalidate a narrowing result after the check.
- Exhaustiveness depends on a genuinely closed set.

Probe both branches of a predicate. Also probe mutation or aliasing when the narrowed object is mutable.

### Model mapping key state

Investigate:

- `TypedDict`.
- `Required` and `NotRequired`.
- `ReadOnly`.
- `Unpack[TypedDict]` for keyword arguments.
- Current `TypedDict` openness and extra-item controls.

Semantic traps:

- A missing key differs from a present key whose value is `None`.
- Class-level totality and per-key requiredness are separate choices.
- Read-only behavior can protect writes through a declared interface without making the runtime mapping immutable.
- Closed shapes are wrong for metadata that external systems can extend.
- Openness controls and backports are recent enough that checker support must be tested.

Probe construction, key access, updates, deletion, extra keys, and `**kwargs` calls as relevant.

### Mark declaration intent

Investigate:

- `override`.
- `final`.
- `ClassVar`.
- Explicit type aliases and native `type` statements.
- `dataclass_transform` for libraries that synthesize class behavior.

Semantic traps:

- `override` catches an accidental failure to override. It does not make an incompatible override valid.
- `final` can apply to names, methods, and classes with different effects.
- A type alias and a runtime value assignment are not the same declaration.
- Native alias and generic syntax can require a newer parser.
- Runtime consumers may observe aliases and annotations differently from the checker.

Probe misspelled method names, incompatible signatures, subclassing, assignment, and runtime introspection as relevant.

### Restrict strings and type expressions

Investigate:

- `Literal` and enums for project-controlled closed values.
- `LiteralString` for APIs that must reject dynamically constructed strings.
- Current type-expression annotation features, such as `TypeForm`, when an API accepts a type expression as data.

Semantic traps:

- `LiteralString` does not validate SQL, shell commands, HTML, or another language. It tracks how a string was formed.
- A literal union is unsafe for values that external systems can extend without an unknown-value policy.
- A class object, a type expression, and an instance have different meanings.
- Type-expression features are recent. Verify the specification, runtime or backport, and checker before use.

Probe literals, formatted values, concatenation, subclasses, unions, and invalid type forms as relevant.

### Control annotation runtime behavior

Investigate the annotation evaluation model for every supported Python version. Check deferred evaluation, forward references, and the current annotation introspection APIs.

Semantic traps:

- Static correctness does not guarantee that a framework can evaluate an annotation.
- Quoted annotations, future imports, aliases, and local names can produce different runtime results.
- Import-time side effects and circular imports can change when annotation evaluation changes.
- Do not recommend a newer annotation form without checking schema generators, validators, dependency injection tools, and other runtime consumers in the project.

Probe the actual consumer instead of relying only on `__annotations__`.

## Compare nearby constructs

Before choosing a design, state why nearby choices do not fit as well.

| Choice | Distinction to verify |
|---|---|
| `object` or `Any` | Safe unknown value versus disabled checking |
| Bound or constraints | Preserve any subtype versus select from listed types |
| Generic or overload | One relationship versus discrete call shapes |
| `Self` or type parameter | Receiver's concrete class versus another explicit relationship |
| `TypeIs` or `TypeGuard` | Subtype and two-branch narrowing rules versus different positive narrowing |
| `Protocol` or union | Required structural behavior versus a closed set of alternatives |
| `NewType` or value object | Static distinction only versus runtime validation and behavior |
| Optional key or optional value | Key may be absent versus value may be `None` |
| Read-only interface or immutable value | Restricted typed writes versus runtime immutability |
| Alias or subclass | Another name for a type versus a distinct runtime class |

## Required design probe

For a nontrivial recommendation, create a temporary file inside a temporary copy of the project. Use the project's configuration and imports.

The probe must contain:

1. A representative valid use that the checker accepts.
2. A plausible invalid use that the checker rejects.
3. `assert_type` or `reveal_type` when inference is part of the guarantee.
4. Both branches when narrowing is part of the guarantee.
5. A runtime check when annotations are inspected at runtime.

Run the exact project checker command. When the proposal changes grammar or runtime imports, also run the oldest supported Python parser or interpreter.

Record:

- Python version.
- Checker name and version.
- `typing_extensions` version, when used.
- Commands.
- Expected result.
- Observed result.
- Any checker differences or limitations.

A probe that does not fail at the intended misuse does not support the recommendation. Revise the design or remove it.

## Maintenance rule

Review this file when Python, `typing_extensions`, or a major checker releases a new typing feature. Keep feature names as research pointers. Do not add an unsupported compatibility claim without a source and an executed probe.
