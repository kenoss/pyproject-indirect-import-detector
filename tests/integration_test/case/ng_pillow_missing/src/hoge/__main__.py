from pathlib import Path

import actfw_core
import PIL

IMAGE_PATH = Path(__file__) / "dummy.png"


def main():
    _image = PIL.Image.open(IMAGE_PATH)  # noqa F841

    _app = actfw_core.Applicatoin()  # noqa F841


if __name__ == "__main__":
    main()
