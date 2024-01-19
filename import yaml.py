import yaml 

with open("help_text.yaml", "r") as f:
    help_text = yaml.safe_load(f)

print(help_text)