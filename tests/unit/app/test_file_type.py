from image_viewer.indexd_searcher import RegexEqual


def test_simple_match():
    match RegexEqual("Something to match"):
        case "^...match":
            print("Nope...")
        case "^S.*ing$":
            print("Closer...")
        case "^S.*match$":
            print("Yep!")
        case _:
            assert False, "Should not match anything else"


def test_extension_match():

    match RegexEqual("/a/b/c/d.txt"):
        case "\\.txt":
            print("ok")
        case _:
            assert False, "Should not match anything else"

    for file_name in ["/a/b/c/d.ome.tif", "/a/b/c/d.ome.tiff", "/a/b/c/d.vcf.gz", "/a/b/c/d.vcf"]:
        match RegexEqual(file_name):
            case "\\.ome.tif?":
                continue
            case "\\.vcf":
                continue
            case _:
                assert False, "Should not match anything else"
        assert False, "Should not match anything else"
