#!/bin/env python3

import io
import random
import string
import PySimpleGUI as sg
import pandas as pd

import os.path

from PIL import Image


class Test:
    def __str__(self) -> str:
        return "str"

    def __repr__(self) -> str:
        return "repr"


def word():
    return "".join(random.choice(string.ascii_lowercase) for i in range(10))


def number(max_val=1000):
    return random.randint(0, max_val)


headers = {
    "Integers": [
        1,
        2,
    ],
    "Strings": ["abc", "def"],
    "Normalized Floats": [3.14, 5.18],
}
table = pd.DataFrame(headers)
headings = list(headers)
values = table.values.tolist()

# ------ Make the Table Data ------



if __name__ == "__main__":
    # First the window layout in 2 columns
    file_list_column = [
        [
            sg.Text("Image Folder"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(
                values=[{"a": "b", "c": "d"}, ["jkl"], Test()],
                enable_events=True,
                size=(40, 20),
                key="-FILE LIST-",
            )
        ],
    ]
    # For now will only show the name of the file that was chosen

    image_viewer_column = [
        [sg.Text("Choose an image from list on left:")],
        [sg.Text(size=(40, 1), key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
    ]
    # ----- Full layout -----

    layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(image_viewer_column),
            sg.VSeperator(),
            sg.Column(
                [
                    [
                        sg.Table(
                            values=values,
                            headings=headings,
                            auto_size_columns=False,
                            col_widths=list(map(lambda x: len(x) + 1, headings)),
                        )
                    ]
                ]
            ),
        ]
    ]
    window = sg.Window("Image Viewer", layout)
    while True:
        event, values = window.read()
        print(f"event: {event}")
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        # Folder name was filled in, make a list of files in the folder
        if event == "-FOLDER-":
            print("in folder event")
            folder = values["-FOLDER-"]
            print(folder)
            try:
                # Get list of files in folder
                print("Getting listdir")
                file_list = os.listdir(folder)
            except Exception as e:
                print("Got exception...")
                print(e)
                file_list = []

            print(file_list)

            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".png", ".gif", ".jpg"))
            ]

            window["-FILE LIST-"].update(fnames)
        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            print("in file list event")
            try:
                print(values["-FILE LIST-"])
                filename = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])
                window["-TOUT-"].update(filename)
                if filename.lower().endswith((".jpg")):
                    pil_image = Image.open(filename)
                    png_bio = io.BytesIO()
                    pil_image.save(png_bio, format="PNG")
                    png_data = png_bio.getvalue()
                    window["-IMAGE-"].update(data=png_data)
                else:
                    window["-IMAGE-"].update(filename=filename)
            except:
                pass
        else:
            print("Unknown event!")

    window.close()
