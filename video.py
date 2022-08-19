#!/usr/bin/env python3

from pathlib import Path
from typing import Dict, List, Tuple
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

# from multiprocessing import Pool

IMAGES_DIR = Path("./edited_imgs")
VIDEOS_DIR = Path("./videos")

MAX_VIDEO_LENGTH = 56.0
MAX_WEEK_LENGTH = 2.0
MIN_PIC_LENGTH = 0.3
MAX_PIC_LENGTH = 1.0
BABY_WEEK_LENGTH = 3.0
BABY_BORN_IN_WEEK = 42


def pic_length(number_of_pictures_in_week: int, is_baby: bool) -> float:
    if is_baby:
        return BABY_WEEK_LENGTH / number_of_pictures_in_week
    length = MAX_WEEK_LENGTH / number_of_pictures_in_week
    length = min(MAX_PIC_LENGTH, length)
    length = max(MIN_PIC_LENGTH, length)
    return length


inf = float("inf")


def is_empty(dir: Path):
    assert dir.exists()
    return not any(dir.iterdir())


def delete_all_files(dir: Path):
    for file in dir.iterdir():
        if file.is_file():
            file.unlink()


def write_video_file(images_fps_filename: Tuple[List[str], float, str]) -> None:
    images, fps, filename = images_fps_filename
    clip = ImageSequenceClip(images, fps=fps)
    clip.write_videofile(filename)


def main():
    assert not is_empty(IMAGES_DIR)

    if not VIDEOS_DIR.exists():
        VIDEOS_DIR.mkdir()
    if not is_empty(VIDEOS_DIR):
        print(f"Deleting all files in {VIDEOS_DIR}")
        delete_all_files(VIDEOS_DIR)
        assert is_empty(VIDEOS_DIR)

    min_week = inf
    max_week = -inf
    image_paths: Dict[int, Dict[int, Path]] = {}
    total_number_of_pics = 0

    for path in IMAGES_DIR.iterdir():
        assert path.is_file(), f"{path} isn't a file"
        stem = path.stem
        assert len(stem) == 5
        week, number = stem.split("-")
        week = int(week)
        number = int(number)
        if week not in image_paths:
            image_paths[week] = {}
        week_dict = image_paths[week]
        if number not in week_dict:
            week_dict[number] = path
        total_number_of_pics += 1

    weeks = sorted(image_paths.keys())
    number_of_weeks = len(weeks)

    image_lengths: Dict[Tuple[int, int], float] = {}
    total_length: float = 0.0
    paths: Dict[Tuple[int, int], Path] = {}
    keys: List[Tuple[int, int]] = []

    for week in weeks:
        week_paths = image_paths[week]
        numbers = sorted(week_paths.keys())
        assert min(numbers) == 1
        max_number = max(numbers)
        assert max_number == len(numbers)
        for number in numbers:
            key = week, number
            length = pic_length(max_number, week >= BABY_BORN_IN_WEEK)
            image_lengths[key] = length
            total_length += length
            paths[key] = week_paths[number]
            keys.append(key)

    if total_length > MAX_VIDEO_LENGTH or True:
        ratio = MAX_VIDEO_LENGTH / total_length
        print(f"Multiplying image lengths with {ratio*100:.1f}%")
        for key in keys:
            image_lengths[key] *= ratio

    list_of_images_fps_filename: List[Tuple[List[str], float, str]] = []

    for week in weeks:
        week_paths = image_paths[week]
        numbers = sorted(week_paths.keys())
        number_of_images = len(numbers)
        length_per_image = image_lengths[(week, 1)]
        length_of_week = number_of_images * length_per_image
        fps = number_of_images / length_of_week
        images: List[str] = []
        for number in numbers:
            key = week, number
            images.append(paths[key].as_posix())
        filename = f"{(VIDEOS_DIR / f'{week:02}.mp4')}"

        list_of_images_fps_filename.append((images, fps, filename))

    print(f"Writing {len(list_of_images_fps_filename)} videos...")

    _ = list(map(write_video_file, list_of_images_fps_filename))

    # pool = Pool()
    # pool.imap_unordered(write_video_file, list_of_images_fps_filename, chunksize=2)

    print("Done!")


if __name__ == "__main__":
    main()
