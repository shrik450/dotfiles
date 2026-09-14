# Research guide for current Python typing features

Use this guide to find relevant typing features and common semantic mistakes. It isn't a compatibility matrix.

Python typing changes often. Confirm recent or uncertain features against current sources and the project's installed versions. Don't infer support from this file.

## Use the right source

Use these sources in order:

1. The [Python typing specification](https://typing.python.org/en/latest/spec/) for current static semantics
2. The [Python `typing` documentation](https://docs.python.org/3/library/typing.html) for runtime availability in each Python release
3. The [`typing_extensions` documentation](https://typing-extensions.readthedocs.io/) for backports and version requirements
4. The configured checker's documentation and release notes for implemented behavior and known limits
5. The relevant Python Enhancement Proposal (PEP) for design history

A PEP isn't always the maintained specification. A checker can implement only part of an accepted feature.

## Build a project capability profile

Record:

- The oldest Python parser that must read the source
- The minimum and maximum supported Python versions
- The configured checker target and exact checker version
- The minimum supported `typing_extensions` version
- Whether the project permits imports from `typing_extensions`
- Whether a framework reads annotations at runtime
- Whether annotations pass through serialization, schema generation, dependency injection, or validation

Answer each support question separately:

| Layer | Question |
|---|---|
| Syntax | Can the oldest supported Python parser read the syntax? |
| Runtime object | Does `typing` provide the object on every supported runtime? |
| Backport | Does the supported `typing_extensions` version provide equivalent behavior? |
| Checker | Does the configured checker implement the required semantics? |
| Runtime consumer | Do frameworks and libraries that read annotations accept the form? |

A backport can provide a runtime object, but it can't add new syntax to an older Python parser.

## Research the required guarantee

Describe the guarantee before you choose a typing feature. Then inspect the matching feature family.

### Preserve one type relationship

Compare:

- Legacy `TypeVar` declarations
- Native type parameter syntax
- Bounds and constraints
- Inferred and explicit variance
- Type parameter defaults
- `Self` for methods tied to the receiver's concrete class
- Overloads for relationships selected by literal values

Check these common mistakes:

- A bound preserves any matching subtype. Constraints select from a fixed set. These behaviors aren't interchangeable.
- Mutation often makes a generic type invariant.
- `Self` means the receiver's concrete class. It doesn't replace every class-scoped type parameter.
- An overload set can hide an implementation whose types are too broad.
- Native syntax can fail on an older parser even when `typing_extensions` provides related runtime objects.

Probe the type that the consumer receives. Don't stop after confirming that the declaration parses.

### Preserve a type sequence or tuple shape

Compare:

- Variadic generics
- Type-variable tuples
- Unpacking in tuple and generic argument positions
- Fixed and unbounded tuple forms

Keep these guarantees separate:

- The type of each tuple element
- The tuple length
- An arbitrary sequence of type arguments

Checker support can differ for complex unpacking, aliases, and nested variadics. Replacing a precise tuple with `tuple[object, ...]` loses position and length information.

Probe valid and invalid lengths, element positions, and unpacking sites.

### Preserve callable parameters

Compare:

- `ParamSpec`
- `Concatenate`
- Callback protocols
- Overloaded callback protocols
- `dataclass_transform` when a library generates typed methods

Check these common mistakes:

- `Callable[..., T]` intentionally removes parameter checking.
- `ParamSpec` preserves a parameter list. A standard type parameter doesn't.
- A callback protocol can preserve parameter names and overloads that `Callable` can't express.
- `dataclass_transform` describes generated behavior to a checker. It doesn't generate runtime behavior.

Probe positional, keyword, and keyword-only calls.

### Narrow after a runtime check

Compare:

- Standard control-flow narrowing
- Tagged unions and exhaustive matching
- `TypeIs`
- `TypeGuard`
- `Never` and `assert_never`

Check these common mistakes:

- A custom narrowing function adds no value when the checker already understands the direct check.
- `TypeIs` and `TypeGuard` have different subtype and branch-narrowing rules.
- A narrowing function is unsound when its runtime test doesn't prove its annotation.
- Mutation can invalidate a narrowing result for an aliased mutable value.
- Exhaustive matching requires a genuinely closed set.

Probe both branches of a predicate. Also probe mutation and aliasing when the narrowed value is mutable.

### Model mapping key state

Compare:

- `TypedDict`
- `Required` and `NotRequired`
- `ReadOnly`
- `Unpack[TypedDict]` for keyword arguments
- Current `TypedDict` openness and extra-item controls

Check these common mistakes:

- A missing key differs from a present key whose value is `None`.
- Class-level totality and per-key requirements are separate choices.
- A read-only type can block writes through its declared interface without making the runtime mapping immutable.
- A closed shape doesn't fit metadata that external systems can extend.
- Openness controls and related backports can have uneven checker support.

Probe construction, key access, updates, deletion, extra keys, and `**kwargs` calls when they matter.

### Mark declaration intent

Compare:

- `override`
- `final`
- `ClassVar`
- Explicit type aliases and native `type` statements
- `dataclass_transform` for libraries that create dataclass-like behavior

Check these common mistakes:

- `override` catches a method that fails to override. It doesn't make an incompatible override valid.
- `final` has different effects on variables, methods, and classes.
- A type alias and a runtime value assignment are different declarations.
- Native alias and generic syntax can require a newer parser.
- Runtime consumers can observe aliases and annotations differently from the checker.

Probe misspelled methods, incompatible signatures, subclassing, assignment, and runtime inspection when they matter.

### Restrict strings and type expressions

Compare:

- `Literal` and enums for project-controlled finite values
- `LiteralString` for APIs that reject strings that aren't literal-derived
- Current type-expression annotations, such as `TypeForm`, for APIs that accept types as data

Check these common mistakes:

- `LiteralString` tracks how code forms a string. It doesn't validate SQL, shell commands, HTML, or another language.
- A literal union doesn't fit values that external systems can extend without an unknown-value policy.
- A class object, type expression, and instance have different meanings.
- Type-expression features are recent and need separate specification, runtime, backport, and checker checks.

Probe literals, formatted values, concatenation, subclasses, unions, and invalid type forms when they matter.

### Control runtime annotation behavior

Check the annotation evaluation model for every supported Python version. Include deferred evaluation, forward references, and current annotation inspection APIs.

Watch for these problems:

- Static correctness doesn't prove that a framework can evaluate an annotation.
- Quoted annotations, future imports, aliases, and local names can produce different runtime results.
- Annotation evaluation changes can affect import-time behavior and circular imports.
- Newer annotation forms can break schema generators, validators, dependency injection tools, or other runtime consumers.

Probe the real runtime consumer instead of inspecting only `__annotations__`.

## Compare nearby designs

Before you recommend a design, explain why similar choices don't fit as well.

| Choice | Distinction to verify |
|---|---|
| `object` or `Any` | Safe unknown value or disabled checking |
| Bound or constraints | Preserve any matching subtype or select from listed types |
| Generic or overload | Express one relationship or several discrete call shapes |
| `Self` or type parameter | Use the receiver's concrete class or another explicit relationship |
| `TypeIs` or `TypeGuard` | Use subtype and two-branch narrowing or different positive-branch narrowing |
| `Protocol` or union | Require structural behavior or define a closed set of alternatives |
| `NewType` or value object | Add a static distinction or runtime validation and behavior |
| Optional key or optional value | Allow an absent key or a present value of `None` |
| Read-only interface or immutable value | Restrict typed writes or enforce runtime immutability |
| Alias or subclass | Give a type another name or create a distinct runtime class |

## Run a design probe

For each nontrivial recommendation, create a temporary file inside a temporary project copy. Use the project's configuration and imports.

Include:

1. A representative valid use that the checker accepts.
2. A plausible invalid use that the checker rejects.
3. `assert_type` or `reveal_type` when inference matters.
4. Both branches when narrowing matters.
5. A runtime test when a library reads the annotations.

Run the project's exact checker command. If the proposal changes syntax or runtime imports, also run the oldest supported Python parser or interpreter.

Record:

- Python version
- Checker name and version
- `typing_extensions` version when used
- Commands
- Expected results
- Observed results
- Checker differences or limits

A probe doesn't support a recommendation unless it fails at the intended misuse. Revise or remove the design when the misuse passes.

## Keep this guide current

Review this file when Python, `typing_extensions`, or a major checker adds a typing feature. Keep feature names as research pointers. Don't add a compatibility claim without a source and an executed probe.
