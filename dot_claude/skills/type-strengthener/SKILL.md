---
name: type-strengthener
description: Audits Python type coverage and recommends local and system-wide ways to make more errors detectable by a type checker. Uses mutation testing to prove where types fail to protect future edits. Finds practical opportunities to model domain rules, preserve type relationships, validate boundaries, and make invalid states harder to express. Groups related findings to expose design causes, such as repeated parsing or weak data structures that flow through many layers. Use for Python type-safety reviews, typing improvements, `Any` usage, dynamic access, string-based dispatch, weak domain models, refactor safety, type checker coverage, and pull request reviews about stronger types.
---

# Type strengthener

Audit the code for type erosion, then find practical ways to make more errors detectable by types. Produce recommendations only. Do not edit the target code unless the user asks you to apply them.

Form an initial view of the code before you read the [type-strengthening hints](references/hints.md). After you map the project's supported Python and checker versions, read the [current typing research guide](references/current-typing.md). Use both references to choose more places to inspect. They do not define or limit the audit.

Do not rely on memory for the availability or semantics of a typing feature. Confirm the current typing specification, runtime availability, backport availability, and configured checker support. Run a minimal positive and negative example with the project's checker before you recommend a feature whose behavior is central to a finding.

## Goal

Maximize the share of plausible future errors that fail during type checking instead of at runtime.

Use two forms of evidence:

- **Proven erosion:** A plausible edit makes the code wrong, but the configured type checker reports no error at an affected consumer.
- **Strengthening opportunity:** The code permits a specific class of mistake that a practical type design would reject.

Keep these forms separate. Erosion requires a demonstrated silent break. A strengthening opportunity requires a concrete error that the proposed type would catch.

## Core principles

### Test the edit space

Do not audit by matching the code against the examples in this skill. Python offers many ways to lose a type guarantee, including mechanisms that have no established name.

Start from the code's data flows, invariants, state changes, and public interfaces. Invent plausible mistakes and future edits for that system. Then test whether the checker rejects them.

Use the listed edit classes and hints only to expand this investigation. They are examples, not a coverage standard. An audit is not complete because every listed pattern has been checked.

Describe a new problem in plain language when no known term fits it. Do not discard a problem because you cannot name its pattern or type construct immediately.

### Check the verification surface first

An annotation only protects code when the project's checker reads it and blocks the change. Excluded files, ignored modules, weak diagnostic settings, and nonblocking continuous integration checks can create verification gaps.

Identify the checker and command that the project actually uses. Inspect project configuration, dependency files, task definitions, developer documentation, and continuous integration. The checker might be Pyright, basedpyright, ty, or another tool. Do not introduce or recommend a different checker when the project already has one.

Confirm what the project checks before you interpret a lack of checker errors.

### Validate boundaries once

Untyped data must enter through boundaries such as JSON, environment variables, database rows, plugins, and untyped libraries. The boundary is not a defect.

Prefer one parse and validation point that returns a trusted domain type. When several consumers independently guess the same data shape, report the missing shared boundary.

### Strengthen types with purpose

Do not suggest a type only because Python supports it. Name the error that the type prevents. Prefer the smallest design that catches the error without making normal changes harder.

Start with a practical local fix. Then check whether the local fix treats a symptom of a system design problem.

### Consider system design

Recommend a system design change when it provides a material improvement over local typing fixes. The change can cross modules, layers, or public interfaces. Do not reduce the recommendation to local edits because a larger change is difficult.

Keep the local fixes in the report. The reader might not control the wider design or might need an immediate improvement. Present the local and system-wide options together, and explain the extra errors that the system design would catch.

Do not propose a broad rewrite only because several files need edits. A system design recommendation needs a shared cause, a clear ownership boundary, and a stronger type guarantee.

## Procedure

### 1. Define the scope

Identify the files, branch, pull request, or package to review. Exclude tests, fixtures, generated code, third-party stubs, and vendored code unless the user includes them.

Record the minimum and maximum supported Python versions. Record the checker name and exact version, its configured target Python version, and the `typing_extensions` version and support policy. Check whether frameworks or libraries inspect annotations at runtime. A recommendation must work across this support range.

### 2. Map the verification surface

Read the checker configuration and continuous integration configuration. Check these items:

- The checker and version.
- The paths that the checker includes and excludes.
- Strictness settings and module-specific overrides.
- Import handling, missing stub behavior, and `Any` reporting.
- Untyped function and decorator handling.
- Suppressions, including module-level and broad ignores.
- Whether continuous integration runs the checker and blocks merges on failure.

Verify that the checker reads each area that you test. Inject a clear type error in a temporary copy when checker behavior is uncertain.

Report verification gaps before local findings. Don't treat a lack of checker errors from an unchecked file or failed checker as proof of safety.

### 3. Build the typing capability profile

Build this profile before you select type constructs:

- The oldest Python parser that must accept the source.
- The `typing` features available at runtime on every supported Python version.
- The features that the project's supported `typing_extensions` version backports.
- The features and semantics implemented by the configured checker version.
- Frameworks, serializers, dependency injection tools, or other code that reads annotations at runtime.
- Whether the project can use newer syntax while supporting an older runtime through compilation or another build step.

For every recent or uncertain feature under consideration, check these sources in order:

1. The current [Python typing specification](https://typing.python.org/en/latest/spec/).
2. The documentation for each relevant Python version.
3. The [`typing_extensions` documentation](https://typing-extensions.readthedocs.io/).
4. The configured checker's documentation and release notes.

Use the typing specification for current static semantics. Use Python documentation for syntax and runtime availability. Use a PEP to understand design history, not as the sole source for current behavior.

Keep four support questions separate:

1. Can the oldest supported Python parse the syntax?
2. Does `typing` or the supported `typing_extensions` version provide the runtime name?
3. Does the configured checker implement the needed semantics?
4. Will runtime annotation consumers accept the form?

If you cannot verify one of these points, use a verified older construct or label the recommendation as unverified. Do not present an assumed feature matrix as fact.

Read [the current typing research guide](references/current-typing.md) after you complete this profile.

### 4. Map the domain model

List the types that carry domain meaning:

- Dataclasses, `TypedDict` definitions, validation models, and named tuples.
- Enums, literal unions, tagged unions, and class hierarchies.
- `NewType` definitions and value objects.
- Protocols, generic types, and callable interfaces.
- Public functions, constructors, adapters, and serialization boundaries.

Map the code without consulting the hint list first. Trace important values across boundaries and layers. Write down failure hypotheses based on the system's actual behavior.

Then run the discovery command as another source of mutation targets:

```bash
uv run scripts/mutate.py discover --root <path>
```

The script does not discover every dynamic connection or strengthening opportunity. Continue the audit when the script finds nothing.

### 5. Test plausible edits

Use the following edit classes as initial examples for important domain types and public functions. Add mutations based on the code's own behavior.

| Edit class | Question |
|---|---|
| Rename a field, method, or parameter | Which consumers use a checker-visible name? Which use a string, mapping key, reflection, or `**kwargs`? |
| Change a field or parameter type | Does each consumer retain the type, or does `Any`, an unchecked cast, or a bare container erase it? |
| Delete a field or method | Does a default value, mapping lookup, serializer list, or dynamic call hide the deletion? |
| Add a closed-set variant | Does dispatch use exhaustive matching and `assert_never`? Does a catch-all branch handle the new case without requiring an update? |
| Add a required mapping key | Do constructors and adapters know the full `TypedDict` shape? Do untyped mappings hide the new requirement? |
| Change call parameters | Do decorators, partial calls, `Callable[..., T]`, or untyped keyword mappings hide the signature? |
| Break a generic relationship | Do consumers depend on an input-output type relationship that the declaration preserves? |
| Change a tuple shape | Do consumers retain tuple length and element-position information? |
| Change an override signature | Does the base interface and `override` checking reject the mismatch? |
| Change a narrowing predicate | Do both branches narrow soundly, including after mutation or aliasing? |
| Split one primitive into distinct roles | Can the checker distinguish values such as `UserId` and `OrderId`, or are both plain strings? |
| Move data across a boundary | Does one parser create a trusted type, or does unvalidated data enter domain logic? |
| Reorder same-typed arguments | Would keyword-only parameters, a value object, or `NewType` prevent an accidental swap? |

Run targeted mutations before broad runs when the scope is large. Use the checker or checker command that the project already uses:

```bash
uv run scripts/mutate.py run --root <path> --checker basedpyright \
  --kind rename --target User.email
uv run scripts/mutate.py run --root <path> \
  --checker-command "uv run ty check {target}" --json type-mutations.json
```

Use `--checker pyright` or `--checker basedpyright` for their JSON output. Use `--checker-command` for another project command. Read `uv run scripts/mutate.py --help` for limits and checker arguments.

The script copies the source tree to a temporary directory. It reports new checker errors and candidate consumer sites that received no error. Its discovery includes selected parameter, literal-alias, `TypedDict`, generic-return, and tuple-shape mutations. Keep the script secondary to code-specific hypotheses and manual probes.

Review every unflagged site. The script collects candidates and can match an unrelated symbol with the same name. Report a site only after you confirm that it consumes the mutated symbol.

Create additional mutations from the code's invariants and data flows. Do not limit mutations to the script's supported edit classes.

If no checker is available, trace consumers by hand. Mark the evidence as reasoned, not executed. Do not report a clean result from a failed checker run.

Before you continue, do a separate open-ended pass. Set aside the named patterns and edit classes. Reconstruct what the system promises about its data, states, and interfaces. Try to invent errors that violate those promises while satisfying the written annotations. Investigate any error that the checker accepts, even when you cannot name the mechanism.

Do not conclude that the code is strong because searches, hints, and scripted mutations found nothing. Base the conclusion on the important data flows and invariants that you tested.

### 6. Find type-strengthening opportunities

Review important workflows from input to output. Ask where a stronger type can reject an invalid value or preserve an unexpressed relationship.

#### Model domain distinctions

Look for values with the same runtime type but different meanings. Examples include identifiers, units, currencies, paths, and normalized versus raw text.

Consider these options:

- Use `NewType` for a low-cost distinction with no runtime behavior.
- Use a frozen dataclass or validated value object when construction must enforce rules.
- Use keyword-only parameters when the main risk is positional argument order.

Name the exact mix-up that the change catches.

#### Make invalid states harder to express

Look for models that allow combinations the domain rejects. Common cases include many optional fields, a status plus unrelated flags, or one object that represents several workflow stages.

Consider these options:

- Use a tagged union with a `Literal` discriminator.
- Use separate dataclasses for separate states.
- Require valid fields in constructors instead of setting them later.
- Use a private constructor and a typed parse function when validation is required.

Do not claim that Python types enforce runtime invariants. State which invalid combinations the checker rejects and which still need runtime validation.

#### Close finite sets

Replace free-form status, mode, and kind strings with `Literal` or `Enum` when the set is controlled by the project. Pair closed sets with exhaustive `match` statements and `assert_never`.

Do not close a set that external systems can extend without a clear unknown-value policy.

#### Preserve relationships between inputs and outputs

Look for unions that lose useful relationships. Examples include a function whose return type depends on a mode, a container that preserves its element type, a tuple that preserves its shape, or a decorator that preserves a callable signature.

First describe the relationship without naming a type construct. Then compare the current feature families that can express it:

- Use a type parameter for a value that keeps the same type through an operation. Compare legacy `TypeVar` declarations with native type parameter syntax when the project can parse it.
- Use `@overload` when literal inputs select distinct return types and one generic relationship cannot express the contract.
- Use `ParamSpec` and `Concatenate` for decorators and callable adapters.
- Consider variadic generics when tuple length, tuple shape, or an arbitrary sequence of type arguments must remain related.
- Use `Self` for fluent methods and alternate constructors when its subclass behavior matches the contract.
- Use a callback protocol when named parameters or overloads matter.
- Consider type parameter defaults and inferred variance only after you verify their semantics and support.

Prefer one clear generic relationship over many overlapping overloads. Check bounds, constraints, variance, and defaults separately. Do not treat them as interchangeable.

#### Describe required behavior

Look for functions that accept `object`, a broad base class, or unrelated concrete classes and then probe for attributes.

Use `Protocol` when callers need a small structural interface. Keep protocols small and based on actual consumers. Do not copy a full implementation interface.

Use `TypeIs` or `TypeGuard` only when a function performs the runtime check that justifies narrowing. Do not treat them as interchangeable. Verify the subtype requirement and two-branch narrowing of `TypeIs`. Use the different positive-branch behavior of `TypeGuard` only when the contract needs it. Probe both the true and false branches with the configured checker.

#### Give mappings a stable shape

Use `TypedDict` for mappings with known keys, including partial mappings and typed keyword arguments. Consider `Unpack[TypedDict]` when a function accepts a fixed `**kwargs` shape.

Model key absence separately from a present key whose value can be `None`. Investigate `Required`, `NotRequired`, `ReadOnly`, and current openness controls when they catch the named error. Verify checker and backport support for each qualifier. State whether a read-only guarantee applies only through the declared interface.

Use a dataclass or validation model when the value has behavior, construction rules, or a long lifetime. Do not replace truly open metadata with a closed shape.

#### Mark declaration intent

Look for declarations whose intended relationship is not checked directly:

- Use `override` when an accidental rename or signature drift could detach a method from its base declaration.
- Use `final` when subclassing or reassignment would violate the design.
- Investigate `dataclass_transform` when a project library generates dataclass-like constructors or fields.
- Distinguish a type alias from a runtime assignment when that intent affects checking or runtime use.

These features describe intent; they do not replace runtime behavior. Verify native alias syntax, decorator availability, generated signatures, checker behavior, and runtime introspection.

#### Restrict special strings and type expressions

Consider `LiteralString` only when an API must reject strings that are not literal-derived. It does not validate SQL, shell syntax, HTML, or another language.

When an API accepts a type expression as data, research the current type-expression annotation features rather than forcing the value into `type[Any]` or `object`. These features are recent. Verify their current specification and full support before recommending them.

#### Contain untyped boundaries

Trace values from JSON, YAML, environment variables, database drivers, plugins, and untyped libraries. Recommend one parse function or validation model that returns a domain type.

Use `object` or an unknown input type at the external boundary when needed. Don't cast boundary data to a trusted type without a runtime check.

#### Improve collection and mutation types

Check whether callers need mutation. Accept `Sequence`, `Mapping`, `Iterable`, or a small protocol when the function only reads. Return a concrete type when callers rely on concrete behavior.

Use immutable domain objects where mutation creates invalid intermediate states. Do not suggest abstract collection types only for style.

### 7. Validate each recommendation

Keep a strengthening opportunity only when all answers are clear:

1. What plausible error does the current type design permit?
2. Why does the current checker accept it?
3. Which type design rejects it?
4. Why is that design a better semantic match than nearby constructs?
5. What code boundary owns the change?
6. What runtime validation remains necessary?
7. What is the migration cost and compatibility effect?
8. Can the minimum Python parse it, can the runtime import it, and does the checker support it?
9. Do runtime annotation consumers accept it?

For each nontrivial design, create a temporary probe with one valid use that passes and one plausible misuse that fails. Use `assert_type` or `reveal_type` when inferred relationships matter. Run the project's exact checker command. Also run the minimum Python parser or runtime when the syntax or runtime form changes. Exercise the relevant runtime annotation consumer when the project uses one.

Record the commands, versions, and results. If you cannot run a probe, label the design `unverified` and explain why. Do not turn an expected future error into claimed evidence.

Remove recommendations that only add annotation detail without catching a named error.

### 8. Rank the work

Rank findings by expected value, not by syntax.

Consider these factors:

- **Impact:** The harm caused by the accepted error.
- **Likelihood:** How plausible the future edit or value mix-up is.
- **Reach:** The number of consumers that inherit the weak type.
- **Distance:** The separation between the edit site and the failure site.
- **Boundary position:** Domain-core weaknesses rank above contained adapter code.
- **Runtime compensation:** Existing validation reduces urgency.
- **Cost:** Prefer focused changes that protect many call sites.

Use `critical`, `high`, `medium`, or `low` only when the distinction helps the reader choose an order. Explain the rank in plain language.

### 9. Identify system design causes

Review every proven erosion finding and strengthening opportunity after the local review. Classify each item as `local`, `systemic`, or `both`.

Use `systemic` when the weak type follows from how the system moves, owns, or transforms data. Use `local` when one declaration or implementation choice fully owns the problem. Use `both` when a local fix helps but a system design change provides a stronger result.

Look for shared causes across findings. A design cause can affect one finding or many findings. Do not require a minimum count.

Ask these questions:

1. Do several consumers parse, validate, cast, narrow, or reconstruct the same value?
2. Does a weak data structure cross several layers that each guess its shape?
3. Does domain logic depend on transport, storage, framework, or serialization formats?
4. Do several local fixes repeat the same type declaration or runtime check?
5. Does one object represent unrelated states, responsibilities, or lifecycle stages?
6. Does dynamic dispatch spread beyond the boundary that requires it?
7. Do casts and suppressions compensate for an interface that loses type relationships?
8. Would moving ownership to one boundary make downstream code trusted by construction?

Trace the full data flow for each possible design cause. Identify where the value enters, changes shape, becomes trusted, and leaves the system. Name the layer that owns parsing, validation, state transitions, or dispatch in the proposed design.

Consider system changes such as:

- Parse external data once, then pass a validated domain type downstream.
- Keep raw transport models separate from trusted domain models.
- Replace a general mapping that crosses layers with a type owned by one layer.
- Centralize state transitions in a tagged union or state-specific object model.
- Contain dynamic framework or plugin behavior behind a typed adapter.
- Preserve generic or callable relationships in a shared interface instead of restoring them at each caller.
- Move serialization and deserialization to one boundary rather than exposing wire formats to domain logic.
- Split an object that combines unrelated responsibilities and therefore requires broad optional or union types.

A system design recommendation must include all of these details:

- **Shared cause:** The design choice that creates the weak types.
- **Affected items:** Every finding or opportunity that the change improves.
- **Ownership:** The boundary or component that owns the stronger type in the proposed design.
- **Design change:** The new data flow, interface, or responsibility split.
- **Typing gain:** The specific error classes that become detectable.
- **Runtime checks:** The validation that remains necessary and where it runs.
- **Local fallback:** The local improvements to use when the design change is not possible.
- **Scope and cost:** The interfaces, callers, and migration work affected.
- **Verification:** Mutations or negative type-checking examples that must fail after the change.

Recommend the system design even when it has a high migration cost, if it materially improves the type guarantees. State the cost directly. Do not weaken the recommendation only to make it easier to adopt.

Reject a system design recommendation when it only moves code, creates a central dependency without clear ownership, or adds types without catching more errors.

## Do not report

Do not report these cases unless a specific error remains catchable:

- `Any` that stays inside a validated boundary adapter.
- A cast justified by an adjacent runtime check or schema validation.
- Dynamic access that is the intended plugin, proxy, or framework boundary and doesn't enter domain code.
- `object` used as a safe unknown type.
- A type-checking bypass with a sound constraint that the project can't control.
- An abstract collection type that offers no error-detection benefit.
- A wrapper type that adds ceremony but no useful domain distinction.
- A closed union for values that are open to external extension.
- A type-level claim that still needs runtime validation.

## Report format

Start with a short verdict that states what the checker verifies, the main verification gaps, and the highest-value strengthening opportunity.

Give each reported item an identifier. Use `E1`, `E2`, and so on for proven erosion. Use `T1`, `T2`, and so on for strengthening opportunities.

### Proven erosion

Use this format for each demonstrated silent break:

```markdown
### E1 [priority] Short finding name

- **Where:** `path:line`, symbol
- **Silent break:** A specific edit leaves this code wrong without a checker error.
- **Evidence:** Mutation output or a hand-traced result.
- **Reach:** Number of affected sites and files.
- **Distance:** Edit site to failure site.
- **Boundary:** Existing validation point or missing validation point.
- **Fix:** Named type construct, why it fits better than nearby choices, and a focused code sketch.
- **Support:** Parser, runtime or backport, checker, and runtime-consumer compatibility.
- **Verification:** The mutation and design-probe commands with observed results. Mark unrun probes as unverified.
```

### Type-strengthening opportunities

Use this format for each improvement that is not proven erosion:

```markdown
### T1 [priority] Short opportunity name

- **Where:** `path:line`, symbol or workflow
- **Error caught:** The concrete mistake that the current types accept.
- **Why accepted:** The missing distinction, state, relationship, or boundary.
- **Design:** Named type construct, why it fits better than nearby choices, and a focused before-and-after sketch.
- **Support:** Parser, runtime or backport, checker, and runtime-consumer compatibility.
- **Limits:** Runtime checks that remain necessary.
- **Cost:** Migration scope and compatibility effect.
- **Verification:** The positive and negative probe, exact commands, and observed results. Mark unrun probes as unverified.
```

### System design opportunities

After the local findings, include a classification table with every reported item. Give each system design recommendation a `D1`, `D2`, or later identifier.

```markdown
| Item | Classification | Reason |
|---|---|---|
| E1 | Both | Repeated boundary parsing causes the local weak types. |
```

Use this format for each `systemic` or `both` item or group:

```markdown
### D1 [priority] Short system design name

- **Affected items:** Finding and opportunity identifiers.
- **Shared cause:** The system design that produces the weak types.
- **Current data flow:** Where the value enters, changes shape, and becomes trusted.
- **Design change:** The proposed ownership boundary, interface, or data flow.
- **Typing gain:** The error classes that the design makes detectable.
- **Runtime checks:** The validation that remains and where it runs.
- **Local fallback:** The local fixes to apply if the design change is not possible.
- **Scope and cost:** The affected interfaces, callers, and migration work.
- **Support:** Parser, runtime or backport, checker, and runtime-consumer compatibility.
- **Verification:** Mutations and positive and negative probes with observed results. Mark unrun probes as unverified.
```

Include this section when one item qualifies. Do not wait for several related findings.

End with these sections:

- **Recommended order:** List the local fixes and system changes in the order that gives the most protection.
- **Coverage:** List the capability profile, edit classes, workflows, boundaries, and code-specific failure hypotheses reviewed. State that the hint list did not define coverage.
- **Mutations:** List each mutation and whether the checker caught it.
- **Excluded items:** List what you did not review and why.
- **Novel mechanisms:** Describe problems that did not match a listed pattern. If none became findings, list the code-specific hypotheses you tested.
- **Not reported:** List suspicious patterns you reviewed but did not report because they lacked a concrete error.

A type-design probe is a short example with a valid use that must pass and a plausible misuse that must fail. Keep probes outside the runtime test suite unless the project already uses a tool for type-checking tests. Delete temporary probes after the audit unless the user asks to retain them.
