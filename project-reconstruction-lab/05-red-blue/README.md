# Red / Blue / Counter Attack

## 角色

- Red Team：杀死没有必要的复杂度，攻击事实、架构、成本和替代方案。
- Blue Team：基于证据给出最小可行回应，不以“企业级”“最佳实践”代替证明。
- Counter Attack：攻击 Blue 的隐含假设、失败语义、运营成本、规模和安全声明。

## 生命周期

```text
Claim
→ Red Attack
→ Blue Response
→ Counter Attack
→ Decision
→ Canonical Sync / Gap
```

Blue 回答不会自动通过。只有反击后仍成立，Architecture 才能进入 `SURVIVED`。

## 输出

每项设计必须得到：`KEEP`、`SIMPLIFY`、`ADOPT`、`EXTEND`、`BUILD`、`DEFER` 或 `DELETE`，并附原因、替代方案、证据和回滚条件。
