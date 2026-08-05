#!/usr/bin/env python3
"""Generate and validate the repository skill catalog."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = ROOT / "catalog" / "taxonomy.json"
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
README_START = "<!-- catalog-summary:start -->"
README_END = "<!-- catalog-summary:end -->"


class CatalogError(ValueError):
    """Raised when the skill catalog is inconsistent."""


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    directory: Path


def load_taxonomy() -> dict[str, Any]:
    try:
        taxonomy = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CatalogError(f"缺少分类配置：{TAXONOMY_PATH.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise CatalogError(f"分类配置不是有效 JSON：{exc}") from exc

    if taxonomy.get("schema_version") != 1:
        raise CatalogError("taxonomy.json 的 schema_version 必须为 1")
    if not isinstance(taxonomy.get("categories"), list):
        raise CatalogError("taxonomy.json 的 categories 必须是数组")
    return taxonomy


def unquote_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def parse_frontmatter(skill_file: Path) -> tuple[str, str]:
    text = skill_file.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise CatalogError(f"{skill_file.relative_to(ROOT)} 缺少 YAML frontmatter")

    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise CatalogError(f"{skill_file.relative_to(ROOT)} 的 YAML frontmatter 未闭合") from exc

    fields: dict[str, str] = {}
    index = 1
    while index < end:
        match = re.match(r"^(name|description):\s*(.*)$", lines[index])
        if not match:
            index += 1
            continue

        key, raw_value = match.groups()
        if raw_value in {"|", "|-", "|+", ">", ">-", ">+"}:
            block: list[str] = []
            index += 1
            while index < end and (not lines[index].strip() or lines[index][:1].isspace()):
                block.append(lines[index].strip())
                index += 1
            fields[key] = ("\n" if raw_value.startswith("|") else " ").join(block).strip()
            continue

        fields[key] = unquote_yaml_scalar(raw_value)
        index += 1

    name = fields.get("name", "").strip()
    description = fields.get("description", "").strip()
    if not name or not description:
        raise CatalogError(f"{skill_file.relative_to(ROOT)} 必须包含 name 和 description")
    return name, description


def discover_skills() -> dict[str, Skill]:
    skills: dict[str, Skill] = {}
    for directory in sorted(ROOT.iterdir(), key=lambda path: path.name):
        skill_file = directory / "SKILL.md"
        if not directory.is_dir() or not skill_file.is_file():
            continue

        name, description = parse_frontmatter(skill_file)
        if not SKILL_NAME_PATTERN.fullmatch(name):
            raise CatalogError(f"skill 名称不合规：{name}")
        if name != directory.name:
            raise CatalogError(f"目录名 {directory.name} 与 SKILL.md name {name} 不一致")
        if name in skills:
            raise CatalogError(f"skill 名称重复：{name}")
        skills[name] = Skill(name=name, description=description, directory=directory)

    if not skills:
        raise CatalogError("仓库根目录未发现任何 SKILL.md")
    return skills


def validate_node(node: dict[str, Any], path: tuple[str, ...], assignments: dict[str, str]) -> None:
    required = ("id", "name", "description", "skills", "children")
    missing = [key for key in required if key not in node]
    if missing:
        raise CatalogError(f"分类节点缺少字段：{', '.join(missing)}")
    if not isinstance(node["skills"], list) or not isinstance(node["children"], list):
        raise CatalogError(f"分类 {node['name']} 的 skills 和 children 必须是数组")

    current_path = path + (str(node["name"]),)
    for skill_name in node["skills"]:
        if skill_name in assignments:
            raise CatalogError(
                f"skill {skill_name} 被重复归类：{assignments[skill_name]}；{' / '.join(current_path)}"
            )
        assignments[skill_name] = " / ".join(current_path)

    child_ids: set[str] = set()
    for child in node["children"]:
        child_id = child.get("id")
        if child_id in child_ids:
            raise CatalogError(f"分类 {node['name']} 下的子分类 id 重复：{child_id}")
        child_ids.add(child_id)
        validate_node(child, current_path, assignments)


def validate_taxonomy(taxonomy: dict[str, Any], skills: dict[str, Skill]) -> None:
    catalog = taxonomy.get("catalog")
    if not isinstance(catalog, dict):
        raise CatalogError("taxonomy.json 缺少 catalog 对象")

    categories = taxonomy["categories"]
    max_root = catalog.get("max_root_categories")
    if not isinstance(max_root, int) or max_root < 1:
        raise CatalogError("max_root_categories 必须是正整数")
    if len(categories) > max_root:
        raise CatalogError(f"一级分类共 {len(categories)} 个，超过上限 {max_root} 个")

    root_ids: set[str] = set()
    assignments: dict[str, str] = {}
    for category in categories:
        category_id = category.get("id")
        if category_id in root_ids:
            raise CatalogError(f"一级分类 id 重复：{category_id}")
        root_ids.add(category_id)
        validate_node(category, (), assignments)

    discovered = set(skills)
    configured = set(assignments)
    missing = sorted(discovered - configured)
    unknown = sorted(configured - discovered)
    errors: list[str] = []
    if missing:
        errors.append(f"未归类 skill：{', '.join(missing)}")
    if unknown:
        errors.append(f"配置引用不存在的 skill：{', '.join(unknown)}")
    if errors:
        raise CatalogError("；".join(errors))


def escape_table(value: str) -> str:
    return " ".join(value.replace("|", "\\|").split())


def count_node_skills(node: dict[str, Any]) -> int:
    return len(node["skills"]) + sum(count_node_skills(child) for child in node["children"])


def collect_node_skills(node: dict[str, Any]) -> list[str]:
    names = list(node["skills"])
    for child in node["children"]:
        names.extend(collect_node_skills(child))
    return sorted(names)


def render_node(node: dict[str, Any], skills: dict[str, Skill], depth: int) -> list[str]:
    heading = "#" * (depth + 2)
    lines = [f"{heading} {node['name']}", "", str(node["description"]), ""]
    if node["skills"]:
        lines.extend(["| Skill | 能力说明 |", "| --- | --- |"])
        for skill_name in sorted(node["skills"]):
            skill = skills[skill_name]
            link = f"{skill.directory.name}/SKILL.md"
            lines.append(f"| [`{skill.name}`]({link}) | {escape_table(skill.description)} |")
        lines.append("")
    for child in node["children"]:
        lines.extend(render_node(child, skills, depth + 1))
    return lines


def render_catalog(taxonomy: dict[str, Any], skills: dict[str, Skill]) -> str:
    catalog = taxonomy["catalog"]
    categories = taxonomy["categories"]
    lines = [
        f"# {catalog['title']}",
        "",
        "> 此文件由 `python scripts/update_catalog.py` 生成。请修改 `catalog/taxonomy.json`，不要直接编辑此文件。",
        "",
        "## 分类总览",
        "",
        "| 一级分类 | 定义 | Skill 数量 |",
        "| --- | --- | ---: |",
    ]
    for category in categories:
        lines.append(
            f"| [{category['name']}](#{category['id']}) | "
            f"{escape_table(str(category['description']))} | {count_node_skills(category)} |"
        )

    lines.extend(["", f"共收录 **{len(skills)}** 个 skill。", ""])
    for category in categories:
        lines.append(f"<a id=\"{category['id']}\"></a>")
        lines.extend(render_node(category, skills, 0))

    lines.extend(
        [
            "## 分类演进规则",
            "",
            f"1. 一级分类最多保留 {catalog['max_root_categories']} 个，按稳定的用户任务域划分。",
            "2. 每个 skill 只归入一个最具体的分类节点，禁止重复归类。",
            "3. 新增 skill 时先放入现有一级分类；同一主题形成多个 skill 后再增加子分类。",
            "4. 分类只影响目录展示，不移动 skill 根目录，不修改 `SKILL.md` frontmatter。",
            "5. 目录由脚本从 `SKILL.md` 的 `name` 与 `description` 动态生成；校验失败时禁止合入。",
            "",
            "## 参考仓库与采纳点",
            "",
        ]
    )
    for reference in taxonomy.get("references", []):
        lines.append(f"- [{reference['name']}]({reference['url']})：{reference['adopted']}")
    lines.append("")
    return "\n".join(lines)


def render_readme(current: str, taxonomy: dict[str, Any], skills: dict[str, Skill]) -> str:
    start = current.find(README_START)
    end = current.find(README_END)
    if start < 0 or end < 0 or end < start:
        raise CatalogError("README.md 缺少有效的分类摘要标记")

    lines = [
        README_START,
        "| 分类 | 定义 | Skills |",
        "| --- | --- | --- |",
    ]
    for category in taxonomy["categories"]:
        skill_links = [f"[`{name}`]({skills[name].directory.name}/SKILL.md)" for name in collect_node_skills(category)]
        lines.append(
            f"| [{category['name']}](CATALOG.md#{category['id']}) | "
            f"{escape_table(str(category['description']))} | {', '.join(skill_links)} |"
        )
    lines.append(README_END)
    block = "\n".join(lines)
    return current[:start] + block + current[end + len(README_END) :]


def main() -> int:
    parser = argparse.ArgumentParser(description="生成或校验 LFen Skills 分类目录")
    parser.add_argument("--check", action="store_true", help="只检查 CATALOG.md 是否为最新")
    args = parser.parse_args()

    try:
        taxonomy = load_taxonomy()
        skills = discover_skills()
        validate_taxonomy(taxonomy, skills)
        rendered = render_catalog(taxonomy, skills)
        output_path = ROOT / taxonomy["catalog"]["generated_file"]
        readme_path = ROOT / "README.md"
        readme = readme_path.read_text(encoding="utf-8")
        rendered_readme = render_readme(readme, taxonomy, skills)

        if args.check:
            if not output_path.exists() or output_path.read_text(encoding="utf-8") != rendered:
                raise CatalogError(
                    f"{output_path.relative_to(ROOT)} 不是最新版本；运行 python scripts/update_catalog.py"
                )
            if readme != rendered_readme:
                raise CatalogError("README.md 的分类摘要不是最新版本；运行 python scripts/update_catalog.py")
            print(f"分类目录校验通过：{len(skills)} 个 skill，{len(taxonomy['categories'])} 个一级分类")
            return 0

        output_path.write_text(rendered, encoding="utf-8", newline="\n")
        readme_path.write_text(rendered_readme, encoding="utf-8", newline="\n")
        print(f"已更新 README.md 与 {output_path.relative_to(ROOT)}：{len(skills)} 个 skill")
        return 0
    except (CatalogError, OSError, KeyError, TypeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
