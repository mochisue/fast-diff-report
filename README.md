# fast-diff-report

Create diff html like [difflib](https://docs.python.org/3/library/difflib.html#difflib.HtmlDiff.make_file) using [google's diff_match_patch](https://github.com/google/diff-match-patch)

# Usage

### Install

The following command will install the latest version of a module and its dependencies.

```
pip install git+https://github.com/mochisue/fast-diff-report.git
```

### Sample Program

You can output the html report in the same way as you would use the [difflib's make_file](https://docs.python.org/3/library/difflib.html#difflib.HtmlDiff.make_file).

```
def sample(text1: str, text2: str, out_html_path: str):
    fast_diff_report = FastDiffReport(wrapcolumn=60)
    res = fast_diff_report.make_file(text1, text2, context=True)

    with open(out_html_path, mode="w", encoding="utf-8") as f:
        f.write(res)
```

# Author

[mochisue](https://github.com/mochisue)

# Licence

[MIT](https://github.com/mochisue/pyqt-async-sample/blob/main/LICENSE)
