from src.ginji import bash_exec, edit_file, list_files, read_file, search_files, write_file


def test_bash_exec():
    output = bash_exec("echo hello")
    assert "hello" in output


def test_read_file(tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("alpha", encoding="utf-8")
    assert read_file(str(path)) == "alpha"


def test_write_file(tmp_path):
    path = tmp_path / "nested" / "item.txt"
    result = write_file(str(path), "beta")
    assert "ok:" in result
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "beta"


def test_edit_file(tmp_path):
    path = tmp_path / "edit.txt"
    path.write_text("hello world", encoding="utf-8")
    result = edit_file(str(path), "world", "fox")
    assert "ok:" in result
    assert path.read_text(encoding="utf-8") == "hello fox"


def test_list_files(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b" / "c.txt").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "b" / "c.txt").write_text("c", encoding="utf-8")
    result = list_files(str(tmp_path))
    assert "a.txt" in result
    assert "b/c.txt" in result


def test_search_files(tmp_path):
    path = tmp_path / "search.txt"
    path.write_text("one\ntarget line\nthree", encoding="utf-8")
    result = search_files("target", str(tmp_path))
    assert "search.txt:2:" in result


def test_edit_file_not_found(tmp_path):
    path = tmp_path / "edit.txt"
    path.write_text("hello world", encoding="utf-8")
    result = edit_file(str(path), "missing", "fox")
    assert "error:" in result
