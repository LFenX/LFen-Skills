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
SKILLS_ROOT = ROOT / "skills"
TAXONOMY_PATH = ROOT / "catalog" / "taxonomy.json"
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CATEGORY_ID_PATTERN = SKILL_NAME_PATTERN
TAG_PATTERN = SKILL_NAME_PATTERN
REQUIRED_SCOPE_IDS = {"general", "team", "project"}
TAXONOMY_SCHEMA_VERSION = 3
README_START = "<!-- catalog-summary:start -->"
README_END = "<!-- catalog-summary:end -->"
SKILLS_START = "<!-- catalog-detail:start -->"
SKILLS_END = "<!-- catalog-detail:end -->"


class CatalogError(ValueError):
    """Raised when the skill catalog is inconsistent."""


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    description_en: str
    directory: Path


@dataclass(frozen=True)
class CategoryPath:
    ids: tuple[str, ...]
    names: tuple[str, ...]

    @property
    def label(self) -> str:
        return " / ".join(self.names)


def load_taxonomy() -> dict[str, Any]:
    try:
        taxonomy = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CatalogError(f"缺少分类配置：{TAXONOMY_PATH.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise CatalogError(f"分类配置不是有效 JSON：{exc}") from exc

    if taxonomy.get("schema_version") != TAXONOMY_SCHEMA_VERSION:
        raise CatalogError(f"taxonomy.json 的 schema_version 必须为 {TAXONOMY_SCHEMA_VERSION}")
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


def parse_frontmatter(skill_file: Path) -> tuple[str, str, str]:
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
        match = re.match(r"^(name|description_en|description):\s*(.*)$", lines[index])
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
    description_en = fields.get("description_en", "").strip()
    if not name or not description or not description_en:
        raise CatalogError(f"{skill_file.relative_to(ROOT)} 必须包含 name、description 和 description_en")
    return name, description, description_en


def discover_skills() -> dict[str, Skill]:
    skills: dict[str, Skill] = {}
    legacy_directories = [
        directory
        for directory in ROOT.iterdir()
        if directory.is_dir() and (directory / "SKILL.md").is_file()
    ]
    if legacy_directories:
        names = ", ".join(sorted(directory.name for directory in legacy_directories))
        raise CatalogError(
            f"发现未规范化的根目录 skill：{names}；"
            "skill 必须位于 skills/<分类>/<skill-name>/"
        )

    if not SKILLS_ROOT.is_dir():
        raise CatalogError("缺少 skills/ 物理目录")

    skill_files = sorted(SKILLS_ROOT.rglob("SKILL.md"), key=lambda path: path.as_posix())
    for skill_file in skill_files:
        directory = skill_file.parent

        name, description, description_en = parse_frontmatter(skill_file)
        if not SKILL_NAME_PATTERN.fullmatch(name):
            raise CatalogError(f"skill 名称不合规：{name}")
        if name != directory.name:
            raise CatalogError(f"目录名 {directory.name} 与 SKILL.md name {name} 不一致")
        if name in skills:
            raise CatalogError(f"skill 名称重复：{name}")
        skills[name] = Skill(name=name, description=description, description_en=description_en, directory=directory)

    if not skills:
        raise CatalogError("skills/ 目录未发现任何 SKILL.md")
    return skills


def validate_output_path(value: Any, field: str, suffix: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(f"catalog.{field} 必须是非空字符串")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.suffix.lower() != suffix:
        raise CatalogError(f"catalog.{field} 必须是仓库内的 {suffix} 相对路径")
    return value


def validate_skills_root(value: Any) -> str:
    if not isinstance(value, str) or value != "skills":
        raise CatalogError("catalog.skills_root 必须固定为 skills")
    return value


def skill_relative_path(skill: Skill) -> str:
    return skill.directory.relative_to(ROOT).as_posix()


def expected_skill_directory(category: CategoryPath, skill_name: str) -> Path:
    return SKILLS_ROOT.joinpath(*category.ids, skill_name)


def validate_node(
    node: dict[str, Any],
    id_path: tuple[str, ...],
    name_path: tuple[str, ...],
    assignments: dict[str, CategoryPath],
    category_ids: set[str],
    depth: int,
    max_depth: int,
) -> None:
    if not isinstance(node, dict):
        raise CatalogError("分类节点必须是对象")
    required = ("id", "name", "name_en", "description", "description_en", "skills", "children")
    missing = [key for key in required if key not in node]
    if missing:
        raise CatalogError(f"分类节点缺少字段：{', '.join(missing)}")

    category_id = node["id"]
    name = node["name"]
    description = node["description"]
    if not isinstance(category_id, str) or not CATEGORY_ID_PATTERN.fullmatch(category_id):
        raise CatalogError(f"分类 id 不合规：{category_id}")
    if category_id in category_ids:
        raise CatalogError(f"分类 id 全局重复：{category_id}")
    category_ids.add(category_id)
    if not isinstance(name, str) or not name.strip():
        raise CatalogError(f"分类 {category_id} 的 name 必须是非空字符串")
    if not isinstance(description, str) or not description.strip():
        raise CatalogError(f"分类 {name} 的 description 必须是非空字符串")
    if not isinstance(node["name_en"], str) or not node["name_en"].strip():
        raise CatalogError(f"分类 {name} 的 name_en 必须是非空字符串")
    if not isinstance(node["description_en"], str) or not node["description_en"].strip():
        raise CatalogError(f"分类 {name} 的 description_en 必须是非空字符串")
    if depth > max_depth:
        raise CatalogError(f"分类 {name} 深度为 {depth}，超过上限 {max_depth}")
    if not isinstance(node["skills"], list) or not isinstance(node["children"], list):
        raise CatalogError(f"分类 {name} 的 skills 和 children 必须是数组")
    if not node["skills"] and not node["children"]:
        raise CatalogError(f"分类 {name} 为空；删除该分类或加入 skill")
    if node["skills"] and node["children"]:
        raise CatalogError(f"分类 {name} 同时包含 skills 和 children；skill 必须归入最具体的叶子分类")
    if any(not isinstance(skill_name, str) for skill_name in node["skills"]):
        raise CatalogError(f"分类 {name} 的 skills 必须全部是字符串")
    if node["skills"] != sorted(node["skills"]):
        raise CatalogError(f"分类 {name} 的 skills 必须按名称排序")

    current_path = CategoryPath(ids=id_path + (category_id,), names=name_path + (name,))
    for skill_name in node["skills"]:
        if skill_name in assignments:
            raise CatalogError(
                f"skill {skill_name} 被重复归类：{assignments[skill_name].label}；{current_path.label}"
            )
        assignments[skill_name] = current_path

    for child in node["children"]:
        validate_node(
            child,
            current_path.ids,
            current_path.names,
            assignments,
            category_ids,
            depth + 1,
            max_depth,
        )


def validate_skill_metadata(
    taxonomy: dict[str, Any], skills: dict[str, Skill], scopes: dict[str, Any]
) -> None:
    metadata = taxonomy.get("skill_metadata")
    if not isinstance(metadata, dict):
        raise CatalogError("taxonomy.json 缺少 skill_metadata 对象")

    discovered = set(skills)
    configured = set(metadata)
    missing = sorted(discovered - configured)
    unknown = sorted(configured - discovered)
    errors: list[str] = []
    if missing:
        errors.append(f"缺少元数据的 skill：{', '.join(missing)}")
    if unknown:
        errors.append(f"元数据引用不存在的 skill：{', '.join(unknown)}")
    if errors:
        raise CatalogError("；".join(errors))

    for skill_name in sorted(metadata):
        item = metadata[skill_name]
        if not isinstance(item, dict):
            raise CatalogError(f"skill {skill_name} 的元数据必须是对象")
        if set(item) != {"scope", "tags"}:
            raise CatalogError(f"skill {skill_name} 的元数据字段必须且只能是 scope、tags")
        scope = item["scope"]
        if scope not in scopes:
            raise CatalogError(f"skill {skill_name} 的 scope 未定义：{scope}")
        tags = item["tags"]
        if not isinstance(tags, list) or not tags:
            raise CatalogError(f"skill {skill_name} 的 tags 必须是非空数组")
        if any(not isinstance(tag, str) or not TAG_PATTERN.fullmatch(tag) for tag in tags):
            raise CatalogError(f"skill {skill_name} 含不合规 tag；tag 必须使用小写 kebab-case")
        if tags != sorted(set(tags)):
            raise CatalogError(f"skill {skill_name} 的 tags 必须去重并按名称排序")


def validate_references(taxonomy: dict[str, Any]) -> None:
    references = taxonomy.get("references", [])
    if not isinstance(references, list):
        raise CatalogError("taxonomy.json 的 references 必须是数组")
    names: set[str] = set()
    for reference in references:
        if not isinstance(reference, dict) or set(reference) != {"name", "url", "adopted"}:
            raise CatalogError("每个 reference 必须且只能包含 name、url、adopted")
        name = reference["name"]
        if not all(isinstance(reference[key], str) and reference[key].strip() for key in reference):
            raise CatalogError("reference 的 name、url、adopted 必须是非空字符串")
        if name in names:
            raise CatalogError(f"reference 名称重复：{name}")
        if not reference["url"].startswith("https://"):
            raise CatalogError(f"reference URL 必须使用 HTTPS：{reference['url']}")
        names.add(name)


def validate_taxonomy(taxonomy: dict[str, Any], skills: dict[str, Skill]) -> dict[str, CategoryPath]:
    catalog = taxonomy.get("catalog")
    if not isinstance(catalog, dict):
        raise CatalogError("taxonomy.json 缺少 catalog 对象")
    for key in (
        "title",
        "generated_markdown",
        "generated_index",
        "skills_root",
        "layout",
        "max_depth",
        "scopes",
    ):
        if key not in catalog:
            raise CatalogError(f"catalog 缺少字段：{key}")
    if not isinstance(catalog["title"], str) or not catalog["title"].strip():
        raise CatalogError("catalog.title 必须是非空字符串")
    generated_markdown = validate_output_path(catalog["generated_markdown"], "generated_markdown", ".md")
    generated_index = validate_output_path(catalog["generated_index"], "generated_index", ".json")
    validate_skills_root(catalog["skills_root"])
    if catalog["layout"] != "skills/<category-path>/<skill-name>":
        raise CatalogError("catalog.layout 必须固定为 skills/<category-path>/<skill-name>")
    protected_paths = {
        Path("README.md"),
        TAXONOMY_PATH.relative_to(ROOT),
        Path("scripts/update_catalog.py"),
    }
    for generated_path in (Path(generated_markdown), Path(generated_index)):
        if generated_path in protected_paths:
            raise CatalogError(f"生成路径不能覆盖权威源：{generated_path}")
    max_depth = catalog["max_depth"]
    if not isinstance(max_depth, int) or max_depth < 1:
        raise CatalogError("catalog.max_depth 必须是正整数")

    scopes = catalog["scopes"]
    if not isinstance(scopes, dict) or not scopes:
        raise CatalogError("catalog.scopes 必须是非空对象")
    if set(scopes) != REQUIRED_SCOPE_IDS:
        raise CatalogError("catalog.scopes 必须且只能定义 general、team、project")
    for scope_id, scope in scopes.items():
        if not isinstance(scope_id, str) or not CATEGORY_ID_PATTERN.fullmatch(scope_id):
            raise CatalogError(f"scope id 不合规：{scope_id}")
        if not isinstance(scope, dict) or set(scope) != {"name", "description"}:
            raise CatalogError(f"scope {scope_id} 必须且只能包含 name、description")
        if not all(isinstance(scope[key], str) and scope[key].strip() for key in scope):
            raise CatalogError(f"scope {scope_id} 的 name、description 必须是非空字符串")

    categories = taxonomy["categories"]
    if not isinstance(categories, list) or not categories:
        raise CatalogError("taxonomy.json 的 categories 必须是非空数组")
    assignments: dict[str, CategoryPath] = {}
    category_ids: set[str] = set()
    for category in categories:
        validate_node(category, (), (), assignments, category_ids, 1, max_depth)

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

    for skill_name, category in assignments.items():
        expected = expected_skill_directory(category, skill_name).resolve()
        actual = skills[skill_name].directory.resolve()
        if actual != expected:
            raise CatalogError(
                f"skill {skill_name} 的物理路径不符合分类："
                f"应为 {expected.relative_to(ROOT).as_posix()}，"
                f"实际为 {actual.relative_to(ROOT).as_posix()}"
            )

    validate_skill_metadata(taxonomy, skills, scopes)
    validate_references(taxonomy)
    return assignments


def escape_table(value: str) -> str:
    return " ".join(value.replace("|", "\\|").split())


def count_node_skills(node: dict[str, Any]) -> int:
    return len(node["skills"]) + sum(count_node_skills(child) for child in node["children"])


def collect_node_skills(node: dict[str, Any]) -> list[str]:
    names = list(node["skills"])
    for child in node["children"]:
        names.extend(collect_node_skills(child))
    return sorted(names)


def render_node(
    node: dict[str, Any],
    skills: dict[str, Skill],
    metadata: dict[str, dict[str, Any]],
    scopes: dict[str, dict[str, str]],
    depth: int,
) -> list[str]:
    heading = "#" * (depth + 2)
    lines = [f"<a id=\"{node['id']}\"></a>", f"{heading} {node['name']}", "", str(node["description"]), ""]
    if node["skills"]:
        lines.extend(["| Skill | 适用范围 | 标签 | 能力说明 |", "| --- | --- | --- | --- |"])
        for skill_name in sorted(node["skills"]):
            skill = skills[skill_name]
            skill_metadata = metadata[skill_name]
            scope_name = scopes[skill_metadata["scope"]]["name"]
            tags = ", ".join(f"`{tag}`" for tag in skill_metadata["tags"])
            link = f"{skill_relative_path(skill)}/SKILL.md"
            lines.append(
                f"| [`{skill.name}`]({link}) | {scope_name} | {tags} | {escape_table(skill.description)} |"
            )
        lines.append("")
    for child in node["children"]:
        lines.extend(render_node(child, skills, metadata, scopes, depth + 1))
    return lines


def render_catalog(taxonomy: dict[str, Any], skills: dict[str, Skill]) -> str:
    catalog = taxonomy["catalog"]
    categories = taxonomy["categories"]
    metadata = taxonomy["skill_metadata"]
    scopes = catalog["scopes"]
    lines = [
        f"# {catalog['title']}",
        "",
        "> 此文件由 `python scripts/update_catalog.py` 根据 `catalog/taxonomy.json` 和各 `SKILL.md` 生成，请勿直接编辑。",
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

    lines.extend(
        [
            "",
            f"共收录 **{len(skills)}** 个 skill。机器可读目录见 "
            f"[`{catalog['generated_index']}`]({catalog['generated_index']})。",
            "",
            "## 适用范围",
            "",
            "| 范围 | 定义 | Skill 数量 |",
            "| --- | --- | ---: |",
        ]
    )
    for scope_id, scope in scopes.items():
        count = sum(1 for item in metadata.values() if item["scope"] == scope_id)
        lines.append(f"| {scope['name']} | {escape_table(scope['description'])} | {count} |")

    lines.extend(["", "## 分类明细", ""])
    for category in categories:
        lines.extend(render_node(category, skills, metadata, scopes, 0))

    lines.extend(
        [
            "## 分类演进规则",
            "",
            "1. 主分类按用户任务与能力域划分；每个 skill 只归入一个最具体的叶子分类。",
            "2. 横向检索使用 `tags`，不得通过重复归类表达跨领域能力。",
            "3. `scope` 只描述复用边界：通用、团队或项目，不表示质量等级。",
            f"4. 分类树最多 {catalog['max_depth']} 层；只有同一领域形成多个稳定主题后才增加子分类。",
            "5. 物理目录统一为 `skills/<category-path>/<skill-name>/`；skill 名称不变，外部安装入口通过 junction 指向该物理路径。",
            "6. Markdown 与 JSON 目录均由生成器重建；遗漏、重复、路径不一致、非法元数据或生成物漂移会使校验失败。",
            "",
            "## 参考仓库与采纳点",
            "",
        ]
    )
    for reference in taxonomy.get("references", []):
        lines.append(f"- [{reference['name']}]({reference['url']})：{reference['adopted']}")
    lines.append("")
    return "\n".join(lines)


def flatten_categories(
    nodes: list[dict[str, Any]],
    id_path: tuple[str, ...] = (),
    name_path: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for node in nodes:
        current_ids = id_path + (node["id"],)
        current_names = name_path + (node["name"],)
        flattened.append(
            {
                "id": node["id"],
                "name": node["name"],
                "description": node["description"],
                "path": list(current_ids),
                "name_path": list(current_names),
                "skill_count": count_node_skills(node),
            }
        )
        flattened.extend(flatten_categories(node["children"], current_ids, current_names))
    return flattened


def render_index(
    taxonomy: dict[str, Any],
    skills: dict[str, Skill],
    assignments: dict[str, CategoryPath],
) -> str:
    catalog = taxonomy["catalog"]
    metadata = taxonomy["skill_metadata"]
    scopes = catalog["scopes"]
    index = {
        "schema_version": 2,
        "source": {
            "taxonomy": str(TAXONOMY_PATH.relative_to(ROOT)).replace("\\", "/"),
            "taxonomy_schema_version": taxonomy["schema_version"],
            "skills_root": catalog["skills_root"],
            "layout": catalog["layout"],
        },
        "skill_count": len(skills),
        "scopes": scopes,
        "categories": flatten_categories(taxonomy["categories"]),
        "skills": [],
        "references": taxonomy.get("references", []),
    }
    for skill_name in sorted(skills):
        skill = skills[skill_name]
        skill_metadata = metadata[skill_name]
        category = assignments[skill_name]
        index["skills"].append(
            {
                "name": skill.name,
                "description": skill.description,
                "path": f"{skill_relative_path(skill)}/SKILL.md",
                "category": {
                    "id": category.ids[-1],
                    "name": category.names[-1],
                    "path": list(category.ids),
                    "name_path": list(category.names),
                },
                "scope": {
                    "id": skill_metadata["scope"],
                    "name": scopes[skill_metadata["scope"]]["name"],
                },
                "tags": skill_metadata["tags"],
            }
        )
    return json.dumps(index, ensure_ascii=False, indent=2) + "\n"


def render_skill_table(taxonomy: dict[str, Any], skills: dict[str, Skill], lang: str = "zh") -> str:
    if lang == "en":
        header = ("| Category | Skill | Description |", "| --- | --- | --- |")
    else:
        header = ("| 分类 | Skill | 能力说明 |", "| --- | --- | --- |")
    lines = list(header)
    for category in taxonomy["categories"]:
        category_name = category["name_en"] if lang == "en" else category["name"]
        category_description = category["description_en"] if lang == "en" else category["description"]
        lines.append(
            f"| [**{category_name}**](CATALOG.md#{category['id']}) |  | "
            f"{escape_table(str(category_description))} |"
        )
        for name in collect_node_skills(category):
            skill = skills[name]
            skill_description = skill.description_en if lang == "en" else skill.description
            lines.append(
                f"|  | [`{name}`]({skill_relative_path(skill)}/SKILL.md) | "
                f"{escape_table(skill_description)} |"
            )
    return "\n".join(lines)


def render_readme(current: str, taxonomy: dict[str, Any], skills: dict[str, Skill]) -> str:
    start = current.find(README_START)
    end = current.find(README_END)
    if start < 0 or end < 0 or end < start:
        raise CatalogError("README.md 缺少有效的分类摘要标记")

    block = "\n".join([README_START, render_skill_table(taxonomy, skills, "zh"), README_END])
    return current[:start] + block + current[end + len(README_END) :]


def render_skills_page(current: str, taxonomy: dict[str, Any], skills: dict[str, Skill], lang: str = "zh") -> str:
    start = current.find(SKILLS_START)
    end = current.find(SKILLS_END)
    if start < 0 or end < 0 or end < start:
        raise CatalogError("SKILLS 页面缺少有效的分类明细标记")

    block = "\n".join([SKILLS_START, render_skill_table(taxonomy, skills, lang), SKILLS_END])
    return current[:start] + block + current[end + len(SKILLS_END) :]


def main() -> int:
    parser = argparse.ArgumentParser(description="生成或校验 LFen Skills 分类目录")
    parser.add_argument("--check", action="store_true", help="只检查配置、README、Markdown 与 JSON 目录是否一致")
    args = parser.parse_args()

    try:
        taxonomy = load_taxonomy()
        skills = discover_skills()
        assignments = validate_taxonomy(taxonomy, skills)
        rendered_catalog = render_catalog(taxonomy, skills)
        rendered_index = render_index(taxonomy, skills, assignments)
        catalog_path = ROOT / taxonomy["catalog"]["generated_markdown"]
        index_path = ROOT / taxonomy["catalog"]["generated_index"]
        readme_path = ROOT / "README.md"
        readme = readme_path.read_text(encoding="utf-8")
        rendered_readme = render_readme(readme, taxonomy, skills)
        skills_page_path = ROOT / "SKILLS.md"
        skills_page = skills_page_path.read_text(encoding="utf-8")
        rendered_skills_page = render_skills_page(skills_page, taxonomy, skills, "zh")
        skills_en_page_path = ROOT / "SKILLS.en.md"
        skills_en_page = skills_en_page_path.read_text(encoding="utf-8")
        rendered_skills_en_page = render_skills_page(skills_en_page, taxonomy, skills, "en")

        if args.check:
            if not catalog_path.exists() or catalog_path.read_text(encoding="utf-8") != rendered_catalog:
                raise CatalogError(
                    f"{catalog_path.relative_to(ROOT)} 不是最新版本；运行 python scripts/update_catalog.py"
                )
            if not index_path.exists() or index_path.read_text(encoding="utf-8") != rendered_index:
                raise CatalogError(
                    f"{index_path.relative_to(ROOT)} 不是最新版本；运行 python scripts/update_catalog.py"
                )
            if readme != rendered_readme:
                raise CatalogError("README.md 的分类摘要不是最新版本；运行 python scripts/update_catalog.py")
            if skills_page != rendered_skills_page:
                raise CatalogError("SKILLS.md 的分类明细不是最新版本；运行 python scripts/update_catalog.py")
            if skills_en_page != rendered_skills_en_page:
                raise CatalogError("SKILLS.en.md 的分类明细不是最新版本；运行 python scripts/update_catalog.py")
            print(
                f"分类目录校验通过：{len(skills)} 个 skill，{len(taxonomy['categories'])} 个一级分类，"
                "Markdown 与 JSON 目录一致"
            )
            return 0

        catalog_path.write_text(rendered_catalog, encoding="utf-8", newline="\n")
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(rendered_index, encoding="utf-8", newline="\n")
        readme_path.write_text(rendered_readme, encoding="utf-8", newline="\n")
        skills_page_path.write_text(rendered_skills_page, encoding="utf-8", newline="\n")
        skills_en_page_path.write_text(rendered_skills_en_page, encoding="utf-8", newline="\n")
        print(
            f"已更新 README.md、SKILLS.md、SKILLS.en.md、{catalog_path.relative_to(ROOT)} 与 {index_path.relative_to(ROOT)}："
            f"{len(skills)} 个 skill"
        )
        return 0
    except (CatalogError, OSError, KeyError, TypeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
