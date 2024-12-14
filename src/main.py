def main():
    print("1 - Effects window")
    print("2 - Mandelbulb window")
    print("3 - Interactive window")
    print("0 - Exit")
    # option = input("Choose an option: ")
    option = "3"

    if option == "1":
        from lib import WindowEffects as Window
    elif option == "2":
        from lib import WindowMandelbulb as Window
    elif option == "3":
        from lib import WindowInteractive as Window
    else:
        return

    window = Window()
    window.create_window()

    window.run()


if __name__ == "__main__":
    main()
