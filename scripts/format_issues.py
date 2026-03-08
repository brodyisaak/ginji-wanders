#!/usr/bin/env python3
import json
import os
import re
import sys

COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
THUMBS_UP = {"thumbs_up", "+1", "THUMBS_UP"}
THUMBS_DOWN = {"thumbs_down", "-1", "THUMBS_DOWN"}


def usage() -> None:
    print("usage: python scripts/format_issues.py <issues_json> <sponsors_json> <day_num>")


def reaction_count(groups, valid_names):
    total = 0
    for group in groups or []:
        content = str(group.get("content", ""))
        if content not in valid_names:
            continue
        if isinstance(group.get("users"), dict):
            total += int(group["users"].get("totalCount", 0) or 0)
        else:
            total += int(group.get("count", 0) or 0)
    return total


def author_login(issue):
    author = issue.get("author") if isinstance(issue.get("author"), dict) else {}
    if author.get("login"):
        return author["login"]
    user = issue.get("user") if isinstance(issue.get("user"), dict) else {}
    return user.get("login", "unknown")


def clean_body(body):
    text = body or ""
    return COMMENT_RE.sub("", text).strip()


def main() -> int:
    if len(sys.argv) != 4:
        usage()
        return 1

    issues_path, sponsors_path, _day_num = sys.argv[1], sys.argv[2], sys.argv[3]
    try:
        issues = json.loads(open(issues_path, "r", encoding="utf-8").read())
    except Exception:
        issues = []
    try:
        sponsors = set(json.loads(open(sponsors_path, "r", encoding="utf-8").read()))
    except Exception:
        sponsors = set()

    if not issues:
        print("no issues today.")
        return 0

    rows = []
    for issue in issues:
        up = reaction_count(issue.get("reactionGroups"), THUMBS_UP)
        down = reaction_count(issue.get("reactionGroups"), THUMBS_DOWN)
        net = up - down
        login = author_login(issue)
        badge = " 💛 sponsor" if login in sponsors else ""
        title = issue.get("title", "untitled")
        number = issue.get("number", "?")
        body = clean_body(issue.get("body", ""))
        rows.append((net, number, title, login, badge, body))

    rows.sort(key=lambda item: item[0], reverse=True)
    boundary = os.urandom(16).hex()
    print(boundary)
    for net, number, title, login, badge, body in rows:
        print(f"### issue #{number}: {title}")
        print(f"**score:** {net:+d} | **author:** @{login}{badge}")
        print()
        print(body)
        print()
    print(boundary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
