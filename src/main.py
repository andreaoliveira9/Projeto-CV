def main():
    print("1 - Interactive window")
    print("2 - Mandelbulb window")
    print("0 - Exit")
    option = input("Choose an option: ")

    if option == "1":
        from lib import WindowInterative as Window
    elif option == "2":
        from lib import WindowMandelbulb as Window
    else:
        return

    window = Window()
    window.create_window()

    window.run()


if __name__ == "__main__":
    main()
