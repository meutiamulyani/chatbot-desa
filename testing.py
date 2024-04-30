import threading

def timeout():
    print("No input")
    # Add code here to gracefully exit or handle the situation

def main():
    # Start the timer thread
    timer = threading.Timer(10, timeout)
    timer.start()

    # Your main program logic here
    # You would typically have some input operation or loop

    # For demonstration, let's just wait for user input
    user_input = input("Enter something: ")

    # If user input is received before the timer expires, cancel the timer
    timer.cancel()
    print("User input:", user_input)

if __name__ == "__main__":
    main()
