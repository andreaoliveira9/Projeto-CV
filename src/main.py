def main():
    print("1 - Blend, Cut, Mask Demo")
    print("2 - Effects window")
    print("3 - Interactive window")
    print("4 - Fractal Mandelbulb window")
    print("5 - Fractal Julia Set 3D")
    print("0 - Exit")
    option = input("Choose an option: ")

    while option not in ["0", "1", "2", "3", "4", "5"]:
        print("Invalid option")
        option = input("Choose an option: ")

    if option == "1":
        from lib import WindowBlendCutMask as Window
    elif option == "2":
        from lib import WindowEffects as Window
    elif option == "3":
        from lib import WindowInteractive as Window
    elif option == "4":
        from lib import WindowMandelbulb as Window
    elif option == "5":
        from lib import WindowJuliaSet3D as Window
    elif option == "0":
        return

    window = Window()
    window.create_window()

    window.run()


if __name__ == "__main__":
    main()
