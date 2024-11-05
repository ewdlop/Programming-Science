Refinement types enhance standard types by incorporating predicates that impose additional constraints on the values they can hold. This approach allows for more precise type definitions and improved program correctness. Below are examples illustrating the application of refinement types in various programming languages:

**1. Haskell**

In Haskell, the Liquid Haskell extension enables the use of refinement types. For instance, to define a type for natural numbers (non-negative integers):

```haskell
{-@ type Nat = {v:Int | v >= 0} @-}
```

This definition specifies that `Nat` includes all integers `Int` where the value `v` satisfies the predicate `v >= 0`. Can This ensures that any value of type `Nat` is non-negative. citeturn0search4

**2. TypeScript**

In TypeScript, refinement types can be simulated using type guards and user-defined type predicates. For example, to define a function that checks if a number is positive:

```typescript
function isPositive(n: number): n is number & { __brand: 'positive' } {
  return n > 0;
}
```

Here, `isPositive` acts as a type guard that refines the type of `n` to ensure it is positive. This pattern allows for more precise type checking at compile time.

**3. Rust**

In Rust, the Flux project introduces refinement types to provide stronger guarantees about program behavior. For instance, to define a type for non-zero integers:

```rust
type NonZeroInt = i32 where |x| x != 0;
```

This definition specifies that `NonZeroInt` includes all 32-bit integers `i32` where the value `x` is not equal to zero, ensuring that any value of this type is non-zero.

**4. F#**

In F#, refinement types can be implemented using type providers or active patterns. For example, to define a type for even integers:

```fsharp
let (|Even|_|) n = if n % 2 = 0 then Some n else None
```

This active pattern `Even` allows for pattern matching on integers to ensure they are even, effectively refining the type during pattern matching.

These examples demonstrate how refinement types can be utilized in different programming languages to enforce specific constraints within the type system, leading to safer and more reliable code by catching potential errors at compile time.

**中文：**

精化类型通过在标准类型中添加谓词来施加额外的约束，从而实现更精确的类型定义和提高程序的正确性。以下是在各种编程语言中应用精化类型的示例：

**1. Haskell**

在 Haskell 中，使用 Liquid Haskell 扩展可以实现精化类型。例如，定义自然数（非负整数）类型：

```haskell
{-@ type Nat = {v:Int | v >= 0} @-}
```

此定义指定 `Nat` 包含所有整数 `Int`，其中值 `v` 满足谓词 `v >= 0`，确保任何 `Nat` 类型的值都是非负的。 citeturn0search4

**2. TypeScript**

在 TypeScript 中，可以使用类型守卫和用户定义的类型谓词来模拟精化类型。例如，定义一个检查数字是否为正数的函数：

```typescript
function isPositive(n: number): n is number & { __brand: 'positive' } {
  return n > 0;
}
```

这里，`isPositive` 作为类型守卫，将 `n` 的类型精化为确保其为正数。这种模式允许在编译时进行更精确的类型检查。

**3. Rust**

在 Rust 中，Flux 项目引入了精化类型，以提供更强的程序行为保证。例如，定义一个非零整数类型：

```rust
type NonZeroInt = i32 where |x| x != 0;
```

此定义指定 `NonZeroInt` 包含所有 32 位整数 `i32`，其中值 `x` 不等于零，确保此类型的任何值都不是零。

**4. F#**

在 F# 中，可以使用类型提供程序或活动模式来实现精化类型。例如，定义一个偶数类型：

```fsharp
let (|Even|_|) n = if n % 2 = 0 then Some n else None
```

此活动模式 `Even` 允许对整数进行模式匹配，以确保它们是偶数，有效地在模式匹配期间精化类型。

这些示例展示了如何在不同的编程语言中使用精化类型在类型系统中强制执行特定约束，通过在编译时捕获潜在错误，从而编写更安全和可靠的代码。

**Formal English:**

Refinement types enhance standard types by incorporating predicates that impose additional constraints on the values they can hold. This approach allows for more precise type definitions and improved program correctness. Below are examples illustrating the application of refinement types in various programming languages:

**1. Haskell**

In Haskell, the Liquid Haskell extension enables the use of refinement types. For instance, to define a type for natural numbers (non-negative integers):

```haskell
{-@ type Nat = {v:Int | v >= 0} @-}
```

This definition specifies that `Nat` includes all integers `Int` where the value `v` satisfies the predicate `v >= 0`. This ensures that any value of type `Nat` is non-negative. citeturn0search4

**2. TypeScript**

In TypeScript, refinement types can be simulated using type guards and user-defined type predicates. For example, to define a function that checks if a number is positive 
