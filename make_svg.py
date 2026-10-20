"""Generates light_mode.svg and dark_mode.svg (neofetch-style profile card).

Edit CONFIG below, run `python make_svg.py`, commit the two SVGs.
today.py then keeps the live stats (age, repos, stars, followers, commits) fresh.
"""
from xml.sax.saxutils import escape

# ----------------------------- CONFIG ---------------------------------
CONFIG = {
    "header": "yourname@github",          # shown at the top, e.g. "alex@github"
    "line_len": 52,                        # total characters per info line
    "info": [                              # static lines: (key, value)
        ("OS", "Windows 11, Ubuntu, Android"),
        ("Host", "Your College / Company"),
        ("Kernel", "Your Job Title / Student"),
        ("IDE", "VS Code, Neovim"),
    ],
    "languages": [
        ("Programming", "Python, JavaScript, C++"),
        ("Computer", "HTML, CSS, SQL, Markdown"),
        ("Real", "English, Hindi, Konkani"),
    ],
    "hobbies": [
        ("Software", "Open source, Automation"),
        ("Hardware", "Raspberry Pi, Keyboards"),
    ],
    "contact": [
        ("Email", "you@example.com"),
        ("LinkedIn", "your-linkedin-handle"),
        ("Discord", "your_discord"),
    ],
}

# Replace this with your own ASCII art (convert any image with an
# image-to-ASCII tool, ~40 columns wide, ~24 rows tall works well).
ASCII_ART = r"""                                                                                                                                                                                                                                                              
                                       ..                     ..       
                                     ...:..                  .::..                                     
                                    ..*@#-..               :.:*@%:..                                   
                                   .:#@@@*=..             ..:#@@@%=..                                  
                                  .:#*#@@@%*..           ..+#@@@%*%=.                                  
                                 ..#+...+%@@*-...     ...:+%@@+:..=@:.                                 
                                ..*#..:...=@@@%#=:....-*%@@@+..:-:.*%..                                
                                .:@-....:...+@@@@@@@@@@@@@*...--...:%=..                               
                               ..+#....:::...=*+*%@@@@#+*+...---:...+#..                               
                               ..*+....::::..-#@@@@@@@@@%=..----:...-%..                               
                               ..##...:::...#@@@@#=*#%@@@@%:.:----..*%:.                               
                              ..+@@=:--:...+%@@@%=#@@@@@@@%+:..:.:-=@@*..                              
                            ..:#@@@#:......**%@@@#=*#%@@%@%+.....:-*@@@%-..                            
                           ..=@@@@*:.........:#.%@@@@@@:*-.........:+@@@@*..                           
                          ..*@@@*-..  ....-.....=@@@@@*.....-.........=%@@%:.                          
                         ..*@@@=-.:....-%*-=#*-:%@@@@@@::*#+-=#=.......:%@@#:.                         
                        ..+@@@*---:...::+%#**#@@@@@:%@@@@%***%+-:....:::-@@@#..                        
                        .:@@@@**=-.....::--:...*@%-.:#@%...:--::.....::=*%@@@+..                       
                       ..=%@@@%+=-.............-#:....*+..........  ..:+#@@@@-.:                       
                        .:@@@@#*-:...-:....... ..    ..:........:-:...:=*@@@@*..                       
                       ..%@%@@%=-.....*%+:..--...      ..:-..:=##:....::%@@%@@-.                       
                       .:@+%@@%--......-@%%%=.............-%%#@=.......:#@@@=@=.                       
                       ..*:@%@@+--..-:..-%@*:...-#*+*#=....=@@=...:..::-%@%@+-:.                       
                        ..:-+@@@*=-::-:..+@=....+@@@@@#....+@*...::.:-+%@@#-:...                       
                        :...**-@@%#=---:.-%@*=....:--:...-+%@+..::::#*@@+=#:...                        
                          ....*@@@*%=-:-..%@@@@*-.-#=.:+@@@@@:.::::#=@@@@.....                         
                          ....%@@@@#%+::-.#@@@*=**+=+**==@@@%.::.-##%@@@@:...                          
                           ...*@@@@@@@#-:--@@@@#*=---=+#@@@@-:..+@@@@@@@@...                           
                             ..#@@@@@@@@*--=@@@@@@@@@@@@@@@+::+%@@@@@@@%:.:                            
                              ..=%@@@@@@@@#=+@@@@@@@@@@@@@+-*@@@@@@@@@*..                              
                               ...*@@@@@@@@@@@@@*##+##*@@@@@@@@@@@@@%-..                               
                                 ..:#@#**@@@@@@@:......%@@@@@@%+*@%-..                                 
                                   ...##--%@%:.@*.....+@..#@@+-+%:..                                   
                                     :..-:.-%%-:%*:..+%-:%%+::-...                                     
                                        .....:+%++%#%*+#*-......                                       
                                             ...:*%@@#-...                                             
                                                 ......                                                
                                                                                                                                                                                             
                                                                                                       
""".strip("\n").split("\n")

THEMES = {
    "light_mode.svg": dict(bg="#f6f8fa", text="#24292f", key="#d9480f",
                           value="#0969da", cc="#8c959f", add="#1a7f37", dele="#cf222e"),
    "dark_mode.svg": dict(bg="#161b22", text="#c9d1d9", key="#ffa657",
                          value="#79c0ff", cc="#616e7c", add="#3fb950", dele="#f85149"),
}

# Dynamic fields: (label, svg element id, placeholder)
STATS = [
    ("Repos", "repo_data", "0"),
    ("Stars", "star_data", "0"),
    ("Followers", "follower_data", "0"),
    ("Commits", "commit_data", "0"),
]
# ----------------------------------------------------------------------

LEFT_X, RIGHT_X, TOP, LH = 15, 400, 30, 20
LINE_LEN = CONFIG["line_len"]


def dots(key, value):
    n = LINE_LEN - len(key) - len(value) - 3
    return " " + "." * max(n, 2) + " "


def row(y, key, value, value_id=None, key_class="key"):
    d = dots(key, value)
    dot_id = f' id="{value_id}_dots"' if value_id else ""
    val_id = f' id="{value_id}"' if value_id else ""
    return (f'<tspan x="{RIGHT_X}" y="{y}" class="{key_class}">{escape(key)}</tspan>:'
            f'<tspan class="cc"{dot_id}>{d}</tspan>'
            f'<tspan class="value"{val_id}>{escape(value)}</tspan>')


def section(y, title):
    rule = "-" * max(LINE_LEN - len(title) - 3, 2)
    return (f'<tspan x="{RIGHT_X}" y="{y}">- {escape(title)}</tspan> '
            f'<tspan class="cc">{rule}-</tspan>')


def build(theme):
    out = []
    # ASCII art on the left
    for i, line in enumerate(ASCII_ART):
        out.append(f'<tspan x="{LEFT_X}" y="{TOP + i * LH}">{escape(line)}</tspan>')
    art = "\n".join(out)

    right, y = [], TOP
    head = CONFIG["header"]
    right.append(f'<tspan x="{RIGHT_X}" y="{y}">{escape(head)}</tspan> '
                 f'<tspan class="cc">{"-" * max(LINE_LEN - len(head) - 1, 2)}-</tspan>')
    for k, v in CONFIG["info"]:
        y += LH
        right.append(row(y, k, v))
    # Uptime (dynamic)
    y += LH
    right.append(row(y, "Uptime", "0 years, 0 months, 0 days", "age_data"))
    y += LH * 2
    right.append(section(y, "Languages"))
    for k, v in CONFIG["languages"]:
        y += LH
        right.append(row(y, "Languages." + k, v))
    y += LH * 2
    right.append(section(y, "Hobbies"))
    for k, v in CONFIG["hobbies"]:
        y += LH
        right.append(row(y, "Hobbies." + k, v))
    y += LH * 2
    right.append(section(y, "Contact"))
    for k, v in CONFIG["contact"]:
        y += LH
        right.append(row(y, "Contact." + k, v))
    y += LH * 2
    right.append(section(y, "GitHub Stats"))
    for label, eid, ph in STATS:
        y += LH
        right.append(row(y, label, ph, eid))
    height = max(y, TOP + len(ASCII_ART) * LH) + 30
    width = 985
    t = theme
    return f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{width}px" height="{height}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {t["key"]};}}
.value {{fill: {t["value"]};}}
.addColor {{fill: {t["add"]};}}
.delColor {{fill: {t["dele"]};}}
.cc {{fill: {t["cc"]};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{width}px" height="{height}px" fill="{t["bg"]}" rx="15"/>
<text xml:space="preserve" x="{LEFT_X}" y="{TOP}" fill="{t["text"]}" class="ascii">
{art}
</text>
<text xml:space="preserve" x="{RIGHT_X}" y="{TOP}" fill="{t["text"]}">
{chr(10).join(right)}
</text>
</svg>
'''


if __name__ == "__main__":
    for name, theme in THEMES.items():
        with open(name, "w", encoding="utf-8") as f:
            f.write(build(theme))
        print("wrote", name)
