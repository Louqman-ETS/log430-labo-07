import os

def main() -> None:
    msg = os.getenv("MESSAGE", "Hello, World!")
    print(msg)


if __name__ == "__main__":
    main()