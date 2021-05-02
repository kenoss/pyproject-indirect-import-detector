`poetry install && poetry run pytest -v tests/check_hoge.py` passes but we get

```console
$ python src/hoge/__main__.py
Traceback (most recent call last):
  File "/home/keno/src/github.com/kenoss/pyproject-indirect-import-detector/tests/integration_test/case/ng_test_cannot_test_import/src/hoge/__main__.py", line 1, in <module>
    import PIL
ModuleNotFoundError: No module named 'PIL'
```

if the environment does not have `PIL`.  This means, tests cannot check import-problem correctly.
