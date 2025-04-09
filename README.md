# Sagger

Custom code editor, where long lines sag, helping reinforce good coding practices

## Demo

<video src="https://github.com/fraune/Sagger/blob/main/assets/sagger_demo.mov" type="video/mov" width="640"></video>

## Goals

Sag Styles

- [ ] "Hanging end"
- [ ] "Droop"

Linting

- [ ] Long lines eventually "break"

## Setup

Create the virtual environment

```
python -m venv .venv
```

Activate the virtual environment

```
source .venv/bin/activate
```

Upgrade pip (optional)

```
pip install --upgrade pip
```

Install dependencies

```
pip install -r requirements_raw.txt
```

When adding new dependencies, add them to a new line in requirements_raw.txt

To inspect dependency versions, you can do:

```
pip freeze > requirements.txt
```

To enforce linting rules:

```
python -m black .
```

