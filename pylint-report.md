# Pylint Report

---

```text
************* Module app
app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
app.py:15:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:19:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:27:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:42:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:46:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:51:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:91:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:119:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:128:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:149:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:184:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:217:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:238:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:271:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:288:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module config
config.py:1:0: C0114: Missing module docstring (missing-module-docstring)
************* Module db
db.py:1:0: C0114: Missing module docstring (missing-module-docstring)
db.py:6:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:12:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:21:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:24:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module games
games.py:1:0: C0114: Missing module docstring (missing-module-docstring)
games.py:7:0: C0115: Missing class docstring (missing-class-docstring)
games.py:16:4: C0116: Missing function or method docstring (missing-function-docstring)
games.py:33:4: C0116: Missing function or method docstring (missing-function-docstring)
games.py:63:0: C0116: Missing function or method docstring (missing-function-docstring)
games.py:73:0: C0116: Missing function or method docstring (missing-function-docstring)
games.py:85:0: C0116: Missing function or method docstring (missing-function-docstring)
games.py:111:0: C0116: Missing function or method docstring (missing-function-docstring)
games.py:116:0: C0116: Missing function or method docstring (missing-function-docstring)
games.py:123:0: C0116: Missing function or method docstring (missing-function-docstring)
games.py:127:0: C0116: Missing function or method docstring (missing-function-docstring)
games.py:131:0: C0116: Missing function or method docstring (missing-function-docstring)
games.py:137:0: C0116: Missing function or method docstring (missing-function-docstring)
games.py:153:0: C0116: Missing function or method docstring (missing-function-docstring)
games.py:182:0: C0116: Missing function or method docstring (missing-function-docstring)
games.py:186:0: C0116: Missing function or method docstring (missing-function-docstring)
games.py:193:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module seed
seed.py:1:0: C0114: Missing module docstring (missing-module-docstring)
************* Module users
users.py:1:0: C0114: Missing module docstring (missing-module-docstring)
users.py:6:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:11:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:15:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:24:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:30:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:42:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:46:0: C0116: Missing function or method docstring (missing-function-docstring)

------------------------------------------------------------------
Your code has been rated at 8.77/10 (previous run: 8.70/10, +0.08)
```

## Report Overview

There are no other warnings in the Pylint report besides missing docstrings, as my personal preference is to adhere to the standard style guidelines of any language I work with. For instance, I see no reason to use lowercase for constants when standard Python conventions dictate uppercase.

### Docstrings

All reported Pylint warnings relate to missing module, class, or function docstrings.

```text
games.py:1:0: C0114: Missing module docstring (missing-module-docstring)
games.py:7:0: C0115: Missing class docstring (missing-class-docstring)
games.py:16:4: C0116: Missing function or method docstring (missing-function-docstring)
````

Omitting docstrings was an intentional design decision. The codebase is relatively simple, and self-descriptive function and module names provide the reader with sufficient context.
