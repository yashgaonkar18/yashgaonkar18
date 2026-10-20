"""Updates the dynamic values in light_mode.svg / dark_mode.svg.

Env vars required:
  ACCESS_TOKEN  - GitHub personal access token (classic: read:user, repo scope for private commits)
  USER_NAME     - your GitHub username
Optional:
  BIRTHDAY      - YYYY-MM-DD, used for the "Uptime" line (default 2000-01-01)
"""
import datetime
import os
import sys
import xml.etree.ElementTree as ET

import requests

ET.register_namespace("", "http://www.w3.org/2000/svg")

HEADERS = {"authorization": "token " + os.environ.get("ACCESS_TOKEN", "")}
USER_NAME = os.environ.get("USER_NAME", "")
BIRTHDAY = os.environ.get("BIRTHDAY") or "2000-01-01"
LINE_LEN = 52  # keep in sync with make_svg.py
SVGS = ["light_mode.svg", "dark_mode.svg"]
API = "https://api.github.com/graphql"


def gql(query, variables):
    r = requests.post(API, json={"query": query, "variables": variables},
                      headers=HEADERS, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"GraphQL failed: {r.status_code} {r.text}")
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


def age_string(birthday):
    b = datetime.date.fromisoformat(birthday)
    t = datetime.date.today()
    years = t.year - b.year
    months = t.month - b.month
    days = t.day - b.day
    if days < 0:
        months -= 1
        prev_month_end = t.replace(day=1) - datetime.timedelta(days=1)
        days += prev_month_end.day
    if months < 0:
        years -= 1
        months += 12
    s = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
    return f"{s(years, 'year')}, {s(months, 'month')}, {s(days, 'day')}" + (
        " \U0001F382" if (months == 0 and days == 0) else "")


def basic_stats(user):
    q = """
    query($login: String!, $cursor: String) {
      user(login: $login) {
        followers { totalCount }
        repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          pageInfo { hasNextPage endCursor }
          nodes { stargazerCount }
        }
        createdAt
      }
    }"""
    stars, cursor, repos, followers, created = 0, None, 0, 0, None
    while True:
        u = gql(q, {"login": user, "cursor": cursor})["user"]
        repos = u["repositories"]["totalCount"]
        followers = u["followers"]["totalCount"]
        created = u["createdAt"]
        stars += sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
        pi = u["repositories"]["pageInfo"]
        if not pi["hasNextPage"]:
            break
        cursor = pi["endCursor"]
    return repos, stars, followers, created


def total_commits(user, created_iso):
    """Sum contributions.totalCommitContributions year by year (API limit: 1 year/query)."""
    q = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }"""
    start = datetime.datetime.fromisoformat(created_iso.replace("Z", "+00:00"))
    now = datetime.datetime.now(datetime.timezone.utc)
    total = 0
    while start < now:
        end = min(start.replace(year=start.year + 1) if not (start.month == 2 and start.day == 29)
                  else start.replace(year=start.year + 1, day=28), now)
        c = gql(q, {"login": user, "from": start.isoformat(), "to": end.isoformat()})
        cc = c["user"]["contributionsCollection"]
        total += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
        start = end
    return total


def fmt(n):
    return f"{n:,}"


def justify(root, element_id, new_text):
    """Set a value and resize its dot leader so the line stays aligned."""
    ns = {"s": "http://www.w3.org/2000/svg"}
    val = root.find(f".//*[@id='{element_id}']", ns)
    dots = root.find(f".//*[@id='{element_id}_dots']", ns)
    if val is None:
        raise KeyError(f"missing #{element_id} in svg")
    val.text = new_text
    if dots is not None:
        # key length is recovered from the preceding tspan text
        key_len = getattr(dots, "_key_len", None)
        if key_len is None:
            key_len = find_key_len(root, dots)
        n = max(LINE_LEN - key_len - len(new_text) - 3, 2)
        dots.text = " " + "." * n + " "


def find_key_len(root, dots):
    for parent in root.iter():
        kids = list(parent)
        for i, k in enumerate(kids):
            if k is dots and i > 0:
                return len(kids[i - 1].text or "")
    return 0


def update_svg(path, values):
    tree = ET.parse(path)
    root = tree.getroot()
    for eid, text in values.items():
        justify(root, eid, text)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main():
    if not USER_NAME or not os.environ.get("ACCESS_TOKEN"):
        sys.exit("Set USER_NAME and ACCESS_TOKEN environment variables.")
    repos, stars, followers, created = basic_stats(USER_NAME)
    commits = total_commits(USER_NAME, created)
    values = {
        "age_data": age_string(BIRTHDAY),
        "repo_data": fmt(repos),
        "star_data": fmt(stars),
        "follower_data": fmt(followers),
        "commit_data": fmt(commits),
    }
    print(values)
    for svg in SVGS:
        update_svg(svg, values)


if __name__ == "__main__":
    main()
