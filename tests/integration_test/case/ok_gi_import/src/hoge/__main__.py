def main():
    import gi

    gi.require_version("Gst", "1.0")
    from gi.repository import Gst

    Gst.init(None)


if __name__ == "__main__":
    main()
