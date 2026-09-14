---
name: type-strengthener
description: Audits Python type safety and finds practical changes that let the project's type checker catch more errors. Uses targeted mutations to test whether types protect consumers after plausible edits. Reviews `Any`, casts, dynamic access, weak domain models, lost type relationships, boundary validation, checker coverage, and related system design. Use for Python type-safety reviews, typing improvements, refactor safety, and pull request reviews that focus on stronger types.
---

# Type strengthener

Audit Python code to find errors that stronger types could catch before runtime. Recommend changes, but don't edit the target code unless the user asks you to apply them.

Start by reading the target code. Don't read the [inspection hints](references/hints.md) until you understand the project's important data flows and domain rules. After you identify the supported Python and checker versions, read the [current typing research guide](references/current-typing.md).

Don't rely on memory for typing feature support. Check the current specification, runtime availability, backport availability, configured checker support, and runtime annotation consumers. If a recommendation depends on a typing feature, test a valid and invalid example with the project's checker.

## Goal

Increase the number of plausible programming errors that the project's type checker rejects.

Use these internal evidence categories:

- **Demonstrated checker gap:** A plausible code change breaks a consumer, but the configured checker doesn't report an error at that consumer.
- **Type improvement:** The current type accepts a specific mistake that a practical type design would reject.

Keep the categories separate while you audit. A demonstrated checker gap requires an executed mutation or a clear manual trace. A type improvement requires a concrete accepted mistake and a type design that rejects it.

Use the reader-facing evidence labels from [Report format](#report-format) in the final report. Don't require the reader to learn the audit's internal taxonomy.

## Key principles

### Test changes, not patterns

Start with the code's promises about data, states, and interfaces. Invent likely mistakes that violate those promises, and test whether the checker rejects them.

The mutation classes and inspection hints provide ideas. They don't define complete coverage. Python can lose type information through mechanisms that have no common name.

Describe an unfamiliar problem in plain language. Don't discard it because you can't name a known pattern or typing feature.

### Confirm what the checker covers

An annotation protects code only when the project checks that code and treats checker errors as failures. Excluded paths, ignored modules, weak diagnostics, and nonblocking continuous integration (CI) jobs create gaps.

Find the checker and exact command that the project uses. Read its configuration, dependency files, task definitions, developer documentation, and CI workflows. Use the existing checker instead of introducing another one.

When coverage is uncertain, add a deliberate invalid assignment to a temporary copy. Confirm that the normal checker command reports it.

### Validate external data at one boundary

External data commonly enters as JSON, environment variables, database rows, plugin values, or values from untyped libraries. Its lack of a trusted type isn't itself a defect.

Prefer one parser or validator that converts the external value into a trusted domain type. If several consumers guess or validate the same shape, report the missing shared boundary.

### Recommend types that prevent named errors

Don't recommend a type only because Python supports it. State the exact mistake that the type prevents. Prefer the smallest design that catches the mistake without making common changes harder.

Check whether a local fix addresses only one symptom of a wider design problem. Keep useful local fixes even when you also recommend a system-wide change.

### Recommend system changes when they add protection

A system change can cross modules, layers, or public interfaces. Recommend one when shared ownership or data flow causes weak types across the system.

State the migration cost directly. Don't reduce a useful recommendation to local edits only because the larger change costs more. Don't propose a broad rewrite without a shared cause, a clear owner, and additional errors that the new design would catch.

## Audit procedure

### 1. Define the scope

Identify the files, branch, pull request, or package under review. Exclude tests, fixtures, generated code, third-party stubs, and vendored code unless the user includes them.

Record:

- The minimum and maximum supported Python versions
- The checker name, exact version, configured Python target, and normal command
- The supported `typing_extensions` version and import policy
- Any framework or library that reads annotations at runtime

A recommendation must work across this support range.

### 2. Map checker coverage

Read the checker and CI configuration. Confirm:

- Which paths the checker includes and excludes
- Which strictness settings and module overrides apply
- How the checker handles imports, missing stubs, and `Any`
- How it handles untyped functions, decorators, and base classes
- Which file-level and module-level suppressions apply
- Whether CI runs the checker and blocks merges when it fails

Test uncertain coverage with a deliberate invalid assignment in a temporary copy. Report coverage gaps before code-level findings.

A clean result from an unchecked file or failed checker run isn't evidence of type safety.

### 3. Build the typing capability profile

Answer these questions before you choose typing features:

1. Can the oldest supported Python version parse the syntax?
2. Does `typing` or the supported `typing_extensions` version provide the runtime object?
3. Does the configured checker implement the required behavior?
4. Do frameworks and other runtime annotation consumers accept it?

Also check whether a build step lets the project use syntax that its oldest runtime can't parse directly.

For recent or uncertain features, use these sources in order:

1. The current [Python typing specification](https://typing.python.org/en/latest/spec/)
2. The documentation for each supported Python version
3. The [`typing_extensions` documentation](https://typing-extensions.readthedocs.io/)
4. The configured checker's documentation and release notes

Use a Python Enhancement Proposal (PEP) for design history, not as the only source for current behavior.

If you can't verify a support layer, use an older verified construct or mark the recommendation as unverified. Then read the [current typing research guide](references/current-typing.md).

### 4. Map the domain model

List the types and interfaces that carry domain meaning:

- Dataclasses, named tuples, `TypedDict` definitions, and validation models
- Enums, literal unions, tagged unions, and class hierarchies
- `NewType` definitions and value objects
- Protocols, generic types, and callable interfaces
- Public functions, constructors, adapters, parsers, and serializers

Trace important values as they enter the system, change shape, become trusted, and reach consumers. Write failure hypotheses based on the system's behavior before you consult the hint list.

Run discovery to find more mutation targets:

```bash
uv run <skill-path>/scripts/mutate.py discover --root <project-path>
```

Replace `<skill-path>` with this skill's directory. The script finds selected mutation targets only. Continue the audit when it finds none.

### 5. Test plausible edits

Start with important domain types and public functions. Test code-specific edits first, then use these examples to expand coverage:

| Edit | What to inspect |
|---|---|
| Rename a field, method, or parameter | Check whether consumers use a typed name or an unchecked string, mapping key, reflection call, or `**kwargs`. |
| Change a field or parameter type | Check whether consumers preserve the type or lose it through `Any`, a cast, or an untyped container. |
| Delete a field or method | Check whether defaults, mapping lookups, serializer lists, or dynamic calls hide the deletion. |
| Add a closed-set variant | Check whether exhaustive matching and `assert_never` require consumers to handle it. |
| Add a required mapping key | Check whether constructors and adapters know the complete `TypedDict` shape. |
| Change callable parameters | Check whether decorators, partial calls, `Callable[..., T]`, or untyped keyword mappings hide the signature. |
| Break a generic relationship | Check whether the declaration preserves the input-output relationship that consumers need. |
| Change a tuple shape | Check whether consumers retain tuple length and element-position information. |
| Change an override signature | Check whether the base interface and `override` reject the mismatch. |
| Change a narrowing predicate | Check both branches, including behavior after mutation or aliasing. |
| Split a primitive into distinct roles | Check whether the checker can distinguish values such as `UserId` and `OrderId`. |
| Move data across a boundary | Check whether a parser creates a trusted type before domain logic uses the data. |
| Swap same-typed arguments | Check whether keyword-only parameters, `NewType`, or a value object prevent the swap. |

Run focused mutations before broad runs:

```bash
uv run <skill-path>/scripts/mutate.py run --root <project-path> \
  --checker basedpyright --kind rename --target User.email
uv run <skill-path>/scripts/mutate.py run --root <project-path> \
  --checker-command "uv run ty check {target}" --json type-mutations.json
```

Use `--checker pyright` or `--checker basedpyright` to parse their JSON output. Use `--checker-command` for another project command. Run `uv run <skill-path>/scripts/mutate.py --help` for all options.

The script checks a temporary source copy. It reports new checker errors and possible consumer sites with no new error. It can match unrelated symbols that share a name, so verify every reported site before you use it as evidence.

Create manual mutations for important rules and data flows that the script doesn't cover. If no checker is available, trace consumers by hand and label the evidence as reasoned rather than executed.

Finish with an open-ended pass. Ignore the named patterns and reconstruct the system's promises. Try to violate each important promise while satisfying the annotations.

### 6. Find type improvements

Review important workflows from input to output. Look for a stronger type that can reject an invalid value or preserve a missing relationship.

#### Separate values with different meanings

Plain values can share a runtime type but represent different roles. Examples include identifiers, units, currencies, paths, and raw versus normalized text.

Choose among:

- `NewType` for a low-cost static distinction with no runtime behavior
- A frozen dataclass or validated value object when construction must enforce rules
- Keyword-only parameters when positional argument order is the main risk

Name the exact mix-up that the change prevents.

#### Make invalid states harder to represent

Look for models that permit combinations the domain rejects. Examples include many optional fields, a status plus conflicting flags, or one object that represents several workflow stages.

Consider:

- A tagged union with a `Literal` discriminator
- Separate dataclasses for separate states
- Constructors that require all fields for a valid state
- A private constructor and typed parser when construction needs runtime validation

Python types don't enforce runtime invariants. State which combinations the checker rejects and which values still need runtime validation.

#### Define controlled finite sets

Use `Literal` or `Enum` for project-controlled status, mode, and kind values. Use exhaustive `match` statements with `assert_never` when each consumer must handle every value.

Don't close a set that an external system can extend unless the boundary defines how to handle unknown values.

#### Preserve input-output relationships

Look for relationships that broad unions or erased generics lose. Examples include mode-dependent return types, element-preserving containers, fixed tuple shapes, and decorators that preserve signatures.

Describe the relationship before you select a construct. Then compare relevant options:

- Use a type parameter when an operation preserves a value's type. Compare `TypeVar` with native type parameter syntax when the project supports both.
- Use `@overload` when literal inputs select distinct return types.
- Use `ParamSpec` and `Concatenate` for decorators and callable adapters.
- Use variadic generics when tuple shape or a sequence of type arguments must stay related.
- Use `Self` when a method returns the receiver's concrete subclass.
- Use a callback protocol when parameter names or overloads matter.
- Consider type parameter defaults and inferred variance only after you verify support and behavior.

Prefer one clear generic relationship over many overlapping overloads. Treat bounds, constraints, variance, and defaults as separate choices.

#### Describe required behavior

Use `Protocol` when a function needs a small structural interface instead of a broad base class or attribute probing. Base the protocol on what consumers use. Don't copy the implementation's full interface.

Use `TypeIs` or `TypeGuard` only when the function performs the runtime check required by its annotation. Compare their subtype and branch-narrowing rules. Test both branches with the configured checker.

#### Give mappings a stable shape

Use `TypedDict` for mappings with known keys. Use `Unpack[TypedDict]` when a function accepts a fixed `**kwargs` shape.

Model a missing key separately from a present key whose value is `None`. Consider `Required`, `NotRequired`, `ReadOnly`, and current openness controls only when they prevent the named error. Verify checker and backport support.

Use a dataclass or validation model when data has behavior, construction rules, or a long lifetime. Keep truly extensible metadata open.

#### Mark declaration intent

Consider:

- `override` when a rename or signature change could detach a method from its base declaration
- `final` when subclassing or reassignment violates the design
- `dataclass_transform` when a project library generates dataclass-like fields or constructors
- An explicit type alias when the distinction from a runtime assignment affects checking or runtime use

These features describe intent. They don't create runtime behavior. Verify syntax, imports, generated signatures, checker behavior, and runtime introspection.

#### Restrict special strings and type expressions

Use `LiteralString` only when an API must reject strings that aren't literal-derived. It doesn't validate SQL, shell syntax, HTML, or another language.

When an API accepts a type expression as data, research current type-expression annotations instead of defaulting to `type[Any]` or `object`. These features are recent, so verify the specification, runtime or backport, and checker support.

#### Contain untyped boundaries

Trace JSON, YAML, environment variables, database values, plugin values, and untyped library results. Put runtime validation in one parser or validation model that returns a trusted domain type.

Use `object` or an unknown input type at the external edge when needed. Don't cast external data to a trusted type without checking it at runtime.

#### Match collection types to behavior

If a function only reads a collection, consider `Sequence`, `Mapping`, `Iterable`, or a small protocol. Return a concrete type when callers depend on its concrete behavior.

Use immutable domain objects when mutation permits invalid intermediate states. Don't recommend abstract collection types unless they catch a named error.

### 7. Validate each recommendation

Keep a recommendation only when you can answer every relevant question:

1. What plausible mistake does the current type accept?
2. Why does the checker accept it?
3. Which design rejects it?
4. Why does that design fit better than nearby choices?
5. Which code boundary owns the change?
6. Which runtime checks remain necessary?
7. What migration and compatibility costs does it add?
8. Can the oldest Python parse it, can every runtime import it, and does the checker support it?
9. Do runtime annotation consumers accept it?

For each nontrivial design, create a temporary probe that contains one valid use and one plausible misuse. Use `assert_type` or `reveal_type` when inference matters. Run the project's exact checker command. Also test the oldest runtime when syntax or imports change, and run any framework that reads the annotations.

Record versions, commands, and results. Mark an unrun or incomplete probe as `unverified`. Remove recommendations that add annotation detail without catching a named error.

### 8. Rank the findings

Keep urgency, evidence, and cost separate. Combining them in one severity label makes the result hard to act on.

Set **priority** from the expected value of the change. Consider:

- The harm that the accepted error can cause
- How likely the edit or value mix-up is
- How many consumers inherit the weak type
- How far the failure appears from the edit that caused it
- Whether the weakness reaches domain code or stays in an adapter
- Whether runtime validation already reduces the risk

Use these priority labels:

- **Fix first:** The change prevents a likely or harmful error and protects important code.
- **Fix next:** The change provides useful protection after the first group.
- **Consider:** The change has a smaller benefit, depends on planned work, or costs more than its immediate protection.

Don't create a finding with a “no action” priority. Put useful limits in the audit record and omit issues that don't justify a change.

Set **evidence** independently:

- **Demonstrated:** An executed mutation produced an unchecked break in real code.
- **Confirmed with a probe:** The checker accepted a concrete misuse of the current design and rejected it with the proposed design.
- **Reasoned:** A manual trace found the problem, but the audit couldn't run the checker.
- **Unverified:** The audit couldn't complete the evidence or compatibility checks required for the recommendation.

Set **effort** independently as `low`, `medium`, or `high`. Base it on affected interfaces, callers, runtime validation, and compatibility work.

Explain labels when the reason isn't clear from the finding.

### 9. Find shared design causes

After the local review, classify every item internally as `local`, `shared`, or `both`:

- **Local:** One declaration or implementation fully owns the problem.
- **Shared:** Data flow, ownership, or transformation across the system causes the weak type.
- **Both:** A local fix helps, but a shared design change provides stronger protection.

Don't add a classification table to the report. Present the preferred design and local fallback together so the reader doesn't have to connect separate sections.

Look for these shared causes:

1. Several consumers parse, validate, cast, narrow, or rebuild the same value.
2. A weak mapping crosses layers that each guess its shape.
3. Domain logic depends on transport, storage, framework, or serialization formats.
4. Several local fixes repeat the same type declaration or runtime check.
5. One object represents unrelated states or lifecycle stages.
6. Dynamic dispatch continues beyond the boundary that requires it.
7. Casts and suppressions repair relationships that a shared interface loses.
8. One earlier ownership boundary could make downstream values trusted by construction.

Trace each candidate from its source to its final consumers. Name the component that should own parsing, validation, transitions, or dispatch.

Possible shared design changes include:

- Parse external data once and pass a validated domain type downstream.
- Separate raw transport models from trusted domain models.
- Replace a cross-layer mapping with a type owned by one layer.
- Put state transitions in a tagged union or state-specific object model.
- Hide dynamic framework or plugin behavior behind a typed adapter.
- Preserve callable or generic relationships in a shared interface.
- Keep serialization and deserialization at one boundary.
- Split an object that combines unrelated responsibilities and therefore needs broad optional or union types.

A shared design recommendation must identify:

- The design choice that weakens the types
- The findings that the change addresses
- The component that should own the stronger type
- The proposed interface, responsibility, or data flow
- The errors that the checker can detect afterward
- The runtime validation that remains and where it runs
- A useful local fallback when the shared change isn't possible
- The affected interfaces, callers, and migration work
- The mutations or negative examples that must fail afterward

Present these details in the problem-focused finding. Don't repeat them in a separate design section.

Reject a shared recommendation that only moves code, adds a central dependency without clear ownership, or adds types without catching more errors.

## Don't report

Don't report these cases unless a specific catchable error remains:

- `Any` contained inside a validated boundary adapter
- A cast justified by an adjacent runtime check or schema validation
- Dynamic access that stays inside an intentional plugin, proxy, or framework boundary
- `object` used as a safe unknown type
- A type-checking bypass with a sound constraint that the project can't control
- An abstract collection type that adds no error detection
- A wrapper type that adds no useful domain distinction
- A closed union for externally extensible values
- A static type claim presented as runtime validation

## Report format

Write the report for a developer who needs to decide what to change. Lead with the decision, then show the accepted mistake, recommended design, cost, and supporting evidence.

Don't organize the report around internal categories. Organize it around the problems the developer can fix.

### 1. Start with the summary

State what the checker covers, the main coverage gaps, and the first change to make. Keep this introduction to three short paragraphs or fewer.

Then add a decision table:

```markdown
## Summary

The checker covers the reviewed package, but API responses lose their field
types before they reach domain code.

Parse API responses first. This change protects 14 consumers and removes six
unchecked casts.

| Priority | Problem | Risk | Recommended change | Effort |
|---|---|---|---|---|
| Fix first | API responses become `dict[str, Any]` | Invalid fields reach domain logic | Parse responses into `OrderResponse` | Medium |
| Fix next | Identifier types are both `str` | Callers can swap identifiers | Add distinct identifier types | Low |
```

Include each reportable problem once. Use direct problem names instead of audit terms.

### 2. Write one decision card for each important problem

Order cards by priority. Use numbered headings with descriptive names. Don't encode evidence categories in identifiers such as `E1`, `T1`, or `D1`.

Use this structure:

````markdown
## 1. Parse API responses before domain code

**Priority:** Fix first  
**Evidence:** Demonstrated  
**Effort:** Medium  
**Location:** `orders/client.py:84`

### What can go wrong

`fetch_order()` returns `dict[str, Any]`. A caller can misspell a field or pass
a value with the wrong type, and the checker reports no error.

```python
order = fetch_order(order_id)
send_receipt(order["totla"])
```

### Recommended change

Validate the response in `orders/client.py` and return `OrderResponse`. Keep raw
JSON inside the API adapter.

```python
@dataclass(frozen=True)
class OrderResponse:
    total: Decimal
    customer_id: CustomerId
```

This change lets the checker reject misspelled fields, missing fields, and
incorrect field values.

### Cost and limits

Update `fetch_order()` and its 14 callers. Keep runtime validation because the
API can return invalid data.

### Evidence and compatibility

- Mutation: Rename `total` to `amount`.
- Result: The checker reported no error in six consumers.
- Checker: basedpyright 1.29.2.
- Python: The design works with the supported Python 3.11-3.13 range.
- Command: `uv run basedpyright orders`.
````

Each card must answer these questions:

1. What can go wrong?
2. What accepted code demonstrates the problem?
3. What change prevents it?
4. Which errors become detectable?
5. What does the change cost?
6. Which runtime checks remain?
7. What evidence supports the recommendation?

Show the shortest realistic invalid example that the current checker accepts. Prefer this example over an abstract explanation of missing type information.

Name the protection gained. Don't write only “use `TypedDict`” or “add a protocol.” State which missing keys, invalid calls, mixed identifiers, or other mistakes the type rejects.

### 3. Keep preferred and local fixes together

When a shared design change provides more protection than a local fix, show both in the same card:

```markdown
### Options

**Preferred:** Parse the response once in the API adapter. This protects every
downstream consumer.

**Local fallback:** Return a `TypedDict` from `fetch_order()`. This catches field
mistakes but doesn't validate API data at runtime.
```

Explain why the preferred option catches more errors. Don't repeat the problem in a separate system design section.

### 4. Group smaller improvements

Write full cards for the three to five findings that most affect a decision. Put lower-value findings in a compact table when they don't need a detailed explanation:

```markdown
## Smaller improvements

| Location | Accepted mistake | Recommended change | Evidence | Effort |
|---|---|---|---|---|
| `cache.py:41` | Callers can swap two integer time units | Add distinct value types | Confirmed with a probe | Low |
| `hooks.py:19` | Decorated functions accept invalid keywords | Preserve parameters with `ParamSpec` | Demonstrated | Low |
```

Expand a smaller finding only when the type choice, compatibility, or runtime limit needs explanation.

### 5. End with a compact audit record

Put reproducibility and coverage details after the recommendations:

```markdown
## Audit record

- Checker: basedpyright 1.29.2
- Command: `uv run basedpyright src`
- Python support: 3.11-3.13
- Reviewed: API parsing, domain models, dispatch, decorators, and public functions
- Excluded: Generated clients and test fixtures
- Mutations: 12 run, eight caught, three exposed gaps, and one was inconclusive
- Unverified: Runtime annotation handling in Pydantic
```

Include the capability profile, checked workflows, boundaries, code-specific hypotheses, exclusions, and mutation totals. State that the hint list didn't define coverage.

List individual mutation commands only in the related card or when the reader needs them to reproduce the result. Don't repeat every mutation in a separate section.

Mention novel mechanisms only when they produced a finding. Mention suspicious patterns without findings only when they explain an important limit of the audit.

Omit empty sections. A small audit should produce a small report.

When the audit finds no practical changes, say so directly after the summary. Don't add empty decision tables or finding sections. Still include the compact audit record so the reader can see what the audit covered.

### Report language

Use these reader-facing terms:

| Internal concept | Report wording |
|---|---|
| Proven erosion | Demonstrated checker gap |
| Strengthening opportunity | Type improvement |
| Systemic cause | Shared design cause |
| Silent break | Unchecked break |
| Verification surface | Checker coverage |
| Reach | Affected code |
| Distance | Where the error appears |
| Boundary | Validation point |

Prefer plain wording in context instead of repeating these labels. For example, write “The checker reported no error in six callers” instead of “The finding has a reach of six.”

Keep type-design probes outside the runtime test suite unless the project already type-checks test fixtures. Delete temporary probes after the audit unless the user asks you to keep them.
