def power(base, exponent):  # Define a function that raises a base to an exponent.
    """Return base raised to exponent."""  # Document the function's result.
    return base ** exponent  # Perform exponentiation and return the result.


def toggle_window(root, event=None):  # Define the function that toggles the application window.
    """Toggle an application's Tk window between visible and withdrawn."""  # Describe the function's purpose.
    if root.state() == "withdrawn":  # Check whether the window is currently hidden.
        root.deiconify()  # Restore the hidden window.
        root.lift()  # Bring the window above other windows.
        root.focus_force()  # Give keyboard focus to the window.
    else:  # Handle the case where the window is visible.
        root.withdraw()  # Hide the window.
    return "break"  # Prevent the key event from propagating further.


class CalculatorApp:  # Define the calculator application class.
    def __init__(self, root=None):  # Initialize a calculator instance.
        import tkinter as tk  # Import the Tkinter library for the graphical interface.

        self.root = root or tk.Tk()  # Use the supplied root window or create one.
        self.root.title("Calculator")  # Set the window title.
        self.root.resizable(False, False)  # Disable resizing in both directions.
        self.root.protocol("WM_DELETE_WINDOW", self.root.withdraw)  # Hide the window instead of closing it.
        self.root.bind("<F10>", lambda event: toggle_window(self.root, event))  # Bind F10 to the window toggle function.

        self._first = None  # Store the first number in a calculation.
        self._operator = None  # Store the selected arithmetic operator.
        self._reset_display = False  # Track whether the display should be replaced on the next digit.
        self._display = tk.Entry(  # Create the calculator display entry widget.
            self.root,  # Place the display in the root window.
            width=18,  # Set the display width.
            font=("TkDefaultFont", 18),  # Set the display font and size.
            justify="right",  # Align entered text to the right.
        )
        self._display.grid(row=0, column=0, columnspan=4, padx=8, pady=8)  # Arrange the display across four columns.
        self._display.insert(0, "0")  # Initialize the display with zero.

        self._thanks_label = tk.Label(  # Create a label for a friendly thank-you message.
            self.root,  # Place the label in the main window.
            text="",  # Start with no visible message.
            font=("TkDefaultFont", 11),  # Set a readable label font and size.
            fg="#4CAF50",  # Give the message a green text color.
        )
        self._thanks_label.grid(row=6, column=0, columnspan=4, pady=(4, 8))  # Place the message below the buttons.

        buttons = (  # Start the tuple containing all button labels and actions.
            ("C", "clear"),  # Define the clear button.
            ("+", "operator"),  # Define the addition button.
            ("-", "operator"),  # Define the subtraction button.
            ("*", "operator"),  # Define the multiplication button.
            ("7", "digit"),  # Define the seven button.
            ("8", "digit"),  # Define the eight button.
            ("9", "digit"),  # Define the nine button.
            ("/", "operator"),  # Define the division button.
            ("4", "digit"),  # Define the four button.
            ("5", "digit"),  # Define the five button.
            ("6", "digit"),  # Define the six button.
            ("^", "operator"),  # Define the exponentiation button.
            ("1", "digit"),  # Define the one button.
            ("2", "digit"),  # Define the two button.
            ("3", "digit"),  # Define the three button.
            ("=", "equals"),  # Define the equals button.
            ("0", "digit"),  # Define the zero button.
            (".", "decimal"),  # Define the decimal-point button.
        )
        button_colors = (  # Start the tuple containing a unique color for each button.
            "#F44336", "#FF9800", "#FFEB3B", "#8BC34A",  # Assign colors to the top-row and first four buttons.
            "#4CAF50", "#009688", "#00BCD4", "#03A9F4",  # Assign colors to the next four buttons.
            "#2196F3", "#3F51B5", "#673AB7", "#9C27B0",  # Assign colors to the middle four buttons.
            "#E91E63", "#F06292", "#FF7043", "#795548",  # Assign colors to the next four buttons.
            "#607D8B", "#26A69A",  # Assign colors to the final two buttons.
        )
        for index, (label, action) in enumerate(buttons):  # Loop through each button and its index.
            row = 1 + index // 4  # Calculate the button's grid row.
            column = index % 4  # Calculate the button's grid column.
            if action == "digit":  # Check whether the button represents a digit.
                command = lambda value=label: self.input_digit(value)  # Connect the button to the digit handler.
            elif action == "decimal":  # Check whether the button represents a decimal point.
                command = self.input_decimal  # Connect the button to the decimal handler.
            elif action == "operator":  # Check whether the button represents an operator.
                command = lambda value=label: self.choose_operator(value)  # Connect the button to the operator handler.
            elif action == "equals":  # Check whether the button represents the equals key.
                command = self.calculate  # Connect the button to the calculation handler.
            else:  # Handle the remaining clear action.
                command = self.clear  # Connect the button to the clear handler.
            color = button_colors[index]  # Select this button's unique background color.
            tk.Button(  # Create a colored calculator button.
                self.root,  # Place the button in the root window.
                text=label,  # Use the button's label as its visible text.
                width=5,  # Set the button width.
                command=command,  # Assign the button's click handler.
                bg=color,  # Set the button's background color.
                fg="#FFFFFF" if color not in ("#FFEB3B", "#8BC34A", "#4CAF50", "#00BCD4", "#03A9F4") else "#222222",  # Choose readable text color for the background.
                activebackground=color,  # Preserve the background color while the button is pressed.
            ).grid(row=row, column=column, padx=2, pady=2)  # Place the button in the grid with spacing.

    def display_text(self):  # Define a method that reads the display.
        return self._display.get()  # Return the display's current text.

    def set_display(self, value):  # Define a method that replaces the display text.
        self._display.delete(0, "end")  # Remove all existing display text.
        self._display.insert(0, str(value))  # Insert the supplied value as text.

    def input_digit(self, digit):  # Define the handler for digit button presses.
        if self._reset_display:  # Check whether the display should start a new number.
            self.set_display(digit)  # Replace the display with the pressed digit.
            self._reset_display = False  # Resume normal digit appending.
        elif self.display_text() == "0":  # Check whether the display currently contains only zero.
            self.set_display(digit)  # Replace the initial zero with the pressed digit.
        else:  # Handle all other display contents.
            self.set_display(self.display_text() + digit)  # Append the pressed digit to the display.

    def input_decimal(self):  # Define the handler for the decimal-point button.
        if self._reset_display:  # Check whether a new number is starting.
            self.set_display("0.")  # Create a new number beginning with zero and a decimal point.
            self._reset_display = False  # Resume normal decimal handling.
        elif "." not in self.display_text():  # Check that the display has no decimal point yet.
            self.set_display(self.display_text() + ".")  # Append a decimal point to the display.

    def choose_operator(self, operator):  # Define the handler for arithmetic operator buttons.
        try:  # Start guarded conversion of the display value.
            current = float(self.display_text())  # Convert the displayed number to a floating-point value.
        except ValueError:  # Handle invalid displayed text.
            self.set_display("Error")  # Show an error message.
            return  # Stop operator selection after the error.

        if self._first is not None and self._operator is not None:  # Check whether another calculation is pending.
            try:  # Start guarded calculation of the pending operation.
                self._first = self._calculate(self._first, current, self._operator)  # Apply the pending operator to the two numbers.
            except (ValueError, ZeroDivisionError):  # Handle invalid or division-by-zero calculations.
                self.set_display("Error")  # Display an error message.
                self._first = None  # Clear the stored first number.
                self._operator = None  # Clear the stored operator.
                self._reset_display = True  # Prepare the display for a replacement value.
                return  # Stop the operator handler.
            else:  # Run if the pending calculation succeeded.
                self.set_display(self._format_result(self._first))  # Display the intermediate result.
        else:  # Handle the first number of a calculation.
            self._first = current  # Store the current display value.
        self._operator = operator  # Store the newly selected operator.
        self._reset_display = True  # Prepare to enter the second number.

    def calculate(self):  # Define the equals-button calculation handler.
        if self._first is None or self._operator is None:  # Check whether a complete operation is available.
            return  # Do nothing if no operation has been selected.
        try:  # Start guarded conversion and calculation.
            current = float(self.display_text())  # Convert the second number to a floating-point value.
            result = self._calculate(self._first, current, self._operator)  # Calculate the final result.
        except (ValueError, ZeroDivisionError):  # Handle invalid input or division by zero.
            self.set_display("Error")  # Display an error message.
        else:  # Run if calculation succeeded.
            self.set_display(self._format_result(result))  # Display the formatted result.
            self._thanks_label.config(text="Thank you for using me!")  # Show the friendly thank-you message.
        self._first = None  # Clear the stored first number.
        self._operator = None  # Clear the stored operator.
        self._reset_display = True  # Prepare the display for a new calculation.

    def clear(self):  # Define the clear-button handler.
        self._first = None  # Clear the stored first number.
        self._operator = None  # Clear the stored operator.
        self._reset_display = False  # Disable display reset mode.
        self.set_display("0")  # Reset the display to zero.
        self._thanks_label.config(text="")  # Remove the thank-you message after clearing.

    @staticmethod  # Mark the following calculation method as a static method.
    def _calculate(first, second, operator):  # Define the internal arithmetic dispatcher.
        if operator == "+":  # Check for addition.
            return first + second  # Add the two numbers and return the result.
        if operator == "-":  # Check for subtraction.
            return first - second  # Subtract the second number from the first.
        if operator == "*":  # Check for multiplication.
            return first * second  # Multiply the two numbers and return the result.
        if operator == "/":  # Check for division.
            return first / second  # Divide the first number by the second.
        if operator == "^":  # Check for exponentiation.
            return power(first, second)  # Raise the first number to the second number's power.
        raise ValueError("Unknown operator")  # Reject any unsupported operator.

    @staticmethod  # Mark the following result-formatting method as static.
    def _format_result(result):  # Define a method that formats a result for display.
        if result.is_integer():  # Check whether the result has no fractional part.
            return str(int(result))  # Convert the whole number to an integer string.
        return str(result)  # Return the fractional result as a string.


def main():  # Define the program entry-point function.
    import tkinter as tk  # Import Tkinter for creating the main window.

    root = tk.Tk()  # Create the application's main window.
    CalculatorApp(root)  # Construct the calculator inside the main window.
    root.mainloop()  # Start the Tkinter event loop.


if __name__ == "__main__":  # Run main only when this file is executed directly.
    main()  # Start the calculator application.
