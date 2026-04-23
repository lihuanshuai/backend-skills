# 命名规范

## 约定

- **变量 / 函数**：`snake_case`
- **类名**：`PascalCase`
- **常量**：`UPPER_SNAKE_CASE`
- **私有成员**：前缀 `_`（如 `_cache`）
- **布尔变量**：使用可读前缀，如 `is_`、`has_`、`can_`、`should_`

## 避免

- `tmp`、`data2`、`foo`、`bar` 这类语义弱命名（短生命周期临时变量除外）
- 单字符命名泛滥（`i`、`j` 仅用于短循环索引）

## 推荐

- 名称体现业务语义与单位，如 `retry_count`、`timeout_seconds`、`member_ids`
