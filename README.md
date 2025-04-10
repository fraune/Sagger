# Sagger

Custom code editor, where long lines sag, helping reinforce good coding practices

## Demo

<video src='https://github.com/user-attachments/assets/154d9c3b-c9c4-4179-94fb-900e3fab0e80'></video>

## TODO

Basic editor features

- [ ] Opening project folder
- [ ] Opening files
- [ ] Saving files
- [ ] Highlight selected code
- [ ] Code syntax coloring

Linting

- [ ] Long lines automatically "break" while writing them, based on linter configuration

Bugs

- [ ] Long lines with the drooping style may have the final characters of text displayed above the current line

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

Import cleanup
```
autoflake --in-place --remove-all-unused-imports --recursive .
```

## Running the app

After environment setup, run:

```
python -m app.main
```
