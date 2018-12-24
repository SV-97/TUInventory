import re

with open("Literaturverzeichnis.bib") as f:
    content = f.read()
pattern = r"url *= *{([^ {},]+)}"
matches = re.findall(pattern, content)
for string in matches:
    print(string)
    content = content.replace(string, "$" + string + "$")
with open("Literaturverzeichnis.bib", "w") as f:
    f.write(content)